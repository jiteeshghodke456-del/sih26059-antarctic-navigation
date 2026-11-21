#!/usr/bin/env python3
"""Validate the iceberg forecast against real later USNIC positions
(HANDOFF_TONIGHT slice 5 step 3).

For every berg in the archived weekly USNIC lists whose position fix falls in
the corridor currents box, integrate from each fix to the next on CMEMS
*analysis* currents (data/cmems_cur_analysis/) and compare the landing point
with where USNIC actually put the berg — against persistence (berg did not
move). USNIC positions are themselves only accurate to a few km, which bounds
how small these errors can meaningfully be.

Writes isih/figures/berg_hindcast.json. Scored once, reported as it comes out.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "isih"))
sys.path.insert(0, str(ROOT / "models" / "iceberg"))

from berg_forecast import (STATUS_OK, CurrentField, forecast_track,  # noqa: E402
                           great_circle_km)
from catalogue import load_usnic  # noqa: E402

CUR_DIR = ROOT / "data" / "cmems_cur_analysis"
ARCHIVE = ROOT / "data" / "icebergs" / "archive"
OUT = ROOT / "isih" / "figures" / "berg_hindcast.json"
BOX = {"lon": (0.0, 80.0), "lat": (-78.0, -55.0)}


def fix_series() -> dict[str, list[tuple[dt.date, float, float, float, float]]]:
    """Per berg: deduped (observed, lat, lon, length_m, width_m), ascending."""
    fixes = defaultdict(dict)
    for path in sorted(ARCHIVE.glob("AntarcticIcebergs_*.csv")):
        for _, r in load_usnic(path).iterrows():
            if r.observed is not None and not np.isnan(r.lat):
                fixes[r["name"]][r.observed.date()] = (
                    float(r.lat), float(r.lon), float(r.length_m), float(r.width_m))
    return {
        name: [(d, *v) for d, v in sorted(days.items())]
        for name, days in fixes.items()
    }


def load_field() -> CurrentField:
    cur_files = sorted(CUR_DIR.glob("*.nc"))
    if not cur_files:
        raise FileNotFoundError(
            f"no analysis currents in {CUR_DIR} — run the slice 4 backfill first")
    field_ = CurrentField.from_files(cur_files)
    print(f"currents: {len(cur_files)} days")
    return field_


def run_segments(field_: CurrentField) -> list[dict]:
    t_min = dt.date.fromtimestamp(field_.t[0] * 86400.0)
    t_max = dt.date.fromtimestamp(field_.t[-1] * 86400.0)
    segments = []
    for name, series in sorted(fix_series().items()):
        for (d0, lat0, lon0, L, W), (d1, lat1, lon1, _, _) in zip(series, series[1:]):
            days = (d1 - d0).days
            if days <= 0:
                continue
            if not (BOX["lon"][0] <= lon0 <= BOX["lon"][1]
                    and BOX["lat"][0] <= lat0 <= BOX["lat"][1]):
                continue
            if d0 < t_min or d1 > t_max:
                continue
            start = dt.datetime(d0.year, d0.month, d0.day, 12)
            tr = forecast_track(name, lat0, lon0, L, W, field_, start, days)
            err = great_circle_km(tr.lats[-1], tr.lons[-1], lat1, lon1)
            pers = great_circle_km(lat0, lon0, lat1, lon1)
            segments.append({
                "berg": name, "from": str(d0), "to": str(d1), "days": days,
                "status": tr.status, "wind_forcing_R": round(tr.wind_forcing_R, 4)
                if tr.wind_forcing_R is not None else None,
                "error_km": round(err, 1),
                "error_km_per_day": round(err / days, 2),
                "persistence_km": round(pers, 1),
                "persistence_km_per_day": round(pers / days, 2),
            })
            print(f"{name:6s} {d0}→{d1} ({days:2d} d) model {err:6.1f} km "
                  f"persist {pers:6.1f} km  {tr.status}")
    return segments


def main() -> int:
    field_ = load_field()
    t_min = dt.date.fromtimestamp(field_.t[0] * 86400.0)
    t_max = dt.date.fromtimestamp(field_.t[-1] * 86400.0)
    segments = run_segments(field_)
    if not segments:
        print("no scorable segments — check archive coverage vs currents dates")
        return 1

    ok = [s for s in segments if s["status"] == STATUS_OK]
    model_kmd = [s["error_km_per_day"] for s in ok]
    pers_kmd = [s["persistence_km_per_day"] for s in ok]
    # USNIC gives positions to ~0.01 deg; >3 km between fixes is real motion,
    # less is indistinguishable from a stationary (grounded) berg.
    moving = [s for s in ok if s["persistence_km"] > 3.0]
    still = [s for s in ok if s["persistence_km"] <= 3.0]
    payload = {
        "generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "currents": f"CMEMS GLO12 analysis surface currents, {t_min}..{t_max}",
        "wind": "zero (slice 6 pending); wind_forcing_R per segment shows the "
                "neglected term's share, computed with an assumed 10 m/s wind",
        "caveats": [
            "USNIC positions are accurate to only a few km",
            "weekly fixes: errors mix drift-model error with fix-timing error",
            "grounded-or-unknown segments are excluded from the km/day summary "
            "but listed in full",
        ],
        "n_segments": len(segments),
        "n_ok": len(ok),
        "median_error_km_per_day": {
            "model": round(float(np.median(model_kmd)), 2) if ok else None,
            "persistence": round(float(np.median(pers_kmd)), 2) if ok else None,
        },
        "mean_error_km_per_day": {
            "model": round(float(np.mean(model_kmd)), 2) if ok else None,
            "persistence": round(float(np.mean(pers_kmd)), 2) if ok else None,
        },
        "split": {
            "stationary_segments": len(still),
            "moving_segments": len(moving),
            "finding": "most corridor giants are grounded (persistence 0 km); "
                       "a current-advection model without grounding detection "
                       "drifts anchored bergs, and persistence also wins on "
                       "the moving sample at weekly fix cadence",
            "moving_median_km_per_day": {
                "model": round(float(np.median([s["error_km_per_day"] for s in moving])), 2) if moving else None,
                "persistence": round(float(np.median([s["persistence_km_per_day"] for s in moving])), 2) if moving else None,
            },
            "stationary_model_median_km_per_day": round(float(np.median(
                [s["error_km_per_day"] for s in still])), 2) if still else None,
        },
        # The site's forecast cone grows at the MEASURED rate, not the
        # unverified 12 km/day figure from the older docs.
        "uncertainty_radius_km_per_day": round(float(np.median(model_kmd)), 2) if ok else None,
        "segments": segments,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"\nwrote {OUT}: {len(ok)}/{len(segments)} ok segments, "
          f"median model {payload['median_error_km_per_day']['model']} km/day "
          f"vs persistence {payload['median_error_km_per_day']['persistence']} km/day")
    return 0


if __name__ == "__main__":
    sys.exit(main())
