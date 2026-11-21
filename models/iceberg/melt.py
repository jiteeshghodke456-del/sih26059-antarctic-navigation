"""Iceberg melt terms (feature F4) — AN ESTIMATE, and labelled as one.

Implements the three deterioration terms the operational literature uses for
iceberg modelling — the set Keghouche, Bertino & Lisæter (2010, JGR 114,
C06012) assembled for the Barents/GIN seas model and that OpenBerg documents
(OpenDrift is GPL-2.0, so nothing is imported from it; these formulas are
reimplemented from the papers):

    basal turbulent melt   El-Tahan et al. (1987) / Weeks & Campbell (1973)
        Mb = 0.58 |v_w - v_i|^0.8 (T_w - T_f) / L^0.2        [m/day]
    buoyant convection     Bigg et al. (1997)
        Mv = 7.62e-3 T_w + 1.29e-3 T_w^2                     [m/day]
    wave erosion           Gladstone et al. (2001) / Bigg et al. (1997)
        Me = (1/12) Ss (T_w + 2)                             [m/day]
        with Ss = -5 + sqrt(32 + 2 Hs)  (sea-state proxy from Hs)

T_w is the sea-surface temperature in °C, T_f the freezing point (-1.92 °C
for Antarctic shelf salinity ~34.5), v the water-relative speed in m/s, L the
waterline length in m, Hs the significant wave height in m.

Honesty box, which every output of this module must carry:
- the coefficients were tuned for Arctic bergs orders of magnitude smaller
  than USNIC giants; applying them to a 50 km tabular berg extrapolates far
  outside their calibration;
- keel draught and thickness of USNIC bergs are not published; the freshwater
  numbers use an assumed 250 m thickness, stated in the output;
- this is a bulk estimate of freshwater input, not a deterioration forecast.
"""
from __future__ import annotations

import numpy as np

T_FREEZE_C = -1.92   # °C, S ≈ 34.5 (Antarctic shelf water)
ASSUMED_THICKNESS_M = 250.0  # typical tabular giant; USNIC publishes no draught


def basal_melt_m_per_day(rel_speed_ms, sst_c, waterline_length_m):
    """El-Tahan/Weeks-Campbell forced-convection basal melt."""
    dT = np.maximum(np.asarray(sst_c, float) - T_FREEZE_C, 0.0)
    v = np.maximum(np.asarray(rel_speed_ms, float), 0.0)
    L = np.maximum(np.asarray(waterline_length_m, float), 1.0)
    return 0.58 * v ** 0.8 * dT / L ** 0.2


def buoyant_convection_m_per_day(sst_c):
    """Bigg et al. (1997) sidewall melt from thermal convection."""
    t = np.maximum(np.asarray(sst_c, float), 0.0)
    return 7.62e-3 * t + 1.29e-3 * t ** 2


def wave_erosion_m_per_day(hs_m, sst_c):
    """Gladstone et al. (2001) wave erosion with the Hs-based sea state."""
    hs = np.maximum(np.asarray(hs_m, float), 0.0)
    ss = -5.0 + np.sqrt(32.0 + 2.0 * hs)
    return np.maximum(ss, 0.0) * (np.asarray(sst_c, float) + 2.0) / 12.0


def freshwater_m3_per_day(length_m, width_m, rel_speed_ms, sst_c, hs_m,
                          thickness_m: float = ASSUMED_THICKNESS_M):
    """Bulk freshwater input of one berg, m³ of ice per day.

    Basal melt acts on the base area (L·W); sidewall terms act on the
    submerged perimeter (≈0.83 draught fraction, Archimedes for ρi/ρw).
    """
    L = float(length_m)
    W = float(width_m)
    draught = 0.83 * float(thickness_m)
    base = L * W
    wall = 2.0 * (L + W) * draught
    mb = basal_melt_m_per_day(rel_speed_ms, sst_c, L)
    mv = buoyant_convection_m_per_day(sst_c)
    me = wave_erosion_m_per_day(hs_m, sst_c)
    return float(mb * base + (mv + me) * wall)
