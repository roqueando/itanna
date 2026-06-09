"""
Buck (Step-Down) Converter Design
==================================

Given input/output specs, calculate critical component values:
  - Duty cycle
  - Inductor value & ripple
  - Output capacitor (for voltage ripple)
  - Input capacitor
  - Power MOSFET / diode ratings

References:
  - "Fundamentals of Power Electronics" — R. W. Erickson & D. Maksimović
  - Application notes: TI SLVA477B, ON Semiconductor AND9135

Usage:
    from electrical.converter.buck import design_buck, BuckSpecification
    from electrical.utils.eseries import nearest_value

    spec = design_buck(
        vin=12, vout=3.3, iout=2.0,
        fsw=300e3, vripple=0.01,
        il_ripple_pct=0.30  # 30% inductor current ripple
    )

    # Pretty-print summary with SI prefixes
    s = BuckSpecification(12, 3.3, 2.0, 300e3, 0.01)
    s.design()
    print(s.summary())

    # Or get org-table rows
    for row in s.to_table():
        print(f"| {row[0]:25s} | {row[1]:>8s} | {row[2]:<6s} |")
"""

from dataclasses import dataclass, field, asdict
from typing import Optional
import math

from electrical.utils.prefixed import pp, p, to_table_row, si_scale
from electrical.utils.eseries import (
    nearest_value as nearest_standard,
    nearest_inductor,
    nearest_capacitor,
)

# Prefixed package for Float(value):.2h formatting
_has_prefixed = False
try:
    from prefixed import Float as PrefixedFloat
    _has_prefixed = True
except ImportError:
    PrefixedFloat = None


# ── Buck converter design ────────────────────────────────────────────────

@dataclass
class BuckSpecification:
    """Buck converter design specification."""
    # Inputs
    vin_nom: float          # Nominal input voltage (V)
    vout: float              # Output voltage (V)
    iout_max: float          # Maximum output current (A)
    fsw: float               # Switching frequency (Hz)
    vripple_max: float       # Maximum output voltage ripple (V)

    # Optional inputs
    vin_min: Optional[float] = None  # Minimum input voltage (V)
    vin_max: Optional[float] = None  # Maximum input voltage (V)
    il_ripple_pct: float = 0.30      # Target inductor current ripple (fraction of Iout)
    diode_vf: float = 0.7            # Diode forward voltage drop (V)
    mosfet_rdson: float = 0.020      # MOSFET RDS(on) (ohms)
    esr_cap: float = 0.005           # Output capacitor ESR (ohms) — initial guess

    # Results (populated by `design`)
    duty: float = 0.0
    inductor: float = 0.0
    inductor_ripple: float = 0.0
    inductor_peak: float = 0.0
    output_cap: float = 0.0
    output_cap_esr: float = 0.0
    input_cap: float = 0.0
    mosfet_voltage: float = 0.0
    mosfet_current: float = 0.0
    diode_voltage: float = 0.0
    diode_current: float = 0.0

    def design(self) -> "BuckSpecification":
        """Run the full buck converter design and populate result fields."""
        v_in = self.vin_nom
        v_out = self.vout
        i_out = self.iout_max
        f_sw = self.fsw
        v_rip = self.vripple_max
        vf_diode = self.diode_vf
        r_ds = self.mosfet_rdson
        r_il = self.il_ripple_pct

        # Use vin_min/max if provided
        v_in_min = self.vin_min if self.vin_min is not None else v_in * 0.9
        v_in_max = self.vin_max if self.vin_max is not None else v_in * 1.1

        # 1. Duty cycle (CCM, ideal)
        #   D = (Vout + Vf_diode) / (Vin - I*Rds + Vf_diode)
        d = (v_out + vf_diode) / (v_in - i_out * r_ds + vf_diode)
        d_min = (v_out + vf_diode) / (v_in_max - i_out * r_ds + vf_diode)
        d_max = (v_out + vf_diode) / (v_in_min - i_out * r_ds + vf_diode)

        # 2. Inductor
        #   L >= (Vin - Vout) * D / (r_il * Iout * fsw)   [for desired ripple]
        delta_il = r_il * i_out
        l_min = (v_in - v_out) * d / (delta_il * f_sw)
        l_actual = nearest_inductor(l_min)
        # Recalculate ripple with actual inductor
        delta_il_actual = (v_in - v_out) * d / (l_actual * f_sw)
        il_peak = i_out + delta_il_actual / 2

        # 3. Output capacitor
        #   Cout >= delta_il / (8 * fsw * vripple_max)   [ignoring ESR]
        c_out_min = delta_il_actual / (8 * f_sw * v_rip)
        c_out = nearest_capacitor(c_out_min)
        # Check ESR contribution to ripple
        v_rip_esr = delta_il_actual * self.esr_cap
        if v_rip_esr > v_rip:
            # Need lower ESR or larger cap
            pass  # log warning

        # 4. Input capacitor
        #   Cin >= Iout * D * (1-D) / (fsw * Vin_ripple)  (assuming Vin_ripple ~ 0.1*Vin)
        vin_ripple_assumed = 0.1 * v_in
        c_in_min = i_out * d * (1 - d) / (f_sw * vin_ripple_assumed)
        c_in = nearest_capacitor(c_in_min)

        # 5. Semiconductor ratings
        v_mosfet = v_in_max           # Vds max = Vin_max
        i_mosfet_rms = i_out * math.sqrt(d)
        v_diode = v_in_max            # Vrrm = Vin_max (approx)
        i_diode_avg = i_out * (1 - d)

        # Store results
        self.duty = d
        self.inductor = l_actual
        self.inductor_ripple = delta_il_actual
        self.inductor_peak = il_peak
        self.output_cap = c_out
        self.output_cap_esr = self.esr_cap
        self.input_cap = c_in
        self.mosfet_voltage = v_mosfet
        self.mosfet_current = i_mosfet_rms
        self.diode_voltage = v_diode
        self.diode_current = i_diode_avg
        return self

    def _fmt(self, value: float, unit: str = "") -> str:
        """Format a value with SI prefix, using prefixed package if available."""
        if _has_prefixed:
            return f"{PrefixedFloat(value):.2h}{unit}"
        return pp(value, unit)

    def summary(self) -> str:
        """Return a human-readable summary string with SI-prefixed values."""
        _ = self._fmt
        lines = [
            "═" * 55,
            "  Buck Converter Design Summary",
            "═" * 55,
            f"  Vin = {_(self.vin_nom, 'V')}  ({_(self.vin_min or self.vin_nom*0.9, 'V')} – {_(self.vin_max or self.vin_nom*1.1, 'V')})",
            f"  Vout = {_(self.vout, 'V')}  @  {_(self.iout_max, 'A')}  (max)",
            f"  Fsw = {_(self.fsw, 'Hz')}",
            f"  Vripple(max) = {_(self.vripple_max, 'V')}",
            "─" * 55,
            f"  Duty cycle (nom)      : {self.duty*100:.1f} %",
            f"  Inductor              : {_(self.inductor, 'H')}  (ΔIL = {_(self.inductor_ripple, 'A')}, peak = {_(self.inductor_peak, 'A')})",
            f"  Output capacitor      : {_(self.output_cap, 'F')}  (ESR ≤ {_(self.output_cap_esr, 'Ω')})",
            f"  Input capacitor       : {_(self.input_cap, 'F')}",
            "─" * 55,
            f"  MOSFET Vds(max)       : {_(self.mosfet_voltage, 'V')}",
            f"  MOSFET Irms           : {_(self.mosfet_current, 'A')}",
            f"  Diode Vrrm            : {_(self.diode_voltage, 'V')}",
            f"  Diode Iavg            : {_(self.diode_current, 'A')}",
            "═" * 55,
        ]
        return "\n".join(lines)

    def to_table(self) -> list:
        """Return results as [parameter, value, unit_with_prefix] for org-mode tables.

        Each row is a list of three strings suitable for inserting into
        an org-mode table with something like:

            #+RESULTS:
            | Parameter         | Value | Unit |
            |-------------------+-------+------|
            | Inductor          |  15.0 | µH   |
            ...
        """
        return [
            ["Duty cycle", f"{self.duty*100:.1f}", "%"],
            to_table_row("Inductor", self.inductor, "H"),
            to_table_row("Inductor ripple", self.inductor_ripple, "A"),
            to_table_row("Inductor peak", self.inductor_peak, "A"),
            to_table_row("Output capacitor", self.output_cap, "F"),
            to_table_row("Input capacitor", self.input_cap, "F"),
            to_table_row("MOSFET Vds", self.mosfet_voltage, "V"),
            to_table_row("MOSFET Irms", self.mosfet_current, "A"),
            to_table_row("Diode Vrrm", self.diode_voltage, "V"),
            to_table_row("Diode Iavg", self.diode_current, "A"),
        ]

    def to_dataframe(self):
        """Return results as a pandas DataFrame for Jupyter display.

        Returns a DataFrame with columns [Parameter, Value, Unit],
        where Value uses SI prefixes (e.g. 15.0, 2.2) and Unit has
        the prefix combined (e.g. µH, mA, kHz).

        If pandas is not installed, falls back to a list of tuples.
        """
        table = self.to_table()
        try:
            import pandas as pd
            return pd.DataFrame(table, columns=["Parameter", "Value", "Unit"])
        except ImportError:
            return table

    def _repr_html_(self) -> str:
        """Render as an HTML table for Jupyter notebook display.

        Uses the `prefixed` package (Float(value):.2h) for SI-prefixed
        value formatting when available, otherwise falls back to the
        built-in `electrical.utils.prefixed` module.
        """
        rows_html = ""
        for row in self._prefixed_table():
            rows_html += f"<tr><td>{row[0]}</td><td style='text-align:right'>{row[1]}</td><td style='text-align:left'>{row[2]}</td></tr>\n"

        # Format the input summary line
        if _has_prefixed:
            vin_s = f"{PrefixedFloat(self.vin_nom):.2h}V"
            vout_s = f"{PrefixedFloat(self.vout):.2h}V"
            iout_s = f"{PrefixedFloat(self.iout_max):.2h}A"
            fsw_s = f"{PrefixedFloat(self.fsw):.2h}Hz"
            vrip_s = f"{PrefixedFloat(self.vripple_max):.2h}V"
        else:
            vin_s = pp(self.vin_nom, 'V')
            vout_s = pp(self.vout, 'V')
            iout_s = pp(self.iout_max, 'A')
            fsw_s = pp(self.fsw, 'Hz')
            vrip_s = pp(self.vripple_max, 'V')

        return f"""
<div style="font-family: 'DejaVu Sans', sans-serif; margin: 10px 0;">
  <h4 style="color: #b58900; margin-bottom: 8px;">⚡ Buck Converter Design</h4>
  <table style="border-collapse: collapse; width: auto;">
    <thead>
      <tr style="background: #eee8d5;">
        <th style="padding: 6px 12px; text-align: left; border-bottom: 2px solid #b58900;">Parameter</th>
        <th style="padding: 6px 12px; text-align: right; border-bottom: 2px solid #b58900;">Value</th>
        <th style="padding: 6px 12px; text-align: left; border-bottom: 2px solid #b58900;">Unit</th>
      </tr>
    </thead>
    <tbody>
{rows_html}    </tbody>
  </table>
  <p style="color: #657b83; font-size: 0.85em; margin-top: 4px;">
    {vin_s} → {vout_s} @ {iout_s} |
    Fsw = {fsw_s} |
    Vripple ≤ {vrip_s}
  </p>
</div>"""

    def _prefixed_table(self) -> list:
        """Return results as [name, formatted_value, unit] using prefixed package."""
        if _has_prefixed:
            def fmt(val, unit):
                return [f"{PrefixedFloat(val):.2h}{unit}"]
            rows = [
                ["Duty cycle", f"{self.duty*100:.1f}", "%"],
                ["Inductor", f"{PrefixedFloat(self.inductor):.2h}", "H"],
                ["Inductor ripple", f"{PrefixedFloat(self.inductor_ripple):.2h}", "A"],
                ["Inductor peak", f"{PrefixedFloat(self.inductor_peak):.2h}", "A"],
                ["Output capacitor", f"{PrefixedFloat(self.output_cap):.2h}", "F"],
                ["Input capacitor", f"{PrefixedFloat(self.input_cap):.2h}", "F"],
                ["MOSFET Vds", f"{PrefixedFloat(self.mosfet_voltage):.2h}", "V"],
                ["MOSFET Irms", f"{PrefixedFloat(self.mosfet_current):.2h}", "A"],
                ["Diode Vrrm", f"{PrefixedFloat(self.diode_voltage):.2h}", "V"],
                ["Diode Iavg", f"{PrefixedFloat(self.diode_current):.2h}", "A"],
            ]
            return rows
        else:
            return self.to_table()

    def __str__(self) -> str:
        """Pretty-print with SI prefixes, suitable for `print()`."""
        return self.summary()

    def __repr__(self) -> str:
        return (
            f"BuckSpecification(vin={self.vin_nom}, vout={self.vout}, "
            f"iout={self.iout_max}, fsw={self.fsw}, vripple={self.vripple_max})"
        )


def design_buck(
    vin: float,
    vout: float,
    iout: float,
    fsw: float,
    vripple: float,
    vin_min: Optional[float] = None,
    vin_max: Optional[float] = None,
    il_ripple_pct: float = 0.30,
    diode_vf: float = 0.7,
    mosfet_rdson: float = 0.020,
    esr_cap: float = 0.005,
    as_dict: bool = False,
    as_dataframe: bool = False,
):
    """Design a buck converter and return results in a convenient format.

    The default return is a `BuckSpecification` object that renders as
    a pretty HTML table in Jupyter notebooks (via `_repr_html_`).

    Args:
        vin: Nominal input voltage (V)
        vout: Output voltage (V)
        iout: Maximum output current (A)
        fsw: Switching frequency (Hz)
        vripple: Maximum output voltage ripple (V)
        vin_min: Minimum input voltage (optional)
        vin_max: Maximum input voltage (optional)
        il_ripple_pct: Target inductor current ripple fraction (default 30%)
        diode_vf: Diode forward voltage drop (default 0.7V)
        mosfet_rdson: MOSFET on-resistance (default 20mΩ)
        esr_cap: Output capacitor ESR estimate (default 5mΩ)
        as_dict: If True, return a plain dict instead of BuckSpecification
        as_dataframe: If True, return a pandas DataFrame (requires pandas)

    Returns:
        BuckSpecification, dict, or pandas DataFrame with results.

    Jupyter usage:
        results = design_buck(12, 3.3, 2, 300e3, 0.01)
        results  # renders as a pretty HTML table

        # Or as a DataFrame:
        df = design_buck(12, 3.3, 2, 300e3, 0.01, as_dataframe=True)
        df
    """
    spec = BuckSpecification(
        vin_nom=vin, vout=vout, iout_max=iout,
        fsw=fsw, vripple_max=vripple,
        vin_min=vin_min, vin_max=vin_max,
        il_ripple_pct=il_ripple_pct,
        diode_vf=diode_vf, mosfet_rdson=mosfet_rdson,
        esr_cap=esr_cap,
    )
    spec.design()
    if as_dict:
        return asdict(spec)
    if as_dataframe:
        return spec.to_dataframe()
    return spec
