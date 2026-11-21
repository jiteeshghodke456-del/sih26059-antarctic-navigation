#!/usr/bin/env python3
"""F4: estimated freshwater input along each giant berg's forecast track.

    python scripts/berg_melt.py [cycle YYYY-MM-DD]

For every USNIC giant in the corridor box: forecast its 0–9 day track on the
cycle's forecast currents (slice 5 machinery), sample forecast SST and daily
max wave height along the track, and integrate the literature melt terms
(models/iceberg/melt.py — Keghouche et al. 2010's set) into m³/day of
freshwater. EVERYTHING here is labelled an estimate: the coefficients are
Arctic-calibrated, and thickness is an assumed 250 m (USNIC publishes none).

Writes dakshin/figures/berg_melt.json.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import xarray as xr

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "dakshin"))
sys.path.insert(0, str(ROOT / "models" / "iceberg"))

from berg_forecast import CurrentField, forecast_track  # noqa: E402
from catalogue import load_usnic  # noqa: E402
from melt import ASSUMED_THICKNESS_M, freshwater_m3_per_day  # noqa: E402

ARCHIVE = ROOT / "data" / "cmems_forecast_archive"
OUT = ROOT / "dakshin" / "figures" / "berg_melt.json"
BOX = {"lon": (0.0, 80.0), "lat": (-78.0, -55.0)}


def nearest(ds_lat, ds_lon, grid, lat, lon):
    i = int(np.clip(np.searchsorted(ds_lat, lat), 1, len(ds_lat) - 1))
    j = int(np.clip(np.searchsorted(ds_lon, lon), 1, len(ds_lon) - 1))
    return float(grid[i, j])


def main() -> int:
    cycle = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 \
        else dt.date(2026, 11, 21)
    cur = CurrentField.from_files([ARCHIVE / f"cmems_cur_{cycle}.nc"])
    sst_ds = xr.open_dataset(ARCHIVE / f"cmems_sst_{cycle}.nc")
    sst = sst_ds["thetao"].values
    if sst.ndim == 4:
        sst = sst[:, 0]
    wav_ds = xr.open_dataset(ARCHIVE / f"cmems_wav_{cycle}.nc")
    hs = wav_ds["VHM0_dmax"].values

    latest = sorted((ROOT / "data" / "icebergs" / "archive")
                    .glob("AntarcticIcebergs_*.csv"))[-1]
    bergs = load_usnic(latest)
    bergs = bergs[(bergs.lon >= BOX["lon"][0]) & (bergs.lon <= BOX["lon"][1])
                  & (bergs.lat >= BOX["lat"][0]) & (bergs.lat <= BOX["lat"][1])]

    start = dt.datetime(cycle.year, cycle.month, cycle.day, 12)
    results = []
    for _, b in bergs.iterrows():
        tr = forecast_track(b["name"], b.lat, b.lon, b.length_m, b.width_m,
                            cur, start, days=9)
        daily = []
        for k, (t, la, lo) in enumerate(zip(tr.times, tr.lats, tr.lons)):
            if t.hour != 12:
                continue
            day = min((t.date() - cycle).days, sst.shape[0] - 1, hs.shape[0] - 1)
            t_w = nearest(sst_ds["latitude"].values, sst_ds["longitude"].values,
                          sst[day], la, lo)
            h_s = nearest(wav_ds["latitude"].values, wav_ds["longitude"].values,
                          hs[day], la, lo)
            u, v = cur.sample(lo, la, t)
            if not all(np.isfinite([t_w, u, v])):
                continue
            h_s = h_s if np.isfinite(h_s) else 0.0  # ice-covered: waves damped
            fw = freshwater_m3_per_day(b.length_m, b.width_m,
                                       float(np.hypot(u, v)), t_w, h_s)
            daily.append({"date": str(t.date()), "sst_c": round(t_w, 2),
                          "hs_m": round(h_s, 2),
                          "freshwater_m3_per_day": round(fw, 0)})
        results.append({
            "berg": b["name"], "area_km2": b.area_km2,
            "track_status": tr.status,
            "n_days_estimated": len(daily),
            "mean_freshwater_m3_per_day": round(float(np.mean(
                [d["freshwater_m3_per_day"] for d in daily])), 0) if daily else None,
            "daily": daily,
        })
        print(f"{b['name']:6s} {len(daily)} days, mean "
              f"{results[-1]['mean_freshwater_m3_per_day']} m3/day {tr.status}")

    payload = {
        "generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "cycle": str(cycle),
        "label": "ESTIMATE — Arctic-calibrated melt coefficients (Keghouche "
                 "et al. 2010 set) extrapolated to tabular giants; assumed "
                 f"thickness {ASSUMED_THICKNESS_M:.0f} m (USNIC publishes none)",
        "inputs": {"currents": f"cmems_cur_{cycle}.nc",
                   "sst": f"cmems_sst_{cycle}.nc",
                   "waves": f"cmems_wav_{cycle}.nc (daily max)",
                   "bergs": latest.name},
        "bergs": results,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
