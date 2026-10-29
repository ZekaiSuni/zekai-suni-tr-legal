"""v0.3 modüllerinin API uçları (kompakt)."""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db import Oturum
from app.modeller2 import (DavaPortfoyKayit, HarcamaKaydi, IzlenenDosya, KesifIstemi,
                           KesifSeti, MatrisHucre, MatrisSeti, PatentIstemSatiri,
                           PatentKarsilastirma, UyumYukumlulugu)

r2 = APIRouter(prefix="/api")
FERAGAT = "Zekai ile hazırlanmıştır; hukuki görüş değildir, güvenilmeden önce bir avukat tarafından gözden geçirilmelidir."


def _db():
    return Oturum()


def _jsonla(kayitlar, alanlar):
    cikti = []
    for k in kayitlar:
        d = {a: getattr(k, a) for a in alanlar}
        for a, v in list(d.items()):
            if hasattr(v, "isoformat"):
                d[a] = v.isoformat()
        cikti.append(d)
    return cikti


# ------------------------------------------------------------ KEŞİF CEVAP KAYDI

@r2.get("/kesif")
def kesif_liste():
    with _db() as db:
        seti = db.query(KesifSeti).first()
        istemler = db.query(KesifIstemi).all()
    s = _jsonla([seti], ["id", "ad", "dosya", "karsi_taraf", "tebliğ_tarihi", "cevap_sonu"])[0] if seti else None
    return {"seti": s,
            "istemler": _jsonla(istemler, ["id", "seti_id", "sira", "tur", "metin", "durum", "cevap",
                                           "kaynak_belge", "kaynak_konum", "onaylayan"]),
            "feragat": FERAGAT}


class KesifGuncelle(BaseModel):
    id: int
    cevap: str = ""
    durum: str | None = None
    onaylayan: str = ""


@r2.post("/kesif/guncelle")
def kesif_guncelle(g: KesifGuncelle):
    with _db() as db:
        k = db.get(KesifIstemi, g.id)
        if not k:
            raise HTTPException(404)
        if g.cevap:
            k.cevap = g.cevap
        if g.durum:
            k.durum = g.durum
        if g.onaylayan:
            k.onaylayan = g.onaylayan
        db.commit()
    return {"durum": "ok"}


# ------------------------------------------------------------ PATENT KARŞILAŞTIRMA

@r2.get("/patent")
def patent_liste():
    with _db() as db:
        k = db.query(PatentKarsilastirma).first()
        satirlar = db.query(PatentIstemSatiri).all()
    kk = _jsonla([k], ["id", "ad", "muvekkil_patent", "referans_patent"])[0] if k else None
    return {"karsilastirma": kk,
            "satirlar": _jsonla(satirlar, ["id", "istem_no", "unsuru", "muvekkil_metin",
                                           "referans_metin", "hukum", "kaynak_istem", "not_metin"]),
            "feragat": FERAGAT}


# ------------------------------------------------------------ DOSYA İZLEME

@r2.get("/izleme")
def izleme_liste():
    kayitlar = _veriler_local()
    bugun = date.today()
    cikti = []
    for d in kayitlar:
        g = d.__dict__ | {}
        for a, v in list(g.items()):
            if hasattr(v, "isoformat"):
                g[a] = v.isoformat()
        g["geciken"] = bool(d.cikarilan_tarih and d.cikarilan_tarih < bugun)
        g["kalan"] = (d.cikarilan_tarih - bugun).days if d.cikarilan_tarih else None
        cikti.append(g)
    return {"dosyalar": cikti, "feragat": FERAGAT,
            "not": "Kaynak: UYAP e-Dosya indirilen tensip/tebligat belgeleri. Gerçek ajan: izlenen dosyalar için yeni işlem taraması ('Checks cost nothing' modeli)."
            }


def _veriler_local():
    with _db() as db:
        return db.query(IzlenenDosya).all()


class IzlemeTeyit(BaseModel):
    id: int
    tarih_durumu: str


@r2.post("/izleme/teyit")
def izleme_teyit(g: IzlemeTeyit):
    with _db() as db:
        d = db.get(IzlenenDosya, g.id)
        if not d:
            raise HTTPException(404)
        d.tarih_durumu = g.tarih_durumu
        db.commit()
    return {"durum": "ok"}


# ------------------------------------------------------------ DIŞ AVUKAT HARCAMASI

@r2.get("/harcama")
def harcama_liste():
    kayitlar = _jsonla(_db_local(), ["id", "buro", "dosya", "donem", "tutar", "butce", "durum", "not_metin"])
    toplam = sum(k["tutar"] for k in kayitlar)
    butce = sum(k["butce"] or 0 for k in kayitlar)
    return {"kayitlar": kayitlar,
            "ozet": {"toplam": toplam, "butce": butce,
                     "asisma": [k for k in kayitlar if k["butce"] and k["tutar"] > k["butce"]]},
            "feragat": FERAGAT}


def _db_local():
    with _db() as db:
        return db.query(HarcamaKaydi).all()


# ------------------------------------------------------------ ŞİRKET UYUM TAKVİMİ

@r2.get("/uyum")
def uyum_liste():
    kayitlar = _jsonla(_uyum_veriler(), ["id", "sirket", "yukumluluk", "periyot", "son_tarih",
                                         "sorumlu", "kaynak_hukum", "durum"])
    kayitlar.sort(key=lambda x: x["son_tarih"] or "9999")
    bugun_iso = date.today().isoformat()
    return {"kayitlar": kayitlar, "bugun": bugun_iso, "feragat": FERAGAT}


def _uyum_veriler():
    with _db() as db:
        return db.query(UyumYukumlulugu).all()


# ------------------------------------------------------------ DAVA PORTFÖYÜ

@r2.get("/portfoy")
def portfoy_liste():
    kayitlar = _jsonla(_portfoy_veriler(),
                       ["id", "musteri", "konu", "mahkeme", "esas_no", "tarafimiz", "dava_degeri",
                        "kazanma_olasiligi", "asama", "sonraki_adim", "karara_baglanma", "not_metin"])
    toplam_deger = sum(k["dava_degeri"] or 0 for k in kayitlar)
    return {"kayitlar": kayitlar,
            "ozet": {"dosya": len(kayitlar), "toplam_deger": toplam_deger,
                     "davaci": sum(1 for k in kayitlar if k["tarafimiz"] == "Davacı"),
                     "davali": sum(1 for k in kayitlar if k["tarafimiz"] == "Davalı")},
            "feragat": FERAGAT}


def _portfoy_veriler():
    with _db() as db:
        return db.query(DavaPortfoyKayit).all()


# ------------------------------------------------------------ KARŞILAŞTIRMALI MATRİS

@r2.get("/matris")
def matris_liste():
    with _db() as db:
        seti = db.query(MatrisSeti).first()
        hucreler = db.query(MatrisHucre).all()
    s = _jsonla([seti], ["id", "ad", "aciklama"])[0] if seti else None
    return {"seti": s,
            "hucreler": _jsonla(hucreler, ["id", "seti_id", "yargi", "alt_soru", "cevap",
                                           "aciklama", "kaynak", "dogrulandi"]),
            "feragat": FERAGAT,
            "not": "TR referans hücreleri web araştırmasıyla doğrulandı (TBK 444-445). Diğer ülkeler demo tohumdur — kullanım öncesi yerel kaynaklardan teyit edilmelidir."}


class YeniIzleme(BaseModel):
    mahkeme: str
    esas_no: str
    taraflar: str
    son_islem: str = "Dava Açılışı"
    islem_turu: str = "Tebliğ"
    cikarilan_tarih: str | None = None
    tarih_durumu: str = "Teyit edildi"
    haber_notu: str = ""
    kisisel_not: str = ""

@r2.post("/izleme/ekle")
def izleme_ekle(i: YeniIzleme):
    with _db() as db:
        from datetime import date
        ct = date.fromisoformat(i.cikarilan_tarih) if i.cikarilan_tarih else None
        dosya = IzlenenDosya(
            mahkeme=i.mahkeme, esas_no=i.esas_no, taraflar=i.taraflar,
            son_islem=i.son_islem, son_islem_tarihi=date.today(),
            islem_turu=i.islem_turu, cikarilan_tarih=ct,
            tarih_durumu=i.tarih_durumu, haber_notu=i.haber_notu,
            kisisel_not=i.kisisel_not
        )
        db.add(dosya)
        db.commit()
        return {"durum": "ok", "id": dosya.id}


class YeniHarcama(BaseModel):
    buro: str
    dosya: str
    donem: str = "2026-10"
    tutar: float
    butce: float = 0.0
    durum: str = "İncelemede"
    not_metin: str = ""

@r2.post("/harcama/ekle")
def harcama_ekle(h: YeniHarcama):
    with _db() as db:
        kayit = HarcamaKaydi(**h.model_dump())
        db.add(kayit)
        db.commit()
        return {"durum": "ok", "id": kayit.id}


class YeniUyum(BaseModel):
    sirket: str
    yargi: str = "Türkiye"
    form_kodu: str = "TTK m. 409"
    aciklama: str = "Olağan Genel Kurul Toplantısı"
    vade: str
    sorumlu: str = "Şirket Sekreteryası"
    ceza_riski: str = "Re'sen terkin ve idari para cezası"
    portal_linki: str = "https://mersis.gtb.gov.tr"

@r2.post("/uyum/ekle")
def uyum_ekle(u: YeniUyum):
    with _db() as db:
        from datetime import date
        v = date.fromisoformat(u.vade) if u.vade else date.today()
        yuk = UyumYukumlulugu(
            sirket=u.sirket, yukumluluk=u.aciklama,
            periyot="Tek seferlik", son_tarih=v, sorumlu=u.sorumlu,
            kaynak_hukum=u.form_kodu, durum="Planlandı"
        )
        db.add(yuk)
        db.commit()
        return {"durum": "ok", "id": yuk.id}

