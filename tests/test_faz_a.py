"""Faz A regresyon testleri — YAZILIMCI-TALIMATNAMESI.md Bölüm 1 + Bölüm 4 kabul kriterleri.
Her test, talimatname'de belgelenen gerçek hatayı yeniden üretip düzeltmeyi kanıtlar."""
import os

os.environ["ZEKAI_TEST"] = "1"

from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.main import app

istemci = TestClient(app)


# Hata 1.2: masa.html "Onayla ve Gönder" → 200 + Kapatıldı
def test_masa_talep_cevap_onayla():
    # önce bir talep yarat
    r = istemci.post("/api/giris/masa/talep/ekle", json={
        "baslik": "Regresyon testi talebi", "metin": "Test talebi", "soran_ad": "Test",
        "bolum": "Satış", "kategori": "NDA", "risk": "Düşük"})
    assert r.status_code == 200, r.text
    tid = r.json()["id"]
    r = istemci.post(f"/api/masa/talep/{tid}/cevap", json={
        "cevap": "Onaylı cevap", "gonderen_kimlikle": "Hukuk Müşavirliği", "onayla": True})
    assert r.status_code == 200, r.text
    assert r.json()["talep_durumu"] == "Kapatıldı"


# Hata 1.4: /dosya/ekle frontend alanlarıyla (muvekkil/alan/sorumlu/sonraki_adim) 500 VERMEMELİ
def test_dosya_ekle_frontend_sekli():
    r = istemci.post("/api/dosya/ekle", json={
        "ad": "Regresyon test dosyası", "muvekkil": "Test Müvekkili A.Ş.",
        "karsi_taraf": "Test Karşı Taraf Ltd.", "alan": "TİC", "sorumlu": "Av. Test",
        "asama": "Yeni", "sonraki_adim": "Dilekçe yaz", "sonraki_tarih": None,
        "zamanasimi_tarihi": None})
    assert r.status_code == 200, r.text
    did = r.json()["id"]
    # GET /api/dosya içinde yeni alanlar + çatışma kaynaklı karşı taraf dönmeli
    liste = istemci.get("/api/dosya").json()["dosyalar"]
    kayit = next(d for d in liste if d["id"] == did)
    assert kayit["karsi_taraf"] == "Test Karşı Taraf Ltd."
    assert "zamanasimi_tarihi" in kayit


# Hata 1.4: zamanaşımı dolu ekleme (tarih dönüştürme patlamamalı)
def test_dosya_ekle_zamanasimi_dolu():
    son = (date.today() + timedelta(days=100)).isoformat()
    r = istemci.post("/api/dosya/ekle", json={
        "ad": "Zamanaşımı testi", "muvekkil": "Test", "alan": "TİC",
        "sorumlu": "Av. Test", "asama": "Aktif", "sonraki_adim": "",
        "zamanasimi_tarihi": son})
    assert r.status_code == 200, r.text
    liste = istemci.get("/api/dosya").json()["dosyalar"]
    kayit = next(d for d in liste if d["ad"] == "Zamanaşımı testi")
    assert kayit["zamanaasimi_gun"] is not None and 90 <= kayit["zamanaasimi_gun"] <= 100


# Hata 1.4: /kabul/ekle frontend alanlarıyla (basvuran/alan/eposta/konu) 422/500 VERMEMELİ
def test_kabul_ekle_frontend_sekli():
    r = istemci.post("/api/kabul/ekle", json={
        "basvuran": "Test Başvuran", "iliskili": "Test Karşı taraf", "alan": "İş hukuku",
        "eposta": "test@ornek.com", "telefon": "", "konu": "Test konusu"})
    assert r.status_code == 200, r.text
    liste = istemci.get("/api/kabul").json()["basvurular"]
    assert any(b["ad"] == "Test Başvuran" for b in liste)


# Hata 1.4: /kronoloji/ekle (baslik/detay/kaynak_belge) 500 VERMEMELİ
def test_kronoloji_ekle_frontend_sekli():
    r = istemci.post("/api/kronoloji/ekle", json={
        "tarih": "2026-05-02", "baslik": "İhtarname gönderildi",
        "detay": "Müvekkil tarafından ihtarname noter aracılığıyla gönderildi.",
        "kaynak_belge": "ihtarname.pdf", "tur": "İşlem"})
    assert r.status_code == 200, r.text
    olaylar = istemci.get("/api/kronoloji").json()["olaylar"]
    assert any("İhtarname gönderildi" in o["metin"] for o in olaylar)


# Hata 1.3: /api/ornek-geri-yukle 500 VERMEMELİ, veriyi geri yüklemeli
def test_ornek_geri_yukle():
    r = istemci.post("/api/ornek-geri-yukle")
    assert r.status_code == 200, r.text
    # geri yükleme sonrası modüller verili olmalı
    assert istemci.get("/api/kesif").json()["seti"] is not None
    assert len(istemci.get("/api/harcama").json()["kayitlar"]) >= 3


# Hata 1.5: /api/atif/durum kayıt yapıyor (atif.html durumDegistir artık çağırıyor)
def test_atif_durum_kayit():
    belgeler = istemci.get("/api/atif").json()["belgeler"]
    assert belgeler, "Atıf belgesi yok"
    tara = istemci.post(f"/api/atif/tara?belge_id={belgeler[0]['id']}")
    assert tara.status_code == 200, tara.text
    atiflar = istemci.get("/api/atif").json()["atiflar"]
    assert atiflar, "Taramadan atıf çıkmadı"
    a = atiflar[0]
    r = istemci.post("/api/atif/durum", json={
        "atif_id": a["id"], "durum": "Doğrulandı", "not_metin": "Regresyon testi"})
    assert r.status_code == 200, r.text
    guncel = next(x for x in istemci.get("/api/atif").json()["atiflar"] if x["id"] == a["id"])
    assert guncel["durum"] == "Doğrulandı" and "Regresyon testi" in guncel["dogrulama_notu"]


# Çatışma taraması artık Dosya.karsi_taraf'ı da arıyor
def test_catisma_taramasi_dosya_karsi_tarafi():
    # ornek-geri-yukle testi dosyaları sildi — önce karşı taraflı dosyayı yeniden oluştur
    r0 = istemci.post("/api/dosya/ekle", json={
        "ad": "Çatışma Regresyon Dosyası", "muvekkil": "Test Müvekkili",
        "karsi_taraf": "Test Karşı Taraf Ltd.", "alan": "TİC", "sorumlu": "Av. Test",
        "asama": "Aktif", "sonraki_adim": ""})
    assert r0.status_code == 200
    # açık dosyanın karşı tarafını başvurunun iliskili alanına eşleyen başvuru ekle
    r = istemci.post("/api/giris/kabul/basvuru/ekle", json={
        "ad": "Çatışma Regresyon A.Ş.", "konu_turu": "Ticari ihtilaflar",
        "tek_satir": "Test", "iliskili": "Test Karşı Taraf Ltd.; diğerleri",
        "iletisim": "c@o.com", "kaynak": "Test"})
    assert r.status_code == 200
    bid = r.json()["id"]
    r = istemci.post(f"/api/kabul/catisma-tara?basvuru_id={bid}")
    assert r.status_code == 200
    bul = r.json()["bulunan"]
    assert any("Test Karşı Taraf" in x["kayit"] for x in bul), bul


# P1: index.html "Sözleşme ekle" gerçek payload'ı (tarihli)
def test_sozlesme_ekle_frontend_tarihli():
    r = istemci.post("/api/sozlesmeler/ekle", json={
        "ad": "Regresyon Sözleşmesi — tarihli", "karsi_taraf": "Test A.Ş.", "tur": "Hizmet",
        "baslangic": "2026-01-15", "sure_ay": 12, "otomatik_uzatma": True,
        "uzatma_suresi_ay": 12, "ihbar_deger": 3, "ihbar_birim": "ay", "ihbar_sekli": "Noter",
        "fiyat_yillik": 100000})
    assert r.status_code == 200, r.text
    liste = istemci.get("/api/sozlesmeler").json()["kayitlar"]
    kayit = next(k for k in liste if k["sozlesme"]["ad"] == "Regresyon Sözleşmesi — tarihli")
    assert kayit["takvim"]["son_ihbar_tarihi"] is not None  # motor çalışıyor


# P0-3: tarihsiz sözleşme — liste endpoint'i ÇÖKMEMELİ, "Tarih yok" rozeti dönmeli
def test_sozlesme_ekle_tarihsiz_liste_cokmez():
    r = istemci.post("/api/sozlesmeler/ekle", json={
        "ad": "Regresyon Sözleşmesi — tarihsiz", "karsi_taraf": "Test A.Ş.", "tur": "Hizmet"})
    assert r.status_code == 200, r.text
    liste = istemci.get("/api/sozlesmeler")  # 500 olmamalı
    assert liste.status_code == 200
    kayit = next(k for k in liste.json()["kayitlar"]
                 if k["sozlesme"]["ad"] == "Regresyon Sözleşmesi — tarihsiz")
    assert kayit["takvim"]["rozet"] == "Tarih yok"
    assert any("başlangıç tarihi kayıtlı değil" in n for n in kayit["takvim"]["hukuki_notlar"])


# P1: masa talep — gerek_tarih alanı düşmemeli (frontend nt-tarih gönderiyor)
def test_masa_talep_gerek_tarih_korunur():
    r = istemci.post("/api/giris/masa/talep/ekle", json={
        "baslik": "Regresyon tarihli talep", "metin": "test", "soran_ad": "Test",
        "bolum": "Satış", "kategori": "NDA", "risk": "Düşük",
        "gerek_tarih": "2027-03-01"})
    assert r.status_code == 200, r.text
    masa = istemci.get("/api/masa").json()["talepler"]
    t = next(x for x in masa if x["baslik"] == "Regresyon tarihli talep")
    assert t["gerek_tarih"] == "2027-03-01"


# P1: dosya ekle frontend payload'ı alan_kodu/sahibi/sonraki_islem ile (düşen alanlar)
def test_dosya_ekle_tum_alanlar():
    r = istemci.post("/api/dosya/ekle", json={
        "ad": "Alan testi", "muvekkil": "Müvekkil X", "karsi_taraf": "Karşı Y",
        "alan_kodu": "İŞ", "sahibi": "Av. Deniz", "asama": "Aktif",
        "sonraki_islem": "Dilekçe sun", "sonraki_tarih": "2027-02-01"})
    assert r.status_code == 200, r.text
    liste = istemci.get("/api/dosya").json()["dosyalar"]
    k = next(d for d in liste if d["ad"] == "Alan testi")
    assert k["alan_kodu"] == "İŞ" and k["sahibi"] == "Av. Deniz" and k["sonraki_islem"] == "Dilekçe sun"


# P0-1: açılış artık veri SİLMİYOR — verili DB'de tohumla_tumu çağrısı kayıplara yol açmaz
def test_tohumla_tumu_mevcut_veriyi_korur():
    once = istemci.get("/api/sozlesmeler").json()["ozet"]["sozlesme_sayisi"]
    assert once > 0
    from app.seed import tohumla_tumu
    sonuc = tohumla_tumu(sifirla=False)
    assert "korundu" in sonuc["mesaj"]
    sonra = istemci.get("/api/sozlesmeler").json()["ozet"]["sozlesme_sayisi"]
    assert sonra == once
