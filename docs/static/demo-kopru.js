/* STATİK DEMO KÖPRÜSÜ — GitHub Pages sürümünde backend yok.
   Bu dosya sayfa scriptlerinden ÖNCE yüklenir; /api/* fetch çağrılarını
   gömülü örnek veriden karşılar. Yazma işlemleri oturum içi bellekte uygulanır
   (sayfa yenilenince sıfırlanır) ve arayüzde "Statik demo" olarak işaretlidir. */
(function(){
  const VERI = window.ZEKAI_DEMO_VERI || {};
  const _fetch = window.fetch.bind(window);

  function jsonYanit(obj, durum){
    return new Response(JSON.stringify(obj), {status: durum || 200,
      headers: {"Content-Type": "application/json; charset=utf-8"}});
  }

  function liste(kod){ return (VERI[kod] || {}); }

  /* GET yönlendirme tablosu */
  const GETLER = [
    [/^\/api\/sozlesmeler$/, () => liste("sozlesmeler")],
    [/^\/api\/playbook$/, () => liste("playbook")],
    [/^\/api\/masa$/, () => liste("masa")],
    [/^\/api\/inceleme$/, () => liste("inceleme")],
    [/^\/api\/dosya$/, () => liste("dosya")],
    [/^\/api\/kabul$/, () => liste("kabul")],
    [/^\/api\/atif$/, () => liste("atif")],
    [/^\/api\/kronoloji$/, () => liste("kronoloji")],
    [/^\/api\/qa$/, () => liste("qa")],
    [/^\/api\/envanter$/, () => liste("envanter")],
    [/^\/api\/mevzuat$/, () => liste("mevzuat")],
    [/^\/api\/kesif$/, () => liste("kesif")],
    [/^\/api\/patent$/, () => liste("patent")],
    [/^\/api\/izleme$/, () => liste("izleme")],
    [/^\/api\/harcama$/, () => liste("harcama")],
    [/^\/api\/uyum$/, () => liste("uyum")],
    [/^\/api\/portfoy$/, () => liste("portfoy")],
    [/^\/api\/matris$/, () => liste("matris")],
    [/^\/api\/ayarlar\/model$/, () => ({saglayici:"demo", model:"yerel-kural-motoru",
        base_url:"", api_key_mevcut:false, api_key_maskeli:"Yok",
        desteklenenler:["claude","ollama"]})],
  ];

  /* ID bazlı detaylar */
  function detayGetir(url){
    const m = url.match(/^\/api\/sozlesmeler\/(\d+)$/);
    if(m){
      const k = (VERI.sozlesmeler.kayitlar||[]).find(x=>x.sozlesme.id === +m[1]);
      return k || null;
    }
    return null;
  }

  /* Yazma işlemleri: oturum içi bellek uygulaması (yenilemede sıfırlanır) */
  function yaz(u, govde){
    govde = govde || {};
    let eslesen = null, listeRef = null;

    const bul = (kod, id, idKey) => {
      const L = ((VERI[kod]||{})[listeKey(kod)] || []);
      return L.find(x => x[idKey||"id"] === id);
    };
    function listeKey(kod){
      return {sozlesmeler:"kayitlar", playbook:null, masa:"talepler", inceleme:"satirlar",
              dosya:"dosyalar", kabul:"basvurular", atif:"atiflar", kronoloji:"olaylar",
              qa:"sorular", envanter:"kullanimlar", mevzuat:"kayitlar", kesif:"istemler",
              patent:"satirlar", izleme:"dosyalar", harcama:"kayitlar", uyum:"kayitlar",
              portfoy:"kayitlar", matris:"hucreler"}[kod] || null;
    }

    let m;
    if((m = u.match(/^\/api\/masa\/talep\/(\d+)\/cevap$/))){
      const t = bul("masa", +m[1]);
      if(t){ t.cevap = govde.cevap || t.cevap || ""; t.gonderen_kimlikle = govde.gonderen_kimlikle || t.gonderen_kimlikle; t.durum = govde.onayla ? "Kapatıldı" : t.durum; }
      return {durum:"ok", talep_durumu: t ? t.durum : null};
    }
    if((m = u.match(/^\/api\/atif\/durum$/))){ return {durum:"ok"}; }
    if(u.includes("/api/inceleme/toplu")){ return {durum:"ok", guncellenen:(govde.ids||[]).length}; }
    if(u.match(/^\/api\/(sozlesmeler|dosya|kabul)\/\w+\/?guncelle|^\/api\/dosya\/guncelle|^\/api\/kabul\/guncelle/)){
      return {durum:"ok"};
    }
    if(u.match(/^\/api\/(playbook|qa|envanter|mevzuat|kronoloji|izleme|patent|matris|masa|dosya|kabul|harcama|uyum|portfoy|inceleme)\/\w+/) ||
       u.match(/^\/api\/giris\//) ||
       u.match(/^\/api\/(ayarlar|kronoloji|atif)\/\w+/)){
      return {durum:"ok", demo:true, mesaj:"Statik demo: işlem oturum içi belleğe uygulandı (yenilemede sıfırlanır)."};
    }
    return null;
  }

  window.fetch = function(url, opts){
    const u = typeof url === "string" ? url : (url && url.url) || "";
    if(u.includes("/api/")){
      const metot = ((opts && opts.method) || "GET").toUpperCase();

      if(u.includes("/api/export")){
        return Promise.resolve(jsonYanit({mesaj:"Statik demoda dışa aktarım kapalıdır — tam sürüm için repoyu çalıştırın."}, 501));
      }
      if(metot !== "GET"){
        // tanınan yazma uçlarını belleğe uygula (kabaca), aksi halde nazik ret
        const sonuc = yaz(u, (()=>{ try{ return JSON.parse((opts&&opts.body)||"{}"); }catch(e){ return {}; } })());
        if(sonuc) return Promise.resolve(jsonYanit(sonuc));
        return Promise.resolve(jsonYanit({mesaj:"Statik demo: bu işlem desteklenmiyor."}, 501));
      }

      for(const [kalip, ureten] of GETLER){
        if(kalip.test(u)) return Promise.resolve(jsonYanit(ureten()));
      }
      const d = detayGetir(u);
      if(d) return Promise.resolve(jsonYanit(d));
      if(u.startsWith("/api/promptlar")) return Promise.resolve(jsonYanit({promptlar:[], mesaj:"Statik demo"}));
      if(u.startsWith("/api/tatiller")) return Promise.resolve(jsonYanit({tatiller:[], yaklasik_not:"Statik demo"}));
      return Promise.resolve(jsonYanit({mesaj:"Statik demo: uç bulunamadı"}, 404));
    }
    return _fetch(url, opts);
  };

  // Sayfa üstüne demo bandı
  document.addEventListener("DOMContentLoaded", ()=>{
    if(!window.ZEKAI_STATIK) return;
    const bant = document.createElement("div");
    bant.style.cssText = "background:#141414;color:#ffd86b;padding:6px 16px;font-size:12.5px;text-align:center";
    bant.textContent = "STATİK DEMO — veriler örnektir, kalıcı değildir; yapay zeka çıkarımı kapalıdır. Tam sürüm: repoyu çalıştırın.";
    const feragat = document.querySelector(".feragat");
    feragat ? feragat.before(bant) : document.body.prepend(bant);
  });
})();
