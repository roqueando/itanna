"""Tests for the buck converter design module."""

from electrical.converter.buck import design_buck, BuckSpecification, nearest_standard


def test_nearest_standard_e24():
    """Test that nearest_standard finds correct E24 values."""
    assert nearest_standard(1000, "E24") == 1000.0
    assert nearest_standard(1100, "E24") == 1100.0
    assert nearest_standard(1050, "E24") in (1000.0, 1100.0)


def test_nearest_standard_e12():
    assert nearest_standard(1000, "E12") == 1000.0
    assert nearest_standard(470, "E12") == 470.0


def test_design_buck_12v_to_3v3():
    """Design a typical 12V-to-3.3V @ 2A buck converter."""
    spec = design_buck(
        vin=12, vout=3.3, iout=2.0,
        fsw=300e3, vripple=0.01,
        as_dict=True
    )
    assert spec["duty"] > 0.2
    assert spec["duty"] < 0.6
    assert spec["inductor"] > 0  # Some reasonable inductor
    assert spec["output_cap"] > 0
    assert spec["mosfet_voltage"] >= 12


def test_design_buck_spec_object():
    """Test using the BuckSpecification class directly."""
    spec = BuckSpecification(
        vin_nom=24, vout=5, iout_max=3,
        fsw=500e3, vripple_max=0.05
    )
    spec.design()
    assert spec.duty > 0
    assert spec.inductor > 0
    assert spec.output_cap > 0


def test_summary():
    """Test that summary() works without errors."""
    spec = BuckSpecification(
        vin_nom=12, vout=3.3, iout_max=2,
        fsw=300e3, vripple_max=0.01
    )
    spec.design()
    summary = spec.summary()
    assert "Buck Converter" in summary
    assert "µH" in summary


def test_to_table():
    """Test table output format."""
    spec = BuckSpecification(
        vin_nom=12, vout=3.3, iout_max=2,
        fsw=300e3, vripple_max=0.01
    )
    spec.design()
    table = spec.to_table()
    assert len(table) > 0
    assert len(table[0]) == 3  # [parameter, value, unit]
