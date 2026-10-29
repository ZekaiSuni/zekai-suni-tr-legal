"""KVKK & PII Maskeleme Katmanı (Talimatname Bölüm 3, Adım 2).
Belge metni harici LLM'e gönderilmeden önce kimlik verileri maskelenir;
LLM yanıtı döndüğünde maske haritası bellekte tutulur ve geri açılabilir.
TCKN: 11 hane + algoritma doğrulaması (1., 3., 5., 7., 9. hane toplamı ×7 ... kısa yöntem).
Varsayılan: maskeleme AÇIK. Kapatmak için açık kullanıcı onayı gerekir (Talimat 5.3)."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

TCKN_KALIP = re.compile(r"\b[1-9](?!0{10})\d{10}\b")
IBAN_KALIP = re.compile(r"\bTR\d{2}(?:\s?\d{4}){5}\s?\d{2}\b")
TEL_KALIP = re.compile(r"(?:\+90|0)?\s?5\d{2}\s?\d{3}\s?\d{2}\s?\d{2}\b")
EPOSTA_KALIP = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b")


def tckn_gecerli_mi(rakamlar: str) -> bool:
    """11 haneli TCKN doğrulama algoritması (10. hane çiftlik testi, 11. hane mod 10)."""
    h = [int(c) for c in rakamlar]
    if h[0] == 0 or sum(h[:10]) % 10 != h[10]:
        return False
    tek = sum(h[0:9:2])
    cift = sum(h[1:8:2])
    return (tek * 7 - cift) % 10 == h[9]


@dataclass
class MaskeSonucu:
    maskeli_metin: str
    harita: dict = field(default_factory=dict)
    istatistik: dict = field(default_factory=dict)


def maskele(metin: str) -> MaskeSonucu:
    """Kimlik verilerini [TUR-1] biçiminde yer tutucularla değiştirir.
    Yer tutucular LLM'e gider; gerçek değerler haritada kalır (LLM'e asla gitmez)."""
    harita: dict = {}
    sayac: dict = {"TCKN": 0, "IBAN": 0, "TEL": 0, "EPOSTA": 0}

    def yer_tutucu(tur: str, gercek: str) -> str:
        sayac[tur] += 1
        kod = f"[{tur}-{sayac[tur]}]"
        harita[kod] = gercek
        return kod

    def tckn_degistir(m):
        rakam = m.group(0)
        return yer_tutucu("TCKN", rakam) if tckn_gecerli_mi(rakam) else rakam

    def genel_degistir(tur):
        def _ic(m):
            return yer_tutucu(tur, m.group(0))
        return _ic

    metin = TCKN_KALIP.sub(tckn_degistir, metin)
    metin = IBAN_KALIP.sub(genel_degistir("IBAN"), metin)
    metin = EPOSTA_KALIP.sub(genel_degistir("EPOSTA"), metin)
    metin = TEL_KALIP.sub(genel_degistir("TEL"), metin)

    return MaskeSonucu(maskeli_metin=metin, harita=harita, istatistik=sayac)


def maskeleri_geri_ac(metin: str, harita: dict) -> str:
    """LLM cevabındaki yer tutucuları gerçek değerlerle değiştirir (yanıt kullanıcıya dönerken)."""
    for kod, gercek in harita.items():
        metin = metin.replace(kod, gercek)
    return metin


def unmask_derin(obj, harita: dict):
    """LLM yanıtındaki tüm dize alanlarda yer tutucuları geri açar (özyinelemeli: str/list/dict)."""
    if isinstance(obj, str):
        return maskeleri_geri_ac(obj, harita)
    if isinstance(obj, list):
        return [unmask_derin(o, harita) for o in obj]
    if isinstance(obj, dict):
        return {k: unmask_derin(v, harita) for k, v in obj.items()}
    return obj


def hazir_girdi(metin: str, tur: str = "BELGE METNI"):
    """Tek çağrıda: maskele + çitle sar. Döner: (çitli_girdi, harita).
    moduller.py'deki modül analiz uçları bunu kullanır."""
    s = maskele(metin)
    from app.prompt_yoneticisi import guvenli_veri_citi
    return guvenli_veri_citi(tur, s.maskeli_metin), s.harita
