# Dakshin: operations runbook

For the question "if I am asked to perform an action on the data, what exactly
do I run?" Every command is run from the repository root unless it says
otherwise. Every path is relative to that root.

Read this first. Several operations overwrite tracked files:

- `scripts/realforecast_hindcast.py` overwrites `dakshin/figures/realforecast_hindcast.json`,
  the committed result that the project has scored once.
- `scripts/resolution_study.py`, `berg_hindcast.py`, `berg_resolution.py`,
  `berg_melt.py` and `real_route_run.py` overwrite their JSON outputs in the same folder.
- The CMEMS, NSIDC, ECMWF and USNIC scripts write into `data/`.

Re-running a script changes the numbers if the inputs have changed (new cycles
arrive every day). Record the date of any re-run next to the number you quote.
The scorers say "scored once, reported as it comes out" (`scripts/realforecast_hindcast.py`
docstring). A re-run is a new score, not a second look at the same one.

Items marked **not run** were read from the code but not executed in this pass.
Times marked **not recorded** have no measurement in the repository.

---

**Snapshot.** Repository read between about 17:56 and 18:21 UTC on 2026-11-21. "In this pass" means the study pass that wrote this file.

## 1. Environment

There is no root `pyproject.toml` or lockfile. The only requirements file is
`dakshin/demo/requirements.txt` (for the demo). The three analysis environments
below live outside the repository, in `/home/agent/.venvs/`. Versions were read
from the installed packages in this pass.

| Venv | Python | Key packages (installed versions) | Used by |
|---|---|---|---|
| `/home/agent/.venvs/sih-work` | 3.12.12 | numpy 2.5.5, xarray 2026.9.0, netCDF4 1.7.5.1.post1, scipy 1.18.1, pyproj 3.8.0, torch 2.15.0+cpu, copernicusmarine 2.5.1, pytest 9.2.0, pyais 3.3.1, ecmwf-opendata (importable), matplotlib 3.11.2, fastapi 0.165.0, uvicorn 0.54.0, pydantic 2.14.4 | Everything except PolarRoute. Default for `pull_checkpoints.sh`. |
| `/home/agent/.venvs/prenv` | 3.11.14 | polar-route 1.1.11, meshiphi 2.3.1, netCDF4 1.7.4, numpy 2.4.6, xarray 2026.7.0, scipy 1.17.1, pyproj 3.7.2, pytest 9.1.1 | PolarRoute and meshiphi. No copernicusmarine, no ecmwf-opendata. |
| `/home/agent/.venvs/isih-demo` | 3.14.4 (when inspected at about 18:08) | numpy 2.5.2, xarray 2026.7.0, scipy 1.18.1, fastapi 0.141.1, uvicorn 0.52.4, pytest 9.1.1 | **Absent at 18:27 in this pass.** The directory was removed between inspections; this pass did not remove it and the cause is not identified. The repository's documented demo venv is Python 3.12 (see §2.14). |

Command-line tools outside the venvs:

- `kaggle` CLI: `/home/agent/.local/bin/kaggle`. It is not installed in `sih-work`.
- `copernicusmarine`: the CLI from `sih-work`. Authenticate once with `copernicusmarine login`
  (the cached credential is what the scripts use). The GitHub workflow uses the environment variables
  `COPERNICUSMARINE_SERVICE_USERNAME` and `COPERNICUSMARINE_SERVICE_PASSWORD` from repository secrets
  (`.github/workflows/cmems-harvest.yml`).
- `uv`: the demo instructions use it (`docs/PROTOTYPE_README.md`). Its presence was not checked here.

Credentials used by the scripts (values never stored in the repository):

| Service | How it is supplied | Used by |
|---|---|---|
| Copernicus Marine | cached `copernicusmarine login`, or the two environment variables above | `harvest_cmems.sh`, `backfill_cur_analysis.py` |
| Kaggle | `KAGGLE_API_TOKEN` environment variable, or `~/.kaggle` | `pull_checkpoints.sh`, notebook push |
| NSIDC NRT, NSIDC CDR, ECMWF open data, USNIC, IBCSO (PANGAEA) | none (public) | `download_nsidc_nrt.py`, `download_nsidc.py`, `harvest_ecmwf_wind.py`, `harvest_usnic.sh`, `subset_bathymetry.py` |

Path-dependent scripts. Several scripts import bare module names
(`from features import ...`, `from ice_quality import ...`) and rely on
`sys.path.insert` lines to find `dakshin/` and `models/iceberg/`. Run them as
`python3 scripts/<name>.py` from the root. Do not import them from another directory.

Two sandbox-specific paths: `scripts/pull_checkpoints.sh` defaults `PY` to
`/home/agent/.venvs/sih-work/bin/python`, and `dakshin/data` is a real directory in
this checkout (not a symlink). Set `PY=` to your own interpreter.

---

## 2. Operations

Each operation gives its purpose, the command, what it produces, how long it takes,
and what can go wrong.

### 2.1 Daily CMEMS forecast harvest (ice, currents, waves)

**Purpose.** Archive today's CMEMS sea-ice forecast cycle, and the matching
currents and waves, before CMEMS overwrites it. The archive is the only source
of forecasts as they were issued; see §3.

**Command (scheduled):** the GitHub workflow `.github/workflows/cmems-harvest.yml`
runs at 12:23, 17:23 and 21:23 UTC, with a manual trigger (`workflow_dispatch`) that
takes an optional `cycle_date`.

**Command (local):**

```
bash scripts/harvest_cmems.sh
```

With `CYCLE_DATE` unset, the cycle date comes from the clock: before 12:00 UTC
the cycle is yesterday's date, after that it is today's. Setting `CYCLE_DATE=YYYY-MM-DD`
is a deliberate back-fill. A back-filled date is the analysis for that day, not the
forecast that was issued, and the length check is skipped.

**Environment variables (all optional):**

| Variable | Default | Effect |
|---|---|---|
| `ARCHIVE_DIR` | `data/cmems_forecast_archive` | Where files are written |
| `LOG_FILE` | `data/cmems_harvest.log` | Appended to, and echoed to stdout |
| `MIN_LON`, `MAX_LON` | `0`, `80` | Corridor longitude box |
| `MIN_LAT`, `MAX_LAT` | `-78`, `-55` | Corridor latitude box |
| `CYCLE_DATE` | blank (clock) | Cycle date to fetch |
| `EXPECTED_DAYS` | `10` | Daily steps a real cycle must have (date plus nine days) |
| `GITHUB_OUTPUT` | unset locally | If set, the script writes `cycle=` and `status=` for the workflow |

**Outputs.** In `data/cmems_forecast_archive/`:

- `cmems_siconc_<cycle>.nc`: dataset `cmems_mod_glo_phy_anfc_0.083deg_P1D-m`, variables
  `siconc`, `sithick`, `usi`, `vsi`, 10 daily steps. Compressed to about 5 MB from 42.6 MB.
- `cmems_cur_<cycle>.nc`: `uo`, `vo` (m/s) for the top model level (0 to 1 m), 10 daily steps.
- `cmems_wav_<cycle>.nc`: `VHM0` and `VMDR` (3-hourly) reduced by
  `scripts/reduce_wav_daily.py` to a daily maximum, `VHM0_dmax`, with the wave
  direction at the peak (commit `e0ee2b2`). `VHM0_dmax` is the variable downstream code reads.
- Lines appended to `data/cmems_harvest.log`.

The script ends with a status line in `GITHUB_OUTPUT`:

| Status | Meaning | Exit code |
|---|---|---|
| `saved` | ice cycle downloaded and length-checked | 0 |
| `already_have` | the cycle file already exists; currents and waves are still tried | 0 |
| `not_published` | the server still held the previous day's forecast (step count wrong); nothing saved | 0 |

Any other failure (login, network) exits non-zero. Currents and waves never fail the
run: they log a warning and the ice cycle is kept.

**Time.** Not recorded. The workflow job has a 25-minute timeout
(`timeout-minutes: 25`).

**What can go wrong.**

- A run before 12:00 UTC files the previous day's forecast under today's name. The
  clock rule and the step-count check (`EXPECTED_DAYS`) are the guards. Four archived
  files got through before those guards existed; see `data/cmems_forecast_archive/KNOWN_STALE.md`.
- The guard is clock-based, not data-based. The backlog's critical item is to derive
  the date from the dataset's time axis (`docs/backlog.md`, `[critical][data]`). Not built.
- A missed bulletin cannot be recovered. CMEMS overwrites each cycle with the next.
- Login: the workflow retries three times, 30 seconds apart. Locally, a stale credential
  fails with a login error.
- The SST file that `scripts/berg_melt.py` reads (`cmems_sst_<cycle>.nc`) is not produced by
  this script. See §2.9 and §3.
- The workflow commits the archive and pushes to `main` as `cmems-harvest-bot`, with three
  rebase-and-retry attempts. A local run does not push; the files stay in the working tree.

### 2.2 The workflow itself

**Purpose.** Run §2.1 at fixed times on GitHub's infrastructure, so it does not depend on
a laptop being on.

**Command.** Triggered by the schedule in `.github/workflows/cmems-harvest.yml`. Manually,
from the GitHub Actions page (the `workflow_dispatch` input `cycle_date`), or with
`gh workflow run cmems-harvest.yml -f cycle_date=YYYY-MM-DD` if `gh` is authenticated (standard `gh` syntax; not run).

**Behaviour recorded in the workflow's comments.**

- Cron slots are never on the hour, and never before 12:00 UTC.
- The second and third slots are cheap: `harvest_cmems.sh` exits early when the cycle is on disk.
- A "verify" step fails the run if the ice file is under 1 MB (a truncated download).
- Scheduled runs were four to five hours late on three consecutive days in the first week.

**Gap.** `.github/workflows/` contains only this one workflow. There is no scheduled job in the
repository for the ECMWF wind (which keeps only 2 to 3 days of data) or the USNIC weekly list (§2.4,
§2.5). Both must be run by hand, or by a schedule outside the repository.

### 2.3 NSIDC near-real-time sea-ice truth

**Purpose.** Download the observed sea-ice concentration that the real-forecast hindcast scores
against. NSIDC keeps this stream for about three months.

**Command.**

```
python3 scripts/download_nsidc_nrt.py --start 2026-08-24 --end 2026-11-21 --out data/nsidc_nrt
```

Defaults: `--start 2026-08-24`, `--end` today, `--out data/nsidc_nrt`.

**Outputs.** `data/nsidc_nrt/sic_pss25_<YYYYMMDD>_am2_icdr_v04r00.nc` (NOAA/NSIDC G10016 v4,
south, daily), plus `MANIFEST.sha256` listing every file fetched and the count of failures.
At the time of writing the folder holds 89 files from 2026-08-24 to 2026-11-20, 35 MB.

**Behaviour.** The script skips a file whose destination exists and is non-empty (line 29), so
re-running is cheap. It records each file's SHA-256 in the manifest.

**Time.** Not recorded. The downloads are about 0.4 MB each.

**What can go wrong.**

- The NRT stream is kept for about three months (`git show 5f32ae3` commit message). Days older
  than that are gone from NSIDC. The earliest local file, 2026-08-24, reaches three months old
  on or about 2026-11-24. Files the repository does not already hold cannot be fetched after that.
- The folder is gitignored (`.gitignore`, `data/nsidc_nrt/`), so the only copy is local.
- The script prints the number of failed fetches and exits; the caller must check that count.

### 2.4 ECMWF 10 m wind forecast

**Purpose.** Daily wind forecast for the weather gate and the iceberg wind term (slice 6).

**Command.**

```
python3 scripts/harvest_ecmwf_wind.py --out data/ecmwf_wind
```

**Outputs.** `data/ecmwf_wind/ecmwf_wind_<YYYY-MM-DD>_<HH>z.nc`: 10u and 10v at steps 0 to 240 h
(6-hourly), cropped to 0 to 80 E, 55 to 78 S, from the latest 00z or 12z IFS run. One file exists
(2026-11-21, 00z). The script header says the required attribution, "Contains modified ECMWF open
data (CC BY 4.0), https://www.ecmwf.int/en/forecasts/datasets/open-data", is written into the file attributes.

**Time.** Not recorded.

**What can go wrong.** ECMWF open data keeps only the last 12 runs, two to three days. A missed day
is unrecoverable. There is no schedule for this script in the repository (§2.2). The script
requires `ecmwf-opendata`, which is installed in `sih-work` only. Open-Meteo is the documented fallback,
but its free tier is non-commercial, so it is not used in outputs (`ATTRIBUTION.md`).

**Current wiring.** The real-route run reads the wind through `dakshin/real_world.py`
(`WIND_DIR = data/ecmwf_wind`, file `ecmwf_wind_<cycle>_00z.nc`, used if present). The iceberg code does
not: `scripts/berg_hindcast.py` and `dakshin/berg_forecast.py` use zero wind.

### 2.5 USNIC weekly Antarctic iceberg list

**Purpose.** The weekly list of giant-iceberg positions, used for validation and for the
iceberg forecast's starting positions.

**Command.**

```
bash scripts/harvest_usnic.sh
```

**Outputs.** `data/icebergs/archive/AntarcticIcebergs_<YYYYMMDD>.csv`, named by the newest
"Last Update" date in the file. Idempotent: re-running on the same issue overwrites the identical file.
The archive holds 14 weekly issues, from `AntarcticIcebergs_20260820.csv` to `AntarcticIcebergs_20261120.csv`.

**Time.** Not recorded (one HTTP GET).

**What can go wrong.** The script fails with "unexpected USNIC payload" if the response does not start
with the expected header. Only the current issue is served by USNIC, so older issues came from the
USNIC archive (commit `fd4eba6`). Whether USNIC keeps those archive files was not verified here.
No schedule is set in the repository (§2.2).

### 2.6 Real-forecast hindcast (CMEMS forecast against NSIDC truth)

**Purpose.** The honest test: score the raw operational forecast, and persistence, on real satellite
truth, at each lead, in the corridor. The U-Net correction is scored by the same script when
checkpoints exist.

**Commands.**

Baselines only (should reproduce the committed JSON; not run in this pass):

```
python3 scripts/realforecast_hindcast.py --no-model
```

With the trained correction (needs `models/sic_correction/checkpoints/isih_prototype_lead{1,3,5,7}.pt`,
which are not in the repository now):

```
python3 scripts/realforecast_hindcast.py
```

**Inputs.** Forecast cycles from `data/cmems_forecast_archive/` (the four stale cycles listed in
`KNOWN_STALE.md` are excluded), truth from `data/nsidc_nrt/`, and the corridor box 0 to 80 E, 55 to 78 S.

**Outputs.** `dakshin/figures/realforecast_hindcast.json`, overwritten. Each lead has `n_cycles`,
`first_cycle`, `last_cycle`, pooled RMSE, and mean IIEE at the 15% threshold, each for `cmems`
and `persistence` (and `unet` with the model). The committed file has `"model": null`.

**Cycle counts.** 83 siconc files from 2026-08-31 to 2026-11-21, less the 4 stale cycles, less the
cycles without truth one day later (for lead 1, the last usable cycle is 2026-11-18). That gives 76 at
lead 1, 75 at lead 3, 74 at lead 5, 72 at lead 7. These counts reconcile with the JSON.

**Time.** Not recorded.

**What can go wrong.** Re-running after new cycles arrive changes the numbers, and the script's
docstring forbids re-tuning on this set. Record the run date with any number you quote. The JSON
does not record its input file list, so a later reader cannot tell which cycles were used except
by counting. The truth switches sensor on 2025-01-01 (AMSR2 for F17 SSMIS), which the JSON notes.

### 2.7 Resolution study (does ocean-model resolution change the answer?)

**Purpose.** Coarsen the same CMEMS cycles to about 1/4° and 1°, and score each against the same
truth (RESOLUTION_STUDY.md, F1).

**Command.**

```
python3 scripts/resolution_study.py --no-model
```

**Outputs.** `dakshin/figures/resolution_study.json` and `dakshin/figures/resolution_study.png`,
both overwritten. The JSON has one block per resolution, each with the lead-by-lead values from §2.6.

**Time.** Not recorded.

**What can go wrong.** The study coarsens one model's output. It does not run a coarser model
(the JSON's own caveat). The U-Net column needs checkpoints, as in §2.6. Without `--no-model`
the script fails until they exist.

### 2.8 Iceberg hindcast, resolution study and melt estimate

These three scripts share the iceberg forecast code (`dakshin/berg_forecast.py`, `models/iceberg/drift.py`).

**2.8a Hindcast against USNIC positions.**

```
python3 scripts/berg_hindcast.py
```

- Inputs: CMEMS analysis currents in `data/cmems_cur_analysis/` (82 daily files, 2026-08-31 to 2026-11-20), and
  the USNIC archive in `data/icebergs/archive/`.
- Output: `dakshin/figures/berg_hindcast.json`. The file records 88 segments, 81 usable, the split into
  stationary (68) and moving (13, persistence displacement above 3 km), median and mean errors, and the
  uncertainty radius (4.35 km/day).
- Wind: zero by default in `dakshin/berg_forecast.py`. The JSON records this as "zero (slice 6 pending)".
  `scripts/berg_hindcast.py` does not read `data/ecmwf_wind/`.
- Time: not recorded.

**2.8b Resolution of the currents.**

```
python3 scripts/berg_resolution.py
```

- Output: `dakshin/figures/berg_resolution.json`, with the currents at 1/12°, 1/4° and 1°.
- The usable-segment counts differ between rows (81, 86, 88). Medians are over different subsets.
- Time: not recorded.

**2.8c Freshwater (melt) estimate.**

```
python3 scripts/berg_melt.py 2026-11-21
```

- Optional argument: the cycle date, `YYYY-MM-DD`. Inputs for that cycle: `cmems_cur_<cycle>.nc`,
  `cmems_sst_<cycle>.nc`, `cmems_wav_<cycle>.nc`, and a USNIC issue. The committed JSON names
  `AntarcticIcebergs_20261120.csv`, which is in the archive.
- Output: `dakshin/figures/berg_melt.json`, labelled "ESTIMATE" in its `label` field.
- **Provenance gap.** No script in the repository produces `cmems_sst_<cycle>.nc`. The 2026-11-21 file
  is in the archive, but the command that fetched it is not recorded. Until that is fixed, this
  output cannot be regenerated from the repository for another cycle.
- Time: not recorded.

### 2.9 Real-route run and weather gate

```
python3 scripts/real_route_run.py 2026-11-21
```

- Argument: the cycle date. The script routes the unmodified Dijkstra router (`dakshin/sim/router.py`)
  on the real GLO12 ice, CMEMS waves and ECMWF wind for that cycle, on the corridor segment south of 55 S.
  It blocks land and depth using the IBCSO subset.
- Inputs: the cycle's ice, currents and waves in `data/cmems_forecast_archive/`, wind in
  `data/ecmwf_wind/ecmwf_wind_<cycle>_00z.nc`, and `data/bathymetry/ibcso_v2_corridor_0p05.nc`.
- Output: `dakshin/figures/real_route.json`: the closest approach, worst ice, worst wave, worst wind,
  and the weather gate state (`FAIL` on 4.77 m against an assumed 3.0 m limit at the 2026-11-21 cycle).
- Time: not recorded.
- What can go wrong: the gate limits (3.0 m waves, Beaufort 7 and 8 wind thresholds) are assumptions,
  not the hull's PWOM. The 80% ice limit is a stand-in. The run covers only the segment south of 55 S.
  The router's nearest-node rule changed in `478ecd2` after the committed `real_route.json` was made, so a
  re-run may give a different result. It was not re-run in this pass.

### 2.10 Claim verification

```
python3 scripts/verify_claims.py
```

- Read-only. It opens files under `dakshin/figures/` and prints a pass or fail line for each claim.
  Point it at another checkout with `DAKSHIN_ROOT=/path/to/checkout`.
- Output on 2026-11-21, run in this pass on HEAD after `13861d9`: `PASSED 29` and `All claims verified against source files.`
- **Caveat.** One of the 18 `check()` calls tests `transit days (rounded)` = 8.6 against `dakshin/figures/route_regret.json`,
  which was computed without depth. `docs/TRUE_CLAIMS.md` §1.11 now uses 8.66 days. The pass does not validate that figure.
- Time: not recorded.
- What it does not check: claims that are not written as a check (anything not in its list).

### 2.11 Test suite

```
python3 -m pytest dakshin models -q
```

Demo tests (from `docs/PROTOTYPE_README.md`):

```
.venv-demo/bin/python -m pytest dakshin/demo -q
```

- Last recorded run: 194 passed, 7 skipped (`docs/CURRENT_STATE.md`). `CURRENT_STATE` attributes
  the skips to the `model_io` tests (in `dakshin/test_model_io.py`) and to pre-existing skips. The
  `model_io` skips un-skip when the checkpoints are present.
- The demo count in the backlog (55 tests across demo, iceberg drift and protected areas) is from 2026-09-07.
- **Not run in this pass.** Commits reached `main` at 18:21 and cleared the uncommitted edits that were
  present earlier. Run `git status` first, so that the result matches a known commit. pytest also writes
  `.pytest_cache`.
- Time: not recorded.

### 2.12 Checkpoint pull (when the Kaggle kernel completes)

**Purpose.** Bring the four trained checkpoints back, check them against their checksums, and
run the scorers that need them.

**Command.**

```
KAGGLE_API_TOKEN=<token> PY=/path/to/python bash scripts/pull_checkpoints.sh
```

The script:

1. `kaggle kernels output jiteeshghodke/notebookd39fdf7959 -p models/sic_correction/checkpoints`.
2. Checks for `isih_prototype_lead{1,3,5,7}.pt` ("MISSING lead N" and exit if one is absent).
3. Writes `SHA256SUMS`.
4. Runs `pytest dakshin/test_model_io.py -q`, then `scripts/realforecast_hindcast.py` and
   `scripts/resolution_study.py` with the model.

The script ends by printing the manual steps: update the results documents with the numbers
as they come out, commit the checkpoints (about 8 MB each), and create the release
`model-v0.1` with `gh release create`.

**Failure modes.** A kernel that is not `COMPLETE` gives the MISSING line. `CURRENT_STATE` gives
the diagnosis for an errored kernel: `kaggle kernels logs jiteeshghodke/notebookd39fdf7959`. The
kernel status at the time of writing was queued; it was not queried in this pass.

**Time.** Not recorded (the kernel itself is queued on Kaggle's free GPU pool).

### 2.13 Training notebook (regenerate and push)

**Command.** Regenerate the notebook from the repository sources:

```
python3 dakshin/kaggle/make_notebook.py
```

This writes `dakshin/kaggle/isih_train.ipynb` (the script's `OUT` path). The embedded modules are
`models/sic_correction/unet.py`, `dakshin/grid.py` and `dakshin/features.py`, and the generated file says
to edit those sources, not the notebook. **Not run in this pass.**

The notebook is pushed to Kaggle with the Kaggle CLI. The push command is not in the repository.

**Time.** The notebook on Kaggle: about 1 to 2 hours (`docs/PROTOTYPE_RESULTS.md`, "Reproducing").
The 20-minute no-background ablation is a separate run described in the same file.

### 2.14 Demo application

```
uv venv .venv-demo --python 3.12
uv pip install --python .venv-demo/bin/python -r dakshin/demo/requirements.txt
.venv-demo/bin/uvicorn dakshin.demo.app:app --port 8000
```

(`docs/PROTOTYPE_README.md`.) Before starting it, the demo needs the data it reads, which is
`dakshin/data/` (the 1,096 NSIDC files, §3). The app's preflight refuses to start when the data is missing,
and its message names the folder.

- Serves committed outputs from `dakshin/figures/` and simulated fields from `dakshin/sim/`. The
  backlog records that the page still labels the synthetic fields as "replay", which is an open item
  (`docs/backlog.md`, world model section). Until it is fixed, say "simulated" aloud.
- Boot time: 3.5 to 3.8 seconds (four runs in the sandbox, 2026-09-07, `docs/backlog.md`).
- A live re-route is documented as needing a Python 3.11 PolarRoute environment (`prenv`). It is a backlog item.

### 2.15 Other scripts

Not run in this pass. Each entry gives the purpose and the header's stated output.

| Script | Purpose (from its header) | Output | Notes |
|---|---|---|---|
| `scripts/backfill_cur_analysis.py` | Back-fill the daily analysis currents | `data/cmems_cur_analysis/` (default `--start 2026-08-31 --end 2026-11-20`) | Uses the `copernicusmarine` package. The analysis is not the forecast as issued. |
| `scripts/subset_bathymetry.py` | Cut bathymetry to the corridor at 0.05°, on the whole sim box (lat 78 S to 30 S, lon 0 to 90 E). IBCSO v2 south of 50 S; GEBCO_2020 north of 50 S | `data/bathymetry/ibcso_v2_corridor_0p05.nc` (3.5 MB, in git) | Rewritten in `24317da`. IBCSO raw (254 MB) comes from the PANGAEA URL in its header into `data/bathymetry/raw/` (gitignored). GEBCO comes from NOAA CoastWatch ERDDAP. The shallowest-cell buffer is one box, about 5 km. Not run in this pass. |
| `scripts/compress_netcdf.py <file> [--lossless] [--keep-original]` | Pack a NetCDF; int16 with scale factors for the ice variables (`PACK_RANGE`) | the file, unless `--keep-original` is given (flag name; not read in full) | Called after each download. The backlog notes that `uo` and `vo` have no int16 range, so currents commit at about 10 MB, not 4 MB. |
| `scripts/reduce_wav_daily.py <file>` | Reduce 3-hourly waves to a daily maximum (`VHM0_dmax`) | the file (inferred from the harvest's use; not read) | Called by the harvest. |
| `dakshin/download_nsidc.py` | Training truth: NSIDC G02202 v6, south, daily F17 SSMIS, 2018 to 2020 | `dakshin/data/nsidc_sic/` (1,096 files) | Public, no auth. Gitignored. The URL base is `noaadata.apps.nsidc.org/NOAA/G02202_V6/south/daily`. |
| `dakshin/route_regret.py` | Route-regret experiment, static versus daily plans | route and regret JSON | `docs/backlog.md` cites a `--depart` option for per-date sweeps. Flag not checked here. |
| `dakshin/make_route_figure.py` | Route figure with PolarRoute | `dakshin/figures/route_map.png` | Needs the PolarRoute venv (`prenv`). |
| `dakshin/audit_ice_quality.py` | Land-spillover and hard-zero audit | the committed `dakshin/figures/ice_quality_audit.json` (writer path not checked) | Defines the 17 by 17 cell box (`APPROACH_RADIUS_CELLS = 8`). |
| `dakshin/destination_window.py` | Bharati and Maitri open or closed by day | the committed `dakshin/figures/destination_window.json` (writer path not checked) | 80% limit; Maitri's offload point is unknown (backlog). |
| `scripts/score_cmems_archive.py` | Score CMEMS against its own later day-0 field | — | **Do not quote.** The backlog flags this scorer as flattering CMEMS. |
| `models/iceberg/regime_report.py` | Drift regime on the USNIC catalogue | `models/iceberg/regime_report.json` | The backlog cites its 10 m/s and 30 m/s wind cases. |
| `dakshin/mlflow_backfill.py` | MLflow backfill | `mlruns/` (gitignored) | Purpose taken from its name and `docs/MLFLOW_SETUP.md`; not read in full. |
| `scripts/gen_*_drawio.py` | Generate the decision-flow and gate diagrams | `docs/*.drawio` | Documentation only. |

---

## 3. Data inventory

Sizes are measured in this pass (`du -sh`, `ls`, `git ls-files`).

| Path | Contents and naming | Size | In git | Can it be regenerated? |
|---|---|---|---|---|
| `data/cmems_forecast_archive/` | 83 `cmems_siconc_<cycle>.nc` (2026-08-31 to 2026-11-21), 1 `cmems_cur_<cycle>.nc`, 1 `cmems_wav_<cycle>.nc`, 1 `cmems_sst_<cycle>.nc`, `KNOWN_STALE.md` | 522 MB | yes (87 files) | **No, for the forecasts.** CMEMS overwrites each cycle with the next, so the forecast as issued cannot be fetched again. The repository's git history is a second copy, if the pushes succeeded. Check `git log origin/main` before relying on it. |
| `data/cmems_cur_analysis/` | 82 `cmems_cur_analysis_<date>.nc`, 2026-08-31 to 2026-11-20 (analysis currents, not forecasts) | 81 MB | yes (82) | Yes, for past analysis dates (`backfill_cur_analysis.py`), while CMEMS serves them. |
| `data/nsidc_nrt/` | 89 `sic_pss25_<YYYYMMDD>_am2_icdr_v04r00.nc` (2026-08-24 to 2026-11-20), `MANIFEST.sha256` | 35 MB | **no** (gitignored) | **Only while NSIDC keeps it, about three months.** The earliest file reaches that age around 2026-11-24. Copy it somewhere durable now. This is the most urgent item in this runbook. |
| `data/ecmwf_wind/` | `ecmwf_wind_<date>_<HH>z.nc`, one file (2026-11-21 00z) | 3.3 MB | yes (1) | **No, after 2 to 3 days.** ECMWF open data keeps the last 12 runs. Missed days are gone. |
| `data/icebergs/archive/` | `AntarcticIcebergs_<YYYYMMDD>.csv`, 14 weekly USNIC issues | 60 KB | yes | Current issue: yes (`harvest_usnic.sh`). Older issues: from the USNIC archive, whether still served was not verified. |
| `data/icebergs/usnic_antarctic_20260902.csv` | A copy of an archived issue (backlog says byte-identical to the 2026-08-27 issue) | not measured | yes | Yes, by deletion of the duplicate. Not verified in this pass. |
| `data/bathymetry/ibcso_v2_corridor_0p05.nc` | Corridor subset, 960 by 1800 cells at 0.05°, variables `elevation` (block maximum, negative is water depth, zero or positive is land or ice shelf) and `elevation_mean` (display only) | 3.5 MB | yes (1) | Yes, from the raw file with `subset_bathymetry.py`. |
| `data/bathymetry/raw/IBCSO_v2_ice-surface_WGS84.nc` | Full IBCSO v2 ice-surface grid. **Absent at 18:21 in this pass** (the directory was present at 18:11 with the 254 MB file). Not removed by this pass. It went missing in the minute `24317da` (which rewrote the subset script) landed; the cause is not established. | 254 MB when present | no (gitignored) | Yes, from PANGAEA (`subset_bathymetry.py` header). The subset itself is in git and does not depend on it. |
| `data/cmems_harvest.log` | Appended log of every harvest run | 72 KB | yes | It is the record. Keep it. |
| `dakshin/data/nsidc_sic/` | 1,096 `sic_pss25_<YYYYMMDD>_F17_v06r00.nc` (2018 to 2020, CDR v6, F17 SSMIS) | 403 MB | no (gitignored) | Yes, from NSIDC G02202 v6 (`dakshin/download_nsidc.py`). The demo needs it (`docs/backlog.md`, `[BLOCKER][demo]`). |
| `dakshin/figures/` | JSON and PNG outputs of the scripts in §2, plus `sic_points.csv` and `waypoints.csv` | 19 tracked files | yes | Yes, by re-running the scripts. The committed JSON is the number that was quoted. |
| `models/sic_correction/` | `unet.py` only | — | yes | Checkpoints absent. Pending the Kaggle kernel (§2.12). |
| `models/iceberg/` | `drift.py`, `melt.py`, `catalogue.py`, `regime_report.py`, the JSON, and tests | — | yes | Code. |
| `dakshin/kaggle/` | `make_notebook.py`, `isih_train.ipynb` | — | yes | Code. |

Naming conventions in use. CMEMS files are named by the cycle (issue) date. NSIDC files by the observation
date. USNIC by the newest "Last Update" date in the issue. Figures by the script that writes them.
Checkpoints by the lead in days (`isih_prototype_lead1.pt`); the `isih_` prefix is the pre-rename name and
is kept on purpose (`pull_checkpoints.sh`).

Irreplaceable, in order of urgency:

1. **`data/nsidc_nrt/`**: rolls off NSIDC after about three months. Not in git.
2. **`data/cmems_forecast_archive/` forecasts**: CMEMS overwrites them. In git only if pushed.
3. **`data/ecmwf_wind/`**: two to three days of retention at ECMWF.
4. **`data/icebergs/archive/`** (older issues): depends on USNIC's archive.

Everything else in this table can be regenerated from one of these or from a public source.

---

## 4. Glossary

"Defined at" gives the file that defines or uses the term in a way that fixes its meaning here.
"Standard usage" means the term is not defined in the repository, and the expansion or meaning is the
usual one in the field.

| Term | Meaning | Source |
|---|---|---|
| **SIC** | Sea-ice concentration, a fraction (0 to 1) or a percentage, depending on the product | Standard usage; used in `dakshin/features.py` |
| **IIEE** | Integrated ice-edge error: the area (km²) where the 15% ice-extent masks of forecast and truth disagree (exclusive OR, times 625 km² per cell) | Defined at `dakshin/features.py` `iiee_km2`; cites Goessling et al. 2016 |
| **RMSE** | Root mean squared error, pooled over cycles and valid cells | Standard usage; `scripts/realforecast_hindcast.py` |
| **CRPS** | Continuous ranked probability score, a proper score for probabilistic forecasts | Standard usage; named in ADR-027 (`docs/DECISIONS.md`); not computed in any file |
| **CDR** | Climate Data Record, the NOAA/NSIDC passive-microwave sea-ice concentration product | Defined at `ATTRIBUTION.md` (NSIDC CDR v6, G02202) |
| **NRT** | Near-real-time: the NSIDC stream kept for about three months | `scripts/download_nsidc_nrt.py` header; `git show 5f32ae3` |
| **ICDR** | Interim CDR, the NRT file-name tag `icdr` | `scripts/download_nsidc_nrt.py` file names; expansion standard |
| **G02202 v6, G10016 v4** | NSIDC product identifiers for the CDR (training) and the NRT stream (truth) | `ATTRIBUTION.md`, `scripts/realforecast_hindcast.py` |
| **NSIDC** | National Snow and Ice Data Center | Standard usage |
| **SSMIS** | Special Sensor Microwave Imager/Sounder, on the DMSP F17 satellite in the training record | Standard usage; `dakshin/figures/realforecast_hindcast.json` caveats |
| **AMSR2** | Advanced Microwave Scanning Radiometer 2, the sensor behind the NRT truth from 2025-01-01 | Standard usage; the JSON caveat |
| **GLO12** | CMEMS global 1/12° ocean analysis and forecast system | Defined at `scripts/harvest_cmems.sh` (dataset `cmems_mod_glo_phy_anfc_0.083deg_P1D-m`) and `ATTRIBUTION.md` |
| **GLORYS12** | CMEMS global 1/12° ocean reanalysis (the training background) | Defined at `ATTRIBUTION.md` (`cmems_mod_glo_phy_my_0.083deg_P1D-m`) |
| **CMEMS** | Copernicus Marine Environment Monitoring Service | `ATTRIBUTION.md` |
| **Cycle** | One daily CMEMS forecast issue, named by its issue date | `scripts/harvest_cmems.sh` comments |
| **Lead, lead time** | Days from the cycle (issue) date to the target date. Leads 1, 3, 5 and 7 are scored | `dakshin/features.py` (`build_channels`); `docs/PROTOTYPE_RESULTS.md` |
| **Analysis vs forecast** | The analysis is the best estimate for a past date, which CMEMS still serves. The forecast is what was issued on a given day, and CMEMS overwrites it | `scripts/harvest_cmems.sh` comments; `docs/PROTOTYPE_RESULTS.md` |
| **Stale cycle** | A file under a date whose content is the previous day's forecast, with the first day cut off | `data/cmems_forecast_archive/KNOWN_STALE.md` |
| **Persistence** | The baseline that carries the last observation forward unchanged | `scripts/realforecast_hindcast.py` docstring. The prototype's persistence is the same idea (`isih/RESULTS.md` in `27308ff`); ADR-006 names a damped anomaly version, which was demoted |
| **Raw CMEMS** | The operational forecast used without correction. ADR-027's mandatory baseline | `docs/DECISIONS.md` ADR-027 |
| **Innovation channel** | Background minus the newest observation at each cell, the signal that tells the model how wrong the background is now | `dakshin/features.py`, channel 8 |
| **Double penalty** | RMSE charges a sharp forecast twice for a misplaced edge (a miss and a false alarm) and a smoothed one once | `docs/RESOLUTION_STUDY.md` |
| **VHM0** | Spectral significant wave height (CMEMS wave variable) | `dakshin/real_world.py` docstring; `scripts/harvest_cmems.sh` |
| **VHM0_dmax** | Daily maximum of VHM0, the variable the router uses | `scripts/reduce_wav_daily.py` output; `dakshin/real_world.py` |
| **VMDR** | Mean wave direction (CMEMS wave variable) | `scripts/harvest_cmems.sh` |
| **Hs** | Significant wave height, in metres | `models/iceberg/melt.py` header |
| **siconc, sithick, usi, vsi** | CMEMS ice variables: concentration, thickness, and the two velocity components | `scripts/harvest_cmems.sh` `VARIABLES` |
| **uo, vo** | Eastward and northward surface current (m/s) | `scripts/harvest_cmems.sh` comments |
| **thetao** | Sea-water potential temperature (the SST input to melt) | `scripts/berg_melt.py` |
| **EPSG:3412** | NSIDC south polar stereographic projection, the 25 km grid | `dakshin/build_dataset.py` (grid label) |
| **IBCSO** | International Bathymetric Chart of the Southern Ocean, version 2; the ice-surface grid is used | `ATTRIBUTION.md`; `scripts/subset_bathymetry.py` header |
| **GEBCO** | General Bathymetric Chart of the Oceans; the north of 50 S in the subset | `scripts/subset_bathymetry.py` header; ADR-026 |
| **TID** | GEBCO type indicator: measured or predicted depth | ADR-026 (`docs/DECISIONS.md`) |
| **ENC** | Electronic navigational chart, the official chart the chart gate needs before it can pass | `dakshin/gates.py` `chart_gate`; `docs/TRUE_CLAIMS.md` §1.17 |
| **ECDIS** | Electronic chart display and information system | `docs/backlog.md` (MSC.232(82)) |
| **QA flag** | The CDR's `cdr_seaice_conc_qa_flag` bit field | `dakshin/ice_quality.py` |
| **Land spillover filter** | CDR filter that writes 0.0 for coastal cells whose footprint overlaps land. QA flag value 4 (`docs/PROTOTYPE_RESULTS.md` calls this "bit 4") | `dakshin/ice_quality.py` docstring and `QA_LAND_SPILLOVER = 4` |
| **Invalid ice mask** | CDR QA flag value 16 | `dakshin/ice_quality.py` (`QA_INVALID_ICE_MASK = 16`) |
| **No input data** | CDR cell with no retrieval input | `dakshin/ice_quality.py` |
| **Grounded or unknown** | Iceberg track state when a forecast step lands on a NaN current (land or outside the data) | `dakshin/berg_forecast.py` |
| **USNIC** | U.S. National Ice Center, source of the weekly Antarctic iceberg list | `ATTRIBUTION.md` |
| **WDE17** | Wagner, Dell and Eisenman 2017, the closed-form iceberg drift model used | `ATTRIBUTION.md`; `models/iceberg/drift.py` |
| **RK2** | Second-order midpoint (Runge-Kutta) integration of berg position | `dakshin/berg_forecast.py` |
| **R (wind forcing)** | Ratio of wind-driven to current-driven drift, per segment, at an assumed 10 m/s wind | `dakshin/berg_forecast.py`; `berg_hindcast.json` |
| **ADE, FDE** | Average and final displacement error, as used in the IDRIFTNET paper; the horizon is not stated there | `docs/backlog.md`; `docs/ICEBERG_RESEARCH.md` |
| **Keghouche et al. 2010** | The melt-term set (basal, buoyant convection, wave erosion) used for freshwater, Arctic-calibrated | `models/iceberg/melt.py` header |
| **Freshwater estimate** | Melt volume per day along a track, an estimate (`berg_melt.json` label) | `scripts/berg_melt.py` |
| **PolarRoute** | British Antarctic Survey routing engine (MIT) that the project wraps | `ATTRIBUTION.md`; ADR-009 |
| **meshiphi** | British Antarctic Survey mesh and ice-physics package used with PolarRoute | `ATTRIBUTION.md`; ADR-013 |
| **excluded_zones** | PolarRoute's vessel-config hook that marks mesh cells inaccessible | ADR-010 (`docs/DECISIONS.md`) |
| **Dijkstra** | Shortest-path search used by the project's router | `dakshin/sim/router.py`; `scripts/real_route_run.py` |
| **POLARIS** | The IMO polar operational limit assessment and risk indexing system (MSC.1/Circ.1519). Its expansion is standard; the repository does not expand it | `docs/backlog.md`; `docs/TRUE_CLAIMS.md` §4 |
| **RIO, RIV** | Risk index outcome, and risk index value per ice class (POLARIS) | `docs/backlog.md` (`RIO = Σ(Ci × RIVi)`) |
| **WMO egg code** | The World Meteorological Organization sea-ice code (stage of development, concentration, form) | `docs/backlog.md` |
| **ULA** | Old Russian ice-class notation for the vessel's class | `docs/PROTOTYPE_RESULTS.md` §5 |
| **MIZ** | Marginal ice zone | `docs/DECISIONS.md` ADR-020; standard usage |
| **Gate states (PASS, MARGINAL, FAIL, UNKNOWN)** | The four outcomes of each decision gate. UNKNOWN names the dataset that would settle it | `dakshin/gates.py` |
| **Conformal prediction (split, stratified)** | A calibration method that gives a coverage guarantee from held-out residuals. Designed for the uncertainty layer | ADR-020 (`docs/DECISIONS.md`) |
| **Ensemble** | Several models whose disagreement is used as uncertainty | ADR-004, ADR-005 |
| **Route regret** | Extra time (or fuel) from planning on stale ice, compared with planning on the day's ice | `docs/PROTOTYPE_RESULTS.md` §3 |
| **STATIC, STATIC-noQA, DAILY** | The three route arms in the regret experiment: planned once on departure ice; the same with spillover cells trusted; re-planned each morning | `docs/PROTOTYPE_RESULTS.md` §3 |
| **Dominance filter** | Removing any route that another route beats on every objective | ADR-021 |
| **Time-expanded graph** | A routing graph with one ice layer per forecast day, so a forecast can change the route | `docs/TRUE_CLAIMS.md` §5 |
| **ASPA, ASMA** | Antarctic Specially Protected Area and Antarctic Specially Managed Area, under the Antarctic Treaty | `dakshin/protected_areas.py`; `docs/backlog.md` |
| **MARPOL Annex I, Reg. 43** | Ban on heavy fuel oil south of 60 S (the reason the vessel runs marine diesel) | `docs/backlog.md` |
| **MV Vasiliy Golovnin** | The chartered vessel the project is calibrated to | `docs/PROTOTYPE_RESULTS.md` §5 |
| **Bharati, Maitri** | Indian Antarctic stations; Bharati is the resupply destination | `docs/PROTOTYPE_RESULTS.md` |
| **ISEA** | The Indian Scientific Expedition to Antarctica series | Standard usage; `docs/PROTOTYPE_RESULTS.md` |
| **NCPOR** | National Centre for Polar and Ocean Research | Standard usage; `docs/backlog.md` |
| **ISIH** | The pre-rename prefix of the prototype (the package was renamed to `dakshin`; file names keep `isih_`) | `docs/CURRENT_STATE.md`; `docs/backlog.md` |
| **Kernel** | A Kaggle notebook run, identified by its owner and slug | `docs/CURRENT_STATE.md` |
| **NEMO, ANHA** | The NEMO ocean model, and the ANHA family of regional NEMO configurations | `docs/RESOLUTION_STUDY.md` |
| **OSI SAF** | Ocean and Sea Ice Satellite Application Facility (ice drift and ice products) | `docs/backlog.md` |
| **ERA5, IFS** | ECMWF's reanalysis and its Integrated Forecasting System | `scripts/harvest_ecmwf_wind.py` header; ATTRIBUTION |
| **AIS** | Automatic Identification System, ship position broadcasts; the Southern Ocean has very little shore-side coverage | `dakshin/ais_feed.py`; `docs/backlog.md` |
| **Beaufort** | Wind-force scale; the weather gate uses Beaufort 7 and 8 thresholds | `dakshin/gates.py` (`WIND_FAIL_MS`, `WIND_MARGINAL_MS`) |
| **USNIC catalogue, "Last Update"** | Weekly list of giant bergs; the newest date in the file names the archive copy | `scripts/harvest_usnic.sh` |
| **Stage A, Stage B** | Stage A is training on the reanalysis; Stage B is fine-tuning and acceptance on the real forecast archive | `docs/DECISIONS.md` ADR-019 |
| **NMEA** | National Marine Electronics Association sentence format for ship instruments and AIS | Standard usage; `dakshin/ais_feed.py` |
| **AIVDM** | The AIS message sentence type used for ship position reports | Standard usage; `dakshin/ais_feed.py` |
| **PC1 to PC7** | IACS Polar Class notations; `dakshin/polaris.py` has the PC table (`CLASSES`) used for the POLARIS speed caps | `dakshin/polaris.py` line 45 |
| **OOW** | Officer of the watch | Standard usage; used in `dakshin/test_workflow.py` and `dakshin/demo/test_app.py` |
| **NM** | Nautical mile; the traffic gate uses 2 and 5 NM bands | `dakshin/gates.py` (`TRAFFIC_FAIL_NM`, `TRAFFIC_MARGINAL_NM`) |
| **ETA** | Estimated time of arrival, in days from departure in the real-route output | `dakshin/figures/real_route.json` (`eta_days`); `dakshin/alternatives.py` |
| **ACC** | Antarctic Circumpolar Current | Standard usage |
| **UKC** | Under-keel clearance, the depth margin above the draught | `docs/DECISIONS.md` ADR-026 |
| **GBM** | Gradient-boosted machine, the planned iceberg residual model (stretch goal) | `docs/DECISIONS.md` ADR-008 |
| **LUT** | Lookup table (the literature thickness and density table) | `docs/DECISIONS.md` ADR-013 |
| **AOI** | Area of interest (the corridor box as a configuration input) | `docs/backlog.md`, configuration requirement |
| **GAMMA, C_A, C_W** | WDE17 drift coefficients: gamma from the air and water drag coefficients (`C_A` = 1.3, `C_W` = 0.9) | `models/iceberg/drift.py` |
| **MATLAB reference code** | The author's reference implementation of WDE17, used to settle the drag-coefficient swap | `docs/backlog.md` (`[resolved][ml]`) |
| **REPLAY, SIMULATED** | Provenance labels on the demo's fields. The backlog records that the synthetic fields still say REPLAY | `dakshin/demo/static/provenance.js`; `docs/backlog.md` |
| **CMIP-style names** | Variable and coordinate naming conventions that the NEMO reader accepts | `dakshin/readers/nemo.py` (F2) |
| **ADR** | Architecture decision record in `docs/DECISIONS.md` | — |
| **Claims ledger** | `docs/TRUE_CLAIMS.md`, each claim with its evidence file | — |
