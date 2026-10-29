"""
Resmî tatil takvimi (2429 sayılı Ulusal Bayram ve Genel Tatiller Hakkında Kanun).
Kaynak: web araştırması 29 Ekim 2026 — dini bayram tarihleri her yıl Resmî Gazete
ile kesinleşir; "YAKLASIK" işaretli tarihler Diyanet hesaplamasına dayanır ve
kullanım öncesi teyit edilmelidir. Dosya elle düzenlenebilir.
"""

from datetime import date

# (ay, gün) — TAM gün tatiller
TAM_TATILLER: dict[int, list[tuple[int, int]]] = {
    2025: [
        (1, 1), (3, 30), (3, 31), (4, 1), (4, 23), (5, 1), (5, 19),
        (6, 6), (6, 7), (6, 8), (6, 9),
        (7, 15), (8, 30), (10, 29),
    ],
    2026: [
        (1, 1),                       # Yılbaşı (Perşembe)
        (3, 20), (3, 21), (3, 22),    # Ramazan Bayramı (20-22 Mart)
        (4, 23),                      # Ulusal Egemenlik ve Çocuk Bayramı
        (5, 1),                       # Emek ve Dayanışma Günü
        (5, 19),                      # Atatürk'ü Anma, Gençlik ve Spor Bayramı
        (5, 27), (5, 28), (5, 29), (5, 30),  # Kurban Bayramı (27-30 Mayıs)
        (7, 15),                      # Demokrasi ve Millî Birlik Günü
        (8, 30),                      # Zafer Bayramı
        (10, 29),                     # Cumhuriyet Bayramı
    ],
    2027: [
        (1, 1),                       # Yılbaşı (Cuma)
        (3, 9), (3, 10), (3, 11),     # Ramazan Bayramı (9-11 Mart) — YAKLAŞIK
        (4, 23),
        (5, 1),
        (5, 19),
        (5, 16), (5, 17), (5, 18), (5, 19),  # Kurban Bayramı (Mayıs 2027) — YAKLAŞIK
        (7, 15),
        (8, 30),
        (10, 29),
    ],
    # 2028-2030: yalnız SABİT milli tatiller (2429 sk.); dini bayramlar RG teyidi ile eklenmeli!
    2028: [(1, 1), (4, 23), (5, 1), (5, 19), (7, 15), (8, 30), (10, 29)],
    2029: [(1, 1), (4, 23), (5, 1), (5, 19), (7, 15), (8, 30), (10, 29)],
    2030: [(1, 1), (4, 23), (5, 1), (5, 19), (7, 15), (8, 30), (10, 29)],
}

# Arife: yarım gün (tam gün sayılmaz; uygulamada öğleden sonra tatil)
YARIM_TATILLER: dict[int, list[tuple[int, int]]] = {
    2026: [(3, 19), (5, 26)],
    2027: [(3, 8)],
}

# Bu tarihler hilal hesabına bağlı; resmî teyit öncesi "yaklaşık"
YAKLASIK_KAYNAKLI = {
    "2027 dini bayramlar": "Diyanet hesaplaması — Resmî Gazete teyidi beklenir",
}


def tam_tatil_mi(d: date) -> bool:
    """Tam gün resmî tatil mi? (hafta sonu dahil DEĞİL — ayrı hesaplanır)"""
    for yil, liste in TAM_TATILLER.items():
        if yil == d.year and (d.month, d.day) in liste:
            return True
    return False


def yarim_tatil_mi(d: date) -> bool:
    for yil, liste in YARIM_TATILLER.items():
        if yil == d.year and (d.month, d.day) in liste:
            return True
    return False


def hafta_sonu_mu(d: date) -> bool:
    # Türkiye'de çalışma haftası: Pazartesi-Cuma (4857 sK.)
    return d.weekday() >= 5  # 5=Cumartesi, 6=Pazar


def is_gunu_mu(d: date) -> bool:
    return not (hafta_sonu_mu(d) or tam_tatil_mi(d))


def izleyen_is_gunu(d: date) -> date:
    """Sonraki iş gününü döndürür (d dahil değil)."""
    k = d
    while True:
        k = k + __import__("datetime").timedelta(days=1)
        if is_gunu_mu(k):
            return k


def tatil_adi(d: date) -> str | None:
    ADLAR = {
        (1, 1): "Yılbaşı", (4, 23): "Ulusal Egemenlik ve Çocuk Bayramı",
        (5, 1): "Emek ve Dayanışma Günü", (5, 19): "Atatürk'ü Anma, Gençlik ve Spor Bayramı",
        (7, 15): "Demokrasi ve Millî Birlik Günü", (8, 30): "Zafer Bayramı",
        (10, 29): "Cumhuriyet Bayramı",
        (3, 19): "Ramazan Bayramı Arifesi (yarım gün)", (3, 20): "Ramazan Bayramı 1. gün",
        (3, 21): "Ramazan Bayramı 2. gün", (3, 22): "Ramazan Bayramı 3. gün",
        (3, 8): "Ramazan Bayramı Arifesi (yarım gün)", (3, 9): "Ramazan Bayramı 1. gün",
        (3, 10): "Ramazan Bayramı 2. gün", (3, 11): "Ramazan Bayramı 3. gün",
        (5, 26): "Kurban Bayramı Arifesi (yarım gün)", (5, 27): "Kurban Bayramı 1. gün",
        (5, 28): "Kurban Bayramı 2. gün", (5, 29): "Kurban Bayramı 3. gün",
        (5, 30): "Kurban Bayramı 4. gün",
        (5, 16): "Kurban Bayramı 1. gün (yaklaşık)", (5, 17): "Kurban Bayramı 2. gün (yaklaşık)",
        (5, 18): "Kurban Bayramı 3. gün (yaklaşık)", (5, 19): "19 Mayıs / Kurban 4. gün (yaklaşık) — ÇAKIŞMA KONTROL EDİLMELİ",
        (6, 6): "Kurban Bayramı 1. gün (2025)", (6, 7): "Kurban Bayramı 2. gün (2025)",
        (6, 8): "Kurban Bayramı 3. gün (2025)", (6, 9): "Kurban Bayramı 4. gün (2025)",
        (9, 4): "Ramazan Bayramı 1. gün (2025)", (9, 5): "Ramazan Bayramı 2. gün (2025)",
        (9, 6): "Ramazan Bayramı 3. gün (2025)",
    }
    if hafta_sonu_mu(d):
        return "Hafta sonu"
    return ADLAR.get((d.month, d.day)) if tam_tatil_mi(d) else None
