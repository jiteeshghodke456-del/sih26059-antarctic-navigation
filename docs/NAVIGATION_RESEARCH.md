# Navigation Research — verified findings (2026-09-01)

Research-only. Facts verified this session by reading primary sources or installed
source code. **No design decision here is approved yet** — proposals live in
`docs/backlog.md` until an ADR is written.

Prompted by a review of `isih/figures/route_map.png`: the straight-line comparison
is a strawman, and the prototype does not yet address the problem statement's
two-phase (open-ocean → ice) structure, ice-class constraints, iceberg CPA, or
multi-vessel effects.

---

## 1. IMO POLARIS — the answer to "ice class constraints"

Source: **IMO MSC.1/Circ.1519, 6 June 2016**, "Guidance on methodologies for
assessing operational capabilities and limitations in ice", Appendix (POLARIS).
Full text retrieved and parsed. Referenced by the Polar Code; the framework named
on the Polar Ship Certificate / in the PWOM.

### Formula

    RIO = (C1 x RIV1) + (C2 x RIV2) + ... + (Cn x RIVn)

`Ci` = concentration of ice type *i* **in tenths**; `RIVi` = Risk Index Value for
that ice type at the ship's ice class.

### Decision thresholds (Table 1.1)

| RIO | Ice classes PC1–PC7 | Ice classes below PC7 |
|---|---|---|
| `RIO >= 0` | Normal operation | Normal operation |
| `-10 <= RIO < 0` | Elevated operational risk | Subject to special consideration |
| `RIO < -10` | Subject to special consideration | Subject to special consideration |

§1.5.3: for **voyage planning**, regimes flagged "special consideration" *should be
avoided*. §1.4.5: areas of elevated risk should also be avoided in planning, or
carry a documented contingency plan.

### Speed limits under elevated risk (Table 1.2)

| Ice class | Recommended speed limit |
|---|---|
| PC1 | 11 knots |
| PC2 | 8 knots |
| PC3–PC5 | 5 knots |
| Below PC5 | 3 knots |

### Risk Index Values — Table 1.3 (standard, non-decayed)

Columns are WMO stage of development.

| Ice Class | Ice-Free | New | Grey | Grey-White | Thin FY 1st | Thin FY 2nd | Med FY <1 m | Med FY | Thick FY | Second Year | Light MY <2.5 m | Heavy MY |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PC1 | 3 | 3 | 3 | 3 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 1 |
| PC2 | 3 | 3 | 3 | 3 | 2 | 2 | 2 | 2 | 2 | 1 | 1 | 0 |
| PC3 | 3 | 3 | 3 | 3 | 2 | 2 | 2 | 2 | 2 | 1 | 0 | -1 |
| PC4 | 3 | 3 | 3 | 3 | 2 | 2 | 2 | 2 | 1 | 0 | -1 | -2 |
| PC5 | 3 | 3 | 3 | 3 | 2 | 2 | 1 | 1 | 0 | -1 | -2 | -2 |
| PC6 | 3 | 2 | 2 | 2 | 2 | 1 | 1 | 0 | -1 | -2 | -3 | -3 |
| PC7 | 3 | 2 | 2 | 2 | 1 | 1 | 0 | -1 | -2 | -3 | -3 | -3 |
| IA Super | 3 | 2 | 2 | 2 | 2 | 1 | 0 | -1 | -2 | -3 | -4 | -4 |
| IA | 3 | 2 | 2 | 2 | 1 | 0 | -1 | -2 | -3 | -4 | -5 | -5 |
| IB | 3 | 2 | 2 | 1 | 0 | -1 | -2 | -3 | -4 | -5 | -6 | -6 |
| IC | 3 | 2 | 1 | 0 | -1 | -2 | -3 | -4 | -5 | -6 | -7 | -8 |
| Not ice strengthened | 3 | 1 | 0 | -1 | -2 | -3 | -4 | -5 | -6 | -7 | -8 | -8 |

Table 1.4 (decayed-ice variant) exists and gives higher RIVs for some types, but
§1.1.3 restricts its use to cases where **ice decay is confirmed by ice information
or visual observation by qualified personnel**. Not usable from a forecast alone.

### Two clauses that answer two other requirements directly

- **§1.7.3 — glacial ice**: "a safe stand-off distance should be observed by the
  ship. This stand-off distance should be recorded in the PWOM." This is the
  problem statement's iceberg CPA safety buffer, as a *regulatory* requirement
  rather than an invented one.
- **§1.6.4 — icebreaker escort**: for voyage planning under escort, the RIO derived
  from non-escorted ice data "may be assumed to be modified by **adding 10** to its
  calculated value" (cautioned as an average that varies significantly). This is
  the formal mechanism by which a *following* vessel benefits from a broken track —
  the basis for any convoy / multi-vessel ordering model.

### Consequence for the ML model

RIO is indexed by **ice type**, not concentration alone. WMO stage of development
maps to thickness (new <10 cm; grey 10–15; grey-white 15–30; thin FY 30–70; medium
FY 70–120; thick FY >120 cm). **Therefore POLARIS cannot be computed from a
sea-ice-concentration forecast alone — it requires a thickness forecast too.**
GLORYS12 carries `sithick`; the existing U-Net extends to a second output channel
without architectural change.

Currently `isih/make_route_figure.py` uses `max_ice_conc: 80`, a threshold we chose
ourselves with no external justification.

---

## 2. PolarRoute / meshiphi — capabilities and gaps, read from installed source

Version 1.1.11, read at `site-packages/polar_route/` and `site-packages/meshiphi/`.

### What already exists (reuse, do not rebuild)

- **Objective functions**: `traveltime`, `fuel`, `battery`
  (`route_planner.py:267`). Fuel routing is supported today.
- **Fuel model**: `SDA.fuel_eq(speed, resistance)` returns tonnes/day as a
  calibrated polynomial. Calibrated for the **RRS Sir David Attenborough**, not for
  any Indian vessel.
- **Ice resistance**: semi-empirical Froude-number formula in `SDA.ice_resistance`,
  hull parameters `slender` `[4.4, -0.8267, 2.0]` / `blunt` `[16.1, -1.7937, 3]`.
  Requires `SIC`, `thickness` **and** `density` present, else it silently no-ops.
- **Wind resistance**: real, 8-heading apparent-wind model using ERA5 `u10`/`v10`
  (`calc_wind`, `wind_resistance`, `c_wind`). Feeds `model_resistance` and therefore
  fuel.
- **Route smoothing**: Newton-method relaxation of cell crossings
  (`crossing_smoothing.py`, `_long_case` / `_lat_case` / `newton_smooth`), a
  Snell's-law-style refraction at cell boundaries. Config keys
  `smoothing_blocked_sic`, `smoothing_max_iterations`, `smoothing_merge_separation`,
  `smoothing_converged_sep`. This is what turns a kinked Dijkstra path into a
  sailable one.
- **meshiphi data loaders already shipped** — the open-ocean data plane exists:
  - scalar: `era5_sig_wave_height`, `era5_max_wave_height`, `era5_wave_period`,
    `era5_mean_wave_direction`, `ecmwf_sig_wave_height`, `era5_wind_mag`,
    `era5_wind_dir`, `gebco`, `amsr`, `modis`, `bsose_sea_ice`, `baltic_sea_ice`,
    `icenet`, `visual_iced`, `shape`, `scalar_csv`, `scalar_grf`
  - vector: `era5_wind`, `era5_wave_direction_vector`, `duacs_current`,
    `oras5_current`, `sose`, `baltic_current`, `north_sea_current`, `vector_csv`
- **`icenet.py`** reads a *forecast* SIC NetCDF keyed by date
  (`<hemisphere>_daily_forecast.<YYYY-MM-DD>.nc`). A forecast-ingestion hook already
  exists — our corrected forecast can adopt this contract instead of inventing one.

### Gap 1 — wave-added resistance is dead code (verified)

`wave_resistance(self, w_height)` is **defined** in `SDA.py:223`,
`example_ship.py:222` and `SDA_wind.py:243`, and **called from nowhere**
(`grep -rn "wave_resistance" polar_route/` returns only the three definitions).
`model_resistance` sums only wind resistance + ice resistance.

Waves therefore act **only as a binary accessibility cutoff** —
`abstract_ship.extreme_waves`: `swh > max_wave` makes a cell inaccessible. There is
no wave penalty on fuel or speed anywhere.

Additional latent bug: the dead method reads `self.vessel_params["Beam"]` and
`["Length"]` (capitalised) while `__init__` uses `"beam"` (lowercase) — it would
raise `KeyError` if it were ever wired up as-is.

Consequence: in the open ocean — the Roaring Forties, where most fuel is actually
burned — PolarRoute currently models **no sea-state fuel penalty at all**. This is
precisely the "minimise fuel consumption and avoid severe weather" half of the
problem statement. Note `docs/ML_ARCHITECTURE.md:620` plans a Golovnin subclass
"with wave resistance"; that plan will silently do nothing unless
`model_resistance` is also overridden.

### Gap 2 — the mesh has no time dimension in the router (verified)

`grep` for `time_dependent|timestep|time_step|dynamic` across `polar_route/` and
`meshiphi/` returns nothing in the route planner. `datetime` appears in
`crossing_smoothing.py` only as a `cumsum` over output legs. Mesh time bounds
select and *aggregate* a slice; they do not produce per-timestep mesh layers.

The router therefore **assumes the environment is frozen for the entire voyage** —
17.4 days, in our own computed route. The problem statement explicitly requires
"dynamically recalculate routes based on the daily or hourly movement of ice
layers."

This is the gap that makes a forecast *usable*: a static router cannot consume a
lead-time forecast, because it has no notion of "the ice you will meet when you
actually arrive."

### Already known and recorded elsewhere

- No native iceberg model; `excluded_zones` is the native extension point
  (`docs/backlog.md`, resolved section).
- `gebco.py` loader exists; the GEBCO file was simply never downloaded — the mesh
  reported "no elevation data" for every cell in our run, so the computed route has
  **no depth constraint at all**.

---

## 3. Indian Antarctic logistics — facts for the deck

- **Departure**: Indian Antarctic expeditions are flagged off from **Goa**
  (Mormugao; NCPOR is at Vasco da Gama). Personnel then travel commercially to
  **Cape Town**, where the chartered ice-strengthened vessel embarks on the
  Antarctic leg. The *sea* leg is Cape Town → Bharati → Maitri.
- **Vessel**: **MV Vasiliy Golovnin** (FESCO; built 1988; diesel-electric
  icebreaking container feeder, ~300 TEU, cargo cranes, helipad, self-propelled
  landing barges; IMO 8723426, MMSI 273149510). Chartered by NCPOR/MoES. Also
  chartered historically by Australia, New Zealand and Argentina.
  **A published ice class was not found** — still open in `docs/backlog.md`.
- **Season**: Cape Town ↔ Bharati/Maitri operation is possible **December to
  April**. 43-ISEA: departed Cape Town end of Dec 2023, Bharati mid-Jan 2024,
  Maitri early Mar 2024.
- **Future**: **GRSE signed an MoU with Kongsberg (Oslo, 2 June 2025)** to build
  India's **first indigenous Polar Research Vessel** at Kolkata, to be operated by
  NCPOR. Still exploratory. This is why supporting an **Indian-port departure** is
  forward-alignment with MoES's own direction rather than a hypothetical.

Implication: do **not** put "Goa → Antarctica by sea" on a slide as *current*
practice. An MoES judge will know the charter leg starts at Cape Town.

---

## 4. Antarctic sea-ice non-stationarity — the climate-change question

Reinforces an already-recorded critical risk (`docs/backlog.md`,
`docs/ML_ARCHITECTURE.md` §296/§348/§748) with primary sourcing.

- Antarctic sea-ice extent has mostly sat below the 1981–2010 average since **2016**;
  record-low summer extents in **2022, 2023** and continuing lows through **2025**.
- Winter maximum hit a record low **16.96 million km² on 10 Sep 2023**.
- Published framing: ocean warming has pushed Antarctic sea ice into a **new
  low-extent state** which "exhibits different seasonal persistence characteristics,
  suggesting that the underlying processes controlling Antarctic sea ice coverage
  may have altered" — i.e. a **regime shift**, not merely a trend.
- Drivers: intensified atmospheric zonal waves, poleward warm-moist transport, and
  >1 °C anomalous warming of the Southern Ocean mixed layer, with ongoing warming at
  ~100–200 m depth.

Two consequences that matter for us:

1. **Persistence — our headline baseline — is itself regime-dependent.** "Different
   seasonal persistence characteristics" means the baseline we beat by 18–31 % is
   not a fixed target. Percentage gains must be reported per-regime, not pooled.
2. It sharpens the existing conformal-exchangeability risk: this is exactly the
   distribution shift that breaks the guarantee.

---

## 5. Operational state of the art — what "existing technology" actually means

Needed because our current figure compares against a great-circle straight line,
which no captain sails.

- **PolarView** (ESA) supplies daily radar + passive-microwave ice products to
  Antarctic programme vessels; the Australian Antarctic Program reports crews found
  them "easy to use, accurately reflected ice conditions encountered, enabling ships
  to travel more efficiently than previously possible."
- Ice charts derived from **AMSR2** (JAXA Shizuku, 6.25 km) processed by University
  of Bremen, plus NOAA charts and CryoSat-2, are transmitted to vessels.
- **Helicopter reconnaissance up to ~100 nautical miles ahead** is used to choose
  the actual track.

So the honest state of the art is: **a human master routing on yesterday's observed
ice plus short-range visual recon** — *not* a straight line, and *not* a forecast.
That is the baseline to beat, and it is beatable specifically on **lead time**,
which is where our model's advantage grows (+18.5 % at 1 day → +30.6 % at 7 days).

---

## Sources

- [IMO MSC.1/Circ.1519 — POLARIS](https://www.nautinst.org/static/uploaded/2f01665c-04f7-4488-802552e5b5db62d9.pdf)
- [PAME — POLARIS](https://pame.is/ourwork/arctic-shipping/current-shipping-projects/polaris/)
- [Record low Antarctic sea ice coverage indicates a new sea ice state — Comms Earth & Environment](https://www.nature.com/articles/s43247-023-00961-9)
- [Antarctic Sea Ice #4: Record lows between 2022 and 2025 — Antarctic Environments Portal](https://environments.aq/publications/antarctic-sea-ice-4-record-lows-between-2022-and-2025/)
- [NOAA Climate.gov — 2023 record-low Antarctic sea ice](https://www.climate.gov/news-features/event-tracker/models-test-potential-influence-global-warming-2023-record-low)
- [Navigation in ships: PolarView — Australian Antarctic Program](https://www.antarctica.gov.au/antarctic-operations/travel-and-logistics/navigation/navigation-in-ships-polarview/)
- [Vasiliy Golovnin supplies two Indian Antarctic stations — Polar Journal](https://polarjournal.ch/en/2024/03/25/vasily-golovnin-supplies-two-indian-antarctic-stations/)
- [MV Vasiliy Golovnin crosses into Antarctic Waters on 43rd ISEA — PIB](https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=1993769)
- [India to Build First-Ever Polar Research Vessel as GRSE signs MoU with Kongsberg — PIB](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2133528)
- [Kongsberg Maritime — MoU with India on indigenous Polar Research Vessel](https://www.kongsberg.com/maritime/news-and-events/news-archive/2025/kongsberg-maritime-signs-mou-with-india-to-explore-design-of-indigenous-polar-research-vessel/)
- [VISIR-2: ship weather routing in Python — Geoscientific Model Development](https://gmd.copernicus.org/articles/17/4355/2024/)
- [Autonomous Passage Planning for a Polar Vessel (PolarRoute)](https://arxiv.org/pdf/2209.02389)
