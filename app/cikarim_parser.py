"""Demo çıkarımı: Türkçe sözleşme metninden kalıp eşleme ile alan çıkarımı.
Bu bir LLM DEĞİLDİR — bilinen kalıpları arar; bulamadıklarını 'Bulunamadı'
olarak raporlar (hücre dürüstlük taksonomisi: negatif bulgu + arama kapsamı).
"""
from __future__ import annotations

import re

KELIME_SAYI = {
    "bir": 1, "iki": 2, "üç": 3, "dört": 4, "beş": 5, "altı": 6, "yedi": 7,
    "sekiz": 8, "dokuz": 9, "on": 10, "yirmi": 20, "otuz": 30, "kırk": 40,
    "elli": 50, "altmış": 60, "yetmiş": 70, "seksen": 80, "doksan": 90,
}
ONLULAR = ("on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan")
HARF = r"[a-zçğıöşüA-ZÇĞİÖŞÜ]"


def kelime_sayi(m) -> int | None:
    """Regex eşleşmesinden sayı çıkarır: rakam grubu öncelikli, yoksa kelime
    grubu ('doksan', 'on iki' gibi)."""
    if m.groupdict().get("rakam"):
        return int(m.group("rakam"))
    kelime = (m.groupdict().get("kelime") or "").lower().strip()
    if not kelime:
        return None
    if kelime in KELIME_SAYI:
        return KELIME_SAYI[kelime]
    parcalar = kelime.split()
    if len(parcalar) == 2 and parcalar[0] in ONLULAR and parcalar[1] in KELIME_SAYI \
            and KELIME_SAYI[parcalar[1]] < 10:
        return KELIME_SAYI[parcalar[0]] + KELIME_SAYI[parcalar[1]]
    return None


KALIPLAR = {
    "otomatik_uzatma": re.compile(
        r"(kendili[ğg]inden uzar|ayn[ıi] s[üu]relerle uzat|otomatik(?:man)? olarak uzat|"
        r"yenilenmi[şs] say[ıi]l[ıi]r|uzat[ıi]lm[ıi][şs] say[ıi]l[ıi]r)", re.IGNORECASE),
    # ihbar: rakam veya kelime sayısı + birim + "önce" (ör. "doksan (90) gün önce", "on iki ay önce")
    "ihbar_suresi": re.compile(
        rf"(?:(?P<kelime>{HARF}+(?:\s+{HARF}+)?)\s*)?\(?(?P<rakam>\d{{1,3}})\)?\s*"
        r"(?:\(\w+\)\s*)?(g[üu]n|hafta|ay)\s+[öo]nce", re.IGNORECASE),
    "ihbar_suresi_kelime": re.compile(
        rf"(?P<kelime>{ONLULAR[0]}|{ONLULAR[1]}|{ONLULAR[2]}|{ONLULAR[3]}|{ONLULAR[4]}|"
        rf"{ONLULAR[5]}|{ONLULAR[6]}|{ONLULAR[7]}|{ONLULAR[8]})"
        rf"(?:\s+(?P<tek>[bB]ir|[iI]ki|[üÜ]ç|[dD]ört|[bB]eş|[aA]ltı|[yY]edi|[sS]ekiz|[dD]okuz))?\s*"
        rf"(?P<birim>g[üu]n|hafta|ay)\s+[öo]nce"),
    "noter": re.compile(r"noter(?:den|kanal[ıi]| arac[ıi]l[ıi][ğg][ıi]yla)", re.IGNORECASE),
    "kep": re.compile(r"kay[ıi]tl[ıi] elektronik posta|KEP\b", re.IGNORECASE),
    "yazili": re.compile(r"yaz[ıi]l[ıi] (?:olarak )?bildir|yaz[ıi]l[ıi] ihbar|fesih bildirimi", re.IGNORECASE),
    "baslangic_tarihi": re.compile(
        r"(?:y[üu]r[üu]rl[üu][ğg]e girer|ba[şs]lar|geçerli olmak)\D{0,40}(\d{1,2})[./](\d{1,2})[./](\d{4})", re.IGNORECASE),
    "sure_yil": re.compile(
        rf"(?:(?P<kelime>{HARF}+(?:\s+{HARF}+)?)\s*)?\(?(?P<rakam>\d{{1,2}})\)?\s*"
        r"(?:\(\w+\)\s*)?y[ıi]l(?:l[ıi]k)?(?:\s*lik)?\s*(?:bir\s*)?(?:s[üu]re|d[öo]nem)", re.IGNORECASE),
    "sure_aylik": re.compile(
        rf"(?:(?P<kelime>{HARF}+(?:\s+{HARF}+)?)\s*)?\(?(?P<rakam>\d{{1,3}})\)?\s*"
        r"(?:\(\w+\)\s*)?ay(?:l[ıi]k)?\s*(?:bir\s*)?(?:s[üu]re|d[öo]nem)", re.IGNORECASE),
    "artis": re.compile(r"%\s*(\d{1,2})|\b(\d{1,2})\s*(?:y[üu]zde)", re.IGNORECASE),
}


def satir_alinti(metin: str, pos: int, max_len=340) -> tuple[str, str]:
    """Eşleşme konumunun bulunduğu paragrafı döndürür (madde numarasıyla)."""
    blok_bas = metin.rfind("\n\n", 0, pos)
    blok_bas = blok_bas + 2 if blok_bas != -1 else 0
    blok_son = metin.find("\n\n", pos)
    blok = metin[blok_bas: blok_son if blok_son != -1 else len(metin)].strip()
    if not blok:
        satir_bas = metin.rfind("\n", 0, pos) + 1
        satir_son = metin.find("\n", pos)
        blok = metin[satir_bas: satir_son if satir_son != -1 else len(metin)].strip()
    m = re.search(r"(?:^|\n)\s*(\d+(?:\.\d+)*)[\s.-]", blok)
    return blok[:max_len], (m.group(1) if m else "")


def demo_cikarim(metin: str) -> dict:
    """Metinden alanları kalıp eşlemeyle çıkarır; her alanın kaynağını yazar."""
    sonuc: dict = {
        "ad": "Bulunamadı", "karsi_taraf": "Bulunamadı", "tur": "Bulunamadı",
        "baslangic": None, "sure_ay": None,
        "otomatik_uzatma": None, "uzatma_suresi_ay": None, "uzatma_artis_yuzdesi": None,
        "ihbar_deger": None, "ihbar_birim": None, "ihbar_sekli": None,
        "kaynak_alinti": "", "kaynak_madde": "", "kaynak_sayfa": "",
        "arama_kapsami": [], "alan_kaynaklari": {},
    }
    if not metin.strip():
        sonuc["cikarim_notu"] = "Belge boş veya metni okunamadı (taramalı PDF olabilir — OCR gerekir)."
        return sonuc

    # Otomatik uzatma
    m = KALIPLAR["otomatik_uzatma"].search(metin)
    if m:
        sonuc["otomatik_uzatma"] = True
        alinti, madde = satir_alinti(metin, m.start())
        sonuc["kaynak_alinti"] = alinti
        sonuc["kaynak_madde"] = madde
        sonuc["alan_kaynaklari"]["otomatik_uzatma"] = alinti[:120]

    # İhbar süresi (öncelik: rakamlı kalıp > kelime sayılı kalıp; birim eşleşmeden)
    m = KALIPLAR["ihbar_suresi"].search(metin)
    sayi = kelime_sayi(m) if m else None
    if not sayi:
        m = KALIPLAR["ihbar_suresi_kelime"].search(metin)
        sayi = kelime_sayi(m) if m else None
    if m and sayi:
        birim = (m.groupdict().get("birim") or "").lower()
        sonuc["ihbar_deger"] = sayi
        sonuc["ihbar_birim"] = {"gün": "gün", "ay": "ay", "hafta": "hafta"}.get(birim, "gün")
        alinti, madde = satir_alinti(metin, m.start())
        if not sonuc["kaynak_alinti"]:
            sonuc["kaynak_alinti"] = alinti
            sonuc["kaynak_madde"] = madde
        sonuc["alan_kaynaklari"]["ihbar_suresi"] = m.group(0)

    # İhbar şekli
    if KALIPLAR["noter"].search(metin):
        sonuc["ihbar_sekli"] = "Noter"
        sonuc["alan_kaynaklari"]["ihbar_sekli"] = "Metinde 'noter' ifadesi bulundu"
    elif KALIPLAR["kep"].search(metin):
        sonuc["ihbar_sekli"] = "KEP"
        sonuc["alan_kaynaklari"]["ihbar_sekli"] = "Metinde KEP atfı bulundu (TTK m. 18/3 uyumlu)"
    elif KALIPLAR["yazili"].search(metin):
        sonuc["ihbar_sekli"] = "Yazılı"
        sonuc["alan_kaynaklari"]["ihbar_sekli"] = "Metinde 'yazılı bildirim' ifadesi bulundu"

    # Süre
    m = KALIPLAR["sure_yil"].search(metin)
    sayi = kelime_sayi(m) if m else None
    if sayi:
        sonuc["sure_ay"] = sayi * 12
        sonuc["alan_kaynaklari"]["sure"] = m.group(0)
    else:
        m = KALIPLAR["sure_aylik"].search(metin)
        sayi = kelime_sayi(m) if m else None
        if sayi:
            sonuc["sure_ay"] = sayi
            sonuc["alan_kaynaklari"]["sure"] = m.group(0)

    # Başlangıç tarihi
    m = KALIPLAR["baslangic_tarihi"].search(metin)
    if m:
        g, a, y = m.group(1), m.group(2), m.group(3)
        sonuc["baslangic"] = f"{y}-{int(a):02d}-{int(g):02d}"
        sonuc["alan_kaynaklari"]["baslangic"] = m.group(0)

    # Artış yüzdesi (uzatma dönemlerinde)
    uzatma_bolgesi = metin
    if sonuc["kaynak_alinti"]:
        idx = metin.find(sonuc["kaynak_alinti"][:60])
        if idx >= 0:
            uzatma_bolgesi = metin[idx: idx + 400]
    m = KALIPLAR["artis"].search(uzatma_bolgesi)
    if m:
        sonuc["uzatma_artis_yuzdesi"] = float(m.group(1) or m.group(2))

    # Otomatik uzatma süresi: "aynı sürelerle" → sözleşme süresiyle aynı
    if sonuc["otomatik_uzatma"] and sonuc["sure_ay"]:
        if re.search(r"ayn[ıi] s[üu]relerle", metin, re.IGNORECASE):
            sonuc["uzatma_suresi_ay"] = sonuc["sure_ay"]

    # Arama kapsamı raporu (dürüstlük)
    sonuc["arama_kapsami"] = [
        "Otomatik uzatma kalıpları (kendiliğinden uzar / yenilenmiş sayılır)",
        "İhbar süresi kalıpları (gün/hafta/ay önce bildirim)",
        "Bildirim şekli kalıpları (noter / KEP / yazılı)",
        "Süre kalıpları (X yıllık / X aylık dönem)",
    ]
    if sonuc["otomatik_uzatma"] is None:
        sonuc["cikarim_notu"] = (
            "Otomatik uzatma hükmü bulunamadı: 'uzat', 'yenilenmiş sayılır' kalıplarının "
            "hiçbiri metinde geçmiyor. Sözleşme ya sabit süreli ya da farklı ifade kullanıyor — "
            "madde metnini elle kontrol edin."
        )
    return sonuc
