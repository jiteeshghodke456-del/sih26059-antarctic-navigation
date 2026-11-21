"""Real seabed depth for the routers: IBCSO v2, cut to the corridor.

The vessel config has carried `min_depth: 20` since the start, and nothing
ever read it, because there was no bathymetry anywhere a router could see.
This is that bathymetry: the committed 0.05 degree subset written by
scripts/subset_bathymetry.py from IBCSO v2 (Dorschel et al. 2022, Scientific
Data 9, 275; CC-BY-4.0).

Each box holds the SHALLOWEST source value inside it, so a lookup errs toward
"too shallow", never toward "deep enough". Coverage is lon 0..80 E,
lat 78..55 S; outside that the answer is NaN (no data), which callers must
treat as unknown rather than as deep water.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np

SUBSET = (Path(__file__).resolve().parents[2]
          / "data" / "bathymetry" / "ibcso_v2_corridor_0p05.nc")


@lru_cache(maxsize=1)
def _grid() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    # A missing file must be loud: a depth check that silently passes
    # everything is the inert constraint this module exists to remove.
    import xarray as xr
    with xr.open_dataset(SUBSET) as ds:
        return (ds["lat"].values.astype(float), ds["lon"].values.astype(float),
                ds["elevation"].values.astype(float))


def depth_m(lon, lat) -> np.ndarray:
    """Shallowest water depth (m, positive down) in the box holding each point.

    Negative or zero means land or ice shelf. NaN means outside the subset.
    Accepts scalars or arrays, like geo_mask.on_land.
    """
    lats, lons, elev = _grid()
    lon = np.atleast_1d(np.asarray(lon, dtype=float))
    lat = np.atleast_1d(np.asarray(lat, dtype=float))
    half = 0.5 * abs(lats[1] - lats[0])
    j = np.clip(np.searchsorted(lats, lat - half), 0, len(lats) - 1)
    i = np.clip(np.searchsorted(lons, lon - half), 0, len(lons) - 1)
    out = -elev[j, i]
    inside = ((lat >= lats[0] - half) & (lat <= lats[-1] + half)
              & (lon >= lons[0] - half) & (lon <= lons[-1] + half))
    return np.where(inside, out, np.nan)


def too_shallow(lon, lat, min_depth_m: float) -> np.ndarray:
    """True where the water is known to be shallower than `min_depth_m`.
    No data is not shallow: it is unknown, and the chart gate says so."""
    d = depth_m(lon, lat)
    return np.where(np.isnan(d), False, d < min_depth_m)
