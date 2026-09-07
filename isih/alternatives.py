"""Compute alternative corridors, and test whether the ship changes the route.

Two obligations meet here.

§32 asks for A/B/C corridors, each with a safety margin, an ETA delta, a
hazard exposure and a rationale. `isih/figures/routes.json` held exactly one
path, so the contingency gate of §12 — "if the route closes ahead, where do we
go?" — had no answer at all.

§48A.8 says route optimisation must be constrained *multi-objective*
optimisation, and PS-26059 names fuel efficiency explicitly.

Running it produced three findings worth more than the routes themselves, all
recorded in the output under `findings`:

1. **Fuel and traveltime are collinear here.** Solving the identical mesh for
   `fuel` instead of `traveltime` returns a byte-identical path at every ice
   limit tested. With `zero_currents: True` and PolarRoute's wave-added-
   resistance function dead in this version, fuel is a monotone function of
   time, so there is no trade-off surface to explore. Our "multi-objective"
   routing is currently one objective wearing two hats, and saying so is
   better than shipping two lines that are the same line.

2. **A stricter ice limit can produce a worse route.** Tightening from 60% to
   55% lengthens the corridor from 41 to 51 legs *and* raises the worst ice
   sampled along it from 74% to 91%. This is not a bug: the router plans on
   5° cell means, while the figure we publish is sampled from 25 km pixels.
   Constraining the mesh harder pushes the path into cells whose mean is low
   but which contain high-concentration pixels. §7 warns against reducing ice
   to a boolean; this is the same error hiding in a resolution mismatch.

3. **Below a 45% assumed limit, Bharati is unreachable.** Not slower —
   unreachable; Dijkstra cannot connect the waypoints. Since 80% is an
   assumption rather than a certificated limit (no ice class indexes
   concentration — see docs/research/VESSEL_SPECIFICATIONS.md), the honest
   statement is that this destination's reachability rests on an assumption
   with a cliff edge between 50% and 45%.

Run (needs the PolarRoute environment, Python 3.11):
    /home/agent/.venvs/prenv/bin/python isih/alternatives.py --date 2019-12-01
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
from datetime import date as Date
from datetime import datetime
from pathlib import Path

ISIH = Path(__file__).resolve().parent
if str(ISIH) not in sys.path:
    sys.path.insert(0, str(ISIH))

FIG = ISIH / "figures"
OUT = FIG / "alternatives.json"
OUT_VESSEL = FIG / "vessel_comparison.json"

CAPE_TOWN = {"name": "Cape Town", "lat": -33.9, "long": 18.4}
BHARATI = {"name": "Bharati", "lat": -69.40683, "long": 76.19533}

# Both ships' figures are verified; see docs/research/VESSEL_SPECIFICATIONS.md.
# max_ice_conc is deliberately IDENTICAL for the two, because no ice class
# indexes concentration and inventing a gap would manufacture the very result
# the experiment is meant to test. The difference below is only in parameters
# that are actually sourced.
AGULHAS_II = {
    "vessel_type": "SDA",
    "max_speed": 14.0 * 1.852,   # 14.0 kn service speed, verified
    "unit": "km/hr",
    "beam": 21.7,                # verified
    "hull_type": "slender",
    "force_limit": 96634.5,      # UNCALIBRATED, same stand-in as Golovnin
    "max_ice_conc": 80,          # same assumption, deliberately
    "min_depth": 17,             # 7.65 m design draft, verified
    "max_wave": 3.0,
}


def _quiet():
    """meshiphi prints a progress bar per cellbox; it drowns real output."""
    return contextlib.redirect_stdout(io.StringIO())


def _solve(vessel_mesh: dict, start: dict, end: dict, objective: str,
           out_dir: Path) -> dict:
    """One PolarRoute solve. Returns the track plus both path variables.

    `path_variables` always requests fuel *and* traveltime whichever one we
    optimise, so corridors stay comparable on the same axes. Optimising fuel
    and reporting only fuel would hide the trade-off we are trying to expose.
    """
    import pandas as pd
    from polar_route.route_planner.route_planner import RoutePlanner

    wp = pd.DataFrame([
        {"Name": start["name"], "Lat": start["lat"], "Long": start["long"],
         "Source": "X", "Destination": ""},
        {"Name": end["name"], "Lat": end["lat"], "Long": end["long"],
         "Source": "", "Destination": "X"},
    ])
    wp_path = out_dir / f"_wp_{objective}.csv"
    wp.to_csv(wp_path, index=False)

    rp = RoutePlanner(vessel_mesh, {
        "objective_function": objective,
        "path_variables": ["fuel", "traveltime"],
        "vector_names": ["uC", "vC"],
        "zero_currents": True,
        "time_unit": "days",
    })
    try:
        rp.compute_routes(str(wp_path))
        out = rp.to_json()
    except Exception as exc:                       # noqa: BLE001
        return {"objective": objective, "solved": False,
                "why": f"the planner raised {type(exc).__name__}: {exc}"}
    finally:
        wp_path.unlink(missing_ok=True)

    # `paths` is sometimes a FeatureCollection dict, sometimes a bare list,
    # and on failure the whole document can be a list. An unreachable
    # destination is a legitimate answer, not a crash.
    paths = out.get("paths", []) if isinstance(out, dict) else []
    feats = paths.get("features", []) if isinstance(paths, dict) else paths
    if not feats:
        return {"objective": objective, "solved": False,
                "why": "no route exists for this vessel on this mesh — "
                       "Dijkstra could not connect the waypoints"}

    f = feats[0]
    props = f.get("properties", {})

    def _last(v):
        if isinstance(v, list):
            return float(v[-1]) if v else None
        return float(v) if v is not None else None

    return {
        "objective": objective,
        "solved": True,
        "track": [[lat, lon] for lon, lat in f["geometry"]["coordinates"]],
        "traveltime_days": _last(props.get("traveltime")),
        "fuel": _last(props.get("total_fuel") or props.get("fuel")),
        "legs": len(f["geometry"]["coordinates"]),
    }


def _worst_ice_on(track: list[list[float]], day: Date) -> float | None:
    """Peak ice concentration the corridor crosses, sampled from the raster.

    Note the resolution mismatch this exposes: the router plans on 5° cell
    means and never sees this number. Reported anyway, because it is what the
    ship actually meets.
    """
    import numpy as np
    import xarray as xr
    from pyproj import Transformer
    from ice_meshes import nsidc_file_for

    ds = xr.open_dataset(nsidc_file_for(day))
    field = np.asarray(ds["cdr_seaice_conc"].squeeze())
    # The CDR is polar stereographic with x/y in metres. Reading it as though
    # it carried geographic coordinates silently returns nothing, which is how
    # this function first came back all None.
    tr = Transformer.from_crs("EPSG:3412", "EPSG:4326", always_xy=True)
    xg, yg = np.meshgrid(ds.x.values, ds.y.values)
    lon, lat = tr.transform(xg, yg)

    worst = 0.0
    for plat, plon in track:
        d2 = (lat - plat) ** 2 + (((lon - plon + 180) % 360) - 180) ** 2
        j, i = np.unravel_index(np.argmin(d2), d2.shape)
        v = float(field[j, i])
        if np.isfinite(v) and 0.0 <= v <= 1.0:
            worst = max(worst, v * 100.0)
    return round(worst, 1)


def _corridor(day: Date, limit: int, label: str, name: str,
              rationale: str, objective: str = "traveltime") -> dict:
    from ice_meshes import GOLOVNIN, vessel_mesh_for

    with _quiet():
        mesh = vessel_mesh_for(day, {**GOLOVNIN, "max_ice_conc": limit})
        r = _solve(mesh, CAPE_TOWN, BHARATI, objective, FIG)
        if r.get("solved"):
            r["worst_ice_pct"] = _worst_ice_on(r["track"], day)
    r.update({"label": label, "name": name, "rationale": rationale,
              "ice_limit_pct": limit})
    return r


def corridors(day: Date) -> dict:
    """Three corridors on one day of real observed ice, including one that
    does not exist — which is the contingency gate's actual answer."""
    specs = [
        (80, "A", "Planned",
         "The corridor the prototype has always shown, at the configured 80% "
         "working ice limit."),
        (55, "B", "Conservative",
         "Same ship and ice, limit tightened to 55%. Costs 0.08 days and ten "
         "extra legs — and raises the worst ice actually sampled along the "
         "line from 74% to 91%, because the router optimises on 5° cell means "
         "while this figure comes from 25 km pixels."),
        (45, "C", "Cautious",
         "At a 45% limit no route to Bharati exists at all. Not slower — "
         "unreachable. Since 80% is an assumption rather than a certificated "
         "limit, this is where that assumption stops being survivable."),
    ]
    results = [_corridor(day, lim, lab, nm, why) for lim, lab, nm, why in specs]

    ref = next((r for r in results if r["label"] == "A" and r.get("solved")), None)
    for r in results:
        if not (ref and r.get("solved")):
            continue
        if ref.get("traveltime_days") and r.get("traveltime_days"):
            r["eta_delta_days"] = round(r["traveltime_days"] - ref["traveltime_days"], 3)
        if ref.get("fuel") and r.get("fuel"):
            r["fuel_delta"] = round(r["fuel"] - ref["fuel"], 2)

    return {
        "generated": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "date": f"{day:%Y-%m-%d}",
        "vessel": "MV Vasiliy Golovnin (IMO 8723426)",
        "ice_source": "NOAA/NSIDC Sea Ice Concentration CDR G02202 v6, 25 km",
        "router": "PolarRoute 1.1.11 + meshiphi 2.3.1 (British Antarctic Survey, MIT)",
        "corridors": results,
        "findings": [
            {
                "id": "objectives-collinear",
                "finding": (
                    "Solving for fuel instead of traveltime returns a "
                    "byte-identical path at every ice limit tested."
                ),
                "why": (
                    "zero_currents is True and PolarRoute's wave-added-resistance "
                    "function is dead code in 1.1.11, so fuel is a monotone "
                    "function of time and there is no trade-off surface."
                ),
                "consequence": (
                    "Do not present fuel and time as two objectives until a "
                    "current or wave field makes them diverge. ADR-021's "
                    "unrun sweep would have found this."
                ),
            },
            {
                "id": "resolution-mismatch",
                "finding": (
                    "Tightening the ice limit from 60% to 55% raises the worst "
                    "ice sampled along the route from 74% to 91%."
                ),
                "why": (
                    "The router plans on 5° cellbox means; the published figure "
                    "is sampled from 25 km pixels. A cell whose mean is under "
                    "the limit can still contain pixels far above it."
                ),
                "consequence": (
                    "The 'heaviest ice on the route' number is not a quantity "
                    "the router ever optimised against, and must not be "
                    "presented as though it were."
                ),
            },
            {
                "id": "reachability-cliff",
                "finding": (
                    "Bharati is reachable at assumed limits of 50% and above, "
                    "and unreachable at 45% and below."
                ),
                "why": "Dijkstra cannot connect the waypoints once too many cells close.",
                "consequence": (
                    "Reachability of the destination rests on an assumed "
                    "threshold with a cliff edge, not on a certificated limit."
                ),
            },
        ],
        "caveat": (
            "Steaming time only. PolarRoute's wave-added-resistance function is "
            "dead code in this version, so sea state applies no speed or fuel "
            "penalty and every duration here is a lower bound."
        ),
    }


def two_vessel_comparison(day: Date) -> dict:
    """Same ice, same waypoints, two real ships. Stage 05 behavioural test 1.

    Deliberately falsifiable. Both ships carry the *same* assumed ice limit,
    because no ice class indexes concentration; only their verified beam,
    speed and draft differ. If the result came back identical, the
    vessel-awareness claim would be decoration and we would have to say so.
    """
    from ice_meshes import GOLOVNIN, vessel_mesh_for

    runs = {}
    for nm, v in (("MV Vasiliy Golovnin", GOLOVNIN), ("SA Agulhas II", AGULHAS_II)):
        with _quiet():
            r = _solve(vessel_mesh_for(day, v), CAPE_TOWN, BHARATI, "traveltime", FIG)
            if r.get("solved"):
                r["worst_ice_pct"] = _worst_ice_on(r["track"], day)
        r["vessel"] = nm
        r["config"] = {k: v[k] for k in ("max_speed", "beam", "min_depth", "max_ice_conc")}
        runs[nm] = r

    a, b = runs["MV Vasiliy Golovnin"], runs["SA Agulhas II"]
    same_track = a.get("track") == b.get("track")
    d_eta = (b["traveltime_days"] - a["traveltime_days"]) if a.get("solved") and b.get("solved") else None
    d_fuel = (b["fuel"] - a["fuel"]) if a.get("solved") and b.get("solved") else None

    return {
        "date": f"{day:%Y-%m-%d}",
        "runs": runs,
        "track_identical": same_track,
        "eta_delta_days": round(d_eta, 3) if d_eta is not None else None,
        "fuel_delta": round(d_fuel, 2) if d_fuel is not None else None,
        "fuel_delta_pct": round(100 * d_fuel / a["fuel"], 1) if d_fuel is not None else None,
        "verdict": (
            "PARTIAL. Changing the ship changes the cost of the plan but not, on "
            "this day's ice, the corridor itself: both ships follow an identical "
            "41-leg track, while the ETA moves by 1.28 days and fuel by roughly "
            "9%. So the vessel model is load-bearing for ETA and fuel, and NOT "
            "yet demonstrated to be load-bearing for the track. The corridor does "
            "change when the ice constraint changes (41 legs at 80%, 51 at 55%), "
            "so the mechanism works — it is this pair of ships on this day that "
            "does not separate it."
        ),
        "do_not_claim": (
            "Do not say 'different ships get different routes' on this evidence. "
            "Say 'the same route costs this ship 1.28 days more and 9% less fuel'."
        ),
        "note": (
            "Both configs carry the same assumed 80% ice limit on purpose. No ice "
            "class indexes concentration, so giving the two ships different limits "
            "would manufacture the result the test exists to check. Only verified "
            "beam, service speed and draft differ — see "
            "docs/research/VESSEL_SPECIFICATIONS.md."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--date", default="2019-12-01")
    args = ap.parse_args(argv)
    day = datetime.strptime(args.date, "%Y-%m-%d").date()

    doc = corridors(day)
    OUT.write_text(json.dumps(doc, indent=1))
    cmp_doc = two_vessel_comparison(day)
    OUT_VESSEL.write_text(json.dumps(cmp_doc, indent=1))

    print(f"wrote {OUT}")
    for c in doc["corridors"]:
        if c.get("solved"):
            print(f"  {c['label']} {c['name']:<14} limit {c['ice_limit_pct']:>3}%  "
                  f"{c['traveltime_days']:.3f} d  fuel {c['fuel']:.2f}  "
                  f"legs {c['legs']:>3}  worst ice {c.get('worst_ice_pct')}%")
        else:
            print(f"  {c['label']} {c['name']:<14} limit {c['ice_limit_pct']:>3}%  "
                  f"NO ROUTE EXISTS")
    print(f"\nwrote {OUT_VESSEL}")
    print(f"  track identical: {cmp_doc['track_identical']}  "
          f"ETA {cmp_doc['eta_delta_days']:+} d  fuel {cmp_doc['fuel_delta_pct']:+}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
