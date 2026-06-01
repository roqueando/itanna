"""
Prefixed — SI unit formatting for engineering values
======================================================

Formats numbers with SI prefixes (p, n, µ, m, k, M, G, etc.)
for clean display in org-mode tables and console output.

Usage:
    from electrical.utils.prefixed import p, pp, si_format

    # p() returns a formatted string with the best matching prefix
    p(0.000015)          → "15.0 µ"
    p(2.5e6)             → "2.5 M"
    p(0.0033)            → "3.3 m"

    # pp() includes unit name
    pp(0.000015, "H")    → "15.0 µH"
    pp(2200e-12, "F")    → "2200 pF"
    pp(100e3, "Hz")      → "100.0 kHz"

    # si_format() lets you pick a specific prefix
    si_format(0.000015, "µ")    → "15.0 µ"
    si_format(10000, "k")       → "10.0 k"

    # Use in org-mode tables:
    # | Component | Value         |
    # |-----------+---------------|
    # | Inductor  | 15.0 µH       |
    # | Cap       | 27.0 nF       |
"""

from typing import Optional

# ── SI Prefixes ──────────────────────────────────────────────────────────
# Ordered from smallest to largest
PREFIXES = [
    (1e-15, "f"),   # femto
    (1e-12, "p"),   # pico
    (1e-9,  "n"),   # nano
    (1e-6,  "µ"),   # micro
    (1e-3,  "m"),   # milli
    (1,     ""),    # base
    (1e3,   "k"),   # kilo
    (1e6,   "M"),   # mega
    (1e9,   "G"),   # giga
    (1e12,  "T"),   # tera
]

# Map prefix symbol → multiplier for si_format
PREFIX_MAP = {sym: mult for mult, sym in PREFIXES}


def si_scale(value: float) -> tuple:
    """Find the best SI prefix for a value.

    Returns (scaled_value, prefix_symbol, multiplier).

    Examples:
        si_scale(0.000015)  → (15.0, "µ", 1e-6)
        si_scale(2500000)   → (2.5, "M", 1e6)
        si_scale(1.0)       → (1.0, "", 1.0)
    """
    if value == 0:
        return (0.0, "", 1.0)

    abs_val = abs(value)
    best_mult, best_sym = 1, ""

    for mult, sym in PREFIXES:
        scaled = value / mult
        if 0.1 <= abs(scaled) < 1000:
            best_mult, best_sym = mult, sym
            break
        # Handle edge cases: very large or very small
        if sym == "T" and abs_val >= 1e12:
            best_mult, best_sym = mult, sym
        if sym == "f" and abs_val < 1e-15:
            best_mult, best_sym = mult, sym

    # Handle case where value is smaller than femto
    if abs_val < 1e-15 and abs_val > 0:
        best_mult, best_sym = PREFIXES[0]  # femto
    # Handle case where value is larger than tera
    if abs_val >= 1e12:
        best_mult, best_sym = PREFIXES[-1]  # tera

    return (value / best_mult, best_sym, best_mult)


def si_format(value: float, prefix: Optional[str] = None, decimals: int = 1) -> str:
    """Format a number with an SI prefix.

    Args:
        value: The numeric value
        prefix: Optional SI prefix symbol ("p", "n", "µ", "m", "", "k", "M", "G", "T").
                If None, the best matching prefix is chosen automatically.
        decimals: Number of decimal places (default 1)

    Returns:
        Formatted string like "15.0 µ", "2.5 M", "3.3 m"
    """
    if prefix is not None:
        mult = PREFIX_MAP.get(prefix, 1)
        scaled = value / mult
        return f"{scaled:.{decimals}f} {prefix}"
    else:
        scaled, sym, _ = si_scale(value)
        return f"{scaled:.{decimals}f} {sym}"


def p(value: float, decimals: int = 1) -> str:
    """Format a plain value with the best SI prefix (no unit).

    Short name for quick use in code.

    Args:
        value: The numeric value
        decimals: Number of decimal places (default 1)

    Returns:
        String like "15.0 µ", "2.5 M", "3.3 m"

    Example:
        p(0.000015)   → "15.0 µ"
        p(2_200_000)  → "2.2 M"
    """
    scaled, sym, _ = si_scale(value)
    return f"{scaled:.{decimals}f} {sym}"


def pp(value: float, unit: str = "", decimals: int = 1) -> str:
    """Format a value with SI prefix and a unit suffix.

    Args:
        value: The numeric value
        unit: Unit symbol like "H", "F", "Hz", "V", "A", "W", "Ω"
        decimals: Number of decimal places (default 1)

    Returns:
        String like "15.0 µH", "2.5 MHz", "3.3 mW"

    Example:
        pp(0.000015, "H")    → "15.0 µH"
        pp(100e3, "Hz")      → "100.0 kHz"
        pp(0.002, "F")       → "2.0 mF"
        pp(4.7, "kΩ")        → "4.7 kΩ"  (note: unit already has k)
    """
    scaled, sym, _ = si_scale(value)
    return f"{scaled:.{decimals}f} {sym}{unit}"


# ── Legacy API (compatible with previous versions) ───────────────────────

def format_value(value: float, unit: str = "", decimals: int = 1) -> str:
    """Legacy name for pp()."""
    return pp(value, unit, decimals)


def to_table_row(name: str, value: float, unit: str = "", decimals: int = 1) -> list:
    """Create an org-mode table row with prefixed value and unit.

    Returns [name, formatted_value, unit_with_prefix]

    Example:
        to_table_row("Inductor", 0.000015, "H")
        → ["Inductor", "15.0", "µH"]
    """
    scaled, sym, _ = si_scale(value)
    formatted = f"{scaled:.{decimals}f}"
    return [name, formatted, f"{sym}{unit}"]
