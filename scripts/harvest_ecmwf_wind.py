#!/usr/bin/env python3
"""Daily ECMWF open-data 10 m wind harvest (HANDOFF_TONIGHT slice 6).

    python scripts/harvest_ecmwf_wind.py [--out data/ecmwf_wind]

ECMWF open data keeps only the last ~12 runs (2–3 days), so this must run
daily; missed days are unrecoverable. Pulls the latest available 00z/12z IFS
run, 10u/10v at steps 0–240 h (6-hourly), crops to the corridor box
(0–80E, 55–78S) and writes a compressed netCDF per cycle.

Licence: ECMWF open data is CC BY 4.0. Required attribution, recorded in the
file attributes and ATTRIBUTION.md: "Contains modified ECMWF open data
(CC BY 4.0), https://www.ecmwf.int/en/forecasts/datasets/open-data".
Open-Meteo is fallback only — its free tier is non-commercial, which may not
cover a government deployment.
"""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

import numpy as np
import xarray as xr
from ecmwf.opendata import Client

BOX = {"lon": (0.0, 80.0), "lat": (-78.0, -55.0)}
STEPS = list(range(0, 241, 6))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("data/ecmwf_wind"))
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    client = Client(source="ecmwf")
    latest = client.latest(type="fc", param=["10u", "10v"], step=STEPS)
    cycle = f"{latest:%Y-%m-%d_%Hz}"
    dest = args.out / f"ecmwf_wind_{cycle}.nc"
    if dest.exists():
        print(f"already have {dest.name}")
        return 0

    with tempfile.NamedTemporaryFile(suffix=".grib2", delete=False) as tmp:
        client.retrieve(type="fc", param=["10u", "10v"], step=STEPS,
                        date=latest.strftime("%Y-%m-%d"), time=latest.hour,
                        target=tmp.name)
        ds = xr.open_dataset(tmp.name, engine="cfgrib",
                             backend_kwargs={"indexpath": ""})
        # IFS grid: latitude descending, longitude 0..360
        sub = ds.sel(latitude=slice(BOX["lat"][1], BOX["lat"][0]),
                     longitude=slice(BOX["lon"][0], BOX["lon"][1]))
        sub = sub[["u10", "v10"]].load()
        speed = np.hypot(sub["u10"].values, sub["v10"].values)
        assert np.isfinite(speed).all() and speed.max() < 80.0, \
            f"implausible wind speeds (max {speed.max():.1f} m/s)"
        sub.attrs["licence"] = ("Contains modified ECMWF open data (CC BY 4.0), "
                                "https://www.ecmwf.int/en/forecasts/datasets/open-data")
        sub.attrs["cycle"] = cycle
        enc = {v: {"zlib": True, "complevel": 4, "dtype": "float32"}
               for v in ("u10", "v10")}
        sub.to_netcdf(dest, encoding=enc)
    Path(tmp.name).unlink(missing_ok=True)
    print(f"wrote {dest} ({dest.stat().st_size/1e6:.1f} MB, "
          f"{len(sub.step)} steps, max wind {speed.max():.1f} m/s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
