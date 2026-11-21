#!/usr/bin/env python3
"""F3: do eddies change iceberg tracks?

    python scripts/berg_resolution.py

Reruns the slice-5 USNIC hindcast with the analysis currents at native 1/12°,
then block-averaged to ~1/4° and ~1° (same coarsen-and-repeat trick as F1, so
the land mask geometry is unchanged except cells averaged across). The current
field is the dominant forcing being varied (wind is held at zero in both
variants, a stated limitation — measured R medians 0.25).

Writes dakshin/figures/berg_resolution.json and a section's numbers for
docs/RESOLUTION_STUDY.md.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "dakshin"))

from berg_forecast import STATUS_OK, CurrentField  # noqa: E402
from berg_hindcast import load_field, run_segments  # noqa: E402
from realforecast_hindcast import block_coarsen  # noqa: E402

OUT = ROOT / "dakshin" / "figures" / "berg_resolution.json"
FACTORS = {1: "1/12°", 3: "1/4°", 12: "1°"}


def coarsen_field(field_: CurrentField, f: int) -> CurrentField:
    if f == 1:
        return field_
    u = np.stack([block_coarsen(field_.u[k], f) for k in range(len(field_.t))])
    v = np.stack([block_coarsen(field_.v[k], f) for k in range(len(field_.t))])
    return CurrentField(u, v, field_.lat, field_.lon, field_.t)


def summarize(segments: list[dict]) -> dict:
    ok = [s for s in segments if s["status"] == STATUS_OK]
    moving = [s for s in ok if s["persistence_km"] > 3.0]
    return {
        "n_segments": len(segments),
        "n_ok": len(ok),
        "n_grounded_or_unknown": len(segments) - len(ok),
        "median_error_km_per_day": round(float(np.median(
            [s["error_km_per_day"] for s in ok])), 2) if ok else None,
        "moving_median_error_km_per_day": round(float(np.median(
            [s["error_km_per_day"] for s in moving])), 2) if moving else None,
    }


def main() -> int:
    base = load_field()
    results = {}
    for f, label in FACTORS.items():
        print(f"\n=== currents at {label} ===")
        results[label] = summarize(run_segments(coarsen_field(base, f)))
        print(label, results[label])

    payload = {
        "generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "question": "does eddy-resolving current resolution matter for "
                    "giant-berg drift in this corridor?",
        "method": "slice-5 USNIC hindcast repeated with currents block-"
                  "averaged to each resolution; same segments, same physics",
        "caveats": [
            "coarsening one model's currents is not running a coarser model",
            "persistence (berg did not move) already beats every variant on "
            "this mostly-grounded sample — see berg_hindcast.json",
        ],
        "resolutions": results,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
