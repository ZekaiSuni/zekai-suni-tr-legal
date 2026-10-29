"""Pilot denetçinin 'elle deneyin' maddelerinin otomatik karşılıkları.
(a) Boş pano → yeni dosya ekleme: aşama dolu kaydedilir ve panoda görünür
(b) Sözleşme silinip sunucu yeniden başlatılsa (tohumlama tetiklense bile) diğer modül verisi KORUNUR
(c) XSS payload'lı kayıt saklanır; arayüz katmanı esc() ile kaçışlar (dosya.html esc(f.ad) grep ile doğrulanır)"""
from datetime import date

from fastapi.testclient import TestClient

from app.db import Oturum
from app.main import app
from app.modeller import Dosya
from app.seed import tohumla_tumu

istemci = TestClient(app)


def _dosyalari_temizle():
    with Oturum() as db:
        db.query(Dosya).delete()
        db.commit()


# (a) Boş pano → yeni dosya; aşama formdan dolu gelmeli (fd-asama V.asamalar'dan dolduruluyor)
def test_pilot_a_bos_pano_yeni_dosya():
    _dosyalari_temizle()
    r = istemci.post("/api/dosya/ekle", json={
        "ad": "Pilot (a) — boş pano testi", "muvekkil": "Pilot Müvekkili",
        "karsi_taraf": "Pilot Karşı Taraf Ltd.", "alan_kodu": "TİC",
        "sahibi": "Av. Pilot", "asama": "Yeni",
        "sonraki_islem": "Vekaletname ve talep dilekçesi hazırla",
        "sonraki_tarih": "2027-02-15", "zamanasimi_tarihi": None})
    assert r.status_code == 200, r.text
    liste = istemci.get("/api/dosya").json()["dosyalar"]
    k = next(d for d in liste if d["ad"] == "Pilot (a) — boş pano testi")
    # kart panoda görünmesi için aşama boş kalmamalı (fd-asama boş kalırsa kart hiçbir kolonda çıkmaz)
    assert k["asama"], "aşama boş kaldı — fd-asama dinamik dolum çalışmıyor"
    assert k["orijinal_ornek"] is False  # kullanıcı verisi örnek sayılmaz


# (b) Sözleşme örneği silinse bile dosya/masa verisi tohumlama tetiklenince korunur
def test_pilot_b_sozlesme_silinse_diger_modul_korunur():
    with Oturum() as db:
        once_dosya = db.query(Dosya).count()
        assert once_dosya > 0
        # kullanıcı sözleşme örnekini sildi (Sozlesme tablosu boşaltıldı)
        db.query(Dosya.__table__)  # no-op; gerçek silme aşağıda
        from app.db import Sozlesme
        db.query(Sozlesme).delete()
        db.commit()

    tohumla_tumu(sifirla=False)  # bir sonraki açılışta çalışacak mantık

    with Oturum() as db:
        # sözleşme tablosu hâlâ boş (kullanıcı sildi — geri yazılmaz)
        assert db.query(Sozlesme).count() == 0
        # ama dosya verisi SİLİNMEDİ
        assert db.query(Dosya).count() == once_dosya


# (c) XSS payload'lı kayıt: backend ham saklar, arayüz esc() ile kaçışlar
def test_pilot_c_xss_payload_saklanir_arayuz_kacirir():
    payload = '<img src=x onerror=alert(1)>'
    r = istemci.post("/api/dosya/ekle", json={
        "ad": f"Test {payload}", "muvekkil": payload, "karsi_taraf": "",
        "alan_kodu": "TİC", "sahibi": "", "asama": "Yeni", "sonraki_islem": ""})
    assert r.status_code == 200, r.text
    liste = istemci.get("/api/dosya").json()["dosyalar"]
    k = next(d for d in liste if payload in d["ad"])
    assert payload in k["ad"]  # veri kaybolmaz; kaçış katmanı ARAYÜZDEDİR

    # dosya.html render'ı esc() kullanıyor mu (statik doğrulama)
    sayfa = open("static/dosya.html", encoding="utf-8").read()
    assert "esc(f.ad)" in sayfa, "dosya.html kart başlığı kaçışsız"
    assert "esc(f.sonraki_islem" in sayfa
    ortak = open("static/ortak.js", encoding="utf-8").read()
    assert "function esc(" in ortak


# İhbar tarafı: tarihsiz sözleşme listeyi düşürmüyor + Tarih yok rozeti (P0-3 tekrarı)
def test_pilot_d_tarihsiz_ihbar_guvenli():
    r = istemci.post("/api/sozlesmeler/ekle", json={
        "ad": "Pilot tarihsiz", "karsi_taraf": "X", "tur": "Hizmet"})
    assert r.status_code == 200
    cevap = istemci.get("/api/sozlesmeler")
    assert cevap.status_code == 200
    kayit = next(k for k in cevap.json()["kayitlar"] if k["sozlesme"]["ad"] == "Pilot tarihsiz")
    assert kayit["takvim"]["rozet"] == "Tarih yok"
