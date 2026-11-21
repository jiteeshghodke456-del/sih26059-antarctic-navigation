# Antarctic Navigation Decision Support System — Technical Brief

**SIH 2026 · Problem Statement 26059 · Prepared for engineering review (MoES / DRDO)**
**Status as of:** repository `origin/main`, last feature commit 8 Sep 2026; daily data harvest running since 31 Aug 2026.
**Scope of this document:** what has been built, the technologies used, the target architecture, the trade-offs behind each choice, and what comes next. It is compiled from the project's own records in `docs/` (index in Appendix A) and adds no new claims.

---

## How to read this document

Every capability is tagged with one of five states. The distinction matters more than usual here, because the project has a working console on **synthetic** conditions *and* a separate console on **real** satellite data, and they must not be confused.

| Tag | Meaning |
|---|---|
| **BUILT · REAL DATA** | Implemented, tested, and running on real observations |
| **BUILT · SYNTHETIC** | Implemented and tested, running on a simulated environment (real physics, invented initial conditions). Badged `SYNTHETIC ENVIRONMENT` on screen |
| **DESIGNED** | Specified in an architecture or decision record, with no code yet |
| **OPEN** | Known gap or unrun experiment, filed in the backlog |
| **WITHDRAWN** | Previously claimed, found to be wrong, retracted in writing |

Numbers carry the project's evidence tags where it matters: **Measured** (a run in the repo produced it), **Sourced** (external citation), **Derived** (arithmetic on measured or sourced values), **Target** (specified, not achieved).

---

## 1. Executive summary

**The problem.** India resupplies Bharati and Maitri stations once a season using a single chartered ice-class ship (MV *Vasiliy Golovnin*) on the Cape Town → Bharati/Maitri corridor. Cargo is not unloaded at a port. It is craned onto fast ice or an ice-shelf edge, and whether that edge is workable on a given day depends on wind-driven ice motion over one to three days. The ship has Iridium-class connectivity south of ~70°S, not broadband.

**The central finding.** The navigation problem is **the last 100 km, not the 5,800 km ocean crossing.** Measured on real NOAA/NSIDC satellite ice for December 2019: Bharati's own mesh cell was closed to this vessel on **23 of 31 days**, while the approach 100 km north was open **31 of 31**. The ocean leg averages about **6 % ice**. (Caveat: the router's coastal cell is ~139 × 49 km, so this comparison is between two adjacent coarse cells. Repeating it at native 25 km resolution is an open item.)

**What exists today.**

- A trained sea-ice correction model (U-Net, 1.93 M parameters). It beats persistence by **+18.5 % at 1 day to +30.6 % at 7 days** RMSE on a held-out season. This is an **upper bound** on forecast skill because of a known leakage path; the test that settles it is written and not yet run.
- A real-data route over real satellite ice, computed by the British Antarctic Survey's open-source router (PolarRoute), with **8.6 days of ideal steaming time**. That figure is not a voyage-duration forecast.
- A **decision layer**: nine named safety gates; route health derived from them rather than scored; a first-class `UNKNOWN` state that can never read as a pass; versioned, attributed master approvals; divergence alerts that name the gate that changed.
- A **bridge console** in the style of an Electronic Chart Display and Information System (ECDIS), plus a physics-consistent synthetic world model. On top of these run a time-aware router, iceberg drift with closest-approach checks against the ship's *future* track, prioritised alerting, and a **measured 7.8 KB daily data pack**.
- A daily archive of the Copernicus Marine (CMEMS) operational forecast, running on GitHub Actions since 31 Aug 2026. It cannot be back-filled, so it had to start on day one.
- A data-quality finding in the incumbent satellite record. The NSIDC Climate Data Record (CDR) writes suppressed coastal pixels as **0.0 % ice (open water)**. That affects the 200 km Bharati approach on **43.2 % of days** (2018–2020). It is corrected in the safe direction: masking moves coastal ice from 46.8 % to 54.6 %.

**What does not exist yet.** The trained model's output does not reach the route. There is no calibrated ensemble uncertainty, no bathymetry in the real-data mesh, and no measured iceberg trajectory error. There is no signed pack, delta sync or key management, and no persistent plan of record. No navigator has ever used the system.

**Cost to date.** ₹0 infrastructure spend: free Kaggle GPU, free GitHub Actions, free and open data, and an MIT-licensed routing engine.

**Honest overall assessment (from the project's own hostile audit).** It scores **70/100**: strong on problem depth, research credibility and defensibility, and weak on measurable impact. The weakness is that no saved ship-day has been proven; the only measurement so far is 0.03 days on one date. The project's own verdict is *"an exceptionally well-evidenced prototype"*, and that is the correct label.

---

## 2. Operational context — the constraints that shape the design

| Constraint | Value | Consequence for design |
|---|---|---|
| Vessel | MV *Vasiliy Golovnin*: LOA 163.9 m, beam 22.4 m, design draft 9.0 m, service speed 16.4 kn (all verified); RS class `KM(★) ULA[2]` (**single-source**; modern IACS equivalent unverifiable from open sources) | Vessel parameters are configuration, not code. Ice limits are labelled assumptions, not certificated figures |
| Comparison vessel | SA *Agulhas II*: IACS PC5 under DNV, "5 kn in 1 m pack ice" (twice-sourced) | Used to test vessel-awareness of the router |
| Voyage length | ~15.2 days at the ship's AIS-observed 8.6 kn average; a real expedition voyage is 2–3 weeks | The best available forecast reaches only 9–10 days, so about 41 % of the route is beyond any forecast at departure (**Derived**) |
| Connectivity | Geostationary VSAT fails south of ~70°S. Iridium Certus peaks at ~704 kbps and is usually far less; legacy service is provisioned for sub-50 KB messages | **The decision engine must run aboard.** A live-API dashboard is not deployable on this ship |
| Forecast availability | The only Antarctic-covering operational ice-ocean forecast is CMEMS `GLOBAL_ANALYSISFORECAST_PHY_001_024`, D+0…D+9, daily. There is no dedicated Antarctic regional ice forecast in CMEMS | The ML model is designed as a *correction* to this forecast, not a replacement |
| Resolution | 25 km passive microwave cannot see growlers (~5 m), leads narrower than a cell, or pressure ridges | Radar and the lookout own tactical hazards. The system works at hours-to-days and tens of km |
| Regulation | IMO Polar Code §11.3 (voyage planning), POLARIS (MSC.1/Circ.1519), MARPOL Annex I Reg. 43 (no heavy fuel oil south of 60°S), Antarctic Treaty protected areas | Decision support, not a navigation system. It never replaces approved Electronic Navigational Charts (ENCs) or type-approved ECDIS |

---

## 3. What has been built

### 3.1 Summary table

| Subsystem | Status | Key evidence |
|---|---|---|
| NSIDC CDR ingestion (1,096 daily files, 2018–2020, 0 failures) | **BUILT · REAL DATA** | `dakshin/download_nsidc.py`, `docs/PROTOTYPE_RESULTS.md` |
| Coastal data-quality layer (QA-flag masking, spillover audit) | **BUILT · REAL DATA** | `dakshin/ice_quality.py`, `dakshin/figures/ice_quality_audit.json` |
| Daily CMEMS forecast archive (GitHub Actions cron, compressed 42.6 MB → ~5.1–5.2 MB/day) | **BUILT · REAL DATA** (two known bugs, §3.2) | `.github/workflows/cmems-harvest.yml`, `scripts/compress_netcdf.py` |
| Sea-ice correction U-Net, trained on Kaggle T4 | **BUILT · REAL DATA** (not consumed by the product) | `models/sic_correction/unet.py`, `dakshin/kaggle/isih_train.ipynb` |
| Real-data route, PolarRoute + meshiphi, Cape Town → Bharati | **BUILT · REAL DATA** (precomputed, single day, single objective) | `dakshin/figures/routes.json`, `dakshin/ice_meshes.py` |
| A/B/C alternative corridors, two-vessel comparison | **BUILT · REAL DATA** | `dakshin/alternatives.py`, `dakshin/figures/vessel_comparison.json` |
| Protected areas (148 polygons: 142 ASPA + 6 ASMA), by legal regime | **BUILT · REAL DATA** | `dakshin/protected_areas.py` |
| Iceberg catalogue (USNIC, 33 bergs as of 27 Aug 2026) + Wagner–Dell–Eisenman drift physics | **BUILT** (physics tested against the paper; never fed real forcing) | `models/iceberg/`, 23/23 tests |
| Decision layer: nine gates, derived health, approval chain, decision log | **BUILT** | `dakshin/decision.py`, `dakshin/gates.py`, `dakshin/demo/decision_service.py` |
| Passage-planning workflow, sign-in → approve → begin navigation, out-of-order steps rejected with HTTP 409 | **BUILT** | `dakshin/workflow.py`, `dakshin/demo/workflow_service.py` |
| Synthetic Southern Ocean world model | **BUILT · SYNTHETIC** | `dakshin/sim/` |
| Time-aware router (cells costed at predicted arrival time), fuel ≠ time | **BUILT · SYNTHETIC** | `dakshin/sim/router.py` |
| Alerting (P1/P2/P3, nine mandated fields, no alert without a route consequence) | **BUILT · SYNTHETIC** | `dakshin/demo/voyage.py` |
| Iceberg forward tracks, 72 h cap, growing uncertainty, closest point of approach (CPA) vs future own-ship track | **BUILT · SYNTHETIC** | `dakshin/sim/bergs.py` |
| POLARIS as a band across plausible ice-class rows, never a single number | **BUILT** | `dakshin/polaris.py` |
| NMEA 0183 sentences and AIS targets | **BUILT · SYNTHETIC** (badged simulated) | `dakshin/demo/` |
| Measured daily pack: 7.8 KB gzip | **BUILT · SYNTHETIC** payload, real compression | `dakshin/demo/voyage.py` |
| Bridge console (ECDIS/OpenCPN idiom, S-52 palettes) + `/legacy` real-data replay console | **BUILT** | `dakshin/demo/static/` |
| MLflow experiment backfill | **BUILT** (local only) | `dakshin/mlflow_backfill.py`, `docs/MLFLOW_SETUP.md` |
| Test suite | **156 tests** pass, plus 7 Playwright browser tests | `pytest dakshin models` |

### 3.2 Data ingestion and quality

- **Observation truth:** NOAA/NSIDC CDR G02202 v6, 25 km south polar stereographic (EPSG:3412), grid **332 × 316** (verified at first ingestion). No authentication. ~368 KB/day.
- **Coastal artifact finding (the project's strongest data result):**
  - The CDR's land-spillover filter writes suppressed coastal pixels as 0.0 %, which reads as open water. This fires on **100 % of days**, averaging ~118 cells/day (max 488).
  - In the 200 km Bharati approach box it affects **43.2 % of days**.
  - **Four of the eight** days Bharati appeared reachable in December 2019 were artifacts reading exactly 0.0 %.
  - The QA flag is now read and those cells are treated as **unknown**, never as 0. The masking makes the router more cautious.
- **Source disagreement.** The CDR's own QA flag contradicts its own concentration field. Both readings are served: at Bharati on 1 Dec 2019, the raw value reads 0.0 % and the quality-checked value reads 30.7 %.
- **CMEMS forecast archive:**
  - Harvested daily at 06:00 UTC by GitHub Actions.
  - Compressed with int16 packing and deflate. Quantisation error is 1.7 × 10⁻⁵ on concentration, about three orders of magnitude below anything downstream uses.
  - This archive is irreplaceable: a forecast *as issued* on a past day cannot be re-downloaded later.
  - **Two live bugs (OPEN):** files are named from the wall clock (risk of a silent D−1 capture), and the harvest bounding box is clipped relative to the training corridor. It also failed once, on a login flag.
- **USNIC icebergs:** archived once (1.9 KB). There is **no history endpoint**, so without a weekly cron no trajectory history accumulates. **OPEN.**

### 3.3 Sea-ice correction model

```
corrected SIC = clip( background SIC + predicted correction , 0, 1 )
```

| Property | Value |
|---|---|
| Architecture | 3-level residual U-Net, **1,929,601 parameters**, zero-initialised head. An untrained or failed model reproduces the background exactly |
| Inputs (12 channels) | Background field valid at target time; last 7 days of observations; innovation (background − newest observation); day-of-year sin/cos; validity mask |
| Background (prototype) | CMEMS GLORYS12 reanalysis, regridded area-weighted to the NSIDC grid (observations are never resampled) |
| Truth | NSIDC CDR, corridor 5°W–85°E, 48°S–80°S, 2019–2020 |
| Split | Contiguous temporal 70/15/15; test scored **exactly once**. An earlier +27 % figure from epoch selection on the test set was withdrawn |
| Compute | Free Kaggle T4, ~1–2 hours |

**Results (test set, RMSE, lower is better):**

| Lead | Model | Persistence | Raw GLORYS12 | Gain vs persistence |
|---|---|---|---|---|
| 1 day | **0.0465** | 0.0570 | 0.1630 | +18.5 % |
| 3 days | **0.0720** | 0.0958 | 0.1630 | +24.9 % |
| 5 days | **0.0938** | 0.1204 | 0.1637 | +22.1 % |
| 7 days | **0.0968** | 0.1395 | 0.1637 | +30.6 % |

The advantage grows with lead time. Model error rises 2.1× from day 1 to day 7, and persistence rises 2.5×.

**Why the headline is an upper bound, stated plainly.** Channel 0 is a *reanalysis* valid at the target date, and a reanalysis has assimilated observations near that date. The flat raw-GLORYS12 error across leads (0.1630 → 0.1637) is the fingerprint of a field that has already seen the target. The leak inflates the 7-day figure most, so **+30.6 % is the most contaminated number.**

The settling experiment has a pre-committed decision rule:

- **Arm A:** background zeroed.
- **Arm B:** background = the analysis at initialisation, i.e. what production would actually have. Three seeds per arm.
- **Rule:** if Arm B's gain at lead 7 falls inside the seed spread, the +30.6 % figure is retired from every slide.

**OPEN, highest value per hour of any item.**

**Other defects the audit found in the model:**

- It was trained **with** the land-spillover zeros present. The QA fix was applied to the router but not to training (**OPEN**).
- RMSE is pooled over a box dominated by open ocean, so skill has never been measured in the coastal band or the marginal ice zone (MIZ) (**OPEN**).
- It uses a single seed and has no tuning.
- The `unet.py` defaults describe a 3.0 M-parameter model that was never trained (**OPEN**).
- The December 2019 demo window sits inside the training slice. That is harmless while the demo runs no model, and becomes a leak the moment model output is shown on those dates.

### 3.4 Routing

**Real-data path (PolarRoute 1.1.11 + meshiphi 2.3.1, BAS, MIT licence):**

- The pipeline runs mesh → vessel performance model → Dijkstra → smoothing in ~9 s on a CPU. Install takes ~90 s with binary wheels only.
- Result: 41 legs and 8.58 days of ideal steaming, Cape Town → Bharati, on real ice for 1 Dec 2019.
- Alternatives: corridor A is 41 legs / 8.58 d. Corridor B is 51 legs / 8.66 d with worst ice at 91 %. Corridor C has **no route at all** below a 45–55 % assumed ice limit: not slower, unreachable.
- **What this path does not do:**
  - It is a single frozen mesh with no time dimension, so it meets day-0 ice on day 9.
  - It has a single objective (`traveltime`). Fuel and time are **collinear** in this configuration: solving for fuel returns a byte-identical path.
  - `min_depth: 20 m` is **inert** because the mesh has no bathymetry.
  - `max_wave` is inert because PolarRoute's wave-resistance function is defined and never called.
  - The ice force limit is borrowed from another hull.
  - Ice thickness and density come from a literature lookup table (disclosed, ADR-013).
- **Vessel-awareness is proven for cost, not track.** *Golovnin* and *Agulhas II* follow an identical 41-leg track; the ETA differs by 1.28 days and fuel by −8.9 %.

**Synthetic-world path (`dakshin/sim/router.py`):**

- A **time-aware search**: each cell is costed with the conditions valid when the ship would actually arrive there. This is the only way a forecast can influence a route. Runs in ~2 s.
- Fuel is expressed per distance, with independent resistance terms for speed, ice and sea state (v², C^1.5, Hs²). **Measured:** time-optimal route 10.66 d / 195 t, fuel-optimal route 17.06 d / 154 t, on tracks sharing only 9 of ~100 waypoints. In this world, time and fuel genuinely diverge.
- The reachability boolean is replaced by `critical_ice_limit()`, the assumed ice limit at which reachability flips. The system does not pretend 80 % is a certificated number.

**Measured null result, published against the project.** The honest baseline is the same router given older ice. On the one departure date tested, planning on stale data cost **0.03 days**. Daily local re-planning measured *slower* than one global optimisation. A multi-date sweep is queued (**OPEN**).

### 3.5 Iceberg hazard

- **Catalogue (real):**
  - USNIC weekly product, 33 icebergs as of 27 Aug 2026. The largest, D15A, is 3,037 km² at 66.63°S 81.92°E, about 390 km from Bharati.
  - "In corridor" is a longitude-band test (−10° to 100°E). One document counts 15 in-corridor bergs and another 11; the discrepancy is unreconciled (**OPEN**).
- **Physics (built, tested):**
  - Wagner–Dell–Eisenman (2017) closed-form drift. It reproduces the paper's coefficient table and its 765 m critical length (23/23 tests).
  - The Southern Hemisphere deflection is flipped to the left from the Coriolis sign. This is **inferred, not verified**, because the reference work is Arctic.
- **In the synthetic world:**
  - Forward tracks by Heun integration, with uncertainty growing 13 km/day.
  - **Projection stops at 72 h.** Past that, a physics-only error of 127–147 km would turn every buffer into an ocean-wide blockade.
  - CPA is computed against the ship's *future* track, not its current position.
  - Bergs ground on a shared land mask. Wind-sensitive bergs are drawn dashed.
- **Not established:** no trajectory error has ever been measured. The validation archive (BYU consolidated database, 1978–2025) is free and unused. **This is one third of the problem statement title, and it is roadmap, not capability.**

### 3.6 Decision layer — the product's real substance

This layer is where the project is genuinely ahead of existing tools.

| Concept | Implementation |
|---|---|
| Gate states | `PASS / MARGINAL / FAIL / UNKNOWN`. **`UNKNOWN` can never read as a pass**; it caps health at `DEGRADED` |
| Nine gates | Ice, logistics, contingency, capability, chart, weather, traffic, communications, execution |
| Health | `VALID / DEGRADED / CRITICAL / INVALID`, the **worst** gate state. The gate that produced it travels with it. **There is no score** |
| Evidence | Each gate carries source, detail, provenance as a real file path, valid time and age |
| Ice gate band | ±7.4 points around the assumed limit, derived from the CDR's own retrieval σ (the one invented threshold replaced by a measured one) |
| Change detection | `gate_digest()`: identical evidence gives an identical digest, so there is no transition. This separates "an assumption changed" from "new data arrived" |
| Approval | Versioned and attributed. The approver's name is required and never defaulted (**400** if missing). Approvals never overwrite: there is a `supersedes` chain |
| Divergence | After approval, a health change names the gate that flipped |
| Expiry | In the bridge console, a layer older than its skill horizon retires its gates to `UNKNOWN`, with the age stated |

**Measured on real data (December 2019 replay).** Health moves DEGRADED (1 Dec) → **INVALID** (5 Dec) → DEGRADED (9 Dec). Re-evaluating the same day produces an identical digest and no divergence. On the real-data console, six of nine gates are `UNKNOWN`, and each names the dataset that would settle it.

**In the synthetic console.** Gates take live inputs: a synthetic seabed for under-keel clearance, communications by latitude, traffic from the AIS picture. Health reads VALID from departure to D+5.5 and DEGRADED at D+7 as the ship enters ice and leaves geostationary cover.

### 3.7 Bridge console and synthetic world model

- **Console (`/`):**
  - Styled in the ECDIS/OpenCPN idiom: S-52 day/dusk/night palettes, magenta reserved for cautionary, tabular numerics, no explanatory prose.
  - Workflow: sign in → command centre → voyage → mission → route (solve) → waypoints → review (nine gates) → approve → begin navigation, then a time slider.
  - Ten rail panels, ten status fields. **Zero external network requests, test-enforced.**
- **Replay console (`/legacy`):** the only page that renders **real** satellite observations. It is kept deliberately as the project's strongest evidence.
- **World model (`dakshin/sim/`) — "real physics, synthetic initial conditions":**
  - One seeded pressure field drives everything. Wind is its gradient, waves grow from wind and die in the pack, the ice edge moves under wind and relaxes, fog forms where warm air crosses cold water, and bergs are advected by the tested drift model.
  - Every field is a pure function of `(seed, t)`, so any time can be served directly without integrating forward.
  - Randomness comes from `blake2b`, not NumPy's generator. NumPy's generator can change between releases, and the demo machine runs a different Python, so the same seed could otherwise give a different world. Bit-identical results are verified across machines.
  - The ice-edge climatology is fitted from the real NSIDC archive.
  - Climatology check: Roaring Forties mean wind 11.0 m/s, Furious Fifties 14.1 m/s.
  - 26 bergs, of which only 5 exceed USNIC's 18.5 km tracking floor. That is deliberate: the catalogue does not see most icebergs.
- **Labelling:** a `SYNTHETIC ENVIRONMENT` badge is shown globally, plus per-panel provenance dots. A behavioural test fails if either console loses its data-mode label.

### 3.8 Offline and bandwidth

- **Measured:** a full daily pack (ice field, wind, route, bergs, alerts) is **7.8 KB gzip**. That is 0.09 s at 704 kbps and 8.9 s at 7 kbps. A season at this size moves about 1 MB in total.
- **Measured earlier (real data):** a vessel-modelled mesh block of 824 cells is 551 KB raw and 76 KB gzip; a route polyline is 796 B.
- **Estimated, not measured:** the full real-data corridor mesh at 0.5–1 MB gzip, and the real-data daily delta.
- **What "offline" means today:** the page makes no network calls (a property, test-enforced). On-board re-planning of the *real-data* route is **not** possible yet: PolarRoute needs Python 3.11 and is kept out of the 3.12 demo runtime. Pack signing, delta sync and rollback are **DESIGNED** only.

---

## 4. Architecture

### 4.1 The governing rule

> **Ashore: everything that needs bandwidth or a GPU. Aboard: everything that needs to answer a question. Sync: a compressed environmental state, not an answer.**

Three tier boundaries were evaluated:

| Boundary | Sync payload | Verdict |
|---|---|---|
| (a) Vessel receives finished routes only | ~1 KB | **Rejected.** The master cannot re-plan; it is a picture, not a tool |
| **(b) Vessel receives environmental state and runs routing locally** | 7.8 KB daily (measured, synthetic) to ~1 MB refresh (target) | **Chosen.** Justified by measurement: the routing pipeline is ~9 s and inference ~0.3–1 s on CPU |
| (c) Vessel runs ingestion and training | GB-scale | **Rejected.** Impossible over Iridium |

### 4.2 Target architecture (designed; partly built)

```
┌──────────────────────── SHORE TIER ("Ops Core") ─────────────────────────┐
│  workstation / campus box · needs bandwidth + GPU                        │
│                                                                          │
│  [1] Ingest    NSIDC CDR · CMEMS forecast (daily harvest) · GLORYS12 ·   │
│                GFS · ERA5 (forcing at t, never t+lead) · USNIC · GEBCO   │
│                + QC pass → qc_flags · regrid to NSIDC 25 km (EPSG:3412)  │
│  [2] Train     residual U-Net ×5 (bias-corrects CMEMS) · conformal       │
│                calibration tables · GBM iceberg residual (stretch)       │
│  [3] Build     corrected SIC μ, σ, SIC_upper (leads 1..10)               │
│                berg exclusion (≤72 h) · hazard fusion · meshiphi mesh ·  │
│                12-run PolarRoute sweep → dominance-filtered candidates   │
│  [4] VOYAGE PACK  signed · versioned · daily delta ≤50 KB · refresh ≤1 MB │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │  Iridium · port Wi-Fi · USB (first-class)
┌─────────────────────────────────▼──────────── VESSEL TIER ("Bridge") ────┐
│  same codebase, MODE=vessel, no outbound network required                │
│  [5] Pack store: current + N previous (rollback)                         │
│  [6] Local compute: time-aware re-plan (~2–9 s) · U-Net re-correction    │
│      from a fresh observation (~0.3–1 s CPU) · daily self-verification   │
│  [7] Decision layer: nine gates · health · approvals · divergence ·      │
│      alerts                                                              │
│  [8] Bridge console: staleness always visible · leg grade styling ·      │
│      POLARIS band · provenance on every layer                            │
└──────────────────────────────────────────────────────────────────────────┘
      Model weights (~60 MB) and calibration tables: USB at Cape Town only,
      never over Iridium. Mid-voyage response to a bad model = fall back to
      raw CMEMS, not ship new weights.
```

### 4.3 As-built data flow and the two missing boundaries

```
NSIDC CDR ─┐
GLORYS12  ─┼─► features (12 ch) ─► U-Net ─► corrected SIC ──╳── (not consumed)
           │
           ▼
   QA masking (ice_quality) ─► meshiphi mesh (coarse cells) ─► VesselPerformanceModeller
                                                   │
                                           PolarRoute Dijkstra + smoothing
                                                   │
                   routes.json · alternatives.json · vessel_comparison.json
ATS protected areas ───────────────────────────────┤
destination window ────────────────────────────────┤
                                                   ▼
                                    NINE GATES ─► health ─► approval ─► decision log
Wagner drift ──╳── (tested, fed by nothing on real data)
```

**Boundary B7, the model → route link, does not exist on real data.** Neither does the model half of the risk layer. The product's value ultimately rests on both. The synthetic console shows the *mechanism* (a time-aware router consuming time-varying fields); connecting it to the real corrected forecast is the top engineering item.

**The resolution seam.** The router optimises on coarse cellbox means, while the published "heaviest ice on route" figure is sampled from 25 km pixels along the line. They are different quantities. Tightening the limit from 60 % to 55 % raised the pixel figure from 74 % to 91 %.

### 4.4 Forecast horizon policy (designed)

A 7–10 day forecast has to support a 14–17 day voyage. The answer is that a voyage is a sequence of decisions, not one decision.

| Band | Lead | Claim | Output |
|---|---|---|---|
| Committed | 0–2 d | Real skill | A track the bridge can steer |
| Steering | 3–7 d | Declining, real skill | A **corridor** with flagged decision points |
| Strategic | 8 d + | **No forecast skill claimed** | Climatology (last-10-year median plus inter-annual spread), drawn as a dashed band. No waypoints, no fuel/time figures |

**Anti-whipsaw rule.** Switch routes only if the cost difference exceeds the manoeuvre cost, plus the width of the conformal interval on that difference, plus an incumbency margin. On most days the correct output is "hold course", and that output carries its own evidence.

### 4.5 Degradation ladder (designed; health cap built)

| Rung | Product | When |
|---|---|---|
| 1 | Corrected forecast + calibrated interval | Normal |
| 2 | Raw CMEMS forecast, labelled `uncorrected` | Model fails daily verification or the acceptance test |
| 3 | Persistence from the newest observation, with uncertainty growing from the **measured** persistence error curve | Forecast feed lost |
| 4 | Climatology for the date, shown as a planning corridor, not a route | No recent observation |

**Principle:** a stale forecast is never an input to a route; it is an input to a *widening*. Falling a rung widens the corridor and moves decision points earlier. Because the model predicts a *correction* with a zero-initialised head, **the floor on model failure is CMEMS's own skill, not zero.**

### 4.6 Uncertainty (designed; the core technical differentiator)

- **Method:** stratified split-conformal prediction, `SIC_upper = clip(μ + q̂(lead, regime)·σ, 0, 1)`, with 30 strata (10 leads × open water/MIZ/pack). It is distribution-free, one-sided (matching how ice-edge error fails), and needs no Gaussian assumption on a bounded variable.
- **Router hook:** the vessel subclass overrides `extreme_ice()` to threshold on `SIC_upper`. This matters because BAS's own `IceNetDataLoader` **drops** the uncertainty columns (verified in source), so the incumbent tool routes on the mean.
- **Pre-committed gate, written before the numbers exist:** MIZ coverage at lead 5 must be in [85 %, 96 %], mean bound width < 25 SIC points, and the result must beat inter-source disagreement as an uncertainty proxy. **Failing any criterion removes the risk-tolerance slider and publicly demotes the claim.**

---

## 5. Technology stack

### 5.1 As built

| Layer | Technology | Why |
|---|---|---|
| Backend | Python 3.12, FastAPI 0.141, Uvicorn, Pydantic 2 | One process, typed refusals (409 / 400 / 503), OpenAPI for free |
| Scientific | NumPy 2.5, xarray, h5netcdf/h5py, pyproj, pyshp (build only) | NetCDF-native; the runtime has no heavy geospatial dependency that can fail live |
| Routing (real data) | PolarRoute 1.1.11 + meshiphi 2.3.1 (BAS, MIT) in a **separate Python 3.11 env** | The field's state-of-the-art open tool; native dataloaders match our sources |
| Routing (synthetic) | Own time-aware search, `dakshin/sim/router.py` | PolarRoute has no time dimension |
| ML | PyTorch U-Net, trained on Kaggle T4 (free); MLflow for tracking | A ~2 M-parameter CNN fits the data size; zero compute cost |
| Iceberg | Wagner–Dell–Eisenman (2017) closed form, NumPy only | Needs no training data; no numerical-integration failure mode |
| Frontend | **Vanilla JS + HTML5 Canvas + SVG**, no build step, no CDN | Nothing to break on a ship; the page is airtight (zero external requests) |
| Ops | GitHub Actions (daily CMEMS cron), git, pytest (156) + Playwright (7) | Free; runs regardless of whether any laptop is on |
| Randomness | `hashlib.blake2b` hashed draws | Bit-identical worlds across Python/NumPy versions |

**A planned-vs-built note.** The team guide planned React + MapLibre + PMTiles. The build uses vanilla JS + Canvas, and the audit endorses that for a bridge laptop: there are no tiles to serve, and a build toolchain on a ship is a liability. The audit's corrections are to vendor a projection library locally (a hand-rolled projection already shipped one 2.92× geometry error at Bharati) and to add a polar-stereographic chart mode for the southern leg.

### 5.2 Planned additions

| Addition | Purpose |
|---|---|
| SQLite (WAL) | Durable plan of record. Today a restart loses the approved plan |
| `zstandard` + `cryptography` | Pack compression and signing, which needs a key-management design first |
| Single pinned runtime (Python 3.11, vendored PolarRoute, one executable) | Removes the 3.11/3.12 split that blocks on-board real-data re-planning |
| `proj4js` or `d3-geo`, vendored locally | Correct projections; EPSG:3031 chart mode |
| BAS Antarctic Digital Database coastline | Separates ice coastline, rock coastline, grounding line and ice-shelf front: operationally real distinctions at Bharati |
| IEC 61162 / NMEA 0183 listener | Real ship sensors, in standards order: GNSS/gyro → AIS → echo sounder → radar |
| `copernicusmarine`, `cdsapi` | Full CMEMS and ERA5 ingestion |

### 5.3 Deliberately excluded

| Excluded | Reason |
|---|---|
| LLM / RAG / agent framework (ADR-015) | The problem has no natural-language task. Every component is numerical prediction or graph search, which must be verifiable and must run offline |
| Foundation models (9 adjudicated, 7 rejected, 2 benchmark-only) | The argument is information-theoretic, not budgetary. The whole daily SIC record is ~17,000 frames of ~10⁵ pixels, which a ~2 M-parameter CNN saturates. None of the nine forecasts SIC or was trained on passive microwave |
| `icenet` library | Pins `netcdf4<1.6.1` and `python<3.12`, irreconcilable with meshiphi; Arctic weights only |
| From-scratch A* router | Would forfeit non-uniform meshing, physics-informed smoothing and vessel models, and invite "why ignore BAS's own tool?" |
| Docker, message queue or tile server on the bridge | Nothing on the bridge should be able to fail for a reason unrelated to ice |
| Bhuvan | Its terms of use prohibit use "in connection with real time navigation or route guidance" |

---

## 6. Data sources

| Source | Variable | Resolution | Status | Notes |
|---|---|---|---|---|
| NOAA/NSIDC CDR G02202 v6 | SIC, QA flag, stdev | 25 km, daily | **Used** | 1979–present with a near-real-time stream, so there is no train/serve mismatch. Weakest exactly at the coast and ice edge |
| CMEMS GLO12 `001_024` | siconc, sithick, ice drift, currents | 1/12°, D+0…D+9 | **Harvested daily; not yet used by the model** | The only Antarctic ice-ocean forecast. Documented to **underestimate** summer Antarctic SIC, which is the unsafe direction |
| CMEMS GLORYS12 | siconc (reanalysis) | 1/12°, 1993– | **Used** (training background) | Source of the disclosed leak |
| USNIC | Iceberg positions ≥ 10 nmi | point, weekly | **Archived once** | No history endpoint; weekly cron needed |
| BYU consolidated iceberg DB | Iceberg tracks 1978–2025 | point | Not used | The trajectory validation set |
| ATS protected areas | 148 polygons | vector | **Used** | 0 of 33 corridor polygons are marine, so none restricts transit; Bharati lies inside ASMA 6 |
| Natural Earth | Coastline | vector | **Used** | To be replaced by the BAS ADD for the southern leg |
| GEBCO 2025 / IBCSO v2 + TID grid | Depth, survey provenance | ~450 m | **Not downloaded** | Only 23.79 % direct measurement south of 50°S; East Antarctica is singlebeam-dominant |
| GFS / GFS-Wave | Wind, pressure, Hs | 0.25° | Verified live, not ingested | Polar wave skill uncharacterised |
| ERA5 | Wind, 2T, waves | 0.25° hourly | Planned | **Leak rule:** forcing at *t*, never *t+lead* (sea ice is a prescribed boundary in ERA5) |
| OSI SAF 401/405/408 | SIC, edge, type, drift | 10 km / 62.5 km | Verified, unused | Drift is produced 1 Apr–31 Oct only, so the resupply season has no observational drift |
| **ISRO EOS-06 SCAT L3** | Ice/water flag | 12.5 / 25 km, daily | **Not used; high-priority** | Indian, Ku-band (independent physics), finer than the CDR. Blocked on format and licence behind MOSDAC registration |
| **INCOIS WAVEWATCH III** | Waves | 1°, 9.75 d | Not used | The only Indian forecast covering the whole route; skill check against ERA5 needed |
| **IMD Polar-WRF** | NWP, 3 km, 72 h | Maitri / Bharati | Not used | Finest Antarctic NWP available; charts only. Gridded access is a relationship question |
| **NCPOR station records** | Maitri 1984–2021, Bharati 2012–2024 | point | Not used | The only multi-decade observations at both corridor endpoints |
| CMEMS 1 km Antarctic L3 (S1 + AMSR2) | SIC | 1 km, daily | Not used | 25× finer than the routing field. An observation, not a forecast |
| S-411 Sea Ice (JCOMM ILP) | S-100 ice charts, Antarctica | chart | Not explored | A live standards-based Antarctic ice source, to be reviewed before building more ice layers |
| Sentinel-1 EW SAR | Backscatter | 20–40 m | Not ingested | The only source that sees leads and small bergs. 1–4 GB/scene, so shore-side only |

---

## 7. Key architecture decisions

The full log is in `docs/DECISIONS.md` (ADR-001 to ADR-027).

| ADR | Decision | Main alternative rejected |
|---|---|---|
| 001 | Scope to one corridor, one vessel, one season (models still train circumpolar) | Circumpolar generality, which is unverifiable and dilutes accuracy |
| 002 / 003 | Two tiers; the boundary sits at "sync state, not answers"; one codebase with `MODE=shore\|vessel` | Thin client (cannot re-plan); full stack aboard (impossible over Iridium) |
| 009 / 010 | Wrap PolarRoute; inject bergs through its native `excluded_zones` hook; no fork | Reimplementing A* |
| 012 / 013 | Fuel reported relatively only; ice thickness from a disclosed literature lookup table | Absolute fuel figures from another hull's polynomial |
| 014 | Source disagreement as its own layer that widens caution | Picking a single "best" source |
| 015 | No LLM anywhere | NL query layer |
| 016 | Demo runs from committed scenario packs, never a live fetch | Live-API demo |
| 017 | Bandwidth budget enforced in CI (≤ 50 KB delta, ≤ 1 MB refresh). The budget is never moved; the product changes instead | Bandwidth as an aspiration |
| 018 | The ML model bias-corrects the CMEMS forecast instead of forecasting from scratch | From-scratch forecaster that concedes a comparison against CMEMS |
| 020 | Stratified split-conformal with a pre-committed pass/fail gate | Gaussian `μ + 1.28σ`; scalar variance inflation |
| 021 | 12-run sweep + dominance filter, named a "candidate set", not a Pareto frontier | Three presets called a Pareto set |
| 022 | Always plan the whole voyage; degrade each leg's *grade* | "Refuse to route" past the horizon, which fails exactly when needed |
| 023 | GPU ashore, CPU aboard, weights by USB only | CPU-only training (~85 h, no iteration) |
| 024 | QC before fusion; one target grid; per-channel imputation; obs-only pack type | Implicit QC |
| 025 | Iceberg projection capped at 72 h; auto-downgrade if exclusions exceed 5 % of the corridor | 7-day projection, which becomes an ocean-wide blockade |
| 026 | Under-keel margin depends on bathymetry provenance: 20 m surveyed, max(50 m, 3 × draft) predicted | Treating GEBCO as ground truth |
| 027 | Raw CMEMS is a mandatory, build-blocking baseline on IIEE and CRPS per lead | Benchmarking only against persistence |

---

## 8. Pros and cons

### 8.1 Architecture-level

| Choice | Pros | Cons / risks |
|---|---|---|
| **Two-tier, router aboard** | Works with no link; answers the master's *next* question; measured to fit a bridge laptop (4 cores, 8–16 GB, no GPU) | Two deployment surfaces to keep in sync; pack format, signing and delta are unbuilt; on-board real-data re-planning is blocked today by the Python split |
| **Bias-correct CMEMS rather than forecast from scratch** | Starts at the operational forecast's skill and cannot be worse by construction (zero-initialised head); targets a documented CMEMS deficiency (MIZ underestimation); ~4× smaller model | Depends on one third-party forecast feed; the Stage A (reanalysis) → Stage B (real forecast) transfer is unproven; the forecast archive cannot be back-filled, so every missed day is permanent |
| **Derived health with first-class `UNKNOWN`** | A missing-data gate can never masquerade as safe; explanations are structural, not prose; directly supports Polar Code §11.3.2 (limitations of hydrographic information) | Early versions stayed permanently amber and read as broken; the project had to give gates real inputs so the state carries information. Stale or no-data situations still show more grey than an operator may like |
| **Reuse PolarRoute** | State of the art, MIT, fast (~9 s), native mesh and vessel framework; credibility with domain judges | No time dimension; single objective; dead wave-resistance code; fuel polynomial fitted to RRS *Sir David Attenborough*; forces a separate Python 3.11 runtime |
| **Own time-aware router (synthetic world)** | Lets the forecast actually influence the route; fuel and time diverge measurably (14 % fuel saving for 72 % more time) | Proven only on synthetic fields; two routers now exist and must converge before any real deployment |
| **Synthetic world model for the live console** | Moves and reacts without faking a replay; physically coupled fields; bit-reproducible; clearly badged | A moving, realistic synthetic world is exactly what a reviewer can mistake for live data; it needs discipline in every demo. Several physics constants remain UNVERIFIED (front positions, katabatic mean, fog frequency) |
| **Vanilla JS, no build, no CDN** | Nothing to break offline; auditable in an afternoon; zero external requests enforced by test | Hand-rolled projection already produced one geometry bug; no polar-stereographic mode; no JS unit tests beyond Playwright smoke tests |
| **No LLM** | Deterministic, verifiable against held-out data, runs offline, no inference endpoint | Less "visible AI" in a demo; a bounded local assistant is roadmap only |
| **Honesty-first claims discipline** (true-claims ledger, withdrawn figures, hostile self-audit) | Pre-empts the strongest reviewer attacks; builds trust with a scientific-institution customer | Headline numbers look smaller than competitors' marketing; the submitted SIH deck was found to contradict the repo in eight places (now corrected in `docs/audit/SIH_PPT_V2.md`) |

### 8.2 Strengths (as assessed by the project's own audit)

1. `UNKNOWN` as a first-class, test-enforced state. Competitors' visual language assumes green means fine.
2. A defect in the incumbent satellite record, measured across the whole archive and corrected in the safe direction.
3. The destination-window reframing (23/31 against 31/31) moves the problem to where the decision actually lives.
4. A decision record that is versioned and attributed, and names the assumption that changed.
5. Protected areas modelled by legal regime. The naive approach (treat them as no-go areas) would have refused to route to India's own station.
6. A research corpus that argues against the project, including a published null result.

### 8.3 Weaknesses

1. **No proven saved ship-day.** The commercial case rests on N = 3 saved days, and the only measurement is 0.03.
2. **No user.** No navigator has ever used the system in a task setting.
3. The model headline has a leak of unknown magnitude and was trained on artifact-contaminated coastal data.
4. The model does not reach the route on real data.
5. Three of four real-data router constraints are inert or borrowed (depth, waves, force limit).
6. No calibrated uncertainty yet. The core differentiator exists on paper only.
7. Security is demo-grade: sign-in accepts any string, packs are unsigned, there is no key management.
8. **Deployment liability:** two Python runtimes, and the real-data archive is reached through a symlink into a sibling git worktree, so an ordinary tidy-up deletes the demo's data (P0).

---

## 9. What the system is not, and will not claim

| Not | Why |
|---|---|
| A growler or bergy-bit detector | A growler is ~5 m; the smallest tracked Antarctic berg is ~18.5 km, a gap of 3.5 orders of magnitude. Radar and the lookout own this |
| An autopilot, collision-avoidance or COLREGs tool | It works at hours-to-days and tens of km |
| A replacement for the master, ENCs or type-approved ECDIS | Decision support; it evaluates the master's intended route first and offers alternatives as annotated deltas |
| A source of absolute fuel figures | Fuel polynomial from a different hull |
| A POLARIS-compliant limit | POLARIS is indexed by ice *type*; the system has concentration only, and *Golovnin*'s pre-1999 notation has no row in Table 1.3. It shows a **band** across plausible rows and flags where the band crosses a tier: 99 % of legs are stable, and class only matters in the pack |
| A compression / ice-pressure forecast | Genuine white space. No operational Antarctic product exists, and there is no summer observational drift field |
| A tool "tested over Iridium" | The correct statement is "tested under emulated link constraints" |

**Withdrawn claims (on record):** a 17.4-day transit (computed at half the ship's speed; corrected to 8.6 d steaming); "route bends around the thickest ice" (it crosses more average ice); "different ships get different routes"; "we beat CMEMS"; "fuel-optimised routing" on the real-data path; "predicts live iceberg drift"; "re-plans automatically"; "76 KB full pack".

---

## 10. What comes next

### 10.1 Immediate — close the evidence gaps (0–3 months)

These are ordered by value per effort; most are a download, a wire-up or a single experiment.

| # | Item | Effort | Why it matters |
|---|---|---|---|
| 1 | **Leak-free ablation** (Arm B: causal background, 3 seeds) | ~1 day on Kaggle | Either the headline stands without its caveat, or +30.6 % is retired. Decision rule already written |
| 2 | Move the NSIDC archive out of the git worktree | ~0.25 day | Removes a demo-day failure with no obvious cause |
| 3 | **GEBCO + TID into the mesh**; make `min_depth` real; close the chart gate | ~2 days | Smallest gap, largest regulatory payoff (Polar Code §11.3.2) |
| 4 | **Multi-date route-regret sweep** (p50 / p90 saved days) | ~1.5 days | The number the entire business case rests on |
| 5 | Stratified re-scoring: coast < 100 km, MIZ 15–80 %, ice edge | ~0.5 day | Skill has never been measured where the decision lives |
| 6 | Retrain with QA masking | Kaggle run | The model currently learns from fake coastal open water |
| 7 | USNIC weekly cron; fix the CMEMS wall-clock naming and clipped box | ~0.5 day | Stops irreversible data loss |
| 8 | Bharati reachability table at native 25 km | ~1 day | Makes the headline finding survive scrutiny at full resolution |
| 9 | Age, valid, issue and received time plus a tier badge on every field; uncertainty growing with age from the measured persistence curve | Schema + lookup table | Should precede further model work; otherwise stale numbers are displayed with confidence |
| 10 | SQLite plan of record; real identity | ~1–2 days | A reboot currently loses the approved plan (pilot blocker) |
| 11 | **One structured walkthrough with an ice-experienced officer, recorded** | 1 session | The largest evidence gap relative to the claim "decision support" |

**Exit criteria:** the ablation is published either way; the regret sweep has a p50 and p90; the chart gate passes or fails for a reason other than "no data"; zero contradictions between the deck and the repository.

### 10.2 Planned — production model and offline tier (3–6 months)

- Full-archive ingestion (1993–2024); a **5-member ensemble**; stratified conformal calibration; the packed-CMEMS acceptance test on harvested forecast cycles; **publish the demotion if the coverage gate fails**.
- **Connect the corrected forecast to the router**, either as a time-expanded mesh stack (one layer per forecast day) or as a two-phase solve (ocean leg on today's field, approach leg on the field valid at the arrival band, solved backwards to a cost-to-go).
- The 12-run dominance-filtered candidate sweep (ADR-021) on real data.
- Pack build/sign/delta with a manifest, where every field carries init, valid and received time plus tier, source and QC version. N previous packs kept for rollback. The CI bandwidth test (ADR-017) written.
- Single pinned runtime; horizon tiering; climatology mode; **full re-plan with networking disabled on real data**.

### 10.3 Planned — shore desk and shadow season (6–12 months)

- **Ice-type / thickness output channel**, which unlocks POLARIS, ice numerals and WMO egg-code output together.
- Iceberg trajectories validated leave-one-berg-out against the BYU archive.
- Places-of-refuge and search-and-rescue remoteness tables. The responsible MRCC changes near 75°E; the nearest capable asset to Bharati is Russian (Progress station).
- GNSS and AIS over IEC 61162; EOS-06 source-disagreement layer.
- **A shadow season:** produce a daily advisory for the 2027–28 expedition that nobody acts on, then write a post-season verification report.

### 10.4 Future scope (12 months +)

- First advisory season in the loop (2028); scheduling-risk support for **Maitri II** construction (January 2029 target, per secondary sources).
- A compression / ice-pressure risk field (white space; blocked on the drift-data choice: modelled drift or own feature tracking).
- Sentinel-1 ice edge and small-berg catalogues. A 2026 catalogue reaches 0.016 km², about 4,000× finer than USNIC, though still far coarser than a growler.
- A **detection-degradation advisory**: the system cannot see growlers, but it can forecast when the lookout is blind (sea state > 4 ft, visibility ≤ 100 m).
- Ship-sensor feedback: shaft power as measured ice resistance (a published blueprint exists on SA *Agulhas II*); speed-through-ice vs predicted as free daily model validation; the anemometer to bias-correct ERA5's −3.89 m/s high-wind bias. Helicopter reconnaissance observations as first-class evidence.
- Robust routing: evaluating a route across a range of plausible futures, not one field. The world model's `perturbed(k, t_issue)` hook is the cheapest path.
- A bounded local LLM assistant *on top of* the numerical pipeline (never a replacement). The captain-health wearable ("Baymax") is unresearched and stays badged as future.

---

## 11. Risks and open questions

| Risk | Severity | Mitigation / pre-committed response |
|---|---|---|
| Conformal coverage fails under the post-2016 Antarctic regime shift (breaks exchangeability) | **Critical** (the riskiest assumption) | Numeric pass/fail gate written in advance; failure removes the slider and demotes the claim publicly |
| Model skill does not survive the causal-background ablation | High | Retire +30.6 %; lead with the decision architecture. The fallback is to route on raw CMEMS with source disagreement as the uncertainty proxy |
| No measurable saved ship-days | High | If the sweep shows ~0, pricing shifts from "N saved days" to risk avoided and decision quality. Written in advance |
| CMEMS archive gaps (unrecoverable) | High | Daily cron live; naming and box bugs to fix; manifest with explicit `missing` rows |
| Single customer (NCPOR) | High | Unmitigated; stated openly |
| Bathymetry is largely *predicted* in East Antarctica | Medium | Provenance-conditional under-keel margin plus a coastal buffer; "predicted bathymetry" overlay |
| Upstream product retirements (NSIDC-0051 stopped 31 Dec 2025; NSIDC-0081 retired 18 Jun 2026; a CMEMS CLI flag deprecation broke the harvest once) | Medium | G02202 is unaffected; pin dependencies; confirm the NRT path |
| Golovnin ice class and IMO Polar Ship Category unverifiable from open sources | Medium | Labelled SINGLE-SOURCE / UNVERIFIED; needs FESCO/NCPOR documents |

**Questions only the customer can answer:** what ice information the charter's "ice-information receiving equipment" (tender §11) receives today and from whom; the charter day rate; whether IMD Polar-WRF gridded output and NCPOR station data can be shared; whether any Indian vessel incident records exist for this corridor.

---

## 12. Notes for MoES and DRDO reviewers

### 12.1 MoES (NCPOR, INCOIS, IMD)

- **Operational fit.** The corridor and operating box in NCPOR's own charter tender (66–70°S, 80°E–06°E; one vessel for 100 ± 30 days; bid = day rate × 100) are exactly the system's scope. The tender anticipates ice stopping overboard discharge and has no clause for when the barge fallback is also blocked. By the tender's own formula, one lost ship-day is about 1 % of the season's hire (**Derived**).
- **Indian data the system should use and does not yet:** ISRO EOS-06 scatterometer ice extent, INCOIS WAVEWATCH III, IMD Polar-WRF, and NCPOR Maitri/Bharati station records. Each is a named backlog item. Several are blocked on licence or access rather than engineering.
- **Relationship to existing services.** INCOIS has provided free ship-route advisories since 2013. That rules out charging Indian mariners, but it frames an Antarctic ice extension as an *extension of an existing national programme*, not a new product. The nearest Indian precedent is a deterministic optimum-route study for the Bharati–Maitri leg (*Polar Science*, 2021). It is a precedent, not a competitor.
- **The ask:** a research collaboration, not a procurement. One named NCPOR user answering a real question with the system's output; access to station data and ice-information practice; a shadow season in 2027–28.

### 12.2 DRDO — engineering properties that may transfer (not validated for defence use)

These are properties of the design that a defence-research reviewer may find relevant. **None has been evaluated in a defence context, and the system makes no such claim.**

- **Denied / degraded communications.** The design assumes a sub-50 KB link or none at all. The decision engine runs locally, the daily state is measured at 7.8 KB, and model weights never travel over the link. Degradation is explicit and graded rather than silent.
- **Evidence-gated decision support.** Health is derived from named gates; missing evidence caps confidence instead of disappearing; every change names its cause; approvals are attributed and non-destructive. This pattern is independent of the ice domain.
- **Reproducibility.** Hash-based seeding produces bit-identical synthetic scenarios across machines, which is useful for rehearsal and red-teaming.
- **Supply-chain posture.** No LLM, no cloud inference dependency, no CDN, zero external requests from the UI (test-enforced), open-source MIT routing engine, open data. The project already screens third-party model repositories: one was rejected partly for installing over plain HTTP with `--trusted-host`.
- **What is not ready, stated for this audience:** authentication is a placeholder; packs are unsigned and there is no key-management design; USB ingestion is an unassessed attack surface; there is no read-only OS user or hardened deployment; the persistent store is not built. Any sensitive deployment would need a proper security design first. The planned items are signed manifests, a read-only runtime user, pinned dependencies and a USB ingestion policy.

---

## Appendix A — Source documents

| Document | Contents |
|---|---|
| `docs/ARCHITECTURE.md` | Target system architecture (rev. 2), tier boundary, sync budget, horizon policy, failure modes, phased plan |
| `docs/ML_ARCHITECTURE.md` | Model design, training plan, conformal calibration, evaluation protocol |
| `docs/DECISIONS.md` | ADR-001 to ADR-027 |
| `docs/DECISION_ARCHITECTURE.md` | Horizon bands, anti-whipsaw rule, degradation ladder, master-first interaction |
| `docs/ARCHITECTURE_DELTA.md` | The decision-layer change, domain model, API endpoints, test plan |
| `docs/TRUE_CLAIMS.md` | Claims with on-screen evidence; what the system is not; honest roadmap |
| `docs/RELEASE_AUDIT.md` | The twelve behavioural tests; verified / partial / failed / unknown claims ledger |
| `docs/audit/MASTER_AUDIT.md` | Hostile full audit (sections A–AT), 70/100 score, final verdict |
| `docs/audit/CORRECTIONS.md` | 39 findings → checkable corrections, with status |
| `docs/audit/WORLD_MODEL_DESIGN.md` | Synthetic world model specification |
| `docs/audit/QUICKSTART.md` | How to run the console and tests |
| `docs/PROTOTYPE_RESULTS.md` | Model results and caveats; routing results |
| `docs/DATASET.md`, `docs/research/DATA_SOURCE_STRATEGY.md` | Data sources, access, licences |
| `docs/research/POLARIS_APPLICABILITY.md` | Why no single RIO is published for this hull |
| `docs/research/VESSEL_SPECIFICATIONS.md` | *Golovnin* and *Agulhas II* particulars with source grading |
| `docs/research/STANDARDS_ALIGNMENT.md` | IHO S-100/S-101, IMO, SOLAS, MARPOL alignment and corrections |
| `docs/research/MODEL_REUSE_MATRIX.md` | Foundation-model adjudication; forcing leak rule |
| `docs/COMPETITIVE_ANALYSIS.md`, `docs/DIFFERENTIATION.md` | Incumbents (IcySea, PolarView, ice services, ECDIS, StormGeo, PolarRoute) and the gap occupied |
| `docs/WEAKNESS_ANALYSIS.md` | The adversarial review that drove architecture revision 2 |
| `docs/backlog.md` | Every open item, with severity and pointer to evidence |
