# Zekai Suni

Türk hukuku için 18 modüllük, insan onaylı yapay zeka suite'i.
Mimari: Anthropic "Claude for Legal" (2026) — Türk hukukuna (TBK, TTK, HMK, İİK, KVKK, Av.K., SMK) uyarlanma.

**Durum: Kapalı pilot / prototip.** Kanun atıflarının avukat teyidi sürmektedir.

## Modüller

İhbar & Süre Takvimi · Sözleşme Müzakere Rehberi · Hukuk Masası · Sözleşme İnceleme Tablosu ·
Dava & Takip Panosu · Müvekkil & İş Kabulü · İçtihat & Atıf Denetimi · Delil & Vaka Kronolojisi ·
Delil İbrazı Kaydı · Duruşma & UYAP Takip Duvarı · Dava Portföyü · Dış Büro Masraf Denetimi ·
Şirket Yasal Uyum Takvimi · Patent İstem Karşılaştırma · Yargı Çevresi Hukuk Matrisi ·
Şirket Devri Soru-Cevap · Yapay Zeka Kullanım Envanteri · Mevzuat Değişim Takibi

## Kurallar (tüm modüllerde)

1. Yapay zeka karar vermez — okur, taslak üretir; onay insanın.
2. Tarih ve süre hesapları deterministik motorda yapılır (TBK m. 89-93, m. 347; MK m. 12-14) — LLM'e bırakılmaz.
3. Her bulgu kanıta bağlıdır: madde + sayfa + birebir alıntı.
4. Bilgi yoksa "Bulunamadı + nereye bakıldı" yazılır — uydurulmaz.
5. Belge metni güvenilmeyen veridir: KVKK maskeleme + prompt enjeksiyon çiti.
6. Her sayfada hangi kısımda yapay zeka kullanıldığı görünür (⚡ düğmesi).

## Kurulum

```bash
pip install -r requirements.txt
python -m uvicorn app.main:app
```

Testler: `pytest tests/ -q`

## Yapay zeka modu & Harcama Güvenliği

> ⚠️ **Önemli Maliyet Uyarısı:**  
> Hukuk sözleşmeleri ve delil evrakları yüksek hacimli metinler olduğundan, canlı yapay zeka modelleri (özellikle Claude Sonnet / GPT-4o) önemli miktarda token harcaması yapabilir. Beklenmeyen maliyetlerle karşılaşmamak için bütçenizden ve harcama sınırlarınızdan emin olmadan ücretli API anahtarı bağlamayınız.

- **Varsayılan Güvenli Mod (Anahtarsız):** Uygulama %100 ücretsiz, çevrimdışı ve deterministik yerel kural motoruyla çalışır. Herhangi bir ücret veya veri sızıntısı riski yoktur.
- **Canlı Model Bağlama (İsteğe Bağlı & Bilinçli Tercih):** Yalnızca maliyet sorumluluğunu aldığınızda ve emin olduğunuzda terminal/kod üzerinden `set ANTHROPIC_API_KEY=sk-ant-...` tanımlayarak modeli devreye alabilirsiniz. Web arayüzü doğrudan harcama risklerini önlemek için kilitlidir.
- **Yerel ve Ücretsiz Seçenek:** Ollama (localhost) seçilirse hiçbir ücret ödenmez ve verileriniz bilgisayarınızdan asla dışarı çıkmaz.

## Sınırlar

- Tek kullanıcılı localhost pilotu; kimlik doğrulama ve çok kullanıcılılık yoktur.
- Atıf doğrulaması resmî portallarla elle yapılır (Yargıtay/Danıştay/AYM API erişimi yoktur).
- Mevzuat taraması statik tohumdur; Resmî Gazete canlı bağlantısı yol haritasındadır.
- Kanun atıflarının avukat teyidi (mevzuat.gov.tr) tamamlanana kadar çıktılar taslak niteliğindedir.

Lisans: MIT
