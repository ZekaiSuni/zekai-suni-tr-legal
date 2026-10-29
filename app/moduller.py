"""Tüm modüllerin API uçları. Her modül: liste + kaydet + versiyonlu export.
Ortak desenler: örnek veri çipi, provenance, insan onayı isim+tarih, sorumluluk şeridi."""
from __future__ import annotations

import re
from datetime import date

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.db import Oturum
from app.modeller import (AIKullanim, AISatici, Atif, AtifBelgesi, Basvuru, Dosya, Girdi,
                          MevzuatKayit, MusteriKayit, Olay, PlaybookPozisyon, QAAlıcı, QASoru,
                          SozlesmeMaddesi, TabloInceleme, Talep, IncelemeSatiri)
from app.sure_motoru import hesapla
from app.kvkk_maskeleme import hazir_girdi, unmask_derin
from app.ortak_muhur import muhur_hesapla

r = APIRouter(prefix="/api")
FERAGAT = "Bu içerik hukuki görüş değildir; güvenilmeden önce bir avukat tarafından gözden geçirilmelidir."


def _db():
    return Oturum()


def _veriler(model):
    with _db() as db:
        return [k for k in db.query(model).all()]


def _sozlukler(kayitlar):
    return [k.__dict__ | {"_ok": True} for k in kayitlar]  # SQLAlchemy obj -> attribute erişimi frontend'e JSON olarak verilecek


def _jsonla(kayitlar, alanlar):
    cikti = []
    for k in kayitlar:
        d = {a: getattr(k, a) for a in alanlar}
        for a, v in list(d.items()):
            if hasattr(v, "isoformat"):
                d[a] = v.isoformat()
        cikti.append(d)
    return cikti


# ============================================================ PLAYBOOK

@r.get("/playbook")
def playbook_liste():
    pozisyonlar = _jsonla(_veriler(PlaybookPozisyon),
                          ["id", "madde_adi", "standart_metin", "fallback_metin", "kirmizi_cizgi",
                           "imza_gerekir_fallback", "imza_gerekmez_standart"])
    maddeler = _jsonla(_veriler(SozlesmeMaddesi),
                       ["id", "sozlesme_adi", "karsi_taraf", "biz_kimiz", "kagit_kimi", "madde_adi",
                        "durum", "sozlesme_alinti", "madde_no", "sayfa", "onerilen_duzenleme",
                        "karsi_tarafa_not", "playbook_eslesen", "imza_gerekir", "karar",
                        "kararin_kimi", "dosya_adi", "playbook_disi"])
    sozlesmeler = {}
    for m in maddeler:
        sozlesmeler.setdefault(m["sozlesme_adi"], {"karsi_taraf": m["karsi_taraf"], "maddeler": {}})
        sozlesmeler[m["sozlesme_adi"]]["maddeler"][m["madde_adi"]] = m
    sapma = sum(1 for m in maddeler if m["durum"] in ("Sapma", "Kabul edilemez"))
    bekleyen = sum(1 for m in maddeler if not m["karar"] and m["durum"] in ("Sapma", "Kabul edilemez", "Fallback 1"))
    return {"pozisyonlar": pozisyonlar, "maddeler": maddeler, "sozlesmeler": sozlesmeler,
            "ozet": {"sozlesme": len(sozlesmeler), "sapma": sapma, "bekleyen": bekleyen},
            "feragat": FERAGAT}


class MaddeGuncelle(BaseModel):
    karar: str | None = None
    kararin_kimi: str | None = None
    onerilen_duzenleme: str | None = None
    karsi_tarafa_not: str | None = None
    durum: str | None = None


class PozisyonEkle(BaseModel):
    madde_adi: str
    standart_metin: str = ""
    fallback_metin: str = ""
    kirmizi_cizgi: str = ""


class PozisyonSil(BaseModel):
    id: int


@r.post("/playbook/pozisyon-ekle")
def playbook_pozisyon_ekle(p: PozisyonEkle):
    with _db() as db:
        mevcut = db.query(PlaybookPozisyon).filter(PlaybookPozisyon.madde_adi == p.madde_adi.strip()).first()
        if mevcut:
            return {"durum": "mevcut", "id": mevcut.id, "madde_adi": mevcut.madde_adi}
        yeni = PlaybookPozisyon(
            madde_adi=p.madde_adi.strip(),
            standart_metin=p.standart_metin.strip() or f"{p.madde_adi} konusunda şirket standart kuralı ve politikası.",
            fallback_metin=p.fallback_metin.strip() or f"{p.madde_adi} alternatif koruyucu karşı hüküm taslağı.",
            kirmizi_cizgi=p.kirmizi_cizgi.strip() or f"{p.madde_adi} konusunda ağır aleyhe ve telafisiz şartlar kabul edilemez."
        )
        db.add(yeni)
        db.commit()
        db.refresh(yeni)
        return {"durum": "ok", "id": yeni.id, "madde_adi": yeni.madde_adi}


@r.post("/playbook/pozisyon-sil")
def playbook_pozisyon_sil(p: PozisyonSil):
    with _db() as db:
        poz = db.get(PlaybookPozisyon, p.id)
        if not poz:
            raise HTTPException(404, "Sütun/madde bulunamadı")
        madde_adi = poz.madde_adi
        db.query(SozlesmeMaddesi).filter(SozlesmeMaddesi.madde_adi == madde_adi).delete()
        db.delete(poz)
        db.commit()
        return {"durum": "ok", "silinen": madde_adi}


@r.post("/playbook/madde/{madde_id}")
def playbook_guncelle(madde_id: int, g: MaddeGuncelle):
    with _db() as db:
        m = db.get(SozlesmeMaddesi, madde_id)
        if not m:
            raise HTTPException(404)
        for alan, deger in g.model_dump(exclude_unset=True).items():
            setattr(m, alan, deger if deger is not None else getattr(m, alan))
        if g.karar:
            m.kararin_kimi = g.kararin_kimi or "Hukuk"
            if g.karar in ("Onaylandı", "Editör kabul etti"):
                m.muhur = muhur_hesapla(m.sozlesme_alinti or m.madde_adi, m.kararin_kimi, date.today().isoformat())
        db.commit()
        return {"durum": "ok", "muhur": m.muhur or None}
    return {"durum": "ok"}


@r.get("/playbook/export.json")
def playbook_export():
    veri = playbook_liste()
    return {"format": "zekai-playbook-panosu/v1", "feragat": FERAGAT,
            "pozisyonlar": veri["pozisyonlar"], "maddeler": veri["maddeler"]}


# ============================================================ HUKUK MASASI

@r.get("/masa")
def masa_liste():
    girdiler = _jsonla(_veriler(Girdi),
                       ["id", "baslik", "metin", "kategori", "onay_durumu", "onay_tarihi",
                        "gecerlilik_tarihi", "sahip", "is_birlikleriyle_paylas", "anahtar_kelimeler"])
    talepler = _jsonla(_veriler(Talep),
                       ["id", "baslik", "soran_ad", "bolum", "kategori", "metin", "alanlar", "risk",
                        "hassas", "uzmanlik", "atanan", "durum", "olusturma", "gerek_tarih", "taslak",
                        "taslak_turu", "dayanilan_girdiler", "muhakeme_izi", "eksikler",
                        "karar_cagrilari", "gonderen_kimlikle", "cevap", "takip_notu"])
    onay_bekleyen = sum(1 for g in girdiler if g["onay_durumu"] == "Taslak")
    return {"girdiler": girdiler, "talepler": talepler, "onay_bekleyen_girdi": onay_bekleyen,
            "avukatsiz_orani": None,  # ölçüm için veri yok — sahte metrik gösterilmez
            "feragat": FERAGAT}


class GirdiOnay(BaseModel):
    girdi_id: int
    karar: str  # Onayla / Reddet
    kimi: str = "Hukuk"


@r.post("/masa/girdi/onayla")
def masa_girdi_onay(g: GirdiOnay):
    with _db() as db:
        kayit = db.get(Girdi, g.girdi_id)
        if not kayit:
            raise HTTPException(404)
        if g.karar == "Onayla":
            kayit.onay_durumu = "Onaylı"
            kayit.onay_tarihi = date.today()
            kayit.gecerlilik_tarihi = date.fromordinal(date.today().toordinal() + 180)
            kayit.sahip = g.kimi or kayit.sahip  # P0-4: onaylayan kişi kayda geçer
        else:
            kayit.onay_durumu = "Reddedildi"
        db.commit()
    return {"durum": "ok", "onaylayan": g.kimi}


class TalepKarar(BaseModel):
    talep_id: int
    islem: str  # gonder / bilgi_iste / kaydet_cevap
    cevap: str = ""
    kimi: str = "Hukuk"


@r.post("/masa/talep/karar")
def masa_talep_karar(g: TalepKarar):
    with _db() as db:
        t = db.get(Talep, g.talep_id)
        if not t:
            raise HTTPException(404)
        if g.islem == "gonder":
            t.cevap = g.cevap or t.taslak
            t.gonderen_kimlikle = g.kimi or t.gonderen_kimlikle or "Hukuk"
            t.durum = "Kapatıldı"
        elif g.islem == "bilgi_iste":
            t.durum = "Bilgi bekliyor"
        elif g.islem == "kaydet_cevap":
            t.cevap = g.cevap
        db.commit()
    return {"durum": "ok"}


@r.get("/masa/export.json")
def masa_export():
    return {"format": "zekai-hukuk-masasi/v1", "feragat": FERAGAT,
            "veriler": masa_liste()}


# ============================================================ TABLO İNCELEME

@r.get("/inceleme")
def inceleme_liste():
    incelemeler = _jsonla(_veriler(TabloInceleme), ["id", "ad"])
    with _db() as db:
        satirlar = _jsonla(db.query(TabloInceleme).all() and db.query(__import__("app.modeller", fromlist=["IncelemeSatiri"]).IncelemeSatiri).all(),
                           ["id", "inceleme_id", "belge_adi", "karsi_taraf", "sozlesme_turu", "yururluk",
                            "bitis_sure", "otomatik_uzatma", "taban_hukuk", "kontrol_degisikligi",
                            "devir", "sorumluluk_tavani", "mali_yukumluluk", "notlar", "ciddi_konu",
                            "okunmayan_sayfa", "inceleme_gerekli", "sahibi"])
    return {"incelemeler": incelemeler, "satirlar": satirlar, "feragat": FERAGAT}


# ============================================================ DOSYA PANOSU

@r.get("/dosya")
def dosya_liste():
    kayitlar = _veriler(Dosya)
    bugun = date.today()
    cikti = []
    for d in kayitlar:
        geciken = d.sonraki_tarih and d.sonraki_tarih < bugun
        kalan = (d.sonraki_tarih - bugun).days if d.sonraki_tarih else None
        zam_gun = (d.zamanasimi_tarihi - bugun).days if d.zamanasimi_tarihi else None
        cikti.append(_jsonla([d], ["id", "ad", "musteri", "karsi_taraf", "alan_kodu", "asama",
                                   "sonraki_islem", "sonraki_tarih", "ikinci_islem", "ikinci_tarih",
                                   "sahibi", "inceleme", "tarih_teyit", "zamanasimi_tarihi", "orijinal_ornek"])[0] | {
            "geciken": bool(geciken), "kalan_gun": kalan,
            "zamanaasimi_gun": zam_gun, "zamanaasimi_gecisti": bool(zam_gun is not None and zam_gun < 0)})
    asamalar = ["Aşamasız", "Yeni", "Aktif", "Başkalarını bekliyor", "Kapatıldı"]
    return {"dosyalar": cikti, "asamalar": asamalar,
            "ozet": {"acik": len([d for d in cikti if d["asama"] != "Kapatıldı"]),
                     "dikkat": len([d for d in cikti if d["geciken"] or d["inceleme"]]),
                     "geciken": len([d for d in cikti if d["geciken"]])},
            "feragat": FERAGAT}


class DosyaGuncelle(BaseModel):
    id: int
    asama: str | None = None
    sonraki_islem: str | None = None
    sonraki_tarih: str | None = None
    sahibi: str | None = None


@r.post("/dosya/guncelle")
def dosya_guncelle(g: DosyaGuncelle):
    with _db() as db:
        d = db.get(Dosya, g.id)
        if not d:
            raise HTTPException(404)
        if g.asama:
            d.asama = g.asama
        if g.sonraki_islem is not None:
            d.sonraki_islem = g.sonraki_islem
        if g.sonraki_tarih:
            d.sonraki_tarih = date.fromisoformat(g.sonraki_tarih)
        if g.sahibi is not None:
            d.sahibi = g.sahibi
        db.commit()
    return {"durum": "ok"}


# ============================================================ MÜVEKKİL KABULÜ

@r.get("/kabul")
def kabul_liste():
    kayitlar = _jsonla(_veriler(MusteriKayit), ["id", "ad", "tur", "neden", "dosya"])
    basvurular = _jsonla(_veriler(Basvuru),
                         ["id", "ad", "konu_turu", "tek_satir", "iliskili", "iletisim", "kaynak",
                          "asama", "catisma_durumu", "catisma_notu", "bekleyen_gun", "zekai_ekledi"])
    asamalar = ["Yeni", "Çatışma", "Karar", "Mektup", "İmzalı", "Açık", "Reddedildi"]
    return {"indeks": kayitlar, "basvurular": basvurular, "asamalar": asamalar,
            "feragat": FERAGAT}


class BasvuruAsama(BaseModel):
    id: int
    asama: str
    catisma_durumu: str | None = None
    catisma_notu: str | None = None


@r.post("/kabul/guncelle")
def kabul_guncelle(g: BasvuruAsama):
    with _db() as db:
        b = db.get(Basvuru, g.id)
        if not b:
            raise HTTPException(404)
        b.asama = g.asama
        if g.catisma_durumu:
            b.catisma_durumu = g.catisma_durumu
        if g.catisma_notu is not None:
            b.catisma_notu = g.catisma_notu
        db.commit()
    return {"durum": "ok"}


@r.post("/kabul/catisma-tara")
def catisma_tara(basvuru_id: int):
    """Demo çatışma taraması: iliskili kişileri indekste kelime bazında arar.
    Gerçek tarama: tam ad + unvan varyantları + grup şirketleri; bu demo
    basit benzerlik kullanır ve sonucu 'Avukat incelemesi'ne düşürür."""
    with _db() as db:
        b = db.get(Basvuru, basvuru_id)
        if not b:
            raise HTTPException(404)
        def tr_lower(s):
            # P1: Türkçe I/İ doğru küçültme — .lower() "KILIÇ"→"kiliç" değil "kili\u0307ç" üretir
            return (s or "").replace("I", "ı").replace("İ", "i").lower()
        bulunan = []
        for d in db.query(Dosya).all():
            if d.karsi_taraf and tr_lower(d.karsi_taraf) in tr_lower(b.iliskili):
                bulunan.append({"kayit": d.karsi_taraf, "tur": "Açık dosyanın karşı tarafı",
                                "neden": f"Açık dosya: {d.ad} (Av.K. m. 38 hasımlık riski)", "dosya": d.ad})
        for k in db.query(MusteriKayit).all():
            kok = tr_lower(k.ad.split()[0])
            if len(kok) >= 4 and kok in tr_lower(b.iliskili):
                bulunan.append({"kayit": k.ad, "tur": k.tur, "neden": k.neden, "dosya": k.dosya})
        if not bulunan:
            b.catisma_durumu = "Temiz"
            b.catisma_notu = "İndeks taraması isabet bulmadı (demo tarama: kelime kökü eşleşmesi)."
        elif len(bulunan) == 1 and bulunan[0]["tur"] == "Müşteri":
            b.catisma_durumu = "1 isabet"
            b.catisma_notu = f"Eşleşme: {bulunan[0]['kayit']} — {bulunan[0]['neden']}. Aynı taraf mı, grup mu? Avukat karar verecek."
        else:
            b.catisma_durumu = "Muhtemel çatışma"
            b.catisma_notu = "; ".join(f"{b_['kayit']} ({b_['tur']}): {b_['neden']}" for b_ in bulunan) + \
                ". Hasımlık değerlendirmesi avukatın."
        db.commit()
        return {"durum": "ok", "bulunan": bulunan,
                "not": "Demo tarama — kelime kökü eşleşmesi. Gerçek taramada unvan varyantları, grup şirketleri ve geçmiş dosyalar kapsanır."}


# ============================================================ ATIF DENETİMİ

ATIF_KALIP = re.compile(
    r"(Yarg[ıi]\.?tay)?\s*(\d{1,2})\.\s*H(?:ukuk)?\s*D\.?|"
    r"(Dan[ıi][şs]tay)?\s*(?:[İI]ddk|IDD K|[İI]dari Dava Daireleri Kurulu)|"
    r"(AYM|Anayasa Mahkemesi)", re.IGNORECASE)
TAM_KALIP = re.compile(
    r"(Yarg\.?\s*\d{1,2}\.\s*H\.?D\.?|Yargıtay\s*\d{1,2}\.\s*HD\.?|Danıştay\s*(?:İDDK|[\d]+\.?\s*D\.?)|"
    r"AYM,?\s*\d\.\s*Bölüm)[^\.]{0,80}?E\.\s*(\d{4}/\d+)[^\.]{0,20}?K\.\s*(\d{4}/\d+)"
    r"(?:[^\.]{0,20}?T\.\s*([\d]{1,2}\.[\d]{1,2}\.[\d]{4}))?", re.IGNORECASE | re.DOTALL)

# P1: E./K. önekisiz yaygın yazım — "9. HD., 2018/123 E., 2019/456 K."
TAM_KALIP_2 = re.compile(
    r"(?:Yarg\.?\s*)?(?:\d{1,2}\.\s*HD\.?|Danıştay\s*(?:İDDK|\d{1,2}\.\s*D\.?)|AYM,?\s*\d\.\s*Bölüm)?"
    r"[^\n]{0,60}?(\d{4}/\d+)\s*E\.,?\s*(\d{4}/\d+)\s*K\.?"
    r"(?:[^\n]{0,20}?T\.\s*(\d{1,2}[./]\d{1,2}[./]\d{4}))?", re.IGNORECASE)


def atiflari_ayristir(metin: str):
    """İki bilinen içtihat atfı kalibini birleştirir (deterministik).
    Kalıp 1: 'Yarg. 10. HD., E. 2018/1234, K. 2020/5678, T. ...'
    Kalıp 2: '9. HD., 2018/123 E., 2019/456 K.' (E./K. önekisiz yaygın yazım)"""
    ham_set = []
    gorulen_aralik = []
    for kalip in (TAM_KALIP, TAM_KALIP_2):
        for m in kalip.finditer(metin):
            cakisiyor = any(not (m.end() <= b or m.start() >= e) for b, e in gorulen_aralik)
            if cakisiyor:
                continue
            gorulen_aralik.append((m.start(), m.end()))
            ham_set.append(re.sub(r"\s+", " ", m.group(0)).strip())
    return ham_set


@r.post("/atif/tara")
def atif_tara(belge_id: int):
    """Atıf ayrıştırma: Yargıtay/Danıştay/AYM formatları.
    Dürüstlük: GERÇEK doğrulama API'si yok — karararama/emsal sistemlerine
    programatik erişim kapalı; araç sadece AYRIŞTIRIR ve 'Kaynak gerekli' işaretler.
    Bilinen kararlar (tohumda işaretli) dışında 'bulunamadı' DEMEK UYDURMAK DEĞİL,
    aramanın sınırını söylemektir."""
    with _db() as db:
        belge = db.get(AtifBelgesi, belge_id)
        if not belge:
            raise HTTPException(404)
        bulunan = []
        for ham in atiflari_ayristir(belge.metin):
            if any(a.ham == ham for a in db.query(Atif).filter(Atif.belge_id == belge_id).all()):
                continue
            yargi = ("Yargıtay" if ("Yarg" in ham or re.search(r"\d{1,2}\.\s*HD", ham))
                     else "Danıştay" if ("Danıştay" in ham or "İDDK" in ham)
                     else "AYM")
            md = re.search(r"(\d{1,2}\.\s*HD|İDDK|\d\.\s*Bölüm)", ham)
            db.add(Atif(belge_id=belge_id, ham=ham, yargi=yargi,
                        daire=md.group(1) if md else "",
                        durum="Kaynak gerekli",
                        dogrulama_notu="Ayrıştırıldı. Resmî portallardan teyit ediniz."))
            bulunan.append(ham)
        db.commit()
        toplam = db.query(Atif).filter(Atif.belge_id == belge_id).count()
    return {"durum": "ok", "yeni": bulunan, "toplam": toplam,
            "not": "Atıf ayrıştırma tamamen deterministiktir (regex). Doğrulama katmanı insan+"}


@r.get("/atif")
def atif_liste():
    belgeler = _jsonla(_veriler(AtifBelgesi), ["id", "ad", "metin", "olusturma"])
    atiflar = _jsonla(_veriler(Atif),
                      ["id", "belge_id", "ham", "yargi", "daire", "esas_no", "karar_no",
                       "karar_tarihi", "durum", "dogrulama_notu", "karar_bulundu"])
    return {"belgeler": belgeler, "atiflar": atiflar, "feragat": FERAGAT}


class AtifDurum(BaseModel):
    atif_id: int
    durum: str  # Doğrulandı / Karar bulunamadı / İçtihat değişmiş olabilir / Kaynak gerekli
    not_metin: str = ""


@r.post("/atif/durum")
def atif_durum(g: AtifDurum):
    with _db() as db:
        a = db.get(Atif, g.atif_id)
        if not a:
            raise HTTPException(404)
        a.durum = g.durum
        a.karar_bulundu = g.durum == "Doğrulandı"
        if g.not_metin:
            a.dogrulama_notu = (a.dogrulama_notu + " | " if a.dogrulama_notu else "") + \
                f"[{g.durum}] {g.not_metin}"
        db.commit()
    return {"durum": "ok"}


# ============================================================ DELİL KRONOLOJİSİ

TARIH_KALIP = re.compile(r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b")


@r.post("/kronoloji/tara")
def kronoloji_tara(dosya_adi: str = "belge"):
    """Demo olay çıkarımı: sunucuya yüklenen/örnek metinden tarih+cümle çıkarımı.
    Gerçek modül: belge yüklemesi + LLM çıkarımı (What Claude read kolonu)."""
    import os
    yol = os.path.join("data", "kronoloji-kaynak.txt")
    if not os.path.exists(yol):
        raise HTTPException(404, "data/kronoloji-kaynak.txt yok")
    metin = open(yol, encoding="utf-8").read()
    with _db() as db:
        eklenen = 0
        for m in TARIH_KALIP.finditer(metin):
            try:
                from datetime import date as _d
                tarih = _d(int(m.group(3)), int(m.group(2)), int(m.group(1)))
            except ValueError:
                continue
            blok_bas = metin.rfind("\n", 0, m.start()) + 1
            blok_son = metin.find("\n", m.end())
            cumle = metin[blok_bas: blok_son if blok_son != -1 else len(metin)].strip()
            if len(cumle) < 20 or any(o.kaynak_alinti == cumle for o in db.query(Olay).all()):
                continue
            tur = "İletişim"
            if re.search(r"sözleşme|protokol|imza", cumle, re.I):
                tur = "Sözleşme"
            elif re.search(r"ödeme|fatura|dekont|bedel", cumle, re.I):
                tur = "Ödeme"
            elif re.search(r"toplantı|görüşme|arabulucu", cumle, re.I):
                tur = "Toplantı"
            db.add(Olay(dosya_adi=dosya_adi, tarih=tarih, tur=tur, metin=cumle[:300],
                        kaynak_alinti=cumle, kaynak_dosya="kronoloji-kaynak.txt",
                        durum="İnceleme", cikarim_yontemi="demo"))
            eklenen += 1
        db.commit()
    return {"durum": "ok", "eklenen": eklenen}


@r.get("/kronoloji")
def kronoloji_liste():
    olaylar = _jsonla(_veriler(Olay),
                      ["id", "dosya_adi", "tarih", "tarihsiz", "yakinlik", "tur", "metin",
                       "kaynak_alinti", "kaynak_dosya", "kaynak_sayfa", "durum", "cikarim_yontemi"])
    olaylar.sort(key=lambda o: o["tarih"] or "9999")
    return {"olaylar": olaylar, "feragat": FERAGAT}


class OlayDurum(BaseModel):
    id: int
    durum: str  # Onaylı / İtirazlı / İnceleme
    metin: str | None = None


@r.post("/kronoloji/olay")
def kronoloji_olay_guncelle(g: OlayDurum):
    with _db() as db:
        o = db.get(Olay, g.id)
        if not o:
            raise HTTPException(404)
        o.durum = g.durum
        if g.metin is not None:
            o.metin = g.metin
        db.commit()
    return {"durum": "ok"}


# ============================================================ AI ENVANTERİ

@r.get("/envanter")
def envanter_liste():
    kullanimlar = _jsonla(_veriler(AIKullanim),
                          ["id", "ad", "bolum", "amac", "asama", "onerilen_katman", "katman",
                           "sahip_rol", "sahip_kisi", "arac", "satici", "etkiyenler", "durum",
                           "kosullar", "kosul_son", "veri_gizlilik"])
    saticilar = _jsonla(_veriler(AISatici),
                        ["id", "arac", "satici", "onayli_veri_siniflari", "egitim_kullaniyor",
                         "dp_imzali", "saklama", "alt_isleyiciler", "guvenlik_kaniti",
                         "sozlesme_ref", "sonraki_inceleme"])
    return {"kullanimlar": kullanimlar, "saticilar": saticilar,
            "ozet": {k: sum(1 for x in kullanimlar if x["katman"] == k)
                     for k in ("Durdur", "Yüksek", "Orta", "Günlük", "Henüz yok")},
            "feragat": FERAGAT}


class KatmanKarar(BaseModel):
    id: int
    katman: str
    kimi: str = "Uyum Ekibi"
    durum: str | None = None


@r.post("/envanter/katman")
def envanter_katman(g: KatmanKarar):
    with _db() as db:
        k = db.get(AIKullanim, g.id)
        if not k:
            raise HTTPException(404)
        k.katman = g.katman
        if g.durum:
            k.durum = g.durum
        db.commit()
    return {"durum": "ok"}


# ============================================================ SATIŞ Q&A

@r.get("/qa")
def qa_liste():
    alicilar = _jsonla(_veriler(QAAlıcı), ["id", "ad", "tur", "kota"])
    sorular = _jsonla(_veriler(QASoru),
                      ["id", "ref", "alici_id", "metin", "kategori", "durum", "cevap_turu",
                       "kimlere", "taslak", "kaynak_belge", "kaynak_konum", "onaylayan",
                       "capraz_ifsa_uyari"])
    return {"alicilar": alicilar, "sorular": sorular, "feragat": FERAGAT,
            "kural": "Yalnız onaylı metin dışarı çıkar."}


class QAKarar(BaseModel):
    id: int
    islem: str  # onayla / yayinla / redline_not
    metin: str = ""
    kimi: str = "Hukuk"


@r.post("/qa/karar")
def qa_karar(g: QAKarar):
    with _db() as db:
        s = db.get(QASoru, g.id)
        if not s:
            raise HTTPException(404)
        if g.islem == "onayla":
            s.durum = "Onaylandı"
            s.onaylayan = g.kimi
            if not s.taslak:
                s.taslak = g.metin
        elif g.islem == "yayinla":
            if s.durum != "Onaylandı":
                raise HTTPException(409, "Yalnız onaylı cevap yayınlanabilir — kapı onaya kilitli.")
            s.durum = "Yayınlandı"
        db.commit()
    return {"durum": "ok"}


# ============================================================ MEVZUAT RADARI

@r.get("/mevzuat")
def mevzuat_liste():
    kayitlar = _jsonla(_veriler(MevzuatKayit),
                       ["id", "baslik", "kaynak", "url", "etki", "kapsam_ozellikleri",
                        "gecer_tarihi", "tarih_durumu", "onerilen_islem", "reviewer", "dogrulandi"])
    kayitlar.sort(key=lambda x: (x["gecer_tarihi"] is None, x["gecer_tarihi"] or ""))
    bugun_iso = date.today().isoformat()
    return {"kayitlar": kayitlar,
            "ozet": {"toplam": len(kayitlar),
                     "yuksek": sum(1 for k in kayitlar if k["etki"] == "Yüksek"),
                     "onumuzdeki90": sum(1 for k in kayitlar if k["gecer_tarihi"] and
                                         0 <= (date.fromisoformat(k["gecer_tarihi"]) - date.today()).days <= 90)},
            "profil_notu": "Etki puanı = düzenleme × kurumun ürün özellikleri (kapsam etiketleri) × yargı × tarih yakınlığı.",
            "feragat": FERAGAT}


@r.post("/mevzuat/dogrula")
def mevzuat_dogrula(kayit_id: int):
    with _db() as db:
        k = db.get(MevzuatKayit, kayit_id)
        if not k:
            raise HTTPException(404)
        k.dogrulandi = True
        db.commit()
    return {"durum": "ok"}


# ============================================================ YENİ VERİ / BELGE EKLEME UÇLARI (CANLI KULLANIM)

class YeniPlaybookMadde(BaseModel):
    sozlesme_adi: str
    karsi_taraf: str = ""
    biz_kimiz: str = "Müşteri"
    kagit_kimi: str = "Onların"
    madde_adi: str
    durum: str = "İnceleme"
    sozlesme_alinti: str = ""
    madde_no: str = ""
    sayfa: str = ""
    onerilen_duzenleme: str = ""
    karsi_tarafa_not: str = ""

@r.post("/playbook/ekle")
def playbook_ekle(m: YeniPlaybookMadde):
    with _db() as db:
        sm = SozlesmeMaddesi(**m.model_dump())
        db.add(sm)
        db.commit()
        return {"durum": "ok", "id": sm.id}


class YeniTalep(BaseModel):
    baslik: str
    soran_ad: str = "İş Birimi"
    bolum: str = "Genel"
    kategori: str = "Sözleşme İncelemesi"
    metin: str
    risk: str = "Orta"
    hassas: bool = False
    atanan: str = "Hukuk Müşavirliği"

@r.post("/masa/talep/ekle")
def masa_talep_ekle(t: YeniTalep):
    with _db() as db:
        from datetime import date
        talep = Talep(**t.model_dump(), olusturma=date.today(), durum="Yeni")
        db.add(talep)
        db.commit()
        return {"durum": "ok", "id": talep.id}


class YeniDosya(BaseModel):
    """dosya.html yeniDosyaKaydet()'in gönderdiği alan adlarıyla birebir (P1)."""
    ad: str
    muvekkil: str = ""
    karsi_taraf: str = ""
    alan_kodu: str = "TİC"
    sahibi: str = ""
    asama: str = "Yeni"
    sonraki_islem: str = ""
    sonraki_tarih: str | None = None
    zamanasimi_tarihi: str | None = None

@r.post("/dosya/ekle")
def dosya_ekle(d: YeniDosya):
    with _db() as db:
        from datetime import date
        st = date.fromisoformat(d.sonraki_tarih) if d.sonraki_tarih else None
        zt = date.fromisoformat(d.zamanasimi_tarihi) if d.zamanasimi_tarihi else None
        dosya = Dosya(
            ad=d.ad, musteri=d.muvekkil, karsi_taraf=d.karsi_taraf,
            alan_kodu=d.alan_kodu, sahibi=d.sahibi, asama=d.asama,
            sonraki_islem=d.sonraki_islem, sonraki_tarih=st, zamanasimi_tarihi=zt,
            orijinal_ornek=False
        )
        db.add(dosya)
        db.commit()
        return {"durum": "ok", "id": dosya.id}


class YeniBasvuru(BaseModel):
    basvuran: str
    iliskili: str = ""
    alan: str = "Dava"
    eposta: str = ""
    telefon: str = ""
    konu: str = ""

@r.post("/kabul/ekle")
def kabul_ekle(b: YeniBasvuru):
    with _db() as db:
        from datetime import date
        basvuru = Basvuru(
            ad=b.basvuran, konu_turu=b.alan, iliskili=b.iliskili,
            iletisim=b.eposta or b.telefon, tek_satir=b.konu,
            asama="Yeni", catisma_durumu="Çalıştırılmadı"
        )
        db.add(basvuru)
        db.commit()
        return {"durum": "ok", "id": basvuru.id}


class YeniAtifBelgesi(BaseModel):
    ad: str
    metin: str

@r.post("/atif/yukle")
def atif_yukle(b: YeniAtifBelgesi):
    with _db() as db:
        from datetime import date
        belge = AtifBelgesi(ad=b.ad, metin=b.metin, olusturma=date.today())
        db.add(belge)
        db.commit()
        db.refresh(belge)
        # Anında içtihatları ayrıştır
        bulunan = []
        for ham in atiflari_ayristir(b.metin):
            yargi = ("Yargıtay" if ("Yarg" in ham or re.search(r"\d{1,2}\.\s*HD", ham))
                     else "Danıştay" if ("Danıştay" in ham or "İDDK" in ham)
                     else "AYM")
            md = re.search(r"(\d{1,2}\.\s*HD|İDDK|\d\.\s*Bölüm)", ham)
            atif = Atif(belge_id=belge.id, ham=ham, yargi=yargi,
                        daire=md.group(1) if md else "",
                        durum="Kaynak gerekli",
                        dogrulama_notu="Ayrıştırıldı. Resmî portallardan teyit ediniz.")
            db.add(atif)
            bulunan.append(ham)
        db.commit()
        return {"durum": "ok", "belge_id": belge.id, "ayristirilan": len(bulunan), "atiflar": bulunan}


class YeniOlay(BaseModel):
    tarih: str
    baslik: str
    detay: str = ""
    kaynak_belge: str = "Manuel Kayıt"
    kaynak_alinti: str = ""
    tur: str = "İşlem"

@r.post("/kronoloji/ekle")
def kronoloji_ekle(o: YeniOlay):
    with _db() as db:
        from datetime import date
        olay = Olay(
            tarih=date.fromisoformat(o.tarih),
            metin=(o.baslik + ": " + o.detay).strip(": ") if o.baslik else (o.detay or o.baslik),
            kaynak_alinti=o.kaynak_alinti or o.detay or o.baslik,
            kaynak_dosya=o.kaynak_belge,
            tur=o.tur,
            durum="Onaylı",
            cikarim_yontemi="elle"
        )
        db.add(olay)
        db.commit()
        return {"durum": "ok", "id": olay.id}


class KronolojiMetinTara(BaseModel):
    metin: str
    belge_adi: str = "Yüklenen Belge"

@r.post("/kronoloji/metin-tara")
def kronoloji_metin_tara(k: KronolojiMetinTara):
    with _db() as db:
        from datetime import date as _d
        eklenen = 0
        for m in TARIH_KALIP.finditer(k.metin):
            try:
                tarih = _d(int(m.group(3)), int(m.group(2)), int(m.group(1)))
            except ValueError:
                continue
            blok_bas = k.metin.rfind("\n", 0, m.start()) + 1
            blok_son = k.metin.find("\n", m.end())
            cumle = k.metin[blok_bas: blok_son if blok_son != -1 else len(k.metin)].strip()
            if len(cumle) < 15:
                continue
            tur = "İşlem"
            if re.search(r"sözleşme|protokol|imza", cumle, re.I):
                tur = "Sözleşme"
            elif re.search(r"ihtar|fesih|tebliğ|ihtarname", cumle, re.I):
                tur = "İhtar"
            elif re.search(r"teslim|nakliye|irsaliye|depo", cumle, re.I):
                tur = "Teslimat"
            elif re.search(r"ödeme|havale|fatura|dekont", cumle, re.I):
                tur = "Ödeme"
            
            metin_kisa = cumle[:250]
            db.add(Olay(
                tarih=tarih, metin=metin_kisa,
                kaynak_dosya=k.belge_adi, kaynak_alinti=cumle,
                tur=tur, durum="Taslak"
            ))
            eklenen += 1
        db.commit()
        return {"durum": "ok", "eklenen": eklenen}


class YeniIncelemeSatiri(BaseModel):
    belge_adi: str
    karsi_taraf: str = ""
    sozlesme_turu: str = "Hizmet"
    yururluk: str = ""
    bitis_sure: str = ""
    otomatik_uzatma: str = "Hayır"
    taban_hukuk: str = "Türk Hukuku"
    sorumluluk_tavani: str = ""
    mali_yukumluluk: str = ""
    notlar: str = ""

@r.post("/inceleme/ekle")
def inceleme_ekle(s: YeniIncelemeSatiri):
    with _db() as db:
        inc = db.query(TabloInceleme).first()
        inc_id = inc.id if inc else 1
        satir = IncelemeSatiri(inceleme_id=inc_id, **s.model_dump())
        db.add(satir)
        db.commit()
        return {"durum": "ok", "id": satir.id}


# ============================================================ GENEL CRUD & SİLME UÇLARI

class SilIstegi(BaseModel):
    id: int

@r.post("/dosya/sil")
def dosya_sil(s: SilIstegi):
    with _db() as db:
        k = db.get(Dosya, s.id)
        if k:
            db.delete(k)
            db.commit()
        return {"durum": "ok"}

@r.post("/dosya/ornek-sil")
def dosya_ornek_sil():
    with _db() as db:
        db.query(Dosya).delete()
        db.commit()
        return {"durum": "ok"}

@r.post("/inceleme/sil")
def inceleme_sil(s: SilIstegi):
    with _db() as db:
        k = db.get(IncelemeSatiri, s.id)
        if k:
            db.delete(k)
            db.commit()
        return {"durum": "ok"}

@r.post("/inceleme/ornek-sil")
def inceleme_ornek_sil():
    with _db() as db:
        db.query(IncelemeSatiri).delete()
        db.commit()
        return {"durum": "ok"}

class IncelemeGuncelle(BaseModel):
    id: int
    belge_adi: str | None = None
    karsi_taraf: str | None = None
    sozlesme_turu: str | None = None
    yururluk: str | None = None
    bitis_sure: str | None = None
    otomatik_uzatma: str | None = None
    taban_hukuk: str | None = None
    sorumluluk_tavani: str | None = None
    mali_yukumluluk: str | None = None
    notlar: str | None = None
    sahibi: str | None = None

@r.post("/inceleme/guncelle")
def inceleme_guncelle(g: IncelemeGuncelle):
    with _db() as db:
        k = db.get(IncelemeSatiri, g.id)
        if not k:
            raise HTTPException(404, "Kayıt bulunamadı")
        for alan, val in g.model_dump(exclude_unset=True).items():
            if val is not None and alan != "id":
                setattr(k, alan, val)
        db.commit()
        return {"durum": "ok"}

@r.post("/playbook/sil")
def playbook_sil(s: SilIstegi):
    with _db() as db:
        k = db.get(SozlesmeMaddesi, s.id)
        if k:
            db.delete(k)
            db.commit()
        return {"durum": "ok"}

@r.post("/playbook/ornek-sil")
def playbook_ornek_sil():
    with _db() as db:
        db.query(SozlesmeMaddesi).delete()
        db.commit()
        return {"durum": "ok"}

@r.post("/masa/talep/sil")
def masa_talep_sil(s: SilIstegi):
    with _db() as db:
        k = db.get(Talep, s.id)
        if k:
            db.delete(k)
            db.commit()
        return {"durum": "ok"}

@r.post("/masa/ornek-sil")
def masa_ornek_sil():
    with _db() as db:
        db.query(Talep).delete()
        db.commit()
        return {"durum": "ok"}

@r.post("/kabul/sil")
def kabul_sil(s: SilIstegi):
    with _db() as db:
        k = db.get(Basvuru, s.id)
        if k:
            db.delete(k)
            db.commit()
        return {"durum": "ok"}

@r.post("/kabul/ornek-sil")
def kabul_ornek_sil():
    with _db() as db:
        db.query(Basvuru).delete()
        db.commit()
        return {"durum": "ok"}

@r.post("/kronoloji/sil")
def kronoloji_sil(s: SilIstegi):
    with _db() as db:
        k = db.get(Olay, s.id)
        if k:
            db.delete(k)
            db.commit()
        return {"durum": "ok"}

@r.post("/kronoloji/ornek-sil")
def kronoloji_ornek_sil():
    with _db() as db:
        db.query(Olay).delete()
        db.commit()
        return {"durum": "ok"}

@r.post("/atif/sil")
def atif_sil(s: SilIstegi):
    with _db() as db:
        db.query(Atif).filter(Atif.belge_id == s.id).delete()
        k = db.get(AtifBelgesi, s.id)
        if k:
            db.delete(k)
        db.commit()
        return {"durum": "ok"}



class TalepCevapGovdesi(BaseModel):
    cevap: str
    gonderen_kimlikle: str = "Hukuk Müşavirliği"
    onayla: bool = False


@r.post("/masa/talep/{tid}/cevap")
def masa_talep_cevap(tid: int, b: TalepCevapGovdesi):
    """masa.html cevapKaydet/cevapOnayla çağrılarının hedefi.
    onayla=True → taslak avukat tarafından onaylanıp gönderilmiş sayılır (isim+tarih kayda geçer)."""
    with _db() as db:
        t = db.get(Talep, tid)
        if not t:
            raise HTTPException(404, "Talep bulunamadı")
        temiz = (b.cevap or "").strip()
        if b.onayla:
            # P0-4: boş veya kalıp cevabın onayı reddedilir — insan metni zorunlu
            if not temiz:
                raise HTTPException(400, "Boş cevap onaylanamaz")
            if temiz.strip(".") == "Talebiniz incelenmiştir ve uygun görülmüştür":
                raise HTTPException(400, "Kalıp (otomatik) cevap onaylanamaz — gerçek görüş metni gerekli")
        t.cevap = b.cevap
        t.gonderen_kimlikle = b.gonderen_kimlikle
        muhur = None
        if b.onayla:
            t.durum = "Kapatıldı"
            muhur = muhur_hesapla(b.cevap, b.gonderen_kimlikle, date.today().isoformat())
            t.muhur = muhur
        db.commit()
        return {"durum": "ok", "talep_durumu": t.durum, "muhur": muhur}


@r.post("/ornek-geri-yukle")
def ornek_geri_yukle():
    from app.seed import tohumla_tumu
    return tohumla_tumu(sifirla=True)


def _metin_cikar(icerik: bytes, dosya_adi: str) -> str:
    """PDF, DOCX veya TXT dosya içeriğinden metin çıkarır."""
    ad = dosya_adi.lower()
    if ad.endswith(".txt") or ad.endswith(".csv"):
        return icerik.decode("utf-8", errors="ignore")
    elif ad.endswith(".docx"):
        import io
        import docx
        doc = docx.Document(io.BytesIO(icerik))
        return "\n".join(p.text for p in doc.paragraphs if p.text)
    elif ad.endswith(".pdf"):
        import io
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(icerik))
        metinler = []
        for p in reader.pages:
            t = p.extract_text()
            if t:
                metinler.append(t)
        return "\n".join(metinler)
    else:
        return icerik.decode("utf-8", errors="ignore")


@r.post("/evrak-yukle-ve-isle")
async def evrak_yukle_ve_isle(
    modul: str = Form(...),
    baslik: str = Form(""),
    metin_girisi: str = Form(""),
    dosya: UploadFile = File(None)
):
    metin = metin_girisi or ""
    dosya_adi = "Metin Girişi"
    if dosya and dosya.filename:
        dosya_adi = dosya.filename
        icerik = await dosya.read()
        metin = _metin_cikar(icerik, dosya_adi)
    
    if not metin.strip():
        raise HTTPException(400, "İşlenecek metin veya dosya içeriği bulunamadı")

    with _db() as db:
        from datetime import date
        from app.cikarim import llm_uret, ayar_getir
        ayarlar = ayar_getir()
        aktif_saglayici = ayarlar["saglayici"]
        aktif_model = ayarlar["model"]

        # 1. TABLO İNCELEME MODÜLÜ
        if modul == "inceleme":
            inc = db.query(TabloInceleme).first()
            inc_id = inc.id if inc else 1

            # LLM Analiz Denemesi
            girdi_blok, kvkk_harita = hazir_girdi(metin)
            llm_prompt = f"""Aşağıdaki sözleşme metnini Türk Borçlar Kanunu ve Ticaret Hukuku açısından incele:
Metin:
{girdi_blok}

Lütfen JSON formatında şu alanları çıkar:
{{
  "karsi_taraf": "Karşı taraf şirket veya şahıs adı",
  "sozlesme_turu": "Hizmet / Kira / Satım / NDA / Eser Sözleşmesi",
  "sorumluluk_tavani": "Sorumluluk tavanı ve tazminat sınırı hükmü özeti",
  "mali_yukumluluk": "Ödeme şartları ve mali taahhütler",
  "taban_hukuk": "Uygulanacak hukuk ve yetkili mahkeme / tahkim",
  "otomatik_uzatma": "Evet veya Hayır",
  "ciddi_konu": true/false (Cezai şart, rücu veya ağır risk varsa true)
}}"""
            llm_res, yontem, mod_ad = await llm_uret(llm_prompt, "Sen uzman bir Türk sözleşme avukatısın.", json_olsun=True)
            if kvkk_harita and isinstance(llm_res, dict):
                llm_res = unmask_derin(llm_res, kvkk_harita)

            if isinstance(llm_res, dict) and "karsi_taraf" in llm_res:
                karsi_taraf = llm_res.get("karsi_taraf", "Belirtilmemiş")[:100]
                sozlesme_turu = llm_res.get("sozlesme_turu", "Hizmet Sözleşmesi")
                tavan = llm_res.get("sorumluluk_tavani", "Bulunamadı — sorumluluk tavanı hükmü tespit edilmedi")[:150]
                taban_hukuk = llm_res.get("taban_hukuk", "Bulunamadı — hukuk/yetki maddesi tespit edilmedi")
                mali_yuk = llm_res.get("mali_yukumluluk", "Sözleşmede belirlenen ödeme planına göre")
                oto = llm_res.get("otomatik_uzatma", "Hayır")
                ciddi = bool(llm_res.get("ciddi_konu", False))
                bilgi_notu = f"{yontem.upper()} ({mod_ad}) yapay zekası ile analiz edildi."
            else:
                # Yedek Kural Motoru
                karsi_taraf = "Tespit Edilemedi"
                m_taraf = re.search(r"(?:Taraflar|Müteahhit|Satıcı|Kiracı|İşveren|Şirket)[\s:]+([^\n\r,]+)", metin, re.I)
                if m_taraf: karsi_taraf = m_taraf.group(1).strip()[:100]
                sozlesme_turu = "Hizmet Sözleşmesi"
                if re.search(r"kira", metin, re.I): sozlesme_turu = "Kira Sözleşmesi"
                elif re.search(r"satım|satış", metin, re.I): sozlesme_turu = "Satım Sözleşmesi"
                elif re.search(r"gizlilik|nda", metin, re.I): sozlesme_turu = "Gizlilik Sözleşmesi (NDA)"
                elif re.search(r"eser|inşaat", metin, re.I): sozlesme_turu = "Eser Sözleşmesi"
                elif re.search(r"iş sözleşmesi|belirli süreli", metin, re.I): sozlesme_turu = "İş Sözleşmesi"
                tavan = "Bulunamadı — sorumluluk tavanı hükmü tespit edilmedi"
                m_tavan = re.search(r"(?:sorumluluk|tazminat)[\s\w]*(?:sınır|tavan|aşamaz)[\s:]*([^\n\r\.]+)", metin, re.I)
                if m_tavan: tavan = m_tavan.group(0).strip()[:150]
                taban_hukuk = "Bulunamadı — hukuk/yetki maddesi tespit edilmedi"
                mali_yuk = "Sözleşmede belirlenen ödeme planına göre"
                oto = "Evet" if re.search(r"otomatik\s+uzar", metin, re.I) else "Hayır"
                ciddi = bool(re.search(r"cezai şart|rücu|müteselsil", metin, re.I))
                bilgi_notu = "Yerel kural motoru (regex) ile çıkarıldı (Model API anahtarı girilmedi)."

            satir = IncelemeSatiri(
                inceleme_id=inc_id,
                belge_adi=baslik or dosya_adi,
                karsi_taraf=karsi_taraf,
                sozlesme_turu=sozlesme_turu,
                yururluk="Bulunamadı — yürürlük tarihi belgede tespit edilmedi",
                bitis_sure="Bulunamadı — süre hükmü belgede tespit edilmedi",
                otomatik_uzatma=oto,
                taban_hukuk=taban_hukuk,
                sorumluluk_tavani=tavan,
                mali_yukumluluk=mali_yuk,
                notlar=bilgi_notu,
                ciddi_konu=ciddi,
                inceleme_gerekli=True
            )
            db.add(satir)
            db.commit()
            return {"durum": "ok", "modul": "inceleme", "id": satir.id, "mesaj": f"'{satir.belge_adi}' incelendi ({bilgi_notu})."}

        # 2. HUKUK MASASI MODÜLÜ
        elif modul == "masa":
            soran = "İş Birimi Yetkilisi"
            bolum = "Operasyon"
            if re.search(r"satınalma|tedarik", metin, re.I): bolum = "Satınalma"
            elif re.search(r"ik|insan kaynakları|istifa", metin, re.I): bolum = "İnsan Kaynakları"
            elif re.search(r"finans|fatura|vergi", metin, re.I): bolum = "Finans"

            girdi_blok, kvkk_harita = hazir_girdi(metin)
            llm_prompt = f"""Aşağıdaki hukuki danışmanlık talebini Türk Hukuku (TTK, TBK, İİK, İş Kanunu vb.) çerçevesinde incele ve şirket için resmi bir HUKUKİ GÖRÜŞ / MÜTALAA TASLAĞI yaz.
Format:
- Olay ve Talep Özeti
- İlgili Mevzuat Hükümleri ve İçtihat İlkeleri
- Hukuki Risk Değerlendirmesi
- Şirkete Önerilen Aksiyon Planı

Danışmanlık Talebi:
{girdi_blok}"""

            llm_res, yontem, mod_ad = await llm_uret(llm_prompt, "Sen kıdemli bir Türk hukuk müşavirisin.", json_olsun=False)

            if llm_res and isinstance(llm_res, str) and len(llm_res) > 50:
                taslak = unmask_derin(llm_res, kvkk_harita)
                bilgi_notu = f"{yontem.upper()} ({mod_ad}) ile hazırlandı"
            else:
                taslak = ("Sayın İlgili,\n\nTalebiniz kayda alınmış ve hukuk müşavirliğine yönlendirilmiştir. "
                          "DİKKAT: Bu otomatik kayıt hukuki görüş DEĞİLDİR — yapay zeka anahtarı tanımlı olmadığından "
                          "içerik analizi yapılmamıştır. Delil muhafazası açısından ilgili yazışma ve belgeleri saklayınız.\n\nHukuk Müşavirliği")
                bilgi_notu = "Kural taslağı (LLM anahtarı girilmedi)"

            talep = Talep(
                baslik=baslik or dosya_adi,
                soran_ad=soran,
                bolum=bolum,
                kategori="Genel Hukuki Danışmanlık",
                metin=metin[:1000],
                risk="Orta",
                durum="Taslak hazır",
                olusturma=date.today(),
                taslak=taslak,
                taslak_turu=f"Zekai Hukuki Görüş ({bilgi_notu})",
                gonderen_kimlikle="Hukuk Müşaviri"
            )
            db.add(talep)
            db.commit()
            return {"durum": "ok", "modul": "masa", "id": talep.id, "mesaj": f"'{talep.baslik}' hukuk masasına kaydedildi ({bilgi_notu})."}

        # 3. KRONOLOJİ MODÜLÜ
        elif modul == "kronoloji":
            eklenen = 0
            
            # Gerçek LLM Çıkarımı Denemesi
            girdi_blok, kvkk_harita = hazir_girdi(metin)
            llm_prompt = f"""Aşağıdaki dava metninden / dilekçeden / tutanaktan tüm somut olayları, delilleri ve tarihleri çıkar.
Her olay için:
- tarih: YYYY-MM-DD formatında geçerli bir tarih (örn: 2024-01-15). Tarih belirsizse boş bırak.
- tur: 'İşlem', 'İletişim', 'Toplantı', 'Sözleşme', 'Ödeme' veya 'Dava'
- metin: Olayın 1-2 cümlelik net özeti
- kaynak_alinti: Metindeki ilgili cümleden birebir kaynak pasaj

Lütfen çıktıyı sadece şu JSON formatında ver:
{{
  "olaylar": [
    {{"tarih": "2024-01-15", "tur": "İşlem", "metin": "Özet", "kaynak_alinti": "Alıntı"}}
  ]
}}

Metin:
{girdi_blok}"""

            llm_res, yontem, mod_ad = await llm_uret(llm_prompt, "Sen Türk Hukukunda uzman, dava ve delil analizi yapan bir avukatsın.", json_olsun=True)
            if kvkk_harita and isinstance(llm_res, dict):
                llm_res = unmask_derin(llm_res, kvkk_harita)

            if isinstance(llm_res, dict) and "olaylar" in llm_res and isinstance(llm_res["olaylar"], list) and len(llm_res["olaylar"]) > 0:
                for o_item in llm_res["olaylar"]:
                    t_str = o_item.get("tarih")
                    t_obj = None
                    if t_str:
                        try:
                            parcalar = [int(p) for p in re.findall(r"\d+", t_str)[:3]]
                            if len(parcalar) == 3:
                                if parcalar[0] > 1900:
                                    t_obj = date(parcalar[0], parcalar[1], parcalar[2])
                                else:
                                    t_obj = date(parcalar[2], parcalar[1], parcalar[0])
                        except Exception:
                            t_obj = None

                    db.add(Olay(
                        dosya_adi=baslik or dosya_adi,
                        tarih=t_obj,
                        tur=o_item.get("tur", "İşlem"),
                        metin=o_item.get("metin", "Olay özeti")[:250],
                        kaynak_alinti=o_item.get("kaynak_alinti", metin[:150]),
                        kaynak_dosya=dosya_adi,
                        durum="İnceleme",
                        cikarim_yontemi=f"{yontem} ({mod_ad})"
                    ))
                    eklenen += 1
                db.commit()
                return {
                    "durum": "ok", 
                    "modul": "kronoloji", 
                    "eklenen": eklenen, 
                    "yontem": yontem,
                    "mesaj": f"Yapay zeka ({yontem.upper()} - {mod_ad}) ile metinden {eklenen} somut vaka ve delil başarıyla çıkarıldı."
                }

            # LLM Anahtarı yoksa veya yanıt dönmediyse: Yedek Kural Motoru
            for m in TARIH_KALIP.finditer(metin):
                try:
                    tarih = date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
                except ValueError:
                    continue
                blok_bas = metin.rfind("\n", 0, m.start()) + 1
                blok_son = metin.find("\n", m.end())
                cumle = metin[blok_bas: blok_son if blok_son != -1 else len(metin)].strip()
                if len(cumle) < 15: continue
                tur = "İşlem"
                if re.search(r"sözleşme|imza", cumle, re.I): tur = "Sözleşme"
                elif re.search(r"ihtar|tebliğ", cumle, re.I): tur = "İletişim"
                elif re.search(r"ödeme|fatura", cumle, re.I): tur = "Ödeme"
                elif re.search(r"toplantı|görüşme", cumle, re.I): tur = "Toplantı"

                db.add(Olay(
                    dosya_adi=baslik or dosya_adi,
                    tarih=tarih,
                    tur=tur,
                    metin=cumle[:200],
                    kaynak_alinti=cumle,
                    kaynak_dosya=dosya_adi,
                    durum="İnceleme",
                    cikarim_yontemi="demo (kural motoru)"
                ))
                eklenen += 1
            db.commit()
            return {
                "durum": "ok", 
                "modul": "kronoloji", 
                "eklenen": eklenen, 
                "yontem": "demo",
                "mesaj": f"Yerel kural motoru ile {eklenen} tarihli olay çıkarıldı.\n(Not: Gerçek DeepSeek/Claude/Qwen yapay zeka analizi için sağ üstteki ⚙ Model Ayarları'ndan API anahtarınızı tanımlayabilirsiniz.)"
            }

        # 4. ATIF DENETİMİ MODÜLÜ
        elif modul == "atif":
            belge = AtifBelgesi(ad=baslik or dosya_adi, metin=metin, olusturma=date.today())
            db.add(belge)
            db.commit()
            db.refresh(belge)
            atif_sayisi = 0
            for m in TAM_KALIP.finditer(metin):
                ham = re.sub(r"\s+", " ", m.group(0)).strip()
                yargi = "Yargıtay" if ("Yarg" in ham or "HD" in ham) else ("Danıştay" if "Danıştay" in ham else "AYM")
                atif = Atif(
                    belge_id=belge.id, ham=ham, yargi=yargi,
                    esas_no=f"E. {m.group(2)}", karar_no=f"K. {m.group(3)}",
                    karar_tarihi=m.group(4) or "", durum="Kaynak gerekli",
                    dogrulama_notu="Zekai atıf motoru tarafından metinden ayıklandı."
                )
                db.add(atif)
                atif_sayisi += 1
            db.commit()
            return {"durum": "ok", "modul": "atif", "id": belge.id, "atif_sayisi": atif_sayisi, "mesaj": f"Belgeden {atif_sayisi} hukuki atıf çıkarıldı."}

        else:
            return {"durum": "ok", "mesaj": "Belge metni alındı."}


# ============================================================ MODEL & SAĞLAYICI AYARLARI

from app import cikarim

@r.get("/ayarlar/model")
def model_ayarlari_getir():
    return cikarim.ayar_getir()

class ModelAyarGuncelle(BaseModel):
    saglayici: str
    model: str | None = None
    api_key: str | None = None
    base_url: str | None = None

@r.post("/ayarlar/model")
def model_ayarlari_kaydet(a: ModelAyarGuncelle):
    try:
        sonuc = cikarim.ayar_guncelle(a.saglayici, a.model, a.api_key, a.base_url)
        return {"durum": "ok", "ayarlar": sonuc}
    except Exception as e:
        raise HTTPException(400, str(e))

class ModelTestIstegi(BaseModel):
    saglayici: str
    model: str
    api_key: str = ""
    base_url: str = ""

@r.post("/ayarlar/model-test")
async def model_test_et(t: ModelTestIstegi):
    res = await cikarim.test_baglanti(t.saglayici, t.model, t.api_key, t.base_url)
    return res






# ---------------------------------------------------- İNCELEME TOPLU İŞLEMLER (P: gerçek backend)

class TopluIstek(BaseModel):
    ids: list
    islem: str  # inceleme | sahip
    sahibi: str = ""


@r.post("/inceleme/toplu")
def inceleme_toplu(t: TopluIstek):
    """P1: inceleme.html toplu düğmelerinin gerçek backend'i (demo stub değildi)."""
    with _db() as db:
        guncellenen = 0
        for satir_id in t.ids:
            s = db.get(IncelemeSatiri, int(satir_id))
            if not s:
                continue
            if t.islem == "inceleme":
                s.inceleme_gerekli = True
            elif t.islem == "sahip" and t.sahibi:
                s.sahibi = t.sahibi
            guncellenen += 1
        db.commit()
    return {"durum": "ok", "guncellenen": guncellenen}
