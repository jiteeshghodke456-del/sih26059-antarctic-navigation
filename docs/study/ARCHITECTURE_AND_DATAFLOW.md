# Dakshin: architecture and data flow

Study document. Written 2026-11-21 against the committed repository (branch `main`, HEAD `44e3efa` at the time of the final check). Another process was editing `dakshin/berg_forecast.py` in the working tree while this was written (an uncommitted addition of a grounding check against the bathymetry subset with an assumed 207 m draught, 0.83 x 250 m); everything below describes the committed code. Every number below is taken from a file in the repository, whose path is given beside it, or was measured while writing this document, in which case it says "measured here" and gives the command. Where something is pending or unknown the text says so. Nothing here is invented to fill a gap.

Conventions. Paths are relative to the repository root. "Committed" means tracked by git; "gitignored" means present on the author's disk but not in the repository and therefore to be re-fetched (see section 9). "Training re-run in progress" marks every place where a U-Net result would sit but does not yet exist.

Contents: 1 what the system is; 2 component map; 3 file-by-file tables; 4 the grid story; 5 the data pipelines (a to e); 6 the nine gates; 7 two routing engines; 8 what is real and what is synthetic; 9 data on disk, committed or not; 10 data operations (commands); 11 state of the model and the open items.

---

## 1. What the system is, in one page

Dakshin is an advisory decision aid for Antarctic resupply voyages. The scoped case (ADR-001, `docs/DECISIONS.md`) is one corridor (Cape Town to Bharati/Maitri), one season (austral summer) and one chartered vessel (MV Vasiliy Golovnin, IMO 8723426). It does not steer the ship, it does not warn about growlers or bergy bits, and it does not quote fuel (`docs/TRUE_CLAIMS.md` section 4).

It has four technical parts.

1. A data layer: harvested ocean-model forecasts (CMEMS GLO12 ice, currents, waves), ECMWF 10 m wind, NSIDC passive-microwave sea-ice concentration (the "truth"), USNIC iceberg positions and IBCSO v2 bathymetry. Quality control on the satellite product is a first-class step (`dakshin/ice_quality.py`).
2. A sea-ice model: a small residual U-Net that corrects the CMEMS ice-concentration forecast toward satellite observations (`models/sic_correction/unet.py`). It is trained, but the checkpoints that would be scored against real operational forecasts are not yet on disk: training re-run in progress (section 11).
3. An iceberg model: the Wagner, Dell and Eisenman (2017) closed-form drift law driven by CMEMS surface currents, integrated with a midpoint (RK2) scheme, validated against later USNIC fixes, plus a melt estimate (`models/iceberg/`, `dakshin/berg_forecast.py`).
4. A decision layer: a time-dependent Dijkstra router (`dakshin/sim/router.py`) fed by a `RealWorld` object (`dakshin/real_world.py`), and nine decision gates whose worst state sets a "route health" (`dakshin/gates.py`, `dakshin/decision.py`). Unknown evidence is never treated as a pass.

The methodological stance, visible everywhere in the code and the docs, is that the repository reports what a test returns, including when it goes against the project. Four numbers have been withdrawn or restated in the record (17.4-day transit, 8.6-day transit, a figure caption, a defence of the reanalysis background); they are listed in `docs/TRUE_CLAIMS.md` section 3.

---

## 2. Component map

| Location | What lives there |
|---|---|
| `dakshin/` | The core package. Satellite-data quality control (`ice_quality.py`), grid and regridding (`grid.py`), feature construction and scoring metrics (`features.py`), checkpoint loading (`model_io.py`), the real-data world for the router (`real_world.py`), iceberg forecasting (`berg_forecast.py`), AIS decoding (`ais_feed.py`), decision objects and gates (`decision.py`, `gates.py`, `workflow.py`), POLARIS band calculation (`polaris.py`), protected areas, coastline, and the September-prototype routing experiments that run on PolarRoute (`make_route_figure.py`, `ice_meshes.py`, `route_regret.py`, `alternatives.py`, `destination_window.py`). |
| `dakshin/readers/` | `nemo.py`: reader for native NEMO output (grid_T/U/V and ice files), mapping classic and CMIP-style variable names to one set of fields on curvilinear `nav_lon`/`nav_lat`. Never run on real NEMO output (its own docstring says so). |
| `dakshin/sim/` | A deterministic, seeded, synthetic Southern Ocean world (`world.py`, `fields.py`, `ice.py`, `bergs.py`, `noise.py`) used by the bridge console demo, plus the `Router` and `VesselModel` (`router.py`) that are also used on real data, plus real-data helpers (`bathymetry.py`, `geo_mask.py`). See section 8. |
| `dakshin/demo/` | FastAPI app and static front end. Serves the real, already computed artifacts under `dakshin/figures/` and the bridge console. The console declares its environment as synthetic (`dakshin/demo/test_bridge_ui.py` asserts the page contains "SYNTHETIC ENVIRONMENT"). |
| `dakshin/kaggle/` | `make_notebook.py` generates `isih_train.ipynb`, the self-contained Kaggle training notebook, by embedding `unet.py`, `grid.py` and `features.py` from the repository so the two cannot drift. |
| `dakshin/figures/` | Committed result files: the JSONs quoted in this document plus figures. |
| `dakshin/data/` | Gitignored. Holds the 1,096 daily NSIDC G02202 v6 files (2018-01-01 to 2020-12-31) used for training truth and for the QA audit. |
| `models/sic_correction/` | `unet.py` only. `checkpoints/` does not exist yet (section 11). |
| `models/iceberg/` | `drift.py` (WDE17), `melt.py` (three melt terms), `catalogue.py` (USNIC loader and archive fetcher), `regime_report.py` and its JSON (which drift regime the real catalogue sits in). |
| `scripts/` | Harvesters, back-fills, and the experiment scripts that write `dakshin/figures/*.json`. |
| `data/` | Harvested archives: `cmems_forecast_archive/` (committed), `cmems_cur_analysis/` (committed), `ecmwf_wind/` (one file committed), `icebergs/` (committed), `bathymetry/` (corridor subset committed), `nsidc_nrt/` (gitignored). |
| `.github/workflows/cmems-harvest.yml` | The only scheduled job in the repository. |
| `docs/` | Design record. `ML_ARCHITECTURE.md`, `ARCHITECTURE.md`, `DECISIONS.md`, `TRUE_CLAIMS.md`, `PROTOTYPE_RESULTS.md`, `RESOLUTION_STUDY.md`, `CURRENT_STATE.md`, `backlog.md`. `docs/study/` is this study pack. |

Test suites sit beside the code (`dakshin/test_*.py`, `dakshin/sim/test_sim.py`, `dakshin/demo/test_*.py`, `dakshin/readers/test_nemo.py`, `models/iceberg/test_*.py`). Measured here (2026-11-21, `python -m pytest -q` from the repository root, working tree): 195 passed, 7 skipped, 27.6 s. The skips are the checkpoint-dependent tests in `dakshin/test_model_io.py` and pre-existing ones; they un-skip when checkpoints land (`docs/CURRENT_STATE.md`). A few minutes earlier the same working tree, mid-edit by another process, showed 3 failures in `dakshin/sim/test_sim.py` and `dakshin/test_behavioural.py`; re-run before quoting a test count.

There is no top-level `requirements.txt` or `pyproject.toml`. The only pinned list is `dakshin/demo/requirements.txt` (fastapi, uvicorn, xarray, numpy, pyproj, h5netcdf, h5py, pyshp, pytest, httpx). The harvest and experiment scripts additionally need `copernicusmarine`, `netCDF4`, `torch`, `scipy`, `pandas`, `matplotlib`, `ecmwf-opendata`, `cfgrib`/`eccodes` and `pyais` (`ATTRIBUTION.md` lists the dependency licences).

---

## 3. File-by-file tables

Writers/readers are given as paths. "lib" means imported by others and does no I/O of its own.

### 3.1 `dakshin/`

| File | What it does | Key functions | Reads / writes |
|---|---|---|---|
| `ice_quality.py` | QA for NSIDC CDR: sets land-spillover and no-input cells to NaN, reports the QA bit breakdown, detects a "hard zero next to heavy ice" without needing flags | `load_sic`, `load_stdev`, `qa_breakdown`, `hard_zero_next_to_ice`; QA bit constants | reads CDR NetCDF (`cdr_seaice_conc`, `cdr_seaice_conc_qa_flag`, `cdr_seaice_conc_stdev`); used by hindcast, route meshes, audit |
| `grid.py` | NSIDC EPSG:3412 geometry and the regridder from a lat/lon source (1-D axes or 2-D curvilinear) onto the NSIDC grid by mean of source points per target cell | `nsidc_lonlat`, `GlorysToNsidcRegridder` (`__call__`, `coverage`) | lib; used by the Kaggle notebook, hindcast, NEMO path |
| `features.py` | Builds the 12 input channels for training (`build_channels`) and for the operational hindcast (`build_channels_operational`); RMSE; IIEE; the baseline suite | `build_channels`, `build_channels_operational`, `iiee_km2`, `rmse`, `evaluate_baselines` | lib |
| `model_io.py` | Loads a lead's checkpoint after a SHA-256 check against `models/sic_correction/checkpoints/SHA256SUMS`; refuses unverified weights | `checkpoint_path`, `verify_checksum`, `load_checkpoint`; config `in_channels=12, base_filters=32, depth=3` | reads `models/sic_correction/checkpoints/isih_prototype_lead{1,3,5,7}.pt` (absent today) |
| `real_world.py` | Real-data counterpart of the synthetic `World` with the same `sample(lat, lon, t)` contract; one archived forecast cycle supplies ice, waves, wind | `RealWorld.sample` | reads `data/cmems_forecast_archive/cmems_siconc_<cycle>.nc`, `cmems_wav_<cycle>.nc`, `data/ecmwf_wind/ecmwf_wind_<cycle>_00z.nc` |
| `berg_forecast.py` | Daily-current field object and RK2 berg integrator with hourly steps; stops a berg at a NaN current and marks it "grounded or unknown" | `CurrentField` (`from_files`, `sample`), `Track`, `forecast_track`, `great_circle_km` | reads CMEMS `uo`/`vo` files; used by `scripts/berg_hindcast.py`, `berg_resolution.py`, `berg_melt.py` |
| `ais_feed.py` | NMEA 0183 AIS decoder (pyais) from UDP or file; latest position per MMSI; sentinels (lat 91, lon 181, 102.3 kn, 360 deg) rejected; fragment buffer bounded | `AISFeed.feed_sentence`, `feed_file`, `listen_udp` | no persistent I/O; feeds `traffic_gate` |
| `decision.py` | Data model of the decision layer: gate states, route health, evidence, decision, approval | `GateState`, `Health`, `GateResult`, `health_from_gates`, `Decision`, `gate_digest` | lib |
| `gates.py` | The nine gate evaluators and `evaluate_all` | `capability_gate`, `chart_gate`, `ice_gate`, `weather_gate`, `traffic_gate`, `logistics_gate`, `communications_gate`, `contingency_gate`, `execution_gate`, `evaluate_all`, `coverage_summary` | lib; called by `dakshin/demo/decision_service.py`, `scripts/real_route_run.py` |
| `workflow.py` | The passage workflow (mission, route plan, review, approve, re-plan) as a state machine | `Workflow`, `Mission`, `Voyage`, `Stage` | lib |
| `polaris.py` | IMO POLARIS (MSC.1/Circ.1519, Table 1.3) risk index computed as a band across candidate ice-class rows, never as one number | `rio_exact`, `rio_single_stage`, `band`, `along`, `tier`, `speed_limit_kn` | lib |
| `protected_areas.py`, `download_protected_areas.py` | ASPA (permit required) versus ASMA (management plan) treated as different constraint types; Treaty Secretariat shapefile (EPSG:3031) to a small committed extract | `load_areas`, `station_context`, `build_extract` | writes `dakshin/figures/protected_areas.json` |
| `coastline.py` | Natural Earth coastline simplified to a committed extract so the running app needs no GIS stack | `build`, `rdp`, `clip_polygon` | writes `dakshin/figures/coastline.json` |
| `download_nsidc.py` | Fetches NSIDC G02202 v6 south daily files for a year range, 6 workers by default | `list_year_files`, `download_one` | writes `dakshin/data/nsidc_sic/` (gitignored) |
| `build_dataset.py` | Builds per-year `.npz` of paired (GLORYS12 background, NSIDC truth, mask, dates); not what the Kaggle notebook uses (the notebook builds the pairs in memory) | `build_year`, `fetch_glorys_year` | writes `.npz` per year |
| `audit_ice_quality.py` | Audits all 1,096 CDR days for spillover, no-input and hard-zero cells, and for the 17 x 17 cell box around Bharati and Maitri | `station_windows` | writes `dakshin/figures/ice_quality_audit.json` |
| `ice_meshes.py` | One cached PolarRoute vessel-performance mesh per day; defines the `GOLOVNIN` config dict | `vessel_mesh_for`, `CellLookup` | needs PolarRoute env; caches under `dakshin/data/vessel_meshes/` |
| `make_route_figure.py`, `plot_route.py` | One PolarRoute route (Cape Town to Bharati, 2019-12-01) and its figure | `nsidc_to_dataframe`, `build_mesh`, `route` | write `dakshin/figures/mesh.json`, `routes.json`, `waypoints.csv`, `sic_points.csv`, `route_map.png` |
| `route_regret.py` | Static plan versus daily re-plan, replayed through observed ice | `plan_route`, `replay`, `sail_daily_replan` | writes `dakshin/figures/route_regret.json`; PolarRoute env |
| `alternatives.py` | Alternative corridors and a two-vessel comparison | `corridors`, `two_vessel_comparison` | writes `alternatives.json`, `vessel_comparison.json` |
| `destination_window.py` | Is the destination cell passable on each day | `main` | writes `dakshin/figures/destination_window.json` |
| `mlflow_backfill.py` | Republishes the numbers in `docs/PROTOTYPE_RESULTS.md` as MLflow runs (it computes nothing) | `backfill` | local MLflow store (gitignored) |
| `test_*.py` | Unit and behavioural tests | | read real files; docstring in `dakshin/demo/test_data.py`: "No fixtures, no synthetic data" |

### 3.2 `dakshin/sim/`, `dakshin/readers/`, `dakshin/demo/`

| File | What it does | Notes |
|---|---|---|
| `sim/router.py` | `VesselModel` (speed and per-distance fuel derating) and `Router` (Dijkstra, 8-connected, arrival-time costs, 6-hour condition slots, land and depth blocking) | The only router that has a time dimension; used on real data via `RealWorld` |
| `sim/world.py` | Assembles `World`: pressure, wind, ice, SST, waves, visibility, bergs, traffic, warnings, from one seed (default 20261207) | Synthetic state; real physics relationships (wind as pressure gradient, waves damped by ice) |
| `sim/fields.py`, `ice.py`, `noise.py`, `hashing.py` | Seeded Fourier noise, atmosphere, ocean, ice-edge model | "Real physics, synthetic initial conditions" (`sim/fields.py` docstring) |
| `sim/bergs.py` | Berg population advected with the tested WDE17 function | Synthetic positions; both catalogue-sized and smaller bergs |
| `sim/bathymetry.py` | Real IBCSO v2 / GEBCO_2020 depth lookup; each 0.05 degree box holds the shallowest source value within it and its eight neighbours (about 5 km buffer, commit `24317da`); NaN outside coverage | Reads `data/bathymetry/ibcso_v2_corridor_0p05.nc` |
| `sim/geo_mask.py` | One land test (even-odd ray casting over the committed coastline rings) | Reads `dakshin/figures/coastline.json` |
| `readers/nemo.py` | `NemoReader(*paths)`: `.field(name)` for `ice_concentration`, `u_current`, `v_current`, `sst`, `ice_thickness`; `.lon`, `.lat` 2-D; `.available()` | Alias lists for classic (`vozocrtx`, `vomecrty`, `votemper`, `ileadfra`, `soicecov`) and CMIP-style (`uo`, `vo`, `thetao`, `tos`, `siconc`) names |
| `demo/app.py` | FastAPI: `/api/summary`, `/api/route`, `/api/cells`, `/api/day/{d}`, `/api/decision`, `/api/workflow`, `/api/alternatives`, `/bridge`, others | Startup refuses to run if any day in the window lacks a satellite file |
| `demo/data.py`, `decision_service.py`, `voyage.py`, `workflow_service.py`, `bridge_api.py` | Loaders for real artifacts; builds a `Decision` from files; voyage state; bridge console API | `decision_service.build` calls `evaluate_all` with `live_sensors=False` and no weather, traffic or wave inputs, so in the demo those gates are UNKNOWN. Real weather is evaluated only in `scripts/real_route_run.py` |

### 3.3 `models/`

| File | What it does |
|---|---|
| `sic_correction/unet.py` | `SICCorrectionUNet(in_channels, base_filters, depth)`: 3-level U-Net with 2 x (3x3 conv, batch-norm, ReLU) blocks, max-pool down, transposed-conv up, skip concatenation, 1x1 head initialised to zero; replicate-pads input to a multiple of 2^depth and crops back; `apply_correction` = clip(base + delta, 0, 1); `count_parameters` |
| `iceberg/drift.py` | WDE17: `GAMMA`, `coriolis_abs`, `harmonic_length`, `lambda_param`, `alpha`, `beta` (both in cancellation-free form), `iceberg_velocity`, `deflection_angle_deg`, `relative_wind_forcing` (R), `critical_length_m` |
| `iceberg/melt.py` | `basal_melt_m_per_day`, `buoyant_convection_m_per_day`, `wave_erosion_m_per_day`, `freshwater_m3_per_day` |
| `iceberg/catalogue.py` | `load_usnic` (SI units, BOM-safe, swaps axes if needed, rejects non-southern latitudes), `fetch_usnic`, `fetch_usnic_archive`, `summarise` |
| `iceberg/regime_report.py` | R across a declared envelope of winds (5, 10, 20, 30 m/s) and currents (0.05, 0.1, 0.3 m/s) for the real catalogue; writes `models/iceberg/regime_report.json` |

### 3.4 `scripts/`

| Script | Purpose | Writes |
|---|---|---|
| `harvest_cmems.sh` | Daily CMEMS cycle harvest (ice, currents, waves), stale-cycle rule, compression | `data/cmems_forecast_archive/cmems_{siconc,cur,wav}_<cycle>.nc`, `data/cmems_harvest.log` |
| `compress_netcdf.py`, `reduce_wav_daily.py` | int16 packing / deflate; 3-hourly waves to daily max | in place |
| `harvest_ecmwf_wind.py` | Latest 00z/12z IFS 10 m wind, steps 0 to 240 h every 6 h, cropped to the box | `data/ecmwf_wind/ecmwf_wind_<date>_<hh>z.nc` |
| `harvest_usnic.sh` | Weekly USNIC CSV, named by the newest "Last Update" | `data/icebergs/archive/AntarcticIcebergs_<yyyymmdd>.csv` |
| `download_nsidc_nrt.py` | NSIDC G10016 v4 NRT daily files and a SHA-256 manifest | `data/nsidc_nrt/` (gitignored) |
| `backfill_cur_analysis.py` | One-off daily analysis currents backfill | `data/cmems_cur_analysis/cmems_cur_analysis_<date>.nc` |
| `subset_bathymetry.py` | IBCSO v2 south of 50 S plus GEBCO_2020 north of it, box-max onto a 0.05 degree grid | `data/bathymetry/ibcso_v2_corridor_0p05.nc` |
| `score_cmems_archive.py` | Persistence versus CMEMS using the model's own later day-0 as truth; flatters CMEMS, a baseline not a skill claim | stdout |
| `realforecast_hindcast.py` | The honest test (section 5c) | `dakshin/figures/realforecast_hindcast.json` |
| `resolution_study.py` | F1, coarsening study | `resolution_study.json`, `resolution_study.png` |
| `berg_hindcast.py`, `berg_resolution.py`, `berg_melt.py` | Berg validation, F3 current coarsening, F4 melt estimate | `berg_hindcast.json`, `berg_resolution.json`, `berg_melt.json` |
| `real_route_run.py` | Router on `RealWorld` plus weather gate | `real_route.json` |
| `pull_checkpoints.sh` | Pull the four checkpoints from the Kaggle run, write `SHA256SUMS`, run the tests and both scorers | checkpoints |
| `verify_claims.py` | Checks 29 quantitative claims against source JSON | stdout |
| `gen_*_drawio.py` | Diagram generators | `docs/*.drawio` |

---

## 4. The grid story

### 4.1 The truth grid

The NSIDC CDR grid is a 25 km south polar stereographic grid, EPSG:3412 (Hughes 1980 ellipsoid, `+proj=stere +lat_0=-90 +lat_ts=-70`; `dakshin/grid.py`). Measured here from a real file (`sic_pss25_20191201_F17_v06r00.nc`): `y` has 332 values starting at 4,337,500 m and decreasing in steps of 25,000 m, `x` has 316 values starting at -3,937,500 m and increasing in steps of 25,000 m, 104,912 cells in all, latitude range -89.84 to -39.36 degrees. Row 0 is therefore the northernmost row. The dimensions 332 x 316 closed an assumption in `docs/ML_ARCHITECTURE.md` section 1.3 (the stale backlog line in `docs/backlog.md` that still says "asserted from memory, not verified" predates this).

A cell is 625 km2 (25 km x 25 km). `features.iiee_km2` uses that constant for every cell. In a polar stereographic projection with a standard parallel at 70 S the true area of a cell varies with latitude, so the constant is an approximation; the repository does not quantify the error, and neither does this document.

### 4.2 Why the truth is never resampled

The rule is in `dakshin/grid.py` and ADR-024: the model field is regridded onto the truth grid, never the reverse. Resampling the field you score against creates ice-edge artefacts that cannot be told from model error, and IIEE is measured on that field.

### 4.3 What the regridder actually does

The docstring speaks of area-averaging. The implementation is this. For every source point (a GLO12 cell centre) it transforms lon/lat to EPSG:3412, converts to a target row and column by rounding (`np.rint((x - x0) / dx)`), and keeps those inside the grid. At call time it sums the finite source values per target cell with `np.bincount` and divides by the finite count. Target cells that receive no source point are NaN, not zero (an empty cell is unknown, not ice-free). So it is an unweighted mean of source cell centres falling in each target cell. It is not a conservative remap that weights by overlap area, which ADR-024 and `docs/ML_ARCHITECTURE.md` section 4.2 describe in words. For a source about 9 km wide and a target 25 km wide the difference is small away from edges; it has not been measured.

Why a mean rather than bilinear: the source is finer than the target, so bilinear sampling would discard most of the source cells and would not preserve ice area (`grid.py` docstring).

Measured here with the 2026-11-19 cycle (`GlorysToNsidcRegridder` on the 277 x 961 GLO12 box): 14.7% of the NSIDC grid is covered by the harvest box (`coverage()` returned 0.14686); source points per covered target cell: minimum 1, median 16, maximum 41; one regridded field has 11,250 finite cells with values 0.0 to 0.9964. Everything outside the box is NaN and is zero-filled before the network (section 5c).

### 4.4 The source grids

GLO12 harvest: regular lat/lon at 1/12 degree, 277 latitudes (78 S to 55 S) by 961 longitudes (0 to 80 E), 10 daily steps per cycle (measured here with `xarray` on `data/cmems_forecast_archive/cmems_siconc_2026-11-19.nc`). Files carry four variables: `siconc`, `sithick`, `usi`, `vsi`.

Training background (GLORYS12 reanalysis) was subset to -5 to 85 E, -80 to -48 S in the notebook (`dakshin/kaggle/make_notebook.py`), a larger box than the scoring box (0 to 80 E, 55 to 78 S).

Router lattice: regular lat/lon, default spacing 0.55 degrees latitude by 0.9 degrees longitude (`dakshin/sim/router.py`). Bathymetry: 0.05 degree boxes, lon 0 to 90 E, lat 78 S to 30 S, IBCSO v2 ice-surface grid south of 50 S and GEBCO_2020 north of it (`dakshin/sim/bathymetry.py`, `scripts/subset_bathymetry.py`). The ice-surface grid is used rather than the bed grid so that an ice shelf reads as positive elevation and blocks the router like land; the bed grid would show hundreds of metres of "water" under the shelf.

### 4.5 How curvilinear NEMO coordinates plug in

`GlorysToNsidcRegridder.__init__` checks `source_lat.ndim`. If 2-D (as for NEMO's `nav_lon` and `nav_lat`) the arrays are used as given; if 1-D they are meshed. So `NemoReader.lon`/`.lat` pass straight in:

```python
from dakshin.readers.nemo import NemoReader
from dakshin.grid import GlorysToNsidcRegridder
r = NemoReader("grid_T.nc", "icemod.nc")            # NOT run on real NEMO output
rg = GlorysToNsidcRegridder(nsidc_template_ds, r.lat, r.lon)
sic_on_nsidc = rg(r.field("ice_concentration"))      # (332, 316), NaN outside the domain
```

Limits to state before a NEMO specialist does. `NemoReader` reads only the first time record and the top level of each variable. It does no C-grid destaggering: `uo` lives on U-points and `vo` on V-points in NEMO and is returned as stored. It does no rotation of grid-relative velocity components to east/north, which matters on a rotated or tripolar grid. Fill values above 1e19 in magnitude become NaN; zeros are kept as zeros. Its tests (`dakshin/readers/test_nemo.py`, 4 tests) use synthetic files in the documented layout, because no small open sample file ships with NEMO. The name ANHA appears in the repository only as an example of a regional NEMO configuration that could be run at several resolutions (`docs/RESOLUTION_STUDY.md`, `scripts/resolution_study.py`, `dakshin/readers/nemo.py`); the repository gives no domain for it. If ANHA is a Northern Hemisphere (Arctic and North Atlantic) domain, as the name suggests, then only the reader and the metrics transfer to it; the south-polar regridder and the 0 to 80 E corridor do not. Verify with the professor rather than assume.

---

## 5. The data pipelines

### 5a. Daily harvest

Scheduled job: `.github/workflows/cmems-harvest.yml`, cron `23 12 * * *`, `23 17 * * *` and `23 21 * * *` UTC, plus manual dispatch with an optional `cycle_date`. It installs `copernicusmarine`, `xarray`, `netCDF4`, logs in (three attempts), runs `scripts/harvest_cmems.sh`, verifies the file exists and exceeds 1,000,000 bytes, then commits `data/cmems_forecast_archive` and `data/cmems_harvest.log` with up to three push attempts, rebasing in between.

Why those times (workflow comment): GitHub starts scheduled runs late (observed 10:38, 11:05, 10:40 UTC for a 06:00 cron), never schedule on the hour, run more than once because the already-have guard makes repeats free, and keep every slot after 12:00 UTC because the CMEMS product manual guarantees the daily bulletin only by 12:00 UTC (CMEMS-GLO-PUM-001-024, issue 2.4, as cited in the workflow). The script names its output from the wall clock, so a run before the bulletin lands would store the previous day's forecast under today's filename and the already-have guard would then block the correct capture. A missed day cannot be recovered: CMEMS overwrites each bulletin with the next.

What the script pulls, for one cycle date D (box lon 0 to 80, lat -78 to -55, from D 00:00 to D+10 days):

| Product | Dataset ID | Variables | Output file | Steps |
|---|---|---|---|---|
| Ice | `cmems_mod_glo_phy_anfc_0.083deg_P1D-m` (GLOBAL_ANALYSISFORECAST_PHY_001_024) | `siconc`, `sithick`, `usi`, `vsi` | `cmems_siconc_<D>.nc` | 10 daily |
| Currents | `cmems_mod_glo_phy-cur_anfc_0.083deg_P1D-m` | `uo`, `vo`, depth 0 to 1 m (top level, 0.494 m) | `cmems_cur_<D>.nc` | 10 daily |
| Waves | `cmems_mod_glo_wav_anfc_0.083deg_PT3H-i` (GLOBAL_ANALYSISFORECAST_WAV_001_027) | `VHM0`, `VMDR`, reduced to daily maximum `VHM0_dmax` (and `VMDR` at the step of the maximum) by `scripts/reduce_wav_daily.py` | `cmems_wav_<D>.nc` | 10 daily |

The stale-cycle rule. A real cycle has exactly 10 daily time steps, the cycle date plus nine forecast days (`EXPECTED_DAYS=10`). If the run is clock-dated (no manual `CYCLE_DATE`) and the hour is before 12 UTC, the cycle is filed under yesterday. After the download the script counts time steps; a file that is not exactly 10 steps is deleted, the status is reported as `not_published`, and a later run retries. Currents and waves are fetched only after the ice cycle is accepted, with the same length check, and their failures never fail the harvest (the runner is discarded after the job, so a late red would lose the already saved ice file). A manually typed date is treated as a deliberate back-fill and is not checked, with the caveat in the script that the analysis for a past date is served but the forecast as issued is gone.

Why `data/cmems_forecast_archive/KNOWN_STALE.md` exists. Found on 2026-11-18 by comparing every archived cycle with the one before. Four files hold the previous day's forecast with its first day cut off (9 steps, `siconc` identical on all 9 shared dates, maximum difference 0.0000): 2026-09-20, 2026-10-11, 2026-11-10, 2026-11-17. Two came from runs that started after midnight UTC (the clock named the file for the next day), two from runs after 12:00 UTC when Copernicus had not yet published (both Sundays). The real forecasts for those four dates were never saved and cannot be recovered. The rule was added after the fact. Consequence for scoring: those four cycles must not be used (their "day 0" is a day-old forecast), and every scorer applies the same 10-step test (`scripts/realforecast_hindcast.py::clean_cycles`, `scripts/score_cmems_archive.py`). Measured here: 83 `cmems_siconc_*.nc` files, 79 clean, 4 stale.

Compression. `copernicusmarine subset` writes uncompressed NetCDF, 42.62 MB per cycle (`scripts/compress_netcdf.py`). The harvest packs `siconc`, `sithick`, `usi`, `vsi` as int16 with deflate and shuffle: the log line for 2026-11-21 reads "42.62 MB -> 4.44 MB (9.6x smaller, int16 packed)" (`data/cmems_harvest.log`); the script's stated maximum error is 1.7e-5 for `siconc` and 3.3e-4 m for `sithick`. `uo`/`vo` are stored as lossless float32 deflate.

Other feeds, and what the repository does and does not schedule.

| Feed | Script | Cadence needed | Scheduled in the repository |
|---|---|---|---|
| ECMWF IFS 10 m wind (CC BY 4.0) | `scripts/harvest_ecmwf_wind.py` | open data keeps only the last ~12 runs (2 to 3 days), so daily | No. Only `cmems-harvest.yml` exists. One wind file is committed (`data/ecmwf_wind/ecmwf_wind_2026-11-21_00z.nc`) |
| USNIC Antarctic icebergs | `scripts/harvest_usnic.sh`, or `models/iceberg/catalogue.py <start> <end>` to back-fill from the archive back to 2014-11-07 | weekly | No. 14 weekly files are committed (2026-08-20 to 2026-11-20) |
| NSIDC NRT G10016 v4 | `scripts/download_nsidc_nrt.py` | the archive keeps about 3 months, so days roll off | No. 89 files on disk (2026-08-24 to 2026-11-20), gitignored |
| CMEMS surface SST for berg melt | no script | | `data/cmems_forecast_archive/cmems_sst_2026-11-21.nc` is committed and `scripts/berg_melt.py` reads it, but nothing in the repository produces it; its provenance is undocumented |
| Analysis currents (for the berg hindcast) | `scripts/backfill_cur_analysis.py` | one-off | 82 daily files committed (2026-08-31 onward) |

Consequences: `scripts/berg_melt.py` and `scripts/real_route_run.py` are single-cycle results (2026-11-21), because only one wind, one SST and one wave-and-current set for that date exist. `docs/CURRENT_STATE.md` describes the wind harvest as "daily"; in the repository it is a script someone must run.

### 5b. Training pipeline

Data and code: `dakshin/kaggle/isih_train.ipynb`, generated by `dakshin/kaggle/make_notebook.py`. File and checkpoint names keep the historical prefix `isih_`; do not rename them (`dakshin/model_io.py`, `scripts/pull_checkpoints.sh`).

Truth. NSIDC CDR G02202 v6 south daily files, 25 km, F17 SSMIS era, years 2019 and 2020 (`YEARS = [2019, 2020]` in the notebook), downloaded by 8 threads from `https://noaadata.apps.nsidc.org/NOAA/G02202_V6/south/daily`. No authentication. Values outside 0 to 1 become NaN.

Background. GLORYS12 reanalysis `cmems_mod_glo_phy_my_0.083deg_P1D-m`, variable `siconc`, box -5 to 85 E, -80 to -48 S, regridded onto the NSIDC grid by `GlorysToNsidcRegridder` (section 4.3). Dates present in both are intersected. NaN is filled with 0 for the network; a validity mask `isfinite(background) & isfinite(truth)` marks where the loss counts.

An alignment sanity check runs before anything is trained: correlation between background and truth must exceed 0.5 or the notebook asserts.

The 12 channels (`dakshin/features.py::build_channels`), for forecast origin `t` and lead `L`:

| Channel | Content |
|---|---|
| 0 | background (GLORYS12) valid at the target date `t + L` |
| 1 to 7 | observed SIC at `t`, `t-1`, ..., `t-6` (channel `k` holds `observed[t - k + 1]`) |
| 8 | innovation: `background[t] - observed[t]` |
| 9, 10 | sin and cos of 2 pi doy/365.25 of the target date |
| 11 | validity mask at `t` |

The header comment of `features.py` says channels 1 to 7 are `t-1 ... t-7` and the innovation uses `observed(t-1)`. The code does otherwise (newest observation index `t`); the docstring of `build_channels_operational` ("index 0 = day t, index 6 = day t-6") agrees with the code. Document the code.

A sample is built only where the 7-day look-back is genuinely consecutive and the gap to the target is exactly `L` days; a hole in the record is never treated as history.

Split and why. Samples are ordered by target date and cut 70% / 15% / 15% by index: train, validation (used only to choose the epoch), test (scored once). Time ordering is mandatory because sea ice barely changes overnight; a random split puts adjacent days on both sides and yields a spectacular, meaningless score (`docs/PROTOTYPE_RESULTS.md`). An earlier run reported +27% by selecting the best of 30 epochs on the set it then reported; that number was inflated and is not used (same file). There is no embargo between the three blocks, so input windows and targets at the boundaries share days across a cut; nothing in the repository measures how much this matters.

Why seed 0. `torch.manual_seed(0)` is called before the model is built at every lead, "same init at every lead, so leads are comparable". It fixes initialisation; it does not make the run bit-reproducible (GPU non-determinism, mixed precision).

Why a residual. The output of the network is `delta`, and the prediction is `clip(background + delta, 0, 1)`. The final 1x1 convolution is zero-initialised (`unet.py`), so an untrained model reproduces the background exactly; the floor is the background's skill, not zero. Model: 3 levels, base filters 32, 12 input channels, 1,929,601 parameters (measured here with `count_parameters`; `docs/PROTOTYPE_RESULTS.md` quotes the same). The unet.py defaults (19 channels, 40 filters, 3,015,481 parameters) are the production design, not the prototype.

Optimisation: masked MSE on the corrected field, Adam at 1e-3, `ReduceLROnPlateau` (factor 0.5, patience 3), mixed precision on GPU, batch size 8, at most 60 epochs, early stop after 12 epochs without validation improvement, best-validation checkpoint kept. One model per lead in {1, 3, 5, 7}. Baselines are scored before training at each lead so the bar is fixed first: raw background, persistence (the newest observation, channel 1), background plus a constant offset, background plus a per-pixel mean bias map fitted on train.

Why same-day correction is not a task: measured over full-year 2020, persistence from yesterday scores RMSE 0.0359 for the same day, better than any correction of a background field (`features.py` docstring). The notebook therefore studies leads 1, 3, 5, 7 days.

Training-time results (test slice, last 15% of 2019 to 2020, melt season), from `docs/PROTOTYPE_RESULTS.md`:

| Lead | Model | Persistence | background + pixel bias | Raw GLORYS12 |
|---|---|---|---|---|
| 1 d | 0.0465 | 0.0570 | 0.1461 | 0.1630 |
| 3 d | 0.0720 | 0.0958 | 0.1461 | 0.1630 |
| 5 d | 0.0938 | 0.1204 | 0.1468 | 0.1637 |
| 7 d | 0.0968 | 0.1395 | 0.1468 | 0.1637 |

Read these as an upper bound on forecast skill, not a measurement (section 5c). They also cannot currently be reproduced: the original 2026-08-31 checkpoints were never in Kaggle's output store, and the saved notebook's training cell was typed as markdown so batch runs trained nothing (`docs/CURRENT_STATE.md`). A re-run is in progress.

The no-background ablation (zero channel 0, retrain at lead 3) exists as a notebook cell and as a stated next step; no result is recorded (`docs/PROTOTYPE_RESULTS.md`, "Not yet run").

### 5c. The real-forecast hindcast

`scripts/realforecast_hindcast.py`. The question: if the ship had used the real CMEMS forecast issued on day `t`, how would raw CMEMS, persistence and (once available) the U-Net have scored against the satellite on day `t + L`?

Procedure. For each clean cycle `t` and lead `L` in {1, 3, 5, 7}: forecast step `L` of the cycle, regridded to the NSIDC grid, is "raw CMEMS"; the NRT observation at `t` is persistence; truth is the QA-masked NRT observation at `t + L`. History needs the 7 days `t-6 ... t` to be present. Scoring uses cells inside the box 0 to 80 E, 55 to 78 S where truth and forecast are finite, pools squared error over all cycles (RMSE) and averages IIEE at the 15% threshold per cycle. Truth NaNs are zero-filled in the squared-error term and excluded by the mask. Run once; no tuning on this set.

What `build_channels_operational` changes relative to training:

| Item | Training (`build_channels`) | Operational (`build_channels_operational`) |
|---|---|---|
| Channel 0 | GLORYS12 reanalysis valid at `t + L` | CMEMS forecast issued at `t`, valid at `t + L` |
| Channel 8 | `background[t] - observed[t]` with reanalysis at `t` | day-0 field of the same forecast cycle minus `observed[t]` |
| Observations | not QA-masked in the notebook (spillover zeros sit in targets and history) | QA-masked by `ice_quality.load_sic` (suspect cells NaN, then zero-filled) |
| Truth sensor | F17 SSMIS (G02202 v6) | AMSR2 (G10016 v4 NRT, file tag `am2`, since 2025-01-01 per `scripts/download_nsidc_nrt.py`) |
| Region | -5 to 85 E, -80 to -48 S | 0 to 80 E, 55 to 78 S (14.7% of the grid; rest zero-filled) |
| Valid mask (channel 11) | from the paired training mask | `isfinite(analysis_t) & isfinite(obs_t)` |

Why this is the honest operational test. A forecast issued at `t` cannot contain information from after `t`; the function takes only things knowable on day `t` and the docstring says nothing after `t` can enter by construction. The reanalysis in training had assimilated observations near the target date, which a real forecast has not.

The leakage question and its answer. The sharpest question is whether training channel 0 leaked the target. `docs/PROTOTYPE_RESULTS.md` caveat 1 answers it in the affirmative in part, and withdraws an earlier defence. The withdrawn defence ("if GLORYS12 contained the answer its own RMSE would be near zero, not 0.163") does not follow, because 0.163 measures grid, algorithm and ice-model mismatch between a 1/12 degree model field and a 25 km passive-microwave product; it is a bias term. The positive evidence of leakage is the flat raw-GLORYS12 error across lead (0.1630 at 1 d, 0.1637 at 7 d, essentially no growth), which is what a field that has seen the target looks like, together with the fact that channel 0 is the reanalysis at `t + L` and channel 8 is the reanalysis at `t`, whose difference (the assimilated tendency) is a linear combination the first convolution can form. Therefore the training-time table is an upper bound on forecast skill. The test that settles the matter is the hindcast on real forecast cycles (this section), plus the not-yet-run ablation.

Results already in hand (raw CMEMS and persistence only), `dakshin/figures/realforecast_hindcast.json` (generated 2026-11-21, `"model": null`):

| Lead | n cycles | RMSE raw CMEMS | RMSE persistence | IIEE raw CMEMS (km2) | IIEE persistence (km2) |
|---|---|---|---|---|---|
| 1 d | 76 | 0.10199 | 0.11977 | 195,058 | 187,706 |
| 3 d | 75 | 0.10479 | 0.14391 | 194,575 | 277,167 |
| 5 d | 74 | 0.10981 | 0.15508 | 200,203 | 319,189 |
| 7 d | 72 | 0.11530 | 0.16414 | 210,200 | 353,255 |
| U-Net (all columns) | | training re-run in progress | | training re-run in progress | |

Reading it. By RMSE raw CMEMS beats persistence at every lead. By IIEE persistence is slightly better at lead 1 (187,706 against 195,058 km2) and CMEMS is clearly better from lead 3. "Raw CMEMS beats persistence at all leads" (`docs/CURRENT_STATE.md`) is therefore true for RMSE only. Persistence IIEE grows with lead, as it should; `docs/RESOLUTION_STUDY.md` gives a persistence IIEE of "211.7" at lead 3 with the note "decays with lead", which the JSON does not support (277,167).

Reproduction delta, measured here today by running the scorer in a scratch copy: leads 3, 5, 7 reproduce the committed JSON exactly; lead 1 gives n = 77 (the cycle of 2026-11-19 is now scorable), RMSE 0.10219 for CMEMS and 0.11914 for persistence, IIEE 196,031 and 186,997 km2. The committed JSON has n = 76. Quote the committed figures and note the delta, or regenerate and commit.

What the scoring cannot tell you, and the caveats carried in the JSON (`CAVEATS` in the script): the sensor change from F17 to AMSR2; corridor only; one spring season (about 76 cycles, strongly autocorrelated, so the effective sample is far smaller than the count); the assumption that the day-`t` satellite file is in hand on day `t`; four stale cycles excluded. Further train-versus-serve differences that no document lists: persistence takes the QA-masked day-`t` observation with NaN zero-filled, which slightly handicaps persistence where the day-`t` cell is suspect (unquantified). ADR-027 makes IIEE and CRPS the build-blocking acceptance gate, but the scorer computes RMSE and IIEE only, so that gate cannot yet be evaluated whatever the U-Net returns.

### 5d. Iceberg pipeline

1. Catalogue. USNIC weekly CSV (`https://usicecenter.gov/File/DownloadCurrent?pId=134`; the archive back to 2014-11-07 via `fetch_usnic_archive`). USNIC names bergs of at least 20 sq nautical miles or 10 nautical miles on the longest axis, about 18.5 km. `load_usnic` converts nautical miles to metres, orders length and width, derives the harmonic length S = LW/(L+W), and raises on malformed or non-southern data; no synthetic bergs are ever generated. The last committed issue is 2026-11-20 (33 bergs in the 2026-08-27 issue summarised in `models/iceberg/regime_report.json`; largest D15A, 3,037.47 km2).
2. Velocity. `models/iceberg/drift.iceberg_velocity`: current plus a wind-driven term, section 2 of `PHYSICS_AND_PAPERS.md`. In the forecast, wind is set to zero (the wind harvest was added later and is not wired in); each track records R computed with an assumed 10 m/s wind and the model current speed at the start.
3. Currents. `CurrentField.from_files` reads the daily `uo`, `vo` files, takes the top level, treats each daily mean as valid at 12:00 UTC, interpolates bilinearly in space (NaN if any of the four neighbours is NaN: near a coast no velocity is invented) and linearly in time, using the nearest day outside the first and last centres.
4. Integration. `forecast_track`: midpoint (RK2) with a 1 h step. k1 from the position, a half step to the midpoint (time `t + h/2`), k2 there, then the full step with k2. Positions in degrees use 111,195 m per degree of latitude and a cosine-of-latitude factor for longitude. A step that lands on NaN current stops the track and sets status "grounded or unknown": motion is never invented. A 9-day track has 217 hourly positions (measured here for D37 from the 2026-11-21 cycle, status ok, 17.2 km net displacement).
5. Validation. `scripts/berg_hindcast.py`: for every consecutive pair of USNIC fixes of a berg inside the 0 to 80 E, 55 to 78 S box, within the period covered by the analysis currents (2026-08-31 to 2026-11-20), integrate from fix to fix on the analysis currents and compare the landing point with the later fix; the baseline is persistence (the berg did not move). 88 segments from 8 bergs (B09G, C18B, C18C, C39, D15C, D15D, D23, D37). Results in `dakshin/figures/berg_hindcast.json`: 81 segments with status ok, 7 "grounded or unknown"; median error 4.35 km/day for the model against 0.0 for persistence; mean 5.06 against 0.43; of the 81, 68 stationary (persistence displacement of 3 km or less between fixes) and 13 moving; moving median 6.01 km/day for the model against 2.45 for persistence; stationary-segment model median 4.26 km/day. The finding: most corridor giants are grounded, and a current-advection model without grounding detection advects anchored ice. The site's forecast-cone growth rate was changed to the measured 4.35 km/day (`uncertainty_radius_km_per_day`), replacing an unverified 12 km/day.
6. Coarse-current experiment (F3), `dakshin/figures/berg_resolution.json`: with currents block-averaged to 1/4 degree the median error falls to 4.07 km/day (86 ok, 2 flagged), at 1 degree to 3.49 (88 ok, 0 flagged), against 4.35 at 1/12 degree (81 ok, 7 flagged); on moving bergs 6.01, 5.93, 5.06. The explanation offered in `docs/RESOLUTION_STUDY.md`: resolved eddy velocity advects ice that is actually grounded, so smoothing drifts the forecast toward "does not move", which happens to be right for this sample. On the 13 moving segments the gap narrows but coarse still wins slightly; that sub-sample is too small to resolve an eddy effect at weekly fix cadence and few-kilometre USNIC accuracy.
7. Melt estimate (F4), `scripts/berg_melt.py`, `dakshin/figures/berg_melt.json`: for the 8 bergs in the box, the 9-day track on the 2026-11-21 forecast currents with SST and daily-max Hs sampled at the nearest grid cell, freshwater input in m3/day with an assumed 250 m thickness. Mean daily values range from 157,451 (C18C) to 1,913,104 (D15C) m3/day. Labelled an estimate throughout (section 3 of `PHYSICS_AND_PAPERS.md`).

Wind is a neglected term. The regime check in `models/iceberg/regime_report.json` sweeps wind and current speeds because observed forcing at each berg is not held. In the segment table of the hindcast the per-segment R (computed with an assumed 10 m/s wind and the berg's model current speed) has median 0.25, minimum 0.037, maximum 1.73 over the 88 segments (measured here from `berg_hindcast.json`), with 81 of 88 above the 0.1 line the code treats as current-dominated and one above 1. The docstrings of `berg_forecast.py` ("the wind term is ~1% of drift") and `scripts/berg_resolution.py` ("R << 1 in every segment") do not agree with that. The honest statement is that R scales as 1/|v_w|, so slow or near-zero model currents at grounded bergs inflate it, and the wind-free simplification drops a term of order a quarter of the current speed in this sample. Section 2 of `PHYSICS_AND_PAPERS.md` gives the envelope.

### 5e. Routing and gates

The contract. `RealWorld(cycle)` exposes `sample(lat, lon, t)` where `t` is days since the cycle date, returning a dict with `sic`, `hs`, `wind_u`, `wind_v`, `wind_ms` and bookkeeping counters. It is the same call signature as the synthetic `World.sample`, so the `Router` runs unchanged on real data. Rules enforced in `real_world.py`:

- Daily fields: `t` is rounded to the nearest forecast day and clamped to the 10-day horizon; `beyond_horizon` reports when the clamp fired.
- Bilinear interpolation, NaN outside the box or next to NaN.
- Inside the box, a cell with no ice value (under-shelf or model land sliver) is UNKNOWN, treated as impassable (`sic = 1.0`) and counted in `sic_unknown_impassable`; never as open water.
- The wave model leaves `VHM0` NaN under ice. Where `sic > 0.15` waves are set to 0.0 (swell is damped by ice) and counted in `hs_filled_ice`. Coastal slivers with no wave cell but open ocean are filled with the day's worst wave in the box so missing data can only over-cost a leg, counted in `hs_filled_coastal_worstcase`.
- No visibility field exists in any harvested data, so none is returned and the weather gate lists visibility as unassessed.
- Wind: the 6-hourly IFS step nearest `day * 24 + 12` hours; the IFS latitude axis is descending and is reversed before interpolation.

The router (`dakshin/sim/router.py`). Dijkstra on a lat/lon lattice, 8-connected. For each node expansion the elapsed hours since departure select a 6-hour slot (`slot = int((depart_t * 24 + t_here) // 6)`), the world is sampled once per slot (cached), and the cost of moving to a neighbour uses the ice and waves valid at that arrival time. That is the time dimension PolarRoute lacks. Rules: a neighbour is skipped if it is land (`on_land`), shallower than the vessel's `min_depth_m` (IBCSO v2 depth, 20 m for Golovnin, `NaN < x` is False so no data is not shallow, it is unknown), or if its SIC exceeds the ice limit (a hard constraint, never priced). The vessel model: speed is `max_speed * (1 - 0.92 * (sic/limit)^1.35)` times a sea factor `1 - 0.45 * clip((Hs - 4)/5, 0, 1)`, floored at 2 kn, zero above the limit; defaults 16.4 kn, ice limit 0.80. The objective is time or fuel; fuel is expressed per distance, `0.000120 v^2 + 0.0200 sic^1.5 + 0.00035 Hs^2` tonnes per km, scaled so a calm 16.4 kn passage burns about 24 t/day, and is explicitly relative only. Stations sit ashore: the node nearest Bharati is on the ice sheet (221 m above sea level in IBCSO), so the endpoint snaps to the closest navigable nodes, and `arrival_offset_km` in the result reports how far short the ship stops. `critical_ice_limit` steps the limit down from 0.85 to 0.30 and returns where the destination stops being reachable, so the output does not rest on one invented threshold.

The real run, `scripts/real_route_run.py`, `dakshin/figures/real_route.json` (cycle 2026-11-21): start (-55.5, 45.0), goal Bharati (-69.4, 76.2), lattice lat -70.6 to -55.0, lon 13.0 to 79.5. At the 80% limit the approach is closed (`approach_closed_at_ice_limit: true`); the closest reachable cell is 50.6 km from Bharati, and the route to it takes 5.55 days over 45 legs with worst ice 0.723, worst Hs 4.77 m, worst wind 14.9 m/s; the weather gate returns FAIL ("waves 4.77 m exceed the assumed 3.0 m limit; wind 14.9 m/s in Beaufort 7"). The 5.55 days is the segment south of 55 S to the closest reachable point, not a voyage time: no real wave or wind data exists north of 55 S.

PolarRoute alternatively. The September prototype's published corridors use PolarRoute 1.1.11 and meshiphi 2.3.1 (British Antarctic Survey, MIT), in a separate Python 3.11 environment (`dakshin/make_route_figure.py` docstring), and are not run in this study environment. See section 7.

Route health from gates (`dakshin/decision.py`). Health is the worst level over the gates, never a score: FAIL gives CRITICAL if `fails_in_hours > 0` (ahead of the ship) and INVALID otherwise; MARGINAL and UNKNOWN both give DEGRADED; all PASS gives VALID. The binding gates are those at the worst level, ordered FAIL, MARGINAL, UNKNOWN. Missing evidence therefore caps health at DEGRADED, by design (a false "all clear" is the expensive error).

---

## 6. The nine gates

Order follows `dakshin/decision.py::GATES`: capability, chart, ice, weather, traffic, logistics, communications, contingency, execution.

| Gate | Question | Evidence it uses | Possible states in code | Can it PASS? |
|---|---|---|---|---|
| capability | May this ship be here, legally and physically? | Vessel config; the force limit 96,634.5 is carried over from another hull | UNKNOWN only | Never. No Polar Ship Certificate or PWOM is held, and inventing vessel thresholds is forbidden |
| chart | Is there water under the keel along the route? | IBCSO v2 (south of 50 S) and GEBCO_2020 (north) depth at each route point vs the vessel `min_depth` (20 m) | FAIL if any known point is shallower; MARGINAL otherwise; UNKNOWN if no points lie in coverage or the mesh has no bathymetry | Never. IBCSO is a scientific compilation, not an official ENC; `CHART_NOT_ENC` is the stated reason |
| ice | Will expected ice exceed the working limit? | Worst SIC on the route vs 80% | FAIL / MARGINAL / PASS | Yes. MARGINAL band is 7.4 points: one median standard deviation of the CDR retrieval across the 70 to 90% band (`cdr_seaice_conc_stdev`, December 2019: median 7.4, mean 8.0, p90 11.7). The limit is flagged as assumed because ice class is defined by thickness, not concentration |
| weather | Will wind, waves or visibility make the corridor unsafe? | Worst `VHM0` daily max and worst 10 m wind on the route at arrival times | FAIL if Hs > 3.0 m or wind >= 17.2 m/s (Beaufort 8); MARGINAL within 0.5 m or wind >= 13.9 m/s (Beaufort 7); UNKNOWN with no data | Yes, but visibility is always listed as unassessed. Limits are assumptions (3.0 m is the PolarRoute example `max_wave`), not this hull's PWOM |
| traffic | Conflict with other vessels? | Ship AIS receiver via `ais_feed.py`; bands 2 nm (FAIL) and 5 nm (MARGINAL) are assumptions, not COLREGS distances | UNKNOWN with no live feed | Only with a live feed. Shore aggregators reach about 40 nm and are empty in the Southern Ocean, and satellite AIS is paid |
| logistics | Will the track meet the station's operating window? | Destination-cell passability from the daily destination window | PASS / FAIL, UNKNOWN if the destination was never scored (not "closed") | Yes |
| communications | Can the ship get warnings and coordinate? | would need GMDSS/satcom link-budget model | UNKNOWN only | Never in code |
| contingency | If the route closes ahead, where do we go? | Number of computed alternative corridors | FAIL (0), MARGINAL (1), PASS (2 or more) | Yes |
| execution | Are observations consistent with what was approved? | Live bridge sensors | UNKNOWN; PASS only if `live_sensors=True` | Only if the flag is set; the demo always passes `live_sensors=False` |

So three gates can never PASS in the code as written (capability, chart, communications), two more can PASS only with live data the repository does not have (traffic, execution), and four can be evaluated from data held (ice, weather, logistics, contingency, with chart returning a depth-based FAIL or MARGINAL). The header docstring of `gates.py` ("of the nine gates we can evaluate four") predates the weather and traffic gates and the chart upgrade; the table above is what the code does.

The chart gate has a history worth knowing. The first claim of "8.6 days Cape Town to Bharati" was withdrawn on 2026-11-21 because the route's final point is Bharati station, which IBCSO v2 places above sea level (91 m in the withdrawal note). The same day the published route was regenerated on the same 1 December 2019 ice with real IBCSO v2 / GEBCO_2020 depth in the mesh: 8.66 days, arriving 16 km off the station, never over water shallower than 89 m (`docs/TRUE_CLAIMS.md` claim 1.11, `docs/PROTOTYPE_RESULTS.md` section 4, commit `13861d9`). It is a steaming-time lower bound with no sea-state penalty (PolarRoute defines `wave_resistance()` and never calls it). The route-regret table (static plan 8.61 d, daily re-plan 9.00 d) was computed on meshes without depth and has not been re-run.

---

## 7. Two routing engines, and why

| | PolarRoute 1.1.11 + meshiphi 2.3.1 | `dakshin/sim/router.py` |
|---|---|---|
| Role | September prototype: published corridors, route-regret, alternatives, destination window | Real-forecast run: time-dependent routing on `RealWorld` |
| Time dimension | None (frozen mesh; verified by source grep, `docs/backlog.md`) | Arrival-time costs on 6-hour slots |
| Cost model | `SDA` performance model; fuel polynomial fitted to RRS Sir David Attenborough; `wave_resistance()` dead code | Simple derating curve; fuel per distance; stated not to be a hull model |
| Environment | Python 3.11 only, separate env | Same environment as the rest |
| Mesh | Non-uniform adaptive, meshiphi | Regular lat/lon lattice, 0.55 x 0.9 degrees |
| Run here | Not run (no PolarRoute environment in this study sandbox) | Run, section 10 |

The choice was ADR-009 (wrap rather than reimplement) for the prototype, and the in-house router exists because PolarRoute cannot consume a forecast (`dakshin/sim/router.py` docstring, `docs/TRUE_CLAIMS.md` 2.3).

---

## 8. What is real and what is synthetic

Real, and on disk: every satellite and model field used for any number in section 5 and in `README.md`; USNIC positions; IBCSO/GEBCO depth; the Natural Earth coastline; the Antarctic Treaty protected-area register; ECMWF wind (one cycle).

Synthetic and labelled so: `dakshin/sim/` generates a seeded world (default seed 20261207) of pressure, wind, ice edge, SST, waves, visibility, berg population, traffic and warnings. The model is "real physics, synthetic state": wind is the gradient of the pressure field, waves grow from wind and are damped by ice, fog forms where warm air meets cold water, and the ice edge moves because the modelled wind pushed it. It exists so the bridge console and the router tests have a full environment to exercise, and the console page says "SYNTHETIC ENVIRONMENT". It is not used for any reported result, and `RealWorld` replaces it for real-data runs. Two further items are described as simulations in `dakshin/demo/app.py` ("Baymax Mode and the local-LLM assistant"). The routes under `dakshin/sim/` use the real depth lookup and real coastline for land and depth blocking.

The other places where a number is not measured: router ice thickness and density are the literature lookup table inside meshiphi (ADR-013); the 80% working ice limit, 3.0 m wave limit and traffic bands are assumptions stated as such in code and output; melt thickness is assumed at 250 m.

---

## 9. Data on disk: committed or not

| Data | Location | Committed? | Re-fetch |
|---|---|---|---|
| CMEMS forecast cycles (ice, plus one cur, wav, sst set) | `data/cmems_forecast_archive/` (87 files: 83 `siconc`, `KNOWN_STALE.md`, `cmems_cur_2026-11-21.nc`, `cmems_wav_2026-11-21.nc`, `cmems_sst_2026-11-21.nc`) | Yes | Cannot be re-fetched: forecasts as issued are gone |
| Analysis currents | `data/cmems_cur_analysis/` (82 files) | Yes | `scripts/backfill_cur_analysis.py` |
| ECMWF wind | `data/ecmwf_wind/` (1 file) | Yes | cannot, beyond 2 to 3 days |
| USNIC | `data/icebergs/archive/` (14 weekly files) and `usnic_antarctic_20260902.csv` | Yes | `catalogue.fetch_usnic_archive` |
| Bathymetry subset | `data/bathymetry/ibcso_v2_corridor_0p05.nc` | Yes (`raw/` gitignored) | `scripts/subset_bathymetry.py` |
| NSIDC NRT G10016 v4 | `data/nsidc_nrt/` (89 files) | No (gitignored; `MANIFEST.sha256` is untracked with it) | `scripts/download_nsidc_nrt.py`, only the last ~3 months |
| NSIDC G02202 v6, 2018 to 2020 | `dakshin/data/nsidc_sic/` (1,096 files) | No | `python dakshin/download_nsidc.py --start-year 2018 --end-year 2020` |
| Checkpoints | `models/sic_correction/checkpoints/` | Not yet (the directory does not exist) | training re-run in progress |

A fresh clone therefore lacks the NRT truth and the 2018 to 2020 archive: the hindcast, the QA audit, the demo's day slider and a number of tests that read those files will not run until the data are fetched.

---

## 10. Data operations: if someone asks you to do something

Each block says whether it was executed while writing this document. "Ran here" means executed in the study sandbox on 2026-11-21 with the output shape observed. Several scripts overwrite committed figure files in `dakshin/figures/`; when running them for a demonstration, copy the repository first or restore with `git checkout -- dakshin/figures/<file>`. The outputs below were obtained from a scratch copy so nothing committed was changed.

Environment: Python 3.12 with `numpy`, `xarray`, `netCDF4` (or `h5netcdf` + `h5py`), `pyproj`, `scipy`, `pandas`, `matplotlib`, `torch` for model runs, `copernicusmarine` for CMEMS. Run everything from the repository root.

### 10.1 Fetch one day of NSIDC data

Near-real-time (AMSR2, the 2026 truth), ran here:

```bash
python scripts/download_nsidc_nrt.py --start 2026-11-19 --end 2026-11-19 --out /tmp/nrt
# ok   sic_pss25_20261119_am2_icdr_v04r00.nc 389301 bytes
# 1 files in manifest; 0 failed
```

Takes about 2 s. Exit code is 1 if any day failed. The NRT archive keeps roughly 3 months, so the default `--start 2026-08-24` will begin to fail as days roll off. The file name hard-codes the `am2` sensor tag, correct since 2025-01-01.

Final CDR G02202 v6 (F17 SSMIS), one day, ran here:

```bash
mkdir -p /tmp/g02202
curl -sSf -o /tmp/g02202/sic_pss25_20191201_F17_v06r00.nc \
  https://noaadata.apps.nsidc.org/NOAA/G02202_V6/south/daily/2019/sic_pss25_20191201_F17_v06r00.nc
# 399,012 bytes
```

A year range (about 130 MB per year, 6 parallel workers), not run: `python dakshin/download_nsidc.py --start-year 2019 --end-year 2020`.

Read it with the QA flag applied, ran here:

```python
import sys; sys.path.insert(0, "dakshin")
from ice_quality import load_sic, qa_breakdown
sic, suspect = load_sic("/tmp/g02202/sic_pss25_20191201_F17_v06r00.nc")
# sic.shape == (332, 316); 112 suspect cells; 22,005 NaN in total
qa_breakdown("/tmp/g02202/sic_pss25_20191201_F17_v06r00.nc")
# {'BT weather filter': 36931, 'NT weather filter': 36323, 'land spillover filter': 112,
#  'no input data': 0, 'invalid ice mask': 24396, 'spatial interpolation': 7,
#  'temporal interpolation': 0, 'cells total': 104912}
```

The Bharati cell (row 152, column 245 by `pyproj` from 69.4044 S, 76.19 E) reads 0.0 with `apply_qa=False` and NaN with `apply_qa=True` on 2019-12-01: the spillover artefact of `dakshin/ice_quality.py`.

### 10.2 Subset CMEMS

Needs `copernicusmarine login` once (credentials are not stored in the repository). A small test subset, ran here (about 10 s):

```bash
copernicusmarine subset \
  --dataset-id cmems_mod_glo_phy_anfc_0.083deg_P1D-m --variable siconc \
  --start-datetime 2026-11-21T00:00:00 --end-datetime 2026-11-22T00:00:00 \
  --minimum-longitude 70 --maximum-longitude 80 \
  --minimum-latitude -72 --maximum-latitude -66 \
  --output-directory /tmp/cmems --output-filename test_siconc.nc
# {"file_size": "0.08 MB", ..., "status": "000", "message": "The request was successful."}
# dims: time 2, latitude 73, longitude 121; variable siconc, max 0.9971
```

The full daily harvest (`bash scripts/harvest_cmems.sh`, optional `CYCLE_DATE=YYYY-MM-DD`) was not run, because it writes into the committed archive and a hand-typed date skips the stale check.

### 10.3 Regrid a field onto the NSIDC grid

Ran here, with the 2026-11-19 cycle and the NRT file from 10.1 as the grid template:

```python
import sys; sys.path.insert(0, "dakshin")
import numpy as np, xarray as xr
from grid import GlorysToNsidcRegridder
tpl = xr.open_dataset("/tmp/nrt/sic_pss25_20261119_am2_icdr_v04r00.nc")
a = xr.open_dataset("data/cmems_forecast_archive/cmems_siconc_2026-11-19.nc")
rg = GlorysToNsidcRegridder(tpl, a.latitude.values, a.longitude.values)
rg.coverage()                                   # 0.1469
out = rg(a.siconc.isel(time=0).values.astype(np.float32))
# out.shape == (332, 316), float32, 11250 finite cells, range 0.0 to 0.9964, NaN elsewhere
```

### 10.4 Run the real-forecast hindcast

Ran here in a scratch copy (about 8 s). It overwrites `dakshin/figures/realforecast_hindcast.json`:

```bash
python scripts/realforecast_hindcast.py --no-model
# clean cycles: 79, NRT days: 89, factors: (1,)
# regridder coverage of NSIDC grid: 14.7%
# lead 1: n=77 (1/12°) f1:cmems=0.10219
# lead 3: n=75 ... 0.10479 ; lead 5: n=74 ... 0.10981 ; lead 7: n=72 ... 0.1153
# wrote dakshin/figures/realforecast_hindcast.json
```

Without `--no-model` it needs `models/sic_correction/checkpoints/` (training re-run in progress) and adds `unet` entries under `rmse` and `iiee_km2_mean`. Note the lead 1 delta against the committed JSON (section 5c).

### 10.5 Run the iceberg forecast

One berg, one 9-day track, ran here:

```python
import sys, datetime as dt; sys.path[:0] = ["dakshin", "models/iceberg", "."]
from pathlib import Path
from berg_forecast import CurrentField, forecast_track, great_circle_km
from catalogue import load_usnic
cur = CurrentField.from_files([Path("data/cmems_forecast_archive/cmems_cur_2026-11-21.nc")])   # u shape (10, 277, 961)
b = load_usnic("data/icebergs/archive/AntarcticIcebergs_20261120.csv")                            # 33 bergs
r = b[b.name == "D37"].iloc[0]                  # lat -69.21, lon 36.36, 55.56 x 12.964 km, 477.77 km2
tr = forecast_track("D37", r.lat, r.lon, r.length_m, r.width_m, cur, dt.datetime(2026, 11, 21, 12), days=9)
# 217 hourly positions, status 'ok', wind_forcing_R 0.583 (assumed 10 m/s wind), net displacement 17.2 km
```

The validation against later USNIC fixes, ran here (about 5 s, overwrites `berg_hindcast.json`):

```bash
python scripts/berg_hindcast.py
# wrote dakshin/figures/berg_hindcast.json: 81/88 ok segments, median model 4.35 km/day vs persistence 0.0 km/day
python scripts/berg_resolution.py      # F3; 1/12°: 81 ok, 4.35 | 1/4°: 86 ok, 4.07 | 1°: 88 ok, 3.49 km/day
python scripts/berg_melt.py            # F4; 8 bergs, mean 157,451 to 1,913,104 m3/day
```

All three reproduce the committed JSONs exactly.

### 10.5b Regime report

Ran here, reproduces the committed `models/iceberg/regime_report.json` exactly when pointed at the 2026-08-27 issue:

```bash
python models/iceberg/regime_report.py --csv data/icebergs/archive/AntarcticIcebergs_20260827.csv
```

Without `--csv` it downloads the current USNIC catalogue (today: issue 2026-11-20, smallest berg 45.36 km2, median long axis 25.9 km), so the output differs from the committed file.

### 10.6 Run a route

Ran here (about 1.6 s, overwrites `dakshin/figures/real_route.json`):

```bash
python scripts/real_route_run.py 2026-11-21
# approach_closed_at_ice_limit true, closest_approach_km 50.6, eta_days 5.55, worst_ice 0.723,
# worst_hs_m 4.77, worst_wind_ms 14.9, weather_gate FAIL, n_legs 45
```

The prototype PolarRoute routes need the Python 3.11 environment (`uv venv --python 3.11 prenv; uv pip install --python prenv/bin/python polar-route==1.1.11 matplotlib`) and were not run: `prenv/bin/python dakshin/make_route_figure.py`, `dakshin/route_regret.py --depart 2019-12-01`, `dakshin/destination_window.py --start 2019-12-01 --days 30`, `dakshin/alternatives.py`.

### 10.7 Run the tests

Ran here:

```bash
python -m pytest -q
# 195 passed, 7 skipped, 1 warning in 27.6s   (working tree, 2026-11-21)
python scripts/verify_claims.py
# PASSED 29 ; All claims verified against source files.
```

The demo app tests need the NSIDC 2018 to 2020 archive (gitignored). `models/iceberg/test_drift.py` has 23 tests (the "23/23" of `docs/TRUE_CLAIMS.md` claim 1.9).

### 10.8 Run the resolution study

Ran here (about 14 s, overwrites `resolution_study.json` and `.png`):

```bash
python scripts/resolution_study.py --no-model
# lead 1..7 lines with f1/f3/f12 cmems RMSE; wrote dakshin/figures/resolution_study.json and .png
```

Leads 3, 5 and 7 reproduce the committed JSON exactly; lead 1 shows n = 77 (RMSE 1/12 degree 0.10219, 1/4 degree 0.10055, 1 degree 0.10419) against n = 76 committed. U-Net columns appear when checkpoints exist (training re-run in progress).

### 10.9 Plug in NEMO output

Not run on real NEMO output. The pattern is in section 4.5; use `NemoReader(...).available()` first to see which fields were resolved.

### 10.10 Retrain, pull checkpoints, run the demo

Not run (needs Kaggle credentials and hours of GPU):

```bash
python dakshin/kaggle/make_notebook.py            # regenerate isih_train.ipynb from unet.py, grid.py, features.py
KAGGLE_API_TOKEN=... bash scripts/pull_checkpoints.sh   # when the kernel is COMPLETE
uvicorn dakshin.demo.app:app --port 8000          # demo; see docs/PROTOTYPE_README.md for the venv
```

---

## 11. State of the model and the open items

Model status. The four checkpoints (leads 1, 3, 5, 7) are not in the repository. `docs/CURRENT_STATE.md` records Kaggle kernel `notebookd39fdf7959` version 6 as queued for the free T4 pool at the time that file was written; the check at `models/sic_correction/` on 2026-11-21 shows only `unet.py`. When the kernel completes the owner runs `scripts/pull_checkpoints.sh`, writes the real-forecast results into `docs/PROTOTYPE_RESULTS.md`, fills the pending U-Net rows of `docs/RESOLUTION_STUDY.md`, and publishes the checkpoints as a release (`model-v0.1`, as named in the script). Every U-Net column in this study pack reads "training re-run in progress" until then.

What is not built, per `docs/TRUE_CLAIMS.md` section 5 and `docs/backlog.md`: the time-expanded graph for PolarRoute, a five-model ensemble and conformal calibration (ADR-020; designed, with a pre-committed pass/fail gate, nothing fitted), a thickness output channel for POLARIS compliance, quality-masked retraining with error reported by distance to coast, a compression-risk field, grounding detection for bergs in committed code (the binding constraint on drift forecasts per the F3 finding; an uncommitted working-tree change to `dakshin/berg_forecast.py` begins to add one).

Inconsistencies noticed while reading, listed rather than fixed, are collected in the final message that accompanies this commit and as one-liners in `docs/backlog.md`.
