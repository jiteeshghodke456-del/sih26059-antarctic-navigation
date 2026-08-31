# DATASET.md — SIH26059 Antarctic Navigation Decision-Support Platform

Data-reality-check gate. All entries below were checked live from this sandbox on **2026-08-31**
(both via WebFetch and via direct `curl` from the sandbox shell, to confirm the outbound HTTP
allowlist does not block them). Where a dataset returned actual current-dated bytes, that raw
evidence is quoted. No dummy/synthetic data is proposed anywhere in this document — every entry
is a real, traceable source. Categories that do NOT have a real accessible source are called out
explicitly as blockers, not glossed over.

---

## 1. Sea ice concentration

### 1.1 NSIDC Sea Ice Index v4 (NOAA@NSIDC) — VERIFIED LIVE, NO AUTH
- **Provider**: National Snow and Ice Data Center (NASA-funded), NOAA
- **Access**: `https://noaadata.apps.nsidc.org/NOAA/G02135/south/daily/data/S_seaice_extent_daily_v4.0.csv` — plain HTTP, **no login**.
- **Confirmed live**: `curl` returned real rows through **2026-08-29**, each pointing at the source AMSR2 granule, e.g.:
  ```
  2026,08,29,17.139,0.000,['NSIDC-0803_SEAICE_AMSR2_S_20260829_v2.0.nc']
  ```
- **Variables**: daily Southern Hemisphere sea ice extent (million km²) and area; the linked per-day AMSR2 NetCDF (`NSIDC-0803`) carries gridded sea ice concentration (%).
- **Coverage/resolution**: Antarctic-wide, daily, extent CSV is a scalar time series; the underlying AMSR2 concentration grid (`AU_SI12`/`nsidc0803`) is 12.5 km polar stereographic.
- **Format/size**: CSV (few MB for the whole daily record) for extent; NetCDF (~few MB/day) for gridded concentration.
- **Access mechanism**: fully open HTTP, no Earthdata login needed for this specific product tree. The higher-resolution `AU_SI12`/`AU_SI25` brightness-temperature + concentration products live under NASA Earthdata (`nsidc.org/data/au_si12`) and DO require a free NASA Earthdata Login (`urs.earthdata.nasa.gov` — confirmed reachable, HTTP 200) plus `.netrc`-based auth for bulk/API download, which is a one-time free registration, not a blocker.
- **Sandbox reachability**: confirmed 200 via curl, no allowlist issue.

### 1.2 EUMETSAT OSI SAF Global Sea Ice Concentration — REAL, ACCOUNT-GATED
- **Provider**: EUMETSAT Ocean and Sea Ice SAF
- **Products** (confirmed live on `osi-saf.eumetsat.int/products/sea-ice-products`):
  - OSI-401-d — Global Sea-Ice Concentration (SSMIS), 10 km, daily
  - OSI-408-a — Global Sea-Ice Concentration (AMSR2), 10 km, daily (successor to the now-suspended OSI-430-a SSMIS interim CDR, suspended 2025-10-17 due to unstable SSMIS access — use OSI-438/408-a instead)
  - OSI-402-d — Sea-Ice Edge, OSI-403-d — Sea-Ice Type, OSI-405-d — Low-Resolution Sea-Ice Drift (62.5 km)
- **Variables**: ice concentration %, ice edge, ice type (first-year/multi-year), ice drift vectors.
- **Coverage**: both hemispheres, Antarctic included, 10 km (concentration/edge/type), 62.5 km (drift), daily.
- **Format**: NetCDF.
- **Access mechanism**: free under CC-BY-4.0, but distribution is via **EUMETSAT Data Centre / FTP / EUMETCast**, which needs a free EUMETSAT account (`https://osi-saf.eumetsat.int`, confirmed 200). No open anonymous HTTP directory was found equivalent to NSIDC's — treat as "free but requires registration," not a blocker.
- **Sandbox reachability**: landing/product pages reachable (200); actual data-centre download endpoint needs the account to test further.

### 1.3 ESA CCI Sea Ice — REAL, OPEN, NO ACCOUNT FOR CEDA
- **Provider**: ESA Climate Change Initiative (Sea_Ice_cci), hosted at CEDA (Centre for Environmental Data Analysis, UK)
- **Products**: Sea Ice Concentration CDR/ICDR at 25 km and 12.5 km, 1991–2020+ (v3), plus AMSR-E/AMSR2 50 km CDR; also distributed as `NSIDC-0718`/`NSIDC-0779` mirrors on NSIDC.
- **Coverage/resolution**: both poles, daily, 25 km / 12.5 km / 50 km depending on product.
- **Format**: NetCDF, DOI-tracked (e.g. `10.5285/c61bfe88-873b-44d8-9b0e-6a0ee884ad95`).
- **Access mechanism**: direct download from the CEDA catalogue (`catalogue.ceda.ac.uk`) — CEDA generally allows anonymous HTTP/FTP download of open products, some CEDA products need a free CEDA account. An alternative access path is via the Copernicus Climate Data Store (`cds.climate.copernicus.eu`) under an "ESA-CCI sea ice concentration" licence, which needs a free CDS/ECMWF account (same account as ERA5 below — one registration covers both).
- **Sandbox reachability**: `cds.climate.copernicus.eu/api` confirmed reachable (HTTP 202).

**Verdict for category 1**: Solid — NSIDC gives an immediately-fetchable, no-auth Antarctic sea ice extent time series today, and three independent concentration products (AMSR2/OSI SAF/ESA CCI) exist as fallback/cross-validation with only free registration as friction. No blocker.

---

## 2. SAR / satellite imagery for ice

### 2.1 Copernicus Sentinel-1 via Copernicus Data Space Ecosystem (CDSE) — VERIFIED LIVE, OPEN CATALOG
- **Provider**: ESA / Copernicus
- **Access**: OData/STAC catalogue search is **anonymous, no auth**: confirmed live via
  ```
  curl "https://catalogue.dataspace.copernicus.eu/odata/v1/Products?\$top=1"
  ```
  returned HTTP 200 with real JSON product metadata (checksums, S3 path, content dates).
  Actual **product download** (the SAFE archive itself) requires a free CDSE account + OAuth2 token (`identity.dataspace.copernicus.eu` — standard client-credentials flow via `cdsapi`/`curl`), which is free self-service registration, not paywalled.
- **Variables**: Sentinel-1 C-band SAR (IW/EW modes, GRD/SLC), usable for sea ice edge detection, iceberg detection (bright SAR returns vs. surrounding ice/water), lead detection. All-weather, day/night — critical for Antarctic winter darkness where optical (Sentinel-3 OLCI) is blind.
- **Coverage/temporal — verified, revised down from initial estimate**: EW mode (400 km swath, 20×40 m pixel spacing, designed for maritime/ice/polar observation) has been systematically acquired over the Antarctic sea ice zone since shortly after Sentinel-1A's 2014 launch — a published archive documents 69,586 EW-mode Antarctic scenes from Oct 2014–Dec 2020 (Tandfonline/CASEarth, confirmed via search, not independently refetched). However, unlike the Arctic, ESA's Sentinel-1 observation scenario does **not** run a standing daily/near-daily EW acquisition plan over the whole Southern Ocean — coverage is denser during austral sea-ice season and near the coast/shipping-relevant zones, sparser mid-ocean. Treat "6–12 day revisit" as **not verified** for a specific Antarctic AOI; the real number depends on which sector and season, and must be checked against ESA's live observation-scenario maps (`sentinel.esa.int/web/sentinel/copernicus/sentinel-1/observation-scenario`) for the actual route corridor once one is chosen, before any routing algorithm assumes a fixed SAR refresh interval.
- **Format/size**: SAFE (zipped, ~1–4 GB per GRD scene, EW mode); also queryable/subsettable via Sentinel Hub API (part of CDSE) for smaller AOI clips.
- **Sandbox reachability**: confirmed 200 for catalogue search.

### 2.2 Sentinel-3 (OLCI/SLSTR) via CDSE
- **Provider**: ESA/Copernicus, same CDSE catalogue/API as above.
- **Variables**: SLSTR provides Sea Surface Temperature (SST) and sea/ice surface temperature; OLCI provides ocean colour/optical imagery (cloud- and darkness-limited, less useful for polar winter than SAR but useful for validation and ice-edge context in daylight/summer).
- **Coverage/resolution**: SLSTR SST ~1 km, daily near-global; OLCI ~300 m.
- **Format**: NetCDF (Level-1/2 products).
- **Access mechanism**: same CDSE account as Sentinel-1.
- **Sandbox reachability**: same catalogue endpoint, confirmed reachable.

**Verdict for category 2**: Solid. Sentinel-1 SAR is the single most valuable dataset for this problem (works through Antarctic winter darkness and cloud) and the catalogue API is confirmed live with anonymous search; only the bulk image download needs a free CDSE token.

---

## 3. Iceberg tracking

### 3.1 BYU/NIC Antarctic Iceberg Tracking Database — VERIFIED LIVE, DIRECT DOWNLOAD, NO ACCOUNT
- **Provider**: Brigham Young University Center for Remote Sensing (Scambos/Budge/Long), in partnership with US National Ice Center.
- **Access**: `https://www.scp.byu.edu/data/iceberg/database1.html` — confirmed reachable (HTTP 200), direct zip download links present.
- **Files** (confirmed on page):
  - **Consolidated Database v8.0** (4.1 MB zip): NIC + scatterometer-derived (ASCAT/QuikSCAT/OSCAT/ERS/NSCAT/SASS) daily iceberg lat/lon, major/minor axis size (km), date (YYYYDDD). Coverage **1978 through 2025-04-22**.
  - **Statistical Database v7.1** (2.5 MB zip): daily-averaged position, size (km²), rotation velocity, surrounding-environment mask (land/sea-ice/open-ocean/no-data). Coverage **1978 through 2023-08-25**.
- **Update cadence**: real-time weekly position feed exists separately; full archive files refreshed 1–2×/year, so the bulk file is ~16 months stale as of today (2026-08-31) — plan to combine with USNIC's live weekly feed (3.2) for current positions.
- **Format**: CSV inside zip.
- **Access mechanism**: fully open HTTP, no login.
- **Sandbox reachability**: confirmed 200.

### 3.2 US National Ice Center (USNIC) Antarctic Iceberg Products — VERIFIED LIVE
- **Provider**: US National Ice Center (NOAA/US Navy/USCG joint)
- **Access**: `https://usicecenter.gov/Products/AntarcIcebergs` — confirmed 200, page lists PDF, CSV, **Shapefile**, and Archive downloads.
- **Variables**: named/tracked iceberg current position, size (nm, longest/widest axis), remarks. Criteria: ≥20 sq nm or ≥10 nm longest axis, tracked weekly via optical/IR/SAR imagery review.
- **Coverage/temporal**: all Southern Ocean, weekly updates, since 1978.
- **Format**: CSV + Shapefile (immediately GIS-usable), PDF for human review.
- **Access mechanism**: open, no registration seen on the page itself (public .gov product page).
- **Sandbox reachability**: confirmed 200.

**Verdict for category 3**: Solid — a genuinely rare case of a fully open, no-auth, current, shapefile-ready government feed (USNIC) plus a deep historical archive (BYU) for training a trajectory model. Combine both: BYU for long-run training data + physical size/rotation features, USNIC weekly shapefile for near-real-time current positions.

---

## 4. Oceanographic (currents, SST)

### 4.1 Copernicus Marine Service (CMEMS) Global Ocean Physics Reanalysis/Forecast — REAL, FREE ACCOUNT
- **Provider**: Mercator Ocean International / EU Copernicus Marine Service.
- **Products confirmed live** (`data.marine.copernicus.eu`, HTTP 200):
  - `GLOBAL_MULTIYEAR_PHY_001_030` (GLORYS12 reanalysis): 1/12° (~8 km), 50 depth levels, 1993–present, daily.
  - `GLOBAL_ANALYSISFORECAST_PHY_001_024`: operational forecast, currents (u/v), SST, salinity, sea surface height, mixed layer depth, 10-day forecast horizon.
- **Access mechanism**: `copernicusmarine` Python package (confirmed real, actively maintained on PyPI — verified via `pypi.org/pypi/copernicusmarine/json`, maintained by Copernicus Marine User Support). CLI/Python API (`copernicusmarine.subset(...)`) after one free account registration at `data.marine.copernicus.eu`; no separate paywall.
- **Variables**: ocean current velocity (uo/vo) — directly needed for fuel-efficient routing (current-assisted vs. current-opposing legs), SST, salinity, sea surface height.
- **Format/size**: NetCDF, subsettable by AOI/depth/time via the toolbox so file sizes for an Antarctic-coastal AOI subset are MBs, not the full global GBs.
- **Sandbox reachability**: confirmed 200 for the product services page; PyPI package metadata confirmed reachable.

### 4.2 NOAA OISST v2.1 — VERIFIED LIVE, NO AUTH, CURRENT TO YESTERDAY
- **Provider**: NOAA NCEI
- **Access**: `https://www.ncei.noaa.gov/data/sea-surface-temperature-optimum-interpolation/v2.1/access/avhrr/` — confirmed 200, browsable by year-month.
- **Confirmed live**: directory listing for `202608/` contains `oisst-avhrr-v02r01.20260829_preliminary.nc`, i.e. data current to **2026-08-29** (2 days lag, "preliminary" flag until final QC pass).
- **Variables**: daily SST, 0.25° global grid, since 1981-09-01.
- **Format/size**: NetCDF-4, ~a few MB/day (global); Southern Ocean subset is smaller.
- **Access mechanism**: direct HTTP/wget/curl, **no login**. (FTP explicitly not supported — must use HTTP.)
- **Sandbox reachability**: confirmed 200, real file listing retrieved.

**Verdict for category 4**: Solid. OISST gives an immediately-usable, no-auth, near-daily SST product; CMEMS gives currents (the harder-to-source variable, essential for fuel-efficient routing) via one free account.

---

## 5. Meteorological (wind, pressure, waves)

### 5.1 ECMWF ERA5 Reanalysis (Copernicus Climate Data Store) — REAL, FREE ACCOUNT
- **Provider**: ECMWF / Copernicus Climate Change Service (C3S)
- **Access**: `cds.climate.copernicus.eu/api` — confirmed reachable (HTTP 202) from this sandbox. Programmatic access via the official `cdsapi` Python client (actively maintained, `github.com/ecmwf/cdsapi`), needs a free CDS account + API key in `~/.cdsapirc`.
- **Variables**: 10 m u/v wind components, mean sea level pressure, 2 m temperature, and — confirmed as part of the **same** `reanalysis-era5-single-levels` CDS dataset (not a separate product; verified via ECMWF/EQC documentation), category "Ocean waves" — `significant_height_of_combined_wind_waves_and_swell`, `mean_wave_direction`, `mean_wave_period`. So wind and wave variables can be pulled from one dataset/one API call pattern, just different variable names in the request. All needed for "safe" routing (avoid high-wave/high-wind legs) on top of ice avoidance.
- **Coverage/resolution**: global, 0.25° hourly, 1940–near-present (~5-day latency for the full QC'd release; ERA5T preliminary within ~5 days).
- **Format/size**: GRIB or NetCDF, full single-level global field ~a few hundred MB/month; an Antarctic-only, wind+pressure-only subset is MBs.
- **Access mechanism**: free registration, standard for any serious met/ocean reanalysis use; not a blocker.
- **Sandbox reachability**: confirmed reachable.

### 5.2 NOAA GFS (via NOMADS) — VERIFIED LIVE, NO AUTH, TODAY'S FORECAST CONFIRMED
- **Provider**: NOAA NCEP
- **Access**: `https://nomads.ncep.noaa.gov/gribfilter.php?ds=gfs_0p25` — confirmed live, form shows forecast cycles from **2026-08-22 through 2026-08-31** (today), i.e. genuinely operational, not stale.
- **Confirmed live**: a direct subset query against today's 00z cycle for the Antarctic Peninsula/Weddell Sea box returned HTTP 200:
  ```
  https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?file=gfs.t00z.pgrb2.0p25.f000&lev_10_m_above_ground=on&var_UGRD=on&var_VGRD=on&subregion=&toplat=-60&leftlon=0&rightlon=60&bottomlat=-80&dir=/gfs.20260831/00/atmos
  ```
- **Variables**: UGRD/VGRD (wind at multiple levels), pressure levels 1000–0.01 mb, gust, wave-shear indicators. GFS is forecast-only (out to 384 h), not a long reanalysis — use alongside ERA5 (historical/training) and GFS (operational forecast for live routing).
- **Coverage/resolution**: global 0.25°, 4 cycles/day.
- **Format/size**: GRIB2, region-subsettable via the grib-filter CGI so an Antarctic-box, wind-only request is small (tens of MB or less).
- **Access mechanism**: fully open, no login, courtesy rate-limit only.
- **Sandbox reachability**: confirmed 200, live query executed successfully.

**Verdict for category 5**: Solid. GFS gives free no-auth operational wind forecasts today; ERA5 gives the deep historical record needed to train/validate any routing or drift model, behind one free account.

---

## 6. Bathymetry / navigation context

### 6.1 GEBCO Gridded Bathymetry — VERIFIED LIVE, NO AUTH
- **Provider**: GEBCO (IHO + IOC joint project), part of Seabed 2030.
- **Access**: `https://www.gebco.net/data-products/gridded-bathymetry-data` — confirmed 200, direct download + web app (AOI-subset) both open, **no login**.
- **Latest release**: GEBCO_2025/2026 grid, 15 arc-second (~450 m) global coverage, ice-surface and sub-ice-topography variants.
- **Format/size**: NetCDF / GeoTIFF / Esri ASCII; **full global grid is ~4 GB compressed / 7–18 GB uncompressed** depending on format — for this project, use the AOI-subset web app/API to pull only the Southern Ocean/Antarctic coastal box (much smaller), not the global file.
- **Access mechanism**: fully open HTTP download or OPeNDAP, no registration.
- **Sandbox reachability**: confirmed 200.

### 6.2 IHO ice-affected shipping lanes — **GENUINE BLOCKER, FLAGGED EXPLICITLY**
No dedicated, downloadable "recommended Antarctic ice-affected shipping lane" dataset exists from IHO or any other body. What exists instead:
- **IHO Electronic Navigational Charts (ENCs)** for Antarctic waters — official vector charts exist but are distributed through national hydrographic offices / IC-ENC / PRIMAR and are **licensed/paywalled**, not a free open dataset, and Antarctic coverage is notoriously sparse/low-resolution because it is barely surveyed (most of the Southern Ocean seafloor is GEBCO-predicted bathymetry, not ship-sounded).
- **IMO Polar Code** and **WWMIWS/METAREA** products (via WMO/IMO/IHO) are operational safety-information broadcast systems (SafetyNet/NAVTEX), not structured route datasets — no bulk API.
- **Conclusion**: there is no real "ice shipping lane" ground-truth dataset to consume. This is expected, not a gap in our research — it is precisely the computed output this platform is meant to produce (safe/fuel-efficient route = ice concentration + iceberg positions + bathymetry + wind/wave, run through a routing algorithm), not an input that already exists elsewhere. Treat GEBCO bathymetry + IHO chart depth soundings (where affordably licensable) as the only real navigation-context input; do not claim an existing "ice lane dataset" is being ingested, since none exists.

**Verdict for category 6**: GEBCO is solid and open. The "ice shipping lane" sub-item is a real, disclosed non-existence — not a data-sourcing failure, a confirmation that route computation is the product's actual job.

---

## 7. NCPOR's own data portal — REAL, CONFIRMED LIVE, LIMITED DIRECT RELEVANCE

Searched directly. NCPOR (`ncpor.res.in`, confirmed 200) runs a **Data Center** menu linking to three distinct live services:

- **National Polar Data Center (NPDC)** — `https://npdc.ncpor.res.in/npdc/` (confirmed 200; redirects through `homepage.action` to a Struts-based catalog app). Confirmed real catalog functionality present in the page: "Dataset by Location", "Dataset by Science Keywords", "Search Raw Data" (`rawData/searchRawData.jsp`), "Submit a New Data", metadata guidance, and a Data Policy page. This is India's own polar-data catalog (expedition data, Automatic Weather Station data from Maitri/Bharati, etc.) — real, but it is metadata/AWS-station-scale, not global satellite-grid data, so its role here is **local ground-truth/validation for the Indian Antarctic stations**, not a primary input feed for the ML models.
- **`data.ncpor.res.in`** — general Data Portal, links to specific observational datasets (e.g. black carbon observations) and a Polar Directory (`data.ncpor.res.in/PolarDirectory`).
- **`synopticdata.ncpor.res.in`** — "Synoptic-Bharati" — live meteorological observations from Bharati station.
- **`las.ncaor.gov.in`** — Live Access Server (LAS), a standard scientific-data visualization/subsetting tool (Ferret-based), suggesting some gridded oceanographic products are also served here.

**Verdict for category 7**: NCPOR does have a real, functioning public data portal (not a dead link, not vaporware) — the National Polar Data Center is a legitimate India-specific catalog. It is not a substitute for the global satellite/reanalysis products above, but it is directly relevant as (a) validation ground-truth near India's own stations, and (b) a differentiator to cite in the pitch ("uses NCPOR's own data + global satellite/reanalysis data," which plays well for an MoES/NCPOR problem statement). Recommend a follow-up pass once `npdc/searchRawData.jsp` is explored interactively (it appeared to require in-page search rather than a REST API — likely needs a browser session or reverse-engineering the Struts endpoints; not blocking for MVP since it's a secondary/validation source).

---

## Summary table

| # | Category | Best source | Live/no-auth today | Auth needed | Blocker? |
|---|---|---|---|---|---|
| 1 | Sea ice concentration | NSIDC Sea Ice Index / AMSR2 | Yes (extent CSV) | Earthdata login only for gridded bulk | No |
| 1 | Sea ice concentration (alt) | OSI SAF / ESA CCI | Product pages yes | Free EUMETSAT / CDS account | No |
| 2 | SAR imagery | Sentinel-1 (CDSE) | Yes (catalogue search) | Free CDSE token for image download | No |
| 3 | Iceberg tracking | BYU + USNIC | Yes, both | None | No |
| 4 | Ocean currents/SST | CMEMS + NOAA OISST | OISST yes no-auth; CMEMS needs account | Free CMEMS account | No |
| 5 | Wind/pressure/waves | GFS (live) + ERA5 (history) | GFS yes no-auth; ERA5 needs account | Free CDS account | No |
| 6 | Bathymetry | GEBCO | Yes | None | No |
| 6 | Ice shipping lanes | — none exists — | — | — | **Yes — genuine gap, expected** |
| 7 | NCPOR portal | NPDC/data.ncpor.res.in | Yes (catalog reachable) | Unclear per-dataset; some open | No (secondary source) |

**Bottom line**: every required input category (ice concentration, SAR, iceberg tracks, ocean currents/SST, wind/wave, bathymetry) has at least one real, currently-live, programmatically-reachable source confirmed from inside this sandbox today (2026-08-31), several with zero authentication (NSIDC extent, OISST, USNIC iceberg shapefile, BYU iceberg archive, GFS, GEBCO). The only registrations needed (NASA Earthdata, Copernicus Data Space, Copernicus Marine, Copernicus Climate Data Store/CDS, EUMETSAT) are free, standard, one-time sign-ups — not paywalls. The one true gap is a pre-existing "ice shipping lane" dataset, which does not exist anywhere and is not expected to — it is the output this platform computes, not an input it should be looking to ingest.
