"""v0.2'den taşınan modül tohumları (tohum.py öteki oturumca yeniden yazılınca buraya alındı).
Öteki oturumun tohumla() kapsamadığı modüller: Müvekkil indeksi, Başvurular, Atıf, AI Envanteri, Q&A, Mevzuat."""
from datetime import date, timedelta

B = date.today()
GEC = lambda g: B - timedelta(days=g)
ILERI = lambda g: B + timedelta(days=g)

MUSTERI_KAYITLARI = [
    dict(ad="Anadolu Teknoloji A.Ş.", tur="Müşteri", neden="Aktif hizmet sözleşmesi (2023'ten beri)", dosya="Anadolu-çerçeve"),
    dict(ad="Marmara Gıda San. Ltd.", tur="Müşteri", neden="Geçmiş dava muhatabı; 2024'te sulh yoluyla çözüldü", dosya="Marmara-icra"),
    dict(ad="Kuzey Yatırım Holding", tur="Hasım", neden="Aktif ticari dava (E.2024/512)", dosya="Kuzey-dava"),
    dict(ad="Beta Lojistik", tur="İlgili", neden="Müşterimizin ana taşeronu — münhasırlık riski", dosya=""),
]

BASVURULAR = [
    dict(ad="Nessa Parlak", konu_turu="İş hukuku", tek_satir="İşten çıkarılma kıdem tazminatı talebi",
         iliskili="Nessa Parlak; Sunever Tekstil A.Ş.", iletisim="—", kaynak="Web sitesi",
         asama="Yeni", catisma_durumu="Çalıştırılmadı", bekleyen_gun=11, zekai_ekledi=True),
    dict(ad="Maren Petifer", konu_turu="Aile", tek_satir="Anlaşmalı boşanma ve mal rejimi tasfiyesi",
         iliskili="Maren Petifer; Cem Petifer", iletisim="—", kaynak="Web araması",
         asama="Çatışma", catisma_durumu="1 isabet",
         catisma_notu="Cem Petifer, Kuzey Yatırım Holding dosyasında tanık listesinde (E.2024/512).",
         bekleyen_gun=9),
    dict(ad="Korvin Abernati", konu_turu="Kişisel yaralanma", tek_satir="Trafik kazası tazminat davası",
         iliskili="Korvin Abernati; Güven Sigorta A.Ş.", iletisim="—", kaynak="Tavsiye",
         asama="Çatışma", catisma_durumu="Muhtemel çatışma",
         catisma_notu="Güven Sigorta, müşterimizin mütekabil sigortacısı; grup bağı değerlendirilmeli.",
         bekleyen_gun=15),
    dict(ad="Lucinda Dikenmez", konu_turu="Miras", tek_satir="Vasiyetname tenkizi davası",
         iliskili="Lucinda Dikenmez", iletisim="—", kaynak="Baro listesi",
         asama="Karar", catisma_durumu="Temiz", catisma_notu="İndeks temiz.", bekleyen_gun=13),
    dict(ad="Fenrağzı Diş Kliniği", konu_turu="Sözleşme", tek_satir="Klinik ortaklık sözleşmesi",
         iliskili="Fenrağzı Diş Kliniği Ltd.", iletisim="—", kaynak="Tavsiye",
         asama="İmzalı", catisma_durumu="Temiz", bekleyen_gun=0),
]

ATIF_ORNEK = dict(
    ad="Karşı Taraf Dilekçesi — İçtihat Denetimi (örnek)",
    metin=("Davacı, sözleşmenin 4.2 maddesinin feshi haklı neden sayılacağını ileri sürmüş ve\n"
           "Yargıtay 10. HD., E. 2018/1234, K. 2020/5678, T. 14.7.2020 sayılı kararına atıf yapmıştır.\n\n"
           "Ayrıca Danıştay İDDK, E. 2019/2200, K. 2021/1450, T. 3.6.2021 sayılı kararında\n"
           "tebligatın muhataba ulaşmaması halinde sürenin başlamayacağı yönünde karar vermiştir.\n\n"
           "Son olarak AYM, 2. Bölüm, E. 2017/19876, K. 2019/24567, T. 12.11.2019 sayılı\n"
           "bireysel başvuru kararında mülkiyet hakkının ihlal edildiğini kabul etmiştir."),
)

AI_KULLANIMLARI = [
    dict(ad="İşyeri araştırma görüşmelerinin özetlenmesi", bolum="İK", asama="Uygulamada",
         amac="Yerinde araştırma görüşmelerinden tutanak özeti çıkarma",
         onerilen_katman="Durdur", katman="Henüz yok", sahip_rol="İK Direktörü", arac="Ses Özeti Aracı",
         satici="Bilinmiyor", etkiyenler="Çalışanlar", durum="Gönderildi",
         veri_gizlilik="Kişilerin adları ve gizli ayrıntıları girdiye yazılmamalı."),
    dict(ad="E-ticaret ekibine kod önerileri", bolum="Teknoloji", asama="Uygulamada",
         amac="Geliştiricilere kod tamamlama önerileri",
         onerilen_katman="Günlük", katman="Günlük", sahip_rol="CTO", arac="Kod Asistanı",
         satici="Bilinmiyor", etkiyenler="Geliştirici ekibi", durum="Onaylandı",
         kosullar="Üretim verisi girdi olarak kullanılamaz.", kosul_son=ILERI(180),
         veri_gizlilik="Müşteri verisi içeren depolara girdi yasak."),
    dict(ad="Mağaza ve depo rolleri için aday eleme", bolum="İnsan Kaynakları", asama="Pilot",
         amac="Başvuruların otomatik ön eleme puanlaması",
         onerilen_katman="Yüksek", katman="Yüksek", sahip_rol="İK Direktörü", arac="Eleme Sihirbazı",
         satici="ScreenCo", etkiyenler="Adaylar", durum="Koşullu onaylandı",
         kosullar="Her otomatik retten önce insan kararı; adaylara AI kullanımı bildirilecek.",
         kosul_son=GEC(3), veri_gizlilik="Aday verisi yalnız şirket içinde işlenir."),
    dict(ad="Çağrı merkezi çalışanlarının sesinden duygu analizi", bolum="Müşteri Hizmetleri",
         asama="Değerlendirme", amac="Çağrı sesinden çalışan stres skorlaması",
         onerilen_katman="Durdur", katman="Henüz yok", sahip_rol="Müşteri Hizmetleri Direktörü",
         arac="Ses Analizi", satici="Bilinmiyor", etkiyenler="Çağrı merkezi çalışanları",
         durum="Reddedildi",
         veri_gizlilik="Çalışanların duygusal durum analizi çalışma hayatında kullanılamaz."),
]

QA_ALICILAR = [
    dict(ad="Alıcı A (Stratejik)", tur="Stratejik", kota=60),
    dict(ad="Alıcı B (Fon)", tur="Finansal", kota=60),
    dict(ad="Alıcı C (Stratejik)", tur="Stratejik", kota=60),
    dict(ad="Alıcı D (Fon)", tur="Finansal", kota=60),
]

QA_SORULAR = [
    dict(ref="A-002", alici_id=1, kategori="Müşteriler",
         metin="İlk 20 müşteri için SKU bazında fiyat ve hacim bilgisi.",
         durum="Taslak hazır", cevap_turu="Anlatım", kimlere="Tek alıcı",
         taslak=("Top 20 müşteri içinde 2026 cirosunun %10'undan fazlasını oluşturan tek müşteri "
                 "bulunmamaktadır. [Finans Direktörü teyidi: 2026 için %10 üzeri müşteri var mı]"),
         kaynak_belge="musteri-tablosu.xlsx", kaynak_konum="Sayfa 3"),
    dict(ref="D-009", alici_id=4, kategori="Çalışanlar",
         metin="Emeklilik telafi planının yıllık şirkete maliyeti nedir?",
         durum="Onaylandı", cevap_turu="Anlatım", kimlere="Tek alıcı",
         taslak=("Şirket, 31 Mart 2031'e kadar her yıl 1,6 milyon TL eksik fon katkısı ödemeyi "
                 "taahhüt etmektedir (5.4.1 maddesinden onaylı cevap)."),
         kaynak_belge="calisan-plani.pdf", kaynak_konum="5.4.1, s. 12",
         onaylayan="Hukuk · Selin K.", capraz_ifsa_uyari=True),
    dict(ref="D-017", alici_id=4, kategori="Hukuki ihtilaflar",
         metin="Açık hukuki ihtilaf var mı?", durum="Geciken", cevap_turu="",
         kimlere="Tek alıcı", taslak="", kaynak_belge="dava-listesi.xlsx", kaynak_konum="—"),
]

MEVZUAT_KAYITLARI = [
    dict(baslik="KVKK: VERBİS kaydı yıllık doğrulama zorunluluğu", kaynak="KVKK",
         url="https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6698", etki="Orta",
         kapsam_ozellikleri="VERBİS kaydı; veri envanteri", gecer_tarihi=None,
         tarih_durumu="İleride tarih yok",
         onerilen_islem="VERBİS doğrulamasını çeyreklik takvime bağla.", reviewer="Selin K.",
         dogrulandi=True),
    dict(baslik="AB Yapay Zeka Tüzüğü: yüksek riskli sistem yükümlülükleri", kaynak="AB",
         url="https://artificialintelligenceact.eu/", etki="Yüksek",
         kapsam_ozellikleri="AB'ye hizmet veren AI sistemleri; insan gözetimi",
         gecer_tarihi=date(2026, 8, 2), tarih_durumu="Önümüzdeki",
         onerilen_islem="AI özellikleri için risk sınıflaması dokümanı hazırla.", reviewer="Erhan T."),
    dict(baslik="6563 e-Ticaret Kanunu: pazarlama onayı ve İYS uyumu", kaynak="BTK",
         url="https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=26847", etki="Yüksek",
         kapsam_ozellikleri="ticari elektronik ileti; İYS; açık rıza", gecer_tarihi=None,
         tarih_durumu="İleride tarih yok",
         onerilen_islem="Pazarlama listelerinin İYS mutabakatını çeyreklik yap.", reviewer="Selin K.",
         dogrulandi=True),
]
