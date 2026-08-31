# System Architecture — SIH26059 Antarctic Navigation Decision Support

Status: **revision 2, 2026-08-31** — revised in response to `WEAKNESS_ANALYSIS.md`. Four
alternatives were genuinely developed; one is chosen. Rejected alternatives and their reasons are
retained below because the reasoning is the deliverable, not just the conclusion.

**What revision 2 changed here:** the bandwidth headline now leads with the measured worst case
rather than the 796 B polyline (§1.2); §2.4a defines an explicit routing-horizon policy for
voyage days 8–14; §2.4b states that model weights ship by USB at port and never over Iridium;
§2.5 gains a defined climatology-mode floor, a per-channel imputation policy and an obs-only pack
type; §2.5a discloses that Antarctic GEBCO bathymetry is largely predicted, with a provenance-
conditional depth margin; §4's timeline absorbs the data-gate and compute realities.

Reads with: `ML_ARCHITECTURE.md` (models), `DECISIONS.md` (ADR log), `DIFFERENTIATION.md`,
`WEAKNESS_ANALYSIS.md` (the review this revision answers).

---

## 1. The constraint that actually shapes this system

The deliverable is a **web app with a local backend**. That constraint is not a packaging
preference — it follows from the operational reality established in `COMPETITIVE_ANALYSIS.md`:

- India's Antarctic resupply runs on the chartered **MV Vasiliy Golovnin**, Cape Town →
  Bharati/Maitri, austral summer, roughly one voyage per expedition.
- Geostationary VSAT does not reliably cover south of ~70°S. Polar maritime comms are
  **Iridium-class**: Certus peaks around 704 kbps and is often far less; legacy service is
  provisioned for **sub-50 KB** critical messages.

**A decision-support platform that calls a live CMEMS or USNIC API from the bridge is assuming
infrastructure the vessel does not have.** Everything below follows from taking that seriously.

### 1.1 Where exactly should the tier boundary sit?

The brief proposed a shore tier plus "a lightweight local serving layer that serves cached
forecast tiles and route recommendations." That is close, but the measurements in
`ML_ARCHITECTURE.md` §0 argue for pushing the boundary **further toward the vessel** than
"cached recommendations." Three candidate boundaries:

| Boundary | Sync payload | Verdict |
|---|---|---|
| **(a) Vessel receives finished routes only** (thin client, cached recommendations) | ~1 KB | **Rejected.** The master cannot re-plan. If the ice looks wrong out the window, or a waypoint changes, or they want a more cautious route, the system has nothing to say. Decision support that cannot answer the operator's actual next question is a picture, not a tool. |
| **(b) Vessel receives the environmental mesh + forecast tensors, and runs routing locally** (model weights are **not** synced — they arrive on USB at port, §2.4b) | **76 KB gzip** per 10°×20° vessel-modelled box (measured); est. **0.5–1 MB gzip** for the full corridor (**not measured** — §1.2) | **Chosen.** |
| **(c) Vessel runs ingestion and training too** | GB-scale | **Rejected.** Impossible over Iridium; ERA5/CMEMS/Sentinel-1 volumes are orders of magnitude beyond the link. |

Boundary (b) is only defensible because it was measured. The full PolarRoute pipeline runs in
**~9 s** on modest CPU (`ML_ARCHITECTURE.md` §0), and a U-Net forward pass is milliseconds — so
**every decision computation is cheap enough to run on a bridge laptop.** The expensive parts are
data ingestion and model training, which are exactly the parts that stay ashore.

The resulting rule is clean:

> **Ashore: everything that needs bandwidth or a GPU. Aboard: everything that needs to answer a
> question. Sync: a compressed environmental state, not an answer.**

### 1.2 The measured bandwidth budget

Stated worst case first, because that is the number the design has to survive.
`WEAKNESS_ANALYSIS.md` §5 is right that leading with the 796 B route polyline is a rhetorical
switch: the polyline is the *smallest* payload in the system and not the thing that has to move
daily. The thing that has to move daily is the **vessel-modelled mesh plus the forecast delta**.

| Payload | Raw | Gzip | Status |
|---|---|---|---|
| **Vessel-modelled mesh, 10°×20° box, 824 cells** (adds speed/fuel/accessibility) | 551 KB | **76 KB** | **measured — this is the representative unit** |
| Full corridor mesh refresh | — | **est. 0.5–1 MB** | **extrapolated, NOT measured** — the adaptive mesh splits hardest in the MIZ, which is exactly where the corridor crosses; the real number could exceed 1 MB |
| Daily incremental delta (changed cells + new leads) | — | **unmeasured** | the load-bearing daily number; measured in Phase 1, not Phase 4 |
| Environmental mesh, same box, pre-vessel-model | 336 KB | 72 KB | measured |
| Route polyline + fuel/time summary | 1.6 KB | **796 B** | measured — the smallest payload, quoted last on purpose |
| Model weights, 5 × ~3 M params fp32 | — | **~60 MB** | **never over Iridium** — see §2.4b |

**The honest headline: a full corridor refresh is a minutes-to-tens-of-minutes Iridium transfer,
and the daily delta is the number the design depends on and has not yet been measured.** What is
measured is that a representative vessel-modelled mesh block compresses to 76 KB, which is what
makes the 50 KB daily-delta target plausible rather than proven.

This produces a concrete, testable engineering target rather than a vague "offline mode":

> **Design target: the daily incremental sync must fit in 50 KB compressed; a full corridor
> refresh in under 1 MB.** Both are enforced by a test in CI that fails the build if a generated
> pack exceeds budget (ADR-017).

**And a pre-committed answer if the corridor mesh misses the target**, since it plausibly will:
coarsen `split_depth` in the open-ocean portion of the corridor (where the mesh gains nothing) and
retain full splitting only within the MIZ band; if that is not enough, drop the full-refresh cadence
from daily to every 2–3 days and ship deltas in between. The budget is not renegotiated; the
product is. That order matters — a bandwidth claim that moves whenever the data moves is not a
constraint.

---

## 2. Chosen architecture — Alternative B: corridor-scoped two-tier, one codebase

### 2.1 Shape

Two deployment *modes of the same application*, not two products. A single FastAPI service with a
`MODE=shore|vessel` switch. This matters for an SIH timeline: it roughly halves the build, and it
is architecturally honest, since the routing and inference code genuinely is identical on both
sides.

```
┌─────────────────────── SHORE TIER ("Ops Core") ────────────────────────┐
│  needs bandwidth + compute; runs on a workstation/campus box           │
│                                                                        │
│  [1] Ingestion      NSIDC CDR SIC · AMSR2 · OSI SAF · OISST · GFS ·    │
│                     ERA5 · CMEMS forecast+GLORYS12 · GEBCO (once) ·    │
│                     USNIC + BYU icebergs                               │
│         ↓ QC pass (artifacts, ranges, swath gaps) → qc_flags layer     │
│         ↓ regrid to NSIDC 25 km polar stereographic, cache raw         │
│  [2] Training       residual U-Net ×5 (bias-corrects CMEMS)  ·         │
│                     GBM drift residual (stretch)                       │
│         ↓ checkpoints (GPU ashore; never retrained aboard)             │
│  [3] Nightly pack build                                                │
│         CMEMS forecast (base) + residual U-Net → SIC μ, σ, leads +1..+10│
│         conformal q̂(lead, regime) → SIC_upper                          │
│         Wagner (+GBM) → berg positions + radii, projection capped 72 h │
│         multi-source fusion → disagreement layer                       │
│         hazard fusion → SIC_upper, berg exclusion, waves, bathymetry   │
│         meshiphi → non-uniform corridor mesh                           │
│         PolarRoute ×12 sweep → dominance-filtered candidate set        │
│         ↓                                                              │
│  [4] VOYAGE PACK  (signed, versioned, <1 MB gzip)                      │
└────────────────────────────────┬───────────────────────────────────────┘
                                 │  Iridium / port wifi / sneakernet USB
                                 │  delta sync, resumable, integrity-checked
┌────────────────────────────────▼─────────── VESSEL TIER ("Bridge") ────┐
│  same codebase, MODE=vessel, no outbound network required              │
│                                                                        │
│  [5] Local store: latest pack + N previous (rollback)                  │
│  [6] Local compute: PolarRoute re-plan on demand (~9 s)                │
│                     residual U-Net re-correction of the packed CMEMS   │
│                     base field when fresh obs arrive (~0.3–1 s, CPU)   │
│  [7] REST API  →  [8] React + Leaflet UI                               │
│         staleness banner · confidence decay · candidate-route selector │
│         risk-tolerance slider (labelled by MEASURED coverage) ·        │
│         source-disagreement overlay · forecast-grade / climatology-    │
│         grade leg styling (§2.4a)                                      │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Component boundaries and interfaces

| # | Component | Responsibility | Interface out |
|---|---|---|---|
| 1 | `ingest/` | One adapter per source in `DATASET.md`. Retries, caches raw, records fetch timestamp + source version. **Plus a mandatory QC pass** — artifact masking, range checks, missing-swath flags, preliminary-data tagging (`ML_ARCHITECTURE.md` §4.1) — and regridding to the single target grid (§4.2). Also runs the **daily CMEMS forecast harvest** (§4, Phase 0). | NetCDF/CSV on disk + a provenance row per fetch + a `qc_flags` layer |
| 2 | `models/` | Residual U-Net ensemble train + inference (bias-corrects the CMEMS base field); conformal calibration tables; Wagner drift; GBM residual | model checkpoints + frozen calibration tables; `forecast(t, lead) → (μ, σ, SIC_upper)` arrays |
| 3 | `fusion/` | Combine sources; compute disagreement on QC-clean cells only; assemble hazard layers incl. `SIC_upper` | mesh-ready DataFrames (`lat`, `long`, `time`, value) |
| 4 | `routing/` | meshiphi mesh build; Golovnin vessel subclass; PolarRoute 12-run sweep + dominance filter | GeoJSON routes + per-route metrics |
| 5 | `pack/` | Serialise, compress, sign, version; delta computation | voyage pack `.tar.zst` |
| 6 | `api/` | FastAPI; identical routes both modes; mode-aware freshness metadata | REST + OpenAPI |
| 7 | `web/` | React + Leaflet; every response annotated with age and confidence | browser |

**The interface between fusion and routing is deliberately just "a DataFrame with lat/long/time
and a named column"** — because that is exactly `meshiphi`'s `ScalarCSVDataLoader` contract
(verified, ~15 lines of source). Our ML plugs into BAS's router with essentially no adapter code.

**Requirement, not an aspiration: the AOI, vessel and season are configuration.** The corridor
bounding box, the vessel parameter block, and the seasonal window live in one config file that
every component reads; no corridor constant is compiled into code. This is what makes ADR-001's
scoping a scoping decision rather than a hard-coded demo, and it must be answerable in a 30-second
re-run when a judge asks "and for the Ross Sea, or a different ship?".

### 2.3 Where each ML decision plugs in

- **Residual SIC U-Net ensemble** → component 2, applied to the CMEMS base forecast, consumed by 3
  as corrected `SIC_mean`/`SIC_std` and the conformal `SIC_upper` mesh layer read by our vessel
  subclass's overridden `extreme_ice()`. Runs ashore at pack build **and** aboard when fresh
  observations arrive (§2.4b).
- **Wagner (+GBM) drift** → component 2, consumed by 3 as buffered exclusion polygons capped at a
  72 h projection horizon (`ML_ARCHITECTURE.md` §2.5), injected via PolarRoute's native
  `excluded_zones` vessel-config hook (verified extension point — no fork). If the polygons cover
  >5 % of navigable corridor area, 3 downgrades them to a weighted cost term for that pack.
- **PolarRoute** → component 4, a 12-run sweep followed by dominance filtering.

### 2.4 Sync and offline strategy

- **Pack is versioned and signed.** The bridge keeps the current pack plus N previous and can
  roll back if a pack is corrupt or looks wrong.
- **Delta sync.** Only changed mesh cells and new forecast leads transfer. Resumable, because
  Iridium links drop.
- **Staleness is a first-class field, never inferred.** Every API response carries
  `pack_built_at`, `age_hours`, and a per-layer `valid_until`. The UI shows it permanently, not
  in a tooltip.
- **Confidence decays with age**, and past the validated skill horizon the product changes rather
  than disappearing — see §2.4a, which replaces revision 1's bare "refuses to route."
- **Sneakernet is a supported path.** A pack can arrive on USB at Cape Town. This is not a
  degraded mode; for a once-per-season voyage it is a legitimate one.

### 2.4a Routing horizon policy — what happens on days 8 to 14

The Cape Town → Bharati/Maitri passage is roughly **10–14 days**. The corrected forecast reaches at
most **10** and the *validated* horizon may be shorter (it is an output of the acceptance rule in
`ML_ARCHITECTURE.md` §1.5, not an assumption). `WEAKNESS_ANALYSIS.md` §7.4 is right that revision 1
said nothing about the remaining days while simultaneously saying the router *refuses* to route
past the horizon — which would have left the departure plan undefined for a third of the voyage.

**The router always produces a plan for the whole voyage. What changes is the grade of each leg,
and the grade is visible.**

| Leg | Field | Uncertainty | Presentation |
|---|---|---|---|
| **Forecast-grade** — day 1 to the last lead passing §1.5's acceptance rule | Corrected CMEMS + conformal `SIC_upper` | Measured conformal coverage per lead × regime | Full-weight route line, waypoints, relative fuel/time, berg exclusion polygons (≤72 h only) |
| **CMEMS-direct** — remaining leads up to CMEMS's day 10 | **Raw packed CMEMS**, labelled `uncorrected` | Band from measured CMEMS-vs-observation error at that lead, computed from the harvested forecast archive (`ML_ARCHITECTURE.md` §1.3 Stage B) — a real number, not a guess | Lighter line, waypoints shown as indicative, no berg polygons |
| **Climatology-grade** — day 11 to arrival, and any leg beyond the pack's validity | **Trend-adjusted climatology**: median SIC field for that day-of-year over the **last 10 years only** (not the full record — post-2016 Antarctic ice is a documented shift, and a 1979-based climatology would be biased high), plus the empirical inter-annual spread as an explicit wide band | Inter-annual spread, which is honestly wide | Dashed corridor band, **not a route line**; no waypoint list, no fuel/time figures, banner: *"planning-grade: which way to go, not where to steer"* |

Two rules bind this together:

- **Uncertainty widens monotonically across the tiers, and the router sees it.** `SIC_upper` in the
  climatology tier uses the inter-annual spread directly, so the optimiser is automatically more
  conservative on the tail without any special-case code — it is the same mesh layer, wider.
- **Daily re-optimisation is the mechanism that makes the tail acceptable.** Every new pack
  re-plans the whole remaining voyage, so the tail is always ~4 days further away than the leg
  being steered, and **the vessel is never executing a climatology-grade leg** — it is only ever
  *committing* to one (which side of a gyre, which longitude to cross the MIZ). That commitment is
  the real decision the tail exists to inform, and it is stated as such in the UI.

### 2.4b Model weights ship by USB at port, never over Iridium

Boundary (b) in §1.1 lists "model weights" in the sync payload. That needs saying plainly, because
the arithmetic is not close: **5 members × ~3 M parameters at fp32 ≈ 60 MB** (revision 1's 8–15 M
design would have been 160–300 MB) — three orders of magnitude past the sub-50 KB Iridium message
budget and hours of transfer even on Certus.

**Weights and the frozen conformal calibration tables are loaded onto the bridge machine once, from
USB, before departure at Cape Town, and are versioned with the same signature scheme as the packs.**
They are never part of a delta sync. A weights update mid-voyage is not a supported operation; if a
model is found to be wrong at sea, the response is to fall back to the raw packed CMEMS field
(`ML_ARCHITECTURE.md` §1.5), which requires no new weights, not to ship new ones.

**What *does* move over the link is small and this is the point of the observation-conditioned
design:** the packed base forecast is re-corrected aboard from a fresh corridor SIC observation —
~20 k cells as scaled uint8, **estimated 5–15 KB gzipped**, inside even the legacy budget. *This
estimate is unmeasured and is logged as such;* if Phase 1 measurement shows it does not fit, the
honest position is that the pack refreshes at whatever cadence the link allows and on-vessel
re-correction is dropped — pack-only forecasts remain a perfectly good design.

### 2.5 Failure modes and fallbacks

| Failure | Behaviour |
|---|---|
| No connectivity for days | Normal operation on cached pack; staleness escalates green → amber → red; when the pack outruns its validity, **climatology mode** (below), never silence |
| Path smoothing fails/hangs | Serve the unsmoothed Dijkstra path (0.7 s, verified) flagged `unsmoothed` — fallback is inherent, no extra code |
| Forecast lead exceeds validated skill | **Tier down, do not refuse** — CMEMS-direct, then climatology-grade, per §2.4a. The plan always covers the whole voyage; the grade of each leg is visible |
| A lead fails the acceptance rule at build time | That lead ships **raw packed CMEMS**, labelled `uncorrected`; the declared skill horizon shortens (`ML_ARCHITECTURE.md` §1.5) |
| Conformal coverage gate fails on held-out data | `SIC_upper` is withdrawn as the routed field; router uses corrected mean + a fixed margin; the slider is **removed** rather than left as theatre; D1 is publicly demoted (`ML_ARCHITECTURE.md` §1.6.5) |
| Ensemble members disagree strongly | Widened `SIC_upper` → automatically more cautious route + explicit low-confidence banner |
| Sources disagree (CMEMS vs NSIDC CDR vs AMSR2) | Disagreement layer widens uncertainty and renders as an overlay — **on QC-clean cells only**, so an artifact cannot masquerade as disagreement (`ML_ARCHITECTURE.md` §4.1) |
| Sensor artifact / bad swath / preliminary data | Caught by the ingest QC pass, flagged in `qc_flags`, excluded from the disagreement statistic, rendered distinctly from genuine disagreement |
| Berg exclusion polygons cover >5 % of navigable corridor | Berg layer auto-downgrades from hard exclusion to weighted cost for that pack, and says so (`ML_ARCHITECTURE.md` §2.5) |
| GBM drift model out of distribution | Falls back to pure Wagner physics, flagged — trigger is a frozen per-feature range check plus a p99 correction cap, unit-tested to fire (`ML_ARCHITECTURE.md` §2.3) |
| **A data source is down at pack-build time** | Per-channel imputation policy below; if the base field or SIC observations are missing, an **obs-only pack** ships instead of a forecast pack |

**Climatology mode — the graceful floor, defined rather than promised.**
`WEAKNESS_ANALYSIS.md` §3 is right that "refuse to route + last-known-good edge + red banner" is an
availability failure dressed as a safety feature: the Antarctic MIZ edge can move tens of km/day in
a storm, so after N days dark the master gets a stale line and a warning at exactly the moment the
tool is most needed. Climatology mode is the floor beneath the refusal, and it is **the same
machinery as §2.4a's climatology-grade tier** applied to every lead rather than only the tail:

- The routed field becomes the **trend-adjusted climatological SIC** for the date (last-10-year
  day-of-year median), with `SIC_upper` set from the **empirical inter-annual spread** — which is
  wide, and is meant to be.
- The router still runs, and still produces a dominance-filtered candidate set, because a heavily
  inflated `SIC_upper` is just another mesh layer.
- The output is presented as a **planning corridor, not a route**: dashed band, no waypoint list,
  no fuel/time numbers, permanent banner *"climatology mode — no forecast newer than <date>"*.
- Berg polygons are **absent**, not stale: past the 72 h projection cap there is nothing honest to
  draw, so the layer shows last-observed positions with their observation date.
- Everything it needs is already ingested for training, so this costs no new data path.

**Per-channel imputation policy** — because revision 1's "pack builds from remaining sources"
directly contradicted a model with fixed input channels (`WEAKNESS_ANALYSIS.md` §4):

| Missing channel | Policy |
|---|---|
| ERA5/GFS wind, 2 m temperature | Persist the last available field, flag `imputed_persistence`; degrade to day-of-year climatology after 48 h |
| OISST SST | Last available field (SST is slowly varying; 1–2 days of persistence is physically defensible), flagged |
| CMEMS base forecast SIC | **Not imputable — this is the base field.** The pack becomes an **obs-only pack** (below) |
| Observed SIC (NSIDC CDR) | If ≤2 days missing, persist last observation, flagged, and mark the innovation channel invalid; if >2 days, **obs-only pack** |
| Land mask, bathymetry, day-of-year | Static or derived; cannot go missing |

Any imputed channel sets a per-cell `imputation_flag`, which is packed, surfaced in the UI, and
**widens `SIC_upper`** — the same mechanism disagreement uses, so degraded inputs make the router
more cautious automatically rather than silently confident.

**Obs-only pack** is a first-class, declared pack type (`pack_type: obs_only`), not an error state:
it carries the latest observed ice field, bathymetry, bergs, waves and a full mesh, and it routes —
but it carries **no forecast leads at all**, so the whole voyage is planned at climatology grade
beyond the observation date. It is the pack the system ships when the forecast pipeline cannot run,
and its existence is why "a data source is down" is a row in this table rather than an outage.

### 2.5a Bathymetry is a model, not ground truth — disclosed, with a margin

`DATASET.md` §6.2 logs the ENC/charted-hazard gap honestly, but the routing layer never stated its
consequence, and `WEAKNESS_ANALYSIS.md` §10.7 is right to call that out: **much of the Antarctic
corridor's GEBCO bathymetry is *predicted* from satellite altimetry, not surveyed by echo sounder.
The router treats depth as truth; it is a model with metre-to-hundreds-of-metre error in unsurveyed
areas.**

Handled, not just admitted:

- GEBCO ships a **Type Identifier (TID) grid** distinguishing measured soundings from predicted
  bathymetry. We ingest it and carry it as a mesh layer.
- **Depth margin is conditional on provenance:** minimum under-keel clearance of **20 m in
  TID-surveyed cells and max(50 m, 3 × draft) in TID-predicted cells.** A predicted-depth cell is
  therefore held to a materially more conservative standard than a surveyed one.
- The UI shows a **"predicted bathymetry" overlay** so the master can see which parts of a route
  cross unsurveyed seabed, and the disclosure sentence sits next to the depth legend, not only in
  this document.
- **This system is decision support, not a navigation system.** It does not replace ENCs, and it
  says so in the product.

### 2.6 Why this wins on the criteria that matter

- **Correctness** — uncertainty propagates end to end rather than being discarded at the router.
- **Reliability** — the demo runs entirely from a local pack; no live third-party API can break it.
- **Implementation time** — one codebase, two modes; PolarRoute measured as a ~90 s install and a
  ~9 s pipeline rather than weeks of integration.
- **Demo quality** — "cut the network cable mid-demo and keep planning routes" is a genuine,
  unfakeable moment that maps to a real operational requirement.
- **Differentiation** — every claim in `DIFFERENTIATION.md` maps to a named component above.

---

## 3. Rejected alternatives

### 3.1 Alternative A — "Ideal": full-fidelity operational system

Continuous ingestion of all seven data categories including **Sentinel-1 SAR ice-edge
extraction**; nightly retraining; assimilation of Sofar buoy in-situ data; AIS integration; NCPOR
NPDC portal integration; full circumpolar mesh; production delta-sync service.

**Rejected for the baseline.** Sentinel-1 GRD scenes are 1–4 GB each and require calibration,
speckle filtering, terrain correction and geocoding before an ice edge can be extracted — that is
weeks of specialist work on its own, and `DATASET.md` §2.1 notes Antarctic EW revisit is *not
verified* for any specific corridor, so the refresh cadence a router would depend on is unknown.
Sofar buoy access is unconfirmed. NPDC is a Struts form, not a REST API.

**Retained as explicit stretch goals**, in priority order: (1) NCPOR NPDC station data as
validation ground truth near Bharati/Maitri — strong pitch value for an MoES audience, (2) a
single hand-picked Sentinel-1 scene as a qualitative ice-edge validation figure rather than a
pipeline, (3) AIS. None are load-bearing.

### 3.2 Alternative C — "Live-API single-tier web app" (the convergent competitor build)

Everything server-side; the browser calls a live backend which calls CMEMS/USNIC on demand.

**Rejected.** This is precisely the design `COMPETITIVE_ANALYSIS.md` §3 predicts competitors will
converge on, and it fails on the one fact that defines the operational context: **the vessel does
not have the connectivity this assumes.** It is also demo-fragile — a live judged demo would
depend on third-party API uptime and the venue's network — and it has no offline story at all.
Building it would mean building a system that could not be deployed on the ship it is for.

### 3.3 Alternative D — "Precomputed static site"

A nightly job renders routes and hazard tiles to static files; the frontend is pure static
hosting. Maximum demo reliability, near-zero runtime risk.

**Rejected as the baseline** for the same reason as boundary (a) in §1.1: the vessel cannot
re-plan, so it is not decision support. It also makes the AI inert at demo time — nothing is
computed while anyone is watching, which is exactly the "UI wrapped around static logic" failure
mode judges are said to be watching for.

**But its best idea is adopted:** pre-baked **demo scenario packs**, committed to the repo, so a
live demo never depends on a network fetch or a nightly job having succeeded. The demo runs the
real router on a real cached pack — reliability without inertness.

---

## 4. Implementation plan and honest timeline

Ordered as a vertical slice first, then depth. Nothing later is a prerequisite for a working demo.

**Phase 0 — spine (days).** Repo + git init (`INFRASTRUCTURE_AUDIT.md` notes there is no VCS
yet), Python 3.11 environment pinned to the versions verified in `ML_ARCHITECTURE.md` §0, FastAPI
skeleton, React shell.
**Plus two things that must start on day 1 because they cannot be back-filled or deferred:**
1. **The daily CMEMS forecast harvest cron** (~5–15 MB/day, corridor subset). The Stage B archive
   in `ML_ARCHITECTURE.md` §1.3 does not exist retrospectively; every day it does not run is a day
   permanently missing from the acceptance test.
2. **The NCPOR-overlap check** (`backlog.md`) — a ~1-hour manual portal review, now a **hard
   blocker on starting the build**, not a backlog line. If NCPOR's "Research Vessel Movements"
   tooling already does route planning or ice forecasting, D5 flips from strength to embarrassment
   in front of the exact audience that would know, and the scope must change before code is
   written rather than after.

*Exit: a route renders on a map from a committed fixture pack; the harvest cron has run once;
the NCPOR question is answered in writing.*

**Phase 1 — real routing on real data, and the data gate (about a week).** GEBCO (+ TID grid) +
NSIDC CDR SIC + GFS ingestion with the QC pass; meshiphi corridor mesh; Golovnin vessel subclass;
PolarRoute single-objective. **No ML yet** — this deliberately gets a genuinely useful, real-data
product working before any model exists.
**Phase 1 also owns the four measurements and one gate that Phase 2 depends on**, because
`WEAKNESS_ANALYSIS.md` §9 is right that *not one byte of training data has been downloaded*:
- **Round-trip one real file from each of** Earthdata-gated NSIDC gridded SIC (`.netrc` bulk auth),
  CDS/ERA5 (`cdsapi`, and measure the actual queue latency for a multi-decade request — it is
  hours-to-days and appears nowhere in the current plan), and CMEMS (`copernicusmarine.subset()`).
- **The §1.4 CMEMS gate:** a real file containing `siconc` at leads 1–10 over the corridor, plus a
  real GLORYS12 SIC file. If it fails, revision 1's from-scratch U-Net is reinstated *here*, with
  time to absorb it.
- **Measure the real corridor mesh size and the daily delta** (§1.2), not in Phase 4.
*Exit: a real Cape Town → Bharati route over real bathymetry and real observed ice, plus four real
data files on disk and a go/no-go on the base field.*

**Phase 2 — the trained model (1–2 weeks, the long pole, and it is a genuine risk).** ERA5/OISST/
GLORYS12 historical ingestion; residual U-Net training on the named GPU (`ML_ARCHITECTURE.md` §1.3
— 8–12 GPU-hours, inside one week of Kaggle's free quota); 5-member input-perturbed ensemble;
conformal calibration tables; the full evaluation protocol including the packed-CMEMS acceptance
rule and the coverage gate.
*Exit: the evaluation table in `ML_ARCHITECTURE.md` §5, filled with real held-out numbers, and a
recorded pass/fail against §1.5 and §1.6.5.*

> **Stated fallback if Phase 2 slips** (`WEAKNESS_ANALYSIS.md` §9 is right that this was unstated):
> ship Phases 1 + 3 + 4 with **raw packed CMEMS as the routed field** and inter-source disagreement
> as the uncertainty proxy. Under the pivot this is a *much* softer landing than it would have been
> under revision 1: the pack, the mesh, the slider mechanics, the berg layer and the offline demo
> are all unchanged, and the pitch degrades from "our model improves the operational forecast" to
> "our decision architecture makes the operational forecast routable." The one thing that must
> survive for the "Real AI only" bar is a trained model — so if the deep correction slips, the
> **GBM iceberg residual is promoted from stretch to baseline**, because it trains in minutes on
> data already downloaded. This ordering is decided now so it is a plan, not a scramble.

**Phase 3 — uncertainty and hazards (about a week).** `SIC_upper` conformal layer; overridden
`extreme_ice()`; Wagner drift with the 72 h cap and area-fraction downgrade; berg exclusion zones;
the 12-run dominance-filtered sweep; fusion disagreement layer; the §2.4a horizon tiering and
climatology mode.
*Exit: the risk-tolerance slider visibly moves the route, and its label matches measured coverage.*

**Phase 4 — offline tier (days).** Pack build/sign/delta; vessel mode; staleness and confidence
UI; the network-cut demo.
*Exit: full re-plan with networking disabled.*

**Stretch, only if Phases 0–4 are genuinely complete:** GBM drift residual; NCPOR validation
data; a Sentinel-1 validation figure.

**Stated plainly:** the GBM residual drift correction, any seasonal DL retraining, and all of
Alternative A are **stretch goals, not baseline** (with the one promotion rule in the Phase 2
fallback above). If the schedule slips, they are cut, and the system still delivers a trained
sea-ice model with measured, calibrated uncertainty driving an uncertainty-aware polar router —
which is already ahead of the convergent competitor build.

**What is prepared versus what is built in the 36-hour finale.** Decided now, because "re-run
training at the nodal centre" is not a thing:

| Prepared before travel (frozen, on USB) | Built/run at the nodal centre |
|---|---|
| Trained weights + conformal calibration tables (§2.4b) | Live re-planning demos, scenario walkthroughs |
| Evaluation results and all figures | UI polish, presentation assembly |
| Committed demo scenario packs (ADR-016) | Judge-requested re-runs on committed packs (real computation, ~9 s + ~84 s sweep) |
| Environment pinned and pre-installed | Bug fixes, integration of anything left open |

Nothing on the left is regenerated on site. Nothing on the right needs a GPU or a network.

---

## 5. Riskiest assumption in this design

**That the calibrated bound is well enough covered for `SIC_upper` to make routing genuinely safer
rather than merely more conservative-looking.** The entire uncertainty-aware differentiation, and
the safety argument for the routing layer, rest on it. Conformal calibration removes the Gaussian
and scalar-inflation weaknesses of revision 1, but its coverage guarantee assumes exchangeability
between calibration residuals and operations — and the post-2016 Antarctic regime is precisely the
distribution shift that can break exchangeability. Mitigation, the pre-committed numeric pass/fail
rule, and the written demotion branch: `ML_ARCHITECTURE.md` §6 and §1.6.5.

**The second riskiest assumption is now schedule-shaped, not technical:** the Stage B CMEMS
forecast archive cannot be back-filled (`ML_ARCHITECTURE.md` §1.3). If the daily harvest does not
start at Phase 0, the acceptance test has nothing to run on in December, and the strongest claim in
the pitch — that we beat the operational forecast on its own held-out output — becomes unprovable.
