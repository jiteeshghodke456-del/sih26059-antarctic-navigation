#!/usr/bin/env python3
"""Slice 6 check: route on REAL forecast data and evaluate the weather gate.

    python scripts/real_route_run.py [cycle YYYY-MM-DD]

Runs the unmodified sim Router (Dijkstra, arrival-time costs, land + IBCSO
depth blocking) with RealWorld — real GLO12 ice, real CMEMS waves, real ECMWF
wind — for one archived cycle, on the corridor segment the data covers
(south of 55S; there is no wave/wind harvest north of the box). Writes
dakshin/figures/real_route.json with worst_hs/worst wind taken from real files
and the weather gate's state.
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

from gates import weather_gate  # noqa: E402
from real_world import RealWorld  # noqa: E402
from sim.router import Router, VesselModel  # noqa: E402

OUT = ROOT / "dakshin" / "figures" / "real_route.json"
START = (-55.5, 45.0)      # corridor entry, on the Cape Town-Bharati line
BHARATI = (-69.4, 76.2)


def main() -> int:
    cycle = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 \
        else dt.date(2026, 11, 21)
    world = RealWorld(cycle)
    router = Router(world, VesselModel(),
                    lat_min=-70.6, lat_max=-55.0, lon_min=13.0, lon_max=79.5)
    result = router.solve(START, BHARATI, depart_t=0.0, objective="time")
    approach_closed = result is None
    closest_km = None
    if approach_closed:
        # The goal is sealed off by over-limit ice (real late-spring fast
        # ice). Route instead to the closest cell the ship can actually
        # reach, and say so — that is the bridge-useful answer.
        LO, LA = np.meshgrid(router.lons, router.lats)
        s0 = world.sample(LA, LO, 0.0)
        passable = (~router.land) & (s0["sic"] <= router.vessel.ice_limit) \
            & ~(np.isfinite(router.depth) & (router.depth < router.vessel.min_depth_m))
        d2goal = np.hypot((LA - BHARATI[0]) * 111.0,
                          (LO - BHARATI[1]) * 111.0 * np.cos(np.radians(BHARATI[0])))
        d2goal[~passable] = np.inf
        j, i = np.unravel_index(np.argmin(d2goal), d2goal.shape)
        closest_km = float(d2goal[j, i])
        result = router.solve(START, (float(router.lats[j]), float(router.lons[i])),
                              depart_t=0.0, objective="time")
    if result is None:
        payload = {"cycle": str(cycle), "route": None,
                   "reason": "no route under the ice limit on this cycle"}
        OUT.write_text(json.dumps(payload, indent=2) + "\n")
        print("no route found"); return 1

    # wind along the track at arrival times, from the real IFS file
    worst_wind = None
    winds = []
    for leg in result["legs"]:
        s = world.sample(leg["lat"], leg["lon"], leg["hours"] / 24.0)
        w = s.get("wind_ms")
        if w is not None and np.isfinite(w):
            winds.append(float(w))
    if winds:
        worst_wind = max(winds)

    gate = weather_gate(worst_hs_m=result["worst_hs"], worst_wind_ms=worst_wind)
    payload = {
        "generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "cycle": str(cycle),
        "start": START, "goal": BHARATI,
        "segment_note": "corridor segment south of 55S — the harvest box; "
                        "no real wave/wind data exists north of it",
        "approach_closed_at_ice_limit": approach_closed,
        "closest_approach_km": round(closest_km, 1) if closest_km is not None else None,
        "eta_days": result["days"],
        "worst_ice": result["worst_sic"],
        "worst_hs_m": result["worst_hs"],
        "worst_wind_ms": round(worst_wind, 1) if worst_wind is not None else None,
        "weather_gate": {"state": gate.state.name, "reason": gate.reason,
                         "unassessed": gate.unassessed},
        "n_legs": len(result["legs"]),
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
