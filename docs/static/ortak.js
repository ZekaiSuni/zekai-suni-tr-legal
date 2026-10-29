/* Ortak yardımcılar: fetch, çipler, çekmece, tarih TR formatı */
/* XSS kaçışı — dış kaynak (belge/LLM/karşı taraf) verisi innerHTML'e basılırken ZORUNLU */
function esc(s){ return (s ?? "").toString().replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;"); }

const AYLAR = ["Oca","Şub","Mar","Nis","May","Haz","Tem","Ağu","Eyl","Eki","Kas","Ara"];
function trTarih(iso){ if(!iso) return "—"; const d=new Date(iso+(iso.length===10?"T00:00:00":"")); return `${d.getDate()} ${AYLAR[d.getMonth()]} ${d.getFullYear()}`; }
async function api(yol, secenek){ const r = await fetch(yol, secenek); if(!r.ok){ throw new Error(await r.text()); } return r.json(); }
function rozet(metin, tur){ return `<span class="rozet ${tur}">${metin}</span>`; }
const DURUM_RENK = {
  "Standart":["Standart","yesil"], "Fallback 1":["◐ Alternatif Hüküm 1","sari"], "Sapma":["Sapma","sari"],
  "Kabul edilemez":["Kabul edilemez","kirmizi"], "Eksik":["Eksik","gri"], "N/A":["N/A","gri"],
  "İnceleme":["İnceleme","gri"], "Bekliyor":["Bekliyor","gri"],
  "Kaçtı":["Kaçtı","kirmizi"], "Belirsiz":["Belirsiz","gri"],
  "Durdur":["Durdur","kirmizi"], "Yüksek":["Yüksek","kirmizi"], "Orta":["Orta","sari"],
  "Günlük":["Günlük","yesil"], "Henüz yok":["Henüz yok","gri"],
  "Onaylandı":["Onaylandı","yesil"], "Koşullu onaylandı":["Koşullu onaylandı","sari"],
  "Reddedildi":["Reddedildi","kirmizi"], "Yükseltildi":["Yükseltildi","sari"], "Gönderildi":["Gönderildi","gri"],
  "Temiz":["Temiz","yesil"], "1 isabet":["1 isabet","sari"], "Muhtemel çatışma":["Muhtemel çatışma","kirmizi"],
  "Çalıştırılmadı":["Çalıştırılmadı","gri"], "Avukat incelemesi":["Avukat incelemesi","mavi"],
  "Kaynak gerekli":["Kaynak gerekli","sari"], "Doğrulandı":["Doğrulandı","yesil"],
  "Karar bulunamadı":["Karar bulunamadı","kirmizi"], "İçtihat değişmiş olabilir":["İçtihat değişmiş olabilir","sari"],
  "Yeni":["Yeni","mavi"], "Taslak hazır":["Taslak hazır","mavi"], "Bilgi bekliyor":["Bilgi bekliyor","sari"],
  "Kapatıldı":["Kapatıldı","yesil"],
  "Geciken":["Geciken","kirmizi"], "Taslak bekliyor":["Taslak bekliyor","gri"],
  "İncelemede":["İncelemede","sari"], "Yayınlandı":["Yayınlandı","yesil"], "Onaylandı ✓":["Onaylandı","yesil"],
  "Geçti":["Geçti","gri"], "Önümüzdeki":["Önümüzdeki","mavi"], "Henüz tarihsiz":["Henüz tarihsiz","gri"],
  "İleride tarih yok":["İleride tarih yok","gri"],
  "Onaylı":["Onaylı","yesil"], "İtirazlı":["İtirazlı","kirmizi"], "Taslak":["Taslak","sari"],
};
function durumRozet(durum){ const d = DURUM_RENK[durum] || [durum, "gri"]; return rozet(d[0], d[1]); }
function cekmeceAc(html){ document.getElementById("cekmecem").classList.remove("gizli"); document.getElementById("d-icerik").innerHTML = html; }
function cekmeceKapat(){ document.getElementById("cekmecem").classList.add("gizli"); }

/* --- İnsan Onayı Mührü (Orijinal FNV-1a 32-bit sealOf mekanizması) --- */
function muhurHesapla(metin, onaylayanKisi, tarih) {
  const ham = `${metin || ""}|${onaylayanKisi || ""}|${tarih || ""}`;
  let h = 0x811c9dc5;
  for (let i = 0; i < ham.length; i++) {
    h ^= ham.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return "fnv1a-" + (h >>> 0).toString(16).padStart(8, "0");
}
/* Onaylı kayıt rozeti: mühürlü ise yeşil ✓, değilse sarı AI taslak rozeti */
function onayRozeti(onaylandi, metin, onaylayan, tarih) {
  return onaylandi
    ? `<span class="mini-cipy mini-duzeltildi" title="${muhurHesapla(metin, onaylayan, tarih)}">✓ Avukat Onaylı (${muhurHesapla(metin, onaylayan, tarih).slice(0, 14)}…)</span>`
    : `<span class="mini-cipy cikarim-demo">Taslak (yapay zeka çıkarımı — avukat onayı bekliyor)</span>`;
}

/* --- Şeffaflık Çekmecesi (Talimatname Bölüm 3, Adım 4) ---
   Her sayfada '⚡ AI Promptu & Şeması' düğmesi: 3 sekme
   1) AI nerede devreye giriyor (deterministik/AI ayrımı)
   2) Türkçe sistem promptu + şema
   3) Orijinal Claude for Legal notes-for-claude */
(function(){
  function cekmeceKur(){
    const hedef = document.querySelector(".ust-sag");
    if(!hedef || document.getElementById("prompt-btn")) return;
    const b = document.createElement("button");
    b.id = "prompt-btn";
    b.className = "ikincil";
    b.textContent = "⚡ Yapay Zeka Talimatı & Şeması";
    b.addEventListener("click", ac);
    hedef.prepend(b);
  }
  async function ac(){
    const modul = window.GIRIS_MODUL || (location.pathname.match(/([a-z]+)\.html/)||[])[1] || "ihbar";
    let d;
    try { d = await api("/api/promptlar/" + modul); }
    catch(e){ alert("Prompt yüklenemedi: " + e.message); return; }
    let eski = document.getElementById("prompt-cekmecesi");
    if(eski) eski.remove();
    const panel = document.createElement("div");
    panel.id = "prompt-cekmecesi";
    panel.style.cssText = "position:fixed;top:0;right:0;bottom:0;width:560px;max-width:94vw;background:#fff;border-left:1px solid var(--cizgi);box-shadow:-8px 0 24px rgba(0,0,0,.07);z-index:70;display:flex;flex-direction:column";
    panel.innerHTML = `
      <div style="padding:14px 18px;border-bottom:1px solid var(--cizgi);display:flex;justify-content:space-between;align-items:center">
        <b>⚡ ${modul} — Yapay Zeka Talimatı & Çalışma Mantığı</b>
        <button id="pc-kapat" style="background:none;border:none;font-size:22px;cursor:pointer">×</button></div>
      <div style="padding:10px 18px;border-bottom:1px solid var(--cizgi);background:var(--yesil-zemin);font-size:12.5px;line-height:1.5">
        <b>1) Yapay zeka nerede devreye giriyor?</b><br>${d.rol_ayrimi||"—"}
        <div style="margin-top:6px;color:var(--ikinci)">Kural: Yapay zeka karar vermez, yalnız okur ve taslak üretir; insan onayı izleri ayrı tutulur (bütünlük işareti FNV-1a — kriptografik imza DEĞİLDİR).</div></div>
      <div style="padding:8px 18px;background:var(--kirmizi-zemin);font-size:12px;line-height:1.5;color:var(--kirmizi)">
        ⚠ HUKUKİ TEYİT BEKLİYOR: Bu modüldeki kanun atıfları avukat tarafından mevzuat.gov.tr üzerinden
        teyit edilmedi (Talimat 5.5). Teyit edilene kadar çıktılar yalnız taslak niteliğindedir.</div>
      <div style="padding:8px 18px;display:flex;gap:8px">
        <button class="ikincil" id="pc-tab-tr" style="font-size:12px">Türkçe Sistem Talimatı</button>
        <button class="ikincil" id="pc-tab-orj" style="font-size:12px">Orijinal Claude Notları</button>
        <button class="ikincil" id="pc-kopyala" style="font-size:12px">📋 Kopyala</button></div>
      <pre id="pc-icerik" style="flex:1;overflow:auto;margin:0;padding:12px 18px;font-size:11.5px;white-space:pre-wrap;background:var(--zemin)"></pre>`;
    document.body.appendChild(panel);
    const icerik = document.getElementById("pc-icerik");
    const goster = (icerikMetni) => { icerik.textContent = icerikMetni || "(dosya henüz yok)"; };
    goster(d.turkce_prompt);
    document.getElementById("pc-tab-tr").addEventListener("click", ()=>goster(d.turkce_prompt));
    document.getElementById("pc-tab-orj").addEventListener("click", ()=>goster(d.orijinal_notes_for_claude));
    document.getElementById("pc-kopyala").addEventListener("click", ()=>{
      navigator.clipboard.writeText(icerik.textContent || "");
      document.getElementById("pc-kopyala").textContent = "Kopyalandı ✓";
    });
    document.getElementById("pc-kapat").addEventListener("click", ()=>panel.remove());
  }
  if(document.readyState==="loading") document.addEventListener("DOMContentLoaded", cekmeceKur); else cekmeceKur();
})();

/* --- HTML etiketli şablon (render katmanı kalıcı XSS çözümü) ---
   Kullanım: kutu.innerHTML = html`<div>${veri}</div>`
   Her ${...} otomatik kaçışlanır; bilinçli HTML için ${raw(deger)} kullanılır. */
function escHtml(s){
  return (s ?? "").toString().replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}
function rawHtml(s){ return { __z_html: (s ?? "").toString() }; }
function html(strings, ...degerler){
  let cikti = "";
  strings.forEach((parca, i) => {
    cikti += parca;
    if (i < degerler.length) {
      const d = degerler[i];
      cikti += (d && d.__z_html) ? d.__z_html : escHtml(d);
    }
  });
  return cikti;
}

/* --- Merkezi sıfırlama onayı (TÜM sayfalar için) ---
   /ornek-sil ve /ornek-geri-yukle çağrıları kullanıcı onayı olmadan geçmez. */
(function(){
  const _fetch = window.fetch;
  window.fetch = function(url, opts){
    const u = typeof url === "string" ? url : (url && url.url) || "";
    if (u.includes("ornek-sil") || u.includes("ornek-geri-yukle")) {
      if (!confirm("DİKKAT: Bu işlem örnek veriyi TÜM modüllerde değiştirir/siler. Emin misiniz?")) {
        return Promise.reject(new Error("kullanıcı iptal etti"));
      }
    }
    return _fetch.apply(this, arguments);
  };
})();
