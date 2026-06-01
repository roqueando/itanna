"""
E-Series Standard Values
=========================

Full set of IEC 60063 standard E-series values (E3, E6, E12, E24, E48, E96, E192)
for resistors, capacitors, inductors, and other electronic components.

Each series defines the base values in the range [1.0, 10.0).
Use `generate_series()` to expand them over any decade range.

Usage:
    from electrical.utils.eseries import (
        nearest_value, E3, E6, E12, E24, E48, E96, E192,
        E3_RESISTOR, E12_RESISTOR, E24_RESISTOR, E48_RESISTOR,
        E12_COMPONENT,
    )

    # Find nearest standard resistor
    nearest_value(12345, "E24")      → 12000.0  (12 kΩ)
    nearest_value(12345, "E12")      → 12000.0  (12 kΩ)
    nearest_value(12345, "E48")      → 12400.0  (12.4 kΩ)

    # Find nearest component value (wider range)
    nearest_value(15e-6, "E12", component=True)   → 15.0e-6  (15 µH)
    nearest_value(27e-6, "E12", component=True)   → 27.0e-6  (27 µF)

    # Get sorted list of all values in a series
    E12               → all E12 values from 0.01 to 10M (resistor range)
    E12_COMPONENT     → all E12 values from 1n to 1k (component range)

References:
    IEC 60063:2015 — Preferred number series for resistors and capacitors
    EIA RS-198 — Standard values for resistors
"""

from typing import Optional

# ── Base values for each E-series (normalized to [1.0, 10.0)) ────────────
# These are the exact IEC 60063 values.

E3_BASE = [
    1.0, 2.2, 4.7,
]

E6_BASE = [
    1.0, 1.5, 2.2, 3.3, 4.7, 6.8,
]

E12_BASE = [
    1.0, 1.2, 1.5, 1.8, 2.2, 2.7,
    3.3, 3.9, 4.7, 5.6, 6.8, 8.2,
]

E24_BASE = [
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6,
    1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
    3.3, 3.6, 3.9, 4.3, 4.7, 5.1,
    5.6, 6.2, 6.8, 7.5, 8.2, 9.1,
]

E48_BASE = [
    1.00, 1.05, 1.10, 1.15, 1.21, 1.27,
    1.33, 1.40, 1.47, 1.54, 1.62, 1.69,
    1.78, 1.87, 1.96, 2.05, 2.15, 2.26,
    2.37, 2.49, 2.61, 2.74, 2.87, 3.01,
    3.16, 3.32, 3.48, 3.65, 3.83, 4.02,
    4.22, 4.42, 4.64, 4.87, 5.11, 5.36,
    5.62, 5.90, 6.19, 6.49, 6.81, 7.15,
    7.50, 7.87, 8.25, 8.66, 9.09, 9.53,
]

E96_BASE = [
    1.00, 1.02, 1.05, 1.07, 1.10, 1.13,
    1.15, 1.18, 1.21, 1.24, 1.27, 1.30,
    1.33, 1.37, 1.40, 1.43, 1.47, 1.50,
    1.54, 1.58, 1.62, 1.65, 1.69, 1.74,
    1.78, 1.82, 1.87, 1.91, 1.96, 2.00,
    2.05, 2.10, 2.15, 2.21, 2.26, 2.32,
    2.37, 2.43, 2.49, 2.55, 2.61, 2.67,
    2.74, 2.80, 2.87, 2.94, 3.01, 3.09,
    3.16, 3.24, 3.32, 3.40, 3.48, 3.57,
    3.65, 3.74, 3.83, 3.92, 4.02, 4.12,
    4.22, 4.32, 4.42, 4.53, 4.64, 4.75,
    4.87, 4.99, 5.11, 5.23, 5.36, 5.49,
    5.62, 5.76, 5.90, 6.04, 6.19, 6.34,
    6.49, 6.65, 6.81, 6.98, 7.15, 7.32,
    7.50, 7.68, 7.87, 8.06, 8.25, 8.45,
    8.66, 8.87, 9.09, 9.31, 9.53, 9.76,
]

E192_BASE = [
    1.00, 1.01, 1.02, 1.04, 1.05, 1.06,
    1.07, 1.09, 1.10, 1.11, 1.13, 1.14,
    1.15, 1.17, 1.18, 1.20, 1.21, 1.23,
    1.24, 1.26, 1.27, 1.29, 1.30, 1.32,
    1.33, 1.35, 1.37, 1.38, 1.40, 1.42,
    1.43, 1.45, 1.47, 1.49, 1.50, 1.52,
    1.54, 1.56, 1.58, 1.60, 1.62, 1.64,
    1.65, 1.67, 1.69, 1.72, 1.74, 1.76,
    1.78, 1.80, 1.82, 1.84, 1.87, 1.89,
    1.91, 1.93, 1.96, 1.98, 2.00, 2.03,
    2.05, 2.08, 2.10, 2.13, 2.15, 2.18,
    2.21, 2.23, 2.26, 2.29, 2.32, 2.34,
    2.37, 2.40, 2.43, 2.46, 2.49, 2.52,
    2.55, 2.58, 2.61, 2.64, 2.67, 2.71,
    2.74, 2.77, 2.80, 2.84, 2.87, 2.91,
    2.94, 2.98, 3.01, 3.05, 3.09, 3.12,
    3.16, 3.20, 3.24, 3.28, 3.32, 3.36,
    3.40, 3.44, 3.48, 3.52, 3.57, 3.61,
    3.65, 3.70, 3.74, 3.79, 3.83, 3.88,
    3.92, 3.97, 4.02, 4.07, 4.12, 4.17,
    4.22, 4.27, 4.32, 4.37, 4.42, 4.48,
    4.53, 4.59, 4.64, 4.70, 4.75, 4.81,
    4.87, 4.93, 4.99, 5.05, 5.11, 5.17,
    5.23, 5.30, 5.36, 5.42, 5.49, 5.56,
    5.62, 5.69, 5.76, 5.83, 5.90, 5.97,
    6.04, 6.12, 6.19, 6.26, 6.34, 6.42,
    6.49, 6.57, 6.65, 6.73, 6.81, 6.90,
    6.98, 7.06, 7.15, 7.23, 7.32, 7.41,
    7.50, 7.59, 7.68, 7.77, 7.87, 7.96,
    8.06, 8.16, 8.25, 8.35, 8.45, 8.56,
    8.66, 8.76, 8.87, 8.98, 9.09, 9.20,
    9.31, 9.42, 9.53, 9.65, 9.76, 9.88,
]

# ── Series name → base map ──────────────────────────────────────────────
SERIES_MAP = {
    "E3":   E3_BASE,
    "E6":   E6_BASE,
    "E12":  E12_BASE,
    "E24":  E24_BASE,
    "E48":  E48_BASE,
    "E96":  E96_BASE,
    "E192": E192_BASE,
}

# ── Generator ────────────────────────────────────────────────────────────

def generate_series(base, decades=(-2, 7)):
    """Generate standard values over a range of decades.

    Args:
        base: List of base values normalized to [1.0, 10.0) range.
              e.g. E12_BASE = [1.0, 1.2, 1.5, ...]
        decades: Tuple of (min_exponent, max_exponent).
                 Default (-2, 7) = 0.01Ω to 10MΩ (resistor range).

    Returns:
        Sorted list of standard values expanded across all decades.
    """
    vals = []
    for d in range(decades[0], decades[1] + 1):
        mul = 10 ** d
        for b in base:
            vals.append(b * mul)
    return sorted(vals)


# ── Pre-generated lists for common decade ranges ────────────────────────

# Resistor range: 0.01Ω to 10MΩ  (9 decades, 10^-2 to 10^7)
E3_RESISTOR   = generate_series(E3_BASE,   decades=(-2, 7))
E6_RESISTOR   = generate_series(E6_BASE,   decades=(-2, 7))
E12_RESISTOR  = generate_series(E12_BASE,  decades=(-2, 7))
E24_RESISTOR  = generate_series(E24_BASE,  decades=(-2, 7))
E48_RESISTOR  = generate_series(E48_BASE,  decades=(-2, 7))
E96_RESISTOR  = generate_series(E96_BASE,  decades=(-2, 7))
E192_RESISTOR = generate_series(E192_BASE, decades=(-2, 7))

# Component range: 1nH/pF to 1kH/F  (12 decades, 10^-9 to 10^3)
# This covers all practical inductor, capacitor, and component values.
E3_COMPONENT   = generate_series(E3_BASE,   decades=(-9, 3))
E6_COMPONENT   = generate_series(E6_BASE,   decades=(-9, 3))
E12_COMPONENT  = generate_series(E12_BASE,  decades=(-9, 3))
E24_COMPONENT  = generate_series(E24_BASE,  decades=(-9, 3))
E48_COMPONENT  = generate_series(E48_BASE,  decades=(-9, 3))
E96_COMPONENT  = generate_series(E96_BASE,  decades=(-9, 3))
E192_COMPONENT = generate_series(E192_BASE, decades=(-9, 3))

# Convenience aliases: if you don't specify, these give the most common ranges
E3   = E3_RESISTOR
E6   = E6_RESISTOR
E12  = E12_RESISTOR
E24  = E24_RESISTOR
E48  = E48_RESISTOR
E96  = E96_RESISTOR
E192 = E192_RESISTOR


# ── Nearest-value lookup ─────────────────────────────────────────────────

def _pool_for_series(series: str, component: bool = False):
    """Get the pre-generated value list for a given series."""
    key = series.upper()
    if key not in SERIES_MAP:
        key = "E24"

    if component:
        # Use component range (wider)
        return {
            "E3": E3_COMPONENT, "E6": E6_COMPONENT, "E12": E12_COMPONENT,
            "E24": E24_COMPONENT, "E48": E48_COMPONENT, "E96": E96_COMPONENT,
            "E192": E192_COMPONENT,
        }.get(key, E12_COMPONENT)
    else:
        return {
            "E3": E3_RESISTOR, "E6": E6_RESISTOR, "E12": E12_RESISTOR,
            "E24": E24_RESISTOR, "E48": E48_RESISTOR, "E96": E96_RESISTOR,
            "E192": E192_RESISTOR,
        }.get(key, E24_RESISTOR)


def nearest_value(value: float, series: str = "E24", component: bool = False) -> float:
    """Find the nearest standard E-series value.

    Args:
        value: Desired component value (e.g., 12345 for 12.345 kΩ)
        series: One of "E3", "E6", "E12", "E24", "E48", "E96", "E192"
        component: If True, search over the component range (nH/pF to kH/F)
                   which is wider than the resistor range (0.01Ω–10MΩ).

    Returns:
        The nearest standard value from the selected series.

    Examples:
        nearest_value(12345, "E12")       → 12000.0   (12 kΩ)
        nearest_value(12345, "E24")       → 12000.0   (12 kΩ)
        nearest_value(12345, "E48")       → 12400.0   (12.4 kΩ)
        nearest_value(12345, "E96")       → 12400.0   (12.4 kΩ)
        nearest_value(12345, "E192")      → 12300.0   (12.3 kΩ)
        nearest_value(0.000015, "E12", component=True)   → 15.0e-6  (15 µH)
    """
    pool = _pool_for_series(series, component=component)
    if not pool:
        return value

    if value <= pool[0]:
        return pool[0]
    if value >= pool[-1]:
        return pool[-1]

    lo, hi = 0, len(pool) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if pool[mid] == value:
            return pool[mid]
        if pool[mid] < value:
            lo = mid + 1
        else:
            hi = mid - 1

    # Nearest of the two surrounding candidates
    if lo >= len(pool):
        return pool[-1]
    if hi < 0:
        return pool[0]
    return pool[lo] if (pool[lo] - value) < (value - pool[hi]) else pool[hi]


# ── Convenience wrappers for common component types ──────────────────────

def nearest_resistor(value: float, series: str = "E24") -> float:
    """Find the nearest standard resistor value (E24 by default)."""
    return nearest_value(value, series, component=False)


def nearest_inductor(value: float, series: str = "E12") -> float:
    """Find the nearest standard inductor value (E12 by default, wide range)."""
    return nearest_value(value, series, component=True)


def nearest_capacitor(value: float, series: str = "E12") -> float:
    """Find the nearest standard capacitor value (E12 by default, wide range)."""
    return nearest_value(value, series, component=True)


# ── List all values in a series for inspection ──────────────────────────

def list_series(series: str = "E24", component: bool = False) -> list:
    """Return the full list of standard values for a given E-series.

    Args:
        series: One of "E3", "E6", "E12", "E24", "E48", "E96", "E192"
        component: If True, return the component range (wider).

    Returns:
        Sorted list of all values in the series.
    """
    return _pool_for_series(series, component=component)
