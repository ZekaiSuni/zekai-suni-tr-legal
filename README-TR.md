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

```
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8765
```

Tarayıcı: `http://127.0.0.1:8765` · Testler: `pytest tests/ -q`

## Yapay zeka modu

- **Anahtar yok:** uygulama yerel kural motoruyla (demo) çalışır — ücretsiz, çevrimdışı, sonuçlar "demo" etiketli.
- **Anahtar varsa:** `set ANTHROPIC_API_KEY=...` sonrası çıkarımlar gerçek modele geçer. Bu modda Anthropic, kullanım başına ücret alır (kendi API hesabınızdan); ücret istemiyorsanız anahtar girmeyin — demo modu yeterlidir.
- **Model listesi:** Model Ayarları → "Çalışan Modelleri Getir" düğmesi, hesabınızda gerçekten açık olan modelleri çeker.
- **Yerel seçenek:** Ollama (localhost) seçilirse veri bilgisayardan çıkmaz.

## Sınırlar

- Tek kullanıcılı localhost pilotu; kimlik doğrulama ve çok kullanıcılılık yoktur.
- Atıf doğrulaması resmî portallarla elle yapılır (Yargıtay/Danıştay/AYM API erişimi yoktur).
- Mevzuat taraması statik tohumdur; Resmî Gazete canlı bağlantısı yol haritasındadır.
- Kanun atıflarının avukat teyidi (mevzuat.gov.tr) tamamlanana kadar çıktılar taslak niteliğindedir.

Lisans: MIT
