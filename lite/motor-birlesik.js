/* Zekai Suni — DETERMİNİSTİK SÜRE MOTORU (JavaScript portu)
   Python kaynağı: app/sure_motoru.py + app/tatiller.py — birebir port.
   Hukuki dayanak: TBK m. 89-93/347, MK m. 12-14, TTK m. 18/3, 2429 sK. */
(function(g){
"use strict";

const TAM_TATILLER = {
  2025: [[1,1],[3,30],[3,31],[4,1],[4,23],[5,1],[5,19],[6,6],[6,7],[6,8],[6,9],[7,15],[8,30],[10,29]],
  2026: [[1,1],[3,20],[3,21],[3,22],[4,23],[5,1],[5,19],[5,27],[5,28],[5,29],[5,30],[7,15],[8,30],[10,29]],
  2027: [[1,1],[3,9],[3,10],[3,11],[4,23],[5,1],[5,19],[5,16],[5,17],[5,18],[7,15],[8,30],[10,29]],
  2028: [[1,1],[4,23],[5,1],[5,19],[7,15],[8,30],[10,29]],
  2029: [[1,1],[4,23],[5,1],[5,19],[7,15],[8,30],[10,29]],
  2030: [[1,1],[4,23],[5,1],[5,19],[7,15],[8,30],[10,29]],
};
const YARIM_TATILLER = { 2026: [[3,19],[5,26]], 2027: [[3,8]] };

const ADLAR = {
  "1/1":"Yılbaşı","23/4":"Ulusal Egemenlik ve Çocuk Bayramı","1/5":"Emek ve Dayanışma Günü",
  "19/5":"Atatürk'ü Anma, Gençlik ve Spor Bayramı","15/7":"Demokrasi ve Millî Birlik Günü",
  "30/8":"Zafer Bayramı","29/10":"Cumhuriyet Bayramı",
  "19/3":"Ramazan Bayramı Arifesi (yarım gün)","20/3":"Ramazan Bayramı 1. gün",
  "21/3":"Ramazan Bayramı 2. gün","22/3":"Ramazan Bayramı 3. gün",
  "8/3":"Ramazan Bayramı Arifesi (yarım gün)","9/3":"Ramazan Bayramı 1. gün",
  "10/3":"Ramazan Bayramı 2. gün","11/3":"Ramazan Bayramı 3. gün",
  "26/5":"Kurban Bayramı Arifesi (yarım gün)","27/5":"Kurban Bayramı 1. gün",
  "28/5":"Kurban Bayramı 2. gün","29/5":"Kurban Bayramı 3. gün","30/5":"Kurban Bayramı 4. gün",
  "30/3":"Ramazan Bayramı 1. gün (2025)","31/3":"Ramazan Bayramı 2. gün (2025)",
  "1/4":"Ramazan Bayramı 3. gün (2025)",
  "6/6":"Kurban Bayramı 1. gün (2025)","7/6":"Kurban Bayramı 2. gün (2025)",
  "8/6":"Kurban Bayramı 3. gün (2025)","9/6":"Kurban Bayramı 4. gün (2025)",
};

function D(y,m,dd){ return new Date(Date.UTC(y, m-1, dd)); }
function iso(d){ return d.toISOString().slice(0,10); }

function tamTatilMi(d){
  const y = d.getUTCFullYear(), anahtar = d.getUTCMonth()+1 + "/" + d.getUTCDate();
  return (TAM_TATILLER[y]||[]).some(x => x[0]===d.getUTCMonth()+1 && x[1]===d.getUTCDate());
}
function yarimTatilMi(d){
  const y = d.getUTCFullYear(), anahtar = d.getUTCMonth()+1 + "/" + d.getUTCDate();
  return (YARIM_TATILLER[y]||[]).some(x => x[0]===d.getUTCMonth()+1 && x[1]===d.getUTCDate());
}
function haftaSonuMu(d){ const w = d.getUTCDay(); return w===0 || w===6; }
function isGunuMu(d){ return !haftaSonuMu(d) && !tamTatilMi(d); }
function izleyenIsGunu(d){
  let k = new Date(d.getTime() + 86400000);
  while(!isGunuMu(k)) k = new Date(k.getTime() + 86400000);
  return k;
}
function tatilAdi(d){
  if(haftaSonuMu(d)) return "Hafta sonu";
  if(!tamTatilMi(d)) return null;
  const anahtar = d.getUTCMonth()+1 + "/" + d.getUTCDate();
  return ADLAR[anahtar] || "Resmî tatil";
}

/* Ay ekleme: MK m. 12-14 — "ayın aynı günü"; ay taşırsa ayın son günü */
function ayEkle(baslangicUTC, aySayisi){
  const toplam = baslangicUTC.getUTCMonth() + aySayisi;
  const yil = baslangicUTC.getUTCFullYear() + Math.floor(toplam/12);
  const ay = (toplam % 12) + 1;
  const ayGunuSayisi = new Date(Date.UTC(yil, ay, 0)).getUTCDate();
  const gun = Math.min(baslangicUTC.getUTCDate(), ayGunuSayisi);
  return D(yil, ay, gun);
}
function ayGeri(bitisUTC, aySayisi){
  const toplam = bitisUTC.getUTCMonth() - aySayisi;
  const yil = bitisUTC.getUTCFullYear() + Math.floor(toplam/12);
  const ay = ((toplam % 12) + 12) % 12 + 1;
  const ayGunuSayisi = new Date(Date.UTC(yil, ay, 0)).getUTCDate();
  const gun = Math.min(bitisUTC.getUTCDate(), ayGunuSayisi);
  return D(yil, ay, gun);
}

/* Bugünü kapsayan dönem */
function mevcutDonem(baslangic, sureAy, otomatikUzatma, uzatmaAy, bugun){
  let bas = baslangic, bit = ayEkle(baslangic, sureAy);
  if(!otomatikUzatma) return [bas, bit];
  const adim = uzatmaAy || sureAy;
  let guvenlik = 0;
  while(bit < bugun && guvenlik < 100){ bas = bit; bit = ayEkle(bit, adim); guvenlik++; }
  return [bas, bit];
}
function sonIhbarGunu(donemBitisi, deger, birim){
  if(!deger) return null;
  if(birim === "gün") return new Date(donemBitisi.getTime() - deger*86400000);
  if(birim === "hafta") return new Date(donemBitisi.getTime() - deger*7*86400000);
  if(birim === "ay") return ayGeri(donemBitisi, deger);
  return null;
}

/* Ana hesap — s: {id, ad, karsi_taraf, tur, baslangic, sure_ay, otomatik_uzatma,
   uzatma_suresi_ay, uzatma_artis_yuzdesi, ihbar_deger, ihbar_birim, ihbar_sekli, karar}
   bugun: Date (UTC gece) */
function hesapla(s, bugun){
  bugun = bugun || new Date(new Date().toISOString().slice(0,10)+"T00:00:00Z");
  if(!s.baslangic){
    return { sozlesme_id:s.id, ad:s.ad, karsi_taraf:s.karsi_taraf||"", tur:s.tur||"",
      donem_baslangici:null, donem_bitisi:null, son_ihbar_tarihi:null,
      son_ihbar_tatil_mi:false, tatil_adi:null, onerilen_is_gunu:null, kalan_gun:null,
      rozet:"Tarih yok", rozet_turu:"gri", kimse_islem_yapmazsa:"—",
      hukuki_not:["Sözleşmenin başlangıç tarihi kayıtlı değil — hesap yapılmadı. Tarihi girin; motor hesabı deterministik olarak yapar."],
      band:{pencere_bas:null, pencere_son:null, bugun:iso(bugun)} };
  }
  const baslangic = D(
    +s.baslangic.slice(0,4), +s.baslangic.slice(5,7), +s.baslangic.slice(8,10));
  let donemBas, donemBit;
  if(s.sure_ay){
    const cift = mevcutDonem(baslangic, s.sure_ay, !!s.otomatik_uzatma, s.uzatma_suresi_ay, bugun);
    donemBas = cift[0]; donemBit = cift[1];
  } else { donemBas = baslangic; donemBit = null; }
  const sonIhbar = donemBit ? sonIhbarGunu(donemBit, s.ihbar_deger, s.ihbar_birim) : null;

  const h = { sozlesme_id:s.id, ad:s.ad, karsi_taraf:s.karsi_taraf||"", tur:s.tur||"",
    donem_baslangici:donemBas, donem_bitisi:donemBit, son_ihbar_tarihi:sonIhbar,
    son_ihbar_tatil_mi:false, tatil_adi:null, onerilen_is_gunu:null, kalan_gun:null,
    rozet:"Belirsiz", rozet_turu:"gri", kimse_islem_yapmazsa:"",
    hukuki_not:[], band:{} };

  if(sonIhbar){
    const kuruYarim = yarimTatilMi(sonIhbar);
    if(tamTatilMi(sonIhbar) || haftaSonuMu(sonIhbar) || kuruYarim){
      h.son_ihbar_tatil_mi = true;
      h.tatil_adi = haftaSonuMu(sonIhbar) ? "Hafta sonu"
        : (kuruYarim ? "Bayram arifesi (yarım gün)" : tatilAdi(sonIhbar));
      h.onerilen_is_gunu = izleyenIsGunu(sonIhbar);
      if(tamTatilMi(sonIhbar)){
        h.hukuki_not.push("Son ihbar günü (" + iso(sonIhbar) + ") resmî tatile denk geliyor"
          + (h.tatil_adi ? " (" + h.tatil_adi + ")" : "")
          + ". TBK m. 93 mütalaasıyla bildirimi " + iso(h.onerilen_is_gunu)
          + " (izleyen iş günü) yapmak düşünülebilir; ancak kesinlik için avukat onayı önerilir — tarih motoru otomatik değiştirmez.");
      }
      if(haftaSonuMu(sonIhbar)){
        h.hukuki_not.push("Son ihbar günü hafta sonuna denk geliyor. KEP (TTK m. 18/3) kesintisiz çalıştığı için bildirim hafta sonunda da yapılabilir; noter yolu tercih edilecekse " + iso(h.onerilen_is_gunu) + " (izleyen iş günü) değerlendirilebilir.");
      }
    }
    if(kuruYarim){
      h.hukuki_not.push("Son ihbar günü bayram arifesi (yarım gün) — kurumların kapanış saati erkenleyebilir; KEP gönderimi saat kısıtlamasına tabi değildir.");
    }
  }

  if(s.karar === "İhbar gönderildi"){
    h.rozet = "İhbar gönderildi"; h.rozet_turu = "yesil";
  } else if(sonIhbar && donemBit){
    const kalan = Math.round((sonIhbar - bugun)/86400000);
    h.kalan_gun = kalan;
    if(bugun > sonIhbar){
      if(bugun >= donemBit){ h.rozet="Dönem bitti"; h.rozet_turu="gri"; }
      else { h.rozet="Kaçtı"; h.rozet_turu="kirmizi"; }
    } else if(kalan <= 7){ h.rozet = kalan+" gün"; h.rozet_turu="kirmizi"; }
    else if(kalan <= 45){ h.rozet = kalan+" gün"; h.rozet_turu="sari"; }
    else { h.rozet = "— "+kalan+" gün"; h.rozet_turu="gri"; }
  } else {
    h.rozet = "Belirsiz"; h.rozet_turu = "gri";
    h.hukuki_not.push("İhbar süresi sözleşmeden çıkarılamadı — maddeleri kontrol edin. Çıkarım eksik olduğu için takvim hesabı yapılmadı (uydurma tarih yok).");
  }

  if(donemBit){
    h.hukuki_not.push("Dönem bitişi 'ayın aynı günü' kuralıyla hesaplandı (MK m. 13). Başlangıç gününün sayılıp sayılmayacağı yorumuna göre ±1 günlük fark olabilir — kritik ihbarlarda bir gün önce göndermek güvenli taraftır.");
  }

  if(s.otomatik_uzatma && donemBit){
    const artis = s.uzatma_artis_yuzdesi ? " · %" + s.uzatma_artis_yuzdesi + " artış" : "";
    h.kimse_islem_yapmazsa = trGun(ayEkle(donemBit, s.uzatma_suresi_ay || s.sure_ay)) + " tarihine kadar uzar" + artis;
  } else if(donemBit){
    h.kimse_islem_yapmazsa = trGun(donemBit) + " tarihinde sona erer (uzatma yok)";
  }

  if((s.tur||"").toLowerCase().indexOf("kira") === 0 && s.otomatik_uzatma){
    const gecenYil = Math.floor((bugun - baslangic)/ (365*86400000));
    if(gecenYil >= 10){
      h.hukuki_not.push("TBK m. 347/2: 10 yıllık uzama süresi dolmuş konut/çatılı işyeri kiralanmasında kiraya veren, her uzatma yılının sonuna doğru en az 3 ay önce yazılı fesih bildirimi yapabilir.");
    }
  }

  const gosterimBas = donemBas < bugun ? donemBas : bugun;
  h.band = {
    pencere_bas: iso(gosterimBas),
    pencere_son: donemBit ? iso(new Date(Math.max(donemBit.getTime(), bugun.getTime()) + 200*86400000)) : null,
    donem_bas: iso(donemBas),
    donem_son: donemBit ? iso(donemBit) : null,
    ihbar_gunu: sonIhbar ? iso(sonIhbar) : null,
    bugun: iso(bugun),
    uzarsa_son: (s.otomatik_uzatma && donemBit) ? iso(ayEkle(donemBit, s.uzatma_suresi_ay || s.sure_ay)) : null,
  };
  return h;
}

const AYLAR_TR = ["Oca","Şub","Mar","Nis","May","Haz","Tem","Ağu","Eyl","Eki","Kas","Ara"];
function trGun(d){ return String(d.getUTCDate()).padStart(2,"0") + " " + AYLAR_TR[d.getUTCMonth()] + " " + d.getUTCFullYear(); }

/* dışa aç */
g.motor = { ayEkle, ayGeri, mevcutDonem, sonIhbarGunu, hesapla, tamTatilMi, yarimTatilMi,
            haftaSonuMu, izleyenIsGunu, tatilAdi, isGunuMu, D, trGun };
})(typeof window !== "undefined" ? window : globalThis);
