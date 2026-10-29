/* Ortak yan menü ve Evrensel Model / API Ayarları Modalı */
(function(){
  const MODULLER = [
    {id:"ihbar",     ad:"İhbar & Süre Takvimi",          ikon:"⏱", sayfa:"index.html"},
    {id:"playbook",  ad:"Sözleşme Müzakere Rehberi",     ikon:"⚖", sayfa:"playbook.html"},
    {id:"masa",      ad:"Hukuk Masası & Hukuki Görüş",   ikon:"✉", sayfa:"masa.html"},
    {id:"inceleme",  ad:"Sözleşme İnceleme Tablosu",     ikon:"▦", sayfa:"inceleme.html"},
    {id:"dosya",     ad:"Dava & Takip Panosu",           ikon:"🗂", sayfa:"dosya.html"},
    {id:"kabul",     ad:"Müvekkil & İş Kabulü",          ikon:"📥", sayfa:"kabul.html"},
    {id:"atif",      ad:"İçtihat & Atıf Denetimi",       ikon:"§",  sayfa:"atif.html"},
    {id:"kronoloji", ad:"Delil & Vaka Kronolojisi",      ikon:"🕘", sayfa:"kronoloji.html"},
    {id:"qa",        ad:"Şirket Devri Soru-Cevap",  ikon:"💬", sayfa:"qa.html"},
    {id:"envanter",  ad:"Yapay Zeka Kullanım Envanteri", ikon:"◈", sayfa:"envanter.html"},
    {id:"mevzuat",   ad:"Mevzuat Değişim Takibi",        ikon:"📡", sayfa:"mevzuat.html"},
    {id:"kesif",     ad:"Delil İbrazı & Belge Sunma Kaydı", ikon:"📋", sayfa:"kesif.html"},
    {id:"izleme",    ad:"Duruşma & UYAP Takip Duvarı",   ikon:"👁", sayfa:"izleme.html"},
    {id:"portfoy",   ad:"Dava Portföyü & Risk Analizi",  ikon:"🏛", sayfa:"portfoy.html"},
    {id:"harcama",   ad:"Dış Büro Masraf Denetimi",   ikon:"💸", sayfa:"harcama.html"},
    {id:"uyum",      ad:"Şirket Yasal Uyum Takvimi",     ikon:"🏢", sayfa:"uyum.html"},
    {id:"patent",    ad:"Patent İstem Karşılaştırma",    ikon:"⚙",  sayfa:"patent.html"},
    {id:"matris",    ad:"Yargı Çevresi Hukuk Matrisi",   ikon:"🌐", sayfa:"matris.html"},
  ];
  const mevcut = (location.pathname.split("/").pop() || "index.html");
  const nav = document.createElement("aside");
  nav.className = "yan-menu";
  nav.innerHTML = `
    <div class="nav-marka"><span class="logo">◐</span> <b>Zekai Suni</b><span class="cipy ornek">TR</span></div>
    ${MODULLER.map(m=>`<a class="nav-oge ${location.href.includes(m.sayfa)|| (mevcut==="index.html"&&m.id==="ihbar") ? "secili":""}" href="${m.sayfa}">
       <span class="nav-ikon">${m.ikon}</span>${m.ad}</a>`).join("")}
    <div class="nav-alt">
      <button type="button" class="nav-btn-ayar" onclick="window.zekaiModelAyarAc()">⚙ Model Ayarları</button>
      <div style="display:flex;gap:10px;margin-top:6px">
        <a href="tanitim.html" style="color:var(--soluk);text-decoration:none">📖 Proje Tanıtımı</a>
        <a href="https://github.com/ZekaiSuni/zekai-suni-tr-legal" target="_blank" style="color:var(--soluk);text-decoration:none">GitHub Deposu</a>
      </div>
    </div>`;
  document.body.prepend(nav);

  // Model Ayarları Modalını Gövdeye Ekle
  const modalDiv = document.createElement("div");
  modalDiv.id = "zekai-model-modal";
  modalDiv.className = "modal-gizli";
  modalDiv.innerHTML = `
    <div class="modal" style="width:580px">
      <div class="modal-bas">
        <h2>⚙ Yapay Zeka Sağlayıcı & Model Ayarları</h2>
        <button class="kapat" onclick="document.getElementById('zekai-model-modal').classList.remove('acik')">×</button>
      </div>
            <div class="modal-icerik">
        <div style="background:#fef3c7;border:1px solid #f59e0b;color:#92400e;padding:11px 13px;border-radius:8px;font-size:12.5px;line-height:1.5;margin-bottom:14px">
          <b>⚠️ Önemli Harcama & Güvenlik Uyarısı:</b><br>
          Hukuk evrakları ve sözleşmeler yüksek hacimli metinler olduğundan, yapay zeka modelleri önemli miktarda token harcaması ve bütçe aşımı yaratabilir. Olası harcama maliyetlerinden emin olmadıkça ücretli API anahtarı bağlamayınız.
        </div>
        
        <div style="margin-bottom:12px">
          <label style="font-size:12px;font-weight:600;color:var(--ikinci);display:block;margin-bottom:4px">Yapay Zeka Sağlayıcısı</label>
          <select id="zm-saglayici" onchange="window.zekaiSaglayiciDegisti(this.value)" style="width:100%;padding:8px 10px;border:1px solid var(--cizgi);border-radius:8px;font-size:14px">
            <option value="demo">⚡ Yerel Kural Motoru (API Anahtarsız / %100 Ücretsiz & Güvenli)</option>
            <option value="claude">🟣 Anthropic Claude (Ücretli API)</option>
            <option value="ollama">💻 Yerel / Çevrimdışı Ollama (Gizli & Ücretsiz)</option>
          </select>
        </div>

        <div style="margin-bottom:12px">
          <label style="font-size:12px;font-weight:600;color:var(--ikinci);display:block;margin-bottom:4px">Model Adı
            <button type="button" id="zm-kesif-btn" onclick="window.zekaiModelleriGetir()" style="float:right;background:var(--mavi-zemin);color:var(--mavi);border:none;border-radius:6px;padding:2px 8px;font-size:11px;cursor:pointer">⟳ Çalışan Modelleri Getir</button>
          </label>
          <input id="zm-model" list="zm-model-liste" style="width:100%;padding:8px 10px;border:1px solid var(--cizgi);border-radius:8px;font-size:13px" placeholder="Model adı">
          <datalist id="zm-model-liste"></datalist>
          <div id="zm-kesif-sonuc" style="font-size:11px;color:var(--ikinci);margin-top:4px"></div>
        </div>


        <div style="margin-bottom:12px" id="zm-key-alan">
          <label style="font-size:12px;font-weight:600;color:var(--ikinci);display:block;margin-bottom:4px">
            API Anahtarı Girişi 🛡️ (Web Demosunda Kilitli)
          </label>
          <input type="password" id="zm-key" disabled style="width:100%;padding:8px 10px;border:1px solid var(--cizgi);border-radius:8px;font-size:13px;background:#f4f4f5;color:#71717a;cursor:not-allowed" placeholder="Web demosunda harcama güvenliği için kilitlidir">
          <div style="font-size:11px;color:#b45309;margin-top:5px;line-height:1.4">
            🛡️ <b>Harcama Koruması:</b> Genel web ortamında beklenmeyen maliyetleri ve güvenlik risklerini önlemek amacıyla doğrudan anahtar girişi kilitlenmiştir. Canlı API kullanmak için projeyi yerel ortamınıza klonlayıp terminal/kod üzerinden <code>export ANTHROPIC_API_KEY=...</code> tanımlayarak çalıştırınız.
          </div>
        </div>
    

        <div style="margin-bottom:16px" id="zm-url-alan">
          <label style="font-size:12px;font-weight:600;color:var(--ikinci);display:block;margin-bottom:4px">Özel API Uç Noktası (isteğe bağlı)</label>
          <input id="zm-url" style="width:100%;padding:8px 10px;border:1px solid var(--cizgi);border-radius:8px;font-size:13px" placeholder="Varsayılan resmi URL kullanılır">
        </div>

        <div id="zm-test-sonuc" style="margin-bottom:12px;font-size:13px;display:none;padding:8px 12px;border-radius:8px"></div>

        <div style="display:flex;justify-content:space-between;align-items:center;margin-top:16px;border-top:1px solid var(--cizgi);padding-top:14px">
          <button type="button" class="ikincil" onclick="window.zekaiModelTest()">Bağlantıyı Test Et</button>
          <div style="display:flex;gap:8px">
            <button type="button" class="ikincil" onclick="document.getElementById('zekai-model-modal').classList.remove('acik')">Kapat</button>
            <button type="button" class="birincil" onclick="window.zekaiModelKaydet()">Ayarları Kaydet</button>
          </div>
        </div>
      </div>
    </div>
  </div>`;
  document.body.appendChild(modalDiv);

  const stil = document.createElement("style");
  stil.textContent = `
  .yan-menu{position:fixed;top:0;left:0;bottom:0;width:220px;background:#141414;color:#e9e6e0;display:flex;flex-direction:column;padding:14px 10px;z-index:40;overflow-y:auto}
  .nav-marka{padding:4px 10px 14px;font-size:15px;display:flex;align-items:center;gap:7px}
  .nav-marka .logo{color:#7da7d8}
  .nav-oge{display:flex;align-items:center;gap:9px;padding:8px 10px;border-radius:8px;color:#cfcac2;text-decoration:none;font-size:13px;margin-bottom:2px}
  .nav-oge:hover{background:#242424;color:#fff}
  .nav-oge.secili{background:#2b2b2b;color:#fff;font-weight:600}
  .nav-ikon{width:18px;text-align:center;opacity:.85}
  .nav-alt{margin-top:auto;padding-top:12px;border-top:1px solid #333;display:flex;flex-direction:column;gap:4px}
  .nav-btn-ayar{background:#262626;color:#e3dfd7;border:1px solid #444;border-radius:6px;padding:6px 10px;font-size:12px;cursor:pointer;text-align:left;width:100%}
  .nav-btn-ayar:hover{background:#333;color:#fff}
  .nav-alt a{color:#8f8a83;font-size:12px;text-decoration:none}
  .nav-alt a:hover{color:#fff}
  body{padding-left:220px}
  .ust-bar,.baslik-satir,.filtreler,main,.lejant{margin-left:0}
  @media (max-width:900px){.yan-menu{width:64px}.nav-marka b,.nav-oge,.nav-alt{display:none}body{padding-left:64px}}
  `;
  document.head.appendChild(stil);

  // Global Fonksiyonlar
  const MODEL_VARSAYILANLARI = {
    claude: {model:"claude-sonnet-5-5", url:"https://api.anthropic.com/v1/messages"},
    ollama: {model:"llama3:latest", url:"http://localhost:11434/v1/chat/completions"},
    demo: {model:"yerel-kural-motoru", url:""}
  };

  // P1: sağlayıcının canlı /v1/models listesini çekip model kutusunu doldurur
  window.zekaiModelleriGetir = async function(){
    const kutu = document.getElementById("zm-kesif-sonuc");
    kutu.textContent = "⏳ Modeller çekiliyor...";
    const saglayici = document.getElementById("zm-saglayici").value;
    const key = document.getElementById("zm-key").value.trim();
    const url = document.getElementById("zm-url").value.trim();
    try {
      const r = await fetch("/api/ayarlar/modelleri-getir", {method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({saglayici, api_key: key, base_url: url})});
      const d = await r.json();
      const liste = d.modeller || [];
      const dl = document.getElementById("zm-model-liste");
      dl.innerHTML = liste.map(m=>`<option value="${m}">`).join("");
      kutu.textContent = d.hata ? ("✗ " + d.hata) : ("✓ " + d.adet + " model bulundu — kutuya yazarken listeden seçebilirsiniz");
      kutu.style.color = d.hata ? "var(--kirmizi)" : "var(--yesil)";
    } catch(err){
      kutu.textContent = "✗ " + err.message;
    }
  };

  window.zekaiSaglayiciDegisti = function(s){
    const d = MODEL_VARSAYILANLARI[s] || {};
    document.getElementById("zm-model").value = d.model || "";
    document.getElementById("zm-url").value = d.url || "";
    const keyAlan = document.getElementById("zm-key-alan");
    if(s === "ollama" || s === "demo"){
      keyAlan.style.display = "none";
    } else {
      keyAlan.style.display = "block";
    }
  };

  window.zekaiModelAyarAc = async function(){
    try {
      const res = await fetch("/api/ayarlar/model");
      const a = await res.json();
      document.getElementById("zm-saglayici").value = a.saglayici;
      document.getElementById("zm-model").value = a.model;
      document.getElementById("zm-url").value = a.base_url || "";
      document.getElementById("zm-key-durum").textContent = a.api_key_mevcut ? `(Mevcut: ${a.api_key_maskeli})` : "(Tanımlı değil)";
      window.zekaiSaglayiciDegisti(a.saglayici);
      document.getElementById("zm-test-sonuc").style.display = "none";
      document.getElementById("zekai-model-modal").classList.add("acik");
    } catch(err){
      alert("Ayar yükleme hatası: " + err.message);
    }
  };

  window.zekaiModelKaydet = async function(){
    const saglayici = document.getElementById("zm-saglayici").value;
    const model = document.getElementById("zm-model").value.trim();
    const key = document.getElementById("zm-key").value.trim();
    const url = document.getElementById("zm-url").value.trim();

    try {
      const res = await fetch("/api/ayarlar/model", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({saglayici, model, api_key: key || undefined, base_url: url || undefined})
      });
      const d = await res.json();
      alert(`Model ayarları güncellendi! Aktif: ${d.ayarlar.saglayici.toUpperCase()} (${d.ayarlar.model})`);
      document.getElementById("zekai-model-modal").classList.remove("acik");
    } catch(err){
      alert("Kayıt hatası: " + err.message);
    }
  };

  window.zekaiModelTest = async function(){
    const saglayici = document.getElementById("zm-saglayici").value;
    const model = document.getElementById("zm-model").value.trim();
    const key = document.getElementById("zm-key").value.trim();
    const url = document.getElementById("zm-url").value.trim();

    const kutu = document.getElementById("zm-test-sonuc");
    kutu.style.display = "block";
    kutu.style.background = "var(--gri-zemin)";
    kutu.style.color = "var(--metin)";
    kutu.textContent = "⏳ Model bağlantısı test ediliyor...";

    try {
      const res = await fetch("/api/ayarlar/model-test", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({saglayici, model, api_key: key, base_url: url})
      });
      const d = await res.json();
      if(d.durum === "ok"){
        kutu.style.background = "var(--yesil-zemin)";
        kutu.style.color = "var(--yesil)";
        kutu.textContent = "✓ " + d.mesaj;
      } else {
        kutu.style.background = "var(--kirmizi-zemin)";
        kutu.style.color = "var(--kirmizi)";
        kutu.textContent = "✗ " + d.mesaj;
      }
    } catch(err){
      kutu.style.background = "var(--kirmizi-zemin)";
      kutu.style.color = "var(--kirmizi)";
      kutu.textContent = "✗ Test hatası: " + err.message;
    }
  };
})();

  window.zekaiMaliyetOnayDegisti = function(onaylandi){
    const inp = document.getElementById("zm-key");
    if(!inp) return;
    inp.disabled = !onaylandi;
    inp.style.background = onaylandi ? "#fff" : "#f4f4f5";
    inp.placeholder = onaylandi ? "sk-ant-... (veya OpenAI/DeepSeek anahtarı)" : "Yukarıdaki harcama onayını işaretlemeden açılamaz";
  };
