# -*- coding: utf-8 -*-
"""
Zekai Hukuk — Claude for Legal Orijinal Zenginlikte Örnek Veri Tohumlayıcı (Seed).
Türk çiçek ve böcek temalı şirketler, gerçekçi Türk Hukuku senaryoları.
Tüm 21 modülü eksiksiz doldurur.
"""
from datetime import date, timedelta
from app.db import Oturum, Sozlesme
from app.modeller import (
    PlaybookPozisyon, SozlesmeMaddesi, Girdi, Talep,
    TabloInceleme, IncelemeSatiri, Dosya, MusteriKayit,
    Basvuru, AtifBelgesi, Atif, Olay,
    AIKullanim, AISatici, QAAlıcı, QASoru, MevzuatKayit
)

BUGUN = date.today()
def g(gun): return BUGUN - timedelta(days=gun)
def i(gun): return BUGUN + timedelta(days=gun)

def tohumla():
    with Oturum() as db:
        # 1. SOZLESMELER (İhbar Takvimi / Renewal Calendar)
        db.query(Sozlesme).delete()
        sozlesmeler = [
            Sozlesme(id=1, ad="Papatya Lojistik A.Ş. — Antrepo ve Dağıtım Çerçeve Sözleşmesi", karsi_taraf="Papatya Lojistik ve Taşımacılık A.Ş.",
                     tur="Hizmet", baslangic=g(330), sure_ay=12, otomatik_uzatma=True, uzatma_suresi_ay=12,
                     uzatma_artis_yuzdesi=25.0, ihbar_deger=60, ihbar_birim="gün", ihbar_sekli="Noter",
                     fiyat_yillik=45000000.0, para_birimi="TL", sahibi="Av. Selin Karaca", inceleme=False, cikarim_yontemi="claude"),
            Sozlesme(id=2, ad="Nilüfer Gayrimenkul — Genel Merkez Ofis Kira Sözleşmesi", karsi_taraf="Nilüfer Gayrimenkul Yatırım A.Ş.",
                     tur="Kira", baslangic=g(360), sure_ay=12, otomatik_uzatma=True, uzatma_suresi_ay=12,
                     uzatma_artis_yuzdesi=65.0, ihbar_deger=15, ihbar_birim="gün", ihbar_sekli="Noter",
                     fiyat_yillik=18500000.0, para_birimi="TL", sahibi="Av. Selin Karaca", inceleme=True, cikarim_yontemi="claude"),
            Sozlesme(id=3, ad="Kardelen Tesis Hizmetleri — Genel Alan Temizlik ve Destek", karsi_taraf="Kardelen Tesis Yönetimi Ltd. Şti.",
                     tur="Hizmet", baslangic=g(180), sure_ay=12, otomatik_uzatma=False,
                     ihbar_deger=30, ihbar_birim="gün", ihbar_sekli="Yazılı",
                     fiyat_yillik=6200000.0, para_birimi="TL", sahibi="Av. Erhan Taşçı", inceleme=False, cikarim_yontemi="claude"),
            Sozlesme(id=4, ad="Erguvan Bulut Bilişim — ERP Yazılım Aboneliği", karsi_taraf="Erguvan Bilişim ve Yazılım A.Ş.",
                     tur="Lisans", baslangic=g(270), sure_ay=24, otomatik_uzatma=True, uzatma_suresi_ay=12,
                     ihbar_deger=90, ihbar_birim="gün", ihbar_sekli="KEP",
                     fiyat_yillik=12400000.0, para_birimi="TL", sahibi="Av. Selin Karaca", inceleme=True, cikarim_yontemi="claude"),
            Sozlesme(id=5, ad="Begonvil Dağıtım — Bölge Bayilik ve Satış Sözleşmesi", karsi_taraf="Begonvil Tüketim Malları San. Tic. Ltd.",
                     tur="Bayilik", baslangic=g(300), sure_ay=12, otomatik_uzatma=True, uzatma_suresi_ay=12,
                     ihbar_deger=45, ihbar_birim="gün", ihbar_sekli="Noter",
                     fiyat_yillik=85000000.0, para_birimi="TL", sahibi="Av. Erhan Taşçı", inceleme=False, cikarim_yontemi="claude"),
            Sozlesme(id=6, ad="Manolya Teknoloji — Veri Analitiği Çerçeve Sözleşmesi", karsi_taraf="Manolya Teknoloji ve Danışmanlık A.Ş.",
                     tur="Hizmet", baslangic=g(90), sure_ay=12, otomatik_uzatma=False,
                     ihbar_deger=30, ihbar_birim="gün", ihbar_sekli="Yazılı",
                     fiyat_yillik=3800000.0, para_birimi="TL", sahibi="Av. Selin Karaca", inceleme=False, cikarim_yontemi="claude")
        ]
        db.add_all(sozlesmeler)

        # 2. SÖZLEŞME İNCELEME TABLOSU (Tabular Review - 8 Zengin Sözleşme)
        db.query(TabloInceleme).delete()
        db.query(IncelemeSatiri).delete()
        inc = TabloInceleme(id=1, ad="Papatya & Nilüfer Holding — Portföy Sözleşme İncelemesi 2026")
        db.add(inc)

        satirlar = [
            IncelemeSatiri(
                inceleme_id=1, belge_adi="01 Papatya Döküm Sanayi A.Ş. — Mal Tedarik Sözleşmesi",
                karsi_taraf="Papatya Döküm Sanayi ve Ticaret A.Ş.", sozlesme_turu="Sanayi vanaları ve döküm parça tedariki",
                yururluk="01.04.2023", bitis_sure="31.03.2028 (5 Yıl, 60 gün ihbarla 1'er yıl uzar)",
                otomatik_uzatma="Evet", taban_hukuk="Türk Hukuku (İstanbul Çağlayan)",
                sorumluluk_tavani="₺45.000.000 (Yıllık sözleşme bedeli tavanı)",
                mali_yukumluluk="₺120.000.000 asgari yıllık alım taahhüdü",
                notlar="Cezai şart bedelin %10'u ile sınırlandırılmıştır. Şirket hisse devrinde 30 gün önceden bildirim zorunludur.",
                ciddi_konu=False, inceleme_gerekli=False, sahibi="Av. Selin Karaca"
            ),
            IncelemeSatiri(
                inceleme_id=1, belge_adi="02 Nilüfer Bilişim Ltd. Şti. — Tek Yetkili Dağıtım Sözleşmesi",
                karsi_taraf="Nilüfer Teknoloji ve Bilişim Çözümleri Ltd. Şti.", sozlesme_turu="Yazılım ürünleri tek yetkili distribütörlük",
                yururluk="15.06.2023", bitis_sure="15.06.2026 (3 Yıl süreli, süre sonunda kendiliğinden biter)",
                otomatik_uzatma="Hayır", taban_hukuk="Türk Hukuku (ISTAC İstanbul Tahkimi)",
                sorumluluk_tavani="Son 12 ayda tahsil edilen distribütörlük bedeli (TBK m. 115)",
                mali_yukumluluk="₺18.500.000 yıllık ciro kotası",
                notlar="ISTAC Tahkim şartı taraflarca karşılıklı kabul edilmiştir. Rakip ürün satma yasağı 2 yıl sürelidir.",
                ciddi_konu=False, inceleme_gerekli=False, sahibi="Av. Erhan Taşçı"
            ),
            IncelemeSatiri(
                inceleme_id=1, belge_adi="03 Kardelen Katılım Bankası — Çerçeve Kredi Finansman Sözleşmesi",
                karsi_taraf="Kardelen Katılım ve Yatırım Bankası A.Ş.", sozlesme_turu="Genel kredi ve teminat sözleşmesi",
                yururluk="30.09.2023", bitis_sure="30.09.2028 (5 Yıl vadeli)",
                otomatik_uzatma="Hayır", taban_hukuk="Türk Hukuku (İstanbul Mahkemeleri ve İcra Daireleri)",
                sorumluluk_tavani="Kredi ana para, faiz ve masraflar toplamı ile sınırlıdır",
                mali_yukumluluk="₺85.000.000 nakdi ve gayrinakdi kredi limiti",
                notlar="Kredi borçlusunun hisse ve ortaklık yapısındaki değişiklikler bankanın ön iznine tabidir; izinsiz devirde kredi muaccel kılınabilir.",
                ciddi_konu=True, inceleme_gerekli=True, sahibi="Av. Selin Karaca"
            ),
            IncelemeSatiri(
                inceleme_id=1, belge_adi="04 Erguvan Kimya Sanayi — Depo ve Tesis Kira Sözleşmesi",
                karsi_taraf="Erguvan Kimya Sanayi ve Depolama A.Ş.", sozlesme_turu="Çatılı işyeri kira sözleşmesi (TBK m. 339 vd.)",
                yururluk="01.01.2024", bitis_sure="01.01.2029 (5 Yıl süreli, kiracı feshetmedikçe 1'er yıl uzar)",
                otomatik_uzatma="Evet", taban_hukuk="Türk Hukuku (Kocaeli Gebze Sulh Hukuk)",
                sorumluluk_tavani="Kira bedeli ve teminat mektubu tutarı (3 aylık kira)",
                mali_yukumluluk="₺14.400.000 yıllık kira bedeli (TÜFE artışlı)",
                notlar="Kiraya verenin yazılı rızası olmadan alt kira ve kira devri yapılamaz. Çevre ve atık izinleri kiracıya aittir.",
                ciddi_konu=False, inceleme_gerekli=False, sahibi="Av. Erhan Taşçı"
            ),
            IncelemeSatiri(
                inceleme_id=1, belge_adi="05 Zambak İlaç ve Sağlık A.Ş. — Ar-Ge Lisans ve Patent Sözleşmesi",
                karsi_taraf="Zambak İlaç ve Biyoteknoloji San. Tic. A.Ş.", sozlesme_turu="Patent lisansı ve Ar-Ge ortaklığı",
                yururluk="10.02.2024", bitis_sure="10.02.2031 (7 Yıl süreli)",
                otomatik_uzatma="Hayır", taban_hukuk="Türk Hukuku (İstanbul Fikri ve Sınai Haklar Mahkemesi)",
                sorumluluk_tavani="₺60.000.000 toplam lisans bedeli tavanı",
                mali_yukumluluk="₺12.000.000 peşin lisans + %4 royalti bedeli",
                notlar="SMK uyarınca patent ihlal iddialarında savunma ve tazmin yükümlülüğü lisans verene aittir.",
                ciddi_konu=False, inceleme_gerekli=False, sahibi="Av. Selin Karaca"
            ),
            IncelemeSatiri(
                inceleme_id=1, belge_adi="06 Manolya Bulut Sistemleri — Kurumsal Bulut Hizmet Sözleşmesi (SLA)",
                karsi_taraf="Manolya Bulut Teknolojileri A.Ş.", sozlesme_turu="SaaS ve Bulut Altyapı Barındırma",
                yururluk="01.03.2024", bitis_sure="01.03.2027 (3 Yıl süreli, 30 gün ihbarla uzar)",
                otomatik_uzatma="Evet", taban_hukuk="Türk Hukuku (Ankara Mahkemeleri)",
                sorumluluk_tavani="Son 6 ayda ödenen abonelik ücreti ile sınırlıdır (Riskli)",
                mali_yukumluluk="₺5.400.000 yıllık lisans ve barındırma bedeli",
                notlar="%99.9 çalışma süresi (uptime) taahhüdü vardır. Veri ihlali sorumluluğunun 6 aylık ücretle sınırlandırılması risklidir.",
                ciddi_konu=True, inceleme_gerekli=True, sahibi="Av. Selin Karaca"
            ),
            IncelemeSatiri(
                inceleme_id=1, belge_adi="07 Begonvil Uluslararası Lojistik — Karayolu Taşıma Çerçeve Sözleşmesi",
                karsi_taraf="Begonvil Uluslararası Taşımacılık Ltd. Şti.", sozlesme_turu="Karayolu yük taşıma ve lojistik",
                yururluk="15.04.2024", bitis_sure="15.04.2026 (2 Yıl süreli)",
                otomatik_uzatma="Evet", taban_hukuk="Türk Ticaret Kanunu (TTK Taşıma Hükümleri / CMR)",
                sorumluluk_tavani="TTK m. 882 ve CMR Konvansiyonu özel çekme hakkı (SDR) limitleri",
                mali_yukumluluk="Taşıma başına navlun tarifesi",
                notlar="Emtiada meydana gelebilecek hasar ve ziya hallerinde 8 gün içinde yazılı ihbar zorunluluğu vardır.",
                ciddi_konu=False, inceleme_gerekli=False, sahibi="Av. Erhan Taşçı"
            ),
            IncelemeSatiri(
                inceleme_id=1, belge_adi="08 Çiğdem Perakende ve Mağazacılık — AVM Mağaza Kira Sözleşmesi",
                karsi_taraf="Çiğdem AVM ve Gayrimenkul Yönetim A.Ş.", sozlesme_turu="AVM Mağaza Kira Sözleşmesi",
                yururluk="01.05.2024", bitis_sure="01.05.2034 (10 Yıl süreli)",
                otomatik_uzatma="Hayır", taban_hukuk="Türk Hukuku (İstanbul Anadolu Mahkemeleri)",
                sorumluluk_tavani="6 Aylık kira bedeli ve banka teminat mektubu",
                mali_yukumluluk="₺24.000.000 yıllık asgari kira + %8 ciro kirası",
                notlar="Erken tahliye halinde kalan sürenin kira bedellerinin muaccel olacağına ilişkin cezai şart hükmü mevcuttur (İnceleme bekliyor).",
                ciddi_konu=True, inceleme_gerekli=True, sahibi="Av. Selin Karaca"
            )
        ]
        db.add_all(satirlar)

        # 3. HUKUK MASASI (Ask Legal - 8 Zengin Talep & 2 Hukuki Görüş)
        db.query(Girdi).delete()
        db.query(Talep).delete()
        girdiler = [
            Girdi(baslik="Sözleşmelerde sorumluluk tavanı ve KVKK sınırları", kategori="Sözleşmeler", sahip="Hukuk Müşavirliği",
                  onay_durumu="Onaylı", onay_tarihi=g(90), gecerlilik_tarihi=i(270),
                  anahtar_kelimeler="sorumluluk tavanı, tazminat, KVKK, TBK 115",
                  metin="Standart sözleşmelerimizde sorumluluk tavanı yıllık sözleşme bedelinin en az %100'ü olmalıdır. KVKK veri ihlalleri, fikri mülkiyet ve ağır kusur halleri tavana dahil edilemez."),
            Girdi(baslik="Satınalma sözleşmelerinde ödeme vadesi ve faiz", kategori="Satınalma", sahip="Hukuk Müşavirliği",
                  onay_durumu="Onaylı", onay_tarihi=g(60), gecerlilik_tarihi=i(120),
                  anahtar_kelimeler="ödeme, vade, temerrüt faizi, fatura",
                  metin="Standart ödeme vademiz 60 gündür; satınalma birimi müzakere ile 45 güne kadar onay verebilir. 30 günden kısa vadeler Finans ve Hukuk onayı gerektirir.")
        ]
        db.add_all(girdiler)

        talepler = [
            Talep(
                baslik="Papatya Lojistik veri analitiği araçları kullanım sözleşmesi incelemesi",
                soran_ad="Deniz Akarsu", bolum="Tedarik & Satınalma", kategori="Sözleşme İncelemesi",
                metin="Papatya Lojistik A.Ş. şirket içi kullanım analitiği aracına ilişkin hizmet sözleşmesini iletti. Sorumluluk sınırı çok dar ve verilerin yurt dışına aktarımı söz konusu. Risk yüksek midir?",
                risk="Yüksek", uzmanlik="Bilişim ve Ticaret Hukuku", atanan="Av. Selin Karaca",
                durum="Bilgi bekliyor", olusturma=g(8), gerek_tarih=g(5),
                taslak="Sayın İlgili,\n\nİncelenen sözleşmede verilerin yurt dışı sunucularda işlenmesi öngörülmekte olup KVKK m. 9 uyarınca açık rıza veya bağlayıcı şirket kuralları aranmaktadır. Ayrıca sorumluluk tavanı şirketimiz zararlarını karşılamaktan uzaktır. Revize maddeler hazırlanmıştır.\n\nBilgilerinize sunarız.\nHukuk Müşavirliği",
                taslak_turu="Zekai Hukuki Görüş Taslağı", gonderen_kimlikle="Kıdemli Ticaret Hukuku Müşaviri"
            ),
            Talep(
                baslik="Müşteri satınalma ekibi sipariş formumuzda tek taraflı değişiklik yaptı",
                soran_ad="Kemal Soylu", bolum="Satış & Pazarlama", kategori="Ticari Satım",
                metin="Kurumsal müşterimiz onayladığımız sipariş formunu geri gönderdi ancak cezai şart oranını %20'ye çıkarmış ve vadeyi 90 güne çekmiş. Bu haliyle kabul edebilir miyiz?",
                risk="Orta", uzmanlik="Borçlar Hukuku", atanan="Av. Erhan Taşçı",
                durum="Yeni", olusturma=g(11), gerek_tarih=g(9),
                taslak="Sayın İlgili,\n\nSipariş formundaki tek taraflı değişiklikler TBK m. 4 uyarınca yeni bir icap (teklif) niteliğindedir. %20 cezai şart fahiş olup şirketimizin standart %5 tavanı ile 45 gün vadesinin karşı teklif olarak sunulması tavsiye olunur.\n\nBilgilerinize sunarız.\nHukuk Müşavirliği",
                taslak_turu="Zekai Hukuki Görüş Taslağı", gonderen_kimlikle="Hukuk Müşaviri"
            ),
            Talep(
                baslik="Yetkili satıcı/bayi bilgi paylaşımından önce kendi tek taraflı NDA'sını dayatıyor",
                soran_ad="Barış Çetinel", bolum="İş Geliştirme", kategori="Gizlilik Sözleşmesi (NDA)",
                metin="Yeni bölge bayimiz olacak firma ticari sırları paylaşmadan önce kendi hazırladığı tek taraflı 1.000.000 TL cezai şartlı NDA'yı imzalamamızı şart koşuyor. İmzalayalım mı?",
                risk="Orta", uzmanlik="Sözleşmeler Hukuku", atanan="Av. Selin Karaca",
                durum="Taslak hazır", olusturma=g(4), gerek_tarih=g(3),
                taslak="Sayın İlgili,\n\nŞirket politikamız gereği tek taraflı cezai şart içeren gizlilik taahhütnameleri kabul edilemez. Karşı tarafa ekte sunduğumuz karşılıklı (mütekabil) ve doğrudan kanıtlanabilir zararlara dayalı kurumsal Gizlilik Sözleşmesi taslağımızın iletilmesi gerekmektedir.\n\nBilgilerinize sunarız.\nHukuk Müşavirliği",
                taslak_turu="Zekai Hukuki Görüş Taslağı", gonderen_kimlikle="Hukuk Müşaviri"
            ),
            Talep(
                baslik="Pazarlama ekibi reklamda 'Pazar liderinden iki kat hızlıyız' iddiasını kullanmak istiyor",
                soran_ad="Taner Nazlı", bolum="Pazarlama & İletişim", kategori="Reklam ve Haksız Rekabet",
                metin="Yeni ürün lansmanında televizyon ve sosyal medya reklamlarımızda 'Sektör lideri rakibimizden 2 kat daha hızlı teslimat' sloganını kullanacağız. Hukuki risk nedir?",
                risk="Acil", uzmanlik="TTK Haksız Rekabet & Reklam Kurulu", atanan="Av. Selin Karaca",
                durum="Yeni", olusturma=g(3), gerek_tarih=g(2),
                taslak="Sayın İlgili,\n\nTicari Reklam ve Haksız Ticari Uygulamalar Yönetmeliği m. 8 uyarınca karşılaştırmalı reklamlarda yer alan iddiaların bağımsız üniversite veya akredite test laboratuvarı raporlarıyla ispatlanması zorunludur. Aksi halde Reklam Kurulu durdurma ve idari para cezası uygulayacaktır.\n\nBilgilerinize sunarız.\nHukuk Müşavirliği",
                taslak_turu="Zekai Hukuki Görüş Taslağı", gonderen_kimlikle="Hukuk Müşaviri"
            ),
            Talep(
                baslik="İmza yetkilimiz izindeyken banka yeni hesap açılışı için imza sirküleri istiyor",
                soran_ad="Cem Önal", bolum="Finans & Hazine", kategori="Şirketler Hukuku",
                metin="A Grubu imza yetkilimiz yurt dışında ve acil kredi hesabı açılması gerekiyor. B Grubu yetkililerimiz münferiden imzalayabilir mi?",
                risk="Acil", uzmanlik="TTK Temsil ve İltizam", atanan="Av. Erhan Taşçı",
                durum="Yeni", olusturma=g(2), gerek_tarih=g(2),
                taslak="Sayın İlgili,\n\nŞirketimizin Ticaret Sicil Gazetesi'nde ilan edilen güncel imza sirküleri uyarınca; 500.000 TL üzerindeki bankacılık ve kredi işlemlerinde en az bir A Grubu yetkili ile bir B Grubu yetkilinin müşterek imzası zorunludur. B Grubu tek başına işlem yapamaz. Noter onaylı özel vekaletname temin edilmelidir.\n\nBilgilerinize sunarız.\nHukuk Müşavirliği",
                taslak_turu="Zekai Hukuki Görüş Taslağı", gonderen_kimlikle="Hukuk Müşaviri"
            ),
            Talep(
                baslik="Yazılım ekibinden kilit bir personelin rakip şirkete geçmek üzere istifası",
                soran_ad="Hassas Başvuru", bolum="İnsan Kaynakları", kategori="İş Hukuku & Rekabet Yasağı",
                metin="Kıdemli yapay zeka mühendisimiz aynı sektördeki doğrudan rakibimize geçmek üzere istifa etti. İş sözleşmesindeki 1 yıllık rekabet yasağı ve cezai şartı işletebilir miyiz?",
                risk="Hassas", uzmanlik="İş Hukuku (TBK m. 444-447)", atanan="Av. Selin Karaca",
                durum="Bilgi bekliyor", olusturma=g(6), gerek_tarih=g(5),
                taslak="Sayın İlgili,\n\nTBK m. 444 uyarınca rekabet yasağının geçerli olabilmesi için personelin müşteri çevresine veya üretim/ticari sırlarına nüfuz etmiş olması ve işverenin bu yüzden önemli bir zarara uğrama ihtimalinin bulunması şarttır. Coğrafi alan Türkiye geneli olarak yazılmışsa Yargıtay bunu aşırı bularak iptal edebilmektedir. Personelin eriştiği kod ve müşteri listeleri derhal tutanak altına alınmalıdır.\n\nBilgilerinize sunarız.\nHukuk Müşavirliği",
                taslak_turu="Zekai Hukuki Görüş Taslağı", gonderen_kimlikle="Kıdemli İş Hukuku Müşaviri"
            ),
            Talep(
                baslik="Tedarikçi sözleşmesinde döviz kuru artışı gerekçesiyle TBK m. 138 uyarlama talebi",
                soran_ad="Kemal Demir", bolum="Satınalma", kategori="Borçlar Hukuku",
                metin="Erguvan Kimya ham madde sözleşmesinde döviz artışını gerekçe göstererek birim fiyatlara %40 zam talep ediyor ve aksi halde sevkiyatı durduracağını ihtar etti. Ne yapmalıyız?",
                risk="Yüksek", uzmanlik="Borçlar Hukuku (Uyarlama Davası)", atanan="Av. Erhan Taşçı",
                durum="Taslak hazır", olusturma=g(3), gerek_tarih=i(2),
                taslak="Sayın İlgili,\n\nTacirler arasında basiretli iş adamı gibi davranma yükümlülüğü (TTK m. 18/2) uyarınca kur dalgalanmaları kural olarak tek başına sözleşmeyi askıya alma hakkı vermez. Sevkiyatın durdurulması temerrüt oluşturur. Karşı tarafa TBK m. 123 uyarınca aynen ifa ve gecikme cezası ihtarnamesi keşide edilmelidir.\n\nBilgilerinize sunarız.\nHukuk Müşavirliği",
                taslak_turu="Zekai Hukuki Görüş Taslağı", gonderen_kimlikle="Hukuk Müşaviri"
            ),
            Talep(
                baslik="KVKK kapsamında eski bir çalışandan gelen kişisel verilerin silinmesi başvurusu",
                soran_ad="Merve Aydın", bolum="İnsan Kaynakları", kategori="Kişisel Verilerin Korunması (KVKK)",
                metin="3 yıl önce ayrılan eski çalışanımız KVKK m. 11 kapsamında şirketimizdeki tüm özlük dosyası, performans değerlendirmeleri ve e-posta kayıtlarının imha edilmesini talep ediyor. Hangi verileri saklamak zorundayız?",
                risk="Orta", uzmanlik="KVKK ve İş Hukuku", atanan="Av. Selin Karaca",
                durum="Taslak hazır", olusturma=g(5), gerek_tarih=i(4),
                taslak="Sayın İlgili,\n\nİş Kanunu ve SGK mevzuatı uyarınca özlük dosyası ve bordro kayıtları 10 yıllık zamanaşımı süresi boyunca saklanmak zorundadır (TBK m. 146). Çalışana kanuni saklama yükümlülüğü gerekçe gösterilerek kısmi ret cevabı verilmeli; zorunlu olmayan pazarlama ve genel kayıtlar imha edilmelidir. 30 günlük yasal cevap süresine dikkat edilmelidir.\n\nBilgilerinize sunarız.\nHukuk Müşavirliği",
                taslak_turu="Zekai Hukuki Görüş Taslağı", gonderen_kimlikle="Hukuk Müşaviri"
            )
        ]
        db.add_all(talepler)

        # 4. SÖZLEŞME MÜZAKERE REHBERİ (Playbook - 7 Pozisyon & 8 Sözleşme x Maddeleri)
        db.query(PlaybookPozisyon).delete()
        db.query(SozlesmeMaddesi).delete()

        pozisyonlar = [
            PlaybookPozisyon(id=1, madde_adi="Sorumluluk sınırı",
                             standart_metin="Tedarikçinin toplam sorumluluğu her sözleşme yılında ödenen bedellerin en az %150'siyle sınırlıdır; gizlilik ve KVKK sınır dışıdır.",
                             fallback_metin="Tavan %100'e düşürülebilir; veri ihlali sorumluluğu yıllık ücretin en az 2 katı olmalıdır.",
                             kirmizi_cizgi="Tavan 12 aylık sözleşme bedelinin altındaysa kabul edilemez."),
            PlaybookPozisyon(id=2, madde_adi="Uygulanacak hukuk ve yetki",
                             standart_metin="Türk hukuku uygulanır; İstanbul (Çağlayan) Mahkemeleri ve İcra Daireleri münhasıran yetkilidir.",
                             fallback_metin="ISTAC (İstanbul Tahkim Merkezi) tahkimi kabul edilebilir.",
                             kirmizi_cizgi="Yabancı ülke mahkemelerinin münhasır yetkisi kabul edilemez."),
            PlaybookPozisyon(id=3, madde_adi="Kişisel verilerin işlenmesi (KVKK)",
                             standart_metin="Tedarikçi kişisel verileri yalnız şirketimizin yazılı talimatı doğrultusunda işler; yapay zeka model eğitimi kesinlikle yasaktır.",
                             fallback_metin="Model eğitimi yapılmaması ve verilerin Türkiye'de kalması şartıyla standart DPA onaylanabilir.",
                             kirmizi_cizgi="Verimizin yapay zeka eğitiminde kullanılması kesinlikle kabul edilemez."),
            PlaybookPozisyon(id=4, madde_adi="Ödeme ve gecikme faizi",
                             standart_metin="Hakediş ve faturalar tebliğden itibaren 60 gün içinde ödenir; yasal temerrüt faizi uygulanır.",
                             fallback_metin="45 gün ödeme vadesi + ticari temerrüt faizi müzakere edilebilir.",
                             kirmizi_cizgi="15 günden kısa ödeme vadesi ve fahiş gecikme cezaları kabul edilemez."),
            PlaybookPozisyon(id=5, madde_adi="Sözleşmenin devri",
                             standart_metin="Taraflar, karşı tarafın önceden yazılı iznini almadan sözleşmeyi üçüncü kişilere devredemez.",
                             fallback_metin="Aynı şirketler topluluğu bünyesindeki grup içi devirlere izin verilebilir.",
                             kirmizi_cizgi="Kontrolümüz dışındaki üçüncü şahıslara serbest devir yetkisi kabul edilemez."),
            PlaybookPozisyon(id=6, madde_adi="Cezai Şart & Gecikme Kesintisi",
                             standart_metin="Günlük gecikme cezası azami %0,05 ve toplam sözleşme bedelinin %10'u ile sınırlıdır.",
                             fallback_metin="Toplam bedelin %15'ine kadar kabul edilebilir; kusur ve yazılı ihtar şartı aranır.",
                             kirmizi_cizgi="Sınırsız cezai şart veya peşin kesinti kabul edilemez."),
            PlaybookPozisyon(id=7, madde_adi="Fesih ve Düzeltme Süresi",
                             standart_metin="Haklı nedenle fesihten önce en az 15 günlük yazılı ihlal giderme mehil süresi verilir.",
                             fallback_metin="10 güne kadar müzakere edilebilir.",
                             kirmizi_cizgi="Derhal ve tazminatsız tek taraflı keyfi fesih kabul edilemez.")
        ]
        db.add_all(pozisyonlar)

        # 8 Sözleşme x Playbook Maddeleri
        sozlesme_adlari = [
            ("Papatya Lojistik A.Ş.", "Papatya Lojistik ve Taşımacılık A.Ş."),
            ("Nilüfer Teknoloji A.Ş.", "Nilüfer Teknoloji Çözümleri A.Ş."),
            ("Erguvan Kimya Sanayi A.Ş.", "Erguvan Kimya San. Tic. A.Ş."),
            ("Kardelen Madencilik A.Ş.", "Kardelen Madencilik Sanayi A.Ş."),
            ("Zambak İlaç ve Biyoteknoloji A.Ş.", "Zambak İlaç San. A.Ş."),
            ("Begonvil Dağıtım Ltd. Şti.", "Begonvil Tüketim Malları Ltd. Şti."),
            ("Manolya Perakende A.Ş.", "Manolya Perakende ve Mağazacılık A.Ş."),
            ("Açelya Enerji ve Altyapı A.Ş.", "Açelya Enerji Yatırımları A.Ş.")
        ]

        maddeler_data = []
        for s_ad, kt in sozlesme_adlari:
            # Sorumluluk
            durum_s = "Standart" if "Papatya" in s_ad or "Begonvil" in s_ad else ("Sapma" if "Nilüfer" in s_ad or "Manolya" in s_ad else "Fallback 1")
            karar_s = "Onaylandı" if durum_s == "Fallback 1" else ("" if durum_s == "Sapma" else "")
            maddeler_data.append(SozlesmeMaddesi(
                sozlesme_adi=s_ad, karsi_taraf=kt, biz_kimiz="Müşteri", kagit_kimi="Bizim", madde_adi="Sorumluluk sınırı",
                durum=durum_s, sozlesme_alinti="Toplam tazminat sorumluluğu sözleşme bedelinin %150'si ile sınırlıdır.",
                madde_no="14.1", sayfa="7", karar=karar_s, dosya_adi=f"{s_ad.lower().replace(' ', '-')}.pdf"
            ))
            # Hukuk
            durum_h = "Kabul edilemez" if "Kardelen" in s_ad else ("Fallback 1" if "Nilüfer" in s_ad or "Açelya" in s_ad else "Standart")
            karar_h = "Onaylandı" if durum_h == "Fallback 1" else ""
            maddeler_data.append(SozlesmeMaddesi(
                sozlesme_adi=s_ad, karsi_taraf=kt, biz_kimiz="Müşteri", kagit_kimi="Onların", madde_adi="Uygulanacak hukuk ve yetki",
                durum=durum_h, sozlesme_alinti="Uyuşmazlıklarda İngiliz Hukuku uygulanır ve Londra Mahkemeleri yetkilidir." if durum_h == "Kabul edilemez" else "Türk Hukuku ve ISTAC Tahkimi yetkilidir.",
                madde_no="22.1", sayfa="12", karar=karar_h, dosya_adi=f"{s_ad.lower().replace(' ', '-')}.pdf"
            ))
            # KVKK
            durum_k = "Kabul edilemez" if "Nilüfer" in s_ad or "Manolya" in s_ad else "Standart"
            maddeler_data.append(SozlesmeMaddesi(
                sozlesme_adi=s_ad, karsi_taraf=kt, biz_kimiz="Müşteri", kagit_kimi="Onların", madde_adi="Kişisel verilerin işlenmesi (KVKK)",
                durum=durum_k, sozlesme_alinti="Tedarikçi sistemdeki verileri yapay zeka modellerini eğitmek amacıyla kullanabilir." if durum_k == "Kabul edilemez" else "Veriler münhasıran sözleşme amacıyla işlenir.",
                madde_no="8.4", sayfa="5", karar="", dosya_adi=f"{s_ad.lower().replace(' ', '-')}.pdf"
            ))
            # Ödeme
            durum_o = "Sapma" if "Erguvan" in s_ad else "Standart"
            maddeler_data.append(SozlesmeMaddesi(
                sozlesme_adi=s_ad, karsi_taraf=kt, biz_kimiz="Müşteri", kagit_kimi="Bizim", madde_adi="Ödeme ve gecikme faizi",
                durum=durum_o, sozlesme_alinti="Faturalar tebliğden itibaren 30 gün içinde ödenir, aylık %5 gecikme faizi işletilir.",
                madde_no="6.2", sayfa="4", karar="Editör kabul etti" if durum_o == "Sapma" else "", dosya_adi=f"{s_ad.lower().replace(' ', '-')}.pdf"
            ))
            # Cezai Şart
            durum_c = "Sapma" if "Zambak" in s_ad or "Açelya" in s_ad else ("Eksik" if "Kardelen" in s_ad else "Standart")
            maddeler_data.append(SozlesmeMaddesi(
                sozlesme_adi=s_ad, karsi_taraf=kt, biz_kimiz="Müşteri", kagit_kimi="Onların", madde_adi="Cezai Şart & Gecikme Kesintisi",
                durum=durum_c, sozlesme_alinti="Her günlük gecikme için sözleşme bedelinin %0,5'i oranında sınırsız cezai şart kesilir." if durum_c == "Sapma" else "Günlük %0,05 ve toplam bedelin %10'u sınırlı ceza.",
                madde_no="11.3", sayfa="9", karar="", dosya_adi=f"{s_ad.lower().replace(' ', '-')}.pdf"
            ))
            # Fesih
            durum_f = "Fallback 1" if "Manolya" in s_ad or "Begonvil" in s_ad else "Standart"
            maddeler_data.append(SozlesmeMaddesi(
                sozlesme_adi=s_ad, karsi_taraf=kt, biz_kimiz="Müşteri", kagit_kimi="Bizim", madde_adi="Fesih ve Düzeltme Süresi",
                durum=durum_f, sozlesme_alinti="Taraflar 10 günlük yazılı ihtarla ihlalin giderilmesini talep eder.",
                madde_no="18.1", sayfa="11", karar="Onaylandı" if durum_f == "Fallback 1" else "", dosya_adi=f"{s_ad.lower().replace(' ', '-')}.pdf"
            ))

        db.add_all(maddeler_data)

        # 5. DAVA VE TAKİP DOSYALARI (Matter Board - 8 Dava Dosyası)
        db.query(Dosya).delete()
        dava_dosyalari = [
            Dosya(id=1, ad="Papatya Lojistik v. Nilüfer Teknoloji (Tazminat Davası)", musteri="Papatya Lojistik A.Ş.",
                  alan_kodu="TIC", asama="Aktif", sahibi="Av. Selin Karaca",
                  sonraki_islem="Bilirkişi raporuna itiraz dilekçesi sunulacak", sonraki_tarih=g(2),
                  ikinci_islem="Tahkikat duruşması", ikinci_tarih=i(14), inceleme=True, tarih_teyit=False),
            Dosya(id=2, ad="Kardelen Madencilik İflas Erteleme & Konkordato", musteri="Kardelen Madencilik A.Ş.",
                  alan_kodu="ICRA", asama="Yeni", sahibi="Av. Erhan Taşçı",
                  sonraki_islem="Kesin mühlet talebine karşı alacaklı beyanı", sonraki_tarih=g(5),
                  ikinci_islem="Alacaklılar kurulu toplantısı", ikinci_tarih=i(20), inceleme=True, tarih_teyit=True),
            Dosya(id=3, ad="Erguvan Kimya Çevre Para Cezası İptali", musteri="Erguvan Kimya San. A.Ş.",
                  alan_kodu="IDA", asama="Yeni", sahibi="Av. Selin Karaca",
                  sonraki_islem="Savunmaya cevap dilekçesi verilecek", sonraki_tarih=i(3),
                  ikinci_islem="Yürütmeyi durdurma kararı tebliği", ikinci_tarih=i(10), inceleme=False, tarih_teyit=False),
            Dosya(id=4, ad="Manolya Perakende AVM Mağaza Kira Tahliyesi", musteri="Manolya Perakende A.Ş.",
                  alan_kodu="BOR", asama="Aktif", sahibi="Av. Erhan Taşçı",
                  sonraki_islem="Ön inceleme duruşması ve tanık listesi", sonraki_tarih=i(7),
                  ikinci_islem="Sulh müzakeresi", ikinci_tarih=i(18), inceleme=False, tarih_teyit=False),
            Dosya(id=5, ad="Begonvil Dağıtım Haksız Rekabet & Tedbir İstemi", musteri="Begonvil Tüketim Ltd.",
                  alan_kodu="TIC", asama="Başkalarını bekliyor", sahibi="Av. Selin Karaca",
                  sonraki_islem="Karar duruşması ve son beyan", sonraki_tarih=i(14),
                  ikinci_islem="İstinaf süresi takibi", ikinci_tarih=i(40), inceleme=False, tarih_teyit=False),
            Dosya(id=6, ad="Zambak İlaç Patent Hükümsüzlüğü Davası", musteri="Zambak İlaç A.Ş.",
                  alan_kodu="TIC", asama="Aktif", sahibi="Av. Selin Karaca",
                  sonraki_islem="TÜBİTAK uzman heyet raporu incelemesi", sonraki_tarih=i(18),
                  ikinci_islem="Bilirkişi ek rapor talebi", ikinci_tarih=i(35), inceleme=True, tarih_teyit=False),
            Dosya(id=7, ad="Açelya Enerji EPDK İdari Yaptırım Kararı İptali", musteri="Açelya Enerji A.Ş.",
                  alan_kodu="IDA", asama="Başkalarını bekliyor", sahibi="Av. Erhan Taşçı",
                  sonraki_islem="Temyiz duruşması mazeret ve beyan", sonraki_tarih=i(24),
                  ikinci_islem="Danıştay ilamı tebliği", ikinci_tarih=i(50), inceleme=False, tarih_teyit=True),
            Dosya(id=8, ad="Defne Lojistik İcra Takibi ve İtirazın İptali", musteri="Defne Lojistik Ltd.",
                  alan_kodu="ICRA", asama="Kapatıldı", sahibi="Av. Erhan Taşçı",
                  sonraki_islem="Haciz tutanağı ve tahsilat tasfiyesi", sonraki_tarih=i(30),
                  ikinci_islem="Dosya infaz kapatma", ikinci_tarih=i(35), inceleme=False, tarih_teyit=False)
        ]
        db.add_all(dava_dosyalari)

        # 6. DELİL KRONOLOJİSİ (Fact Chronology - 10 Somut Olay)
        db.query(Olay).delete()
        olaylar = [
            Olay(id=1, dosya_adi="Papatya Lojistik A.Ş. — Nilüfer Teknoloji A.Ş. Uyuşmazlığı", tarih=date(2023, 9, 15), tur="Sözleşme",
                 metin="Taraflar arasında İstanbul'da Çerçeve Lojistik ve Antrepo Hizmet Sözleşmesi akdedildi (m. 14 yetki şartı).",
                 kaynak_alinti="İşbu Çerçeve Sözleşme 15.09.2023 tarihinde İstanbul'da akdedilmiştir. (papatya-nilufer-cerceve-sozlesmesi.pdf)",
                 kaynak_dosya="D-1 Sözleşme", durum="Onaylı", cikarim_yontemi="claude"),
            Olay(id=2, dosya_adi="Papatya Lojistik A.Ş. — Nilüfer Teknoloji A.Ş. Uyuşmazlığı", tarih=date(2023, 10, 15), tur="İşlem",
                 metin="İlk parti emtianın antrepoya teslimi ve UAT kabul muayenesinin ihtirazi kayıtsız tamamlanması.",
                 kaynak_alinti="15.10.2023 tarihli Ambar Teslim ve Kabul Tutanağı: Ürünler tam ve hasarsız teslim alınmıştır.",
                 kaynak_dosya="D-2 Teslim Tutanağı", durum="Onaylı", cikarim_yontemi="claude"),
            Olay(id=3, dosya_adi="Papatya Lojistik A.Ş. — Nilüfer Teknoloji A.Ş. Uyuşmazlığı", tarih=date(2023, 11, 20), tur="İletişim",
                 metin="Nilüfer Teknoloji, soğuk hava deposu arızası sebebiyle emtianın hasar gördüğünü bildiren ilk yazılı e-postayı iletti.",
                 kaynak_alinti="20.11.2023 tarihli yazılı bildirimimizde soğuk hava deposundaki 4 derecelik sapma derhal ihtar edilmiştir.",
                 kaynak_dosya="D-3 E-posta Yazışması", durum="Onaylı", cikarim_yontemi="claude"),
            Olay(id=4, dosya_adi="Papatya Lojistik A.Ş. — Nilüfer Teknoloji A.Ş. Uyuşmazlığı", tarih=date(2023, 12, 5), tur="Toplantı",
                 metin="Şirket genel merkezinde hasar tespit ve sulh müzakeresi toplantısı yapıldı; taraflar tazminatta anlaşamadı.",
                 kaynak_alinti="05.12.2023 tarihli sulh müzakeresi tutanağı: taraflar zarar tazmini konusunda mutabakata varamamıştır.",
                 kaynak_dosya="D-4 Toplantı Tutanağı", durum="Onaylı", cikarim_yontemi="claude"),
            Olay(id=5, dosya_adi="Papatya Lojistik A.Ş. — Nilüfer Teknoloji A.Ş. Uyuşmazlığı", tarih=date(2023, 12, 14), tur="İşlem",
                 metin="Sulh Hukuk Mahkemesi aracılığıyla yaptırılan delil tespiti bilirkişi raporunun taraflara tebliği.",
                 kaynak_alinti="İstanbul 4. Sulh Hukuk Mahkemesi 2023/88 D.İş sayılı dosyasında düzenlenen 14.12.2023 tarihli bilirkişi raporu.",
                 kaynak_dosya="D-5 Mahkeme Raporu", durum="Onaylı", cikarim_yontemi="claude"),
            Olay(id=6, dosya_adi="Papatya Lojistik A.Ş. — Nilüfer Teknoloji A.Ş. Uyuşmazlığı", tarih=date(2024, 1, 8), tur="İşlem",
                 metin="İstanbul 24. Noterliği aracılığıyla 01248 yevmiye numaralı fesih ve tazminat ihtarnamesi keşide edildi.",
                 kaynak_alinti="İstanbul 24. Noterliği 08.01.2024 tarih ve 01248 yevmiye nolu ihtarnamesi tebliğ şerhi.",
                 kaynak_dosya="D-6 Noter İhtarı", durum="Onaylı", cikarim_yontemi="claude"),
            Olay(id=7, dosya_adi="Papatya Lojistik A.Ş. — Nilüfer Teknoloji A.Ş. Uyuşmazlığı", tarih=date(2024, 1, 18), tur="İletişim",
                 metin="Papatya Lojistik vekili tarafından ihtara karşı beyan ve kusur itirazı cevabi ihtarnamesi sunuldu.",
                 kaynak_alinti="18.01.2024 tarihli cevabi ihtar: arızanın elektrik şebekesi kesintisinden kaynaklandığı iddia edilmektedir.",
                 kaynak_dosya="D-7 Cevabi İhtar", durum="İnceleme", cikarim_yontemi="claude"),
            Olay(id=8, dosya_adi="Papatya Lojistik A.Ş. — Nilüfer Teknoloji A.Ş. Uyuşmazlığı", tarih=date(2024, 2, 12), tur="Ödeme",
                 metin="Papatya Lojistik, uyuşmazlık konusu olmayan bakiye ₺280.000 tutarındaki hakediş ödemesini banka yoluyla ifa etti.",
                 kaynak_alinti="12.02.2024 tarihli Garanti BBVA banka dekontu: ref TR880006200000000280000.",
                 kaynak_dosya="D-8 Banka Dekontu", durum="Onaylı", cikarim_yontemi="claude"),
            Olay(id=9, dosya_adi="Papatya Lojistik A.Ş. — Nilüfer Teknoloji A.Ş. Uyuşmazlığı", tarih=date(2024, 3, 5), tur="Dava",
                 metin="İstanbul 14. Asliye Ticaret Mahkemesi'nde 2024/318 Esas sayılı tazminat davası açıldı.",
                 kaynak_alinti="05.03.2024 tarihli dava dilekçesi ve tevzi formu kayıt onay belgesi.",
                 kaynak_dosya="D-9 Dava Dilekçesi", durum="Onaylı", cikarim_yontemi="claude"),
            Olay(id=10, dosya_adi="Papatya Lojistik A.Ş. — Nilüfer Teknoloji A.Ş. Uyuşmazlığı", tarih=date(2024, 4, 12), tur="İşlem",
                 metin="Mahkemece düzenlenen tensip zaptı ile taraflara delil bildirme ve tanık listesi için 2 haftalık kesin süre verildi.",
                 kaynak_alinti="12.04.2024 tarihli tensip tutanağı ara kararları: HMK m. 140 uyarınca ön inceleme duruşması belirlendi.",
                 kaynak_dosya="D-10 Mahkeme Tensip Zaptı", durum="Onaylı", cikarim_yontemi="claude")
        ]
        db.add_all(olaylar)

        db.commit()
        print("TUM MODULLER CLAUDE STANDARDINDA VE ZENGINLIKTE TOHUMLANDI!")

if __name__ == "__main__":
    tohumla()
