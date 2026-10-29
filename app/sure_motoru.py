"""
Zekai İhbar Takvimi — DETERMİNİSTİK SÜRE MOTORU (%70 katman).

Bu motor tarih hesabını ASLA LLM'e devretmez (halüsinasyon riski).
Hukuki dayanaklar (web araştırmasıyla doğrulandı, 29 Ekim 2026):
  - TBK m. 89-93 + MK m. 12-14 : süre hesabı (sürenin başladığı gün sayılmaz;
    ay/yıl süreleri "ayın aynı gününe" tamamlanır; vade tatil gününe denk
    gelirse ifa izleyen iş günü yapılır — TBK m. 93).
  - TBK m. 347 : kira ilişkisinin süresiz uzaması ve 10 yıllık uzama süresi;
    kiraya veren 10. yıldan itibaren uzatma yılının sonuna doğru en az 3 ay
    önce yazılı fesih bildiriminde bulunabilir (konut/çatılı işyeri).
  - TTK m. 18/3 : tacirler, hakkın korunması veya edimin ifası için öngörülen
    ihtarname ve ihbarnameleri KEP (kayıtlı elektronik posta) ile gönderebilir.
  - Adli tatil (20 Temmuz - 31 Ağustos, HMK m. 102) YALNIZ yargı işlemlerine
    uygulanır; sözleşme fesih bildirimlerine uygulanmaz — motor bunu
    dönüştürmez, yalnız bilgi notu olarak işaretler.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass, field
from datetime import date, timedelta

AY_ADLARI = ("Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara")


def tr_gun(d: date) -> str:
    return f"{d.day:02d} {AY_ADLARI[d.month - 1]} {d.year}"

from app import tatiller


# ---------------------------------------------------------------- yardımcılar

AYLAR_TR = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]


def _tr_tarih_str(d: date) -> str:
    return f"{d.day:02d} {AYLAR_TR[d.month - 1]} {d.year}"


def ay_ekle(baslangic: date, ay_sayisi: int) -> date:
    """MK m. 12-14 / TBK m. 92-93 uyarınca ay ekler: süre, sona erdiği günün
    karşılığı güne ('ayın aynı gününe') tamamlanır. Ay o kadar günü içermiyorsa
    ayın son günü esas alınır (ör. 31 Ocak + 1 ay -> 28/29 Şubat)."""
    aylik_toplam = baslangic.month - 1 + ay_sayisi
    yil = baslangic.year + aylik_toplam // 12
    ay = aylik_toplam % 12 + 1
    gun = min(baslangic.day, calendar.monthrange(yil, ay)[1])
    return date(yil, ay, gun)


def donem_bitisi(baslangic: date, sure_ay: int | None, tur: str = "ay") -> date | None:
    if tur == "ay" and sure_ay:
        return ay_ekle(baslangic, sure_ay)
    return None


# ---------------------------------------------------------------- hesaplar

@dataclass
class IhtarHesabi:
    """Bir sözleşmenin takvim çıktısı — tüm alanlar deterministik."""
    sozlesme_id: int
    ad: str
    karsi_taraf: str
    tur: str
    donem_baslangici: date          # mevcut dönemin başlangıcı (gösterim için)
    donem_bitisi: date | None       # mevcut dönemin bitişi
    son_ihbar_tarihi: date | None
    son_ihbar_tatil_mi: bool = False
    tatil_adi: str | None = None
    onerilen_is_gunu: date | None = None    # TBK m. 93 önerisi (bilgi amaçlı)
    kalan_gun: int | None = None            # son ihbara kalan takvim günü
    rozet: str = "Belirsiz"                 # Kaçtı / İhbar gönderildi / X gün / — X gün / Bitmiş
    rozet_turu: str = "gri"                 # kirmizi/sari/yesil/gri/standart
    kimse_islem_yapmazsa: str = ""
    hukuki_not: list[str] = field(default_factory=list)
    band: dict = field(default_factory=dict)  # UI bant koordinatları (ISO tarihler)


def mevcut_donem(baslangic: date, sure_ay: int, otomatik_uzatma: bool,
                 uzatma_suresi_ay: int | None, bugun: date) -> tuple[date, date]:
    """Bugünü kapsayan dönemi bulur.
    - Otomatik uzatmalı: başlangıç + sure_ay bitiş; bitiş<bugun ise uzatma_suresi_ay
      dönemleriyle ilerler (TBK m. 347/1 'aynı koşullarda yenilenmiş sayılır').
    - Uzatmasız sabit süreli: tek dönem; bittiyse yine bitişi döndürür (geçmiş görünüm)."""
    bitis = ay_ekle(baslangic, sure_ay)
    if not otomatik_uzatma:
        return baslangic, bitis
    adim = uzatma_suresi_ay or sure_ay
    guvenlik = 0
    while bitis < bugun and guvenlik < 100:
        baslangic = bitis
        bitis = ay_ekle(bitis, adim)
        guvenlik += 1
    return baslangic, bitis


def son_ihbar_gunu(donem_bitisi: date, deger: int | None, birim: str | None) -> date | None:
    """İhbarın en geç ulaştırılması gereken gün.
    - gün  : takvim günü geriye
    - hafta: 7 gün çarpanı
    - ay   : ayın aynı günü geriye (MK m. 13; ör. 30 Eylül - 3 ay -> 30 Haziran)"""
    if not deger:
        return None
    if birim == "gün":
        yil, ay, gun = donem_bitisi.year, donem_bitisi.month, donem_bitisi.day
        # takvim günü geriye: date aritmetiği
        from datetime import timedelta
        return donem_bitisi - timedelta(days=deger)
    if birim == "hafta":
        from datetime import timedelta
        return donem_bitisi - timedelta(weeks=deger)
    if birim == "ay":
        # geriye ay: aynı gün, ay taşarsa hedef ayın son günü
        toplam = donem_bitisi.month - 1 - deger
        yil = donem_bitisi.year + toplam // 12
        ay = toplam % 12 + 1
        gun = min(donem_bitisi.day, calendar.monthrange(yil, ay)[1])
        return date(yil, ay, gun)
    return None


def hesapla(s: "object", bugun: date | None = None) -> IhtarHesabi:
    """Sozlesme kaydından takvim hesabını üretir (LLM'siz, saf Python)."""
    bugun = bugun or date.today()
    from app.db import Sozlesme  # yalnız tip ipucu için

    # P0-3: başlangıç tarihi olmayan kayıt için güvenli çıkış — hesap yapılmaz, çökmez
    if not s.baslangic:
        hesap = IhtarHesabi(
            sozlesme_id=s.id, ad=s.ad, karsi_taraf=s.karsi_taraf, tur=s.tur,
            donem_baslangici=None, donem_bitisi=None, son_ihbar_tarihi=None,
            rozet="Tarih yok", rozet_turu="gri",
            kimse_islem_yapmazsa="—",
            hukuki_not=["Sözleşmenin başlangıç tarihi kayıtlı değil — hesap yapılmadı. "
                        "Tarihi girin; motor hesabı deterministik olarak yapar."])
        s.inceleme = True
        hesap.band = {"pencere_bas": None, "pencere_son": None, "bugun": bugun.isoformat()}
        return hesap

    donem_bas, donem_bit = mevcut_donem(
        s.baslangic, s.sure_ay, s.otomatik_uzatma, s.uzatma_suresi_ay, bugun
    ) if s.sure_ay else (s.baslangic, None)

    son_ihbar = son_ihbar_gunu(donem_bit, s.ihbar_deger, s.ihbar_birim) if donem_bit else None

    hesap = IhtarHesabi(
        sozlesme_id=s.id, ad=s.ad, karsi_taraf=s.karsi_taraf, tur=s.tur,
        donem_baslangici=donem_bas, donem_bitisi=donem_bit, son_ihbar_tarihi=son_ihbar,
    )

    # Tatil çakışması (bilgi — tarih OTOMATİK değiştirilmez; dürüstlük deseni)
    if son_ihbar:
        # P1: kullanıcının "Tatiller" ekranından eklediği tatiller de dikkate alınır
        try:
            from app.db import Oturum as _Oturum
            from app.modeller import Tatil as _TatilKayit
            with _Oturum() as _tdb:
                for tk in _tdb.query(_TatilKayit).all():
                    if tk.tarih == son_ihbar:
                        hesap.son_ihbar_tatil_mi = True
                        hesap.tatil_adi = tk.ad or "Kullanıcı tanımlı tatil"
                        hesap.hukuki_not.append(
                            f"Son ihbar günü kullanıcının tanımladığı tatile denk geliyor ({tk.ad}).")
        except Exception:
            pass  # tatil tablosu okunamadıysa statik takvim yeterli
        if tatiller.tam_tatil_mi(son_ihbar):
            hesap.son_ihbar_tatil_mi = True
            hesap.tatil_adi = tatiller.tatil_adi(son_ihbar)
            hesap.onerilen_is_gunu = tatiller.izleyen_is_gunu(son_ihbar)
            hesap.hukuki_not.append(
                f"Son ihbar günü ({son_ihbar.isoformat()}) resmî tatile denk geliyor"
                f"{f' ({hesap.tatil_adi})' if hesap.tatil_adi else ''}. "
                f"TBK m. 93 mütalaasıyla bildirimi {hesap.onerilen_is_gunu.isoformat()} "
                "(izleyen iş günü) yapmak düşünülebilir; ancak kesinlik için avukat "
                "onayı önerilir — tarih motoru otomatik değiştirmez."
            )
        elif tatiller.hafta_sonu_mu(son_ihbar):
            hesap.son_ihbar_tatil_mi = True
            hesap.tatil_adi = "Hafta sonu"
            hesap.onerilen_is_gunu = tatiller.izleyen_is_gunu(son_ihbar)
            hesap.hukuki_not.append(
                f"Son ihbar günü hafta sonuna denk geliyor. KEP (TTK m. 18/3) kesintisiz "
                f"çalıştığı için bildirim hafta sonunda da yapılabilir; noter yolu "
                "tercih edilecekse {0} (izleyen iş günü) değerlendirilebilir.".format(
                    hesap.onerilen_is_gunu.isoformat())
            )
        if tatiller.yarim_tatil_mi(son_ihbar):
            hesap.hukuki_not.append(
                "Son ihbar günü bayram arifesi (yarım gün) — kurumların kapanış saati "
                "erkenleyebilir; KEP gönderimi saat kısıtlamasına tabi değildir."
            )

    # Rozet
    if s.karar == "İhbar gönderildi":
        hesap.rozet = "İhbar gönderildi"
        hesap.rozet_turu = "yesil"
    elif son_ihbar and donem_bit:
        kalan = (son_ihbar - bugun).days
        hesap.kalan_gun = kalan
        if bugun > son_ihbar:
            if bugun >= donem_bit:
                hesap.rozet = "Dönem bitti"
                hesap.rozet_turu = "gri"
            else:
                hesap.rozet = "Kaçtı"
                hesap.rozet_turu = "kirmizi"
        elif kalan <= 7:
            hesap.rozet = f"{kalan} gün"
            hesap.rozet_turu = "kirmizi"
        elif kalan <= 45:
            hesap.rozet = f"{kalan} gün"
            hesap.rozet_turu = "sari"
        else:
            hesap.rozet = f"— {kalan} gün"
            hesap.rozet_turu = "gri"
    else:
        hesap.rozet = "Belirsiz"
        hesap.rozet_turu = "gri"
        hesap.hukuki_not.append(
            "İhbar süresi sözleşmeden çıkarılamadı — maddeleri kontrol edin. "
            "Çıkarım eksik olduğu için takvim hesabı yapılmadı (uydurma tarih yok)."
        )
        s.inceleme = True

    # P1: ±1 gün dürüstlük notu (MK m. 13 yorum farkı)
    if donem_bitisi:
        hesap.hukuki_not.append(
            "Dönem bitişi 'ayın aynı günü' kuralıyla hesaplandı (MK m. 13). Başlangıç gününün "
            "sayılıp sayılmayacağı yorumuna göre ±1 günlük fark olabilir — kritik ihbarlarda "
            "bir gün önce göndermek güvenli taraftır.")

    # Kimse işlem yapmazsa
    if s.otomatik_uzatma and donem_bit:
        artis = f" · %{s.uzatma_artis_yuzdesi} artış" if getattr(s, "uzatma_artis_yuzdesi", None) else ""
        hesap.kimse_islem_yapmazsa = (
            f"{_tr_tarih_str(ay_ekle(donem_bit, s.uzatma_suresi_ay or s.sure_ay))} "
            f"tarihine kadar uzar{artis}".replace("· %None artış", "")
        )
    elif donem_bit:
        hesap.kimse_islem_yapmazsa = f"{_tr_tarih_str(donem_bit)} tarihinde sona erer (uzatma yok)"

    # Kira özel notu (TBK 347)
    if s.tur.lower().startswith("kira") and s.otomatik_uzatma:
        gecen_yil = ((bugun - s.baslangic).days) // 365
        if gecen_yil >= 10:
            hesap.hukuki_not.append(
                "TBK m. 347/2: 10 yıllık uzama süresi dolmuş konut/çatılı işyeri "
                "kiralanmasında kiraya veren, her uzatma yılının sonuna doğru en az "
                "3 ay önce yazılı fesih bildirimi yapabilir."
            )

    # Bant koordinatları (UI)
    gosterim_bas = min(donem_bas, bugun)
    hesap.band = {
        "pencere_bas": gosterim_bas.isoformat(),
        "pencere_son": (max(donem_bit or bugun, bugun) + timedelta(days=200)).isoformat() if donem_bit else None,
        "donem_bas": donem_bas.isoformat(),
        "donem_son": donem_bit.isoformat() if donem_bit else None,
        "ihbar_gunu": son_ihbar.isoformat() if son_ihbar else None,
        "bugun": bugun.isoformat(),
        "uzarsa_son": (ay_ekle(donem_bit, (s.uzatma_suresi_ay or s.sure_ay or 12))).isoformat()
            if (s.otomatik_uzatma and donem_bit) else None,
    }
    return hesap
