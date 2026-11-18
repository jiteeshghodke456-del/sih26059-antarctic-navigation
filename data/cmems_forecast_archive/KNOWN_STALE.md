# Known stale cycles in this archive

Found on 2026-11-18 by comparing every archived cycle with the one before it.

Four files do not hold the forecast issued on the date in their name. Each is
a copy of the **previous day's** forecast with its first day cut off: 9 daily
steps instead of 10, and sea-ice concentration identical to the previous
cycle on all 9 shared dates (maximum difference 0.0000).

| File | Run started (UTC) | What it really holds |
|---|---|---|
| `cmems_siconc_2026-09-20.nc` | 2026-09-20 16:14 | the 2026-09-19 forecast, days 2 to 10 |
| `cmems_siconc_2026-10-11.nc` | 2026-10-11 17:42 | the 2026-10-10 forecast, days 2 to 10 |
| `cmems_siconc_2026-11-10.nc` | 2026-11-10 00:44 | the 2026-11-09 forecast, days 2 to 10 |
| `cmems_siconc_2026-11-17.nc` | 2026-11-17 00:51 | the 2026-11-16 forecast, days 2 to 10 |

## Why it happened

- **11-10 and 11-17.** The Monday 17:23 UTC scheduled run started more than
  seven hours late, after midnight UTC. The script named the file from the
  clock (Tuesday) while the server still held Monday's forecast. The two real
  Tuesday runs then found the file and skipped.
- **09-20 and 10-11.** The run started after 12:00 UTC, but Copernicus had not
  published that day's forecast yet. Both days are Sundays.

The real forecasts for these four dates were never saved. CMEMS overwrites
each forecast with the next, so they cannot be recovered.

## What to do with them

- Do not use these four cycles when scoring forecasts by lead time. Their
  "day 0" is really a one-day-old forecast, not that day's analysis.
- The honest count is 75 clean cycles and 4 stale ones out of 79
  (2026-08-31 to 2026-11-17).

`scripts/harvest_cmems.sh` now rejects a download whose length is not exactly
10 daily steps, and files a run that starts before 12:00 UTC under the
previous day's cycle, so this should not happen again.
