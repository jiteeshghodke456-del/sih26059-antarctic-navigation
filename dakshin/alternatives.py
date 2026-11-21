"""Compute alternative corridors, and test whether the ship changes the route.

Two obligations meet here.

§32 asks for A/B/C corridors, each with a safety margin, an ETA delta, a
hazard exposure and a rationale. `dakshin/figures/routes.json` held exactly one
path, so the contingency gate of §12 — "if the route closes ahead, where do we
go?" — had no answer at all.

§48A.8 says route optimisation must be constrained *multi-objective*
optimisation, and the problem statement names fuel efficiency explicitly.

Running it produces three findings worth more than the routes themselves,
recorded in the output under `findings`. Every number in them is measured in
the run that writes the file - they were literal strings once, and went stale
the moment depth entered the mesh.

1. **Fuel and traveltime barely diverge.** With `zero_currents: True` and
   PolarRoute's wave-added-resistance function dead in this version, fuel
   differs from time only through the ice term of the fuel rate. On the
   pre-depth meshes the two objectives returned a byte-identical path; on
   the depth-aware meshes (2019-12-01 ice) they differ by at most ~1.6% fuel.
   Either way there is no real trade-off surface, and "multi-objective"
   routing would be one objective wearing two hats.

2. **A stricter ice limit can produce a worse route.** Tightening from 60% to
   55% raises the worst ice sampled along the route (74% to 91% on
   2019-12-01). The router plans on cell means, while the figure we publish
   is sampled from 25 km pixels, so constraining the mesh harder can push
   the path into cells whose mean is low but which contain high-
   concentration pixels. §7 warns against reducing ice to a boolean; this is
   the same error hiding in a resolution mismatch.

3. **There is a reachability cliff.** At some assumed limit Bharati becomes
   unreachable - not slower; Dijkstra cannot connect the waypoints (between
   50% and 45% on 2019-12-01). Since 80% is an assumption rather than a
   certificated limit (no ice class indexes concentration - see
   docs/research/VESSEL_SPECIFICATIONS.md), the destination's reachability
   rests on an assumption with a cliff edge.

Run (needs the PolarRoute environment, Python 3.11):
    /home/agent/.venvs/prenv/bin/python dakshin/alternatives.py --date 2019-12-01
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

DAKSHIN = Path(__file__).resolve().parent
if str(DAKSHIN) not in sys.path:
    sys.path.insert(0, str(DAKSHIN))

FIG = DAKSHIN / "figures"
# make_route_figure.build_mesh: 5 deg cells split at most 4 times.
SMALLEST_CELL_DEG = 5.0 / 2 ** 4
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


def _time_and_fuel(day: Date, limit: int) -> tuple[dict, dict]:
    """The same mesh solved for traveltime and for fuel."""
    from ice_meshes import GOLOVNIN, vessel_mesh_for

    with _quiet():
        mesh = vessel_mesh_for(day, {**GOLOVNIN, "max_ice_conc": limit})
        return (_solve(mesh, CAPE_TOWN, BHARATI, "traveltime", FIG),
                _solve(mesh, CAPE_TOWN, BHARATI, "fuel", FIG))


def corridors(day: Date) -> dict:
    """Three corridors on one day of real observed ice, including one that
    does not exist — which is the contingency gate's actual answer."""
    specs = [
        (80, "A", "Planned",
         "The corridor the prototype has always shown, at the configured 80% "
         "working ice limit."),
        (55, "B", "Conservative",
         "Same ship and ice, limit tightened to 55%."),   # costs measured below
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

    by = {r["label"]: r for r in results}
    a_, b_ = by["A"], by["B"]
    if a_.get("solved") and b_.get("solved"):
        b_["rationale"] = (
            f"Same ship and ice, limit tightened to 55%. Costs "
            f"{b_['eta_delta_days']:.2f} days and {b_['legs'] - a_['legs']} extra "
            f"legs - and the worst ice actually sampled along the line goes from "
            f"{a_['worst_ice_pct']:.0f}% to {b_['worst_ice_pct']:.0f}%, because the "
            f"router optimises on cell means while this figure comes from 25 km pixels.")

    # Finding 1: does solving for fuel change the answer?
    pairs = {lim: _time_and_fuel(day, lim) for lim in (80, 55)}
    diffs = [(lim, t, f) for lim, (t, f) in pairs.items()
             if t.get("solved") and f.get("solved")]
    identical = all(t["track"] == f["track"] for _, t, f in diffs)
    if identical:
        collinear = ("objectives-collinear",
                     "Solving for fuel instead of traveltime returns a "
                     "byte-identical path at every ice limit tested "
                     f"({', '.join(f'{l}%' for l, _, _ in diffs)}).")
    else:
        save = max(100.0 * (t["fuel"] - f["fuel"]) / t["fuel"] for _, t, f in diffs)
        cost = max(f["traveltime_days"] - t["traveltime_days"] for _, t, f in diffs)
        collinear = ("objectives-nearly-collinear",
                     f"Solving for fuel instead of traveltime saves at most "
                     f"{save:.1f}% fuel for at most {cost:.3f} extra days at the "
                     f"limits tested ({', '.join(f'{l}%' for l, _, _ in diffs)}): "
                     f"the paths differ, but the objectives barely diverge.")

    # Finding 2: does a stricter limit raise the worst ice on the route?
    t60, _ = _time_and_fuel(day, 60)
    w60 = _worst_ice_on(t60["track"], day) if t60.get("solved") else None
    w55 = b_.get("worst_ice_pct")
    if w60 is not None and w55 is not None:
        verb = "raises" if w55 > w60 else "does not raise"
        mismatch = (f"Tightening the ice limit from 60% to 55% {verb} the worst "
                    f"ice sampled along the route ({w60:.0f}% to {w55:.0f}%).")
    else:
        mismatch = "The 60% or 55% corridor did not solve, so this was not measured."

    # Finding 3: where does Bharati stop being reachable?
    t50, _ = _time_and_fuel(day, 50)
    c_solved = by["C"].get("solved")
    if t50.get("solved") and not c_solved:
        cliff = ("Bharati is reachable at every assumed limit tested from 80% "
                 "down to 50%, and unreachable at 45%.")
    else:
        cliff = (f"Reachability at 50%: {bool(t50.get('solved'))}; at 45%: "
                 f"{bool(c_solved)}. The cliff is not between 50% and 45% on this day.")

    return {
        "generated": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "date": f"{day:%Y-%m-%d}",
        "vessel": "MV Vasiliy Golovnin (IMO 8723426)",
        "ice_source": "NOAA/NSIDC Sea Ice Concentration CDR G02202 v6, 25 km",
        "router": "PolarRoute 1.1.11 + meshiphi 2.3.1 (British Antarctic Survey, MIT)",
        "corridors": results,
        "findings": [
            {
                "id": collinear[0],
                "finding": collinear[1],
                "why": (
                    "zero_currents is True and PolarRoute's wave-added-resistance "
                    "function is dead code in 1.1.11, so fuel differs from time "
                    "only through the ice term of the fuel rate - not enough to "
                    "give a real trade-off surface."
                ),
                "consequence": (
                    "Do not present fuel and time as two objectives until a "
                    "current or wave field makes them diverge materially."
                ),
            },
            {
                "id": "resolution-mismatch",
                "finding": mismatch,
                "why": (
                    "The router plans on cellbox means; the published figure "
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
                "finding": cliff,
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
    import numpy as np
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

    # Byte-identity is too strict a test of "same corridor": PolarRoute's
    # path smoothing moves a crossing point slightly when the ship's speed
    # changes. Same number of points, each closer than half the smallest
    # mesh cell, means the same sequence of cells.
    offset_km = None
    if a.get("solved") and b.get("solved") and len(a["track"]) == len(b["track"]):
        ta, tb = np.radians(np.array(a["track"])), np.radians(np.array(b["track"]))
        h = (np.sin((tb[:, 0] - ta[:, 0]) / 2) ** 2 + np.cos(ta[:, 0]) * np.cos(tb[:, 0])
             * np.sin((tb[:, 1] - ta[:, 1]) / 2) ** 2)
        offset_km = float(2 * 6371.0 * np.arcsin(np.sqrt(h)).max())
    same_corridor = offset_km is not None and offset_km < 0.5 * SMALLEST_CELL_DEG * 111.2

    if same_corridor and d_eta is not None:
        how = ("an identical" if same_track else
               f"the same {len(a['track'])}-point track (largest point offset "
               f"{offset_km:.1f} km, a smoothing artefact; mesh cells are at least "
               f"{SMALLEST_CELL_DEG * 111.2:.0f} km across)")
        verdict = (
            f"PARTIAL. Changing the ship changes the cost of the plan but not, on "
            f"this day's ice, the corridor itself: both ships follow {how}, while "
            f"the ETA moves by {abs(d_eta):.2f} days and fuel by "
            f"{abs(100 * d_fuel / a['fuel']):.0f}%. So the vessel model is "
            f"load-bearing for ETA and fuel, and NOT yet demonstrated to be "
            f"load-bearing for the corridor. The corridor does change when the ice "
            f"constraint changes (alternatives.json, corridors A and B), so the "
            f"mechanism works - it is this pair of ships on this day that does not "
            f"separate it.")
        do_not = (
            f"Do not say 'different ships get different routes' on this evidence. "
            f"Say 'the same route costs this ship {d_eta:.2f} days more and "
            f"{abs(100 * d_fuel / a['fuel']):.0f}% less fuel'.")
    else:
        verdict = ("The two ships take different corridors on this day's ice; "
                   "inspect runs[*].track before claiming why.")
        do_not = "Do not attribute the different corridors to any one parameter unmeasured."

    return {
        "date": f"{day:%Y-%m-%d}",
        "runs": runs,
        "track_identical": same_track,
        "same_corridor": same_corridor,
        "max_track_offset_km": None if offset_km is None else round(offset_km, 2),
        "eta_delta_days": round(d_eta, 3) if d_eta is not None else None,
        "fuel_delta": round(d_fuel, 2) if d_fuel is not None else None,
        "fuel_delta_pct": round(100 * d_fuel / a["fuel"], 1) if d_fuel is not None else None,
        "verdict": verdict,
        "do_not_claim": do_not,
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
