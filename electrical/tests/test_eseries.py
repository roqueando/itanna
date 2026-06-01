"""Tests for the E-series standard values module."""

from electrical.utils.eseries import (
    nearest_value, nearest_resistor, nearest_inductor, nearest_capacitor,
    list_series, generate_series,
    E3, E6, E12, E24, E48, E96, E192,
    E3_BASE, E6_BASE, E12_BASE, E24_BASE, E48_BASE, E96_BASE, E192_BASE,
    E12_COMPONENT,
)


def test_base_lengths():
    """Verify each E-series has the correct number of base values."""
    assert len(E3_BASE) == 3
    assert len(E6_BASE) == 6
    assert len(E12_BASE) == 12
    assert len(E24_BASE) == 24
    assert len(E48_BASE) == 48
    assert len(E96_BASE) == 96
    assert len(E192_BASE) == 192


def test_generated_lengths():
    """Verify generated lists span the correct number of decades."""
    # 9 decades (10^-2 to 10^7) × base count
    assert len(E3) == 3 * 10
    assert len(E6) == 6 * 10
    assert len(E12) == 12 * 10
    assert len(E24) == 24 * 10
    assert len(E48) == 48 * 10
    assert len(E96) == 96 * 10
    assert len(E192) == 192 * 10


def test_nearest_value_e3():
    """Test nearest match in E3 series."""
    assert nearest_value(1.0, "E3") == 1.0
    # 1.8 is closer to 2.2 (dist 0.4) than to 1.0 (dist 0.8)
    assert nearest_value(1.8, "E3") == 2.2
    # 3.0 is closer to 2.2 (dist 0.8) than to 4.7 (dist 1.7)
    assert nearest_value(3.0, "E3") == 2.2
    assert nearest_value(5.0, "E3") == 4.7


def test_nearest_value_e6():
    """Test nearest match in E6 series."""
    assert nearest_value(1.0, "E6") == 1.0
    assert nearest_value(2.2, "E6") == 2.2
    assert nearest_value(4.7, "E6") == 4.7
    assert nearest_value(3.0, "E6") == 3.3
    assert nearest_value(5.0, "E6") == 4.7


def test_nearest_value_e12():
    """Test the most common series."""
    assert nearest_value(1000, "E12") == 1000.0
    assert nearest_value(1200, "E12") == 1200.0
    assert nearest_value(470, "E12") == 470.0
    assert nearest_value(12345, "E12") == 12000.0
    assert nearest_value(68000, "E12") == 68000.0


def test_nearest_value_e24():
    """Test E24 series."""
    assert nearest_value(1000, "E24") == 1000.0
    assert nearest_value(1100, "E24") == 1100.0
    assert nearest_value(1050, "E24") in (1000.0, 1100.0)


def test_nearest_value_e48():
    """Test E48 series (higher precision)."""
    # 1.24 is exactly midway between E48 values 1.21 and 1.27.
    # Either is correct — check it picks one of them.
    result = nearest_value(12400, "E48")
    assert result in (12100.0, 12400.0, 12700.0)

    assert nearest_value(10000, "E48") == 10000.0
    # 1.2345 is closer to 1.21 (dist 0.0245) than to 1.27 (dist 0.0355)? No...
    # 1.2345 - 1.21 = 0.0245, 1.27 - 1.2345 = 0.0355. So 1.21 is closer!
    result2 = nearest_value(12345, "E48")
    assert result2 in (12100.0, 12400.0)


def test_nearest_value_e96():
    """Test E96 series."""
    assert nearest_value(12400, "E96") == 12400.0
    assert nearest_value(10000, "E96") == 10000.0


def test_nearest_value_e192():
    """Test E192 series (finest granularity)."""
    assert nearest_value(12300, "E192") == 12300.0
    assert nearest_value(10000, "E192") == 10000.0
    # 1.0050 is midway between 1.00 and 1.01. Either is fine.
    result = nearest_value(10050, "E192")
    assert result in (10000.0, 10100.0)


def test_nearest_resistor():
    """Test the resistor convenience wrapper."""
    assert nearest_resistor(1000) == 1000.0
    assert nearest_resistor(12345) == 12000.0  # E24 default


def test_nearest_inductor():
    """Test inductor values use component range."""
    # 15 µH should exist in E12 component range
    val = nearest_inductor(15e-6)
    assert abs(val - 15e-6) / 15e-6 < 0.2

    # 47 µH
    val = nearest_inductor(47e-6)
    assert abs(val - 47e-6) / 47e-6 < 0.2


def test_nearest_capacitor():
    """Test capacitor values use component range."""
    # 10 µF
    val = nearest_capacitor(10e-6)
    assert abs(val - 10e-6) / 10e-6 < 0.2

    # 100 µF
    val = nearest_capacitor(100e-6)
    assert abs(val - 100e-6) / 100e-6 < 0.2

    # 1 nF
    val = nearest_capacitor(1e-9)
    assert abs(val - 1e-9) / 1e-9 < 0.2


def test_component_range():
    """Test component range covers nH/pF to H/F."""
    # 1 nH
    assert nearest_value(1e-9, "E12", component=True) <= 1.2e-9
    # 1 H
    assert nearest_value(1.0, "E12", component=True) >= 1.0


def test_list_series():
    """Test listing all values in a series."""
    vals = list_series("E3")
    assert len(vals) == 30  # 3 × 10 decades
    assert vals[0] == 0.01  # 10^-2 × 1.0
    assert vals[-1] == 47000000.0  # 10^7 × 4.7


def test_edge_values():
    """Test values at the boundaries."""
    # Below minimum — returns minimum
    assert nearest_value(0.001, "E12") == 0.01  # E12 starts at 0.01
    # Above maximum — returns maximum
    assert nearest_value(1e9, "E12") == 82000000.0  # E12 ends at 82M


def test_generate_series_custom():
    """Test generation with custom decade range."""
    vals = generate_series(E3_BASE, decades=(0, 0))
    assert len(vals) == 3
    assert vals == [1.0, 2.2, 4.7]
