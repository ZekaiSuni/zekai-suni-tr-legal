"""v0.4 — Her modüle veri girişi: form ekleme, dosya analizi, 'Örneği sil'.
Kaynak uygulamadaki 'New review / Drop files / Send to Claude / Delete sample' deseninin karşılığı."""
from __future__ import annotations

import io
import re
from datetime import date

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.cikarim import analiz_yap, metin_oku
from app.db import Oturum
from app.modeller import (AIKullanim, AISatici, Atif, AtifBelgesi, Basvuru, Dosya, Girdi,
                          MevzuatKayit, MusteriKayit, Olay, PlaybookPozisyon, QAAlıcı, QASoru,
                          SozlesmeMaddesi, TabloInceleme, IncelemeSatiri, Talep)
from app.modeller2 import (DavaPortfoyKayit, HarcamaKaydi, IzlenenDosya, KesifIstemi,
                           KesifSeti, MatrisHucre, MatrisSeti, PatentIstemSatiri,
                           PatentKarsilastirma, UyumYukumlulugu)
from app.cikarim_parser import demo_cikarim

rg = APIRouter(prefix="/api/giris")


def _db():
    return Oturum()


class Alan(BaseModel):
    degerler: dict = {}


def _sil(db, model):
    sayi = db.query(model).count()
    for k in db.query(model).all():
        db.delete(k)
    db.commit()
    return sayi


# ---------------------------------------------------------------- ortak silme

@rg.post("/ornek-sil/{modul}")
def ornek_sil(modul: str):
    """'Delete sample' karşılığı: modülün tüm kayıtlarını siler (sıfırdan başlangıç).
    Onay arayüzde yapılır; burada tek modül etkilenir."""
    TABLOLAR = {
        "ihbar": (__import__("app.db", fromlist=["Sozlesme"]).Sozlesme,),
        "playbook-maddeler": (SozlesmeMaddesi,),
        "playbook": (SozlesmeMaddesi,), "masa": (Talep,), "girdi": (Girdi,),
        "inceleme": (IncelemeSatiri, TabloInceleme), "dosya": (Dosya,),
        "kabul": (Basvuru,), "kayit": (MusteriKayit,), "atif": (AtifBelgesi, Atif),
        "kronoloji": (Olay,), "qa": (QASoru,), "envanter": (AIKullanim,),
        "mevzuat": (MevzuatKayit,), "kesif": (KesifIstemi, KesifSeti),
        "izleme": (IzlenenDosya,), "harcama": (HarcamaKaydi,), "uyum": (UyumYukumlulugu,),
        "portfoy": (DavaPortfoyKayit,), "patent": (PatentIstemSatiri, PatentKarsilastirma),
        "matris": (MatrisHucre, MatrisSeti),
    }
    if modul not in TABLOLAR:
        raise HTTPException(404, "Bilinmeyen modül")
    with _db() as db:
        toplam = 0
        for model in TABLOLAR[modul]:
            toplam += _sil(db, model)
    return {"durum": "ok", "silinen": toplam,
            "not": "Örnek veri silindi — artık yalnız sizin girdiğiniz kayıtlar var."}


# ---------------------------------------------------------------- HUKUK MASASI

class TalepEkle(BaseModel):
    baslik: str
    soran_ad: str = ""
    bolum: str = ""
    kategori: str = ""
    metin: str = ""
    risk: str = "Orta"
    hassas: bool = False
    gerek_tarih: str | None = None


@rg.post("/masa/talep/ekle")
def masa_talep_ekle(t: TalepEkle):
    """Yeni talep + demo taslak üretimi: talep metni/başlığı Guidance kayıtlarının
    anahtar kelimeleriyle eşleştirilir; eşleşen kayıtlar taslağı ve muhakeme izini besler.
    (Gerçek modülde bu adım Claude çağrısıdır — demo karşılığı deterministiktir.)"""
    with _db() as db:
        talep = Talep(baslik=t.baslik, soran_ad=t.soran_ad, bolum=t.bolum, kategori=t.kategori,
                      metin=t.metin, risk=t.risk, hassas=t.hassas,
                      gerek_tarih=date.fromisoformat(t.gerek_tarih) if t.gerek_tarih else None,
                      durum="Yeni", olusturma=date.today())
        if not t.hassas:
            arama = (t.baslik + " " + t.metin + " " + t.kategori).lower()
            eslesen = []
            for g in db.query(Girdi).filter(Girdi.onay_durumu == "Onaylı").all():
                sk = 0
                for kw in (g.anahtar_kelimeler or "").split(","):
                    kw = kw.strip().lower()
                    if kw and kw in arama:
                        sk += 1
                if sk:
                    eslesen.append((sk, g))
            eslesen.sort(key=lambda x: -x[0])
            if eslesen:
                ilk = eslesen[0][1]
                talep.taslak = (
                    "Kayıtlarımız bu soruyu yanıtlıyor.\n\n" + ilk.metin + "\n\n"
                    "Lütfen bize şunları iletin: işin belge kopyası; tarihleri; karşı tarafın "
                    "talebinde değişiklik olup olmadığı. Bu taslak avukat onayına bekler.")
                talep.taslak_turu = "Kayıtlar soruyu yanıtlıyor (demo eşleştirme)"
                talep.durum = "Taslak hazır"
                talep.muhakeme_izi = "\n".join(
                    f"- ({g.baslik}) {g.metin[:140]}…" for _, g in eslesen[:4])
                talep.dayanilan_girdiler = __import__("json").dumps([g.baslik for _, g in eslesen[:4]], ensure_ascii=False)
                talep.eksikler = ("Belge kopyası; tarihler; karşı tarafın değişiklik talebi olup olmadığı. "
                                  "Demo eşleştirme anahtar kelime temellidir — zengin eşleşme için Claude anahtarı gerekir.")
                talep.karar_cagrilari = ("- Taslağı olduğu gibi onaylayacak mısınız?\n"
                                         "- Eşleşmeyen bir kayıt var mı?")
                talep.atajan = ilk.sahip
                talep.uzmanlik = ilk.kategori
        db.add(talep)
        db.commit()
        return {"id": talep.id, "taslak_uretildi": bool(talep.taslak)}


class GirdiEkle(BaseModel):
    baslik: str
    metin: str
    kategori: str = ""
    sahip: str = ""
    anahtar_kelimeler: str = ""
    is_birlikleriyle_paylas: bool = True


@rg.post("/masa/girdi/ekle")
def masa_girdi_ekle(g: GirdiEkle):
    with _db() as db:
        db.add(Girdi(baslik=g.baslik, metin=g.metin, kategori=g.kategori, sahip=g.sahip,
                     anahtar_kelimeler=g.anahtar_kelimeler,
                     is_birlikleriyle_paylas=g.is_birlikleriyle_paylas,
                     onay_durumu="Taslak", gecerlilik_tarihi=date.fromordinal(date.today().toordinal() + 180)))
        db.commit()
    return {"durum": "ok", "not": "Kayıt 'Taslak' olarak eklendi — onay bekliyor (görev ayrımı)."}


# ---------------------------------------------------------------- TABLO İNCELEME

@rg.post("/inceleme/yeni-belge")
async def inceleme_yeni(inceleme_id: int, dosya: UploadFile = File(...)):
    """Belge yükle → çıkarım (Claude/demo) → inceleme satırı olarak eklenir.
    'New review + Add documents + Send to Claude' deseninin karşılığı."""
    icerik = await dosya.read()
    sonuc = await analiz_yap(icerik, dosya.filename)
    eksik = [a for a in ("baslangic", "sure_ay", "otomatik_uzatma", "ihbar_deger") if sonuc.get(a) in (None, "Bulunamadı")]
    with _db() as db:
        inc = db.get(TabloInceleme, inceleme_id)
        if not inc:
            inc = TabloInceleme(ad="Yeni inceleme")
            db.add(inc)
            db.flush()
        satir = IncelemeSatiri(
            inceleme_id=inc.id,
            belge_adi=sonuc.get("ad") if sonuc.get("ad") not in (None, "Bulunamadı") else dosya.filename,
            karsi_taraf=sonuc.get("karsi_taraf") or "Bulunamadı",
            sozlesme_turu=sonuc.get("tur") or "Bulunamadı",
            yururluk=sonuc.get("baslangic") or "Bulunamadı",
            bitis_sure=(f"{sonuc['sure_ay']} ay" if sonuc.get("sure_ay") else "Bulunamadı"),
            otomatik_uzatma=("Evet" if sonuc.get("otomatik_uzatma") else
                             "Hayır" if sonuc.get("otomatik_uzatma") is False else "Bulunamadı"),
            taban_hukuk="Bulunamadı — demo çıkarımı bu alanı aramadı; elle girin",
            kontrol_degisikligi="Bulunamadı — arama kapsamı: kontrol değişikliği/devir kalıpları (demo)",
            devir="Bulunamadı — arama kapsamı: devir kalıpları (demo)",
            sorumluluk_tavani="Bulunamadı — arama kapsamı: tavan kalıpları (demo)",
            mali_yukumluluk="Bulunamadı",
            notlar=(sonuc.get("cikarim_notu") or "") + (f" | Kaynak alıntı: {sonuc.get('kaynak_alinti','')[:160]}" if sonuc.get("kaynak_alinti") else ""),
            inceleme_gerekli=bool(eksik) or sonuc.get("cikarim_yontemi") == "demo",
            sahibi="")
        db.add(satir)
        db.commit()
        return {"id": satir.id, "cikarim_yontemi": sonuc.get("cikarim_yontemi"),
                "eksik_alanlar": eksik,
                "not": "Eksik alanlar 'Bulunamadı + arama kapsamı' ile dolduruldu (uydurma yok); satır inceleme kuyruğunda."}


# ---------------------------------------------------------------- PLAYBOOK

KONU_KELIMELERI = {
    "Sorumluluk sınırı": ["sorumluluk", "tavan", "sınırl", "zarar"],
    "Tazminat ve Rücu Taahhüdü": ["tazminat", "rücu", "zarara uğratma", "masuniyet", "indemn"],
    "Uygulanacak hukuk": ["uygulanacak hukuk", "tabi olur", "kanun", "mahkemeler", "tahkim"],
    "Veri işleme": ["kişisel veri", "veri işleme", "kvkk", "model", "makine öğren"],
    "Ödeme": ["ödeme", "fatura", "vade", "faiz"],
    "Devir": ["devir", "temlik", "devret"],
    "Gizlilik": ["gizlilik", "confidential"],
    "Süre ve fesih": ["süre", "fesih", "ihbar", "uzatma"],
}


@rg.post("/playbook/belge-tara")
async def playbook_belge_tara(dosya: UploadFile = File(...)):
    """Sözleşme yükle → playbook konu kelimeleriyle madde taraması (deterministik demo;
    gerçek modülde Claude madde→pozisyon eşleşmesi yapar) → 'İnceleme' durumunda satırlar."""
    metin = metin_oku(await dosya.read(), dosya.filename)
    eklenen = []
    with _db() as db:
        for konu, kelimeler in KONU_KELIMELERI.items():
            for kelime in kelimeler:
                m = re.search(kelime, metin, re.IGNORECASE)
                if not m:
                    continue
                blok_bas = metin.rfind("\n\n", 0, m.start())
                blok_bas = blok_bas + 2 if blok_bas != -1 else 0
                blok_son = metin.find("\n\n", m.start())
                alinti = metin[blok_bas: blok_son if blok_son != -1 else len(metin)].strip()[:340]
                madde = re.search(r"(?:^|\n)\s*(\d+(?:\.\d+)*)[\s.-]", alinti)
                if any(e.sozlesme_adi == dosya.filename and e.madde_adi == konu
                       for e in db.query(SozlesmeMaddesi).all()):
                    continue
                db.add(SozlesmeMaddesi(
                    sozlesme_adi=dosya.filename, karsi_taraf="Bulunamadı (belgeden)",
                    biz_kimiz="Müşteri", kagit_kimi="Onların", madde_adi=konu, durum="İnceleme",
                    sozlesme_alinti=alinti, madde_no=madde.group(1) if madde else "",
                    onerilen_duzenleme="Zekai demo taraması: pozisyon eşleştirmesi insan kararıdır. "
                                       "Claude anahtarıyla otomatik Standart/Fallback/Sapma puanlaması yapılır.",
                    dosya_adi=dosya.filename))
                eklenen.append(konu)
                break
        db.commit()
    return {"durum": "ok", "eklenen_maddeler": eklenen,
            "not": "Demo tarama konu kelimeleriyle çalışır (deterministik). Satırlar 'İnceleme' durumunda — playbook pozisyonlarıyla elle eşleştirin veya Claude anahtarı ekleyin."}


# ---------------------------------------------------------------- KRONOLOJİ

@rg.post("/kronoloji/belge")
async def kronoloji_belge(dosya: UploadFile = File(...)):
    """Belge yükle → metne çevir → tarih+cümle çıkarımı → olaylar (İnceleme durumunda)."""
    metin = metin_oku(await dosya.read(), dosya.filename)
    eklenen = 0
    with _db() as db:
        for m in re.finditer(r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b", metin):
            try:
                tarih = date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
            except ValueError:
                continue
            blok_bas = metin.rfind("\n", 0, m.start()) + 1
            blok_son = metin.find("\n", m.end())
            cumle = metin[blok_bas: blok_son if blok_son != -1 else len(metin)].strip()
            if len(cumle) < 20:
                continue
            tur = "İletişim"
            if re.search(r"sözleşme|protokol|imza", cumle, re.I):
                tur = "Sözleşme"
            elif re.search(r"ödeme|fatura|dekont|bedel", cumle, re.I):
                tur = "Ödeme"
            elif re.search(r"toplantı|görüşme|arabuluc|duruşma", cumle, re.I):
                tur = "Toplantı"
            db.add(Olay(dosya_adi=dosya.filename, tarih=tarih, tur=tur, metin=cumle[:300],
                        kaynak_alinti=cumle, kaynak_dosya=dosya.filename,
                        durum="İnceleme", cikarim_yontemi="demo"))
            eklenen += 1
        db.commit()
    return {"durum": "ok", "eklenen": eklenen,
            "not": "Demo çıkarım: tarih kalıbı + cümle. LLM anahtarıyla olay sınıflandırma ve taraflar da çıkarılır."}


# ---------------------------------------------------------------- ATIF

@rg.post("/atif/belge")
async def atif_belge_ekle(dosya: UploadFile = File(...)):
    metin = metin_oku(await dosya.read(), dosya.filename)
    with _db() as db:
        belge = AtifBelgesi(ad=dosya.filename, metin=metin, olusturma=date.today())
        db.add(belge)
        db.flush()
        belge_id = belge.id
        db.commit()
    from app.moduller import atif_tara
    sonuc = atif_tara(belge_id=belge_id)
    return {"belge_id": belge_id, **sonuc}


# ---------------------------------------------------------------- KEŞİF

@rg.post("/kesif/set")
async def kesif_set_ekle(dosya: UploadFile = File(None), ad: str = "Yeni soru seti",
                         karsi_taraf: str = "", metin: str = ""):
    """Tebliğ edilen soru setini yükle (PDF/Word/txt) veya numaralı metni yapıştır →
    numaralı maddeler istemlere ayrıştırılır ('Request, as served')."""
    if dosya and dosya.filename:
        metin = metin_oku(await dosya.read(), dosya.filename)
    if not metin.strip():
        raise HTTPException(422, "Metin boş — dosya yükleyin veya numaralı soruları yapıştırın")
    with _db() as db:
        seti = KesifSeti(ad=ad, karsi_taraf=karsi_taraf, tebliğ_tarihi=date.today())
        db.add(seti)
        db.flush()
        eklenen = 0
        for satir in metin.splitlines():
            m = re.match(r"^\s*(\d{1,3})[.)]\s+(.{15,})", satir)
            if not m:
                continue
            tur = "Yazılı soru"
            if re.search(r"belge|ibraz|aslı|örneği", m.group(2), re.I):
                tur = "Belge ibrazı"
            elif re.search(r"bilirkişi|uzman", m.group(2), re.I):
                tur = "Bilirkişi sorusu"
            db.add(KesifIstemi(seti_id=seti.id, sira=m.group(1), tur=tur, metin=m.group(2)[:600]))
            eklenen += 1
        db.commit()
    return {"seti_id": seti.id, "eklenen": eklenen,
            "not": "Numaralı maddeler 'tebliğ edildiği gibi' ayrıştırıldı (deterministik)."}


# ---------------------------------------------------------------- İZLEME

TARIH_K = re.compile(r"(\d{1,2})[./](\d{1,2})\.(\d{4})")


@rg.post("/izleme/ekle")
def izleme_ekle(mahkeme: str, esas_no: str, taraflar: str = "", son_islem: str = "",
                islem_turu: str = "Tensip", tensip_metni: str = ""):
    """Tensip/tebligat metnini yapıştır → son tarih kalıbı çıkarılır ('Teyit bekliyor')."""
    cikarilan = None
    alinti = ""
    if tensip_metni:
        m = TARIH_K.search(tensip_metni)
        if m:
            try:
                cikarilan = date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
                bas = max(0, m.start() - 60)
                alinti = tensip_metni[bas: m.end() + 30].strip()
            except ValueError:
                pass
    with _db() as db:
        db.add(IzlenenDosya(mahkeme=mahkeme, esas_no=esas_no, taraflar=taraflar,
                            son_islem=son_islem or "Yeni işlem eklendi",
                            son_islem_tarihi=date.today(), islem_turu=islem_turu,
                            cikarilan_tarih=cikarilan,
                            tarih_durumu="Teyit bekliyor" if cikarilan else "Metinde geçiyor",
                            tarih_alinti=alinti))
        db.commit()
    return {"durum": "ok", "cikarilan_tarih": cikarilan.isoformat() if cikarilan else None,
            "not": "Tarih metinden çıkarıldı ve 'Teyit bekliyor' durumunda — onayınızı bekler."}


# ---------------------------------------------------------------- basit form eklemeleri

def _ekle_router(model, alanlar, router_path):
    class _E(BaseModel):
        pass
    # pydantic dinamik model yerine dict kabul edelim
    def _ekle(degerler: dict):
        with _db() as db:
            temiz = {k: v for k, v in degerler.items() if hasattr(model, k) and v not in ("", None)}
            for a in ("son_tarih", "karara_baglanma", "kosul_son", "sonraki_inceleme", "sonraki_tarih"):
                if a in temiz and isinstance(temiz[a], str):
                    temiz[a] = date.fromisoformat(temiz[a])
            obj = model(**temiz)
            db.add(obj)
            db.commit()
            return {"id": obj.id, "durum": "ok"}
    _ekle.__name__ = "ekle_" + router_path.replace("/", "_")
    rg.post(router_path)(_ekle)


_ekle_router(Dosya, ["ad", "musteri", "alan_kodu", "asama", "sonraki_islem", "sonraki_tarih", "sahibi"], "/dosya/ekle")
_ekle_router(Basvuru, ["ad", "konu_turu", "tek_satir", "iliskili", "iletisim", "kaynak", "asama"], "/kabul/basvuru/ekle")
_ekle_router(MusteriKayit, ["ad", "tur", "neden", "dosya"], "/kabul/kayit/ekle")
_ekle_router(HarcamaKaydi, ["buro", "dosya", "donem", "tutar", "butce", "not_metin"], "/harcama/ekle")
_ekle_router(UyumYukumlulugu, ["sirket", "yukumluluk", "periyot", "son_tarih", "sorumlu", "kaynak_hukum"], "/uyum/ekle")
_ekle_router(DavaPortfoyKayit, ["musteri", "konu", "mahkeme", "esas_no", "tarafimiz", "dava_degeri",
                                "kazanma_olasiligi", "asama", "sonraki_adim", "not_metin"], "/portfoy/ekle")
_ekle_router(QASoru, ["ref", "alici_id", "metin", "kategori", "kimlere"], "/qa/soru/ekle")
_ekle_router(AIKullanim, ["ad", "bolum", "amac", "asama", "sahip_rol", "arac", "satici",
                          "etkiyenler", "veri_gizlilik"], "/envanter/kullanim/ekle")
_ekle_router(AISatici, ["arac", "satici", "onayli_veri_siniflari", "egitim_kullaniyor",
                        "dp_imzali", "saklama", "alt_isleyiciler", "guvenlik_kaniti"], "/envanter/satici/ekle")
_ekle_router(MevzuatKayit, ["baslik", "kaynak", "url", "etki", "kapsam_ozellikleri",
                            "gecer_tarihi", "onerilen_islem"], "/mevzuat/kayit/ekle")
_ekle_router(SozlesmeMaddesi, ["sozlesme_adi", "karsi_taraf", "madde_adi", "durum",
                               "sozlesme_alinti", "madde_no", "sayfa"], "/playbook/madde/ekle")
_ekle_router(PatentIstemSatiri, ["karsilastirma_id", "istem_no", "unsuru", "muvekkil_metin",
                                 "referans_metin", "hukum", "kaynak_istem", "not_metin"], "/patent/satir/ekle")
_ekle_router(MatrisHucre, ["seti_id", "yargi", "alt_soru", "cevap", "aciklama", "kaynak"], "/matris/hucre/ekle")
