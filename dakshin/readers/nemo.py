"""Native NEMO output reader (feature F2).

Reads the files a NEMO ocean–sea-ice run actually writes — `grid_T`, `grid_U`,
`grid_V` and the sea-ice model's output — and returns the same fields the rest
of this pipeline consumes, on NEMO's curvilinear `nav_lon`/`nav_lat`
coordinates. `dakshin.grid.GlorysToNsidcRegridder` accepts those 2-D
coordinate arrays directly, so a regional NEMO run (e.g. an ANHA
configuration) can drop into the ice-edge scoring of
`scripts/realforecast_hindcast.py` or feed currents to the berg forecast
after regridding — asking "what would a ship have done in this run?".

Variable names differ across NEMO versions and XIOS configurations, so each
field is looked up through an alias list covering the classic names
(`vozocrtx`, `vomecrty`, `votemper`, LIM's `ileadfra`/`soicecov`) and the
CMIP-style names newer SI3/XIOS setups write (`uo`, `vo`, `thetao`/`tos`,
`siconc`). An unknown layout fails loudly with the variables it did find.

STATUS: written against the NEMO 4.2 / SI3 documentation and the classic
OPA/LIM names; **not yet exercised on real NEMO output** — no small open
sample file ships with NEMO. The unit tests cover the alias resolution and
coordinate handling with synthetic files in the documented layout.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import xarray as xr

# field -> accepted variable names, first match wins
ALIASES = {
    "ice_concentration": ("siconc", "ileadfra", "soicecov", "sic"),
    "u_current": ("uo", "vozocrtx", "ssu", "sozocrtx"),
    "v_current": ("vo", "vomecrty", "ssv", "somecrty"),
    "sst": ("tos", "sosstsst", "thetao", "votemper"),
    "ice_thickness": ("sivolu", "sithic", "iicethic", "sithick"),
}
COORD_ALIASES = {"lon": ("nav_lon", "glamt", "longitude", "lon"),
                 "lat": ("nav_lat", "gphit", "latitude", "lat")}


def _find(ds: xr.Dataset, names: tuple[str, ...]) -> str | None:
    for n in names:
        if n in ds:
            return n
    return None


def _surface(da: xr.DataArray) -> np.ndarray:
    """First time step and, when a depth axis is present, the top level."""
    for dim in ("time_counter", "time", "t"):
        if dim in da.dims:
            da = da.isel({dim: 0})
            break
    for dim in ("deptht", "depthu", "depthv", "olevel", "z", "depth"):
        if dim in da.dims:
            da = da.isel({dim: 0})
            break
    return da.values.astype(np.float32)


class NemoReader:
    """One or more native NEMO output files, read as a unit.

    Pass whichever of the files exist; fields resolve from the first file
    that holds them (NEMO splits fields across grid_T/U/V and the ice file,
    but single-file setups work too).
    """

    def __init__(self, *paths: Path | str):
        if not paths:
            raise ValueError("give at least one NEMO output file")
        self._ds = [xr.open_dataset(p) for p in paths]
        self._paths = [str(p) for p in paths]

        lon = lat = None
        for ds in self._ds:
            lon_name = _find(ds, COORD_ALIASES["lon"])
            lat_name = _find(ds, COORD_ALIASES["lat"])
            if lon_name and lat_name:
                lon = ds[lon_name].values
                lat = ds[lat_name].values
                break
        if lon is None:
            raise ValueError(
                f"no nav_lon/nav_lat (or aliases) in {self._paths}")
        # 2-D curvilinear arrays (squeeze drops a stray time axis some
        # outputs attach); 1-D axes from a regular-grid subset are legal too.
        self.lon = np.squeeze(np.asarray(lon))
        self.lat = np.squeeze(np.asarray(lat))

    def field(self, name: str) -> np.ndarray:
        """One of ice_concentration, u_current, v_current, sst, ice_thickness
        as a 2-D surface array; NaN where the file uses its fill value."""
        if name not in ALIASES:
            raise KeyError(f"unknown field {name!r}; know {sorted(ALIASES)}")
        for ds in self._ds:
            var = _find(ds, ALIASES[name])
            if var:
                v = _surface(ds[var])
                # NEMO land points are 0.0 in masked fields or huge fill
                # values; treat only fills as NaN — zero ice is a real value.
                return np.where(np.abs(v) > 1e19, np.nan, v)
        found = [v for ds in self._ds for v in ds.data_vars]
        raise KeyError(
            f"none of {ALIASES[name]} found for {name!r}; files hold {found}")

    def available(self) -> dict[str, bool]:
        return {f: any(_find(ds, al) for ds in self._ds)
                for f, al in ALIASES.items()}

    def close(self) -> None:
        for ds in self._ds:
            ds.close()
