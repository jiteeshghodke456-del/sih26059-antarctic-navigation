"""Cut IBCSO v2 down to the Cape Town -> Bharati corridor at 0.05 degrees.

Source: the International Bathymetric Chart of the Southern Ocean, version 2,
the WGS84 (geographic) netCDF of the *ice-surface* grid:

    https://download.pangaea.de/dataset/937574/files/IBCSO_v2_ice-surface_WGS84.nc

Citation (dataset):
    Dorschel, B., Hehemann, L., Viquerat, S., et al. (2022). The International
    Bathymetric Chart of the Southern Ocean Version 2 (IBCSO v2) [dataset].
    PANGAEA, https://doi.org/10.1594/PANGAEA.937574
Citation (paper):
    Dorschel, B., et al. (2022). The International Bathymetric Chart of the
    Southern Ocean Version 2. Scientific Data 9, 275.
    https://doi.org/10.1038/s41597-022-01366-7
Licence: Creative Commons Attribution 4.0 International (CC-BY-4.0), as stated
on the PANGAEA landing page. Attribution travels inside the output file.

Why these choices:

* The ice-surface grid, not the bed grid. Over open water the two are the same
  seafloor; under an ice shelf the bed grid gives the seafloor beneath the ice,
  which would read as hundreds of metres of "water" a ship cannot enter. The
  ice-surface grid gives the top of the shelf instead (positive elevation), so
  ice shelves block the router the same way land does.
* The WGS84 grid (242.6 MB; AWI's own resampling of the 500 m polar-
  stereographic grid onto a 0.01065 degree lat/lon grid) rather than the
  native one (703.4 MB): the routers work in lat/lon, and it avoids a
  reprojection. 5x5 blocks of it give a 0.0532 degree output grid.
  The GeoTIFF is smaller still (54.5 MB) but needs GDAL/rasterio, which this
  project does not depend on; netCDF4 and xarray are already here.
* Two aggregates per 0.05 degree box. `elevation` is the SHALLOWEST source
  value in the box, and it is what the routers test against the vessel's
  minimum depth: a mean over 25 source cells hides exactly the shoal that
  matters. `elevation_mean` is the plain block mean, kept for display.

The raw download is ~240 MB and lives in data/bathymetry/raw/, which is
gitignored. Only the corridor subset (a few MB) is committed.

Usage:
    python scripts/subset_bathymetry.py            # download if needed, then cut
    python scripts/subset_bathymetry.py --raw PATH # use an existing download
"""

from __future__ import annotations

import argparse
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
import xarray as xr

REPO = Path(__file__).resolve().parents[1]
URL = "https://download.pangaea.de/dataset/937574/files/IBCSO_v2_ice-surface_WGS84.nc"
RAW = REPO / "data" / "bathymetry" / "raw" / "IBCSO_v2_ice-surface_WGS84.nc"
OUT = REPO / "data" / "bathymetry" / "ibcso_v2_corridor_0p05.nc"

LON = (0.0, 80.0)
LAT = (-78.0, -55.0)
TARGET_STEP_DEG = 0.05

CITATION = (
    "Dorschel, B., Hehemann, L., Viquerat, S., et al. (2022). The International "
    "Bathymetric Chart of the Southern Ocean Version 2. Scientific Data 9, 275, "
    "https://doi.org/10.1038/s41597-022-01366-7. Dataset: PANGAEA, "
    "https://doi.org/10.1594/PANGAEA.937574"
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
            print(f"[{k}/{attempts}] PANGAEA is staging the file from tape; "
                  f"retrying in {wait_s:.0f} s", file=sys.stderr)
            time.sleep(wait_s)
    raise RuntimeError(f"{url} was still not staged after {attempts} attempts")


def _elevation_var(ds: xr.Dataset) -> xr.DataArray:
    """The one 2-D data variable, with coordinates named lat/lon."""
    ds = ds.rename({k: v for k, v in {"x": "lon", "y": "lat"}.items() if k in ds.dims})
    names = [n for n, v in ds.data_vars.items() if set(v.dims) == {"lat", "lon"}]
    if len(names) != 1:
        raise ValueError(f"expected one lat/lon grid in the file, found {names}")
    return ds[names[0]]


def subset(raw: Path, out: Path) -> xr.Dataset:
    with xr.open_dataset(raw) as ds:
        z = _elevation_var(ds)
        z = z.sortby("lat").sortby("lon")
        z = z.sel(lon=slice(*LON), lat=slice(*LAT)).astype("float32").load()

    step = float(np.abs(np.diff(z.lon.values[:2]))[0])
    f = max(1, round(TARGET_STEP_DEG / step))
    blocks = z.coarsen(lat=f, lon=f, boundary="trim")
    shallowest = blocks.max()
    mean = blocks.mean()

    enc = {"dtype": "int16", "zlib": True, "complevel": 9, "_FillValue": -32768}
    out_ds = xr.Dataset(
        {
            "elevation": shallowest.round().astype("float32").assign_attrs(
                units="m", positive="up",
                long_name="shallowest IBCSO v2 ice-surface elevation in the box",
                comment=("Maximum of the source cells in each box. Negative is "
                         "water depth below sea level; zero or positive is land or "
                         "ice-shelf surface. This is the value routers test against "
                         "a vessel's minimum depth.")),
            "elevation_mean": mean.round().astype("float32").assign_attrs(
                units="m", positive="up",
                long_name="mean IBCSO v2 ice-surface elevation in the box",
                comment="Block mean. For display only; hides shoals, never route on it."),
        },
        attrs={
            "title": "IBCSO v2 ice-surface elevation, Cape Town-Bharati corridor, ~0.05 deg",
            "source": URL,
            "source_doi": "https://doi.org/10.1594/PANGAEA.937574",
            "references": CITATION,
            "license": "CC-BY-4.0 (https://creativecommons.org/licenses/by/4.0/)",
            "source_grid_step_deg": step,
            "block_factor": f,
            "grid_step_deg": step * f,
            "history": (f"{time.strftime('%Y-%m-%d')}: cut to lon {LON}, lat {LAT}, "
                        f"{f}x{f} block max and mean by scripts/subset_bathymetry.py"),
            "caveat": ("IBCSO is a scientific compilation, not an official electronic "
                       "navigational chart (ENC). Not for navigation."),
        },
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out_ds.to_netcdf(out, encoding={"elevation": enc, "elevation_mean": enc})
    return out_ds


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", type=Path, default=RAW)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    raw = args.raw if args.raw.exists() else download(URL, args.raw)
    ds = subset(raw, args.out)
    e = ds["elevation"].values
    print(f"wrote {args.out} ({args.out.stat().st_size / 1e6:.2f} MB), "
          f"grid {ds.sizes['lat']}x{ds.sizes['lon']} at {ds.attrs['grid_step_deg']:.4f} deg; "
          f"elevation {np.nanmin(e):.0f}..{np.nanmax(e):.0f} m; "
          f"{np.mean(e > -20) * 100:.1f}% of boxes shallower than 20 m or dry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
