"""Cut real bathymetry down to the Cape Town -> Bharati corridor at 0.05 degrees.

Output grid: lat 78 S .. 30 S, lon 0 .. 90 E, exactly 0.05 degree boxes. That
covers the whole simulation box and the PolarRoute mesh. Two sources, split
at 50 S, which is where IBCSO stops:

South of 50 S - IBCSO v2, the WGS84 netCDF of the *ice-surface* grid:

    https://download.pangaea.de/dataset/937574/files/IBCSO_v2_ice-surface_WGS84.nc

    Dataset: Dorschel, B., Hehemann, L., Viquerat, S., et al. (2022). The
    International Bathymetric Chart of the Southern Ocean Version 2 (IBCSO v2).
    PANGAEA, https://doi.org/10.1594/PANGAEA.937574
    Paper: Dorschel, B., et al. (2022). Scientific Data 9, 275.
    https://doi.org/10.1038/s41597-022-01366-7
    Licence: CC-BY-4.0, as stated on the PANGAEA landing page.

North of 50 S - GEBCO_2020 at its full 15 arc-second resolution, subset
through NOAA CoastWatch ERDDAP (the 2026 grid has no subsetting service; the
global zip is several GB and would not fit this machine):

    https://coastwatch.pfeg.noaa.gov/erddap/griddap/GEBCO_2020

    GEBCO Compilation Group (2020). GEBCO 2020 Grid.
    https://doi.org/10.5285/a29c5465-b138-234d-e053-6c86abc040b9
    Licence: GEBCO grid terms of use - public domain, free to use and
    redistribute with acknowledgement; ERDDAP adds "free to use and
    redistribute, no warranty". Not to be used for navigation.

Why these choices:

* IBCSO's ice-surface grid, not its bed grid. Over open water the two are the
  same seafloor; under an ice shelf the bed grid gives the seafloor beneath
  the ice, which would read as hundreds of metres of "water" a ship cannot
  enter. The ice-surface grid gives the top of the shelf (positive elevation),
  so ice shelves block the router the same way land does.
* IBCSO's WGS84 grid (242.6 MB; AWI's own resampling of the 500 m polar-
  stereographic grid onto a 0.01065 degree lat/lon grid) rather than the
  native one (703.4 MB): the routers work in lat/lon, so no reprojection.
  The GeoTIFF is smaller (54.5 MB) but needs GDAL/rasterio, which this
  project does not depend on.
* Two aggregates per box. `elevation` is the SHALLOWEST source value in the
  box AND its eight neighbours, and it is what the routers test against the
  vessel's minimum depth: a mean over the ~20-150 source cells in a box hides
  exactly the shoal that matters. The one-box (~5 km) neighbourhood is there
  because PolarRoute's mesh assigns each box to one cell by its centre, so a
  dry box straddling a cell edge was invisible to the cell next door - the
  regenerated Bharati route ended on such an edge, 2.9 km from the station,
  in a box with land in it. With the buffer, a cell is open only if every box
  touching it is deep enough. It also serves as the coastline margin that
  IBCSO's singlebeam-dominated East Antarctic shelf calls for.
  `elevation_mean` is the plain block mean, unbuffered, kept for display.

Raw downloads go to data/bathymetry/raw/ (gitignored). GEBCO is fetched in
latitude bands and each band is discarded once aggregated. Only the subset
(a few MB) is committed.

Usage:
    python scripts/subset_bathymetry.py              # download if needed, then cut
    python scripts/subset_bathymetry.py --raw PATH   # use an existing IBCSO download
"""

from __future__ import annotations

import argparse
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
import xarray as xr
from scipy.ndimage import maximum_filter

REPO = Path(__file__).resolve().parents[1]
IBCSO_URL = "https://download.pangaea.de/dataset/937574/files/IBCSO_v2_ice-surface_WGS84.nc"
GEBCO_URL = "https://coastwatch.pfeg.noaa.gov/erddap/griddap/GEBCO_2020.nc"
RAW = REPO / "data" / "bathymetry" / "raw" / "IBCSO_v2_ice-surface_WGS84.nc"
OUT = REPO / "data" / "bathymetry" / "ibcso_v2_corridor_0p05.nc"

STEP = 0.05
LAT_EDGES = np.round(np.arange(-78.0, -30.0 + STEP / 2, STEP), 6)
LON_EDGES = np.round(np.arange(0.0, 90.0 + STEP / 2, STEP), 6)
SPLIT_LAT = -50.0          # IBCSO south of this, GEBCO north of it
GEBCO_BAND_DEG = 2.0       # ~21 MB per request at 15 arc-seconds

CITATION = (
    "South of 50S: Dorschel, B., Hehemann, L., Viquerat, S., et al. (2022). The "
    "International Bathymetric Chart of the Southern Ocean Version 2. Scientific "
    "Data 9, 275, https://doi.org/10.1038/s41597-022-01366-7; dataset PANGAEA, "
    "https://doi.org/10.1594/PANGAEA.937574 (CC-BY-4.0). North of 50S: GEBCO "
    "Compilation Group (2020) GEBCO 2020 Grid, "
    "https://doi.org/10.5285/a29c5465-b138-234d-e053-6c86abc040b9 (public domain)."
)


def download(url: str, dest: Path, attempts: int = 20, wait_s: float = 60.0) -> Path:
    """Fetch `url` to `dest`. PANGAEA keeps large files on tape and answers
    503 with an HTML "loading from tape" page until the file is staged, so a
    503 or an HTML body means wait and retry, not fail."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_suffix(dest.suffix + ".part")
    req = urllib.request.Request(url, headers={"User-Agent": "subset_bathymetry/1.0"})
    for k in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                if "html" in r.headers.get("Content-Type", ""):
                    raise urllib.error.HTTPError(url, 503, "html staging page", r.headers, None)
                with open(part, "wb") as f:
                    while chunk := r.read(1 << 20):
                        f.write(chunk)
            part.rename(dest)
            return dest
        except urllib.error.HTTPError as e:
            if e.code != 503:
                raise
            print(f"[{k}/{attempts}] {url} not ready (503); retrying in {wait_s:.0f} s",
                  file=sys.stderr)
            time.sleep(wait_s)
    raise RuntimeError(f"{url} was still not available after {attempts} attempts")


def block_reduce(z: np.ndarray, lat: np.ndarray, lon: np.ndarray,
                 lat_edges: np.ndarray, lon_edges: np.ndarray):
    """Max and mean of `z` over each box between consecutive edges.

    `lat`/`lon` are ascending source cell centres; a cell belongs to the box
    its centre falls in. Every box must hold at least one source cell, which
    holds for both sources here (source step < 0.05 degree)."""
    keep_j = (lat >= lat_edges[0]) & (lat < lat_edges[-1])
    keep_i = (lon >= lon_edges[0]) & (lon < lon_edges[-1])
    z, lat, lon = z[np.ix_(keep_j, keep_i)], lat[keep_j], lon[keep_i]
    if np.isnan(z).any():
        raise ValueError("source grid has gaps inside the corridor")
    r = np.searchsorted(lat, lat_edges[:-1])
    c = np.searchsorted(lon, lon_edges[:-1])
    if len(np.unique(r)) != len(r) or len(np.unique(c)) != len(c):
        raise ValueError("a target box holds no source cell")
    zmax = np.maximum.reduceat(np.maximum.reduceat(z, r, axis=0), c, axis=1)
    zsum = np.add.reduceat(np.add.reduceat(z.astype("float64"), r, axis=0), c, axis=1)
    n = (np.diff(np.append(r, len(lat)))[:, None]
         * np.diff(np.append(c, len(lon)))[None, :])
    return zmax.astype("float32"), (zsum / n).astype("float32")


def _grid(ds: xr.Dataset) -> xr.DataArray:
    """The one lat/lon data variable, sorted ascending."""
    ds = ds.rename({k: v for k, v in {"latitude": "lat", "longitude": "lon"}.items()
                    if k in ds.dims})
    names = [n for n, v in ds.data_vars.items() if set(v.dims) == {"lat", "lon"}]
    if len(names) != 1:
        raise ValueError(f"expected one lat/lon grid in the file, found {names}")
    return ds[names[0]].sortby("lat").sortby("lon")


def ibcso_part(raw: Path):
    edges = LAT_EDGES[LAT_EDGES <= SPLIT_LAT]
    with xr.open_dataset(raw) as ds:
        z = _grid(ds).sel(lat=slice(edges[0], edges[-1]),
                          lon=slice(LON_EDGES[0], LON_EDGES[-1])).load()
    step = float(np.diff(z.lat.values[:2])[0])
    zmax, zmean = block_reduce(z.values.astype("float32"), z.lat.values, z.lon.values,
                               edges, LON_EDGES)
    return zmax, zmean, step


def gebco_part(tmp_dir: Path):
    edges = LAT_EDGES[LAT_EDGES >= SPLIT_LAT]
    maxes, means = [], []
    bands = np.arange(edges[0], edges[-1], GEBCO_BAND_DEG)
    for lo in bands:
        hi = min(lo + GEBCO_BAND_DEG, edges[-1])
        q = (f"?elevation%5B({lo:.4f}):1:({hi:.4f})%5D"
             f"%5B({LON_EDGES[0]:.4f}):1:({LON_EDGES[-1]:.4f})%5D")
        f = download(GEBCO_URL + q, tmp_dir / f"gebco_{lo:.0f}.nc", attempts=5, wait_s=30)
        with xr.open_dataset(f) as ds:
            z = _grid(ds).load()
        f.unlink()
        band_edges = edges[(edges >= lo - 1e-9) & (edges <= hi + 1e-9)]
        zmax, zmean = block_reduce(z.values.astype("float32"), z.lat.values,
                                   z.lon.values, band_edges, LON_EDGES)
        maxes.append(zmax)
        means.append(zmean)
        print(f"GEBCO band {lo:.0f}..{hi:.0f}: done", file=sys.stderr)
    return np.concatenate(maxes), np.concatenate(means)


def build(raw: Path, out: Path) -> xr.Dataset:
    s_max, s_mean, ibcso_step = ibcso_part(raw)
    n_max, n_mean = gebco_part(raw.parent)
    # Shallowest within one box of each box: see the module docstring.
    zmax = maximum_filter(np.concatenate([s_max, n_max]), size=3, mode="nearest")
    zmean = np.concatenate([s_mean, n_mean])
    lat = np.round((LAT_EDGES[:-1] + LAT_EDGES[1:]) / 2, 6)
    lon = np.round((LON_EDGES[:-1] + LON_EDGES[1:]) / 2, 6)
    assert zmax.shape == (len(lat), len(lon)), zmax.shape

    enc = {"dtype": "int16", "zlib": True, "complevel": 9, "_FillValue": -32768}
    ds = xr.Dataset(
        {
            "elevation": (("lat", "lon"), np.round(zmax), dict(
                units="m", positive="up",
                long_name="shallowest source elevation within one box of this box",
                comment=("Maximum of the source cells in this box and its eight "
                         "neighbours (~5 km buffer). Negative is "
                         "water depth below sea level; zero or positive is land or "
                         "ice-shelf surface. This is the value routers test against "
                         "a vessel's minimum depth."))),
            "elevation_mean": (("lat", "lon"), np.round(zmean), dict(
                units="m", positive="up",
                long_name="mean source elevation in the box",
                comment="Block mean. For display only; hides shoals, never route on it.")),
        },
        coords={"lat": ("lat", lat, {"units": "degrees_north"}),
                "lon": ("lon", lon, {"units": "degrees_east"})},
        attrs={
            "title": "Corridor bathymetry, Cape Town-Bharati, 0.05 deg "
                     "(IBCSO v2 south of 50S, GEBCO_2020 north of 50S)",
            "source": f"south of 50S: {IBCSO_URL}; north of 50S: {GEBCO_URL}",
            "source_doi": ("https://doi.org/10.1594/PANGAEA.937574; "
                           "https://doi.org/10.5285/a29c5465-b138-234d-e053-6c86abc040b9"),
            "references": CITATION,
            "license": ("IBCSO v2 part: CC-BY-4.0 (https://creativecommons.org/licenses/by/4.0/); "
                        "GEBCO_2020 part: public domain, attribution requested"),
            "source_split_lat": SPLIT_LAT,
            "ibcso_source_step_deg": ibcso_step,
            "gebco_source_step_deg": 1.0 / 240.0,
            "grid_step_deg": STEP,
            "history": (f"{time.strftime('%Y-%m-%d')}: box max and mean onto "
                        f"lat {LAT_EDGES[0]}..{LAT_EDGES[-1]}, lon {LON_EDGES[0]}.."
                        f"{LON_EDGES[-1]} by scripts/subset_bathymetry.py"),
            "caveat": ("IBCSO and GEBCO are scientific compilations, not official "
                       "electronic navigational charts (ENC). Not for navigation."),
        },
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    ds.to_netcdf(out, encoding={"elevation": enc, "elevation_mean": enc})
    return ds


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", type=Path, default=RAW)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    raw = args.raw if args.raw.exists() else download(IBCSO_URL, args.raw)
    ds = build(raw, args.out)
    e = ds["elevation"].values
    print(f"wrote {args.out} ({args.out.stat().st_size / 1e6:.2f} MB), "
          f"grid {ds.sizes['lat']}x{ds.sizes['lon']} at {STEP} deg; "
          f"elevation {np.nanmin(e):.0f}..{np.nanmax(e):.0f} m; "
          f"{np.mean(e > -20) * 100:.1f}% of boxes shallower than 20 m or dry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
