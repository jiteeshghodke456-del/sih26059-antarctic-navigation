"""Audit the local NSIDC archive for retrieval artifacts.

Answers three questions with numbers rather than anecdote:

  1. How often does the land-spillover filter fire, and how many cells does it
     silently set to 0.0?
  2. How many cells per day are "hard zero flush against heavy ice" -- the
     physical tell that needs no QA flag?
  3. How bad is it in the places we actually route to: the approaches to
     Bharati and Maitri?

Writes isih/figures/ice_quality_audit.json.

    prenv/bin/python isih/audit_ice_quality.py
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import xarray as xr
from pyproj import Transformer

from ice_quality import (QA_LAND_SPILLOVER, QA_NO_INPUT, hard_zero_next_to_ice,
                         load_sic)

NSIDC_DIR = Path(__file__).parent / "data" / "nsidc_sic"

# Station approaches: the water a resupply ship must actually cross.
STATIONS = {"Bharati": (-69.4, 76.2), "Maitri": (-70.8, 11.7)}
APPROACH_RADIUS_CELLS = 8      # 8 x 25 km = 200 km box around the station


def station_windows() -> dict[str, tuple[slice, slice]]:
    """Grid-index windows around each station."""
    sample = sorted(NSIDC_DIR.glob("sic_pss25_*.nc"))[0]
    ds = xr.open_dataset(sample)
    xs, ys = ds.x.values, ds.y.values
    fwd = Transformer.from_crs("EPSG:4326", "EPSG:3412", always_xy=True)

    windows = {}
    for name, (lat, lon) in STATIONS.items():
        x, y = fwd.transform(lon, lat)
        j = int(np.abs(ys - y).argmin())
        i = int(np.abs(xs - x).argmin())
        r = APPROACH_RADIUS_CELLS
        windows[name] = (slice(max(0, j - r), j + r + 1),
                         slice(max(0, i - r), i + r + 1))
    return windows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path,
                    default=Path("isih/figures/ice_quality_audit.json"))
    args = ap.parse_args()

    files = sorted(NSIDC_DIR.glob("sic_pss25_*.nc"))
    if not files:
        print("no NSIDC files found")
        return 1
    windows = station_windows()

    spillover_cells = []
    no_input_cells = []
    hard_zero_cells = []
    per_station = {name: {"days_with_suspect": 0, "suspect_cell_days": 0,
                          "worst_day": None, "worst_count": 0}
                   for name in STATIONS}
    days_any = 0

    for n, path in enumerate(files, 1):
        ds = xr.open_dataset(path)
        qa = np.nan_to_num(
            ds["cdr_seaice_conc_qa_flag"].isel(time=0).values, nan=0
        ).astype(np.int32)

        spill = (qa & QA_LAND_SPILLOVER) != 0
        noin = (qa & QA_NO_INPUT) != 0
        spillover_cells.append(int(spill.sum()))
        no_input_cells.append(int(noin.sum()))

        raw, _ = load_sic(path, apply_qa=False)
        hz = hard_zero_next_to_ice(raw)
        hard_zero_cells.append(int(hz.sum()))
        if hz.any():
            days_any += 1

        suspect = spill | noin
        for name, (js, iss) in windows.items():
            cnt = int(suspect[js, iss].sum())
            if cnt:
                per_station[name]["days_with_suspect"] += 1
                per_station[name]["suspect_cell_days"] += cnt
                if cnt > per_station[name]["worst_count"]:
                    per_station[name]["worst_count"] = cnt
                    per_station[name]["worst_day"] = path.name.split("_")[2]

        if n % 200 == 0:
            print(f"  {n}/{len(files)} days ...", flush=True)

    box_cells = (2 * APPROACH_RADIUS_CELLS + 1) ** 2
    out = {
        "archive": {"files": len(files),
                    "first": files[0].name.split("_")[2],
                    "last": files[-1].name.split("_")[2]},
        "land_spillover": {
            "mean_cells_per_day": round(float(np.mean(spillover_cells)), 1),
            "max_cells_per_day": int(np.max(spillover_cells)),
            "days_affected": int(sum(1 for c in spillover_cells if c > 0)),
        },
        "no_input_data": {
            "mean_cells_per_day": round(float(np.mean(no_input_cells)), 1),
            "max_cells_per_day": int(np.max(no_input_cells)),
        },
        "hard_zero_next_to_heavy_ice": {
            "mean_cells_per_day": round(float(np.mean(hard_zero_cells)), 1),
            "max_cells_per_day": int(np.max(hard_zero_cells)),
            "days_affected": days_any,
            "pct_of_days": round(100.0 * days_any / len(files), 1),
        },
        "station_approaches": {
            name: {**vals,
                   "box_cells": box_cells,
                   "pct_of_days_affected": round(
                       100.0 * vals["days_with_suspect"] / len(files), 1)}
            for name, vals in per_station.items()
        },
        "note": ("A cell flagged Land_spillover_filter_applied is written as "
                 "0.0 inside valid_range, so an unguarded reader treats it as "
                 "open water."),
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    print(f"\nWrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
