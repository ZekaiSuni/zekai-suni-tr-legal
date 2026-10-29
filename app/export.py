"""Dışa aktarım: .ics takvim, CSV, JSON (versiyonlu format: zekai-ihbar-takvimi/v1)."""
from __future__ import annotations

import csv
import io
import json

from app.sure_motoru import hesapla


def ics_uret(kayitlar, bugun) -> str:
    satirlar = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Zekai Suni//Ihbar Takvimi//TR",
        "CALSCALE:GREGORIAN",
        "X-WR-CALNAME:Zekai İhbar Takvimi",
    ]
    for s in kayitlar:
        h = hesapla(s, bugun)
        if not h.son_ihbar_tarihi:
            continue
        d = h.son_ihbar_tarihi
        zaman = f"{d.year:04d}{d.month:02d}{d.day:02d}"
        ozet = f"[İhbar son günü] {s.ad} — {s.karsi_taraf}"
        aciklama = (
            f"Son ihbar tarihi. Şekil: {s.ihbar_sekli or 'Yazılı'}. "
            f"Kaynak: {s.kaynak_madde or '—'} {s.kaynak_dosya or ''}. "
            f"Zekai Suni ile hazırlanmıştır; hukuki görüş değildir."
        ).replace(",", "\\,").replace(";", "\\;")
        satirlar += [
            "BEGIN:VEVENT",
            f"UID:zekai-ihbar-{s.id}@zekai.local",
            f"DTSTAMP:{zaman}T090000Z",
            f"DTSTART;VALUE=DATE:{zaman}",
            f"SUMMARY:{ozet}",
            f"DESCRIPTION:{aciklama}",
            "BEGIN:VALARM", "TRIGGER:-P3D", "ACTION:DISPLAY",
            f"DESCRIPTION:{ozet[:60]}", "END:VALARM",
            "END:VEVENT",
        ]
        # Dönem bitişi (ikinci etkinlik)
        if h.donem_bitisi:
            d2 = h.donem_bitisi
            z2 = f"{d2.year:04d}{d2.month:02d}{d2.day:02d}"
            satirlar += [
                "BEGIN:VEVENT",
                f"UID:zekai-bitis-{s.id}@zekai.local",
                f"DTSTAMP:{z2}T090000Z",
                f"DTSTART;VALUE=DATE:{z2}",
                f"SUMMARY:[Dönem bitişi] {s.ad} — {h.kimse_islem_yapmazsa}",
                "END:VEVENT",
            ]
    satirlar.append("END:VCALENDAR")
    return "\r\n".join(satirlar)


def csv_uret(kayitlar, bugun) -> str:
    buf = io.StringIO()
    yazici = csv.writer(buf)
    yazici.writerow([
        "Sözleşme", "Karşı taraf", "Tür", "Dönem başlangıcı", "Dönem bitişi",
        "Otomatik uzatma", "Uzatma süresi (ay)", "İhbar süresi", "İhbar şekli",
        "Son ihbar tarihi", "Durum", "Kalangün", "Kimse işlem yapmazsa",
        "Kaynak madde", "Kaynak dosya", "Karar", "Notlar",
    ])
    for s in kayitlar:
        h = hesapla(s, bugun)
        ihbar_metni = f"{s.ihbar_deger} {s.ihbar_birim or ''}".strip() if s.ihbar_deger else "Bulunamadı"
        yazici.writerow([
            s.ad, s.karsi_taraf, s.tur,
            h.donem_baslangici.isoformat() if h.donem_baslangici else "",
            h.donem_bitisi.isoformat() if h.donem_bitisi else "",
            "Evet" if s.otomatik_uzatma else "Hayır",
            s.uzatma_suresi_ay or "", ihbar_metni, s.ihbar_sekli or "",
            h.son_ihbar_tarihi.isoformat() if h.son_ihbar_tarihi else "Hesaplanamadı",
            h.rozet, h.kalan_gun if h.kalan_gun is not None else "",
            h.kimse_islem_yapmazsa, s.kaynak_madde, s.kaynak_dosya,
            s.karar, s.notlar,
        ])
    return buf.getvalue()


def json_uret(kayitlar, bugun) -> str:
    """Versiyonlu dışa aktarım — suite'in 'versiyonlu export' deseni."""
    cikti = {
        "format": "zekai-ihbar-takvimi/v1",
        "uretim": bugun.isoformat(),
        "hukuki_not": "Zekai Suni ile hazırlanmıştır; hukuki görüş değildir, güvenilmeden "
                      "önce bir avukat tarafından gözden geçirilmelidir.",
        "hukuki_dayanaklar": {
            "sure_hesabi": "TBK m. 89-93; MK m. 12-14",
            "kira_uzatma": "TBK m. 347",
            "kep_ihtarname": "TTK m. 18/3",
        },
        "sozlesmeler": [],
    }
    for s in kayitlar:
        h = hesapla(s, bugun)
        cikti["sozlesmeler"].append({
            "sozlesme": s.dict(),
            "takvim": {
                "donem_baslangici": h.donem_baslangici.isoformat(),
                "donem_bitisi": h.donem_bitisi.isoformat() if h.donem_bitisi else None,
                "son_ihbar_tarihi": h.son_ihbar_tarihi.isoformat() if h.son_ihbar_tarihi else None,
                "son_ihbar_tatil_mi": h.son_ihbar_tatil_mi,
                "tatil_adi": h.tatil_adi,
                "onerilen_is_gunu": h.onerilen_is_gunu.isoformat() if h.onerilen_is_gunu else None,
                "kalan_gun": h.kalan_gun,
                "rozet": h.rozet,
                "kimse_islem_yapmazsa": h.kimse_islem_yapmazsa,
                "hukuki_notlar": h.hukuki_not,
                "band": h.band,
            },
        })
    return json.dumps(cikti, ensure_ascii=False, indent=2)
