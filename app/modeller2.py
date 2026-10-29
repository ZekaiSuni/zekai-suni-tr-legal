"""Eksik kalan 7 modülün veri modelleri (v0.3)."""
from datetime import date

from sqlalchemy import Boolean, Date, Float, Integer, String, Text

from app.db import Base
from sqlalchemy.orm import Mapped, mapped_column


# --------------------------------------------------- Keşif Cevap Kaydı (Discovery → HMK delil/soru listesi)

class KesifSeti(Base):
    __tablename__ = "kesif_seti"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ad: Mapped[str] = mapped_column(String(200))
    dosya: Mapped[str] = mapped_column(String(120), default="")      # hangi dava dosyası
    karsi_taraf: Mapped[str] = mapped_column(String(120), default="")
    tebliğ_tarihi: Mapped[date | None] = mapped_column(Date, nullable=True)
    cevap_sonu: Mapped[date | None] = mapped_column(Date, nullable=True)


class KesifIstemi(Base):
    __tablename__ = "kesif_istemi"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    seti_id: Mapped[int] = mapped_column(Integer)
    sira: Mapped[str] = mapped_column(String(10), default="")        # "1", "2"…
    tur: Mapped[str] = mapped_column(String(40), default="Yazılı soru")
    # Yazılı soru / Belge ibrazı / Bilirkişi sorusu
    metin: Mapped[str] = mapped_column(Text, default="")             # tebliğ edildiği gibi
    durum: Mapped[str] = mapped_column(String(30), default="Bekliyor")
    # Bekliyor / Taslak hazır / Cevaplandı / İtiraz edildi / Süre geçti
    cevap: Mapped[str] = mapped_column(Text, default="")
    kaynak_belge: Mapped[str] = mapped_column(String(200), default="")
    kaynak_konum: Mapped[str] = mapped_column(String(120), default="")
    onaylayan: Mapped[str] = mapped_column(String(100), default="")


# --------------------------------------------------- Patent Talep Karşılaştırması

class PatentKarsilastirma(Base):
    __tablename__ = "patent_karsilastirma"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ad: Mapped[str] = mapped_column(String(200))
    muvekkil_patent: Mapped[str] = mapped_column(String(120), default="")
    referans_patent: Mapped[str] = mapped_column(String(120), default="")


class PatentIstemSatiri(Base):
    __tablename__ = "patent_istem_satir"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    karsilastirma_id: Mapped[int] = mapped_column(Integer)
    istem_no: Mapped[str] = mapped_column(String(10), default="")    # "1[a]", "2"…
    unsuru: Mapped[str] = mapped_column(String(200), default="")     # limitation
    muvekkil_metin: Mapped[str] = mapped_column(Text, default="")
    referans_metin: Mapped[str] = mapped_column(Text, default="")
    hukum: Mapped[str] = mapped_column(String(30), default="İnceleme")
    # Aynı veya daha dar / Daha geniş, farklı veya yok / İnceleme
    kaynak_istem: Mapped[str] = mapped_column(String(40), default="")  # referans claim no
    not_metin: Mapped[str] = mapped_column(Text, default="")


# --------------------------------------------------- Dosya İzleme (Docket watch → UYAP uyarlaması)

class IzlenenDosya(Base):
    __tablename__ = "izlenen_dosya"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mahkeme: Mapped[str] = mapped_column(String(200), default="")
    esas_no: Mapped[str] = mapped_column(String(60), default="")
    taraflar: Mapped[str] = mapped_column(String(300), default="")
    son_islem: Mapped[str] = mapped_column(String(300), default="")   # son tebliğ/tensip özeti
    son_islem_tarihi: Mapped[date | None] = mapped_column(Date, nullable=True)
    islem_turu: Mapped[str] = mapped_column(String(40), default="")   # Tensip/Dilekçe/Celse/Karar
    cikarilan_tarih: Mapped[date | None] = mapped_column(Date, nullable=True)  # örn. celse günü
    tarih_durumu: Mapped[str] = mapped_column(String(20), default="Teyit bekliyor")
    # Teyit bekliyor / Teyit edildi / Metinde geçiyor
    tarih_alinti: Mapped[str] = mapped_column(Text, default="")       # tensipten alıntı
    haber_notu: Mapped[str] = mapped_column(Text, default="")         # "In the news"
    kisisel_not: Mapped[str] = mapped_column(Text, default="")


# --------------------------------------------------- Dış Avukat Harcaması

class HarcamaKaydi(Base):
    __tablename__ = "harcama_kaydi"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    buro: Mapped[str] = mapped_column(String(200))
    dosya: Mapped[str] = mapped_column(String(200), default="")
    donem: Mapped[str] = mapped_column(String(20), default="")        # "2026-10"
    tutar: Mapped[float] = mapped_column(Float, default=0)
    butce: Mapped[float | None] = mapped_column(Float, nullable=True)
    durum: Mapped[str] = mapped_column(String(30), default="Bekliyor")
    # Bekliyor / Onaylandı / Sorgulanacak
    not_metin: Mapped[str] = mapped_column(Text, default="")


# --------------------------------------------------- Şirket Uyum Takvimi (Entity compliance)

class UyumYukumlulugu(Base):
    __tablename__ = "uyum_yukumluluk"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sirket: Mapped[str] = mapped_column(String(200))
    yukumluluk: Mapped[str] = mapped_column(String(200))              # Genel kurul, VERBİS doğrulama…
    periyot: Mapped[str] = mapped_column(String(40), default="")      # Yıllık/Çeyreklik/Aylık
    son_tarih: Mapped[date | None] = mapped_column(Date, nullable=True)
    sorumlu: Mapped[str] = mapped_column(String(100), default="")
    kaynak_hukum: Mapped[str] = mapped_column(String(200), default="")  # TTK m. 416 vb.
    durum: Mapped[str] = mapped_column(String(30), default="Planlandı")


# --------------------------------------------------- Dava Portföyü

class DavaPortfoyKayit(Base):
    __tablename__ = "dava_portfoy"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    musteri: Mapped[str] = mapped_column(String(200))
    konu: Mapped[str] = mapped_column(String(300), default="")
    mahkeme: Mapped[str] = mapped_column(String(200), default="")
    esas_no: Mapped[str] = mapped_column(String(60), default="")
    tarafimiz: Mapped[str] = mapped_column(String(20), default="Davacı")  # Davacı/Davalı
    dava_degeri: Mapped[float | None] = mapped_column(Float, nullable=True)
    kazanma_olasiligi: Mapped[str] = mapped_column(String(20), default="Orta")  # Düşük/Orta/Yüksek
    asama: Mapped[str] = mapped_column(String(60), default="")
    sonraki_adim: Mapped[str] = mapped_column(String(300), default="")
    karara_baglanma: Mapped[date | None] = mapped_column(Date, nullable=True)
    not_metin: Mapped[str] = mapped_column(Text, default="")


# --------------------------------------------------- Karşılaştırmalı Hukuk Matrisi (Survey matrix → TR uyarlaması)

class MatrisSeti(Base):
    __tablename__ = "matris_seti"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ad: Mapped[str] = mapped_column(String(300))                      # ana soru
    aciklama: Mapped[str] = mapped_column(Text, default="")


class MatrisHucre(Base):
    __tablename__ = "matris_hucre"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    seti_id: Mapped[int] = mapped_column(Integer)
    yargi: Mapped[str] = mapped_column(String(80))                    # ülke/yargı
    alt_soru: Mapped[str] = mapped_column(String(120), default="")    # kolon (alt soru)
    cevap: Mapped[str] = mapped_column(String(20), default="Belirsiz")
    # Evet / Hayır / Koşullu / Belirsiz / Uygulanamaz
    aciklama: Mapped[str] = mapped_column(Text, default="")
    kaynak: Mapped[str] = mapped_column(String(300), default="")      # kanun maddesi/karar
    dogrulandi: Mapped[bool] = mapped_column(Boolean, default=False)
