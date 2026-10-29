/* STATİK DEMO KÖPRÜSÜ v3 — GitHub Pages'te tam interaktif çalışma modu.
   - Tüm /api/* istekleri yakalanır (GET, POST).
   - Veriler localStorage'a kaydedilir (tarayıcı yenilense de silinmez).
   - "Demo verilerini sıfırla" butonuyla ilk fabrika ayarlarına dönülür.
   - İhbar ekleme, karar verme, onaylama, arama, filtreleme ve .csv/.json/.ics indirme canlı çalışır. */
(function(){
  const ANAHTAR = "zekaiDemoVeri";

  let state;
  try {
    const sakli = localStorage.getItem(ANAHTAR);
    state = sakli ? JSON.parse(sakli) : (window.ZEKAI_DEMO_VERI || {});
  } catch(e){ state = window.ZEKAI_DEMO_VERI || {}; }
  if(!localStorage.getItem(ANAHTAR)){
    try { localStorage.setItem(ANAHTAR, JSON.stringify(state)); } catch(e){}
  }
  function kaydet(){ try { localStorage.setItem(ANAHTAR, JSON.stringify(state)); } catch(e){} }

  const _fetch = window.fetch.bind(window);

  function jsonYanit(obj, durum){
    return new Response(JSON.stringify(obj), {status: durum || 200,
      headers: {"Content-Type": "application/json; charset=utf-8"}});
  }

  const L = kod => (state[kod] || {});
  function listedenBul(kod, listeKey, id){
    const L2 = (state[kod] || {})[listeKey] || [];
    return L2.find(x => x.id === id);
  }

  const TATILLER_VERISI = {"tatiller": [{"tarih": "2026-01-01", "ad": "Yılbaşı", "tur": "tam"}, {"tarih": "2026-03-20", "ad": "Ramazan Bayramı 1. gün", "tur": "tam"}, {"tarih": "2026-03-21", "ad": "Hafta sonu", "tur": "tam"}, {"tarih": "2026-03-22", "ad": "Hafta sonu", "tur": "tam"}, {"tarih": "2026-04-23", "ad": "Ulusal Egemenlik ve Çocuk Bayramı", "tur": "tam"}, {"tarih": "2026-05-01", "ad": "Emek ve Dayanışma Günü", "tur": "tam"}, {"tarih": "2026-05-19", "ad": "19 Mayıs / Kurban 4. gün (yaklaşık)", "tur": "tam"}, {"tarih": "2026-05-27", "ad": "Kurban Bayramı 1. gün", "tur": "tam"}, {"tarih": "2026-05-28", "ad": "Kurban Bayramı 2. gün", "tur": "tam"}, {"tarih": "2026-05-29", "ad": "Kurban Bayramı 3. gün", "tur": "tam"}, {"tarih": "2026-05-30", "ad": "Hafta sonu", "tur": "tam"}, {"tarih": "2026-07-15", "ad": "Demokrasi ve Millî Birlik Günü", "tur": "tam"}, {"tarih": "2026-08-30", "ad": "Hafta sonu", "tur": "tam"}, {"tarih": "2026-10-29", "ad": "Cumhuriyet Bayramı", "tur": "tam"}, {"tarih": "2026-03-19", "ad": "Bayram arifesi (yarım gün)", "tur": "yarim"}, {"tarih": "2026-05-26", "ad": "Bayram arifesi (yarım gün)", "tur": "yarim"}, {"tarih": "2027-01-01", "ad": "Yılbaşı", "tur": "tam"}, {"tarih": "2027-03-09", "ad": "Ramazan Bayramı 1. gün", "tur": "tam"}, {"tarih": "2027-03-10", "ad": "Ramazan Bayramı 2. gün", "tur": "tam"}, {"tarih": "2027-03-11", "ad": "Ramazan Bayramı 3. gün", "tur": "tam"}, {"tarih": "2027-04-23", "ad": "Ulusal Egemenlik ve Çocuk Bayramı", "tur": "tam"}, {"tarih": "2027-05-01", "ad": "Hafta sonu", "tur": "tam"}, {"tarih": "2027-05-16", "ad": "Hafta sonu", "tur": "tam"}, {"tarih": "2027-05-17", "ad": "Kurban Bayramı 2. gün (yaklaşık)", "tur": "tam"}, {"tarih": "2027-05-18", "ad": "Kurban Bayramı 3. gün (yaklaşık)", "tur": "tam"}, {"tarih": "2027-05-19", "ad": "19 Mayıs / Kurban 4. gün", "tur": "tam"}, {"tarih": "2027-07-15", "ad": "Demokrasi ve Millî Birlik Günü", "tur": "tam"}, {"tarih": "2027-08-30", "ad": "Zafer Bayramı", "tur": "tam"}, {"tarih": "2027-10-29", "ad": "Cumhuriyet Bayramı", "tur": "tam"}, {"tarih": "2027-03-08", "ad": "Bayram arifesi (yarım gün)", "tur": "yarim"}], "yaklasik_not": "2027 dini bayram tarihleri yaklaşiktir — Resmî Gazete teyidi öncesi motor yalnız bilgi notu üretir, tarih değiştirmez."};

  const GETLER = [
    [/^\/api\/sozlesmeler$/, () => L("sozlesmeler")],
    [/^\/api\/playbook$/, () => L("playbook")],
    [/^\/api\/masa$/, () => L("masa")],
    [/^\/api\/inceleme$/, () => L("inceleme")],
    [/^\/api\/dosya$/, () => L("dosya")],
    [/^\/api\/kabul$/, () => L("kabul")],
    [/^\/api\/atif$/, () => L("atif")],
    [/^\/api\/kronoloji$/, () => L("kronoloji")],
    [/^\/api\/qa$/, () => L("qa")],
    [/^\/api\/envanter$/, () => L("envanter")],
    [/^\/api\/mevzuat$/, () => L("mevzuat")],
    [/^\/api\/kesif$/, () => L("kesif")],
    [/^\/api\/patent$/, () => L("patent")],
    [/^\/api\/izleme$/, () => L("izleme")],
    [/^\/api\/harcama$/, () => L("harcama")],
    [/^\/api\/uyum$/, () => L("uyum")],
    [/^\/api\/portfoy$/, () => L("portfoy")],
    [/^\/api\/matris$/, () => L("matris")],
    [/^\/api\/tatiller$/, () => TATILLER_VERISI],
    [/^\/api\/promptlar$/, () => ({promptlar:[], mesaj:"Statik demo modu: promptlar repodadır."})],
    [/^\/api\/ayarlar\/model$/, () => ({saglayici:"demo", model:"yerel-kural-motoru",
        base_url:"", api_key_mevcut:false, api_key_maskeli:"Yok",
        desteklenenler:["claude","ollama","demo"]})],
  ];

  const YAZILAR = [
    [/^\/api\/masa\/talep\/(\d+)\/cevap$/, (m, b) => {
      const t = listedenBul("masa", "talepler", +m[1]);
      if(t){ t.cevap = b.cevap !== undefined ? b.cevap : t.cevap;
             t.gonderen_kimlikle = b.gonderen_kimlikle || t.gonderen_kimlikle;
             if(b.onayla) t.durum = "Kapatıldı"; }
      return {durum:"ok", talep_durumu: t ? t.durum : null};
    }],
    [/^\/api\/atif\/durum$/, (m, b) => {
      const a = listedenBul("atif", "atiflar", b.atif_id);
      if(a){ a.durum = b.durum; if(b.not_metin) a.dogrulama_notu = b.not_metin; }
      return {durum:"ok"};
    }],
    [/^\/api\/playbook\/madde\/(\d+)$/, (m, b) => {
      const mad = listedenBul("playbook", "maddeler", +m[1]);
      if(mad){ if(b.karar){ mad.karar = b.karar; mad.kararin_kimi = b.kararin_kimi || mad.kararin_kimi; }
               if(b.durum) mad.durum = b.durum; }
      return {durum:"ok"};
    }],
    [/^\/api\/sozlesmeler\/(\d+)\/guncelle$/, (m, b) => {
      const k = listedenBul("sozlesmeler", "kayitlar", +m[1]);
      if(k && k.sozlesme) Object.assign(k.sozlesme, b);
      return {durum:"ok"};
    }],
    [/^\/api\/dosya\/guncelle$/, (m, b) => {
      const d = listedenBul("dosya", "dosyalar", b.id);
      if(d){ if(b.asama) d.asama = b.asama; if(b.sonraki_islem!=null) d.sonraki_islem = b.sonraki_islem;
             if(b.sahibi!=null) d.sahibi = b.sahibi; }
      return {durum:"ok"};
    }],
    [/^\/api\/kabul\/guncelle$/, (m, b) => {
      const bv = listedenBul("kabul", "basvurular", b.id);
      if(bv){ bv.asama = b.asama; if(b.catisma_durumu) bv.catisma_durumu = b.catisma_durumu; }
      return {durum:"ok"};
    }],
    [/^\/api\/envanter\/katman$/, (m, b) => {
      const k = listedenBul("envanter", "kullanimlar", b.id);
      if(k){ k.katman = b.katman; if(b.durum) k.durum = b.durum; }
      return {durum:"ok"};
    }],
    [/^\/api\/qa\/karar$/, (m, b) => {
      const s = listedenBul("qa", "sorular", b.id);
      if(s){ if(b.islem==="onayla"){ s.durum = "Onaylandı"; s.onaylayan = b.kimi || s.onaylayan; if(b.metin) s.taslak = b.metin; }
             else if(b.islem==="yayinla" && s.durum==="Onaylandı"){ s.durum = "Yayınlandı"; } }
      return {durum:"ok"};
    }],
    [/^\/api\/kronoloji\/olay$/, (m, b) => {
      const o = listedenBul("kronoloji", "olaylar", b.id);
      if(o){ o.durum = b.durum; if(b.metin) o.metin = b.metin; }
      return {durum:"ok"};
    }],
    [/^\/api\/izleme\/teyit$/, (m, b) => {
      const d = listedenBul("izleme", "dosyalar", b.id);
      if(d) d.tarih_durumu = b.tarih_durumu;
      return {durum:"ok"};
    }],
    [/^\/api\/inceleme\/toplu$/, (m, b) => {
      let n = 0;
      (b.ids||[]).forEach(id => {
        const s = listedenBul("inceleme", "satirlar", id);
        if(s){ if(b.islem==="inceleme") s.inceleme_gerekli = true;
               if(b.islem==="sahip" && b.sahibi) s.sahibi = b.sahibi; n++; }
      });
      return {durum:"ok", guncellenen:n};
    }],
  ];

  function sonrakiId(listeKey){
    const L2 = (state[listeKey] || []);
    return 1 + L2.reduce((mx, x) => Math.max(mx, x.id || 0), 0);
  }

  const EKLE = [
    [/^\/api\/giris\/dosya\/ekle$/, "dosya", "dosyalar", v => ({id: sonrakiId("dosyalar"), ...v, asama: v.asama || "Yeni", orijinal_ornek: false})],
    [/^\/api\/giris\/kabul\/basvuru\/ekle$/, "kabul", "basvurular", v => ({id: sonrakiId("basvurular"), ...v, asama: v.asama || "Çatışma", catisma_durumu: "Çalıştırılmadı", bekleyen_gun: 0})],
    [/^\/api\/giris\/qa\/soru\/ekle$/, "qa", "sorular", v => ({id: sonrakiId("sorular"), ...v, durum: "Taslak bekliyor", kimlere: v.kimlere || "Tek alıcı"})],
    [/^\/api\/giris\/envanter\/kullanim\/ekle$/, "envanter", "kullanimlar", v => ({id: sonrakiId("kullanimlar"), ...v, katman: "Henüz yok", durum: "Gönderildi"})],
    [/^\/api\/giris\/mevzuat\/kayit\/ekle$/, "mevzuat", "kayitlar", v => ({id: sonrakiId("kayitlar"), ...v, etki: v.etki || "Orta", tarih_durumu: v.gecer_tarihi ? "Önümüzdeki" : "Henüz tarihsiz", dogrulandi: false})],
    [/^\/api\/giris\/portfoy\/ekle$/, "portfoy", "kayitlar", v => ({id: sonrakiId("kayitlar"), ...v})],
    [/^\/api\/giris\/harcama\/ekle$/, "harcama", "kayitlar", v => ({id: sonrakiId("kayitlar"), ...v, durum: "Bekliyor"})],
    [/^\/api\/giris\/uyum\/ekle$/, "uyum", "kayitlar", v => ({id: sonrakiId("kayitlar"), ...v, durum: "Planlandı"})],
    [/^\/api\/giris\/playbook\/madde\/ekle$/, "playbook", "maddeler", v => ({id: sonrakiId("maddeler"), ...v, durum: v.durum || "İnceleme"})],
  ];

  window.fetch = function(url, opts){
    const u = typeof url === "string" ? url : (url && url.url) || "";
    if(!u.includes("/api/")) return _fetch(url, opts);

    const metot = ((opts && opts.method) || "GET").toUpperCase();

    if(metot === "GET"){
      for(const [kalip, ureten] of GETLER){
        if(kalip.test(u)) return Promise.resolve(jsonYanit(ureten()));
      }
      const m = u.match(/^\/api\/sozlesmeler\/(\d+)$/);
      if(m){
        const k = listedenBul("sozlesmeler", "kayitlar", +m[1]);
        return k ? Promise.resolve(jsonYanit(k)) : Promise.resolve(jsonYanit({mesaj:"bulunamadı"}, 404));
      }
      return Promise.resolve(jsonYanit({mesaj:"Statik demo: uç simüle edildi"}, 200));
    }

    let govde = {};
    try { govde = JSON.parse((opts && opts.body) || "{}"); } catch(e){}

    // Sözleşme Ekleme (İhbar Takvimi)
    if(u === "/api/sozlesmeler/ekle"){
      const szState = state.sozlesmeler = state.sozlesmeler || {kayitlar:[], ozet:{}};
      const kayitlar = szState.kayitlar = szState.kayitlar || [];
      const yeniId = 1 + kayitlar.reduce((mx, k) => Math.max(mx, (k.sozlesme && k.sozlesme.id) || 0), 0);
      
      let bitis = null;
      let sonIhbar = null;
      let kalanGun = 60;
      let rozet = "Açık";
      let rozetTuru = "sari";
      
      if(govde.baslangic){
        const basD = new Date(govde.baslangic);
        if(!isNaN(basD)){
          const sureAy = govde.sure_ay || 12;
          basD.setMonth(basD.getMonth() + sureAy);
          bitis = basD.toISOString().slice(0, 10);
          
          const ihbarGun = govde.ihbar_deger || 30;
          basD.setDate(basD.getDate() - ihbarGun);
          sonIhbar = basD.toISOString().slice(0, 10);
          
          const bugun = new Date();
          kalanGun = Math.round((basD - bugun) / (1000 * 60 * 60 * 24));
          if(kalanGun < 0){ rozet = "Kaçtı"; rozetTuru = "kirmizi"; }
          else if(kalanGun <= 30){ rozet = "İhbar zamanı"; rozetTuru = "sari"; }
          else { rozet = "Açık"; rozetTuru = "yesil"; }
        }
      }
      
      const yeniKayit = {
        sozlesme: {
          id: yeniId,
          ad: govde.ad || "Yeni Sözleşme",
          karsi_taraf: govde.karsi_taraf || "Belirtilmedi",
          tur: govde.tur || "Hizmet",
          dosya_adi: "",
          baslangic: govde.baslangic || null,
          sure_ay: govde.sure_ay || 12,
          otomatik_uzatma: !!govde.otomatik_uzatma,
          uzatma_suresi_ay: govde.uzatma_suresi_ay || null,
          uzatma_artis_yuzdesi: govde.uzatma_artis_yuzdesi || null,
          ihbar_deger: govde.ihbar_deger || 30,
          ihbar_birim: govde.ihbar_birim || "gün",
          ihbar_sekli: govde.ihbar_sekli || "Yazılı",
          fiyat_yillik: govde.fiyat_yillik || null,
          para_birimi: "TL",
          sahibi: govde.sahibi || "Avukat",
          inceleme: false,
          duzeltilmis: false,
          cikarim_yontemi: "elle",
          notlar: govde.notlar || "Arayüzden eklendi."
        },
        takvim: {
          donem_baslangici: govde.baslangic || null,
          donem_bitisi: bitis,
          son_ihbar_tarihi: sonIhbar,
          son_ihbar_tatil_mi: false,
          tatil_adi: null,
          onerilen_is_gunu: null,
          kalan_gun: kalanGun,
          rozet: rozet,
          rozet_turu: rozetTuru,
          kimse_islem_yapmazsa: govde.otomatik_uzatma ? "Sözleşme süresi kadar kendiliğinden uzar" : "Kendiliğinden sona erer",
          hukuki_notlar: ["Kullanıcı tarafından elle oluşturuldu."],
          band: {
            pencere_bas: govde.baslangic || "2026-01-01",
            pencere_son: bitis || "2027-01-01",
            donem_bas: govde.baslangic || "2026-01-01",
            donem_son: bitis || "2027-01-01",
            ihbar_gunu: sonIhbar,
            bugun: new Date().toISOString().slice(0, 10),
            uzarsa_son: bitis
          }
        }
      };
      
      kayitlar.unshift(yeniKayit);
      if(szState.ozet) szState.ozet.sozlesme_sayisi = kayitlar.length;
      kaydet();
      return Promise.resolve(jsonYanit({durum:"ok", id: yeniId}));
    }

    // Dosya analizi (Simüle çıkarım)
    if(u.includes("/api/analiz") || u.includes("/api/evrak-yukle-ve-isle")){
      return Promise.resolve(jsonYanit({
        durum: "ok",
        ad: "Yüklenen Belge Analizi",
        karsi_taraf: "Örnek Karşı Taraf Ltd. Şti.",
        tur: "Hizmet",
        baslangic: "2026-06-01",
        sure_ay: 12,
        otomatik_uzatma: true,
        uzatma_suresi_ay: 12,
        ihbar_deger: 30,
        ihbar_birim: "gün",
        ihbar_sekli: "Noter",
        fiyat_yillik: 250000,
        alinti: "İşbu sözleşme 01.06.2026 tarihinde yürürlüğe girer ve 1 yıl geçerlidir. Taraflardan biri 30 gün önceden noter kanalıyla bildirmedikçe birer yıl uzar.",
        notlar: "Demo çıkarım tamamlandı (kanıt alıntısıyla teyit edildi)."
      }));
    }

    for(const [kalip, islev] of YAZILAR){
      const m = u.match(kalip);
      if(m){ const s = islev(m, govde); kaydet(); return Promise.resolve(jsonYanit(s)); }
    }
    for(const [kalip, kod, listeKey, kurucu] of EKLE){
      if(kalip.test(u)){
        const yeniKayit = kurucu(govde);
        if(!state[kod]) state[kod] = {};
        if(!state[kod][listeKey]) state[kod][listeKey] = [];
        state[kod][listeKey].push(yeniKayit);
        kaydet();
        return Promise.resolve(jsonYanit({durum:"ok", id: yeniKayit.id, demo_kalici: true}));
      }
    }
    kaydet();
    return Promise.resolve(jsonYanit({durum:"ok", demo:true, mesaj:"İşlem demo ortamına kaydedildi."}));
  };

  // İndirme ve Dışa Aktarma Butonlarını Bağlama
  document.addEventListener("DOMContentLoaded", ()=>{
    if(!window.ZEKAI_STATIK) return;

    // Üst Demo Bildirim Bandı
    const bant = document.createElement("div");
    bant.style.cssText = "background:#18181b;color:#fef08a;padding:8px 16px;font-size:13px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #27272a;position:sticky;top:0;z-index:9999";
    bant.innerHTML = `
      <div><b>◐ CANLI DEMO SÜRÜMÜ:</b> Tüm işlemler tarayıcınızın hafızasında (localStorage) güvenle saklanır. Herhangi bir sunucuya veri gitmez.</div>
      <div style="display:flex;gap:10px;align-items:center">
        <a href="tanitim.html" style="color:#93c5fd;text-decoration:none;font-weight:600">📖 Dokümantasyon</a>
        <button id="zk-demo-sifirla" style="background:#fef08a;color:#18181b;border:none;border-radius:6px;padding:3px 10px;font-size:12px;font-weight:600;cursor:pointer">Demo Verilerini Sıfırla</button>
      </div>`;
    document.body.prepend(bant);

    const btnSifirla = document.getElementById("zk-demo-sifirla");
    if(btnSifirla) btnSifirla.addEventListener("click", ()=>{
      if(!confirm("Demo verileriniz sıfırlanacak ve fabrika ayarlarına dönülecektir. Emin misiniz?")) return;
      localStorage.removeItem(ANAHTAR); location.reload();
    });

    // İhbar Takvimi İndirme Butonları (.json, .csv, .ics)
    const btnJson = document.getElementById("btn-json");
    if(btnJson) {
      btnJson.onclick = (e) => {
        e.preventDefault();
        const veri = state.sozlesmeler || {};
        const blob = new Blob([JSON.stringify(veri, null, 2)], {type: "application/json;charset=utf-8"});
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "zekai-ihbar-takvimi.json";
        a.click();
      };
    }
    const btnCsv = document.getElementById("btn-csv");
    if(btnCsv) {
      btnCsv.onclick = (e) => {
        e.preventDefault();
        const kayitlar = (state.sozlesmeler && state.sozlesmeler.kayitlar) || [];
        let csv = "ID;Sözleşme Adı;Karşı Taraf;Tür;Başlangıç;Süre (Ay);Son İhbar Günü;Kalan Gün;Rozet\n";
        kayitlar.forEach(k => {
          const s = k.sozlesme || {};
          const t = k.takvim || {};
          csv += `${s.id || ""};"${(s.ad||"").replace(/"/g, '""')}";"${(s.karsi_taraf||"").replace(/"/g, '""')}";${s.tur||""};${s.baslangic||""};${s.sure_ay||""};${t.son_ihbar_tarihi||""};${t.kalan_gun!=null?t.kalan_gun:""};${t.rozet||""}\n`;
        });
        const blob = new Blob(["\ufeff" + csv], {type: "text/csv;charset=utf-8"});
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "zekai-ihbar-takvimi.csv";
        a.click();
      };
    }
    const btnIcs = document.getElementById("btn-ics");
    if(btnIcs) {
      btnIcs.onclick = (e) => {
        e.preventDefault();
        const kayitlar = (state.sozlesmeler && state.sozlesmeler.kayitlar) || [];
        let ics = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Zekai Suni//TR Legal v1.0//TR\n";
        kayitlar.forEach(k => {
          const s = k.sozlesme || {};
          const t = k.takvim || {};
          if(t.son_ihbar_tarihi) {
            const dStr = t.son_ihbar_tarihi.replace(/-/g, "");
            ics += `BEGIN:VEVENT\nSUMMARY:İhbar Son Günü: ${s.ad || "Sözleşme"}\nDESCRIPTION:${s.karsi_taraf || ""} ihbar son tarihi.\nDTSTART;VALUE=DATE:${dStr}\nDTEND;VALUE=DATE:${dStr}\nEND:VEVENT\n`;
          }
        });
        ics += "END:VCALENDAR";
        const blob = new Blob([ics], {type: "text/calendar;charset=utf-8"});
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "zekai-ihbarlar.ics";
        a.click();
      };
    }
  });
})();
