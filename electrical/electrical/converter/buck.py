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
    from electrical.converter.buck import design_buck, nearest_standard

    spec = design_buck(
        vin=12, vout=3.3, iout=2.0,
        fsw=300e3, vripple=0.01,
        il_ripple_pct=0.30  # 30% inductor current ripple
    )

    for k, v in spec.items():
        print(f"{k:25s}: {v}")
"""

from dataclasses import dataclass, field, asdict
from typing import Optional
import math

# ── Standard resistor/series values ──────────────────────────────────────

E12_BASE = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]
E24_BASE = [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
            3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1]
E48_BASE = [1.00, 1.05, 1.10, 1.15, 1.21, 1.27, 1.33, 1.40, 1.47, 1.54,
            1.62, 1.69, 1.78, 1.87, 1.96, 2.05, 2.15, 2.26, 2.37, 2.49,
            2.61, 2.74, 2.87, 3.01, 3.16, 3.32, 3.48, 3.65, 3.83, 4.02,
            4.22, 4.42, 4.64, 4.87, 5.11, 5.36, 5.62, 5.90, 6.19, 6.49,
            6.81, 7.15, 7.50, 7.87, 8.25, 8.66, 9.09, 9.53]

def _generate_series(base, decades=(-2, 7)):
    """Generate standard values over a range of decades.

    Args:
        base: List of base values normalized to [1.0, 10.0) range.
              E12_BASE = [1.0, 1.2, 1.5, ...]
              E48_BASE = [1.00, 1.05, 1.10, ...]
        decades: Tuple of (min_exponent, max_exponent)

    Returns:
        Sorted list of standard values.
    """
    vals = []
    for d in range(decades[0], decades[1] + 1):
        mul = 10 ** d
        for b in base:
            vals.append(b * mul)
    return sorted(vals)

# Generate standard series
# Resistor range: 0.01Ω to 10MΩ  (9 decades)
E12_RESISTOR = _generate_series(E12_BASE, decades=(-2, 7))
E24_RESISTOR = _generate_series(E24_BASE, decades=(-2, 7))
E48_RESISTOR = _generate_series(E48_BASE, decades=(-2, 7))

# Component range: 1nH/pF to 1kH/F (12 decades — covers everything)
E12_COMPONENT = _generate_series(E12_BASE, decades=(-9, 3))


def nearest_standard(value, series: str = "E24", component: bool = False) -> float:
    """Find the nearest standard E-series value.

    Args:
        value: Desired value
        series: "E12", "E24", or "E48"
        component: If True, use wide component range (nH/pF to H/F)
                   instead of resistor range (0.01Ω–10MΩ).

    Returns:
        Nearest standard value from the selected series.
    """
    if component:
        pool = {"E12": E12_COMPONENT, "E24": E12_COMPONENT, "E48": E12_COMPONENT}.get(series.upper(), E12_COMPONENT)
    else:
        pool = {"E12": E12_RESISTOR, "E24": E24_RESISTOR, "E48": E48_RESISTOR}.get(series.upper(), E24_RESISTOR)
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
    # Nearest of two candidates
    if lo >= len(pool):
        return pool[-1]
    if hi < 0:
        return pool[0]
    return pool[lo] if (pool[lo] - value) < (value - pool[hi]) else pool[hi]


def nearest_inductor(value: float) -> float:
    """Find the nearest standard inductor value (E12 series, from 1 nH to 1 kH)."""
    return nearest_standard(value, "E12", component=True)


def nearest_capacitor(value: float) -> float:
    """Find the nearest standard capacitor value (E12 series, from 1 pF to 1 F)."""
    return nearest_standard(value, "E12", component=True)


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
        """Return a human-readable summary string."""
        lines = [
            "═" * 55,
            "  Buck Converter Design Summary",
            "═" * 55,
            f"  Vin = {self.vin_nom:.1f} V  ({self.vin_min or self.vin_nom*0.9:.1f} – {self.vin_max or self.vin_nom*1.1:.1f} V)",
            f"  Vout = {self.vout:.2f} V  @  {self.iout_max:.2f} A  (max)",
            f"  Fsw = {self.fsw/1000:.0f} kHz",
            f"  Vripple(max) = {self.vripple_max*1000:.1f} mV",
            "─" * 55,
            f"  Duty cycle (nom)      : {self.duty*100:.1f} %",
            f"  Inductor              : {self.inductor*1e6:.0f} µH  (ΔIL = {self.inductor_ripple*1000:.0f} mA, peak = {self.inductor_peak*1000:.0f} mA)",
            f"  Output capacitor      : {self.output_cap*1e6:.0f} µF  (ESR ≤ {self.output_cap_esr*1000:.0f} mΩ)",
            f"  Input capacitor       : {self.input_cap*1e6:.0f} µF",
            "─" * 55,
            f"  MOSFET Vds(max)       : {self.mosfet_voltage:.1f} V",
            f"  MOSFET Irms           : {self.mosfet_current*1000:.0f} mA",
            f"  Diode Vrrm            : {self.diode_voltage:.1f} V",
            f"  Diode Iavg            : {self.diode_current*1000:.0f} mA",
            "═" * 55,
        ]
        return "\n".join(lines)

    def to_table(self) -> list:
        """Return results as a list of [parameter, value, unit] for org-mode tables."""
        return [
            ["Duty cycle", f"{self.duty*100:.1f}", "%"],
            ["Inductor", f"{self.inductor*1e6:.0f}", "µH"],
            ["Inductor ripple", f"{self.inductor_ripple*1000:.0f}", "mA"],
            ["Inductor peak", f"{self.inductor_peak*1000:.0f}", "mA"],
            ["Output capacitor", f"{self.output_cap*1e6:.0f}", "µF"],
            ["Input capacitor", f"{self.input_cap*1e6:.0f}", "µF"],
            ["MOSFET Vds", f"{self.mosfet_voltage:.1f}", "V"],
            ["MOSFET Irms", f"{self.mosfet_current*1000:.0f}", "mA"],
            ["Diode Vrrm", f"{self.diode_voltage:.1f}", "V"],
            ["Diode Iavg", f"{self.diode_current*1000:.0f}", "mA"],
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
