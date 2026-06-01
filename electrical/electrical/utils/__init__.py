"""
Itanna EE Utilities
====================

Helper modules for the electrical package.
"""

from .prefixed import p, pp, si_format, si_scale
from .eseries import (
    nearest_value, nearest_resistor, nearest_inductor, nearest_capacitor,
    list_series, generate_series,
    E3, E6, E12, E24, E48, E96, E192,
    E3_RESISTOR, E6_RESISTOR, E12_RESISTOR, E24_RESISTOR,
    E48_RESISTOR, E96_RESISTOR, E192_RESISTOR,
    E3_COMPONENT, E6_COMPONENT, E12_COMPONENT, E24_COMPONENT,
    E48_COMPONENT, E96_COMPONENT, E192_COMPONENT,
)
