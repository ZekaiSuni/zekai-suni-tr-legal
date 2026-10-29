"""Süre motoru testleri — deterministik hesapların doğruluğu.
Hukuki dayanak: MK m. 12-14, TBK m. 89-93, TBK m. 347, TTK m. 18/3."""
from datetime import date

from app.sure_motoru import ay_ekle, mevcut_donem, son_ihbar_gunu
from app import tatiller


# --- ay ekleme (MK m. 12-14: ayın aynı günü; ay taşıma kuralı)

def test_ay_ekle_aynin_ayni_gunu():
    assert ay_ekle(date(2026, 3, 15), 12) == date(2027, 3, 15)

def test_ay_ekle_ay_sonu_tasmasi():
    # 31 Ocak + 1 ay -> Şubat'ta 31 yok -> ayın son günü (28/29)
    assert ay_ekle(date(2026, 1, 31), 1) == date(2026, 2, 28)

def test_ay_ekle_yil_gecisi():
    assert ay_ekle(date(2026, 11, 15), 3) == date(2027, 2, 15)


# --- son ihbar günü

def test_ihbar_gun_geriye():
    assert son_ihbar_gunu(date(2026, 3, 31), 60, "gün") == date(2026, 1, 30)

def test_ihbar_ay_geriye_aynin_ayni_gunu():
    # 30 Eylül - 3 ay -> 30 Haziran (MK m. 13 karşılık gün)
    assert son_ihbar_gunu(date(2026, 9, 30), 3, "ay") == date(2026, 6, 30)

def test_ihbar_hafta():
    assert son_ihbar_gunu(date(2026, 4, 7), 2, "hafta") == date(2026, 3, 24)


# --- tatil tespiti (web araştırmasıyla doğrulanmış 2026 tarihleri)

def test_1_ocak_2026_tatil():
    assert tatiller.tam_tatil_mi(date(2026, 1, 1))
    assert not tatiller.is_gunu_mu(date(2026, 1, 1))

def test_30_agustos_2026_hafta_sonu_ve_tatil():
    # 30 Ağustos 2026 Pazar gününe denk geliyor
    assert tatiller.hafta_sonu_mu(date(2026, 8, 30))
    assert tatiller.tam_tatil_mi(date(2026, 8, 30))
    # izleyen iş günü 31 Ağustos Pazartesi
    assert tatiller.izleyen_is_gunu(date(2026, 8, 30)) == date(2026, 8, 31)

def test_kurban_bayrami_2026():
    for g in (27, 28, 29, 30):
        assert tatiller.tam_tatil_mi(date(2026, 5, g))
    assert not tatiller.is_gunu_mu(date(2026, 5, 27))

def test_ramazan_bayrami_2026_cuma_tatil():
    # 20 Mart 2026 Cuma — bayram; motor iş günü saymaz
    assert not tatiller.is_gunu_mu(date(2026, 3, 20))

def test_normal_is_gunu_tatil_degil():
    assert tatiller.is_gunu_mu(date(2026, 2, 10))  # Salı


# --- mevcut dönem (otomatik uzatma döngüsü)

def test_otomatik_uzatma_dongusu():
    # Başlangıç 1.4.2025, 12 ay + otomatik 12 ay; bugün 29.10.2026 -> içinde bulunduğumuz dönem 1.4.2026-1.4.2027
    b, bit = mevcut_donem(date(2025, 4, 1), 12, True, 12, date(2026, 10, 29))
    assert (b, bit) == (date(2026, 4, 1), date(2027, 4, 1))

def test_uzatmasiz_sozlesme_gecmisse_donen_ayni_donem():
    b, bit = mevcut_donem(date(2024, 3, 1), 36, False, None, date(2026, 10, 29))
    assert (b, bit) == (date(2024, 3, 1), date(2027, 3, 1))


# --- adli tatil notu: motor sözleşme bildirimlerine adli tatili UYGULAMAZ
def test_temmuz_agustos_is_gunu_sayilir():
    # 5 Ağustos 2026 — adli tatilde ama ticari bildirim için iş günüdür
    assert tatiller.is_gunu_mu(date(2026, 8, 5))


# --- demo çıkarım (parser): yazı sayılar, madde alıntısı

def test_parser_yazi_sayi_doksan():
    from app.cikarim_parser import demo_cikarim
    metin = """MADDE 8 - FESİH
8.2 Bu Sözleşme aynı sürelerle kendiliğinden uzar. Taraflardan her biri, dönemin
bitiminden en az doksan (90) gün önce yazılı olarak bildirmek zorundadır."""
    d = demo_cikarim(metin)
    assert d["otomatik_uzatma"] is True
    assert d["ihbar_deger"] == 90 and d["ihbar_birim"] == "gün"
    assert d["kaynak_madde"] == "8.2"

def test_parser_on_iki_ay():
    from app.cikarim_parser import demo_cikarim
    metin = """MADDE 4 - SÜRE
4.1 Bu Sözleşme on iki (12) ay süreyle yürürlükte kalır."""
    d = demo_cikarim(metin)
    assert d["sure_ay"] == 12

def test_parser_bulunamayan_durustluk():
    from app.cikarim_parser import demo_cikarim
    d = demo_cikarim("Bu sözleşmede özel bir uzatma hükmü yoktur.")
    assert d["otomatik_uzatma"] is None
    assert "uzat" in d["cikarim_notu"]
