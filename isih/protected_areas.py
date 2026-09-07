"""Antarctic protected areas as *route constraints of the correct kind*.

The master prompt (§48A.17) is explicit: "Do not treat every protected area as
an identical 'no-sail' polygon. Determine whether the legal/management regime
imposes a prohibition, permit requirement, operational condition, or other
restriction." This module exists to obey that, because the naive version —
draw 148 polygons, mark them no-go, route around them — is both wrong and
easy, and it is what a team under deadline reaches for.

WHAT THE LAW ACTUALLY SAYS

Both regimes come from Annex V to the Protocol on Environmental Protection to
the Antarctic Treaty, and they are not the same instrument:

  ASPA — Antarctic Specially Protected Area (Annex V, Art. 3).
         Entry is PROHIBITED except in accordance with a permit. For a vessel
         this binds on entry into the area, including its marine parts where
         it has any.

  ASMA — Antarctic Specially Managed Area (Annex V, Art. 4).
         Entry does NOT require a permit. Activities within it must conform to
         the area's Management Plan. This is an operational condition, not a
         prohibition — and conflating the two would tell a captain he may not
         enter waters he is in fact entitled to enter.

That distinction is the whole point of this file, and it has a sharp
consequence for this project: Bharati sits INSIDE ASMA 6, so a system that
modelled ASMAs as no-go would refuse to route to India's own station.

WHAT THE DATA ACTUALLY SHOWS FOR THIS CORRIDOR

Of the 33 protected-area polygons intersecting the project corridor, ZERO are
flagged marine in the Secretariat's own dataset (`Marine` field). Every one is
terrestrial or coastal-terrestrial. So for this voyage the honest finding is:

    No ASPA or ASMA in the Cape Town -> Bharati/Maitri corridor restricts the
    ship's TRANSIT. They restrict what may be done ashore and, for ASPAs,
    require a permit to enter at all.

They are therefore modelled as constraints on STATION OPERATIONS — landing,
offload, small-boat and helicopter activity, personnel movement — and not as
obstacles in the routing mesh. Adding them to the mesh as exclusions would
manufacture a hazard that does not exist and would make the route look
cleverer than the evidence supports.

Where a marine area *does* exist (there are 8 in the full Antarctic dataset,
none here), `constraint_for_vessel()` returns the permit gate, so the logic is
already correct for a corridor that has one — the Ross Sea, for instance.

SOURCE
    Antarctic Treaty Secretariat, `apa_shape_2024.zip` (edition 2024).
    77 unique ASPAs / 142 polygons, 6 ASMAs / 6 polygons, 148 total.
    CRS EPSG:3031, read from the .prj, not assumed.
    Fetch with `python isih/download_protected_areas.py`.

Usage:
    python isih/protected_areas.py            # write the corridor extract
    python isih/protected_areas.py --report   # print what is near the stations
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

from pyproj import Transformer

DATA_DIR = Path(__file__).parent / "data" / "protected_areas"
OUT_JSON = Path(__file__).parent / "figures" / "protected_areas.json"

# Same corridor the rest of the prototype uses. Deliberately a constant here
# and a config item later — docs/backlog.md carries that as an open item.
CORRIDOR = {"lon_min": -5.0, "lon_max": 85.0, "lat_min": -80.0, "lat_max": -48.0}

# Station positions as NCPOR publishes them, converted from DMS.
#   Maitri  70 45 52 S, 11 44 03 E
#   Bharati 69 24.41 S, 76 11.72 E
STATIONS = {
    "Bharati": (76.19533, -69.40683),
    "Maitri": (11.73417, -70.76444),
}

_TO_LL = Transformer.from_crs("EPSG:3031", "EPSG:4326", always_xy=True)
_TO_XY = Transformer.from_crs("EPSG:4326", "EPSG:3031", always_xy=True)


@dataclass(frozen=True)
class ProtectedArea:
    """One polygon from the register, with the regime that governs it."""

    kind: str            # "ASPA" | "ASMA"
    number: str
    name: str
    proponent: str
    instrument: str      # the Measure/Recommendation that designates it
    marine: bool
    area_km2: float
    rings: list          # list of rings, each a list of [lon, lat]
    rings_omitted: int = 0   # dropped from the DRAWING only; see DRAW_MIN_EXTENT_M

    @property
    def entry_regime(self) -> str:
        """The legal gate on ENTERING this area. Annex V, Arts. 3 and 4."""
        if self.kind == "ASPA":
            return "permit_required"      # Art. 3(4): entry prohibited without one
        return "management_plan"          # Art. 4: no permit; plan governs activity

    def constraint_for_vessel(self) -> dict:
        """What this area actually binds for a ship, as opposed to a person.

        A terrestrial ASPA cannot be entered by a hull. It constrains the
        boat/helicopter/foot activity the ship mounts, which is why the
        answer is scoped by `applies_to` rather than being a yes/no no-go.
        """
        if self.marine:
            return {
                "applies_to": "transit_and_operations",
                "effect": self.entry_regime,
                "note": (
                    "Marine area: the vessel itself can enter it, so the "
                    "regime binds navigation as well as shore activity."
                ),
            }
        return {
            "applies_to": "shore_operations",
            "effect": self.entry_regime,
            "note": (
                "Terrestrial area: does not restrict the ship's track. "
                "Binds landing, small-boat, helicopter and personnel activity."
            ),
        }


# Display simplification tolerance, in projected metres. The register is
# surveyed to metres; the demo draws the whole 90-degree corridor on a laptop
# screen where one pixel is several kilometres, so full resolution costs 2 MB
# to show detail no one can see. 500 m is two orders of magnitude finer than
# the 25 km ice grid the route is computed on.
#
# This affects DRAWING ONLY. Station containment and the distances in
# `station_context()` are computed from the unsimplified rings at build time,
# so no published number moves when this tolerance changes.
SIMPLIFY_M = 500.0

# ASPA 102 (Rookery Islands) is an archipelago of hundreds of islets. Each ring
# is already minimal, so RDP cannot reduce it, and it alone was 97% of the
# drawn artifact — 17,695 of 18,260 vertices — for features smaller than one
# screen pixel at corridor scale. Rings whose bounding box is smaller than this
# are omitted FROM THE DRAWING and counted in `rings_omitted_for_display`, so
# the omission is visible in the artifact rather than silent.
#
# Again: drawing only. The area still appears, with its full record, its
# regime, and its exact-geometry distance to the stations.
DRAW_MIN_EXTENT_M = 2000.0


def _rings(shape) -> list:
    """Split a shapefile polygon into its parts. Coordinates stay EPSG:3031."""
    pts = shape.points
    parts = list(shape.parts) + [len(pts)]
    return [pts[parts[i] : parts[i + 1]] for i in range(len(parts) - 1)]


def _simplify(ring, tol_m: float):
    """Ramer-Douglas-Peucker, iterative so a long coastline cannot blow the stack."""
    if tol_m <= 0 or len(ring) < 3:
        return ring
    keep = [False] * len(ring)
    keep[0] = keep[-1] = True
    stack = [(0, len(ring) - 1)]
    while stack:
        lo, hi = stack.pop()
        if hi <= lo + 1:
            continue
        ax, ay = ring[lo]
        bx, by = ring[hi]
        dx, dy = bx - ax, by - ay
        norm = (dx * dx + dy * dy) ** 0.5
        worst, worst_i = -1.0, -1
        for i in range(lo + 1, hi):
            px, py = ring[i]
            if norm < 1e-9:
                d = ((px - ax) ** 2 + (py - ay) ** 2) ** 0.5
            else:
                d = abs(dy * px - dx * py + bx * ay - by * ax) / norm
            if d > worst:
                worst, worst_i = d, i
        if worst > tol_m:
            keep[worst_i] = True
            stack.append((lo, worst_i))
            stack.append((worst_i, hi))
    out = [p for p, k in zip(ring, keep) if k]
    # A ring needs 4 points to close; if simplification collapsed it, keep the
    # original rather than emitting a degenerate polygon.
    return out if len(out) >= 4 else ring


def _point_in_ring(pt, ring) -> bool:
    """Even-odd ray cast. Both in the same projected CRS."""
    x, y = pt
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if (yi > y) != (yj > y):
            denom = (yj - yi) or 1e-30
            if x < (xj - xi) * (y - yi) / denom + xi:
                inside = not inside
        j = i
    return inside


def _min_dist_km(pt, ring) -> float:
    """Distance to the nearest ring VERTEX, in km.

    Vertex distance, not true edge distance — it slightly over-states the gap
    on long straight segments. Stated rather than hidden because these numbers
    get quoted: it is a proximity indicator for "what is near the station",
    not a separation guarantee, and nothing safety-critical depends on it.
    """
    x, y = pt
    return min(((x - a) ** 2 + (y - b) ** 2) ** 0.5 for a, b in ring) / 1000.0


def load_areas(
    shp_path: Path | None = None,
    corridor: dict | None = None,
    simplify_m: float = 0.0,
    min_extent_m: float = 0.0,
):
    """Read the register. `corridor=None` returns all of Antarctica.

    `simplify_m` defaults to 0 — EXACT geometry. Simplification is opt-in and
    used only for the drawn artifact, never for containment or distances.
    """
    try:
        import shapefile  # pyshp
    except ImportError:  # pragma: no cover - dependency guidance
        raise SystemExit(
            "pyshp is required to read the ATS shapefile: pip install pyshp"
        )

    if shp_path is None:
        shp_path = next(DATA_DIR.glob("*.shp"), None)
    if shp_path is None or not Path(shp_path).exists():
        raise SystemExit(
            "protected-areas shapefile not found — run "
            "`python isih/download_protected_areas.py` first"
        )

    reader = shapefile.Reader(str(shp_path))
    fields = [f[0] for f in reader.fields[1:]]
    idx = {f: i for i, f in enumerate(fields)}

    out: list[ProtectedArea] = []
    for sr in reader.shapeRecords():
        rec, shape = sr.record, sr.shape
        rings_ll = []
        omitted = 0
        keep = corridor is None
        for ring in _rings(shape):
            if len(ring) < 4:
                continue

            # Corridor membership is decided on the RAW ring, before any
            # display thinning. Deciding it afterwards meant an area whose
            # every ring fell below the draw threshold (ASPA 102's 158 islets)
            # never set `keep`, dropped out of the display pass, and silently
            # fell back to full-resolution geometry — the exact opposite of
            # what the thinning was for.
            raw_lons, raw_lats = _TO_LL.transform(
                [p[0] for p in ring], [p[1] for p in ring]
            )
            if corridor is not None and not keep:
                if (
                    max(raw_lons) >= corridor["lon_min"]
                    and min(raw_lons) <= corridor["lon_max"]
                    and max(raw_lats) >= corridor["lat_min"]
                    and min(raw_lats) <= corridor["lat_max"]
                ):
                    keep = True

            # Simplify in metres, where the tolerance means something, then
            # reproject. Doing it the other way round would make the tolerance
            # vary with latitude.
            ring = _simplify(ring, simplify_m)
            if min_extent_m > 0:
                xs_m = [p[0] for p in ring]
                ys_m = [p[1] for p in ring]
                span = max(max(xs_m) - min(xs_m), max(ys_m) - min(ys_m))
                if span < min_extent_m:
                    omitted += 1
                    continue

            if simplify_m > 0:
                lons, lats = _TO_LL.transform(
                    [p[0] for p in ring], [p[1] for p in ring]
                )
            else:
                lons, lats = raw_lons, raw_lats
            # 4 dp is ~11 m at these latitudes: far finer than the 25 km ice
            # grid the route is computed on, and it keeps the artifact small.
            rings_ll.append([[round(a, 4), round(b, 4)] for a, b in zip(lons, lats)])

        if not keep:
            continue

        out.append(
            ProtectedArea(
                kind=str(rec[idx["Tipo_apa"]]).strip(),
                number=str(rec[idx["Numero_apa"]]).strip(),
                name=str(rec[idx["Name"]]).strip(),
                proponent=str(rec[idx["Propon"]]).strip(),
                instrument=str(rec[idx["DesigInstr"]]).strip(),
                marine=str(rec[idx["Marine"]]).strip() == "1",
                area_km2=float(rec[idx["Area_km"]] or 0.0),
                rings=rings_ll,
                rings_omitted=omitted,
            )
        )
    return out


def station_context(areas, stations: dict | None = None, near_km: float = 60.0):
    """For each station: which areas contain it, and which are close.

    Containment is computed in EPSG:3031 metres, which is what the register is
    published in — reprojecting to lat/lon first and testing there would
    distort the test at these latitudes.
    """
    stations = stations or STATIONS
    result = {}
    for name, (lon, lat) in stations.items():
        px, py = _TO_XY.transform(lon, lat)
        containing, nearby = [], []
        for a in areas:
            best = None
            hit = False
            for ring_ll in a.rings:
                xs, ys = _TO_XY.transform(
                    [p[0] for p in ring_ll], [p[1] for p in ring_ll]
                )
                ring_xy = list(zip(xs, ys))
                if _point_in_ring((px, py), ring_xy):
                    hit = True
                d = _min_dist_km((px, py), ring_xy)
                best = d if best is None else min(best, d)
            if hit:
                containing.append({**_brief(a), "distance_km": 0.0})
            elif best is not None and best <= near_km:
                nearby.append({**_brief(a), "distance_km": round(best, 1)})
        result[name] = {
            "lat": lat,
            "lon": lon,
            "inside": containing,
            "nearby": sorted(nearby, key=lambda r: r["distance_km"]),
        }
    return result


def _brief(a: ProtectedArea) -> dict:
    return {
        "kind": a.kind,
        "number": a.number,
        "name": a.name,
        "proponent": a.proponent,
        "instrument": a.instrument,
        "marine": a.marine,
        "entry_regime": a.entry_regime,
        "constraint": a.constraint_for_vessel(),
    }


def build_extract(shp_path: Path | None = None) -> dict:
    """The committed artifact the demo reads. No shapefile at runtime.

    Two passes on purpose: the exact geometry answers "is Bharati inside
    ASMA 6 and how far is Stornes", and a simplified copy is what gets drawn.
    The numbers therefore never depend on the drawing tolerance.
    """
    areas = load_areas(shp_path, CORRIDOR)                      # exact
    drawn = load_areas(
        shp_path, CORRIDOR, simplify_m=SIMPLIFY_M, min_extent_m=DRAW_MIN_EXTENT_M
    )
    rings_by_key = {(a.kind, a.number, a.name): (a.rings, a.rings_omitted) for a in drawn}
    marine = [a for a in areas if a.marine]
    return {
        "source": "Antarctic Treaty Secretariat, apa_shape_2024.zip (edition 2024)",
        "source_url": "https://documents.ats.aq/gis/apa_shape_2024.zip",
        "legal_basis": (
            "Protocol on Environmental Protection to the Antarctic Treaty, "
            "Annex V, Art. 3 (ASPA: entry by permit only) and Art. 4 "
            "(ASMA: no permit to enter; Management Plan governs activity)"
        ),
        "crs_source": "EPSG:3031 (read from .prj)",
        "geometry_note": (
            f"Drawn outlines simplified to {SIMPLIFY_M:.0f} m "
            f"(Ramer-Douglas-Peucker); rings spanning under "
            f"{DRAW_MIN_EXTENT_M:.0f} m omitted from the drawing and counted in "
            f"rings_omitted_for_display. Display only \u2014 station containment "
            f"and the distances below are computed from the unsimplified register."
        ),
        "corridor": CORRIDOR,
        "counts": {
            "polygons": len(areas),
            "aspa_polygons": sum(1 for a in areas if a.kind == "ASPA"),
            "asma_polygons": sum(1 for a in areas if a.kind == "ASMA"),
            "marine": len(marine),
        },
        "transit_finding": (
            "No protected area in this corridor is flagged marine, so none "
            "restricts the vessel's transit. They bind shore operations; "
            "ASPAs additionally require a permit to enter at all."
            if not marine
            else f"{len(marine)} marine area(s) bind transit — see per-area constraint."
        ),
        "stations": station_context(areas),
        "areas": [
            {
                **_brief(a),
                "area_km2": a.area_km2,
                "rings": rings_by_key.get((a.kind, a.number, a.name), (a.rings, 0))[0],
                "rings_omitted_for_display": rings_by_key.get(
                    (a.kind, a.number, a.name), (a.rings, 0)
                )[1],
            }
            for a in areas
        ],
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--shp", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=OUT_JSON)
    ap.add_argument("--report", action="store_true", help="print, do not write")
    args = ap.parse_args(argv)

    extract = build_extract(args.shp)

    if args.report:
        c = extract["counts"]
        print(f"corridor polygons: {c['polygons']}  "
              f"(ASPA {c['aspa_polygons']}, ASMA {c['asma_polygons']}, "
              f"marine {c['marine']})")
        print(f"\n{extract['transit_finding']}\n")
        for name, ctx in extract["stations"].items():
            print(f"{name} ({ctx['lat']}, {ctx['lon']})")
            for a in ctx["inside"]:
                print(f"  INSIDE  {a['kind']} {a['number']} — {a['name'][:46]}")
                print(f"          {a['instrument']} | {a['entry_regime']} | "
                      f"proponent: {a['proponent'][:52]}")
            for a in ctx["nearby"]:
                print(f"  {a['distance_km']:6.1f} km  {a['kind']} {a['number']} — "
                      f"{a['name'][:44]}")
            print()
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(extract, indent=1))
    kb = args.out.stat().st_size / 1024
    print(f"wrote {args.out} ({kb:.0f} KB, {extract['counts']['polygons']} polygons)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
