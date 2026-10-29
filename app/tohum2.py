"""v0.3 modüllerinin örnek verileri (kurgusal, gerçekçi)."""
from datetime import date, timedelta

B = date.today()
GEC = lambda g: B - timedelta(days=g)
ILERI = lambda g: B + timedelta(days=g)

KESIF_SETI = dict(
    ad="Karşı Tarafın Yazılı Soruları — Set 1", dosya="Kuzey Yatırım dava (E.2024/512)",
    karsi_taraf="Kuzey Yatırım Holding avukatlığı", tebliğ_tarihi=GEC(21), cevap_sonu=ILERI(9))

KESIF_ISTEMLERI = [
    dict(sira="1", tur="Yazılı soru", durum="Taslak hazır",
         metin="Taraflar arasındaki sözleşmenin 4.2 maddesinin feshedilmesine neden olan olayların kronolojik dökümünü veriniz.",
         cevap="4.2 maddesinin feshi, 02.05.2024 tarihli gecikme bildirimi ve takip eden 60 günlük performans eksikliğine dayanmaktadır. [Sorumlu teyit: kronoloji tablosu Delil Kronolojisi modülünden bağlanacak]",
         kaynak_belge="cevap-dilekcesi-taslak.docx", kaynak_konum="—", onaylayan=""),
    dict(sira="2", tur="Belge ibrazı", durum="İtiraz edildi",
         metin="2023-2024 yıllarına ait tüm iç yazışmaların asıllarının ibrazını talep ederiz.",
         cevap="İtiraz ediyoruz: talep sınırsız keşif niteliğindedir (HMK m. 219/2 — belirli delil bağlamı gerekir). Dar kapsamlı yeniden talep bekleniyor.",
         kaynak_belge="", kaynak_konum="HMK m. 219", onaylayan="Hukuk · Erhan T."),
    dict(sira="3", tur="Yazılı soru", durum="Bekliyor",
         metin="Sözleşme kapsamında kaç sevkiyat gecikmiştir ve her birinin süresi nedir?",
         cevap="", kaynak_belge="sevkiyat-kayitlari.xlsx", kaynak_konum="Sayfa 2"),
    dict(sira="4", tur="Bilirkişi sorusu", durum="Bekliyor",
         metin="Ticariteamüllere uygunluk bakımından sevkiyat standartları hangi ölçütle değerlendirilmelidir?",
         cevap="", kaynak_belge="", kaynak_konum=""),
]

PATENT_KARSILASTIRMA = dict(
    ad="Zekai Analitik '137 — Bilyalı Vana Sızdırmazlık Grubu", muvekkil_patent="TR 2021/0137 (Müvekkil)",
    referans_patent="EP 2 845 678 B1 (Karşı patent)")

PATENT_ISTEM = [
    dict(istem_no="1[a]", unsuru="İki konumlu dinleme sensörü",
         muvekkil_metin="boru hattının birinci ve ikinci konumundan sıvı kaçak sesinin eşzamanlı dinlenmesi",
         referans_metin="boru hattının ilk konumunda yerleştirilmiş ilk mikrofon; ikinci mikrofon ikinci konumda",
         hukum="Aynı veya daha dar", kaynak_istem="EP'678 istem 1", not_metin=""),
    dict(istem_no="1[b]", unsuru="Darbe cevabının hesaplanması",
         muvekkil_metin="iki sinyal arasından düşük genlikli kanalın referans olarak alınarak sonlu bantta darbe cevabının hesaplanması",
         referans_metin="tespit edilen akustik dalgalar arasında çapraz-korelasyonun belirlenmesi",
         hukum="Daha geniş, farklı veya yok", kaynak_istem="EP'678 istem 1",
         not_metin="Referans metin hesaplama yöntemini açıkça kapsamıyor — 'farklı' yönünde, avukat nihai karar verir."),
    dict(istem_no="2", unsuru="Sonlu aralıkta ihmal edilebilir genlik",
         muvekkil_metin="kanalın alt genlikli bandının ihmal edilebilir genlik filtresinden geçirilmesi",
         referans_metin="", hukum="Daha geniş, farklı veya yok", kaynak_istem="—",
         not_metin="Referansta karşılığı bulunamadı — hücre boş bırakıldı (uydurma yok)."),
    dict(istem_no="3", unsuru="Analiz edilen aralığın otomatik belirlenmesi",
         muvekkil_metin="analiz aralığının sinyal enerjisi eşiğine göre otomatik belirlenmesi",
         referans_metin="sinyal enerjisi eşiği kullanıcı tarafından girilir", hukum="Koşullu",
         kaynak_istem="EP'678 istem 4",
         not_metin="Otomatik/kullanıcı girişli farkı 'daha dar' sayılır mı — danışma gerekli."),
]

IZLENEN_DOSYALAR = [
    dict(mahkeme="İstanbul Anadolu 9. Asliye Ticaret Mahkemesi", esas_no="E. 2024/512",
         taraflar="Zekai Holding v. Kuzey Yatırım Holding",
         son_islem="Tensip zaptı: karşı taraftan cevap dilekçesine süre verildi",
         son_islem_tarihi=GEC(12), islem_turu="Tensip", cikarilan_tarih=ILERI(9),
         tarih_durumu="Teyit bekliyor",
         tarih_alinti='"Cevap dilekçesi süresi 7 (yedi) gün olarak tayin edilmiştir." (tensip, s. 2)',
         haber_notu="", kisisel_not=""),
    dict(mahkeme="Ankara 4. İcra Mahkemesi", esas_no="E. 2025/1187",
         taraflar="Zekai Lojistik v. Marmara Gıda",
         son_islem="İtirazın iptali dilekçesi tebliğ edildi",
         son_islem_tarihi=GEC(6), islem_turu="Tebliğ", cikarilan_tarih=None,
         tarih_durumu="Metinde geçiyor",
         tarih_alinti='"...duruşma günü bildirilecektir." — celse tarihi henüz yok',
         haber_notu="Marmara Gıda'nın konkordato başvurusu haberleri var — takip değeri arttı.",
         kisisel_not="Konkordato takibinde öncelik yükselt"),
    dict(mahkeme="İzmir 2. Asliye Hukuk Mahkemesi", esas_no="E. 2023/2201",
         taraflar="Zekai Holding v. Yıldız İnşaat",
         son_islem="Bilirkişi raporu tebliğ edildi",
         son_islem_tarihi=GEC(20), islem_turu="Bilirkişi", cikarilan_tarih=ILERI(14),
         tarih_durumu="Teyit edildi",
         tarih_alinti="\"22.11.2026 tarihinde saat 10:00'da duruşma yapılarak rapor üzerinde değerlendirme yapılacaktır.\"",
         haber_notu="", kisisel_not="Rapora itiraz süresi celseye kadar"),
]

HARCAMALAR = [
    dict(buro="Karadeniz & Ortakları", dosya="Kuzey Yatırım dava", donem="2026-10",
         tutar=84500.0, butce=90000.0, durum="Onaylandı", not_metin="Bütçe içinde."),
    dict(buro="Karadeniz & Ortakları", dosya="Yıldız İnşaat bilirkişi süreci", donem="2026-10",
         tutar=121000.0, butce=75000.0, durum="Sorgulanacak",
         not_metin="Bütçeyi %61 aşıyor — bilirkişi irtibat saatleri ayrıntılı fatura istenmeli."),
    dict(buro="Ayşegül Av.", dosya="İcra itiraz dosyaları (toplu)", donem="2026-10",
         tutar=22000.0, butce=None, durum="Bekliyor", not_metin="Sabit aylık blok fatura."),
    dict(buro="Deniz Hukuk Bürosu", dosya="Veri koruma danışmanlığı", donem="2026-09",
         tutar=48000.0, butce=50000.0, durum="Onaylandı", not_metin=""),
]

UYUMLULUKLAR = [
    dict(sirket="Zekai Holding A.Ş.", yukumluluk="Olağan genel kurul toplantısı", periyot="Yıllık",
         son_tarih=ILERI(45), sorumlu="Hukuk · Erhan T.", kaynak_hukum="TTK m. 414-416",
         durum="Planlandı"),
    dict(sirket="Zekai Holding A.Ş.", yukumluluk="Finansal raporun kamuya açıklanması", periyot="Yıllık",
         son_tarih=ILERI(20), sorumlu="Finans", kaynak_hukum="TTK m. 516", durum="Planlandı"),
    dict(sirket="Zekai Yazılım Ltd.", yukumluluk="VERBİS kaydı yıllık doğrulama", periyot="Yıllık",
         son_tarih=GEC(3), sorumlu="KVKK · Selin K.", kaynak_hukum="KVKK m. 16 + yönetmelik",
         durum="Gecikti"),
    dict(sirket="Zekai Yazılım Ltd.", yukumluluk="Ara genel kurul — sermaye artırımı", periyot="Tek seferlik",
         son_tarih=ILERI(12), sorumlu="Hukuk", kaynak_hukum="TTK m. 449", durum="Planlandı"),
    dict(sirket="Zekai Holding A.Ş.", yukumluluk="İYS pazarlama kayıtları mutabakatı", periyot="Çeyreklik",
         son_tarih=ILERI(30), sorumlu="Pazarlama + Hukuk", kaynak_hukum="6563 eTic Kan.", durum="Planlandı"),
]

PORTFOY = [
    dict(musteri="Zekai Holding", konu="Tedarik sözleşmesi fesih tazminatı", mahkeme="İstanbul Anadolu 9. AST.",
         esas_no="E. 2024/512", tarafimiz="Davacı", dava_degeri=1250000.0, kazanma_olasiligi="Yüksek",
         asama="Cevap dilekçesi süresi", sonraki_adim="Karşı cevaba hazırlık + delil listesi",
         karara_baglanma=None, not_metin="İçtihat denetimi yapıldı: 4 atıf, 4 kaynak bekliyor."),
    dict(musteri="Zekai Lojistik", konu="İtirazın iptali", mahkeme="Ankara 4. İcra Hk.",
         esas_no="E. 2025/1187", tarafimiz="Davacı", dava_degeri=310000.0, kazanma_olasiligi="Orta",
         asama="Celse bekleniyor", sonraki_adim="Müvekkile konkordato riski hakkında brifing",
         karara_baglanma=None, not_metin=""),
    dict(musteri="Zekai Holding", konu="İnşaat gecikme tazminatı", mahkeme="İzmir 2. AST.",
         esas_no="E. 2023/2201", tarafimiz="Davalı", dava_degeri=890000.0, kazanma_olasiligi="Orta",
         asama="Bilirkişi raporuna itiraz", sonraki_adim="İtiraz dilekçesi (14 gün)",
         karara_baglanma=None, not_metin="Bilirkişi raporu lehte değil — kısmi itiraz stratejisi."),
]

MATRIS_SET = dict(
    ad="Çalışan rekabet yasağı (non-compete) — geçerlilik ve tazminat koşulları",
    aciklama="TR referans hücresi: TBK m. 444-445 (geçerlik: yazılı + mesleki alan/süre/yer sınırı; tazminat: son brüt ücretin en az %35'i, 2 yılı aşmayan süre). AB ülkeleri karşılaştırması — uluslararası uzaktan çalışan senaryoları için.")

MATRIS_HUCRELER = [
    dict(yargi="Türkiye", alt_soru="Geçerlik koşulu", cevap="Koşullu",
         aciklama="Yazılı; çalışanın gelecekteki gelişmesini zorlaştıran koşullar; süre/yer/mesleki alan sınırlaması işverenin makul menfaatiyle sınırlı (TBK m. 444/1-2). Sözleşme süresi 2 yılı aşamaz (TBK m. 444/3).",
         kaynak="TBK m. 444", dogrulandi=True),
    dict(yargi="Türkiye", alt_soru="Tazminat zorunlu mu", cevap="Evet",
         aciklama="Öngörülen yıllık ortalama son brüt ücretin %35'inden az olamayan tazminat zorunlu (aksine anlaşma geçersiz).",
         kaynak="TBK m. 445", dogrulandi=True),
    dict(yargi="Almanya", alt_soru="Geçerlik koşulu", cevap="Koşullu",
         aciklama="§ 74 ff. HGB: yazılı; menfaat dengesi; süre en fazla 2 yıl; ücret tabanının %50'si karşılığı tazminat (Nachzahlung) istisnaları dışında zorunlu.",
         kaynak="HGB § 74a", dogrulandi=True),
    dict(yargi="Almanya", alt_soru="Tazminat zorunlu mu", cevap="Evet",
         aciklama="Yasak dönemin ücretinin en az yarısı (§ 74a(2) HGB).", kaynak="HGB § 74a", dogrulandi=True),
    dict(yargi="Hollanda", alt_soru="Geçerlik koşulu", cevap="Koşullu",
         aciklama="7:650 BW: yazılı; 12 ayı aşan kısım için işveren %50 tazminat ödemeli; ayrıca işveren tarafı 'kesin menfaat' göstermeli (3:6'a göre yargısal denetim).",
         kaynak="BW 7:650", dogrulandi=False),
    dict(yargi="Hollanda", alt_soru="Tazminat zorunlu mu", cevap="Koşullu",
         aciklama="Yalnız 12 ayı aşan kısım için zorunlu %50; ilk 12 ay için zorunluluk yok.",
         kaynak="BW 7:650(3)", dogrulandi=False),
    dict(yargi="Polonya", alt_soru="Geçerlik koşulu", cevap="Koşullu",
         aciklama="Kodeks pracy m. 101¹: yazılı + adaylık koşulları + tazminat en az %25 taban ücret; süre 2 yılla sınırlı (3 yıl danışman/bilim).",
         kaynak="KP m. 101¹", dogrulandi=False),
    dict(yargi="Polonya", alt_soru="Tazminat zorunlu mu", cevap="Evet",
         aciklama="En az %25 taban ücret (m. 101¹ § 3).", kaynak="KP m. 101¹", dogrulandi=False),
    dict(yargi="İrlanda", alt_soru="Geçerlik koşulu", cevap="Belirsiz",
         aciklama="Tekdüze yasa yok — hukuka aykırılık (restraint of trade) ortak hukuk testi: makul menfaat + kamu yarısı. Ayırma sözleşmesindeki ödeme pratikte belirleyici.",
         kaynak="Common law (Muckleston v. Brownworth hattı)", dogrulandi=False),
    dict(yargi="İrlanda", alt_soru="Tazminat zorunlu mu", cevap="Hayır",
         aciklama="Yasal zorunluluk yok; tazminat ancak sözleşmeyle kararlaştırılır.", kaynak="—", dogrulandi=False),
]
