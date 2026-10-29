"""SQLite veri modeli (SQLAlchemy)."""
import os

from datetime import date

from sqlalchemy import Boolean, Date, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DB_YOLU = os.environ.get("ZEKAI_DB", "data/zekai.db")  # testler izole DB kullanır (conftest)
engine = create_engine(
    "sqlite:///" + DB_YOLU,
    connect_args={"check_same_thread": False, "timeout": 30},
)

from sqlalchemy import event, text


@event.listens_for(engine, "connect")
def _wal_ac(dbapi_baglanti, _):
    imlec = dbapi_baglanti.cursor()
    imlec.execute("PRAGMA journal_mode=WAL")
    imlec.execute("PRAGMA busy_timeout=30000")
    imlec.close()


def _kolon_ekle_yoksa(conn, tablo, kolon, tip):
    mevcut = {r[1] for r in conn.execute(text(f"PRAGMA table_info({tablo})"))}
    if kolon not in mevcut:
        conn.execute(text(f"ALTER TABLE {tablo} ADD COLUMN {kolon} {tip}"))


def gocleri_uygula():
    """Idempotent şema göçleri — create_all mevcut tabloya kolon eklemez.
    Göç öncesi veritabanı dosyasının yedeğini alır (veri kaybı yok)."""
    import os
    import shutil
    from datetime import datetime
    if os.path.exists(DB_YOLU):
        yedek = DB_YOLU + ".bak-" + datetime.now().strftime("%Y%m%d")
        if not os.path.exists(yedek):
            shutil.copyfile(DB_YOLU, yedek)
    with engine.begin() as conn:
        _kolon_ekle_yoksa(conn, "dosya", "karsi_taraf", "VARCHAR(200) DEFAULT ''")
        _kolon_ekle_yoksa(conn, "dosya", "zamanasimi_tarihi", "DATE")
        _kolon_ekle_yoksa(conn, "dosya", "orijinal_ornek", "BOOLEAN DEFAULT 1")
        _kolon_ekle_yoksa(conn, "masa_talep", "muhur", "VARCHAR(40) DEFAULT ''")
        _kolon_ekle_yoksa(conn, "sozlesme_maddesi", "muhur", "VARCHAR(40) DEFAULT ''")
Oturum = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Sozlesme(Base):
    __tablename__ = "sozlesmeler"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ad: Mapped[str] = mapped_column(String(200))
    karsi_taraf: Mapped[str] = mapped_column(String(200), default="")
    tur: Mapped[str] = mapped_column(String(40), default="Hizmet")  # Kira/Hizmet/Lisans/Bayilik/Tedarik
    dosya_adi: Mapped[str] = mapped_column(String(300), default="")

    baslangic: Mapped[date | None] = mapped_column(Date, nullable=True)
    sure_ay: Mapped[int | None] = mapped_column(Integer, nullable=True)
    otomatik_uzatma: Mapped[bool] = mapped_column(Boolean, default=False)
    uzatma_suresi_ay: Mapped[int | None] = mapped_column(Integer, nullable=True)
    uzatma_artis_yuzdesi: Mapped[float | None] = mapped_column(Float, nullable=True)

    ihbar_deger: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ihbar_birim: Mapped[str | None] = mapped_column(String(10), nullable=True)  # gün/hafta/ay
    ihbar_sekli: Mapped[str | None] = mapped_column(String(20), nullable=True)  # Yazılı/Noter/KEP

    fiyat_yillik: Mapped[float | None] = mapped_column(Float, nullable=True)
    para_birimi: Mapped[str] = mapped_column(String(6), default="TRY")

    kaynak_alinti: Mapped[str] = mapped_column(Text, default="")
    kaynak_madde: Mapped[str] = mapped_column(String(20), default="")
    kaynak_sayfa: Mapped[str] = mapped_column(String(10), default="")
    kaynak_dosya: Mapped[str] = mapped_column(String(300), default="")

    karar: Mapped[str] = mapped_column(String(40), default="")  # İhbar gönderildi / Yenilensin / Feshedilsin / ""
    karar_notu: Mapped[str] = mapped_column(Text, default="")
    kararin_kimi: Mapped[str] = mapped_column(String(100), default="")
    karar_tarihi: Mapped[date | None] = mapped_column(Date, nullable=True)

    sahibi: Mapped[str] = mapped_column(String(100), default="")
    inceleme: Mapped[bool] = mapped_column(Boolean, default=False)
    duzeltilmis: Mapped[bool] = mapped_column(Boolean, default=False)
    cikarim_yontemi: Mapped[str] = mapped_column(String(20), default="elle")  # claude/demo/elle
    notlar: Mapped[str] = mapped_column(Text, default="")

    def dict(self) -> dict:
        return {
            "id": self.id, "ad": self.ad, "karsi_taraf": self.karsi_taraf,
            "tur": self.tur, "dosya_adi": self.dosya_adi,
            "baslangic": self.baslangic.isoformat() if self.baslangic else None,
            "sure_ay": self.sure_ay, "otomatik_uzatma": self.otomatik_uzatma,
            "uzatma_suresi_ay": self.uzatma_suresi_ay,
            "uzatma_artis_yuzdesi": self.uzatma_artis_yuzdesi,
            "ihbar_deger": self.ihbar_deger, "ihbar_birim": self.ihbar_birim,
            "ihbar_sekli": self.ihbar_sekli,
            "fiyat_yillik": self.fiyat_yillik, "para_birimi": self.para_birimi,
            "kaynak_alinti": self.kaynak_alinti, "kaynak_madde": self.kaynak_madde,
            "kaynak_sayfa": self.kaynak_sayfa, "kaynak_dosya": self.kaynak_dosya,
            "karar": self.karar, "karar_notu": self.karar_notu,
            "kararin_kimi": self.kararin_kimi,
            "karar_tarihi": self.karar_tarihi.isoformat() if self.karar_tarihi else None,
            "sahibi": self.sahibi, "inceleme": self.inceleme,
            "duzeltilmis": self.duzeltilmis, "cikarim_yontemi": self.cikarim_yontemi,
            "notlar": self.notlar,
        }


class Tatil(Base):
    """Kullanıcının elle eklediği tatiller (ör. kurum-specific tatil, doğrulanmış dini bayram)."""
    __tablename__ = "tatiller"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tarih: Mapped[date] = mapped_column(Date)
    ad: Mapped[str] = mapped_column(String(200), default="")
    kaynak: Mapped[str] = mapped_column(String(200), default="elle eklendi")


def baslat():
    import os
    os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(engine)
    gocleri_uygula()
