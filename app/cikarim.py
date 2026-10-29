"""
Zekai Hukuk — Çoklu Sağlayıcı Yapay Zeka Çıkarım Motoru (Multi-Provider LLM).
Desteklenen Sağlayıcılar:
- Anthropic Claude (claude-sonnet-5-5, claude-3-7-sonnet vb.)
- DeepSeek (deepseek-chat / V3, deepseek-reasoner / R1 - Çin)
- Alibaba Qwen / DashScope (qwen-max, qwen-plus, qwen-turbo - Çin)
- Google Gemini (gemini-2.5-flash, gemini-2.5-pro)
- OpenAI (gpt-4o, gpt-4o-mini, o1, o3-mini)
- Yerel / Offline Ollama (localhost:11434 - Llama 3, Qwen 2.5, DeepSeek R1)
- Yerel Regex / Kural Motoru (API anahtarsız bedava demo modu)
"""
from __future__ import annotations

import json
import os
import re
from typing import Any

from app.cikarim_parser import demo_cikarim
from app.kvkk_maskeleme import maskele, maskeleri_geri_ac
from app.prompt_yoneticisi import guvenli_veri_citi

SISTEM_PROMPTU_YOLU = os.path.join(os.path.dirname(__file__), "..", "prompts", "01-ihbar-takvimi-tr.md")

# Çalışma zamanı dinamik ayarları
AKTIF_AYARLAR = {
    "saglayici": os.environ.get("ZEKAI_LLM_PROVIDER", "claude"),  # claude | deepseek | qwen | gemini | openai | ollama | demo
    "model": os.environ.get("ZEKAI_MODEL", "claude-sonnet-5-5"),
    "api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
    "base_url": os.environ.get("ZEKAI_LLM_BASE_URL", "")
}

SAGLAYICI_VARSAYILANLARI = {
    "claude": {
        "model": "claude-sonnet-5-5",
        "base_url": "https://api.anthropic.com/v1/messages",
        "env_key": "ANTHROPIC_API_KEY"
    },
    "deepseek": {
        "model": "deepseek-chat",
        "base_url": "https://api.deepseek.com/v1/chat/completions",
        "env_key": "DEEPSEEK_API_KEY"
    },
    "qwen": {
        "model": "qwen-plus",
        "base_url": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions",
        "env_key": "DASHSCOPE_API_KEY"
    },
    "gemini": {
        "model": "gemini-2.5-flash",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "env_key": "GEMINI_API_KEY"
    },
    "openai": {
        "model": "gpt-4o",
        "base_url": "https://api.openai.com/v1/chat/completions",
        "env_key": "OPENAI_API_KEY"
    },
    "ollama": {
        "model": "llama3:latest",
        "base_url": "http://localhost:11434/v1/chat/completions",
        "env_key": ""
    },
    "demo": {
        "model": "yerel-kural-motoru",
        "base_url": "",
        "env_key": ""
    }
}


def ayar_getir() -> dict:
    s = AKTIF_AYARLAR["saglayici"]
    cfg = SAGLAYICI_VARSAYILANLARI.get(s, SAGLAYICI_VARSAYILANLARI["claude"])
    key = AKTIF_AYARLAR["api_key"] or (os.environ.get(cfg["env_key"], "") if cfg["env_key"] else "")
    model = AKTIF_AYARLAR["model"] or cfg["model"]
    base_url = AKTIF_AYARLAR["base_url"] or cfg["base_url"]
    
    return {
        "saglayici": s,
        "model": model,
        "base_url": base_url,
        "api_key_mevcut": bool(key.strip()),
        "api_key_maskeli": f"{key[:4]}...{key[-4:]}" if len(key) > 8 else ("Var" if key else "Yok"),
        # P0-4: pilot kapsamı — yalnız Anthropic (ABD) ve yerel Ollama (KVKK m. 9 dostu).
        # DeepSeek/Qwen (Çin) gibi sağlayıcılar pilotta sunulmaz.
        "desteklenenler": ["claude", "ollama"]
    }


def ayar_guncelle(saglayici: str, model: str | None = None, api_key: str | None = None, base_url: str | None = None):
    izinli = ["claude", "ollama"]
    if os.environ.get("ZEKAI_TUM_SAGLAYICILAR") != "1":
        izinli = ["claude", "ollama"]  # P0-4: pilot kilidi (env ile açılabilir)
    if saglayici not in izinli:
        raise ValueError(f"Pilot kapsamında izinli değil: {saglayici} (izinli: {', '.join(izinli)})")
    AKTIF_AYARLAR["saglayici"] = saglayici
    cfg = SAGLAYICI_VARSAYILANLARI[saglayici]
    AKTIF_AYARLAR["model"] = model.strip() if model else cfg["model"]
    if api_key is not None:
        AKTIF_AYARLAR["api_key"] = api_key.strip()
    if base_url:
        AKTIF_AYARLAR["base_url"] = base_url.strip()
    elif saglayici in SAGLAYICI_VARSAYILANLARI:
        AKTIF_AYARLAR["base_url"] = cfg["base_url"]
    return ayar_getir()


def metin_oku(dosya_bytes: bytes, dosya_adi: str) -> str:
    """PDF / DOCX / TXT içeriğini metne çevirir."""
    ad = dosya_adi.lower()
    if ad.endswith(".pdf"):
        import io
        from pypdf import PdfReader
        okuyucu = PdfReader(io.BytesIO(dosya_bytes))
        sayfalar = []
        for i, sayfa in enumerate(okuyucu.pages, 1):
            sayfalar.append(f"[Sayfa {i}]\n{sayfa.extract_text() or ''}")
        return "\n\n".join(sayfalar)
    if ad.endswith(".docx"):
        import io
        from docx import Document
        doc = Document(io.BytesIO(dosya_bytes))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return dosya_bytes.decode("utf-8", errors="replace")


def _sistem_promptu() -> str:
    yol = os.path.abspath(SISTEM_PROMPTU_YOLU)
    if os.path.exists(yol):
        with open(yol, encoding="utf-8") as f:
            return f.read()
    return "Sen kıdemli bir Türk avukatısın. Verilen sözleşmeyi inceleyip yapılandırılmış JSON çıktısı üret."


def _json_ayikla(metin: str) -> dict:
    """Model yanıtından JSON bloğunu temizce ayıklar."""
    eslesme = re.search(r"\{.*\}", metin, re.DOTALL)
    if not eslesme:
        raise ValueError("Yapay zeka yanıtında geçerli bir JSON objesi bulunamadı")
    return json.loads(eslesme.group(0))


async def claude_cikarim(metin: str, model: str, api_key: str, base_url: str) -> dict:
    """Anthropic Claude API çağrısı."""
    import httpx
    metin = metin[:60000]
    url = base_url or "https://api.anthropic.com/v1/messages"
    async with httpx.AsyncClient(timeout=120) as istemci:
        yanit = await istemci.post(
            url,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": model,
                "max_tokens": 2048,
                "system": _sistem_promptu(),
                "messages": [{"role": "user", "content": metin}],
            },
        )
        yanit.raise_for_status()
        icerik = yanit.json()["content"][0]["text"]
    
    sonuc = _json_ayikla(icerik)
    sonuc["cikarim_yontemi"] = "claude"
    sonuc["model"] = model
    return sonuc


async def llm_uret(prompt: str, sistem: str = "", json_olsun: bool = False) -> tuple[Any, str, str]:
    """
    Tüm Zekai modülleri için genel amaçlı çoklu sağlayıcı LLM çıkarım fonksiyonu.
    Döner: (sonuc, yontem, model)
    """
    import httpx
    ayarlar = ayar_getir()
    saglayici = ayarlar["saglayici"]
    model = ayarlar["model"]
    base_url = ayarlar["base_url"]
    
    cfg = SAGLAYICI_VARSAYILANLARI.get(saglayici, {})
    api_key = AKTIF_AYARLAR["api_key"] or (os.environ.get(cfg.get("env_key", ""), "") if cfg.get("env_key") else "")
    
    if saglayici == "demo" or (saglayici != "ollama" and not api_key):
        return None, "demo", "yerel-kural-motoru"
        
    try:
        sistem_metni = sistem or "Sen Türk Hukukunda uzman, kıdemli bir hukuk müşaviri ve avukatsın."
        if json_olsun:
            sistem_metni += "\nCevabını yalnızca ve kesinlikle geçerli bir JSON objesi veya listesi olarak ver. Markdown kod bloğu (```json) veya fazladan açıklama metni ekleme."
            
        icerik_metin = ""
        if saglayici == "claude":
            url = base_url or "https://api.anthropic.com/v1/messages"
            async with httpx.AsyncClient(timeout=120) as istemci:
                yanit = await istemci.post(
                    url,
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": model,
                        "max_tokens": 4096,
                        "system": sistem_metni,
                        "messages": [{"role": "user", "content": prompt[:60000]}],
                    },
                )
                yanit.raise_for_status()
                icerik_metin = yanit.json()["content"][0]["text"]
        else:
            headers = {"content-type": "application/json"}
            if api_key:
                headers["authorization"] = f"Bearer {api_key}"
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": sistem_metni},
                    {"role": "user", "content": prompt[:60000]}
                ],
                "temperature": 0.2
            }
            if json_olsun and saglayici in ("openai", "deepseek", "gemini"):
                payload["response_format"] = {"type": "json_object"}
                
            async with httpx.AsyncClient(timeout=120) as istemci:
                yanit = await istemci.post(base_url, headers=headers, json=payload)
                yanit.raise_for_status()
                icerik_metin = yanit.json()["choices"][0]["message"]["content"]
                
        if json_olsun:
            # Temiz JSON ayıkla
            eslesme = re.search(r"(\[.*\]|\{.*\})", icerik_metin, re.DOTALL)
            if eslesme:
                return json.loads(eslesme.group(0)), saglayici, model
            return json.loads(icerik_metin), saglayici, model
            
        return icerik_metin.strip(), saglayici, model
        
    except Exception as e:
        print(f"[LLM ÇAĞRI HATASI] {saglayici} ({model}): {e}")
        return None, "demo", f"hata: {str(e)[:100]}"


async def openai_uyumlu_cikarim(metin: str, model: str, api_key: str, base_url: str, saglayici_adi: str) -> dict:
    """DeepSeek, Qwen (DashScope), Gemini, OpenAI veya Ollama için standart çağrı."""
    import httpx
    metin = metin[:60000]
    headers = {"content-type": "application/json"}
    if api_key:
        headers["authorization"] = f"Bearer {api_key}"
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": _sistem_promptu() + "\nCevabını yalnızca saf geçerli JSON olarak ver, fazladan markdown veya açıklama ekleme."},
            {"role": "user", "content": metin}
        ],
        "temperature": 0.2
    }
    
    # Destekleyen modellerde json_object formatı iste
    if saglayici_adi in ("openai", "deepseek", "gemini"):
        payload["response_format"] = {"type": "json_object"}

    async with httpx.AsyncClient(timeout=120) as istemci:
        yanit = await istemci.post(base_url, headers=headers, json=payload)
        yanit.raise_for_status()
        veri = yanit.json()
        icerik = veri["choices"][0]["message"]["content"]

    sonuc = _json_ayikla(icerik)
    sonuc["cikarim_yontemi"] = saglayici_adi
    sonuc["model"] = model
    return sonuc


async def analiz_yap(dosya_bytes: bytes, dosya_adi: str, maskele_kvkk: bool = True) -> dict:
    """
    Ana çıkarım fonksiyonu: Belgeyi seçilen modele gönderir.
    Hata veya anahtar eksikliğinde otomatik yerel regex çıkarımına düşer.

    KVKK / güvenlik (Talimat 5.3 + Bölüm 3):
    - maskele_kvkk=True (varsayılan): TCKN/IBAN/tel/e-posta LLM'e gitmeden maskelenir,
      yanıt dönerken geri açılır (harita yalnız bellekte).
    - Belge metni ayrıca rastgele hex çitle sarılır (DATA_RULE — enjeksiyon savunması).
    """
    metin = metin_oku(dosya_bytes, dosya_adi)
    ham_uzunluk = len(metin)
    ayarlar = ayar_getir()
    saglayici = ayarlar["saglayici"]
    model = ayarlar["model"]
    base_url = ayarlar["base_url"]

    # Gerçek API anahtarını çöz
    cfg = SAGLAYICI_VARSAYILANLARI.get(saglayici, {})
    api_key = AKTIF_AYARLAR["api_key"] or (os.environ.get(cfg.get("env_key", ""), "") if cfg.get("env_key") else "")

    harita: dict = {}
    kvkk_uygulandi = False
    if maskele_kvkk and saglayici != "demo":
        m_sonuc = maskele(metin)
        metin = guvenli_veri_citi("BELGE METNI", m_sonuc.maskeli_metin)
        harita = m_sonuc.harita
        kvkk_uygulandi = bool(harita)

    ZORUNLU = ("ad", "karsi_taraf")

    if saglayici != "demo":
        try:
            if saglayici == "claude" and api_key:
                sonuc = await claude_cikarim(metin, model, api_key, base_url)
                # Şema doğrulama + tek retry (Talimat 5.3: şemaya uymayan sessizce kırpılmaz)
                eksik = [a for a in ZORUNLU if a not in sonuc or sonuc[a] in (None, "")]
                if eksik and "otomatik_uzatma" not in sonuc:
                    yeniden = await claude_cikarim(
                        metin + "\n\n(ÖNCEKİ YANIT ŞEMAYA UYMADI — yalnızca belirtilen JSON şemasını döndür.)",
                        model, api_key, base_url)
                    if all(a in yeniden for a in ZORUNLU):
                        sonuc = yeniden
            elif saglayici in ("deepseek", "qwen", "gemini", "openai") and api_key:
                sonuc = await openai_uyumlu_cikarim(metin, model, api_key, base_url, saglayici)
            elif saglayici == "ollama":  # Ollama yerelde çalıştığı için api_key zorunlu değil
                sonuc = await openai_uyumlu_cikarim(metin, model, api_key, base_url, "ollama")
            else:
                raise ValueError(f"Sağlayıcı anahtarı yok: {saglayici}")
            if harita:
                sonuc = _unmask_derin(sonuc, harita)
            return sonuc
        except Exception as hata:
            sonuc = demo_cikarim(metin_oku(dosya_bytes, dosya_adi))  # çitsiz ham metinle demo
            sonuc["cikarim_yontemi"] = "demo"
            sonuc["cikarim_notu"] = (
                f"{saglayici.upper()} ({model}) çağrısı başarısız ({type(hata).__name__}: {str(hata)[:120]}); "
                "yerel yedek kural çıkarımı kullanıldı."
            )
            if ham_uzunluk > 60000:
                sonuc["cikarim_notu"] += f" Belge {ham_uzunluk} karakterdir; ilk 60.000 karakter analiz edildi, KALANI OKUNMADI."
            return sonuc

    # Varsayılan / Anahtar yoksa: Demo Kural Motoru
    sonuc = demo_cikarim(metin_oku(dosya_bytes, dosya_adi))
    sonuc["cikarim_yontemi"] = "demo"
    sonuc.setdefault(
        "cikarim_notu",
        f"{saglayici.upper()} API anahtarı tanımlı değil — yerel kural motoru (kalıp eşleme) kullanıldı."
    )
    if ham_uzunluk > 60000:
        sonuc["cikarim_notu"] += f" Belge {ham_uzunluk} karakterdir; ilk 60.000 karakter analiz edildi, KALANI OKUNMADI."
    return sonuc


def _unmask_derin(obj: Any, harita: dict) -> Any:
    """LLM yanıtındaki tüm dize alanlarında [TCKN-1] vb. yer tutucuları geri açar (özyinelemeli)."""
    if isinstance(obj, str):
        return maskeleri_geri_ac(obj, harita)
    if isinstance(obj, list):
        return [_unmask_derin(o, harita) for o in obj]
    if isinstance(obj, dict):
        return {k: _unmask_derin(v, harita) for k, v in obj.items()}
    return obj


async def test_baglanti(saglayici: str, model: str, api_key: str, base_url: str) -> dict:
    """Sağlayıcı bağlantısını test eder."""
    import httpx
    test_metin = "İşbu Sözleşme 01.01.2026 tarihinde akdedilmiştir. Taraflar: A Ltd. ve B A.Ş. Süre 1 yıldır."
    try:
        if saglayici == "claude":
            yanit = await claude_cikarim(test_metin, model, api_key, base_url)
        elif saglayici in ("deepseek", "qwen", "gemini", "openai", "ollama"):
            yanit = await openai_uyumlu_cikarim(test_metin, model, api_key, base_url, saglayici)
        else:
            return {"durum": "ok", "mesaj": "Yerel demo motoru hazır."}
        return {"durum": "ok", "mesaj": f"{saglayici.upper()} ({model}) bağlantısı başarılı!", "ornek": yanit.get("sozlesme_turu", "Tamam")}
    except Exception as e:
        return {"durum": "hata", "mesaj": f"Bağlantı başarısız: {type(e).__name__}: {str(e)}"}


# ---------------------------------------------------------------- canlı model keşfi (P1)

MODELLER_UCLARI = {
    "claude": "https://api.anthropic.com/v1/models",
    "ollama": "http://localhost:11434/v1/models",
}


async def modelleri_getir(saglayici: str, api_key: str = "", base_url: str = "") -> dict:
    """Sağlayıcının canlı /v1/models listesini çeker (kullanıcının anahtarıyla).
    Anahtar verilmediyse kayıtlı anahtar kullanılır; ollama anahtarsız çalışır."""
    import httpx
    cfg = SAGLAYICI_VARSAYILANLARI.get(saglayici, {})
    anahtar = api_key or AKTIF_AYARLAR["api_key"] or (
        os.environ.get(cfg.get("env_key", ""), "") if cfg.get("env_key") else "")
    url = base_url or MODELLER_UCLARI.get(saglayici)
    if not url:
        return {"modeller": [], "hata": f"{saglayici} için keşif ucu tanımlı değil"}

    try:
        basliklar = {"content-type": "application/json"}
        if anahtar:
            basliklar["authorization"] = f"Bearer {anahtar}"
        if saglayici == "claude":
            basliklar["x-api-key"] = anahtar
        async with httpx.AsyncClient(timeout=30) as istemci:
            yanit = await istemci.get(url, headers=basliklar)
            yanit.raise_for_status()
            veri = yanit.json()

        modeller = []
        for m in veri.get("data", []):
            kimlik = m.get("id") or m.get("name") or ""
            if kimlik:
                modeller.append(kimlik)
        return {"modeller": sorted(modeller), "adet": len(modeller), "hata": None}
    except Exception as hata:
        return {"modeller": [], "hata": f"{type(hata).__name__}: {str(hata)[:140]}"}
