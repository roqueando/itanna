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

from electrical.utils.prefixed import pp, p, to_table_row
from electrical.utils.eseries import (
    nearest_value as nearest_standard,
    nearest_inductor,
    nearest_capacitor,
)


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

    def summary(self) -> str:
        """Return a human-readable summary string with SI-prefixed values."""
        lines = [
            "═" * 55,
            "  Buck Converter Design Summary",
            "═" * 55,
            f"  Vin = {pp(self.vin_nom, 'V')}  ({pp(self.vin_min or self.vin_nom*0.9, 'V')} – {pp(self.vin_max or self.vin_nom*1.1, 'V')})",
            f"  Vout = {pp(self.vout, 'V')}  @  {pp(self.iout_max, 'A')}  (max)",
            f"  Fsw = {pp(self.fsw, 'Hz')}",
            f"  Vripple(max) = {pp(self.vripple_max, 'V')}",
            "─" * 55,
            f"  Duty cycle (nom)      : {self.duty*100:.1f} %",
            f"  Inductor              : {pp(self.inductor, 'H')}  (ΔIL = {pp(self.inductor_ripple, 'A')}, peak = {pp(self.inductor_peak, 'A')})",
            f"  Output capacitor      : {pp(self.output_cap, 'F')}  (ESR ≤ {pp(self.output_cap_esr, 'Ω')})",
            f"  Input capacitor       : {pp(self.input_cap, 'F')}",
            "─" * 55,
            f"  MOSFET Vds(max)       : {pp(self.mosfet_voltage, 'V')}",
            f"  MOSFET Irms           : {pp(self.mosfet_current, 'A')}",
            f"  Diode Vrrm            : {pp(self.diode_voltage, 'V')}",
            f"  Diode Iavg            : {pp(self.diode_current, 'A')}",
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
    as_dict: bool = True,
):
    """Convenience function to design a buck converter.

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
        as_dict: If True, return dict; if False, return BuckSpecification

    Returns:
        Dict or BuckSpecification with all computed values.
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
    return spec
