"""One land test, used everywhere land matters.

There were two places that needed to know whether a point is ashore - iceberg
spawning and the wind/current vectors - and neither had one, which is how seven
of twenty-six icebergs ended up sitting on Antarctica and how weather came to be
drawn across the continent. A previous attempt clamped bergs into the domain's
bounding BOX, which is not the same question and made it worse.

The coastline extract already committed for the chart is enough: 16 rings and
545 vertices, of which ring 14 is the Antarctic mainland and ring 15 is Africa.
Standard even-odd ray casting, vectorised over points and looped over the small
number of rings.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import numpy as np

COASTLINE = Path(__file__).resolve().parents[1] / "figures" / "coastline.json"


@lru_cache(maxsize=1)
def _rings() -> tuple:
    if not COASTLINE.exists():
        return ()
    doc = json.loads(COASTLINE.read_text())
    out = []
    for ring in doc.get("land", []):
        a = np.asarray(ring, dtype=float)
        if len(a) >= 3:
            out.append((a[:, 0].copy(), a[:, 1].copy()))
    return tuple(out)


def on_land(lon, lat) -> np.ndarray:
    """True where the point is ashore. Accepts scalars or arrays."""
    lon = np.atleast_1d(np.asarray(lon, dtype=float))
    lat = np.atleast_1d(np.asarray(lat, dtype=float))
    inside = np.zeros(np.broadcast(lon, lat).shape, dtype=bool)
    for x, y in _rings():
        xj, yj = np.roll(x, 1), np.roll(y, 1)
        # Even-odd rule: count crossings of a ray cast in +lon.
        for k in range(len(x)):
            dy = yj[k] - y[k]
            if dy == 0.0:
                continue
            straddles = (y[k] > lat) != (yj[k] > lat)
            xint = (xj[k] - x[k]) * (lat - y[k]) / dy + x[k]
            inside ^= straddles & (lon < xint)
    return inside


def at_sea(lon, lat) -> np.ndarray:
    return ~on_land(lon, lat)
