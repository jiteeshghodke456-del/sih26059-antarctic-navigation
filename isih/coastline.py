"""Build a committed coastline extract for the corridor.

§2.2 asks for "very accurate maps" and to "preserve sailor learning curves".
The chart had no coastline, no land and no graticule, so it read as a scatter
plot of ice cells rather than as a chart — every reference the specification
names (Polarstern MapViewer, OpenCPN, and even Nuyina's own navigational view)
carries land and a graticule.

Method follows `isih/protected_areas.py` exactly, and for the same reason: the
heavy vector work happens at build time and only a small simplified extract is
committed, so the running app keeps **zero geospatial runtime dependencies**
and nothing new can fail in front of a judge. The demo never reads a shapefile
or reprojects anything; it reads one JSON file.

Source: Natural Earth, which is **public domain** with no attribution
requirement — the cleanest licence available for something we redistribute in
a repository. Natural Earth's Antarctic coastline is a general-purpose
rendering of the ice front.

What this deliberately is NOT: the BAS Antarctic Digital Database, which is
CC BY 4.0, native EPSG:3031, and separates ice-coastline from rock-coastline,
grounding-line and ice-shelf-front — distinctions that are operationally real
at Bharati and that no general dataset offers. ADD is the right upgrade for
the 60–70°S leg and is filed in docs/backlog.md; hybrid regional sourcing is
what R/V Laura Bassi's own dashboard does today (NGA for Antarctica, LINZ for
New Zealand, OSM elsewhere).

Usage:
    python isih/coastline.py            # fetch, clip, simplify, write
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import urllib.error
import urllib.request
from pathlib import Path

FIG = Path(__file__).resolve().parent / "figures"
OUT = FIG / "coastline.json"

# Natural Earth 1:50m. 1:10m is sharper but roughly six times the payload for
# detail finer than a 25 km ice pixel, which is the resolution the rest of
# this screen works at.
BASE = ("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/"
        "master/geojson/")
LAND = BASE + "ne_50m_land.geojson"
COAST = BASE + "ne_50m_coastline.geojson"

# A little wider than the drawn bounds (15–80 E, 70–30 S) so polygons clipped
# at the frame still close cleanly off-screen rather than cutting inland.
BOX = {"lon_min": 8.0, "lon_max": 88.0, "lat_min": -78.0, "lat_max": -26.0}

# Douglas–Peucker tolerance in degrees. 0.02° is about 2 km of latitude —
# below the 25 km ice pixel, so simplification cannot move the coast by a
# visible amount at this scale. Display only; nothing is computed from it.
SIMPLIFY_DEG = 0.02
MIN_RING = 4


def fetch(url: str, timeout: int = 120) -> dict:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.URLError as exc:
        raise SystemExit(f"could not reach Natural Earth: {exc}")


def _perp(pt, a, b) -> float:
    (x, y), (x1, y1), (x2, y2) = pt, a, b
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(x - x1, y - y1)
    t = max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(x - (x1 + t * dx), y - (y1 + t * dy))


def rdp(pts: list, eps: float) -> list:
    """Ramer–Douglas–Peucker, iterative so a long coast cannot blow the stack."""
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        worst, idx = 0.0, -1
        for k in range(i + 1, j):
            d = _perp(pts[k], pts[i], pts[j])
            if d > worst:
                worst, idx = d, k
        if idx != -1 and worst > eps:
            keep[idx] = True
            stack.append((i, idx))
            stack.append((idx, j))
    return [p for p, k in zip(pts, keep) if k]


def _touches(ring: list) -> bool:
    return any(BOX["lon_min"] <= x <= BOX["lon_max"]
               and BOX["lat_min"] <= y <= BOX["lat_max"] for x, y in ring)


def clip_polygon(ring: list) -> list:
    """Sutherland-Hodgman clip of a closed ring to the corridor box.

    A touch test is not enough: Antarctica is a single ring spanning all 360
    degrees of longitude, so keeping any ring that intersects the box keeps
    the entire continent and the file comes out at 300 KB with a global
    extent. Clipping is what makes the extract an extract.
    """
    def inside(p, edge):
        x, y = p
        return {"l": x >= BOX["lon_min"], "r": x <= BOX["lon_max"],
                "b": y >= BOX["lat_min"], "t": y <= BOX["lat_max"]}[edge]

    def cut(a, b, edge):
        (x1, y1), (x2, y2) = a, b
        if edge in ("l", "r"):
            xe = BOX["lon_min"] if edge == "l" else BOX["lon_max"]
            t = (xe - x1) / (x2 - x1) if x2 != x1 else 0.0
            return (xe, y1 + t * (y2 - y1))
        ye = BOX["lat_min"] if edge == "b" else BOX["lat_max"]
        t = (ye - y1) / (y2 - y1) if y2 != y1 else 0.0
        return (x1 + t * (x2 - x1), ye)

    out = list(ring)
    for edge in ("l", "r", "b", "t"):
        if not out:
            return []
        buf, prev = [], out[-1]
        for cur in out:
            ci, pi = inside(cur, edge), inside(prev, edge)
            if ci:
                if not pi:
                    buf.append(cut(prev, cur, edge))
                buf.append(cur)
            elif pi:
                buf.append(cut(prev, cur, edge))
            prev = cur
        out = buf
    return out


def clip_line(line: list) -> list:
    """Split an open coastline into the runs that fall inside the box."""
    def inside(p):
        x, y = p
        return (BOX["lon_min"] <= x <= BOX["lon_max"]
                and BOX["lat_min"] <= y <= BOX["lat_max"])
    runs, cur = [], []
    for pt in line:
        if inside(pt):
            cur.append(pt)
        elif cur:
            runs.append(cur); cur = []
    if cur:
        runs.append(cur)
    return [r for r in runs if len(r) >= 2]


def _rings(geom: dict):
    t = geom.get("type")
    if t == "Polygon":
        return list(geom["coordinates"])
    if t == "MultiPolygon":
        return [r for poly in geom["coordinates"] for r in poly]
    if t == "LineString":
        return [geom["coordinates"]]
    if t == "MultiLineString":
        return list(geom["coordinates"])
    return []


def build(simplify: float = SIMPLIFY_DEG) -> dict:
    land = fetch(LAND)
    coast = fetch(COAST)

    def collect(doc: dict, closed: bool) -> list:
        out = []
        for feat in doc.get("features", []):
            for ring in _rings(feat.get("geometry") or {}):
                pts = [(float(c[0]), float(c[1])) for c in ring if len(c) >= 2]
                if len(pts) < 2 or not _touches(pts):
                    continue
                pieces = [clip_polygon(pts)] if closed else clip_line(pts)
                for piece in pieces:
                    if len(piece) < (MIN_RING if closed else 2):
                        continue
                    simp = rdp(piece, simplify)
                    if len(simp) >= (MIN_RING if closed else 2):
                        out.append([[round(x, 4), round(y, 4)] for x, y in simp])
        return out

    land_rings = collect(land, closed=True)
    coast_lines = collect(coast, closed=False)

    return {
        "source": "Natural Earth 1:50m physical (land, coastline)",
        "source_url": BASE,
        "licence": "public domain — no attribution required "
                   "(naturalearthdata.com/about/terms-of-use)",
        "crs": "EPSG:4326",
        "clip": BOX,
        "simplify_deg": simplify,
        "simplify_note": (
            "Douglas-Peucker at 0.02 degrees, about 2 km — well below the "
            "25 km ice pixel, so the coast cannot move a visible distance at "
            "this scale. Display only: nothing is computed from this file."
        ),
        "not_used": (
            "The BAS Antarctic Digital Database (CC BY 4.0, native EPSG:3031) "
            "separates ice-coastline, rock-coastline, grounding-line and "
            "ice-shelf-front. Those distinctions are operationally real at "
            "Bharati and Natural Earth does not carry them. Filed as the "
            "upgrade for the 60-70S leg."
        ),
        "counts": {"land_rings": len(land_rings), "coast_lines": len(coast_lines)},
        "land": land_rings,
        "coast": coast_lines,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--simplify", type=float, default=SIMPLIFY_DEG)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args(argv)

    doc = build(args.simplify)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(doc, separators=(",", ":")))
    kb = args.out.stat().st_size / 1024
    pts = sum(len(r) for r in doc["land"]) + sum(len(r) for r in doc["coast"])
    print(f"wrote {args.out}  ({kb:.0f} KB)")
    print(f"  {doc['counts']['land_rings']} land rings, "
          f"{doc['counts']['coast_lines']} coastline segments, {pts} points")
    return 0


if __name__ == "__main__":
    sys.exit(main())
