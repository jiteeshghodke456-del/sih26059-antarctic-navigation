# Data source strategy — Indian and foreign, compared objectively

§29's instruction, quoted, because the framing matters:

> "Use Indian government/research sources where technically competitive, but do
> NOT prioritize Indian infrastructure for ideological, nationalistic, or
> 'local-for-local' reasons. Treat every Indian government/research source as a
> candidate to be evaluated **objectively** against the best foreign
> alternative… **Never assume an Indian service covers Antarctica merely
> because the organization operates internationally. Verify actual spatial
> coverage, update frequency, resolution, and current availability.**"

**This was the weakest requirement in the project and nothing had flagged it.**
Before this document, a grep for `ISRO`, `NRSC`, `IMD`, `Oceansat`, `SCATSAT`,
`MOSDAC` or `Bhuvan` returned **zero hits anywhere in the repository**, and
`INCOIS` appeared twice — both times in a pricing discussion, as a competitor.

**Method.** Live agency endpoints were queried on 2026-09-07: the MOSDAC
catalog API, INCOIS THREDDS/ncWMS/ERDDAP, the VEDAS polar GeoServer
GetCapabilities, the NCPOR data portal, IMD NWP pages, and published ATBDs.
Coverage was *read off the grids*, not inferred from an organisation's remit.
Anything that could not be opened is marked `UNVERIFIED`.

---

## 1. The headline, and a correction to our own prior belief

We had assumed no Indian gridded Antarctic sea-ice product existed. **That was
wrong.**

**ISRO's EOS-06 (Oceansat-3) SCAT Level-3 "Global Sea Ice" is live.** MOSDAC's
own catalog returns `E06SCT_L3_GS_GLB12` and `_GLB25` — **daily, 12.5 km and
25 km, 2024-06-01 to 2026-09-06, Active**, i.e. latency of about one day on the
day we checked. The 12.5 km grid is *finer than the 25 km NSIDC CDR we train
on*.

It does not displace the incumbent, and the reason is specific rather than
dismissive: it is an **extent** product — a binary ice/water flag from Ku-band
σ⁰ thresholds — not a concentration field, and its record begins in June 2024.
You cannot train a concentration model on a binary flag, and you cannot build a
climatology from 2.3 years. But those are the wrong tests for what it is good
for, which is an independent daily read of where the ice edge is, on completely
different physics from passive microwave.

Second correction: **INCOIS operates a global WAVEWATCH III forecast that
reaches 80°S** — 1°, 79 steps at 3 h (≈9.75 days), open via THREDDS, ncWMS,
OPeNDAP and plain HTTP. It is the only Indian forecast product covering the
whole Cape Town–Bharati corridor. INCOIS's *ocean* forecasts, by contrast, stop
at 30–45°S — north of the ice zone entirely, and east of 30°E, which does not
even include Cape Town.

---

## 2. The candidates, verified

### 2.1 NCPOR — station observations, not gridded products
`data.ncpor.res.in` publishes Antarctic meteorological data from Indian
stations: **Maitri 1984–2021**, **Bharati 2012–2024**, Dakshin Gangotri
1982–2010, plus GPS and magnetometer series. Direct ZIP/TXT/Excel download,
some request-only. The portal states plainly that "the listed Datasets are raw
data, not linked with metadata"; observation cadence is not published and there
is no licence text (`UNVERIFIED`). **No gridded product of any kind** —
no sea ice, no forecast, no bathymetry.

### 2.2 INCOIS — Indian Ocean, with one global exception
Read directly from the THREDDS catalogue:

| Product | Domain | Resolution | Horizon | Reaches the corridor? |
|---|---|---|---|---|
| **Global WW3** (waves + winds) | 80°S–70°N, all lon | 1° | 9.75 d / 3 h | **Yes** |
| RSMC combined WW3 | 30–120°E, 60°S–30°N | 0.1° | 7 d | No — starts at 30°E |
| RSMC HYCOM | 20–120°E, **45°S**–31°N | ~0.06° | 7 d | No — stops at 45°S |
| CURRENTS_IO | 30–120°E, 30°S–30°N | 1/12° | 4 d | No |
| INCOIS-GODAS | global analysis | 0.25° | analysis only | Not a forecast |

Every INCOIS-*produced* gridded dataset on ERDDAP is bounded 30°S–30°N,
30–120°E. Only Indian Argo float positions reach 69.7°S. **There is no INCOIS
sea-ice product.** The ship-routing advisory exists but is registration-gated
and its Antarctic coverage is `UNVERIFIED`.

### 2.3 ISRO / SAC / MOSDAC / NRSC
- **EOS-06 SCAT sea ice** — as §1. Algorithm per the SAC ATBD: σ⁰ thresholds
  (> −25 dB winter, > −28 dB summer), polarisation ratio, 4-day σ⁰ standard
  deviation, temporal coherence (3 of 4 days), spatial coherence (≥5 of 9),
  masked by climatological maximum extent. Heritage validation on SCATSAT-1 at
  2.25 km: **~96.1 % class agreement against AMSR2-ASI** (2017–18). The ATBD
  itself concedes the scatterometer "slightly underestimates" ice relative to a
  radiometer, with ~5 dB backscatter drop in summer melt and ambiguity under
  high wind or thin ice — an honest document.
- **A 2.25 km South-Pole backscatter/brightness product exists**, but the
  2.25 km *sea-ice extent* product is generated for the **North Pole only**.
- **SCATSAT-1** operated 2016–2021, but its sea-ice product stopped in May 2019
  — two years before the satellite failed. Worth noting as a continuity risk.
- **VEDAS polar GeoServer** carries daily SCATSAT-1 Antarctic layers in
  EPSG:3031 to March 2021 and **nothing after** — it was not continued onto
  EOS-06.
- **AGEOS at Bharati** (commissioned 2013) receives Cartosat, SCATSAT-1 and
  Resourcesat, up to ~10 passes/day. Whether it receives EOS-04/EOS-06, and
  any Antarctic SAR tasking, is `UNVERIFIED`.
- **Bhuvan is disqualified on its own terms**, independent of coverage: its
  terms of use prohibit use "for, or in connection with real time navigation
  or route guidance". That is exactly what this product does.

### 2.4 IMD / NCMRWF
IMD has observed in Antarctica since 1981 and runs **Polar-WRF at 3 km, driven
by GFS T1534, out to 72 h, specifically for Maitri and Bharati**, with
published verification at Maitri (MSLP RMSE 3.4→2.0 hPa at 24 h; 10 m wind
correlation 0.7→0.9). It is the finest-resolution Antarctic NWP available to
this project by a wide margin. **But the output is charts and meteograms —
there is no gridded download**, which is what stops it being an input rather
than a reference. NCMRWF's NCUM global runs at 12 km and covers Antarctica by
construction; external gridded access is `UNVERIFIED`.

---

## 3. Verdicts — the §29 justification, one line per capability

| Capability | Source | Why an Indian source was or was not selected |
|---|---|---|
| **Sea-ice observation** (training target) | NSIDC CDR G02202 **retained**, plus **EOS-06 SCAT L3 GS adopted as an independent daily ice-edge check** | The Indian product is extent-only with a 2.3-year record — it cannot train a concentration model or supply a 48-year climatology. It *is* competitive on resolution (12.5 km vs 25 km) and latency, and it is different physics, so disagreement between them is informative. Adopted for what it is good at. |
| **Sea-ice / ocean forecast** | CMEMS GLO12 **retained** | No Indian system forecasts sea ice at all, and INCOIS's ocean forecasts stop at 30–45°S. This is the legitimate "the Indian option does not cover Antarctica" answer, verified against the grids rather than assumed. |
| **Wave / wind forecast** | GFS-Wave / GFS **retained**; **INCOIS global WW3 evaluated as a fallback** | INCOIS reaches 80°S with 10-day, 3-hourly output and open OPeNDAP — genuinely usable. But 1° against 0.25°, with Southern Ocean skill `UNVERIFIED` and no licence text. Worth a skill check against ERA5 before adoption; not primary today. |
| **Icebergs** | USNIC catalogue **retained** | No Indian catalogue exists. Worth stating without overclaiming: Indian scatterometer data (OSCAT, SCATSAT-1) already feed the BYU/NIC iceberg record we use. |
| **Bathymetry** | GEBCO / IBCSO v2 **retained** | No Indian Antarctic bathymetry found, and no Indian institution among IBCSO v2's ~145 contributors. |
| **Protected areas** | ATS register **retained** | The legal authority under the Treaty, to which India is a Consultative Party. There is no substitute and it would be wrong to look for one. |
| **Routing engine** | PolarRoute + meshiphi **retained** | No Indian polar routing engine exists. INCOIS's ship-route service is Indian-Ocean and registration-gated. |
| **Terminal-area weather** | **IMD Polar-WRF adopted as approach guidance** | The only 3 km Antarctic NWP for our two destinations, with published verification. Chart-only, so it informs the terminal phase rather than feeding the router. |
| **Validation and ground truth** | **NCPOR / IMD station records, Indian Argo, the 2025 INCOIS glider — selected outright** | See §4. |

---

## 4. Where India is the right answer, and it is not a consolation

**The two long station records at our two destinations are Indian.** Maitri
1984–2021 and Bharati 2012–2024 are the only multi-decade observations at the
corridor's endpoints. They are the correct validation set for forecast wind and
pressure, and for the melt-season behaviour of any ice-edge product near Prydz
Bay and the Schirmacher coast — which is precisely where both passive microwave
and ML sea-ice models degrade, and precisely where our own product makes its
sharpest claim. This is not a gridded input, and it is what makes the accuracy
claims defensible to the organisation that will judge them.

**An independent ice-edge observation on different physics.** EOS-06 SCAT is
Ku-band backscatter; NSIDC is passive microwave. Where they disagree is
information, and §48A.16 asks for source disagreement to be first-class. This
is a better use of the product than pretending it can replace the CDR.

**In-situ along the actual transit.** Indian Argo floats to 69.7°S, NPDC's
Southern Ocean Expedition data, and the autonomous glider INCOIS deployed
during the 44th ISEA (December 2025, from *MV Vasiliy Golovnin* — our own
modelled vessel) are the Indian in-situ record along this exact route.

---

## 5. The headline, for a judge from MoES or NCPOR

> Our source strategy is capability-driven, and it was checked against live
> Indian endpoints rather than assumed. The best Antarctic sea-ice record is
> American — NSIDC's 48-year, 25 km concentration CDR — and the best ice–ocean
> forecast is European, CMEMS at 1/12° with concentration, thickness and drift.
> No Indian system forecasts sea ice, and INCOIS's ocean forecasts stop at
> 30–45°S, well north of the ice. India does, however, field two products that
> genuinely cover this corridor: ISRO's EOS-06 scatterometer Global Sea Ice, at
> 12.5 km daily and active since June 2024, and INCOIS's global WAVEWATCH III
> reaching 80°S. We adopt the first as an independent daily ice-edge check and
> evaluate the second as a wave and wind fallback. Where India is clearly best —
> four decades of IMD and NCPOR station observation at Maitri and Bharati,
> IMD's 3 km Polar-WRF at the terminals, and Indian Southern Ocean expedition,
> Argo and glider data — those sources are used for validation and
> terminal-phase guidance, which is where the accuracy of the whole product is
> actually proven. Nothing was chosen or rejected for reasons of origin.

---

## 6. Still UNVERIFIED — stated, not papered over

MOSDAC's EOS-06 sea-ice product **data format and licence** (registration
required); INCOIS THREDDS terms of use and the Southern Ocean skill of its 1°
WW3; how sea ice is handled inside that WW3 run; NCMRWF gridded access; the
NPDC data policy text; whether AGEOS receives EOS-04/EOS-06 and any Antarctic
SAR tasking; the USNIC update cadence (not stated on the product page); Indian
Naval Hydrographic Office Antarctic charting (none found, but absence is
unproven); and the interpretation of the VEDAS 500 m 35-day composites.

Two of these gate an adoption and are filed in `docs/backlog.md`: the EOS-06
licence and format, and an INCOIS WW3 skill check against ERA5.
