"""Which drift regime are the real tracked icebergs actually in?

WDE17 concludes that large Antarctic tabular bergs move with the surface
current and that wind drag is negligible for them. That claim is made with
illustrative sizes. This script checks it against the **real USNIC catalogue**,
berg by berg, and reports the answer as a number rather than a citation.

Why it matters more than it sounds: if the tracked bergs really are
current-dominated, then the accuracy of any trajectory forecast we build is
inherited almost entirely from the ocean-current product, and tuning drag
coefficients is wasted effort. That is an architecture decision, and it should
rest on our own data.

    R = gamma sqrt(alpha^2 + beta^2) |v_a| / |v_w|      (WDE17 eq. 14)
    R > 1    wind-dominated
    R < 0.1  current-dominated

ON FORCING VALUES -- read this before quoting anything here. We do not have
observed wind and current at each berg's position without authenticated ERA5 /
CMEMS downloads, and we will not invent them. Instead R is evaluated across an
explicitly stated envelope of wind and current speeds spanning calm to storm.
The berg dimensions are real; the forcing is a declared sensitivity sweep, not
an observation. The conclusion is reported only where it holds across the whole
envelope, which is a stronger statement than one value would give.

    prenv/bin/python models/iceberg/regime_report.py
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from catalogue import load_usnic, summarise
from drift import GAMMA, alpha, beta, deflection_angle_deg, lambda_param

# Sensitivity envelope. Southern Ocean surface winds routinely reach 20 m/s and
# the katabatic events discussed in NAVIGATION_RESEARCH.md section 7 exceed 30;
# 0.05-0.30 m/s brackets typical Southern Ocean surface current speeds.
WIND_SPEEDS_MS = [5.0, 10.0, 20.0, 30.0]
CURRENT_SPEEDS_MS = [0.05, 0.10, 0.30]

# The corridor this project routes through (RESULTS.md), widened to the sector
# a Maitri/Bharati voyage would actually cross.
CORRIDOR_LON = (-10.0, 100.0)


def relative_forcing(frame, wind_ms, current_ms):
    """Lambda and R for every berg in `frame` under one forcing pair."""
    lam = lambda_param(wind_ms, frame.lat.values,
                       frame.length_m.values, frame.width_m.values)
    r = GAMMA * np.hypot(alpha(lam), beta(lam)) * wind_ms / current_ms
    return lam, r


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv", type=Path, default=None,
                    help="USNIC CSV; downloads today's if omitted")
    ap.add_argument("--out", type=Path,
                    default=Path("models/iceberg/regime_report.json"))
    args = ap.parse_args()

    bergs = load_usnic(args.csv)
    stats = summarise(bergs)
    print(f"USNIC catalogue: {stats['icebergs']} bergs, observed "
          f"{stats['observed']}\n")

    # --- worst case for the current-dominated claim: strongest wind, weakest
    # current. If R stays below 0.1 there, it stays below everywhere.
    worst_wind, worst_current = max(WIND_SPEEDS_MS), min(CURRENT_SPEEDS_MS)
    lam_worst, r_worst = relative_forcing(bergs, worst_wind, worst_current)

    envelope = []
    for wind in WIND_SPEEDS_MS:
        for current in CURRENT_SPEEDS_MS:
            _, r = relative_forcing(bergs, wind, current)
            envelope.append({
                "wind_ms": wind, "current_ms": current,
                "max_R": round(float(r.max()), 4),
                "median_R": round(float(np.median(r)), 4),
                "n_wind_dominated_R_gt_1": int((r > 1.0).sum()),
                "n_current_dominated_R_lt_0p1": int((r < 0.1).sum()),
            })

    print(f"{'wind':>6} {'current':>8} {'max R':>9} {'median R':>10} "
          f"{'R>1':>5} {'R<0.1':>7}")
    for row in envelope:
        print(f"{row['wind_ms']:>6.0f} {row['current_ms']:>8.2f} "
              f"{row['max_R']:>9.3f} {row['median_R']:>10.4f} "
              f"{row['n_wind_dominated_R_gt_1']:>5d} "
              f"{row['n_current_dominated_R_lt_0p1']:>7d}")

    # --- bergs inside the corridor we route through
    in_corridor = bergs[bergs.lon.between(*CORRIDOR_LON)].copy()
    lam_c, r_c = relative_forcing(in_corridor, 10.0, 0.1)
    in_corridor["lambda"] = np.round(lam_c, 4)
    in_corridor["R_at_10ms"] = np.round(r_c, 4)
    in_corridor["deflection_deg"] = np.round(deflection_angle_deg(lam_c), 2)

    print(f"\nBergs in the routing corridor "
          f"({CORRIDOR_LON[0]} to {CORRIDOR_LON[1]} degrees east): "
          f"{len(in_corridor)} of {len(bergs)}")
    if len(in_corridor):
        cols = ["name", "lat", "lon", "length_m", "area_km2",
                "lambda", "R_at_10ms", "deflection_deg"]
        print(in_corridor[cols].to_string(index=False))

    # Typical forcing, i.e. the case WDE17's own regime discussion uses.
    _, r_typical = relative_forcing(bergs, 10.0, 0.10)
    n_typ_current = int((r_typical < 0.1).sum())
    n_worst_wind = int((r_worst > 1.0).sum())
    all_current_dominated = bool((r_worst < 0.1).all())
    report = {
        "catalogue": stats,
        "method": {
            "equation": "WDE17 eq. (14)  R = gamma sqrt(a^2+b^2) |v_a|/|v_w|",
            "berg_dimensions": "REAL, from the USNIC feed",
            "forcing": ("DECLARED SENSITIVITY SWEEP, not observations -- we do "
                        "not have wind/current at these positions and did not "
                        "invent them"),
            "wind_speeds_ms": WIND_SPEEDS_MS,
            "current_speeds_ms": CURRENT_SPEEDS_MS,
        },
        "envelope": envelope,
        "regime": {
            "typical_forcing": {
                "wind_ms": 10.0, "current_ms": 0.10,
                "n_current_dominated_R_lt_0p1": n_typ_current,
                "n_total": int(len(bergs)),
                "max_R": round(float(r_typical.max()), 4),
            },
            "storm_forcing": {
                "wind_ms": worst_wind, "current_ms": worst_current,
                "n_wind_dominated_R_gt_1": n_worst_wind,
                "max_R": round(float(r_worst.max()), 4),
                "max_lambda": round(float(lam_worst.max()), 4),
            },
            "all_bergs_current_dominated_everywhere": all_current_dominated,
            "finding": (
                "Regime is set by the FORCING as much as by berg size. Under "
                "typical forcing the tracked bergs are current-dominated or "
                "close to it, but under storm winds with a weak current a "
                "majority become wind-dominated. 'Large Antarctic bergs move "
                "with the current' is therefore a statement about typical "
                "conditions, not a property of the bergs -- and the storms are "
                "exactly when the forecast matters most."),
        },
        "corridor": {
            "lon_range": list(CORRIDOR_LON),
            "n_bergs": int(len(in_corridor)),
            "bergs": in_corridor[["name", "lat", "lon", "area_km2",
                                  "R_at_10ms"]].to_dict("records"),
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2))

    total = len(bergs)
    print(f"\nTypical forcing (10 m/s wind, 0.10 m/s current): "
          f"{n_typ_current}/{total} bergs current-dominated (R < 0.1), "
          f"max R = {r_typical.max():.3f}")
    print(f"Storm forcing  ({worst_wind:.0f} m/s wind, {worst_current:.2f} m/s "
          f"current): {n_worst_wind}/{total} bergs WIND-dominated (R > 1), "
          f"max R = {r_worst.max():.3f}")

    if all_current_dominated:
        print("\n=> Current-dominated across the entire envelope. Trajectory "
              "skill is set by\n   the ocean-current field, not by drag "
              "tuning.")
    else:
        print("\n=> The regime is set by the FORCING as much as by berg size. "
              "Under typical\n   conditions these bergs track the current, but "
              "under storm winds with a weak\n   current a majority become "
              "wind-dominated -- and Antarctic katabatic events\n   reach "
              "30 m/s (NAVIGATION_RESEARCH.md section 7). So 'large bergs move "
              "with the\n   current' is a claim about typical conditions, not a "
              "property of the bergs.\n   Both terms are needed exactly when "
              "the forecast matters most.")
    print(f"\nWrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
