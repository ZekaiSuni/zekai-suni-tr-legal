/* P3: Horizon-scan tarzı yatay zaman çizelgesi — yargı kulvarları + etki renkleri.
   mevzuat.html bunu yükler; ciz() içinde zamanCizelgesiCiz(filtreli kayıtlar) çağrılır. */
const ETKI_RENK = {"Yüksek":"#b3261e","Orta":"#c79100","Düşük":"var(--ikinci)"};
const AYLAR_TR = ["Oca","Şub","Mar","Nis","May","Haz","Tem","Ağu","Eyl","Eki","Kas","Ara"];

function zamanCizelgesiCiz(kayitlar){
  const alan = document.getElementById("zaman-alan");
  if(!alan || !kayitlar.length){ if(alan) alan.innerHTML=""; return; }
  const tarihli = kayitlar.filter(k=>k.gecer_tarihi);
  if(!tarihli.length){ alan.innerHTML = '<div class="alinti-kaynak">Tarihli gelişme yok — "Henüz tarihsiz" kayıtlar listeye bakar.</div>'; return; }

  const tarihDegerleri = tarihli.map(k=>new Date(k.gecer_tarihi));
  let min = new Date(Math.min(...tarihDegerleri)); min.setDate(min.getDate()-20);
  let max = new Date(Math.max(...tarihDegerleri)); max.setMonth(max.getMonth()+1);
  const bugun = new Date();
  const b90 = new Date(bugun.getTime() + 90*86400000);
  const toplam = (max - min) || 1;
  const pos = d => Math.max(0, Math.min(100, ((d - min)/toplam)*100));

  const yargilar = [...new Set(tarihli.map(k=>k.kaynak))];

  const kulvarSatirlar = yargilar.map(y=>{
    const satirlar = tarihli.filter(k=>k.kaynak===y);
    const noktalar = satirlar.map(k=>{
      const d = new Date(k.gecer_tarihi);
      const renk = k.etki==="Yüksek" ? "var(--kirmizi)" : k.etki==="Orta" ? "#c79100" : "var(--ikinci)";
      const gecikti = d < bugun;
      return `<div class="zc-nokta" style="left:${pos(d)}%;background:${renk}"
        title="${esc(k.baslik)}\n${trTarih(k.gecer_tarihi)} · ${k.etki}"></div>`;
    }).join("");
    return `<div class="zc-kulvar"><span class="zc-kulvar-ad">${esc(y)}</span>
      <div class="zc-cizgi">${noktalar}</div></div>`;
  }).join("");

  const ayIsaretleri = (()=>{
    let cik = ""; const d = new Date(min);
    while(d < max){
      cik += `<div class="zc-ay" style="left:${pos(d)}%">${AYLAR_TR[d.getMonth()]} ${String(d.getFullYear()).slice(2)}</div>`;
      d.setMonth(d.getMonth()+1);
    }
    return cik;
  })();

  const b90pos = pos(b90);
  alan.innerHTML = `
    <div class="zc-kapsul">
      <div class="zc-ust">${ayIsaretleri}
        <div class="zc-bugun-cizgi" style="left:${pos(bugun)}%"></div>
        <div class="zc-bugun-eticik" style="left:${pos(bugun)}%">Bugün</div>
        <div class="zc-band90" style="left:${pos(bugun)}%;width:${b90pos - pos(bugun)}%"></div>
      </div>
      ${kulvarSatirlar}
      <div class="zc-lejant">
        <span><i class="nokta" style="background:var(--kirmizi)"></i> Yüksek</span>
        <span><i class="nokta" style="background:#c79100"></i> Orta</span>
        <span><i class="nokta" style="background:var(--ikinci)"></i> Düşük/Bilinmeyen</span>
        <span class="zc-not">nokta = yürürlük tarihi · dikey çizgi = bugün · gölgeli bant = önümüzdeki 90 gün</span>
      </div>
    </div>`;
}
