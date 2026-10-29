/* Her sayfaya "veri giriş ekranı" ekler:
   - .ust-sag'a "+ Yeni kayıt" düğmesi (GIRIS_ALANLARI tanımlıysa)
   - "Örneği sil" düğmesi (GIRIS_MODUL tanımlıysa)
   - Dosya yükleme + metin yapıştırma seçenekleri (tur:"dosya" / "metin")
   Kullanım: sayfada window.GIRIS_MODUL="modulad"; window.GIRIS_ALANLARI=[...];
             window.GIRIS_GONDER=async (veri, dosya) => {...}; tanımla, bu dosya modalı kurar. */
(function(){
  function kur(){
    const hedef = document.querySelector(".ust-sag");
    if(!hedef) return;
    const btn = document.createElement("button");
    btn.className = "birincil";
    btn.textContent = window.GIRIS_BASLIK || "+ Yeni kayıt";
    btn.addEventListener("click", ac);
    hedef.prepend(btn);
    if(window.GIRIS_MODUL){
      // Sayfada zaten 'Örnek verileri sil' (geri almali) düğmesi varsa kendi sil düğmemizi eklemeyiz
      const kapsamli = [...document.querySelectorAll("button")].some(b=>b.textContent.includes("Örnek verileri sil"));
      if(!kapsamli){
        const sil = document.createElement("button");
        sil.className = "ikincil";
        sil.textContent = "Örneği sil";
        sil.addEventListener("click", async ()=>{
          if(!confirm("ÖRNEK VERİ + bu modüldeki TÜM kayıtlar silinecek (sıfırdan başlarsınız). Emin misiniz?")) return;
          const r = await api("/api/giris/ornek-sil/"+window.GIRIS_MODUL, {method:"POST"});
          alert(r.not + " (silinen: "+r.silinen+")");
          location.reload();
        });
        hedef.prepend(sil);
      }
    }
  }
  function ac(){
    const eski = document.getElementById("giris-modal");
    if(eski) eski.remove();
    const modal = document.createElement("div");
    modal.id = "giris-modal";
    modal.style.cssText = "position:fixed;inset:0;background:rgba(20,20,20,.35);z-index:60;display:flex;align-items:flex-start;justify-content:center;padding:50px 16px;overflow-y:auto";
    const kutu = document.createElement("div");
    kutu.style.cssText = "background:#fff;border-radius:14px;width:660px;max-width:96vw;padding:0 0 18px;max-height:88vh;overflow-y:auto";
    let icerik = `<div style="display:flex;justify-content:space-between;align-items:center;padding:16px 22px 6px">
      <h2 style="margin:0;font-size:18px">${window.GIRIS_BASLIK || "Yeni kayıt"}</h2>
      <button id="gm-kapat" style="background:none;border:none;font-size:22px;cursor:pointer">×</button></div>
      <div style="padding:6px 22px">`;
    if(window.GIRIS_ACIKLAMA) icerik += `<p class="uyari">${window.GIRIS_ACIKLAMA}</p>`;
    for(const a of (window.GIRIS_ALANLARI||[])){
      icerik += `<label style="display:block;font-size:12px;color:var(--ikinci);margin:10px 0 0">${a.etiket}`;
      if(a.tur==="textarea") icerik += `<textarea data-key="${a.key}" rows="3" style="width:100%;border:1px solid var(--cizgi);border-radius:7px;padding:7px;font-size:13px"></textarea>`;
      else if(a.tur==="select") icerik += `<select data-key="${a.key}" style="width:100%;border:1px solid var(--cizgi);border-radius:7px;padding:7px;font-size:13px">${a.secenekler.map(s=>`<option>${s}</option>`).join("")}</select>`;
      else if(a.tur==="checkbox") icerik += ` <input type="checkbox" data-key="${a.key}" style="margin-left:8px">`;
      else if(a.tur==="dosya") icerik += `<input type="file" data-key="${a.key}" accept="${a.kabul||".pdf,.docx,.txt"}" style="width:100%;padding:6px;font-size:13px">`;
      else icerik += `<input type="${a.tur||"text"}" data-key="${a.key}" placeholder="${a.ornek||""}" style="width:100%;border:1px solid var(--cizgi);border-radius:7px;padding:7px;font-size:13px">`;
      icerik += "</label>";
    }
    icerik += `<div id="gm-sonuc" style="margin-top:10px"></div>
      <button id="gm-gonder" class="birincil" style="margin-top:14px">${window.GIRIS_GONDER_BASLIK||"Kaydet ve gönder"}</button></div>`;
    kutu.innerHTML = icerik;
    modal.appendChild(kutu);
    document.body.appendChild(modal);
    modal.querySelector("#gm-kapat").addEventListener("click", ()=>modal.remove());
    modal.addEventListener("click", e=>{ if(e.target===modal) modal.remove(); });
    modal.querySelector("#gm-gonder").addEventListener("click", async ()=>{
      const btn = modal.querySelector("#gm-gonder");
      const sonuc = modal.querySelector("#gm-sonuc");
      btn.disabled = true; btn.textContent = "İşleniyor…";
      try{
        const veri = {};
        let dosya = null;
        modal.querySelectorAll("[data-key]").forEach(el=>{
          const k = el.dataset.key;
          if(el.type==="checkbox") veri[k]=el.checked;
          else if(el.type==="file"){ if(el.files[0]) dosya=el.files[0]; }
          else if(el.value!=="") veri[k]=el.value;
        });
        await window.GIRIS_GONDER(veri, dosya, sonuc);
        btn.textContent = "Kaydedildi ✓";
        setTimeout(()=>{ modal.remove(); if(window.yukle) yukle(); }, 700);
      }catch(h){
        sonuc.innerHTML = `<div class="uyari" style="background:var(--kirmizi-zemin)">Hata: ${String(h.message||h).slice(0,200)}</div>`;
        btn.disabled = false; btn.textContent = "Tekrar dene";
      }
    });
  }
  if(document.readyState==="loading") document.addEventListener("DOMContentLoaded", kur); else kur();
})();
