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

---

## 6. Where sea-ice concentration products actually fail

Researched 2026-09-02. This is the evidence base for "IcySea and its peers do
not have accurate ice maps" — a claim that is true, but only precise when it is
attached to numbers.

Every operational ice service, IcySea included, is built on top of the same
passive-microwave concentration retrievals. Their failure modes are therefore
*our* failure modes too, and stating them first is stronger than being asked.

### 6.1 Resolution is not grid spacing

- SSMIS 19 GHz footprint is roughly **70 × 45 km**, gridded to 10–25 km. The
  grid is finer than the measurement.
- AMSR2 footprints: 6.9 GHz 62 km · 18.7 GHz 20 km · 36.5 GHz 10 km · 89 GHz
  5 km, gridded to 25 / 12.5 / 6.25 km.
- NSIDC states plainly that the ice edge derived from 25 km passive microwave
  can be **off by 25–50 km** versus higher-resolution systems.

**Consequence for us:** we cannot see a lead narrower than a cell, and the
feature a master most wants to exploit is exactly that. We route to the *region*
where leads are likely, never to a lead.

### 6.2 Thin ice is systematically under-read

- **All** algorithms underestimate concentration for ice thinner than ~25 cm,
  and most retain a ~5% negative bias even above 30 cm (Ivanova et al. 2015).
- Saturation thickness by algorithm: N90 20–25 cm · OSI-SAF 25–30 cm · NASA
  Team 30–35 cm.
- For the Antarctic marginal ice zone specifically, thin ice (dark nilas,
  grease) and slush are reported as the single largest cold-season error source
  (Stentella et al. 2026). *Caution: the journal page and the preprint summary
  quote different magnitudes (up to 70% vs up to 30%) — verify against the
  published figure before quoting a number.*

**Consequence:** new and young ice — the ice a ship can actually break — is the
ice the sensor is worst at. This cuts both ways and is worth saying out loud.

### 6.3 Coastal contamination, in both directions

- Land emissivity resembles ice emissivity, so brightness temperature is
  contaminated **several tens of kilometres** from the coast, and uncorrected
  retrievals **overestimate** coastal SIC (false ice).
- The corrections then overshoot: Lavergne et al. 2019 notes corrections are
  "not perfect, and some false sea ice remains", and that **true coastal ice can
  also be removed**.
- NSIDC's AMSR2 spillover correction analyses a **7 × 7 pixel (87.5 km)**
  neighbourhood and assumes land pixels radiate like 90% SIC.

**This is the mechanism behind our own measured finding** (§ `isih/ice_quality.py`,
`RESULTS.md §2`): the CDR's land-spillover filter zeroes coastal cells and
writes `0.0`, which reads as open water. The literature describes the
overestimate; what bites us operationally is the **overcorrection**, at exactly
the cells nearest a station.

### 6.4 Weather filters delete real ice

- The OSI-401 open-water filter threshold is 10%, plus a 7 °C air-temperature
  mask.
- Cost, quantified: the classic gradient-ratio filters wrongly zero out **27% of
  pixels at a true SIC of 15%**, and 9% at 20% (Ivanova et al. 2015).
- Lavergne 2019 confirms the filter "also has the effect of removing some amount
  of true low-concentration ice, especially in the marginal ice zone."

**Consequence:** the MIZ — where a ship makes its most consequential decisions —
is where the products are most aggressively censored.

### 6.5 The between-algorithm spread is the honest error bar

From the 30-algorithm round robin (Ivanova et al. 2015), standard deviation at
**low concentration (15% SIC)**:

| Algorithm | NH SD | Algorithm | NH SD |
|---|---|---|---|
| 6H | 2.8% | Bristol | 6.6% |
| CalVal | 3.8% | Bootstrap-P | 13.5% |
| OSI-SAF hybrid | 4.7% | ASI | 28.5% |
| NASA Team | 5.4% | N90 | 28.8% |

**Roughly a 10× spread between algorithms at low concentration**, and the
Southern Hemisphere is worse (N90 35.0%). At high concentration (75%) the spread
collapses to 2.9–9.0%.

> **The line for a judge:** "There is no such thing as *the* sea-ice
> concentration. At the ice edge, published algorithms disagree with each other
> by an order of magnitude more than they do in the pack. Any system that
> presents a single number without an error bar is hiding that."

### 6.6 The Antarctic is measurably harder than the Arctic

- Ozsoy-Cicek et al. 2009, against ASPeCt ship observations: **R² = 0.41**;
  AMSR-E may underestimate ice area inside the ice edge by **up to 14%
  (~1.5 million km²)**, and placed the ice edge **38–102 km too far south**.
- NSIDC AMSR2 vs VIIRS: bias 3.9% / RMSE 11.0% (Arctic) versus bias 4.45% /
  RMSE 8.8% (Antarctic).
- Mechanism: Antarctic summer surfaces are dominated by thick snow, **flooding
  and snow-ice formation**, not the melt ponds that drive Arctic error.

*Flag:* no published Antarctic melt-pond-fraction number was found. "Antarctic
ponding is weaker" is physically well-supported (Andreas & Ackley 1982) but
quantitatively **unverified** — do not put a number on it.

### 6.7 Forecast skill: the bar is lower than people assume

- **SIPN South** (Massonnet et al. 2023), 22 contributors, >3000 forecasts:
  **only 51% (42 of 82) of predictions beat a plain climatological forecast**
  in CRPS. Dynamical models did not beat statistical ones (mean CRPS 0.49 vs
  0.57 million km²); for spatial information in Dec–Jan, statistical models
  performed *better*.
- **The exploitable gap:** the authors state they did **not** implement
  persistence or anomaly-persistence benchmarks, calling it "not always
  straightforward" for series with a marked seasonal cycle. Our prototype's
  entire result is measured against persistence. That is a genuine
  methodological edge, not a marketing line.
- Ice-edge subseasonal skill vs climatology: ECMWF ~38 days, multi-model ~60
  days, individual members 30–38 days.
- Massonnet 2023 on the regime shift: the system "appears to be in a
  non-stationary state where **climatology is, by definition, not meaningful**."
  This is the cleanest available justification for why trend- and
  climatology-based statistical models broke after 2016.

### 6.8 Uncertainty is shipped — and is knowingly incomplete

- OSI SAF ships per-pixel `algorithm_uncertainty`, `smearing_uncertainty` and
  `total_uncertainty`. Typical σ_algo is 2–3% SIC; **σ_smear reaches 40% SIC at
  the ice edge** and ~0% in homogeneous areas.
- So **total uncertainty is dominated by smearing exactly where a ship needs
  it** — at the edge.
- **The admission worth quoting:** Lavergne et al. 2019 states explicitly that
  melt-pond misinterpretation, the thin-ice effect, and the open-water-filter
  effect are **not included** in the shipped uncertainty variables. What ships
  is a *precision* estimate, not a total error budget.
- The NOAA/NSIDC CDR we use ships `cdr_seaice_conc_stdev` per pixel. **We are
  not currently using it.** It belongs in the input channels and in the
  conformal calibration.

### 6.9 The white space

**No study was found that propagates sea-ice concentration or forecast
uncertainty into a routing decision.** Nearest neighbours:

- ice-chart uncertainty impact on operational planning, Kara Sea (OMAE2022-79051)
- probabilistic ice drift for search-and-rescue (Rabatel et al. 2018, 10-day)
- **directly relevant precedent:** an optimum-route study for the
  **Bharati–Maitri** leg, *Polar Science* 2021 — **deterministic ice and wind
  resistance only, no uncertainty**.

*Confidence: medium.* The agent's web-search budget ran out mid-task and this
rests on Crossref queries. Re-verify before claiming novelty in a deck.

**That Indian precedent matters twice over:** it proves the problem is
recognised in the Indian Antarctic programme, and it marks precisely where we
add something — the same corridor, done probabilistically.

### 6.10 Manual ice charting is not ground truth either

Cheng et al. 2020, Canadian Ice Service analysts on RADARSAT-2:

- analyst SIC matched automated segmentation **exactly only 39%** of the time
  (84% within ±1/10)
- inter-analyst agreement Krippendorff's α = **0.779**
- analysts **systematically overestimate** SIC in the 1/10–3/10 range
- named ambiguities: open water under low wind looks like first-year ice;
  surface meltwater mimics open water

**Consequence:** validating against ice charts has its own error floor. Two
experts disagree materially. This is an argument for calibrated intervals rather
than a single number — which is our differentiator D1.

### 6.11 What this section licenses us to say

- ✅ "The products every ice service depends on disagree by ~10× at the ice edge."
- ✅ "Shipped uncertainty excludes three known error sources, by the producers'
  own admission."
- ✅ "Antarctic retrievals are measurably worse than Arctic ones, and most tools
  are Arctic-first."
- ✅ "Half of Antarctic seasonal forecasts fail to beat climatology."
- ❌ Do **not** say "IcySea is inaccurate." We have not tested IcySea. We have
  characterised the data layer beneath it, which is a different and defensible
  claim.

---

## 7. Physical ice hazards — what the 25 km field cannot see, and what closes on a ship

Researched 2026-09-02. Route context: Cape Town → Maitri (Princess Astrid
Coast) and Bharati (Larsemann Hills, Prydz Bay), December–April.

### 7.1 The scoping blocker: there is no summer Antarctic drift product

> **OSI SAF OSI-405-d sea-ice drift is produced for the Southern Hemisphere
> ONLY between 1 April and 31 October.**

Our entire resupply season — December to March — falls in the gap. Copernicus
SAR-derived Antarctic drift is reprocessed-only. So any convergence, deformation
or compression layer must come from:

- **modelled** ice velocity: CMEMS `GLOBAL_ANALYSISFORECAST_PHY_001_024`,
  `siu`/`siv`, 1/12° (~9 km), 10-day forecast, daily, coverage to 80°S; or
- in-house Sentinel-1 feature tracking.

This must be settled before any compression work starts. It is a *data
availability* constraint, not a modelling choice.

### 7.2 Ice compression — the "sandwiching" hazard, and a genuine white space

**No operational Antarctic ice-pressure product exists anywhere in the world.**
AARI forecasts gridded compression, but only for the Barents and adjacent Kara
Sea. Canada's CAPS runs Arctic-only. Finland and Sweden publish no gridded
Baltic pressure field — compression reaches Baltic mariners as icebreaker
observations plus a narrative text forecast.

**IMO POLARIS is provably blind to it.** Read end to end, MSC.1/Circ.1519 does
not contain the words *pressure*, *compression*, *ridge*, or *drift*. RIO is
concentration × ice-type only. The MANICE egg code likewise encodes
concentration, stage and floe size, and no pressure.

**Physical drivers** (AARI, Buzin/Klyachkin/Frolov 2022): compression arises
from *gradients* in drift speed and direction; obstacles — coast, islands,
grounded stamukhi, **landfast ice** — are decisive; onshore winds produce the
strongest coastal compression. Their normative statement is directly
operational:

> *The most dangerous case for shipping is compression at the fast-ice edge when
> the general drift sets into it at an angle.*

★ **That is exactly the Bharati and Maitri offloading geometry** — a ship sitting
at the fast-ice edge — and it is a computable geometric test: onshore wind
component × concentration × distance to a blocking boundary.

**Concentration threshold:** strong compression occurs predominantly at 10/10
concentration; local compression at 7–9/10. This corroborates the classical
compactness ≈ 0.8 free-drift limit and USNIC's own 80% pack/MIZ split — the same
80% our vessel config uses.

**Formulas that exist and are usable:**

| Quantity | Expression | Constants |
|---|---|---|
| Ice strength (Hibler 1979) | `P = P* · h · exp[−C(1−A)]` | **P\* = 27 500 N m⁻², C = 20**, ellipse e = 2.0 |
| Ice pressure in a model | `p = −(σ₁₁ + σ₂₂)/2` | |
| Divergence | `ε̇_div = ∂u/∂x + ∂v/∂y` | |
| Shear | `ε̇_shr = ½√[(∂u/∂y+∂v/∂x)² + (∂u/∂x−∂v/∂y)²]` | |
| Drift-error law (Dierking 2020) | `σ_div ≈ √2·σ_tr /(ΔT·L)` | grid spacing and timestep decide whether signal survives |
| Free drift | `U_i = α e^(−iθ)U_a + U_w` | α ≈ 2%, θ ≈ 20–40° **left of wind in the SH** |

★ **The uncertainty consequence that matters to us.** Hibler strength is
*exponential* in concentration with C = 20, so `dP/P = 20·dA`. **A 5-percentage-
point SIC error changes modelled ice strength by 2.7×; a 10-point error by
7.4×.** Any compression layer built on 25 km passive microwave inherits that
amplification. This is the strongest possible argument for our uncertainty work
— and equally a warning against shipping a compression number without one.

**The best published computable proxy is ridged-ice production rate**, not
pressure. Pärn, Haapala & Kõuts (2007) diagnosed two Gulf of Finland hull
damages using 24 h growth of deformed-ice thickness: **0.1–0.3 m/day at the
damage sites, peak 1.4 m/day nearby**, in ≥95% concentration. Their
counter-intuitive result is worth quoting:

> *"Low winds (≈4 m/s) with variable direction are able to cause strong ice
> deformation, but stronger steady winds (≈9 m/s) may result in a lower
> deformation rate."*

**Wind-direction change matters more than wind speed.** Their own caveat:
modelled stresses (~0.01–0.03 MPa) are two orders below actual ship–ice impact
stresses.

**AARI 0–3 compression scale:** 0 none/dispersing · 1 weak, patches of open
water remain · 2 noticeable, open water closes, ridges break and re-form · 3
strong continuous ridging. Grades 2–3 cut transit speed by **50–95%**.

### 7.3 Besetting — including an Indian-programme incident

- ★ **MV Magdalena Oldendorff — the directly relevant case.** Chartered as
  support ship for the **20th Indian Antarctic Expedition**. Beset **11 June
  2002** near Novolazarevskaya (Muskegbukta Bay) on her second voyage to Maitri.
  SA Agulhas lifted out 79 Russian scientists and 11 crew by helicopter; **ARA
  Almirante Irízar failed to free her**; she overwintered and self-released in
  late November 2002 — roughly **5.5 months beset**. She is a ULA-class SA-15,
  designed to break 1 m level ice continuously — *the same ice class as
  Golovnin*. **Caveat: source dates conflict and no primary ATCM/COMNAP document
  was located. Verify before presenting.**
- **MV Akademik Shokalskiy, 25 Dec 2013 – 7 Jan 2014, Commonwealth Bay — in peak
  austral summer.** Antecedent: iceberg **B09B grounded there in Dec 2010**,
  producing year-round fast ice up to 3 m thick. **Xue Long stalled at 6 nmi and
  became beset itself**; Aurora Australis abandoned the attempt at ~10 nmi
  rather than risk besetting. **Release mechanism: a wind-direction change
  loosening the pack — divergence, not icebreaking.**
- Statistics: 1922–1990, 10 ships lost on the Northern Sea Route, **9 of them to
  compression**. Hudson Strait vessels are beset on average **40% of total
  voyage time**.
- Dawson et al.: *"ice under pressure … is very difficult to detect, observe, or
  predict, and ship captains are often unaware until their vessels become
  beset."*
- **No besetting incident could be documented for any Indian-flagged vessel**
  (Sagar Kanya, Ivan Papanin, Vasiliy Golovnin). That is an evidence gap, not a
  null result — NCPOR expedition reports would settle it.

### 7.4 What the 25 km concentration field cannot see

| Hazard | Visible at 25 km? | Note |
|---|---|---|
| Ice pressure / compression | **No** — no observable at any resolution | Sub-grid pressure exceeds grid mean by ~4×; a ship is 10⁻³ of a cell |
| Pressure ridges, rafting, hummocks | **No** | The dominant resistance term |
| Fast ice vs pack ice | **No** | AMSR2 at 6.25 km already misplaces the Prydz Bay fast-ice edge vs MODIS |
| Leads, tide cracks | **No** | 25 km is ~250× a navigable lead |
| Icebergs < ~6 km | **No** | USNIC tracks ≥ ~18.5 km; BYU ~6 km |
| **Growlers, bergy bits** | **No** | See below — the critical honesty point |
| Thin ice (nilas, grey) | Underestimated | Algorithms calibrated for thick FY/MY ice |
| Anything within 25–50 km of coast | Contaminated | Many studies simply mask 50 km — that mask covers *both* Indian station approaches |
| Summer melt state | Corrupted | Wet snow corrupts emissivity in exactly the Dec–Mar window |
| Floe size distribution | **No** | No operational product; MIZ is a concentration band only |

★ **The growler gap, stated precisely.** A growler is < 1 m above water, < 5 m
long, ~87.6% submerged (≈7 m keel), glacier ice at ρ ≈ 900 kg/m³ that does not
fail in bending like sea ice. Bowditch: growlers *"cannot usually be detected at
ranges greater than four miles, and are lost in a sea greater than four feet."*
Sentinel-1 EW detection rates in **best-case** conditions: **< 60 m bergs
5–13%**; 60–120 m 41–70%; > 120 m 83–96% — the authors conclude accuracy *"is
still too low for an unsupervised mapping of iceberg positions to be used for
navigation."*

> **The gap between the smallest operationally tracked object and the classic
> hull-holing hazard is 3.5 orders of magnitude.** Our product must never imply
> a growler warning. That is a radar-and-lookout problem.

**Optical rescue is not available:** Southern Ocean mean cloud fraction is
**0.82–0.86**, highest in summer.

**There is no near-real-time Antarctic landfast-ice product.** The Fraser
circum-Antarctic product (1 km, 15-day) ends March 2018.

### 7.5 Summer blizzards and katabatic winds

**Definition (Australian Antarctic Division):** gale force or stronger for at
least one hour, temperature < 0 °C, **visibility ≤ 100 m**.

**Mechanism:** radiative cooling over the ice sheet drains dense air downslope,
deflected **20–50° left of the fall line** in the Southern Hemisphere. Coastal
katabatics can exceed 100 km/h for days; a seven-day Mawson blizzard ran
100–148 km/h sustained with one gust at **244 km/h**.

★ **Crucially, Turner et al. (2009)** — the continent-wide 60-year study — find
strong wind events are *"a feature of the extended winter season"*, and that
around East Antarctica the significant majority arise from **katabatic flow
enhanced by the synoptic circulation**. Pure katabatic is the background; the
damaging events are katabatic × cyclone.

**At Maitri (Indian data, *Mausam*, 1990–2005):**

| | |
|---|---|
| Blizzards per year | ~21, affecting the station on **45 days/year** |
| Peak month | August, ~7 blizzard days |
| Mean wind during blizzards | **52 kt**, exceeding 100 kt on several occasions |
| Mean duration | **25 h**; longest **168 h** (June 1997); 12 events over 72 h |
| Direction | Katabatics highly directional from the **southeast** |

The source states explicitly that blizzard frequency is **highest in winter and
lowest in summer**. *Derived estimate, flagged as such: with 15–20 of the 21
annual events in April–August, December–March plausibly sees **0–2 blizzards per
season** at Maitri.* Rare is not absent — the Shokalskiy was beset on Christmas
Day, and a single 25-hour event at 52 kt moves the ice field ~30 km.

**Operational impact:** cargo and personnel transfer stops; visibility in blowing
snow falls below the growler-lookout threshold precisely when radar is also
degraded by sea state; the ice field reorganises within hours — at 30 m/s free
drift is ~**52 km/day**.

★ **The resupply window is the breakout window.** Prydz Bay fast ice at
Zhongshan/Davis reaches **1.59 ± 0.17 m** maximum and **breaks up mid-December
to late January, associated with passing cyclones.**

**Katabatics as opportunity:** East Antarctic surveys identify **28 coastal
latent-heat polynyas** opened by offshore katabatic flow. *Caveat: mean maximum
extent is June–October* — principally a winter feature. In summer they merge
with open water, so the routing opportunity in Dec–Mar is better framed as
**offshore-wind-driven opening events** than as named polynyas.

**Forecast sources and their limits:**

- **AMPS** (polar WRF, real-time): domains at 24, 8, 2.67 and 0.89 km; 120 h
  outer, 39 h nests; free. *Whether any sub-8 km nest covers Dronning Maud Land
  or Prydz Bay is unconfirmed — the domain-map pages 404'd.*
- **ERA5** correlates r = 0.91 with ASCAT for summer Antarctic coastal
  easterlies, mean bias −0.51 m/s — **but −3.89 m/s above 20 m/s**, worst near
  complex orography. Turner et al. reach the same conclusion.

> ★ **ERA5 will under-forecast exactly the winds that beset ships.** Any
> wind-driven hazard layer must bias-correct or say so.

### 7.6 The closest precedent to what we are building

**CHINARE FIPS** (Fast Ice Prediction System) runs a HIGHTSI-class model at
**0.125°, 10-day forecast, for 68.375–69.75°S / 73.5–79°E** — which is
**precisely the Bharati approach**. It is the nearest existing system to our
station-approach problem and should be checked for obtainable outputs before we
build anything similar.

### 7.7 Explicit uncertainties in this section

Carried forward verbatim from the research, because they bound what we may
claim:

- Growler collision-energy figures and drift-divergence noise floors were
  **calculated, not cited**.
- The Maitri summer blizzard count (0–2/season) is **derived** from the monthly
  breakdown, not stated in the source.
- Magdalena Oldendorff dates **conflict across sources**; no primary document
  found.
- AMPS nest coverage of Dronning Maud Land / Prydz Bay is **unconfirmed**.
- The Southern-Hemisphere free-drift turning angle: direction (left of wind) is
  certain; the **20–40° magnitude is inferred from Northern-Hemisphere Nansen
  values with the sign mirrored**, not SH-verified.
