"""NSIDC polar-stereographic grid geometry, and regridding GLORYS12 onto it.

Design decision (ML_ARCHITECTURE.md §4.2): the **truth field is never
resampled**. GLORYS12 is regridded onto the NSIDC grid, not the other way
round — resampling the field you score against would create ice-edge artifacts
indistinguishable from real model error, and IIEE is measured on that field.

GLORYS12 (~0.083°, ~9 km) is finer than NSIDC (25 km), so the correct
operation is **area-averaging** many GLORYS12 cells into each NSIDC cell, not
bilinear sampling. Bilinear would throw away most source cells and fail to
preserve ice area. Here that is done with a precomputed cell-index map plus a
bincount, so the expensive geometry runs once rather than per day.

CRS verified from a real NSIDC file (2026-08-31):
    EPSG:3412, Hughes 1980 ellipsoid, +proj=stere +lat_0=-90 +lat_ts=-70
Verified correct by transforming the grid origin, which returns lat = -90.0.
"""

from __future__ import annotations

import numpy as np
import xarray as xr
from pyproj import Transformer

NSIDC_CRS = "EPSG:3412"
LATLON_CRS = "EPSG:4326"


def nsidc_lonlat(ds: xr.Dataset) -> tuple[np.ndarray, np.ndarray]:
    """Return (lon, lat) arrays for every cell of an NSIDC grid, shape (y, x)."""
    transformer = Transformer.from_crs(NSIDC_CRS, LATLON_CRS, always_xy=True)
    x_grid, y_grid = np.meshgrid(ds.x.values, ds.y.values)
    lon, lat = transformer.transform(x_grid, y_grid)
    return lon, lat


class GlorysToNsidcRegridder:
    """Area-average GLORYS12 lat/lon fields onto the NSIDC polar grid.

    The mapping from source cells to target cells depends only on the two
    grids, so it is computed once at construction and reused for every day.
    """

    def __init__(
        self,
        nsidc_ds: xr.Dataset,
        source_lat: np.ndarray,
        source_lon: np.ndarray,
    ):
        self.ny = nsidc_ds.sizes["y"]
        self.nx = nsidc_ds.sizes["x"]
        self.n_cells = self.ny * self.nx

        # NSIDC grid is a regular 25 km grid in projected space, so a source
        # point's target cell is a direct arithmetic index — no search needed.
        x = nsidc_ds.x.values
        y = nsidc_ds.y.values
        self._x0 = float(x[0])
        self._y0 = float(y[0])
        self._dx = float(x[1] - x[0])
        self._dy = float(y[1] - y[0])

        src_lon_grid, src_lat_grid = np.meshgrid(source_lon, source_lat)
        transformer = Transformer.from_crs(LATLON_CRS, NSIDC_CRS, always_xy=True)
        src_x, src_y = transformer.transform(src_lon_grid, src_lat_grid)

        col = np.rint((src_x - self._x0) / self._dx).astype(np.int64)
        row = np.rint((src_y - self._y0) / self._dy).astype(np.int64)

        inside = (row >= 0) & (row < self.ny) & (col >= 0) & (col < self.nx)
        self._src_valid = inside.ravel()
        self._flat_index = (row * self.nx + col).ravel()[self._src_valid]

        # Cells with no source point at all must stay NaN rather than silently
        # reading as zero ice — an empty cell is unknown, not ice-free.
        self._counts_geometry = np.bincount(self._flat_index, minlength=self.n_cells)

    def __call__(self, source_values: np.ndarray) -> np.ndarray:
        """Regrid one (lat, lon) field to (y, x) on the NSIDC grid."""
        flat = source_values.ravel()[self._src_valid]
        finite = np.isfinite(flat)

        idx = self._flat_index[finite]
        vals = flat[finite]

        sums = np.bincount(idx, weights=vals, minlength=self.n_cells)
        counts = np.bincount(idx, minlength=self.n_cells)

        out = np.full(self.n_cells, np.nan, dtype=np.float32)
        has_data = counts > 0
        out[has_data] = (sums[has_data] / counts[has_data]).astype(np.float32)
        return out.reshape(self.ny, self.nx)

    def coverage(self) -> float:
        """Fraction of NSIDC cells any source point maps into. Sanity check:
        if this is low, the source subset does not cover the target grid."""
        return float((self._counts_geometry > 0).mean())
