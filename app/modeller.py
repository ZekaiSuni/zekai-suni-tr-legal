"""Tüm modüllerin veri modelleri (suite deseni: iskelet + provenance + onay)."""
from datetime import date

from sqlalchemy import Boolean, Date, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


# ------------------------------------------------------- Playbook Sapma Panosu

class PlaybookPozisyon(Base):
    """Kurumun sözleşme maddelerine standart pozisyonu."""
    __tablename__ = "playbook_pozisyon"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    madde_adi: Mapped[str] = mapped_column(String(120))
    standart_metin: Mapped[str] = mapped_column(Text, default="")
    fallback_metin: Mapped[str] = mapped_column(Text, default="")
    kirmizi_cizgi: Mapped[str] = mapped_column(Text, default="")  # Kabul edilemez: ...
    imza_gerekir_fallback: Mapped[bool] = mapped_column(Boolean, default=True)
    imza_gerekmez_standart: Mapped[bool] = mapped_column(Boolean, default=True)


class SozlesmeMaddesi(Base):
    """Bir sözleşmede tespit edilen madde × playbook karşılaştırması."""
    __tablename__ = "sozlesme_maddesi"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sozlesme_adi: Mapped[str] = mapped_column(String(200))
    karsi_taraf: Mapped[str] = mapped_column(String(200), default="")
    biz_kimiz: Mapped[str] = mapped_column(String(20), default="Alıcı")
    kagit_kimi: Mapped[str] = mapped_column(String(20), default="Onların")  # Bizim/Onların
    madde_adi: Mapped[str] = mapped_column(String(120))
    durum: Mapped[str] = mapped_column(String(30), default="İnceleme")
    # Standart | Fallback 1 | Sapma | Kabul edilemez | Eksik | N/A | İnceleme | Bekliyor
    sozlesme_alinti: Mapped[str] = mapped_column(Text, default="")
    madde_no: Mapped[str] = mapped_column(String(20), default="")
    sayfa: Mapped[str] = mapped_column(String(10), default="")
    onerilen_duzenleme: Mapped[str] = mapped_column(Text, default="")
    karsi_tarafa_not: Mapped[str] = mapped_column(Text, default="")
    playbook_eslesen: Mapped[str] = mapped_column(String(30), default="")  # Standart/Fallback 1
    imza_gerekir: Mapped[str] = mapped_column(String(120), default="")
    karar: Mapped[str] = mapped_column(String(30), default="")  # Onaylandı/Reddedildi/Geri gönderildi/Editör kabul etti
    kararin_kimi: Mapped[str] = mapped_column(String(100), default="")
    muhur: Mapped[str] = mapped_column(String(40), default="")  # FNV-1a insan onayı mührü
    dosya_adi: Mapped[str] = mapped_column(String(300), default="")
    playbook_disi: Mapped[bool] = mapped_column(Boolean, default=False)  # Not in our playbook


# ------------------------------------------------------------- Hukuk Masası

class Girdi(Base):
    """Guidance register: hukuk departmanının yazılı standart pozisyonları."""
    __tablename__ = "masa_girdi"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    baslik: Mapped[str] = mapped_column(String(200))
    metin: Mapped[str] = mapped_column(Text)
    kategori: Mapped[str] = mapped_column(String(80), default="")
    onay_durumu: Mapped[str] = mapped_column(String(20), default="Taslak")  # Taslak/Onaylı
    onay_tarihi: Mapped[date | None] = mapped_column(Date, nullable=True)
    gecerlilik_tarihi: Mapped[date | None] = mapped_column(Date, nullable=True)  # review by
    sahip: Mapped[str] = mapped_column(String(100), default="")
    is_birlikleriyle_paylas: Mapped[bool] = mapped_column(Boolean, default=True)  # değilse "Not for colleagues"
    anahtar_kelimeler: Mapped[str] = mapped_column(String(300), default="")  # virgülle


class Talep(Base):
    """İş biriminden gelen hukuk talebi."""
    __tablename__ = "masa_talep"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    baslik: Mapped[str] = mapped_column(String(300))
    soran_ad: Mapped[str] = mapped_column(String(100), default="")
    bolum: Mapped[str] = mapped_column(String(80), default="")     # Satınalma/Satış/Pazarlama/Finans/İK
    kategori: Mapped[str] = mapped_column(String(80), default="")
    metin: Mapped[str] = mapped_column(Text, default="")
    alanlar: Mapped[str] = mapped_column(Text, default="")          # yapılandırılmış giriş (json)
    risk: Mapped[str] = mapped_column(String(20), default="Orta")   # Düşük/Orta/Yüksek/Acil/Hassas
    hassas: Mapped[bool] = mapped_column(Boolean, default=False)
    uzmanlik: Mapped[str] = mapped_column(String(80), default="Ticari Hukuk")
    atanan: Mapped[str] = mapped_column(String(100), default="")
    durum: Mapped[str] = mapped_column(String(30), default="Yeni")
    # Yeni | Taslak hazır | Bilgi bekleniyor | Yönlendirildi | Kapatıldı
    olusturma: Mapped[date | None] = mapped_column(Date, nullable=True)
    gerek_tarih: Mapped[date | None] = mapped_column(Date, nullable=True)
    taslak: Mapped[str] = mapped_column(Text, default="")            # Claude draft
    taslak_turu: Mapped[str] = mapped_column(String(40), default="")  # Standart talimat yanıtlar / Koşullu taslak / —
    dayanilan_girdiler: Mapped[str] = mapped_column(Text, default="")  # json list
    muhakeme_izi: Mapped[str] = mapped_column(Text, default="")       # "Kayıtların söyledikleri" özeti
    eksikler: Mapped[str] = mapped_column(Text, default="")
    karar_cagrilari: Mapped[str] = mapped_column(Text, default="")    # insanın karar noktaları
    gonderen_kimlikle: Mapped[str] = mapped_column(String(100), default="")  # "Sent as"
    muhur: Mapped[str] = mapped_column(String(40), default="")  # FNV-1a insan onayı mührü
    cevap: Mapped[str] = mapped_column(Text, default="")             # insanın son cevabı
    takip_notu: Mapped[str] = mapped_column(Text, default="")


# --------------------------------------------------------- Tablo İnceleme

class TabloInceleme(Base):
    __tablename__ = "tablo_inceleme"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ad: Mapped[str] = mapped_column(String(200))


class IncelemeSatiri(Base):
    __tablename__ = "tablo_inceleme_satir"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    inceleme_id: Mapped[int] = mapped_column(Integer)
    belge_adi: Mapped[str] = mapped_column(String(200))
    karsi_taraf: Mapped[str] = mapped_column(String(200), default="")
    sozlesme_turu: Mapped[str] = mapped_column(String(100), default="")
    yururluk: Mapped[str] = mapped_column(String(100), default="")
    bitis_sure: Mapped[str] = mapped_column(String(200), default="")
    otomatik_uzatma: Mapped[str] = mapped_column(String(20), default="")
    taban_hukuk: Mapped[str] = mapped_column(String(120), default="")
    kontrol_degisikligi: Mapped[str] = mapped_column(Text, default="")
    devir: Mapped[str] = mapped_column(Text, default="")
    sorumluluk_tavani: Mapped[str] = mapped_column(Text, default="")
    mali_yukumluluk: Mapped[str] = mapped_column(String(120), default="")
    notlar: Mapped[str] = mapped_column(Text, default="")
    ciddi_konu: Mapped[bool] = mapped_column(Boolean, default=False)
    okunmayan_sayfa: Mapped[str] = mapped_column(String(40), default="")
    inceleme_gerekli: Mapped[bool] = mapped_column(Boolean, default=False)
    sahibi: Mapped[str] = mapped_column(String(60), default="")


# --------------------------------------------------------------- Dosya Panosu

class Dosya(Base):
    __tablename__ = "dosya"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ad: Mapped[str] = mapped_column(String(200))
    musteri: Mapped[str] = mapped_column(String(120), default="")
    karsi_taraf: Mapped[str] = mapped_column(String(200), default="")
    zamanasimi_tarihi: Mapped[date | None] = mapped_column(Date, nullable=True)
    alan_kodu: Mapped[str] = mapped_column(String(10), default="")  # TİC/AİLE/İŞ/TAŞ/KAMU
    asama: Mapped[str] = mapped_column(String(30), default="Yeni")
    # Aşamasız / Yeni / Aktif / Başkalarını bekliyor / Kapatıldı
    sonraki_islem: Mapped[str] = mapped_column(String(200), default="")
    sonraki_tarih: Mapped[date | None] = mapped_column(Date, nullable=True)
    ikinci_islem: Mapped[str] = mapped_column(String(200), default="")
    ikinci_tarih: Mapped[date | None] = mapped_column(Date, nullable=True)
    sahibi: Mapped[str] = mapped_column(String(80), default="")
    inceleme: Mapped[bool] = mapped_column(Boolean, default=False)
    tarih_teyit: Mapped[bool] = mapped_column(Boolean, default=False)  # Dates to confirm
    orijinal_ornek: Mapped[bool] = mapped_column(Boolean, default=False)  # tohum örnek satırı işareti


# ----------------------------------------------------------- Müvekkil Kabulü

class MusteriKayit(Base):
    """Çatışma indeksi: mevcut müşteriler + hasım taraflar."""
    __tablename__ = "musteri_kayit"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ad: Mapped[str] = mapped_column(String(200))
    tur: Mapped[str] = mapped_column(String(60), default="")   # Müşteri/Hasım/İlgili
    neden: Mapped[str] = mapped_column(Text, default="")       # Why it is here
    dosya: Mapped[str] = mapped_column(String(120), default="")


class Basvuru(Base):
    __tablename__ = "kabul_basvuru"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ad: Mapped[str] = mapped_column(String(200))
    konu_turu: Mapped[str] = mapped_column(String(80), default="")
    tek_satir: Mapped[str] = mapped_column(String(300), default="")
    iliskili: Mapped[str] = mapped_column(String(400), default="")  # Everyone involved
    iletisim: Mapped[str] = mapped_column(String(200), default="")
    kaynak: Mapped[str] = mapped_column(String(120), default="")    # How they found us
    asama: Mapped[str] = mapped_column(String(20), default="Yeni")
    # Yeni/Çatışma/Karar/Mektup/İmzalı/Açık/Reddedildi
    catisma_durumu: Mapped[str] = mapped_column(String(30), default="Çalıştırılmadı")
    # Çalıştırılmadı/1 isabet/Muhtemel çatışma/Temiz/Avukat incelemesi
    catisma_notu: Mapped[str] = mapped_column(Text, default="")
    bekleyen_gun: Mapped[int] = mapped_column(Integer, default=0)
    zekai_ekledi: Mapped[bool] = mapped_column(Boolean, default=False)


# -------------------------------------------------------------- Atıf Denetimi

class AtifBelgesi(Base):
    __tablename__ = "atif_belge"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ad: Mapped[str] = mapped_column(String(200))
    metin: Mapped[str] = mapped_column(Text, default="")
    olusturma: Mapped[date | None] = mapped_column(Date, nullable=True)


class Atif(Base):
    __tablename__ = "atif"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    belge_id: Mapped[int] = mapped_column(Integer)
    ham: Mapped[str] = mapped_column(String(400))              # metindeki orijinal
    yargi: Mapped[str] = mapped_column(String(60), default="")  # Yargıtay/Danıştay/AYM/Anayasa
    daire: Mapped[str] = mapped_column(String(40), default="")  # 11. HD / İDDK / 2. Bölüm
    esas_no: Mapped[str] = mapped_column(String(40), default="")
    karar_no: Mapped[str] = mapped_column(String(40), default="")
    karar_tarihi: Mapped[str] = mapped_column(String(20), default="")
    durum: Mapped[str] = mapped_column(String(30), default="Kaynak gerekli")
    # Kaynak gerekli / Doğrulandı / Karar bulunamadı / İçtihat değişmiş olabilir
    dogrulama_notu: Mapped[str] = mapped_column(Text, default="")
    karar_bulundu: Mapped[bool] = mapped_column(Boolean, default=False)


# ------------------------------------------------------------ Delil Kronolojisi

class Olay(Base):
    __tablename__ = "kronoloji_olay"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dosya_adi: Mapped[str] = mapped_column(String(120), default="")
    tarih: Mapped[date | None] = mapped_column(Date, nullable=True)
    tarihsiz: Mapped[bool] = mapped_column(Boolean, default=False)
    yakinlik: Mapped[str] = mapped_column(String(20), default="Kesin")  # Kesin/Yaklaşık
    tur: Mapped[str] = mapped_column(String(40), default="İletişim")  # İletişim/Toplantı/Sözleşme/Ödeme
    metin: Mapped[str] = mapped_column(Text, default="")
    kaynak_alinti: Mapped[str] = mapped_column(Text, default="")
    kaynak_dosya: Mapped[str] = mapped_column(String(200), default="")
    kaynak_sayfa: Mapped[str] = mapped_column(String(10), default="")
    durum: Mapped[str] = mapped_column(String(20), default="İnceleme")  # İnceleme/Onaylı/İtirazlı
    cikarim_yontemi: Mapped[str] = mapped_column(String(20), default="demo")


# ---------------------------------------------------------- AI Kullanım Envanteri

class AIKullanim(Base):
    __tablename__ = "ai_kullanim"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ad: Mapped[str] = mapped_column(String(200))
    bolum: Mapped[str] = mapped_column(String(80), default="")
    amac: Mapped[str] = mapped_column(Text, default="")
    asama: Mapped[str] = mapped_column(String(40), default="")
    onerilen_katman: Mapped[str] = mapped_column(String(20), default="")  # first pass
    katman: Mapped[str] = mapped_column(String(20), default="Henüz yok")
    # Durdur / Yüksek / Orta / Günlük / Henüz yok
    sahip_rol: Mapped[str] = mapped_column(String(100), default="")
    sahip_kisi: Mapped[str] = mapped_column(String(100), default="")
    arac: Mapped[str] = mapped_column(String(120), default="")
    satici: Mapped[str] = mapped_column(String(120), default="")
    etkiyenler: Mapped[str] = mapped_column(String(300), default="")
    durum: Mapped[str] = mapped_column(String(40), default="Gönderildi")
    # Gönderildi / Onaylandı / Koşullu onaylandı / Reddedildi / Yükseltildi
    kosullar: Mapped[str] = mapped_column(Text, default="")
    kosul_son: Mapped[date | None] = mapped_column(Date, nullable=True)
    veri_gizlilik: Mapped[str] = mapped_column(Text, default="")  # girdi hijyeni notu


class AISatici(Base):
    __tablename__ = "ai_satici"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    arac: Mapped[str] = mapped_column(String(120))
    satici: Mapped[str] = mapped_column(String(120))
    onayli_veri_siniflari: Mapped[str] = mapped_column(String(300), default="")
    egitim_kullaniyor: Mapped[bool] = mapped_column(Boolean, default=False)
    dp_imzali: Mapped[bool] = mapped_column(Boolean, default=False)
    saklama: Mapped[str] = mapped_column(String(120), default="")
    alt_isleyiciler: Mapped[str] = mapped_column(String(300), default="")
    guvenlik_kaniti: Mapped[str] = mapped_column(String(200), default="")
    sozlesme_ref: Mapped[str] = mapped_column(String(120), default="")
    sonraki_inceleme: Mapped[date | None] = mapped_column(Date, nullable=True)


# --------------------------------------------------------------- Satış Q&A

class QAAlıcı(Base):
    __tablename__ = "qa_alici"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ad: Mapped[str] = mapped_column(String(120))
    tur: Mapped[str] = mapped_column(String(40), default="Stratejik")  # Stratejik/Finansal
    kota: Mapped[int] = mapped_column(Integer, default=60)


class QASoru(Base):
    __tablename__ = "qa_soru"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ref: Mapped[str] = mapped_column(String(20))
    alici_id: Mapped[int] = mapped_column(Integer)
    metin: Mapped[str] = mapped_column(Text)
    kategori: Mapped[str] = mapped_column(String(80), default="")
    durum: Mapped[str] = mapped_column(String(30), default="Taslak bekliyor")
    # Geciken / Taslak bekliyor / Taslak hazır / İncelemede / Onaylandı / Yayınlandı / Kapatıldı
    cevap_turu: Mapped[str] = mapped_column(String(60), default="")  # Anlatım/Belgeye bakınız/...
    kimlere: Mapped[str] = mapped_column(String(30), default="Tek alıcı")  # Tek alıcı/Tüm alıcılar
    taslak: Mapped[str] = mapped_column(Text, default="")
    kaynak_belge: Mapped[str] = mapped_column(String(200), default="")
    kaynak_konum: Mapped[str] = mapped_column(String(120), default="")  # "4.2.3, s. 10"
    onaylayan: Mapped[str] = mapped_column(String(100), default="")
    capraz_ifsa_uyari: Mapped[bool] = mapped_column(Boolean, default=False)


# -------------------------------------------------------------- Mevzuat Radar

class MevzuatKayit(Base):
    __tablename__ = "mevzuat_kayit"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    baslik: Mapped[str] = mapped_column(String(300))
    kaynak: Mapped[str] = mapped_column(String(120), default="")   # RG / AB / KVKK / BTK
    url: Mapped[str] = mapped_column(String(400), default="")
    etki: Mapped[str] = mapped_column(String(10), default="Orta")  # Yüksek/Orta/Düşük
    kapsam_ozellikleri: Mapped[str] = mapped_column(String(400), default="")  # covers...
    gecer_tarihi: Mapped[date | None] = mapped_column(Date, nullable=True)
    tarih_durumu: Mapped[str] = mapped_column(String(30), default="Önümüzdeki")
    # Geçti / Önümüzdeki / Henüz tarihsiz / İleride tarih yok
    onerilen_islem: Mapped[str] = mapped_column(Text, default="")
    reviewer: Mapped[str] = mapped_column(String(80), default="")
    dogrulandi: Mapped[bool] = mapped_column(Boolean, default=False)
