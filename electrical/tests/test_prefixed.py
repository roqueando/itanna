"""Tests for the prefixed SI unit formatter."""

from electrical.utils.prefixed import p, pp, si_format, si_scale, to_table_row


def test_si_scale_basic():
    """Test that si_scale chooses the right prefix."""
    scaled, sym, mult = si_scale(0.000015)
    assert abs(scaled - 15.0) < 0.1
    assert sym == "µ"

    scaled, sym, mult = si_scale(2_500_000)
    assert abs(scaled - 2.5) < 0.1
    assert sym == "M"

    scaled, sym, mult = si_scale(1000)
    assert abs(scaled - 1.0) < 0.1
    assert sym == "k"


def test_p():
    """Test plain formatting."""
    assert "µ" in p(0.000015)
    assert "k" in p(1000)
    assert "M" in p(1_000_000)
    assert "m" in p(0.003)
    assert "n" in p(0.000000001)


def test_pp():
    """Test formatting with units."""
    assert pp(0.000015, "H") == "15.0 µH"
    assert pp(2200e-12, "F") == "2.2 nF"
    assert pp(100e3, "Hz") == "100.0 kHz"
    assert pp(12, "V") == "12.0 V"
    assert pp(0.005, "A") == "5.0 mA"


def test_si_format():
    """Test specific prefix formatting."""
    assert si_format(0.000015, "µ") == "15.0 µ"
    assert si_format(10000, "k") == "10.0 k"
    assert si_format(1.5, "") == "1.5 "


def test_to_table_row():
    """Test table row formatting."""
    row = to_table_row("Inductor", 0.000015, "H")
    assert row[0] == "Inductor"
    assert row[1] == "15.0"
    assert row[2] == "µH"

    row = to_table_row("Freq", 300000, "Hz")
    assert row[0] == "Freq"
    assert row[2] == "kHz"


def test_zero():
    """Test zero handling."""
    scaled, sym, mult = si_scale(0)
    assert scaled == 0.0
    assert sym == ""
    assert "0" in p(0)
