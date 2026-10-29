"""Örnek veri: kurgusal Türk şirketleri, gerçekçi Türkçe sözleşme maddeleri.
Suite'in pedagojisi: çalışır örnek veriyle açılış — kullanıcının ilk gerçek
verisi gelince örneğin gizlenmesi arayüzde işaretlenir.
"""
from datetime import date

from app.db import Oturum

ORNEKLER = [
    dict(
        ad="Karayel Lojistik A.Ş. — Depolama Hizmet Sözleşmesi",
        karsi_taraf="Karayel Lojistik A.Ş.", tur="Hizmet",
        baslangic=date(2025, 4, 1), sure_ay=12, otomatik_uzatma=True,
        uzatma_suresi_ay=12, uzatma_artis_yuzdesi=25,  # TÜFE yerine %25 tavan
        ihbar_deger=3, ihbar_birim="ay", ihbar_sekli="Yazılı",
        fiyat_yillik=285000.0,
        kaynak_alinti=(
            "12.3 Bu Sözleşme bir (1) yıllık süre için akdedilmiş olup, sürenin "
            "bitiminden itibaren aynı sürelerle kendiliğinden uzar. Taraflardan "
            "her biri, uzatma döneminin başlamasından en az üç (3) ay önce yazılı "
            "olarak bildirimde bulunarak Sözleşmeyi sona erdirebilir."),
        kaynak_madde="12.3", kaynak_sayfa="7", kaynak_dosya="karayel-depolama-sozlesmesi.pdf",
        sahibi="Hukuk · Selin K.", inceleme=False, cikarim_yontemi="demo",
        notlar="Örnek veri. 3 ay ihbar 'ayın aynı günü' kuralıyla geriye hesaplanır (MK m. 13).",
    ),
    dict(
        ad="Meridyen Gayrimenkul — Merkez Ofis İşyeri Kirası",
        karsi_taraf="Meridyen Gayrimenkul Yatırım A.Ş.", tur="Kira",
        baslangic=date(2014, 11, 1), sure_ay=36, otomatik_uzatma=True,
        uzatma_suresi_ay=12, uzatma_artis_yuzdesi=0,
        ihbar_deger=3, ihbar_birim="ay", ihbar_sekli="Noter",
        fiyat_yillik=540000.0,
        kaynak_alinti=(
            "5.1 Kira ilişkisi 36 ay süreyle kurulmuştur. Sürenin sonunda taraflar "
            "aksini kararlaştırmadıkça kira ilişkisi TBK hükümleri uyarınca uzar. "
            "Kiracı, ilişkinin sona ermesinden en az üç ay önce yazılı bildirimde bulunarak ayrılabilir."),
        kaynak_madde="5.1", kaynak_sayfa="3", kaynak_dosya="meridyen-kira-sozlesmesi.pdf",
        sahibi="Hukuk · Erhan T.", inceleme=False, cikarim_yontemi="demo",
        notlar=(
            "TBK m. 347 senaryosu: 10 yıllık uzama süresi doldu — kiraya veren artık "
            "sürenin bitimine dayanamaz; her uzatma yılının sonuna doğru en az 3 ay "
            "önce bildirimle feshedebilir. Motor bu notu otomatik üretir."),
    ),
    dict(
        ad="Anka Temizlik — Genel Alan Temizlik Hizmetleri",
        karsi_taraf="Anka Temizlik ve Destek Hizmetleri Ltd. Şti.", tur="Hizmet",
        baslangic=date(2025, 9, 15), sure_ay=12, otomatik_uzatma=True,
        uzatma_suresi_ay=12, uzatma_artis_yuzdesi=30,
        ihbar_deger=60, ihbar_birim="gün", ihbar_sekli="KEP",
        fiyat_yillik=132000.0,
        kaynak_alinti=(
            "7.2 Bu sözleşme 12 ay süreyle yürürlükte kalır ve aksi yazılı olarak "
            "kararlaştırılmadıkça aynı şartlarla otomatik olarak uzatılır. Fesih "
            "istemleri, süre bitiminden en az 60 (altmış) gün önce kayıtlı "
            "elektronik posta (KEP) sistemi üzerinden yapılır."),
        kaynak_madde="7.2", kaynak_sayfa="9", kaynak_dosya="anka-temizlik-sozlesmesi.docx",
        sahibi="", inceleme=False, cikarim_yontemi="demo",
        notlar="Örnek veri. İhbar şekli KEP (TTK m. 18/3): hafta sonu dahil kesintisiz gönderilebilir.",
    ),
    dict(
        ad="MegaSunucu Bilişim — Bulut Barındırma Aboneliği",
        karsi_taraf="MegaSunucu Bilişim Hizmetleri A.Ş.", tur="Lisans",
        baslangic=date(2024, 3, 1), sure_ay=36, otomatik_uzatma=False,
        uzatma_suresi_ay=None, uzatma_artis_yuzdesi=None,
        ihbar_deger=None, ihbar_birim=None, ihbar_sekli=None,
        fiyat_yillik=198000.0,
        kaynak_alinti=(
            "3.1 Abonelik dönemi 36 aydır ve tarafların yazılı mutabakatı dışında "
            "uzatılmaz. Dönemin bitiminde hizmet durdurulur; veriler 30 gün içinde "
            "müşteriye teslim edilir."),
        kaynak_madde="3.1", kaynak_sayfa="4", kaynak_dosya="megasunucu-barindirma.pdf",
        sahibi="IT · Deniz A.", inceleme=False, cikarim_yontemi="demo",
        notlar="Örnek veri. Otomatik uzatma yok — sadece dönem bitiş tarihi izlenir.",
    ),
    dict(
        ad="Boğaziçi Dağıtım — Bayilik Sözleşmesi",
        karsi_taraf="Boğaziçi İçecek Dağıtım San. ve Tic. Ltd. Şti.", tur="Bayilik",
        baslangic=date(2021, 7, 1), sure_ay=60, otomatik_uzatma=True,
        uzatma_suresi_ay=24, uzatma_artis_yuzdesi=10,
        ihbar_deger=6, ihbar_birim="ay", ihbar_sekli="Noter",
        fiyat_yillik=420000.0,
        kaynak_alinti=(
            "16.4 Bayilik sözleşmesi beş (5) yıl için kurulmuştur. Süre sonunda "
            "taraflardan hiçbiri fesih bildiriminde bulunmamışsa sözleşme yirmi dört "
            "(24) aylık dönemlerle uzar; bu uzatmanın önlenebilmesi için fesih "
            "bildirimi altı (6) ay önceden noter kanalıyla tebliğ edilir."),
        kaynak_madde="16.4", kaynak_sayfa="12", kaynak_dosya="bogazici-bayilik.pdf",
        sahibi="", inceleme=False, cikarim_yontemi="demo",
        notlar="Örnek veri. 6 ay ihbar süresi; noter bildirimi hafta sonuna denk gelirse dikkate alın.",
    ),
    dict(
        ad="Pergel Danışmanlık — Veri Analitiği Çerçeve Sözleşmesi",
        karsi_taraf="Pergel Danışmanlık ve Teknoloji Ltd. Şti.", tur="Hizmet",
        baslangic=date(2025, 2, 1), sure_ay=24, otomatik_uzatma=True,
        uzatma_suresi_ay=12, uzatma_artis_yuzdesi=None,
        ihbar_deger=None, ihbar_birim=None, ihbar_sekli="Yazılı",
        fiyat_yillik=310000.0,
        kaynak_alinti=(
            "9.1 Sözleşme 24 aylık süreyi kapsar ve taraflarca yazılı olarak "
            "başka türlü kararlaştırılmadıkça kendiliğinden uzamaz."),
        kaynak_madde="9.1", kaynak_sayfa="6", kaynak_dosya="pergel-cerceve.docx",
        sahibi="Hukuk · Selin K.", inceleme=True, cikarim_yontemi="demo",
        notlar=(
            "Örnek veri. İhbar süresi maddede düzenlenmemiş — 'kendiliğinden uzamaz' "
            "ifadesi var. İnceleme kuyruğunda: uzatma olmasa da hizmetin kesintiye "
            "uğramaması için devir planı gerekir."),
    ),
]

# ---------------------------------------------------------------- tohumla_tumu
# Öteki oturumun tohum.tohumla() 6 ana grubu (Sözleşme/İnceleme/Masa/Playbook/Dosya/Olay)
# kendi oturumunda sil+yeniden yazar. Buradaki fonksiyon kalan modülleri ekler ve
# tek tohumlama noktası olur (main.py startup + /api/ornek-geri-yukle birlikte kullanır).


def _geri_kalan_moduller(db):
    """tohum.tohumla() kapsamı dışındaki modüller (count==0 ise eklenir)."""
    from datetime import date
    from app.modeller import (AIKullanim, AtifBelgesi, Basvuru, MevzuatKayit,
                              MusteriKayit, QAAlıcı, QASoru)
    from app.modeller2 import (DavaPortfoyKayit, HarcamaKaydi, IzlenenDosya, KesifIstemi,
                               KesifSeti, MatrisHucre, MatrisSeti, PatentIstemSatiri,
                               PatentKarsilastirma, UyumYukumlulugu)
    from app import tohum2, tohum_devam

    if db.query(MusteriKayit).count() == 0:
        for o in tohum_devam.MUSTERI_KAYITLARI:
            db.add(MusteriKayit(**o))
    if db.query(Basvuru).count() == 0:
        for o in tohum_devam.BASVURULAR:
            db.add(Basvuru(**o))
    if db.query(AtifBelgesi).count() == 0:
        b = tohum_devam.ATIF_ORNEK
        db.add(AtifBelgesi(ad=b["ad"], metin=b["metin"], olusturma=date.today()))
    if db.query(AIKullanim).count() == 0:
        for o in tohum_devam.AI_KULLANIMLARI:
            db.add(AIKullanim(**o))
    if db.query(QAAlıcı).count() == 0:
        for o in tohum_devam.QA_ALICILAR:
            db.add(QAAlıcı(**o))
    if db.query(QASoru).count() == 0:
        for o in tohum_devam.QA_SORULAR:
            db.add(QASoru(**o))
    if db.query(MevzuatKayit).count() == 0:
        for o in tohum_devam.MEVZUAT_KAYITLARI:
            db.add(MevzuatKayit(**o))

    # v0.3 modülleri (tohum2)
    if db.query(KesifSeti).count() == 0:
        ks = KesifSeti(**tohum2.KESIF_SETI)
        db.add(ks)
        db.flush()
        for s in tohum2.KESIF_ISTEMLERI:
            db.add(KesifIstemi(seti_id=ks.id, **s))
    if db.query(PatentKarsilastirma).count() == 0:
        pk = PatentKarsilastirma(**tohum2.PATENT_KARSILASTIRMA)
        db.add(pk)
        db.flush()
        for s in tohum2.PATENT_ISTEM:
            db.add(PatentIstemSatiri(karsilastirma_id=pk.id, **s))
    if db.query(IzlenenDosya).count() == 0:
        for o in tohum2.IZLENEN_DOSYALAR:
            db.add(IzlenenDosya(**o))
    if db.query(HarcamaKaydi).count() == 0:
        for o in tohum2.HARCAMALAR:
            db.add(HarcamaKaydi(**o))
    if db.query(UyumYukumlulugu).count() == 0:
        for o in tohum2.UYUMLULUKLAR:
            db.add(UyumYukumlulugu(**o))
    if db.query(DavaPortfoyKayit).count() == 0:
        for o in tohum2.PORTFOY:
            db.add(DavaPortfoyKayit(**o))
    if db.query(MatrisSeti).count() == 0:
        ms = MatrisSeti(**tohum2.MATRIS_SET)
        db.add(ms)
        db.flush()
        for h in tohum2.MATRIS_HUCRELER:
            db.add(MatrisHucre(seti_id=ms.id, **h))


def tohumla_tumu(db=None, sifirla: bool = False):
    """Tek tohumlama noktası.
    sifirla=False: yalnız boş tabloları doldurur (startup).
    sifirla=True : /api/ornek-geri-yukle — tüm örnek veriyi sıfırlayıp yeniden yazar."""
    from app import tohum
    kendi = db is None
    if kendi:
        db = Oturum()
    # P0-1: startup'ta VERİ SİLME YOK — yalnız boş DB'de tohum çalışır.
    if not sifirla:
        from app.db import Sozlesme
        from app.modeller import SozlesmeMaddesi, TabloInceleme, Talep
        from app.modeller import Dosya as _DosyaG, Olay as _OlayG
        birincil = [Sozlesme, TabloInceleme, Talep, SozlesmeMaddesi, _DosyaG, _OlayG]
        if any(db.query(m).count() > 0 for m in birincil):
            return {"durum": "ok",
                    "mesaj": "Veritabanı boş değil — tohumlama atlandı (mevcut veriler korundu)."}
    if sifirla:
        # tohum.tohumla() kendi 6 grubunu zaten delete+insert yapıyor;
        # kalan modüllerin tablolarını burada temizliyoruz:
        from app.modeller import (AIKullanim, Atif, AtifBelgesi, Basvuru, MevzuatKayit,
                                  MusteriKayit, QAAlıcı, QASoru)
        from app.modeller2 import (DavaPortfoyKayit, HarcamaKaydi, IzlenenDosya, KesifIstemi,
                                   KesifSeti, MatrisHucre, MatrisSeti, PatentIstemSatiri,
                                   PatentKarsilastirma, UyumYukumlulugu)
        for model in (MusteriKayit, Basvuru, Atif, AtifBelgesi, AIKullanim, QAAlıcı, QASoru,
                      MevzuatKayit, KesifIstemi, KesifSeti, PatentIstemSatiri,
                      PatentKarsilastirma, IzlenenDosya, HarcamaKaydi, UyumYukumlulugu,
                      DavaPortfoyKayit, MatrisHucre, MatrisSeti):
            db.query(model).delete()
        db.commit()
    tohum.tohumla()  # 6 ana grup (kendi oturumuyla)
    # Demo görünürlüğü: bir dosyaya yakın (≤30 gün) zamanaşımı ata — uyarı rozeti canlı görünsün
    from app.modeller import Dosya as Dosya2
    ilk = db.query(Dosya2).first()
    if ilk is not None:
        from datetime import timedelta
        ilk.karsi_taraf = ilk.karsi_taraf or "Karşı Taraf A.Ş."
        ilk.zamanasimi_tarihi = date.today() + timedelta(days=25)
    _geri_kalan_moduller(db)
    db.commit()
    return {"durum": "ok", "mesaj": "Tüm 18 modülün örnek verileri hazır."}
