"""What does it cost to sail on an ice chart that is already out of date?

`route_map.png` compared our computed route against a great-circle line. That
is a strawman and we should retire it: no master sails a straight line into pack
ice. What a master actually does today is plan on the most recent ice chart
available -- PolarView, AMSR2, a NOAA chart -- and sail that plan, updating it
when a new chart arrives.

So the honest baseline is not a straight line. It is *the same router, given
older ice*. This module measures the difference.

    STATIC   plan once on departure-day ice, then sail it blind
    DAILY    re-plan every day on that day's observed ice

Both plans are then REPLAYED through the ice that actually happened, day by day,
from the NSIDC archive. The reported transit time is therefore what the ship
would really have experienced, not what its planner hoped for.

Why this matters more than a lower RMSE: it converts "our sea-ice forecast is
18-31% better" into days and blocked hours, which is the unit a captain and a
judge both think in. It can also come out against us, which is the point.

    STATIC vs DAILY  = the value of fresh information (no forecast involved)
    DAILY vs ORACLE  = the headroom a forecast could still capture  <- our model

Run (needs the PolarRoute env, Python 3.11):
    prenv/bin/python isih/route_regret.py --depart 2019-12-01
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass, field
from datetime import date as Date
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from ice_meshes import GOLOVNIN, CellLookup, vessel_mesh_for

CAPE_TOWN = {"name": "CapeTown", "lat": -33.9, "long": 18.4}
BHARATI = {"name": "Bharati", "lat": -69.4, "long": 76.2}

EARTH_RADIUS_KM = 6371.0

# How finely we sample the planned track when replaying it. The mesh cells are
# 1.25-5 degrees, so 25 km steps resolve a cell crossing several times over
# without making the walk expensive.
STEP_KM = 25.0

# A beset ship waits for the ice to open. If it has not opened after this many
# days the voyage is reported as compromised rather than silently accumulating
# an implausible delay.
MAX_WAIT_DAYS = 5


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = (math.sin(dp / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2)
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def interpolate(lat1: float, lon1: float, lat2: float, lon2: float,
                fraction: float) -> tuple[float, float]:
    """Point a given fraction along the great circle from 1 to 2.

    Linear interpolation in lat/long would cut corners at these latitudes, and
    the corner it cuts is exactly the kind of place ice sits.
    """
    d = haversine_km(lat1, lon1, lat2, lon2) / EARTH_RADIUS_KM
    if d == 0:
        return lat1, lon1
    a = math.sin((1 - fraction) * d) / math.sin(d)
    b = math.sin(fraction * d) / math.sin(d)
    p1, l1, p2, l2 = map(math.radians, (lat1, lon1, lat2, lon2))
    x = a * math.cos(p1) * math.cos(l1) + b * math.cos(p2) * math.cos(l2)
    y = a * math.cos(p1) * math.sin(l1) + b * math.cos(p2) * math.sin(l2)
    z = a * math.sin(p1) + b * math.sin(p2)
    return (math.degrees(math.atan2(z, math.hypot(x, y))),
            math.degrees(math.atan2(y, x)))


def densify(track: list[tuple[float, float]],
            step_km: float = STEP_KM) -> list[tuple[float, float]]:
    """Resample a waypoint polyline to roughly even steps along the track."""
    if len(track) < 2:
        return list(track)
    out: list[tuple[float, float]] = [track[0]]
    for (lat1, lon1), (lat2, lon2) in zip(track, track[1:]):
        leg_km = haversine_km(lat1, lon1, lat2, lon2)
        n = max(1, int(math.ceil(leg_km / step_km)))
        for i in range(1, n + 1):
            out.append(interpolate(lat1, lon1, lat2, lon2, i / n))
    return out


@dataclass
class VoyageOutcome:
    """What actually happened when a plan met the real ice."""

    planner: str
    depart: Date
    planned_days: float | None
    actual_days: float
    blocked_hours: float
    max_sic: float
    mean_sic: float
    distance_km: float
    completed: bool
    note: str = ""
    daily_positions: list[dict] = field(default_factory=list)

    @property
    def regret_days(self) -> float | None:
        if self.planned_days is None:
            return None
        return self.actual_days - self.planned_days

    def as_dict(self) -> dict:
        d = {
            "planner": self.planner,
            "depart": f"{self.depart:%Y-%m-%d}",
            "planned_days": self.planned_days,
            "actual_days": round(self.actual_days, 2),
            "regret_days": (None if self.regret_days is None
                            else round(self.regret_days, 2)),
            "blocked_hours": round(self.blocked_hours, 1),
            "max_sic_encountered": round(self.max_sic, 1),
            "mean_sic_encountered": round(self.mean_sic, 1),
            "distance_km": round(self.distance_km, 1),
            "completed": self.completed,
            "note": self.note,
        }
        return d


def plan_route(vessel_mesh: dict, start: dict, end: dict,
               out_dir: Path) -> tuple[list[tuple[float, float]], float | None]:
    """Run PolarRoute on a prepared vessel mesh. Returns (track, planned days).

    The mesh is already vessel-modelled, so this is the Dijkstra + smoothing
    stage only.
    """
    from polar_route.route_planner.route_planner import RoutePlanner

    waypoints = pd.DataFrame([
        {"Name": start["name"], "Lat": start["lat"], "Long": start["long"],
         "Source": "X", "Destination": ""},
        {"Name": end["name"], "Lat": end["lat"], "Long": end["long"],
         "Source": "", "Destination": "X"},
    ])
    wp_path = out_dir / "_wp.csv"
    waypoints.to_csv(wp_path, index=False)

    planner_config = {
        "objective_function": "traveltime",
        "path_variables": ["fuel", "traveltime"],
        "vector_names": ["uC", "vC"],
        "zero_currents": True,
        "time_unit": "days",
    }
    rp = RoutePlanner(vessel_mesh, planner_config)
    rp.compute_routes(str(wp_path))
    result = rp.to_json()

    features = result.get("paths", {}).get("features", [])
    if not features:
        return [], None

    feat = features[0]
    coords = feat["geometry"]["coordinates"]      # [lon, lat] pairs
    track = [(lat, lon) for lon, lat in coords]

    props = feat.get("properties", {})
    planned = props.get("traveltime")
    if isinstance(planned, list) and planned:
        planned = planned[-1]
    return track, (float(planned) if planned is not None else None)


def replay(track: list[tuple[float, float]], depart: Date,
           vessel: dict | None = None,
           label: str = "STATIC", apply_qa: bool = True) -> VoyageOutcome:
    """Sail a fixed plan through the ice that actually happened.

    The ship advances along the planned track at whatever speed that day's real
    ice permits. Where the plan runs into ice the ship may not enter, it waits
    -- which is what a beset ship does -- and re-checks the next day.
    """
    vessel = vessel or GOLOVNIN
    points = densify(track)

    hours = 0.0
    blocked_hours = 0.0
    distance_km = 0.0
    sic_samples: list[float] = []
    positions: list[dict] = []

    lookups: dict[Date, CellLookup] = {}

    def lookup_for(day: Date) -> CellLookup:
        if day not in lookups:
            lookups[day] = CellLookup(
                vessel_mesh_for(day, vessel, apply_qa=apply_qa))
        return lookups[day]

    day_logged = -1
    for (lat1, lon1), (lat2, lon2) in zip(points, points[1:]):
        leg_km = haversine_km(lat1, lon1, lat2, lon2)
        if leg_km == 0:
            continue

        waited = 0.0
        while True:
            today = depart + timedelta(days=int(hours // 24))
            try:
                look = lookup_for(today)
            except FileNotFoundError:
                return VoyageOutcome(
                    label, depart, None, hours / 24, blocked_hours,
                    max(sic_samples, default=0.0),
                    (sum(sic_samples) / len(sic_samples)) if sic_samples else 0.0,
                    distance_km, False,
                    "ran past the end of the local NSIDC archive",
                    positions)

            speed = look.speed_at(lat2, lon2)
            if speed is not None and speed > 0:
                break
            # Blocked: wait a day for the ice to open.
            hours += 24.0
            blocked_hours += 24.0
            waited += 1
            if waited > MAX_WAIT_DAYS:
                return VoyageOutcome(
                    label, depart, None, hours / 24, blocked_hours,
                    max(sic_samples, default=0.0),
                    (sum(sic_samples) / len(sic_samples)) if sic_samples else 0.0,
                    distance_km, False,
                    f"beset: ice did not open within {MAX_WAIT_DAYS} days at "
                    f"{lat2:.1f}, {lon2:.1f}",
                    positions)

        sic = look.sic_at(lat2, lon2)
        if sic is not None:
            sic_samples.append(sic)

        hours += leg_km / speed
        distance_km += leg_km

        elapsed_day = int(hours // 24)
        if elapsed_day != day_logged:
            day_logged = elapsed_day
            positions.append({
                "day": elapsed_day,
                "date": f"{depart + timedelta(days=elapsed_day):%Y-%m-%d}",
                "lat": round(lat2, 3), "lon": round(lon2, 3),
                "sic": None if sic is None else round(sic, 1),
                "speed_kmh": round(speed, 2),
            })

    return VoyageOutcome(
        label, depart, None, hours / 24, blocked_hours,
        max(sic_samples, default=0.0),
        (sum(sic_samples) / len(sic_samples)) if sic_samples else 0.0,
        distance_km, True, "", positions)


def sail_daily_replan(depart: Date, vessel: dict | None = None,
                      out_dir: Path = Path("."), max_days: int = 45,
                      label: str = "DAILY",
                      apply_qa: bool = True) -> VoyageOutcome:
    """Re-plan every day on that day's observed ice, then sail one day of it.

    This is the strongest baseline that uses no forecast at all: a perfectly
    informed operator who receives a fresh ice chart every morning and re-routes
    on it. Beating STATIC only proves fresh data helps. The gap that remains
    between this and a perfect-foresight route is the space a forecast can
    actually win -- which is where our model has to earn its place.
    """
    vessel = vessel or GOLOVNIN
    pos = (CAPE_TOWN["lat"], CAPE_TOWN["long"])
    dest = (BHARATI["lat"], BHARATI["long"])
    arrive_km = 30.0

    hours = blocked_hours = distance_km = 0.0
    sic_samples: list[float] = []
    positions: list[dict] = []
    replans = 0

    def outcome(completed: bool, note: str) -> VoyageOutcome:
        return VoyageOutcome(
            label, depart, None, hours / 24, blocked_hours,
            max(sic_samples, default=0.0),
            (sum(sic_samples) / len(sic_samples)) if sic_samples else 0.0,
            distance_km, completed, note, positions)

    while hours / 24 < max_days:
        today = depart + timedelta(days=int(hours // 24))
        try:
            vessel_mesh = vessel_mesh_for(today, vessel, apply_qa=apply_qa)
        except FileNotFoundError:
            return outcome(False, "ran past the end of the local NSIDC archive")

        look = CellLookup(vessel_mesh)
        track, _ = plan_route(vessel_mesh,
                              {"name": "Now", "lat": pos[0], "long": pos[1]},
                              BHARATI, out_dir)
        replans += 1
        if not track:
            hours += 24.0
            blocked_hours += 24.0
            continue

        points = densify(track)
        budget = 24.0
        for (lat1, lon1), (lat2, lon2) in zip(points, points[1:]):
            leg_km = haversine_km(lat1, lon1, lat2, lon2)
            if leg_km == 0:
                continue
            speed = look.speed_at(lat2, lon2)
            if speed is None or speed <= 0:
                break                      # today's plan hits ice: stop, re-plan
            travel_h = leg_km / speed
            if travel_h > budget:
                pos = interpolate(lat1, lon1, lat2, lon2, budget / travel_h)
                distance_km += leg_km * (budget / travel_h)
                hours += budget
                budget = 0.0
                break
            pos = (lat2, lon2)
            distance_km += leg_km
            hours += travel_h
            budget -= travel_h
            sic = look.sic_at(lat2, lon2)
            if sic is not None:
                sic_samples.append(sic)

        if budget > 0:                     # day ended early: ship held position
            hours += budget
            blocked_hours += budget

        positions.append({
            "day": int(hours // 24), "date": f"{today:%Y-%m-%d}",
            "lat": round(pos[0], 3), "lon": round(pos[1], 3),
            "replans": replans,
        })

        if haversine_km(pos[0], pos[1], dest[0], dest[1]) <= arrive_km:
            return outcome(True, f"arrived after {replans} daily re-plans")

    return outcome(False, f"did not arrive within {max_days} days "
                          f"({replans} re-plans)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--depart", default="2019-12-01",
                    help="departure date, YYYY-MM-DD")
    ap.add_argument("--out-dir", type=Path, default=Path("isih/figures"))
    args = ap.parse_args()

    depart = datetime.strptime(args.depart, "%Y-%m-%d").date()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Departure: {depart:%Y-%m-%d}  vessel: MV Vasiliy Golovnin "
          f"(beam {GOLOVNIN['beam']} m, {GOLOVNIN['max_speed']} km/hr, "
          f"ice limit {GOLOVNIN['max_ice_conc']}%)\n", flush=True)

    results: list[VoyageOutcome] = []

    # --- arm 1: plan once on departure ice, sail blind ----------------------
    print("[STATIC] planning once on departure-day ice ...", flush=True)
    mesh0 = vessel_mesh_for(depart)
    track0, planned0 = plan_route(mesh0, CAPE_TOWN, BHARATI, args.out_dir)
    if not track0:
        print("  no route found on departure day", flush=True)
        return 1
    print(f"  planner promised {planned0:.2f} days over {len(track0)} waypoints",
          flush=True)
    print("[STATIC] replaying it through the ice that really happened ...",
          flush=True)
    static = replay(track0, depart, label="STATIC")
    static.planned_days = planned0
    results.append(static)

    # --- arm 2: the same thing, but reading the QA-suspect cells as truth ---
    # This isolates what the land-spillover artifact alone costs, rather than
    # asserting that reading QA flags matters.
    print("[STATIC-noQA] same plan, but trusting spillover-filtered cells ...",
          flush=True)
    mesh0_raw = vessel_mesh_for(depart, apply_qa=False)
    track_raw, planned_raw = plan_route(mesh0_raw, CAPE_TOWN, BHARATI,
                                        args.out_dir)
    if track_raw:
        static_raw = replay(track_raw, depart, label="STATIC-noQA",
                            apply_qa=False)
        static_raw.planned_days = planned_raw
        results.append(static_raw)

    # --- arm 3: a fresh chart every morning, no forecast -------------------
    print("[DAILY] re-planning every day on that day's observed ice ...",
          flush=True)
    daily = sail_daily_replan(depart, out_dir=args.out_dir, label="DAILY")
    results.append(daily)

    out = {
        "experiment": "route regret: what it costs to sail on stale ice",
        "vessel": "MV Vasiliy Golovnin",
        "vessel_config": GOLOVNIN,
        "depart": f"{depart:%Y-%m-%d}",
        "route": "Cape Town -> Bharati",
        "ice_source": "NSIDC CDR daily, observed",
        "step_km": STEP_KM,
        "max_wait_days": MAX_WAIT_DAYS,
        "arms": {
            "STATIC": "plan once on departure ice, sail blind (today's practice)",
            "STATIC-noQA": "same, but trusting QA-suspect cells as open water",
            "DAILY": "fresh observed chart every morning, no forecast",
        },
        "results": [r.as_dict() for r in results],
    }
    (args.out_dir / "route_regret.json").write_text(json.dumps(out, indent=2))

    print("\n--- outcome ---")
    for r in results:
        print(json.dumps(r.as_dict(), indent=2))
    print(f"\nWrote {args.out_dir / 'route_regret.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
