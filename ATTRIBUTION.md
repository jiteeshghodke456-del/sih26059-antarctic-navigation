# Data and dependency attribution

Dakshin's code is MIT-licensed (see LICENSE). Every dataset and dependency it
uses carries its own terms, recorded here. The licence rule this repo
follows: MIT/BSD/CC-BY material may ship with the project; GPL tools
(OpenDrift) are optional, separately installed, and never imported by the
core packages.

## Datasets

| Dataset | Used for | Licence / terms | Citation |
|---|---|---|---|
| Copernicus Marine GLOBAL_ANALYSISFORECAST_PHY_001_024 (`cmems_mod_glo_phy_anfc_0.083deg_P1D-m`, `...phy-cur...`) | daily ice forecast archive, surface currents | Free with registration; credit required | "E.U. Copernicus Marine Service Information; Global Ocean Physics Analysis and Forecast, DOI 10.48670/moi-00016" |
| Copernicus Marine GLOBAL_ANALYSISFORECAST_WAV_001_027 (`cmems_mod_glo_wav_anfc_0.083deg_PT3H-i`) | daily max wave height | same | "E.U. Copernicus Marine Service Information; Global Ocean Waves Analysis and Forecast, DOI 10.48670/moi-00017" |
| Copernicus Marine GLORYS12 reanalysis (`cmems_mod_glo_phy_my_0.083deg_P1D-m`) | prototype training background | same | "E.U. Copernicus Marine Service Information; Global Ocean Physics Reanalysis, DOI 10.48670/moi-00021" |
| NOAA/NSIDC Sea Ice Concentration CDR v6 (G02202) | training/validation truth 2019–2020 | NOAA open data; citation required | Meier, W. N. et al. (2021). NOAA/NSIDC Climate Data Record of Passive Microwave Sea Ice Concentration, Version 6. NSIDC. DOI 10.7265/efmz-2t65 |
| NOAA/NSIDC Near-Real-Time CDR v4 (G10016) | 2026 satellite truth for the real-forecast hindcast | NOAA open data; citation required | Meier, W. N. et al. NOAA/NSIDC Near-Real-Time CDR of Passive Microwave Sea Ice Concentration, Version 4. NSIDC. DOI 10.7265/tgam-yv28 |
| ECMWF open data (IFS 10 m wind) | daily wind forecasts | **CC BY 4.0** — required wording: "Contains modified ECMWF open data (CC BY 4.0), https://www.ecmwf.int/en/forecasts/datasets/open-data" | ECMWF Open Data, accessed daily from 2026-11-21 |
| IBCSO v2 (ice-surface grid) | bathymetry south of 50°S, min-depth routing, chart gate | CC-BY-4.0 | Dorschel, B. et al. (2022). The International Bathymetric Chart of the Southern Ocean Version 2. Scientific Data 9, 275. Dataset DOI 10.1594/PANGAEA.937574 |
| USNIC Antarctic iceberg list | weekly giant-berg positions, drift validation | US Government work, public | U.S. National Ice Center, Antarctic Icebergs, https://usicecenter.gov/Products/AntarcIcebergs |
| Natural Earth | coastline/land mask | public domain | naturalearthdata.com |
| Antarctic Treaty ASPA register | protected-area avoidance | public treaty data | Antarctic Treaty Secretariat, ats.aq |
| Open-Meteo marine/forecast APIs | **fallback only, not used in outputs** | CC BY 4.0 data; free tier is NON-COMMERCIAL — may not cover a government deployment, which is why it stays a fallback | open-meteo.com |

## Python dependencies (runtime)

| Package | Licence |
|---|---|
| numpy, scipy, pandas, xarray | BSD-3-Clause |
| torch | BSD-3-Clause |
| pyproj | MIT |
| netCDF4 | MIT |
| h5netcdf / h5py | BSD-3-Clause |
| matplotlib | PSF-based (BSD-compatible) |
| fastapi, uvicorn, starlette, pydantic, httpx | BSD-3-Clause / MIT |
| copernicusmarine toolbox | EUPL-1.2 (used as a CLI/client, not vendored) |
| ecmwf-opendata | Apache-2.0 |
| pyais | MIT |
| pyshp | MIT |
| cfgrib / eccodes | Apache-2.0 |
| pytest | MIT |
| mlflow | Apache-2.0 |

## Reference designs and optional tools

| Project | Licence | Relationship |
|---|---|---|
| PolarRoute + meshiphi (British Antarctic Survey) | MIT | used for mesh/route computation |
| OpenDrift / OpenBerg | **GPL-2.0** | optional cross-check only; never imported by `dakshin/` or `models/` |
| IceNet | MIT | reference design only; no code imported |

## Iceberg drift physics

The drift model implements Wagner, T. J. W., Dell, R. W., Eisenman, I. (2017),
"An Analytical Model of Iceberg Drift", Journal of Physical Oceanography 47(7)
(WDE17), with the melt terms of Keghouche et al. (2010) noted as future work.
