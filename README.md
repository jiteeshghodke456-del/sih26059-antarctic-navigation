# Dakshin

Dakshin is an advisory decision aid for Antarctic resupply voyages, built on real observations and operational model output only. It combines an ocean-model sea-ice forecast, satellite sea-ice concentration with explicit quality control, an iceberg drift and melt estimate, bathymetry and weather into a time-dependent route search and nine evidence-based decision gates. It is scoped to one corridor (Cape Town to Bharati and Maitri), one season (austral summer) and one chartered vessel (MV Vasiliy Golovnin), and it advises; it does not steer the ship.

The project treats its own negative results as findings. Several of its first claims were withdrawn after testing, and the record of why is part of the method (see "Withdrawn claims").

Study documents for a technical reader are in `docs/study/`: [architecture and data flow](docs/study/ARCHITECTURE_AND_DATAFLOW.md) and [physics, statistics and papers](docs/study/PHYSICS_AND_PAPERS.md).

## Results

All numbers below come from files committed in this repository. The path of the file that produces each is given.

### 1. Raw operational forecast against persistence, 2026 spring

76 archived CMEMS GLO12 forecast cycles (2026-08-31 to 2026-11-18), regridded to the NSIDC 25 km grid and scored against NSIDC near-real-time concentration (AMSR2, QA-masked) in the corridor 0 to 80 E, 55 to 78 S. Source: `dakshin/figures/realforecast_hindcast.json`.

| Lead | RMSE, CMEMS | RMSE, persistence | IIEE, CMEMS (km2) | IIEE, persistence (km2) | U-Net |
|---|---|---|---|---|---|
| 1 day | 0.10199 | 0.11977 | 195,058 | 187,706 | training re-run in progress |
| 3 days | 0.10479 | 0.14391 | 194,575 | 277,167 | training re-run in progress |
| 5 days | 0.10981 | 0.15508 | 200,203 | 319,189 | training re-run in progress |
| 7 days | 0.11530 | 0.16414 | 210,200 | 353,255 | training re-run in progress |

By RMSE the forecast beats persistence at every lead. By ice-edge error (IIEE, 15% threshold) persistence is marginally better at one day and clearly worse from three days. The sample is one spring season of strongly autocorrelated cycles and no confidence intervals are reported.

### 2. Model resolution: RMSE cannot see it, the ice edge can

The same forecasts block-averaged from 1/12 degree to about 1/4 degree and 1 degree, scored on identical cells. Source: `dakshin/figures/resolution_study.json`, `docs/RESOLUTION_STUDY.md`.

Coarsening to 1/4 degree slightly improves RMSE (0.10035 against 0.10199 at one day) and 1 degree roughly ties it, which is the double-penalty effect: a sharp forecast that misplaces an edge is penalised twice, a smoothed one once. The ice-edge metric does separate them: at 1 degree the integrated ice-edge error is 4% worse than at 1/12 degree at one day and 16% worse (33,975 km2) at seven days. 1/12 degree and 1/4 degree are not distinguishable in this corridor and season. Coarsening one model's output is not the same as running a coarser model; a proper test needs the same model run at several resolutions, which is the purpose of the NEMO reader (`dakshin/readers/nemo.py`, not yet run on real NEMO output).

### 3. Icebergs: most corridor giants are grounded

Wagner, Dell and Eisenman (2017) drift driven by CMEMS surface currents, integrated with a midpoint scheme, validated against 88 later weekly USNIC position pairs from 8 bergs. Source: `dakshin/figures/berg_hindcast.json`.

| Quantity | Model | Persistence (berg did not move) |
|---|---|---|
| Median error, 81 usable segments (km/day) | 4.35 | 0.0 |
| Moving segments only, 13 (km/day) | 6.01 | 2.45 |

Persistence wins. Most giants are anchored, and a current-advection model without grounding detection moves anchored ice. Block-averaging the currents to 1 degree lowers the error (3.49 km/day, `dakshin/figures/berg_resolution.json`) for the same reason, not because eddies are unimportant. The drift forecast cone in the interface grows at the measured 4.35 km/day.

### 4. The satellite product writes coastal ice as open water

The NOAA/NSIDC CDR applies a land-spillover filter and writes the suppressed cells as 0.0, which lies inside the product's valid range. Over all 1,096 daily files from 2018 to 2020 the filter fires on every day (mean 118 cells, maximum 488), and in a 17 by 17 cell box around Bharati station suspect cells occur on 43.2% of days. Bharati's own cell was closed to this vessel on 23 of 31 days of December 2019 at an 80% working limit, while the approach point 100 km north was open on all 31; four of the eight apparently open days were exact-zero artefacts. Source: `dakshin/figures/ice_quality_audit.json`, `dakshin/figures/destination_window.json`, `dakshin/ice_quality.py`.

### 5. A real-data route run

On the 2026-11-21 forecast, with real ice, waves and wind, the time-dependent router finds the Bharati approach closed at the 80% limit; the closest reachable cell is 50.6 km away, the weather gate returns FAIL (4.77 m significant wave height against an assumed 3.0 m limit), and the segment south of 55 S takes 5.55 days. Source: `dakshin/figures/real_route.json`. The published prototype route (1 December 2019 ice, PolarRoute, real IBCSO v2 depth in the mesh) takes 8.66 days steaming and ends 16 km off the station; this is a lower bound with no sea-state penalty (`docs/TRUE_CLAIMS.md` claim 1.11).

### Withdrawn claims

| Claim | What happened |
|---|---|
| 17.4-day Cape Town to Bharati transit | Computed with beam and speed wrong, the ship at about half its real speed. Corrected. |
| 8.6-day transit | Its final point was Bharati station itself, above sea level in IBCSO v2. Withdrawn 2026-11-21, then regenerated with depth in the mesh as 8.66 days. |
| "The route bends around the thickest ice" | Measurement showed the route crosses more average ice (19.6% against 8.4%). Caption removed. |
| Defence that the reanalysis background could not have leaked the target | Withdrawn; the flat error across lead is the fingerprint of a field that has seen the target. |
| +27% over persistence | Selected the best of 30 epochs on the set it then reported. Not used. |
| A 12 km/day iceberg uncertainty growth | Unverified; replaced by the measured 4.35 km/day. |

The earlier training-time result (a residual U-Net beating persistence by 18.5% to 30.6% at 1 to 7 days) used a reanalysis background and is an upper bound on forecast skill, not a measurement of it (`docs/PROTOTYPE_RESULTS.md`).

## Architecture

```
 harvest (daily)                    quality control            models                       decision
 CMEMS GLO12 ice, currents, waves   NSIDC QA flags             residual U-Net on SIC        RealWorld.sample(lat, lon, t)
 ECMWF 10 m wind                    land-spillover masking     (clip(background + delta))   time-dependent Dijkstra router
 NSIDC CDR / NRT truth              regrid onto 25 km grid     WDE17 iceberg drift (RK2)    depth and land blocking
 USNIC weekly bergs                 stale-cycle rejection      iceberg melt estimate        nine gates -> route health
 IBCSO v2 / GEBCO bathymetry                                                                 (UNKNOWN never passes)
```

The truth grid is the NSIDC south polar stereographic grid, EPSG:3412, 332 by 316 cells at 25 km. Model fields are regridded onto it and the truth is never resampled. The sea-ice model learns a residual on top of the CMEMS forecast, so a zero output reproduces the operational forecast. The router evaluates ice and waves at the time the ship would arrive at each lattice node. The nine decision gates are capability, chart, ice, weather, traffic, logistics, communications, contingency and execution; route health is the worst gate state, and a gate with no evidence counts as unknown rather than as a pass. The chart gate can never pass, because the bathymetry is a scientific compilation and not an official chart. Details, file by file, are in the architecture study document.

A seeded synthetic world (`dakshin/sim/`) exists only to drive the bridge-console demo and the router tests, and the console labels itself as synthetic. No reported result uses it.

## Data sources and licences

Full terms and citations are in `ATTRIBUTION.md`. The code is MIT-licensed (`LICENSE`).

| Data | Used for | Terms |
|---|---|---|
| Copernicus Marine GLO12 analysis and forecast (ice, currents), doi:10.48670/moi-00016 | daily forecast archive, currents | free with registration, credit required |
| Copernicus Marine global wave analysis and forecast, doi:10.48670/moi-00017 | daily maximum wave height | same |
| Copernicus Marine GLORYS12 reanalysis, doi:10.48670/moi-00021 | training background | same |
| NOAA/NSIDC CDR G02202 v6, doi:10.7265/efmz-2t65 | training truth 2018 to 2020, quality audit | NOAA open data, citation required |
| NOAA/NSIDC near-real-time CDR G10016 v4, doi:10.7265/tgam-yv28 | 2026 satellite truth | NOAA open data, citation required |
| ECMWF open data, IFS 10 m wind | wind | CC BY 4.0; "Contains modified ECMWF open data (CC BY 4.0)" |
| IBCSO v2, doi:10.1594/PANGAEA.937574 | bathymetry south of 50 S | CC-BY-4.0 |
| GEBCO_2020, doi:10.5285/a29c5465-b138-234d-e053-6c86abc040b9 | bathymetry north of 50 S | public domain; not for navigation |
| US National Ice Center Antarctic iceberg list | weekly giant-berg positions | US Government work |
| Natural Earth; Antarctic Treaty protected-area register | coastline; protected areas | public domain; public treaty data |

PolarRoute and meshiphi (British Antarctic Survey, MIT) are used for the prototype corridors. OpenDrift and OpenBerg (GPL-2.0) are never imported.

## Reproducing the numbers

Run from the repository root with Python 3.12 and `numpy`, `xarray`, `netCDF4` or `h5netcdf`, `pyproj`, `scipy`, `pandas`, `matplotlib` (and `torch` for model runs, `copernicusmarine` for CMEMS). There is no top-level requirements file; `dakshin/demo/requirements.txt` pins the demo stack. Several scripts overwrite the committed JSON they reproduce, so work in a copy if you want to keep the originals. Tests that read the satellite archives need the gitignored data (see below).

| Number | Command | Output |
|---|---|---|
| Test suite | `python -m pytest -q` | 195 passed, 7 skipped (the skips wait for model checkpoints) |
| 29 quoted claims against source | `python scripts/verify_claims.py` | `PASSED 29` |
| Table 1 (raw CMEMS, persistence) | `python scripts/realforecast_hindcast.py --no-model` | `dakshin/figures/realforecast_hindcast.json` |
| Table 2 (resolution) | `python scripts/resolution_study.py --no-model` | `resolution_study.json`, `resolution_study.png` |
| Table 3 (bergs) | `python scripts/berg_hindcast.py`, `python scripts/berg_resolution.py` | `berg_hindcast.json`, `berg_resolution.json` |
| Melt estimate | `python scripts/berg_melt.py` | `berg_melt.json` |
| Real-data route | `python scripts/real_route_run.py 2026-11-21` | `real_route.json` |
| Quality audit | `python dakshin/audit_ice_quality.py` | `ice_quality_audit.json` (needs the 2018 to 2020 archive) |
| Iceberg regime table | `python models/iceberg/regime_report.py --csv data/icebergs/archive/AntarcticIcebergs_20260827.csv` | `models/iceberg/regime_report.json` (without `--csv` it downloads today's catalogue and the values change) |

Re-running the hindcast today gives the committed values at leads 3, 5 and 7 and a slightly different lead 1 (77 cycles, RMSE 0.10219 against persistence 0.11914), because the 2026-11-19 cycle has since become scorable. The study document records this.

Data that is not in the repository: the NSIDC near-real-time files (`python scripts/download_nsidc_nrt.py`, only about the last three months are available) and the 2018 to 2020 CDR archive (`python dakshin/download_nsidc.py --start-year 2018 --end-year 2020`). The forecast archive in `data/cmems_forecast_archive/` is committed and cannot be re-fetched, because forecasts as issued are overwritten. Four of its cycles are stale copies of the previous day and are excluded (`data/cmems_forecast_archive/KNOWN_STALE.md`).

## Repository map

| Path | Contents |
|---|---|
| `dakshin/` | core package: quality control, grid and regridding, features, gates, decision objects, real-data world, iceberg forecast, demo |
| `dakshin/readers/` | NEMO output reader (curvilinear coordinates into the regridder) |
| `dakshin/sim/` | router and vessel model; synthetic demo world; bathymetry and land lookups |
| `dakshin/figures/` | committed result files quoted above |
| `models/sic_correction/` | residual U-Net (`unet.py`); checkpoints pending |
| `models/iceberg/` | WDE17 drift, melt terms, USNIC loader, regime report |
| `scripts/` | harvesters, back-fills, experiments |
| `data/` | harvested archives (forecast cycles, currents, wind, bergs, bathymetry subset) |
| `.github/workflows/cmems-harvest.yml` | the daily CMEMS harvest, the only scheduled job |
| `docs/` | design record; `docs/TRUE_CLAIMS.md` lists what can be shown and what cannot; `docs/backlog.md` lists open work |
| `docs/study/` | study documents |

## Status and what is pending

Training re-run in progress. The four trained checkpoints (leads 1, 3, 5, 7 days) are not yet in the repository: the original 2026-08-31 checkpoints were never retrievable, and a re-run on Kaggle (kernel version 6) was queued when `docs/CURRENT_STATE.md` was last written. Until it completes, every U-Net column above is pending, the training-time results in `docs/PROTOTYPE_RESULTS.md` cannot be reproduced, and the question of whether the correction beats raw CMEMS on real forecasts is open. The no-background ablation that would settle the leakage question has not been run.

Not built, by design recorded in `docs/`: calibrated uncertainty (a conformal bound with a pre-committed pass gate), an ensemble, a thickness channel for POLARIS, berg grounding detection (a first version is an uncommitted change at the time of writing), a compression-risk field, and a time-expanded route graph for the PolarRoute engine. The nine gates include three that cannot pass in code (capability, chart, communications) and two that pass only with live data (traffic, execution).

Known limits to state first: the sensor changes between the training truth (SSMIS) and the 2026 truth (AMSR2); the corridor and season are narrow; the 80% ice limit, the 3.0 m wave limit and the traffic distances are working assumptions, and ice class is defined by thickness, not concentration; fuel is relative only; the iceberg melt coefficients are Arctic-calibrated and the melt figures are estimates.
