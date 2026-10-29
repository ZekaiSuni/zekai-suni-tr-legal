/* STATİK DEMO KÖPRÜSÜ v2 — GitHub Pages'te tam interaktif çalışma modu.
   - /api/* GET çağrıları gömülü örnek veriden karşılanır.
   - Yazma işlemleri tarayıcının localStorage'ına KAYDEDİLİR (yenilemede kalır).
   - "Demo verilerini sıfırla" ile başlangıç durumuna dönülür. */
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
    [/^\/api\/ayarlar\/model$/, () => ({saglayici:"demo", model:"yerel-kural-motoru",
        base_url:"", api_key_mevcut:false, api_key_maskeli:"Yok",
        desteklenenler:["claude","ollama"]})],
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

    if(u.includes("/api/export")){
      return Promise.resolve(jsonYanit({mesaj:"Statik demoda dışa aktarım kapalıdır — tam sürüm için repoyu çalıştırın."}, 501));
    }
    if(u.includes("/api/promptlar")){
      return Promise.resolve(jsonYanit({promptlar:[], mesaj:"Statik demoda prompt görüntüleyici kapalıdır."}, 200));
    }
    if(u.includes("/api/tatiller")){
      return Promise.resolve(jsonYanit({tatiller:[], yaklasik_not:"Statik demo — tatil takvimi tam sürümdedir."}, 200));
    }
    if(u.includes("/api/ayarlar/model")){
      return Promise.resolve(jsonYanit({saglayici:"demo", model:"yerel-kural-motoru",
        base_url:"", api_key_mevcut:false, api_key_maskeli:"Yok",
        desteklenenler:["claude","ollama"]}));
    }

    if(metot === "GET"){
      for(const [kalip, ureten] of GETLER){
        if(kalip.test(u)) return Promise.resolve(jsonYanit(ureten()));
      }
      const m = u.match(/^\/api\/sozlesmeler\/(\d+)$/);
      if(m){
        const k = listedenBul("sozlesmeler", "kayitlar", +m[1]);
        return k ? Promise.resolve(jsonYanit(k)) : Promise.resolve(jsonYanit({mesaj:"bulunamadı"}, 404));
      }
      return Promise.resolve(jsonYanit({mesaj:"Statik demo: uç bulunamadı"}, 404));
    }

    let govde = {};
    try { govde = JSON.parse((opts && opts.body) || "{}"); } catch(e){}

    for(const [kalip, islev] of YAZILAR){
      const m = u.match(kalip);
      if(m){ const s = islev(m, govde); kaydet(); return Promise.resolve(jsonYanit(s)); }
    }
    for(const [kalip, kod, listeKey, kurucu] of EKLE){
      if(kalip.test(u)){
        const yeniKayit = kurucu(govde);
        state[kod][listeKey].push(yeniKayit);
        kaydet();
        return Promise.resolve(jsonYanit({durum:"ok", id: yeniKayit.id, demo_kalici: true}));
      }
    }
    kaydet();
    return Promise.resolve(jsonYanit({durum:"ok", demo:true,
      mesaj:"Statik demo: işlem simüle edildi."}));
  };

  document.addEventListener("DOMContentLoaded", ()=>{
    if(!window.ZEKAI_STATIK) return;
    const bant = document.createElement("div");
    bant.style.cssText = "background:#141414;color:#ffd86b;padding:6px 16px;font-size:12.5px;text-align:center";
    bant.innerHTML = "STATİK DEMO — veriler tarayıcınıza kaydedilir (sunucuya gitmez). " +
      '<button id="zk-demo-sifirla" style="background:#ffd86b;color:#141414;border:none;border-radius:4px;padding:1px 8px;font-size:11px;cursor:pointer">Demo verilerini sıfırla</button>';
    const feragat = document.querySelector(".feragat");
    feragat ? feragat.before(bant) : document.body.prepend(bant);
    const btn = document.getElementById("zk-demo-sifirla");
    if(btn) btn.addEventListener("click", ()=>{
      if(!confirm("Demo verileriniz sıfırlanacak (örnek veri geri gelir). Emin misiniz?")) return;
      localStorage.removeItem(ANAHTAR); location.reload();
    });
  });
})();
