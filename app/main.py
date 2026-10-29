"""
Zekai Suni — İhbar Takvimi (v0.1)
FastAPI sunucu: statik arayüz + API.
Çalıştırma:  python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
"""
from __future__ import annotations

import os
from datetime import date

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app import export, tatiller
from app.cikarim import analiz_yap
from app.db import Oturum, Sozlesme, Tatil, baslat
from app.modeller import (AIKullanim, AISatici, Atif, AtifBelgesi, Basvuru, Dosya, Girdi,
                          MevzuatKayit, MusteriKayit, Olay, PlaybookPozisyon, QAAlıcı, QASoru,
                          SozlesmeMaddesi, TabloInceleme, Talep, IncelemeSatiri)
from app.moduller import r as modul_router
from app.moduller2 import r2 as modul_router2
from app.giris_api import rg as giris_router
from app.prompt_yoneticisi import rp as prompt_router
from app.seed import ORNEKLER
from app.sure_motoru import hesapla
from app import tohum

app = FastAPI(title="Zekai Suni — Türk Hukuk Suite'i", version="0.7.0")
baslat()
app.include_router(modul_router)
app.include_router(modul_router2)
app.include_router(giris_router)
app.include_router(prompt_router)

FERAGATNAME = ("Zekai Suni ile hazırlanmıştır; hukuki görüş değildir, güvenilmeden "
               "önce bir avukat tarafından gözden geçirilmelidir.")
BIRIM_FIYAT_CHIPI = ""


def _oturum():
    return Oturum()


def _tum_sozlesmeler():
    with _oturum() as db:
        return db.query(Sozlesme).order_by(Sozlesme.baslangic).all()


def _takvim_ciktisi(kayitlar, bugun: date):
    """Kayıtları takvim hesabıyla birlikte döndürür (özet + band + notlar)."""
    cikti = []
    for s in kayitlar:
        h = hesapla(s, bugun)
        k = s.dict()
        k.pop("kaynak_alinti", None)
        cikti.append({
            "sozlesme": k,
            "takvim": {
                "donem_baslangici": h.donem_baslangici.isoformat() if h.donem_baslangici else None,
                "donem_bitisi": h.donem_bitisi.isoformat() if h.donem_bitisi else None,
                "son_ihbar_tarihi": h.son_ihbar_tarihi.isoformat() if h.son_ihbar_tarihi else None,
                "son_ihbar_tatil_mi": h.son_ihbar_tatil_mi,
                "tatil_adi": h.tatil_adi,
                "onerilen_is_gunu": h.onerilen_is_gunu.isoformat() if h.onerilen_is_gunu else None,
                "kalan_gun": h.kalan_gun,
                "rozet": h.rozet,
                "rozet_turu": h.rozet_turu,
                "kimse_islem_yapmazsa": h.kimse_islem_yapmazsa,
                "hukuki_notlar": h.hukuki_not,
                "band": h.band,
            },
        })
    return cikti


# -------------------------------------------------------------------- sayfa

@app.get("/")
def ana_sayfa():
    return FileResponse("static/index.html")


# -------------------------------------------------------------------- API

@app.get("/api/sozlesmeler")
def listele():
    bugun = date.today()
    kayitlar = _tum_sozlesmeler()
    takvim = _takvim_ciktisi(kayitlar, bugun)
    acik_ihbar = sum(1 for t in takvim
                     if t["takvim"]["rozet_turu"] in ("sari", "kirmizi"))
    geciken = sum(1 for t in takvim if t["takvim"]["rozet"] == "Kaçtı")
    inceleme = sum(1 for t in takvim if t["sozlesme"]["inceleme"])
    ornek_mi = any(t["sozlesme"]["cikarim_yontemi"] == "demo" for t in takvim)
    return {
        "format": "zekai-ihbar-takvimi/v1",
        "bugun": bugun.isoformat(),
        "ozet": {
            "sozlesme_sayisi": len(takvim),
            "acik_ihbar_penceresi": acik_ihbar,
            "geciken": geciken,
            "inceleme_gerekli": inceleme,
            "ornek_veri_var": ornek_mi,
        },
        "fiyat_chipi": BIRIM_FIYAT_CHIPI,
        "kayitlar": takvim,
    }


@app.get("/api/sozlesmeler/{sozlesme_id}")
def detay(sozlesme_id: int):
    kayitlar = _tum_sozlesmeler()
    for s in kayitlar:
        if s.id == sozlesme_id:
            h = hesapla(s, date.today())
            return {"sozlesme": s.dict(), "takvim": _takvim_ciktisi([s], date.today())[0]["takvim"],
                    "kaynak_alinti": s.kaynak_alinti}
    raise HTTPException(404, "Sözleşme bulunamadı")


class Guncelleme(BaseModel):
    # Düzenleme formu alanları — 'Corrected' (Düzeltildi) deseni
    ihbar_deger: int | None = None
    ihbar_birim: str | None = None
    ihbar_sekli: str | None = None
    baslangic: str | None = None
    sure_ay: int | None = None
    otomatik_uzatma: bool | None = None
    uzatma_suresi_ay: int | None = None
    uzatma_artis_yuzdesi: float | None = None
    sahibi: str | None = None
    notlar: str | None = None
    karar: str | None = None
    karar_notu: str | None = None
    kararin_kimi: str | None = None


@app.post("/api/sozlesmeler/{sozlesme_id}/guncelle")
def guncelle(sozlesme_id: int, g: Guncelleme):
    with _oturum() as db:
        s = db.get(Sozlesme, sozlesme_id)
        if not s:
            raise HTTPException(404, "Sözleşme bulunamadı")
        duzeltildi = False
        for alan, deger in g.model_dump(exclude_unset=True).items():
            if alan in ("baslangic",) and deger:
                from datetime import datetime
                setattr(s, alan, date.fromisoformat(deger))
            elif alan in ("karar", "karar_notu", "kararin_kimi"):
                if alan == "karar" and deger:
                    s.karar_tarihi = date.today()
                setattr(s, alan, deger or "")
            else:
                if alan in ("ihbar_deger", "ihbar_birim", "ihbar_sekli") and deger is not None:
                    duzeltildi = True
                setattr(s, alan, deger)
        if duzeltildi:
            s.duzeltilmis = True
        db.commit()
    return {"durum": "ok"}


class Ekle(BaseModel):
    ad: str
    karsi_taraf: str = ""
    tur: str = "Hizmet"
    baslangic: str | None = None
    sure_ay: int | None = None
    otomatik_uzatma: bool = False
    uzatma_suresi_ay: int | None = None
    uzatma_artis_yuzdesi: float | None = None
    ihbar_deger: int | None = None
    ihbar_birim: str | None = None
    ihbar_sekli: str | None = None
    fiyat_yillik: float | None = None
    kaynak_alinti: str = ""
    kaynak_madde: str = ""
    kaynak_sayfa: str = ""
    kaynak_dosya: str = ""
    cikarim_yontemi: str = "elle"
    notlar: str = ""


@app.post("/api/sozlesmeler/ekle")
def ekle(e: Ekle):
    with _oturum() as db:
        veri = e.model_dump()
        veri.pop("baslangic", None)  # çift anahtar: ayrıca aşağıda dönüştürülerek veriliyor
        s = Sozlesme(
            **veri,
            baslangic=date.fromisoformat(e.baslangic) if e.baslangic else None,
        )
        db.add(s)
        db.commit()
        return {"id": s.id, "durum": "ok"}


@app.post("/api/analiz")
async def analiz(dosya: UploadFile = File(...)):
    """KVKK maskeleme HER ZAMAN açıktır (P0-4: açık-onay olmadan kapatılamaz).
    Kapsam: TCKN/IBAN/telefon/e-posta. Ad, unvan ve adres KAPSAM DIŞIDIR — avukatlık
    sırrı (Av.K. m. 36) gereği hassas dosyalar dış sağlayıcıya gönderilmeden önce
    elle redakte edilmelidir ya da yerel Ollama seçilmelidir."""
    icerik = await dosya.read()
    if len(icerik) > 20 * 1024 * 1024:
        raise HTTPException(413, "Dosya 20 MB sınırını aşıyor")
    try:
        sonuc = await analiz_yap(icerik, dosya.filename, maskele_kvkk=True)
    except Exception as hata:
        raise HTTPException(422, f"Belge okunamadı: {type(hata).__name__}: {hata}")
    return JSONResponse(sonuc)


# -------------------------------------------------------------------- export

@app.get("/api/export.ics")
def export_ics():
    icerik = export.ics_uret(_tum_sozlesmeler(), date.today())
    return Response(icerik, media_type="text/calendar; charset=utf-8",
                    headers={"Content-Disposition": "attachment; filename=zekai-ihbar-takvimi.ics"})


@app.get("/api/export.csv")
def export_csv():
    icerik = export.csv_uret(_tum_sozlesmeler(), date.today())
    return Response("\ufeff" + icerik, media_type="text/csv; charset=utf-8",
                    headers={"Content-Disposition": "attachment; filename=zekai-ihbar-takvimi.csv"})


@app.get("/api/export.json")
def export_json():
    return Response(export.json_uret(_tum_sozlesmeler(), date.today()),
                    media_type="application/json; charset=utf-8",
                    headers={"Content-Disposition": "attachment; filename=zekai-ihbar-takvimi.json"})


# -------------------------------------------------------------------- tatiller

@app.get("/api/tatiller")
def tatiller_getir():
    yil = date.today().year
    liste = []
    for y in (yil, yil + 1):
        for (ay, gun) in tatiller.TAM_TATILLER.get(y, []):
            liste.append({"tarih": date(y, ay, gun).isoformat(),
                          "ad": tatiller.tatil_adi(date(y, ay, gun)) or "Resmî tatil",
                          "tur": "tam"})
        for (ay, gun) in tatiller.YARIM_TATILLER.get(y, []):
            liste.append({"tarih": date(y, ay, gun).isoformat(),
                          "ad": "Bayram arifesi (yarım gün)", "tur": "yarim"})
    return {"tatiller": liste,
            "yaklasik_not": "2027 dini bayram tarihleri yaklaşiktir — Resmî Gazete "
                            "teyidi öncesi motor yalnız bilgi notu üretir, tarih değiştirmez."}


@app.post("/api/tatiller/ekle")
def tatil_ekle(tarih: str, ad: str = ""):
    with _oturum() as db:
        db.add(Tatil(tarih=date.fromisoformat(tarih), ad=ad or "Kullanıcı tanımlı tatil"))
        db.commit()
    return {"durum": "ok"}




class ModelKesif(BaseModel):
    saglayici: str
    api_key: str = ""
    base_url: str = ""


@app.post("/api/ayarlar/modelleri-getir")
async def modelleri_getir(k: ModelKesif):
    """P1: sağlayıcının canlı /v1/models listesini kullanıcının anahtarıyla çeker.
    Anahtar girdiği an arayüzdeki model kutusu gerçek çalışan modellerle dolar."""
    from app.cikarim import modelleri_getir as kes
    sonuc = await kes(k.saglayici, k.api_key, k.base_url)
    return sonuc


# -------------------------------------------------------------------- başlangıç

@asynccontextmanager
async def yasam_dongusu(app):
    ilk_veri()
    yield

app.router.lifespan_context = yasam_dongusu


def ilk_veri():
    """Tek tohumlama noktası: seed.tohumla_tumu (boş DB'de çalışır)."""
    from app import seed
    seed.tohumla_tumu()



STATIK_DIR = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIK_DIR)), name="static")
