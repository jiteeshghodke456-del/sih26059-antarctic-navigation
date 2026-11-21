#!/usr/bin/env python3
"""Reduce a 3-hourly CMEMS wave subset to daily fields, in place.

    python scripts/reduce_wav_daily.py <file.nc>

Keeps, per day: VHM0 daily maximum (the planning-relevant number — the worst
sea the ship meets that day) and VMDR at the 3-hour step of that maximum (the
direction of the peak sea; a plain daily mean of a direction is circular
nonsense). Cuts the file ~8x before compression.
"""
import sys
from pathlib import Path

import numpy as np
import xarray as xr


def main() -> int:
    path = Path(sys.argv[1])
    ds = xr.open_dataset(path)
    days = ds.time.dt.floor("D")
    out_days, vhm0_max, vmdr_at_max = [], [], []
    for day, grp in ds.groupby(days):
        h = grp["VHM0"].values  # (steps, lat, lon)
        with np.errstate(invalid="ignore"):
            idx = np.nanargmax(np.where(np.isfinite(h), h, -np.inf), axis=0)
        mx = np.take_along_axis(h, idx[None], 0)[0]
        mdr = np.take_along_axis(grp["VMDR"].values, idx[None], 0)[0]
        all_nan = ~np.isfinite(h).any(axis=0)
        mx[all_nan] = np.nan
        mdr[all_nan] = np.nan
        out_days.append(day)
        vhm0_max.append(mx.astype(np.float32))
        vmdr_at_max.append(mdr.astype(np.float32))
    out = xr.Dataset(
        {
            "VHM0_dmax": (("time", "latitude", "longitude"), np.stack(vhm0_max),
                          {"long_name": "daily maximum significant wave height",
                           "units": "m"}),
            "VMDR_at_dmax": (("time", "latitude", "longitude"), np.stack(vmdr_at_max),
                             {"long_name": "wave direction at the daily maximum",
                              "units": "degree"}),
        },
        coords={"time": np.array(out_days), "latitude": ds.latitude,
                "longitude": ds.longitude},
        attrs=dict(ds.attrs, reduction="daily max of 3-hourly VHM0; VMDR at argmax"),
    )
    ds.close()
    enc = {v: {"zlib": True, "complevel": 4} for v in out.data_vars}
    tmp = path.with_suffix(".reduced.nc")
    out.to_netcdf(tmp, encoding=enc)
    tmp.replace(path)
    print(f"reduced {path.name}: {len(out_days)} days")
    return 0


if __name__ == "__main__":
    sys.exit(main())
