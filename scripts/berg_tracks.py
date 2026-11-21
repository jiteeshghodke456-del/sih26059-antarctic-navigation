#!/usr/bin/env python3
"""Forecast drift tracks for the corridor's giants, for the chart's vector
arrows (owner request 2026-11-22).

    python scripts/berg_tracks.py [cycle YYYY-MM-DD]

For each USNIC giant in the box: integrate 0-9 days on the cycle's forecast
currents (slice 5 machinery, grounding-aware v2), and emit daily positions
plus the net drift vector. Bergs the model holds as grounded get a zero
vector and say so — the chart must show "held", not invent motion.

Writes dakshin/figures/berg_tracks.json.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "dakshin"))

from berg_forecast import (BathymetryGrid, CurrentField, forecast_track,  # noqa: E402
                           great_circle_km)
from models.iceberg.catalogue import load_usnic  # noqa: E402

ARCHIVE = ROOT / "data" / "cmems_forecast_archive"
OUT = ROOT / "dakshin" / "figures" / "berg_tracks.json"
BOX = {"lon": (0.0, 80.0), "lat": (-78.0, -55.0)}


def main() -> int:
    cycle = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 \
        else dt.date(2026, 11, 21)
    cur = CurrentField.from_files([ARCHIVE / f"cmems_cur_{cycle}.nc"])
    bathy = BathymetryGrid()
    latest = sorted((ROOT / "data" / "icebergs" / "archive")
                    .glob("AntarcticIcebergs_*.csv"))[-1]
    bergs = load_usnic(latest)
    inside = bergs[(bergs.lon >= BOX["lon"][0]) & (bergs.lon <= BOX["lon"][1])
                   & (bergs.lat >= BOX["lat"][0]) & (bergs.lat <= BOX["lat"][1])]

    start = dt.datetime(cycle.year, cycle.month, cycle.day, 12)
    tracks = []
    for _, b in inside.iterrows():
        tr = forecast_track(b["name"], b.lat, b.lon, b.length_m, b.width_m,
                            cur, start, days=9, bathymetry=bathy)
        daily = [{"day": k // 24, "lat": round(la, 4), "lon": round(lo, 4)}
                 for k, (la, lo) in enumerate(zip(tr.lats, tr.lons))
                 if k % 24 == 0]
        net_km = great_circle_km(tr.lats[0], tr.lons[0], tr.lats[-1], tr.lons[-1])
        n_days = max((tr.times[-1] - tr.times[0]).total_seconds() / 86400.0, 1e-9)
        tracks.append({
            "berg": b["name"], "area_km2": b.area_km2,
            "status": tr.status,
            "wind_forcing_R": round(tr.wind_forcing_R, 3)
            if tr.wind_forcing_R is not None else None,
            "daily_positions": daily,
            "net_drift_km": round(net_km, 1),
            "net_drift_km_per_day": round(net_km / n_days, 2),
            "bearing_deg": round(float(np.degrees(np.arctan2(
                (tr.lons[-1] - tr.lons[0]) * np.cos(np.radians(tr.lats[0])),
                tr.lats[-1] - tr.lats[0]))) % 360.0, 0),
        })
        print(f"{b['name']:6s} {tr.status:20s} {net_km:6.1f} km "
              f"bearing {tracks[-1]['bearing_deg']:.0f}")

    OUT.write_text(json.dumps({
        "generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "cycle": str(cycle),
        "model": "WDE17 drift on GLO12 forecast currents, RK2 1 h, zero wind "
                 "(stated limitation, see berg_hindcast.json), grounding-aware "
                 "(assumed 207 m keel vs IBCSO)",
        "validation": "see berg_hindcast.json — persistence beats this model "
                      "on the 2026 sample; arrows are advisory, the circles "
                      "grow at the measured 4.35 km/day error rate",
        "tracks": tracks,
    }, indent=2) + "\n")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
