/* İhbar Takvimi — arayüz katmanı */
let VERI = null;
let SECILI = null;
let SAHIP_FILTRE = false, INCELEME_FILTRE = false;

const GUN_ADLAR = ["Paz", "Pzt", "Sal", "Çar", "Per", "Cum", "Cmt"];
const AY_ADLAR = ["Oca","Şub","Mar","Nis","May","Haz","Tem","Ağu","Eyl","Eki","Kas","Ara"];

function trTarih(iso){ if(!iso) return "—"; const d=new Date(iso+"T00:00:00"); return `${d.getDate()} ${AY_ADLAR[d.getMonth()]} ${d.getFullYear()}`; }
function gunAdi(iso){ const d=new Date(iso+"T00:00:00"); return GUN_ADLAR[d.getDay()]; }

async function yukle(){
  const r = await fetch("/api/sozlesmeler");
  VERI = await r.json();
  ciz();
}

function ciz(){
  const o = VERI.ozet;
  // P4: ORTAK zaman ekseni — tüm satırlar aynı cetvelde hizalanır (Claude sadakati)
  let gBas = null, gSon = null;
  for(const k of VERI.kayitlar){
    const b = k.takvim.band;
    for(const anahtar of ["pencere_bas","pencere_son","uzarsa_son"]){
      if(!b[anahtar]) continue;
      const d = new Date(b[anahtar]);
      if(!gBas || d < gBas) gBas = d;
      if(!gSon || d > gSon) gSon = d;
    }
  }
  if(gBas && gSon){
    gBas = new Date(gBas.getTime() - 15*86400000);
    gSon = new Date(gSon.getTime() + 45*86400000);
  }
  window.__gEksen = (gBas && gSon) ? {bas:gBas, son:gSon} : null;
  document.getElementById("ozet-satiri").innerHTML =
    `${o.sozlesme_sayisi} sözleşme · <b class="${o.acik_ihbar_penceresi?'kirmizi':''}">${o.acik_ihbar_penceresi} ihbar penceresi açık</b> · ${o.geciken} geciken · ${o.inceleme_gerekli} inceleme bekliyor`;
  const fc = document.getElementById("fiyat-chipi");
  if(fc) fc.remove();
  const oc = document.getElementById("ornek-cipi");
  if(oc) oc.style.display = o.ornek_veri_var ? "" : "none";
  const fs = document.getElementById("f-sahipsiz");
  if(fs) fs.innerHTML = `Sahipsiz <b>${VERI.kayitlar.filter(k=>!k.sozlesme.sahibi).length}</b>`;
  const fi = document.getElementById("f-inceleme");
  if(fi) fi.innerHTML = `İnceleme gerekli <b>${o.inceleme_gerekli}</b>`;

  const ara = document.getElementById("ara").value.toLowerCase();
  const liste = document.getElementById("liste");
  liste.innerHTML = "";
  cetvelBaslikEkle(liste);
  for(const k of VERI.kayitlar){
    const s = k.sozlesme, t = k.takvim;
    if(ara && !(`${s.ad} ${s.karsi_taraf}`.toLowerCase().includes(ara))) continue;
    if(SAHIP_FILTRE && s.sahibi) continue;
    if(INCELEME_FILTRE && !s.inceleme) continue;
    liste.appendChild(satirCiz(k));
  }
}

function cetvelBaslikEkle(liste){
  if(!window.__gEksen || !VERI.kayitlar.length) return;
  const {bas, son} = window.__gEksen;
  const toplam = (son - bas) || 1;
  // ay sınırlarını işaretle
  let isaretler = [];
  const d = new Date(bas); d.setDate(1); d.setMonth(d.getMonth()+1); // sonraki ay başı
  let sonEtiketPos = -100;
  while(d < son){
    const p = ((d-bas)/toplam)*100;
    // etiketler sıkışmasın: en az %6 aralık
    if(p - sonEtiketPos >= 6){
      isaretler.push({pos: p, ad: AYLAR[d.getMonth()] + (d.getMonth()===0 ? " " + d.getFullYear().toString().slice(2) : "")});
      sonEtiketPos = p;
    }
    d.setMonth(d.getMonth()+1);
  }
  const bugunPos = ((new Date() - bas)/toplam)*100;
  const cetvel = document.createElement("div");
  cetvel.className = "sozlesme-satir cetvel-bas";
  cetvel.style.gridTemplateColumns = "230px 1fr 240px 150px";
  cetvel.innerHTML = `<div></div><div class="bant-alan cetvel-eksen">
    ${isaretler.map(i=>`<div class="cetvel-isaret" style="left:${i.pos}%">${i.ad}</div>`).join("")}
    <div class="bugun-cizgi" style="left:${bugunPos}%"></div><div class="bugun-eticik" style="left:${bugunPos}%">Bugün</div>
  </div><div></div><div></div>`;
  liste.appendChild(cetvel);
}

function satirCiz(k){
  const s = k.sozlesme, t = k.takvim;
  const div = document.createElement("div");
  div.className = "sozlesme-satir";

  // Bant koordinatları
  let bantlar = "";
  if(t.band.pencere_bas && t.band.pencere_son && window.__gEksen){
    const bas = window.__gEksen.bas, son = window.__gEksen.son;
    const toplam = (son-bas) || 1;
    const pos = d => Math.max(0, Math.min(100, ((new Date(d)-bas)/toplam)*100));
    if(t.band.donem_bas && t.band.donem_son)
      bantlar += `<div class="bant donem" style="left:${pos(t.band.donem_bas)}%;width:${pos(t.band.donem_son)-pos(t.band.donem_bas)}%" title="Dönem"></div>`;
    if(t.band.ihbar_gunu && t.band.donem_son)
      bantlar += `<div class="bant ihbar" style="left:${pos(t.band.ihbar_gunu)}%;width:${Math.max(0.5,pos(t.band.donem_son)-pos(t.band.ihbar_gunu))}%" title="İhbar penceresi"></div>`;
    if(t.band.uzarsa_son)
      bantlar += `<div class="bant uzarsa" style="left:${pos(t.band.donem_son)}%;width:${Math.max(0.5,pos(t.band.uzarsa_son)-pos(t.band.donem_son))}%" title="Uzarsa"></div>`;
    if(t.rozet === "Kaçtı" && t.band.ihbar_gunu)
      bantlar += `<div class="bant gec" style="left:${pos(t.band.ihbar_gunu)}%;width:${Math.max(0.5,pos(t.band.bugun)-pos(t.band.ihbar_gunu))}%" title="İhbar penceresi kaçtı"></div>`;
    bantlar += `<div class="son-gun-cizgi" style="left:${pos(t.band.ihbar_gunu)}%" title="Son ihbar günü"></div>`;
    bantlar += `<div class="bugun-cizgi" style="left:${pos(t.band.bugun)}%"></div><div class="bugun-eticik" style="left:${pos(t.band.bugun)}%">Bugün</div>`;
  }

  // Rozetler
  const rozetler = [];
  if(s.inceleme) rozetler.push(`<span class="mini-cipy mini-inceleme">İnceleme</span>`);
  if(s.duzeltilmis) rozetler.push(`<span class="mini-cipy mini-duzeltildi">Düzeltildi</span>`);
  if(s.cikarim_yontemi === "demo") rozetler.push(`<span class="mini-cipy cikarim-demo">demo çıkarımı</span>`);
  if(s.cikarim_yontemi === "claude") rozetler.push(`<span class="mini-cipy cikarim-claude">Claude</span>`);
  if(s.sahibi) rozetler.push(`<span class="mini-cipy mini-sahip">${esc(s.sahibi)}</span>`);

  div.innerHTML = `
    <div>
      <div class="s-ad">${esc(s.ad)}</div>
      <div class="s-alt">${esc(s.tur)} · ${esc(s.karsi_taraf || "—")}${s.fiyat_yillik?` · ₺${s.fiyat_yillik.toLocaleString("tr-TR")}/yıl`:""}</div>
      <div class="s-rozetler">${rozetler.join("")}</div>
    </div>
    <div class="bant-alan">${bantlar}</div>
    <div class="s-islem">
      <div style="font-weight:600;color:var(--metin)">Kimse işlem yapmazsa</div>
      ${esc(t.kimse_islem_yapmazsa || "—")}
    </div>
    <div class="s-son-gun">
      <div class="deger">${t.son_ihbar_tarihi ? trTarih(t.son_ihbar_tarihi) : "Belirsiz"}</div>
      <div style="font-size:11px;color:var(--ikinci);margin:2px 0 5px">${t.son_ihbar_tarihi ? gunAdi(t.son_ihbar_tarihi) : ""}</div>
      <span class="rozet ${t.rozet_turu}">${t.rozet}</span>
    </div>`;
  div.addEventListener("click", () => detayAc(s.id));
  return div;
}

async function detayAc(id){
  const r = await fetch(`/api/sozlesmeler/${id}`);
  if(!r.ok) return;
  const d = await r.json();
  const s = d.sozlesme, t = d.takvim;
  SECILI = id;
  document.getElementById("d-karsi-taraf").textContent = `${s.tur} · ${s.karsi_taraf || "—"}`;
  document.getElementById("d-ad").textContent = s.ad;
  const roset = s.duzeltilmis ? `<span class="rozet yesil">Düzeltildi</span> ` : "";
  const ihbarMetni = s.ihbar_deger ? `${s.ihbar_deger} ${s.ihbar_birim}` : "Bulunamadı";

  let alinti = "—";
  if(d.kaynak_alinti){
    alinti = `<div class="alinti-kutu">"${esc(d.kaynak_alinti)}"</div>
      <div class="alinti-kaynak">m. ${esc(s.kaynak_madde || "—")} · s. ${esc(s.kaynak_sayfa || "—")} · ${esc(s.kaynak_dosya || "kaynak dosya yok")} ·
      <a title="Kaynak dosya sunucuda saklanmıyor; orijinal belgeyi dosya deposunda açın">Sözleşmede göster ↗</a></div>`;
  } else {
    alinti = `<div class="alinti-kutu" style="color:var(--ikinci)">Bulunamadı — bu sözleşme için alıntı kaydedilmemiş. <span class="alinti-kaynak">Arama kapsamı: sözleşme metnindeki uzatma ve bildirim kalıpları.</span></div>`;
  }

  const notlar = (t.hukuki_notlar || []).map(n=>`<div class="not-kutu">${esc(n)}</div>`).join("");
  const cikarimCipi = s.cikarim_yontemi === "demo"
    ? `<span class="cikarim-cipi cikarim-demo">demo çıkarımı — doğrulayın</span>`
    : (s.cikarim_yontemi === "claude" ? `<span class="cikarim-cipi cikarim-claude">Claude çıkarımı</span>` : "");

  document.getElementById("d-icerik").innerHTML = `
    <div class="bolum">
      ${roset}<span class="rozet ${t.rozet_turu}">${t.rozet}</span> ${cikarimCipi}
      <div style="margin-top:10px;font-size:13px;line-height:1.7">
        <div><b>Dönem:</b> ${trTarih(t.donem_baslangici)} – ${trTarih(t.donem_bitisi)}</div>
        <div><b>Otomatik uzatma:</b> ${s.otomatik_uzatma ? `Evet — ${s.uzatma_suresi_ay || s.sure_ay} ay${s.uzatma_artis_yuzdesi?` · %${s.uzatma_artis_yuzdesi} artış`:""}` : "Hayır"}</div>
        <div><b>İhbar süresi:</b> ${ihbarMetni} · <b>Şekli:</b> ${s.ihbar_sekli || "Belirsiz"}</div>
        <div><b>Son ihbar günü:</b> ${trTarih(t.son_ihbar_tarihi)}${t.son_ihbar_tarihi?` (${gunAdi(t.son_ihbar_tarihi)})`:""}</div>
        ${t.kimse_islem_yapmazsa?`<div><b>Kimse işlem yapmazsa:</b> ${esc(t.kimse_islem_yapmazsa)}</div>`:""}
      </div>
    </div>
    ${notlar ? `<div class="bolum"><div class="bolum-bas">Hukuki notlar</div>${notlar}</div>` : ""}
    <div class="bolum">
      <div class="bolum-bas">Sözleşmedeki ifade</div>
      ${alinti}
    </div>
    <div class="bolum">
      <div class="bolum-bas">Karar</div>
      <div class="karar-butonlar">
        ${["İhbar gönderildi","Yenilensin","Feshedilsin"].map(kr=>
          `<button class="${s.karar===kr?"secili":""}" data-karar="${kr}" onclick="kararVer('${kr}')">${kr}</button>`).join("")}
      </div>
      ${s.karar_tarihi ? `<div style="font-size:12px;color:var(--ikinci)">Karar tarihi: ${trTarih(s.karar_tarihi)}${s.kararin_kimi?` · ${s.kararin_kimi}`:""}</div>`:""}
    </div>
    <div class="bolum">
      <div class="bolum-bas">Bilgileri düzelt (Claude'ın çıkarımına itiraz edebilirsiniz)</div>
      <div class="form-grid">
        <label>İhbar süresi<input id="f-ihbar-deger" type="number" value="${s.ihbar_deger||""}"></label>
        <label>Birim<select id="f-ihbar-birim">${["gün","hafta","ay"].map(b=>`<option ${s.ihbar_birim===b?"selected":""}>${b}</option>`).join("")}</select></label>
        <label>İhbar şekli<select id="f-ihbar-sekli">${["Yazılı","Noter","KEP"].map(b=>`<option ${s.ihbar_sekli===b?"selected":""}>${b}</option>`).join("")}</label>
        <label>Süre (ay)<input id="f-sure" type="number" value="${s.sure_ay||""}"></label>
        <label class="sec"><input id="f-uzatma" type="checkbox" ${s.otomatik_uzatma?"checked":""}> Otomatik uzatma</label>
        <label>Sahibi<input id="f-sahibi" value="${esc(s.sahibi||"")}"></label>
      </div>
      <button class="birincil" onclick="duzeltKaydet()">Düzeltmeyi kaydet</button>
    </div>
    <div class="bolum">
      <div class="bolum-bas">Claude için notlar (istemle birlikte kopyalanır)</div>
      <textarea id="f-notlar" style="width:100%;min-height:60px;border:1px solid var(--cizgi);border-radius:8px;padding:8px;font-size:13px">${esc(s.notlar||"")}</textarea>
      <div style="margin-top:6px"><button class="ikincil" onclick="notKaydet()">Notu kaydet</button></div>
    </div>`;
  document.getElementById("cekmecem").classList.remove("gizli");
}

async function kararVer(karar){
  const kimi = prompt("Kararı veren (ad/rol) — kayda geçer:", "Hukuk · ");
  if(kimi === null) return;
  await fetch(`/api/sozlesmeler/${SECILI}/guncelle`, {method:"POST", headers:{"Content-Type":"application/json"},
    body: JSON.stringify({karar, kararin_kimi: kimi || "Hukuk"})});
  yukle(); detayAc(SECILI);
}

async function duzeltKaydet(){
  const govde = {
    ihbar_deger: parseInt(document.getElementById("f-ihbar-deger").value) || null,
    ihbar_birim: document.getElementById("f-ihbar-birim").value,
    ihbar_sekli: document.getElementById("f-ihbar-sekli").value,
    sure_ay: parseInt(document.getElementById("f-sure").value) || null,
    otomatik_uzatma: document.getElementById("f-uzatma").checked,
    sahibi: document.getElementById("f-sahibi").value,
  };
  await fetch(`/api/sozlesmeler/${SECILI}/guncelle`, {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(govde)});
  yukle(); detayAc(SECILI);
}

async function notKaydet(){
  await fetch(`/api/sozlesmeler/${SECILI}/guncelle`, {method:"POST", headers:{"Content-Type":"application/json"},
    body: JSON.stringify({notlar: document.getElementById("f-notlar").value})});
}

// ---------------------------------------------------------- ekle + analiz

async function dosyaSecildi(){
  const f = document.getElementById("e-dosya").files[0];
  if(!f) return;
  const kutu = document.getElementById("e-analiz");
  kutu.innerHTML = "Analiz ediliyor…";
  const fd = new FormData(); fd.append("dosya", f);
  const r = await fetch("/api/analiz", {method:"POST", body: fd});
  if(!r.ok){ kutu.innerHTML = `<div class="uyari">Analiz başarısız: ${await r.text()}</div>`; return; }
  const d = await r.json();
  window.__analiz = d;
  // Formu doldur (found = doldur, not found = boş bırak + dürüst not)
  document.getElementById("e-ad").value = d.ad !== "Bulunamadı" ? d.ad : f.name.replace(/\.(pdf|docx|txt)$/i,"");
  document.getElementById("e-karsi").value = d.karsi_taraf !== "Bulunamadı" ? d.karsi_taraf : "";
  if(d.baslangic) document.getElementById("e-baslangic").value = d.baslangic;
  if(d.sure_ay) document.getElementById("e-sure").value = d.sure_ay;
  document.getElementById("e-uzatma").checked = !!d.otomatik_uzatma;
  if(d.uzatma_suresi_ay) document.getElementById("e-uzatma-sure").value = d.uzatma_suresi_ay;
  if(d.uzatma_artis_yuzdesi) document.getElementById("e-artis").value = d.uzatma_artis_yuzdesi;
  if(d.ihbar_deger) document.getElementById("e-ihbar-deger").value = d.ihbar_deger;
  if(d.ihbar_birim) document.getElementById("e-ihbar-birim").value = d.ihbar_birim;
  if(d.ihbar_sekli) document.getElementById("e-ihbar-sekli").value = d.ihbar_sekli;

  const kapsam = (d.arama_kapsami||[]).map(x=>`<li>${x}</li>`).join("");
  kutu.innerHTML = `
    <div class="alinti">
      <div class="baslik">ÇIKARIM: ${d.cikarim_yontemi === "claude" ? "CLAUDE ("+(d.model||"")+")" : "DEMO (kalıp eşleme)"}</div>
      ${d.cikarim_notu ? `<div style="margin-bottom:6px;color:var(--sari)">${esc(d.cikarim_notu)}</div>` : ""}
      <div><b>Otomatik uzatma:</b> ${d.otomatik_uzatma === null ? "Bulunamadı" : (d.otomatik_uzatma ? "Evet" : "Hayır")}</div>
      <div><b>İhbar süresi:</b> ${d.ihbar_deger ? d.ihbar_deger+" "+d.ihbar_birim : "Bulunamadı"}</div>
      <div><b>İhbar şekli:</b> ${d.ihbar_sekli || "Bulunamadı"}</div>
      <div><b>Süre:</b> ${d.sure_ay ? d.sure_ay+" ay" : "Bulunamadı"}</div>
      ${d.kaynak_alinti ? `<div style="margin-top:6px;font-style:italic">"${esc(d.kaynak_alinti)}"</div><div class="alinti-kaynak">m. ${d.kaynak_madde||"—"}</div>` : ""}
      ${kapsam ? `<div class="alinti-kaynak" style="margin-top:6px"><b>Arama kapsamı:</b><ul style="margin:4px 0 0;padding-left:18px">${kapsam}</ul></div>` : ""}
    </div>`;
  document.getElementById("e-alinti").classList.remove("gizli");
}

async function ekleKaydet(){
  const a = window.__analiz || {};
  const govde = {
    ad: document.getElementById("e-ad").value || "Adsız sözleşme",
    karsi_taraf: document.getElementById("e-karsi").value,
    tur: document.getElementById("e-tur").value,
    baslangic: document.getElementById("e-baslangic").value || null,
    sure_ay: parseInt(document.getElementById("e-sure").value) || null,
    otomatik_uzatma: document.getElementById("e-uzatma").checked,
    uzatma_suresi_ay: parseInt(document.getElementById("e-uzatma-sure").value) || null,
    uzatma_artis_yuzdesi: parseFloat(document.getElementById("e-artis").value) || null,
    ihbar_deger: parseInt(document.getElementById("e-ihbar-deger").value) || null,
    ihbar_birim: document.getElementById("e-ihbar-deger").value ? document.getElementById("e-ihbar-birim").value : null,
    ihbar_sekli: document.getElementById("e-ihbar-deger").value ? document.getElementById("e-ihbar-sekli").value : null,
    fiyat_yillik: parseFloat(document.getElementById("e-fiyat").value) || null,
    kaynak_alinti: a.kaynak_alinti || "", kaynak_madde: a.kaynak_madde || "",
    kaynak_sayfa: a.kaynak_sayfa || "", kaynak_dosya: document.getElementById("e-dosya").files[0]?.name || a.kaynak_dosya || "",
    cikarim_yontemi: a.cikarim_yontemi || "elle",
    notlar: a.cikarim_notu || "",
  };
  const r = await fetch("/api/sozlesmeler/ekle", {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(govde)});
  if(r.ok){ modalKapat(); yukle(); }
  else alert("Kaydedilemedi: " + await r.text());
}

// ---------------------------------------------------------- tatiller

async function tatilAc(){
  const r = await fetch("/api/tatiller");
  const d = await r.json();
  document.getElementById("t-liste").innerHTML =
    d.tatiller.map(t=>`<li><b>${trTarih(t.tarih)}</b> (${gunAdi(t.tarih)}) — ${t.ad}${t.tur==="yarim"?" ⏲":""}</li>`).join("");
  document.getElementById("t-yaklasik").textContent = d.yaklasik_not;
  document.getElementById("tatil-modal").classList.add("acik");
}

function modalKapat(){
  document.getElementById("ekle-modal").classList.remove("acik");
  document.getElementById("tatil-modal").classList.remove("acik");
  document.getElementById("cekmecem").classList.add("gizli");
}

// ---------------------------------------------------------- olaylar

document.getElementById("btn-ekle").addEventListener("click", () => document.getElementById("ekle-modal").classList.add("acik"));
document.getElementById("e-kapat").addEventListener("click", modalKapat);
document.getElementById("btn-tatiller").addEventListener("click", tatilAc);
document.getElementById("t-kapat").addEventListener("click", modalKapat);
document.getElementById("d-kapat").addEventListener("click", () => document.getElementById("cekmecem").classList.add("gizli"));
document.getElementById("e-dosya").addEventListener("change", dosyaSecildi);
document.getElementById("e-kaydet").addEventListener("click", ekleKaydet);
document.getElementById("btn-ics").addEventListener("click", ()=>location.href="/api/export.ics");
document.getElementById("btn-csv").addEventListener("click", ()=>location.href="/api/export.csv");
document.getElementById("btn-json").addEventListener("click", ()=>location.href="/api/export.json");
document.getElementById("ara").addEventListener("input", ciz);
document.getElementById("f-sahipsiz").addEventListener("click", e => { SAHIP_FILTRE=!SAHIP_FILTRE; e.currentTarget.classList.toggle("secili"); ciz(); });
document.getElementById("f-inceleme").addEventListener("click", e => { INCELEME_FILTRE=!INCELEME_FILTRE; e.currentTarget.classList.toggle("secili"); ciz(); });

yukle();
