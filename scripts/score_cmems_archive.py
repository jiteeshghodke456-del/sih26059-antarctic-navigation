#!/usr/bin/env python3
"""Score the archived CMEMS sea-ice forecasts against persistence, by lead day.

    python scripts/score_cmems_archive.py [data/cmems_forecast_archive]

For each cycle D and lead k, the forecast is day k of cycle D and persistence
is day 0 of cycle D. Both are scored against day 0 of cycle D+k.

Know this before quoting the numbers: the "truth" is the model's own later
day-0 field, not a satellite observation, so the result flatters CMEMS. It is
the baseline a bias-correction model must beat, not a claim about real skill.

Stale cycles (see data/cmems_forecast_archive/KNOWN_STALE.md) are skipped by
the same rule the harvest uses: a real cycle has exactly 10 daily steps.
"""

import datetime as dt
import glob
import os
import sys

import numpy as np
import xarray as xr

archive = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(__file__), "..", "data", "cmems_forecast_archive")

cycles = {}
for path in sorted(glob.glob(os.path.join(archive, "cmems_siconc_*.nc"))):
    day = dt.date.fromisoformat(os.path.basename(path)[13:23])
    with xr.open_dataset(path) as ds:
        if ds.sizes["time"] != 10:
            continue
        # every lead below relies on step k being cycle day + k
        steps = ds.time.values.astype("datetime64[D]")
        assert (steps == np.datetime64(day) + np.arange(10)).all(), path
        cycles[day] = ds["siconc"].values.astype("float32")

print(f"clean cycles: {len(cycles)}  ({min(cycles)} to {max(cycles)})")
print("RMSE in sea-ice concentration %, over cells with ice in any of the three fields")
print("lead  pairs  cmems  persistence  cmems better by")
for k in range(1, 10):
    f_err, p_err = [], []
    for day, fields in cycles.items():
        later = cycles.get(day + dt.timedelta(days=k))
        if later is None:
            continue
        truth, forecast, persistence = later[0], fields[k], fields[0]
        ice = np.isfinite(truth) & np.isfinite(forecast) & (
            (truth > 0.01) | (forecast > 0.01) | (persistence > 0.01))
        f_err.append(np.mean((forecast[ice] - truth[ice]) ** 2))
        p_err.append(np.mean((persistence[ice] - truth[ice]) ** 2))
    f, p = 100 * np.sqrt(np.mean(f_err)), 100 * np.sqrt(np.mean(p_err))
    print(f"{k:>4} {len(f_err):>6} {f:>6.2f} {p:>12.2f} {100 * (1 - f / p):>12.1f}%")
