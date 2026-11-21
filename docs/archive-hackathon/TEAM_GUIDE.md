# Team Guide — SIH26059

Full version (system diagram, sourced learning map): https://claude.ai/code/artifact/83e086a9-4d37-4204-b19d-852eaf59e9f0
Reasoning behind every choice below lives in `ARCHITECTURE.md`, `ML_ARCHITECTURE.md`, `DECISIONS.md`.

## Tech stack (copy-paste)

**Shore — data & ML** (`requirements.txt`)
```
python==3.11.14
polar-route==1.1.11
meshiphi==2.3.1
torch
scikit-learn
lightgbm
xarray
netCDF4
zarr
numpy
pandas
geopandas
shapely
copernicusmarine
cdsapi
requests
```
Do not add `icenet` — pins `netcdf4<1.6.1`, conflicts with meshiphi's `netcdf4==1.7.4` (verified).

**Backend**
```
fastapi
uvicorn[standard]
pydantic
pytest
zstandard
cryptography
```
One codebase, `MODE=shore|vessel` config switch — not two services.

**Frontend** (`package.json`)
```
react
react-dom
typescript
vite
maplibre-gl
pmtiles
```
MapLibre + PMTiles, not Leaflet — offline vector tiles, no tile server needed on the bridge.

**DevOps**: docker, docker-compose, git, GitHub Actions. CI must include the ADR-017 bandwidth-budget test (fails build if a pack exceeds 50 KB daily / 1 MB full-refresh).

**Training compute**: Kaggle Notebooks (free, primary, 8–12 GPU-h fits one week's quota) → Google Colab Pro (backup) → spot T4/L4 (~$5–10, paid fallback). Nothing trains at the nodal centre; weights ship by USB.

## Team split (6 people)

| Role | Owns | Heaviest | Gate | Depends on |
|---|---|---|---|---|
| Data & Ingestion Lead | `ingest/`, QC, CMEMS harvest cron, source auth | Phase 0–1 | Daily CMEMS cron live from day 1 (unbackfillable); real file from each of NSIDC/ERA5/CMEMS by end Phase 1 | Nobody — starts day 1 |
| ML / Forecasting Engineer | `models/` (SIC) — residual U-Net ×5, Stage A/B training | Phase 2 | Beats packed CMEMS on IIEE+CRPS per lead | Data lead's archives |
| Calibration & Iceberg Physics Engineer | Conformal calibration; Wagner drift; GBM residual + fallback | Phase 2–3 | MIZ coverage ∈[85,96]% at lead 5, width <25 SIC-% | ML engineer; Data lead |
| Routing Engineer | `routing/` — PolarRoute+meshiphi, vessel subclass, 12-run sweep | Phase 1, 3 | Real Cape Town→Bharati route by end Phase 1 | Data lead's GEBCO/GFS |
| Backend/Systems Engineer | `api/`, `pack/` — FastAPI modes, sign/delta-sync, CI budget test | Phase 0, 4 | Full re-plan with networking disabled | Everyone's interfaces |
| Frontend & Integration/Demo Lead | `web/` — React+MapLibre, slider, demo packs, judge Q&A prep | Phase 3–4 | Slider visibly moves route; network-cut demo | Backend; Routing |

## This week's actual blockers (not architecture — logistics only you can do)

1. Start the daily CMEMS forecast harvest cron the day the repo exists — it cannot be back-filled later.
2. Register free accounts: NASA Earthdata, Copernicus Data Space, Copernicus Marine, Copernicus Climate Data Store (CDS). None are paywalled; all are needed before Phase 1's data gate.

Full backlog, including remaining ML/build items: `backlog.md`.
