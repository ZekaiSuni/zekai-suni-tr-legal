"""Kriptografik İnsan Onayı Mührü (Talimatname Bölüm 3, Adım 3).
Orijinal Claude for Legal'in 32-bit FNV-1a `sealOf` mekanizmasının Python karşılığı.
Bir kayıt avukat tarafından onaylandığında mühür hesaplanıp kayda yazılır;
arayüzde '✓ Avukat Onaylı (Mühür: fnv1a-…)' rozeti gösterilir.
LLM çıktısı asla mühürlenemez — mühür yalnız insan onayında üretilir."""

FNV_OFFSET = 0x811C9DC5
FNV_ASAL = 0x01000193
MASKE = 0xFFFFFFFF


def muhur_hesapla(metin: str, onaylayan_kisi: str, tarih: str) -> str:
    """metin|onaylayan|tarih üçlüsünün FNV-1a 32-bit mührü.
    Aynı içerik + aynı onaylayan + aynı tarih → aynı mühür (bütünlük denetlenebilir)."""
    ham = f"{metin or ''}|{onaylayan_kisi or ''}|{tarih or ''}"
    h = FNV_OFFSET
    for karakter in ham:
        h ^= ord(karakter)
        h = (h * FNV_ASAL) & MASKE
    return "fnv1a-" + format(h, "08x")
