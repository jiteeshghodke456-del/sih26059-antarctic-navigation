#!/usr/bin/env python3
"""One-off backfill of daily surface ANALYSIS currents for the corridor box.

    python scripts/backfill_cur_analysis.py [--start 2026-08-31] [--end 2026-11-20]
                                            [--out data/cmems_cur_analysis]

Writes one file per day, data/cmems_cur_analysis/cmems_cur_analysis_<date>.nc,
holding that day's daily-mean uo/vo (m s-1) at the top model level (0.494 m)
over the same box as scripts/harvest_cmems.sh (lon 0..80, lat -78..-55).

Source is the dataset the daily harvest uses for forecast currents,
cmems_mod_glo_phy-cur_anfc_0.083deg_P1D-m (GLOBAL_ANALYSISFORECAST_PHY_001_024).
For a date before the current bulletin it serves the best analysis, not the
forecast issued on that date; those forecasts are gone, which is why the daily
harvest exists. Days within roughly two weeks of the run date can still be
revised by CMEMS's later analysis runs. Delete those files and re-run to
refresh them. Existing files are skipped, so the script is safe to re-run.

Each file is checked straight after download (one time step on the requested
day, one depth level, units m s-1, finite speeds under 2 m/s for >= 99.9 % of
ocean cells) and compressed with scripts/compress_netcdf.py, which stores
uo/vo as lossless float32 deflate. Requires `copernicusmarine login` once.
"""
from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

import copernicusmarine
import numpy as np
import xarray as xr

from compress_netcdf import compress  # scripts/ is on sys.path when run as a script

DATASET_ID = "cmems_mod_glo_phy-cur_anfc_0.083deg_P1D-m"
BOX = dict(minimum_longitude=0, maximum_longitude=80,
           minimum_latitude=-78, maximum_latitude=-55)
SANE_SPEED = 2.0       # m/s; surface currents in this box are well below this
SANE_FRACTION = 0.999  # share of ocean cells that must be under SANE_SPEED


def check(path: Path, day: date) -> float:
    """Assert the file is one sane surface day; return its max speed in m/s."""
    with xr.open_dataset(path) as ds:
        days = ds.time.values.astype("datetime64[D]")
        assert list(days) == [np.datetime64(day)], f"{path.name}: time is {days}"
        assert ds.sizes["depth"] == 1 and float(ds.depth[0]) < 1, f"{path.name}: depth {ds.depth.values}"
        for v in ("uo", "vo"):
            assert ds[v].attrs.get("units") == "m s-1", f"{path.name}: {v} units {ds[v].attrs.get('units')}"
        speed = np.hypot(ds.uo.values, ds.vo.values)
    ocean = speed[np.isfinite(speed)]
    assert ocean.size > 0, f"{path.name}: no ocean cells"
    share = float(np.mean(ocean < SANE_SPEED))
    assert share >= SANE_FRACTION, f"{path.name}: only {share:.4%} of cells under {SANE_SPEED} m/s"
    return float(ocean.max())


def fetch_day(day: date, out_dir: Path) -> Path:
    dest = out_dir / f"cmems_cur_analysis_{day}.nc"
    if dest.exists():
        return dest
    stamp = f"{day}T00:00:00"
    copernicusmarine.subset(
        dataset_id=DATASET_ID, variables=["uo", "vo"],
        minimum_depth=0, maximum_depth=1,
        start_datetime=stamp, end_datetime=stamp, **BOX,
        output_directory=out_dir, output_filename=dest.name,
    )
    try:
        check(dest, day)
    except AssertionError:
        dest.unlink()  # a file that fails the check must not be skipped as "already have" next run
        raise
    compress(dest)
    return dest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--start", type=date.fromisoformat, default=date(2026, 8, 31))
    ap.add_argument("--end", type=date.fromisoformat, default=date(2026, 11, 20))
    ap.add_argument("--out", type=Path, default=Path("data/cmems_cur_analysis"))
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    failed, peak = [], (0.0, None)
    day = args.start
    while day <= args.end:
        try:
            path = fetch_day(day, args.out)
            vmax = check(path, day)  # re-checked after compression too
            peak = max(peak, (vmax, day), key=lambda p: p[0])
            print(f"ok   {path.name}  {path.stat().st_size / 1e6:.2f} MB  max |v| {vmax:.2f} m/s")
        except Exception as e:  # noqa: BLE001 - record the day and carry on; summary exits non-zero
            failed.append(day)
            print(f"FAIL {day}: {e}")
        day += timedelta(days=1)

    files = sorted(args.out.glob("cmems_cur_analysis_*.nc"))
    total = sum(f.stat().st_size for f in files) / 1e6
    print(f"{len(files)} files, {total:.1f} MB; max |v| {peak[0]:.2f} m/s on {peak[1]}; "
          f"{len(failed)} failed{': ' + ', '.join(map(str, failed)) if failed else ''}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
