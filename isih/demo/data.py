"""Loaders for the ISIH demo. Every function reads a real file already on disk.

Nothing here computes a number that is not already published in
docs/ISIH_RESULTS.md. The app reads those outputs — routes.json,
destination_window.json, and the NOAA/NSIDC daily files — so what is on screen
cannot disagree with what is in the results document.

Station open/closed status comes from destination_window.json, which was
derived from the vessel-performance mesh. It is deliberately NOT recomputed
from the raw raster here: a different aggregation would give a different
number, and two numbers for one fact is how a demo dies in front of a judge.
"""

from __future__ import annotations

import json
import re
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
import xarray as xr
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[2]
ISIH = ROOT / "isih"
FIG = ISIH / "figures"
NSIDC = ISIH / "data" / "nsidc_sic"

# isih/ is a flat script directory, not a package; make its QC loader importable.
if str(ISIH) not in sys.path:
    sys.path.insert(0, str(ISIH))
from ice_quality import load_sic  # noqa: E402

# Same corridor as make_route_figure.MESH_BOUNDS, and the same subsample step,
# so the raster on screen is the raster the route was computed on.
BOUNDS = {"lat_min": -70.0, "lat_max": -30.0, "lon_min": 15.0, "lon_max": 80.0}
STEP = 2

STATIONS = [
    {"name": "Cape Town", "lat": -33.9, "lon": 18.4, "role": "start"},
    {"name": "Bharati", "lat": -69.4, "lon": 76.2, "role": "destination"},
    {"name": "Bharati approach (100 km N)", "lat": -68.5, "lon": 76.2,
     "role": "approach"},
]

SOURCE_ICE = "NOAA/NSIDC Sea Ice Concentration CDR G02202 v6, 25 km"
SOURCE_ROUTE = "PolarRoute 1.1.11 + meshiphi (British Antarctic Survey, MIT licence)"


# --------------------------------------------------------------------------
# destination window — the 74 % number
# --------------------------------------------------------------------------

@lru_cache(maxsize=1)
def window() -> dict:
    """The destination-window result, with no-data targets separated out.

    `destination_window.json` computes `passable` as "the mesh gives this cell
    a speed greater than zero". When a target lies OUTSIDE the routing mesh
    there is no cell at all, so `sic_qa_on` is null and `passable` comes back
    False — and a target that was never scored then reads as closed on every
    single day. The file still carries one such row, "Maitri (Leningradskaya
    coast)", left behind when Maitri was deliberately dropped as a target
    (isih/destination_window.py:27 — it is ~100 km inland and its maritime
    offload point is not sourced). All 31 of its days are null.

    "100 % closed" and "never measured" are the same three characters on a
    slide and opposite claims in a viva, so they are separated here rather
    than trusted to a reader. Master prompt §48A.15: UNAVAILABLE is its own
    state, distinct from a value.

    Any future target that is never scored takes this path automatically.
    """
    doc = json.loads((FIG / "destination_window.json").read_text())

    scored, unavailable = {}, {}
    for name, summ in doc.get("summary", {}).items():
        observed = [
            row[name]["sic_qa_on"]
            for row in doc.get("daily", [])
            if name in row and row[name].get("sic_qa_on") is not None
        ]
        if observed:
            scored[name] = summ
        else:
            unavailable[name] = {
                "reason": "no mesh cell contains this point — never scored",
                "days_with_data": 0,
                "days_in_window": len(doc.get("daily", [])),
            }

    doc["summary"] = scored
    doc["unavailable"] = unavailable
    return doc


def dates() -> list[str]:
    return [row["date"] for row in window()["daily"]]


def day_status(d: str) -> dict:
    for row in window()["daily"]:
        if row["date"] == d:
            return row
    raise KeyError(d)


# --------------------------------------------------------------------------
# route and mesh cells — from routes.json exactly as PolarRoute wrote it
# --------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _routes_json() -> dict:
    return json.loads((FIG / "routes.json").read_text())


def _parse_polygon(geom) -> list[list[float]]:
    """Outer ring of a cellbox as [[lon, lat], ...]. Accepts GeoJSON or WKT."""
    if isinstance(geom, dict):
        return [[float(x), float(y)] for x, y in geom["coordinates"][0]]
    m = re.search(r"POLYGON\s*\(\((.*?)\)\)", str(geom))
    if not m:
        raise ValueError(f"unrecognised cellbox geometry: {str(geom)[:60]}")
    pts = [p.strip().split() for p in m.group(1).split(",")]
    return [[float(x), float(y)] for x, y in pts]


def _clean(v):
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if np.isnan(f) else round(f, 1)


@lru_cache(maxsize=1)
def cells() -> list[dict]:
    """The 236 mesh cells the route was solved on, with the ice value each carried."""
    out = []
    for i, c in enumerate(_routes_json()["cellboxes"]):
        out.append({
            "id": c.get("id", i),
            "ring": _parse_polygon(c["geometry"]),
            "sic": _clean(c.get("SIC")),
            "land": bool(c.get("land", False)),
            "inaccessible": bool(c.get("inaccessible", False)),
        })
    return out


@lru_cache(maxsize=1)
def _raster_points() -> tuple[np.ndarray, np.ndarray]:
    """The exact ice points the figure was drawn from: (lon/lat [n,2], SIC %)."""
    rows = np.loadtxt(FIG / "sic_points.csv", delimiter=",", skiprows=1)
    return rows[:, [1, 0]], rows[:, 2]          # csv columns are lat, long, SIC


def _sample_ice(path: np.ndarray, per_leg: int) -> np.ndarray:
    """Ice along a polyline — the same method as isih/plot_route.py.

    Each leg is densified to `per_leg` points; each point takes the nearest
    raster cell within 1.0 degree. Reproduced here rather than imported so the
    demo has no scipy dependency, and asserted against the figure's numbers in
    the tests: the app must not show one "max ice" while the slide shows another.
    """
    pts, sic = _raster_points()
    legs = [np.c_[np.linspace(path[i][0], path[i + 1][0], per_leg),
                  np.linspace(path[i][1], path[i + 1][1], per_leg)]
            for i in range(len(path) - 1)]
    q = np.vstack(legs)
    out = []
    for chunk in np.array_split(q, max(1, len(q) // 500)):
        d2 = ((chunk[:, None, :] - pts[None, :, :]) ** 2).sum(axis=2)
        idx = d2.argmin(axis=1)
        near = np.sqrt(d2[np.arange(len(chunk)), idx]) < 1.0
        out.append(sic[idx[near]])
    return np.concatenate(out) if out else np.array([])


@lru_cache(maxsize=1)
def route() -> dict:
    r = _routes_json()
    paths = r["paths"]
    feats = paths["features"] if isinstance(paths, dict) else paths
    f = feats[0]
    props = f["properties"]
    coords = np.array(f["geometry"]["coordinates"], dtype=float)
    limit = float(window()["ice_limit_pct"])

    along = _sample_ice(coords, per_leg=60)
    straight = _sample_ice(np.array([coords[0], coords[-1]]), per_leg=2000)
    return {
        "name": props.get("name"),
        "from": props.get("from"),
        "to": props.get("to"),
        "ice_date": window()["start"],
        "engine": SOURCE_ROUTE,
        "coords": [[round(float(lon), 3), round(float(lat), 3)] for lon, lat in coords],
        # Cumulative days-since-departure at each waypoint. PolarRoute reports
        # one arrival time per leg, so the departure point is prepended at
        # zero to give one value per coordinate. This is what lets the day
        # slider place the ship on its own track instead of only changing the
        # ice underneath it — §5 asks the system to look further down the
        # route, which needs to know where "down the route" currently is.
        "traveltime_cumulative": [0.0] + [
            round(float(t), 4) for t in (props.get("traveltime") or [])
        ],
        "total_traveltime_days": float(props["total_traveltime"]),
        "n_legs": len(props.get("CellIndices", [])),
        # sampled from the satellite raster along each line, as in the figure
        "max_sic_pct_along_route": round(float(along.max()), 1) if along.size else None,
        "route_samples_over_limit": int((along > limit).sum()),
        "straight_max_sic_pct": round(float(straight.max()), 1) if straight.size else None,
        "straight_samples_over_limit": int((straight > limit).sum()),
    }


# --------------------------------------------------------------------------
# daily ice raster — the real satellite files, QA on or off
# --------------------------------------------------------------------------

def nsidc_file(d: str) -> Path:
    hits = sorted(NSIDC.glob(f"sic_pss25_{d.replace('-', '')}_*.nc"))
    if not hits:
        raise FileNotFoundError(f"no NSIDC file for {d} in {NSIDC}")
    return hits[0]


def preflight() -> list[str]:
    """Dates in the window with no file on disk. Non-empty means do not start."""
    missing = []
    for d in dates():
        try:
            nsidc_file(d)
        except FileNotFoundError:
            missing.append(d)
    return missing


@lru_cache(maxsize=1)
def _lonlat() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(lon, lat, inside-corridor mask) for the subsampled grid — computed once."""
    ds = xr.open_dataset(nsidc_file(dates()[0]))
    tr = Transformer.from_crs("EPSG:3412", "EPSG:4326", always_xy=True)
    xg, yg = np.meshgrid(ds.x.values, ds.y.values)
    lon, lat = tr.transform(xg, yg)
    lon, lat = lon[::STEP, ::STEP], lat[::STEP, ::STEP]
    inside = ((lat >= BOUNDS["lat_min"]) & (lat <= BOUNDS["lat_max"])
              & (lon >= BOUNDS["lon_min"]) & (lon <= BOUNDS["lon_max"]))
    return lon, lat, inside


@lru_cache(maxsize=64)
def day_field(d: str, qa: bool) -> dict:
    """One day of ice inside the corridor.

    qa=True  — cells the CDR's own QA flag marks as land-spillover or
               no-input are returned separately as `unknown`, not as a value.
    qa=False — what an unguarded reader sees: those cells come back as 0.0 %.
    """
    sic, suspect = load_sic(nsidc_file(d), apply_qa=qa)
    sic, suspect = sic[::STEP, ::STEP], suspect[::STEP, ::STEP]
    lon, lat, inside = _lonlat()
    known = inside & np.isfinite(sic)
    unknown = inside & suspect
    pct = np.rint(sic[known] * 100.0).astype(int)
    return {
        "date": d,
        "qa": qa,
        "source": SOURCE_ICE,
        "lat": np.round(lat[known], 2).tolist(),
        "lon": np.round(lon[known], 2).tolist(),
        "sic": pct.tolist(),
        "unknown_lat": np.round(lat[unknown], 2).tolist(),
        "unknown_lon": np.round(lon[unknown], 2).tolist(),
        "n_known": int(known.sum()),
        "n_unknown": int(unknown.sum()),
        "n_exact_zero": int((pct == 0).sum()),
    }


# --------------------------------------------------------------------------
# the one payload the page boots from
# --------------------------------------------------------------------------

# Published numbers, quoted verbatim from docs/TRUE_CLAIMS.md and
# docs/ISIH_RESULTS.md §6. The "do not claim" lines ship with them on purpose.
RESULTS = {
    "source": "docs/ISIH_RESULTS.md, docs/TRUE_CLAIMS.md",
    "claims": [
        "Forecasting sea-ice concentration 1 to 7 days ahead, the prototype "
        "model beats persistence at every horizon, by +18.5 % to +30.6 %.",
        "Bharati's own grid cell was closed to this vessel on 74 % of "
        "December 2019 days; the approach 100 km north was open every day.",
        "Four of the eight days Bharati appeared reachable were data "
        "artifacts reading exactly 0.0 %.",
        "Masking those cells moves coastal ice up, 46.8 % to 54.6 % mean — "
        "the fix makes the router more cautious, not less.",
        "Route computed on real satellite ice with a real open-source router: "
        "8.6 days steaming, Cape Town to Bharati.",
    ],
    "do_not_claim": [
        "Any fuel figure — the vessel's fuel model is uncalibrated.",
        "8.6 days as a voyage duration — it is steaming time with no waiting.",
        "That daily re-planning beats static planning — on this one departure "
        "date it did not.",
        "That the prototype corrects a live forecast — it corrects a "
        "reanalysis background; the production model corrects the forecast.",
    ],
}


def summary() -> dict:
    w = window()
    return {
        "vessel": w["vessel"],
        "ice_limit_pct": w["ice_limit_pct"],
        "start": w["start"],
        "dates": dates(),
        "summary": w["summary"],
        "unavailable": w.get("unavailable", {}),
        "daily": w["daily"],
        "note": w["note"],
        "stations": STATIONS,
        "bounds": BOUNDS,
        "sources": {"ice": SOURCE_ICE, "route": SOURCE_ROUTE},
        "results": RESULTS,
        "data_mode": DATA_MODE,
    }


# --- Data mode -------------------------------------------------------------
# Master prompt §27 and §48A.15: the system must distinguish LIVE DATA from
# HISTORICAL REPLAY from SIMULATED INPUT, and must never present replay as
# live. This demo replays real satellite observations from December 2019.
# Every one of those bytes is real — but it is not now, and a judge glancing
# at a moving ice map is entitled to assume it is. So the app says so, in
# words, on screen, rather than relying on the date label being noticed.
DATA_MODE = {
    "mode": "HISTORICAL REPLAY",
    "window": "1–31 December 2019",
    "means": (
        "Real satellite observations from a past season, replayed. "
        "Not a live feed and not simulated data."
    ),
    "live_capable": (
        "The same pipeline ingests the live CMEMS forecast — a daily harvest "
        "has been running since 31 Aug 2026 (7 consecutive cycles archived). "
        "December 2019 is used here because it is a season with ground truth "
        "to score against."
    ),
}


@lru_cache(maxsize=1)
def protected() -> dict:
    """Antarctic Treaty Secretariat protected areas for the corridor.

    Reads the committed extract, never the shapefile — the running app has no
    geospatial dependency, so there is nothing new that can fail live.
    Returns an empty, explicitly-labelled structure if the extract is absent
    rather than raising: a missing optional layer should not take down a
    demo whose whole point is graceful degradation.
    """
    path = FIG / "protected_areas.json"
    if not path.exists():
        return {"available": False, "reason": f"{path.name} not generated",
                "areas": [], "stations": {}}

    doc = json.loads(path.read_text())

    # Only the areas that fall inside the demo map's own viewport can be
    # drawn; the rest are still reported in the counts so the panel does not
    # quietly under-state what is in the corridor.
    drawable = []
    for a in doc.get("areas", []):
        rings = [
            r for r in a.get("rings", [])
            if any(BOUNDS["lon_min"] <= p[0] <= BOUNDS["lon_max"]
                   and BOUNDS["lat_min"] <= p[1] <= BOUNDS["lat_max"] for p in r)
        ]
        if rings:
            drawable.append({**a, "rings": rings})

    return {
        "available": True,
        "source": doc.get("source"),
        "legal_basis": doc.get("legal_basis"),
        "geometry_note": doc.get("geometry_note"),
        "counts": doc.get("counts", {}),
        "transit_finding": doc.get("transit_finding"),
        "stations": doc.get("stations", {}),
        "drawn": len(drawable),
        "areas": drawable,
    }
