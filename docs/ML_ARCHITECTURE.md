# ML Architecture — SIH26059 Antarctic Navigation Decision Support

Status: **revision 2, 2026-08-31** — revised in response to the adversarial review in
`WEAKNESS_ANALYSIS.md`. Supersedes the "recommended baseline" language in `GAP_ANALYSIS.md`
— that document surveyed options, this one commits. Every claim below either cites
`DATASET.md` for data provenance or a hands-on verification run in this sandbox (marked
**[verified]** with the measured number).

**What revision 2 changed:** the SIC model is re-aimed from a from-scratch direct forecaster to a
**bias-correction / uncertainty-quantification head on the CMEMS operational forecast** (§1.0–§1.1),
with packed CMEMS as a build-blocking evaluation baseline (§1.5); the training product and window
are resolved and a compute plan is named (§1.3); calibration moves from a scalar variance-inflation
factor to **stratified conformal prediction with a pre-committed pass/fail rule** (§1.6); the GBM
fallback trigger (§2.3) and the iceberg exclusion horizon (§2.5) are made concrete; the "Pareto
set" becomes a real dominance-filtered sweep (§3.4c); a QC and regridding pass is added ahead of
fusion (§4.1–§4.2). §7 records where we push back on the review.

Companion documents: `ARCHITECTURE.md` (system), `DECISIONS.md` (ADR log),
`DIFFERENTIATION.md` (what makes this not the obvious build),
`WEAKNESS_ANALYSIS.md` (the review this revision answers).

---

## 0. Verification performed before committing

Rather than reason about PolarRoute's integration cost from its README, it was installed and
run end to end. These measurements drive several decisions below and are reproducible:

| Check | Result |
|---|---|
| `polar-route` 1.1.11 install (Python 3.11, `uv`) | **Clean, ~90 s, all binary wheels, zero compilation** |
| `import polar_route, meshiphi` | 2.6 s |
| Mesh build, 10°×20° Southern Ocean box, split_depth 3 | **2.1 s → 824 adaptive cells** |
| Vessel performance modelling over that mesh | **0.1 s** |
| Dijkstra route computation | **0.7 s** |
| Physics-informed path smoothing | **6.1 s** |
| Environmental mesh serialised | 336 KB raw / **72 KB gzip** |
| Route polyline + fuel/time summary ("voyage pack") | 1.6 KB raw / **796 B gzip** |
| `icenet` 0.2.9 dependency check | **Rejected — see §1.4** |

Package versions pinned as tested: `polar-route==1.1.11`, `meshiphi==2.3.1`, Python 3.11.14.

---

## 1. Sea-ice concentration forecasting

> **Revision 2 (2026-08-31, post-adversarial-review).** Sections 1.1–1.8 below replace
> revision 1's from-scratch direct-forecast U-Net. The reasoning for the change is §1.0.
> Revision 1's design is not deleted — it survives as the named contingency in §1.4.

### 1.0 What changed, and the mistake that produced revision 1

Revision 1 committed to a 5-member U-Net ensemble doing **direct** multi-lead SIC forecasting,
benchmarked against damped anomaly persistence. `WEAKNESS_ANALYSIS.md` §2 attacked this as the
design's central structural flaw, and the attack lands:

1. `COMPETITIVE_ANALYSIS.md` §2 states in our own words that the CMEMS 10-day assimilating
   sea-ice forecast is "the operational baseline any 'novel forecasting' claim has to beat, and
   it's a hard bar." Revision 1 §1.5 then set the bar at damped anomaly persistence and §1.6
   conceded CMEMS probably wins. We ducked our own bar.
2. The "runs offline on the vessel" justification did not survive our own architecture. The
   shore tier has full bandwidth (`ARCHITECTURE.md` §2.1) and can pack CMEMS's 10-day forecast
   into the voyage pack exactly as it packs our own output. *Packed* CMEMS is offline too,
   reaches 10 days, and needs no training.
3. **`GAP_ANALYSIS.md` §1's own table names the strongest 1–10-day approach as "DL
   bias-correction on top of a short-range ice-ocean model."** Revision 1's rejection table
   never argued against it — the one alternative never argued against was the best one.

**Why it was dropped the first time — the honest account.** `GAP_ANALYSIS.md` §1 names the
approach with a specific example system: *"DL bias-correction on top of a short-range ice-ocean
model (e.g. TOPAZ4)."* TOPAZ4 is the Copernicus **Arctic** analysis-forecast system
(`ARCTIC_ANALYSISFORECAST_PHY_002_001`); it has no Antarctic domain. Revision 1 read the row as
naming a *product we cannot use*, filed it as Arctic-only, and followed the two Antarctic
reference models instead — IceNet and ANTSIC-UNet — both of which are from-scratch direct
forecasters, so the architecture inherited their shape. That was an error of reading a **method**
as a **product**. The method transfers to Antarctica even though TOPAZ4 does not: the global
CMEMS analysis-forecast system `GLOBAL_ANALYSISFORECAST_PHY_001_024` is the Antarctic-covering
equivalent, it carries sea-ice concentration alongside the currents we already need, and it was
**already in `DATASET.md` §4.1** — sitting in our own data inventory, being used for one variable
and ignored for the other. Nothing new had to be found; the row simply had to be read properly.

**Adopted: `WEAKNESS_ANALYSIS.md` §2 option 2 (bias-correction pivot), *and* option 1's mandatory
packed-CMEMS baseline on top of it.** Option 1 alone would have left the routed field as a
third-party product with our model demoted to a cross-check; option 2 keeps a real trained model,
reuses the same data plumbing, targets a *documented* deficiency of the base field, and converts
"we probably lose to CMEMS" into "we improve CMEMS and add the σ it does not expose." The
packed-CMEMS baseline is retained regardless, because a bias-correction model that does not beat
its own base field is worthless and must be caught by the evaluation, not by a judge.

### 1.1 Decision

**A 5-member ensemble of small residual U-Nets that bias-corrects the CMEMS operational sea-ice
forecast over the Antarctic grid, conditioned on the most recent real satellite observations,
emitting corrected SIC at leads +1 … +10 days plus a conformally calibrated per-cell upper
bound. Mandatory baseline: the raw packed CMEMS forecast itself.**

Formally, for base forecast `F_k` at lead `k` issued at time `t`, and observations `O_{t-6..t}`:

```
ΔSIC_k  =  g_θ( F_k ,  O_{t-6..t} ,  F_0 − O_t ,  forcing ,  k )
SIC_k   =  clip( F_k + ΔSIC_k , 0 , 1 )
```

The network learns the **residual** `ΔSIC_k`, never the field itself. Three consequences that are
the point of the pivot:

- **The floor is CMEMS's skill, not zero.** `ΔSIC = 0` reproduces the operational forecast
  exactly, so the model cannot be worse than the bar by more than its own noise — and the
  evaluation in §1.5 makes "worse than the bar" a build-blocking failure per lead.
- **`F_0 − O_t`, the innovation, is an explicit input.** The correction is anchored to how wrong
  the base field is *right now*, at the cell in question. This is the mechanism by which the model
  can learn the documented CMEMS MIZ underestimate (`COMPETITIVE_ANALYSIS.md` §2, Alaska ice-chart
  paper) rather than a generic climatological offset.
- **The model is small.** A residual on an already-skilful field needs far less capacity than a
  forecaster: 3-level U-Net, 16 base filters, **~2–4 M parameters**, not 8–15 M. This is what makes
  the compute plan in §1.3 fit free-tier GPU hours (5 members in 4–8 GPU-hours, §1.3).

The per-cell uncertainty is still the load-bearing output — but it is now produced by conformal
calibration (§1.6), not by trusting an ensemble spread.

### 1.2 Model specification

**Inputs** (all real, all traced to `DATASET.md`; all on the single target grid of §1.3):

| Channel group | Source | `DATASET.md` ref |
|---|---|---|
| CMEMS base forecast SIC at lead k (1 ch) | `GLOBAL_ANALYSISFORECAST_PHY_001_024` (serve) / GLORYS12 `GLOBAL_MULTIYEAR_PHY_001_030` (train, §1.3) | §4.1 |
| CMEMS base SIC at lead 0 (analysis) (1 ch) | as above | §4.1 |
| Observed SIC, previous 7 days (7 ch) | NOAA/NSIDC Sea Ice CDR, SSM/I–SSMIS family, 25 km (§1.3) | §1.1 |
| Innovation `F_0 − O_t` (1 ch) | derived | — |
| 2 m temperature, 10 m u/v wind (3 ch) | ERA5 (training) / GFS (operational) | §5.1, §5.2 |
| Sea surface temperature (1 ch) | NOAA OISST v2.1 | §4.2 |
| Day-of-year sin/cos (2 ch) | derived | — |
| Lead time k, normalised (1 ch) | derived | — |
| Land/ocean mask (1 ch) | derived from GEBCO | §6.1 |
| QC-flag fraction (1 ch) | `ingest/` QC pass (§4.1) | — |

**19 input channels → residual U-Net → 1 output channel = `ΔSIC` at lead k.** Lead is an input
channel rather than an output head, so a single network serves all leads 1–10 and the training set
is 10× larger per forecast cycle. This is the opposite of revision 1's direct-multi-lead choice and
the reason is that the argument for multi-lead heads (coherent per-lead variance) is now supplied
by per-lead conformal strata (§1.6) instead of by the architecture.

**Why not autoregressive:** unchanged from revision 1, and now moot — the base field already
carries the temporal evolution; we correct it, we do not roll it forward.

**Ensemble:** 5 members, differing in **both** random seed **and input perturbation** — each member
trains on forcing channels jittered at the analysis-error scale (ERA5 10 m wind ensemble spread,
OISST reported error) and on a resampled observation window. Revision 1's seed-only ensemble is
explicitly abandoned per `WEAKNESS_ANALYSIS.md` §8.2: seed-only ensembles capture parameter
uncertainty alone and systematically under-disperse. The spread is now used as the *shape* of the
uncertainty field, with its *magnitude* set by conformal quantiles (§1.6) — see the rebuttal in §7.1
for why this changes what ensemble size has to buy us.

**Domain:** trained circumpolar; metrics reported **both** circumpolar and restricted to the Cape
Town–Bharati/Maitri corridor sector, as in revision 1.

### 1.3 Training data, window, target grid and compute — resolved

`WEAKNESS_ANALYSIS.md` §9 is correct that revision 1's spec ("NSIDC/AMSR2 SIC … 1979–2018") was
chronologically impossible: AMSR2 flies from mid-2012, AMSR-E covers 2002–2011 with an Oct 2011 –
Jul 2012 gap, and OISST starts Sep 1981. Resolved as follows.

**Observation product (the truth field and the obs input channels): the NOAA/NSIDC Sea Ice
Concentration CDR, SSM/I–SSMIS passive-microwave family, 25 km south polar stereographic
(`G02202` v4 for the 1979–recent record, extended by the `G10016` NRT product, same algorithm
family).** Reasons, in order:

- **It removes the train/serve mismatch entirely rather than documenting it.** The review offered
  (a) accept a CDR-train / AMSR2-serve mismatch or (b) shrink to the AMSR2 era. We take neither:
  the CDR family runs 1979–present *including the operational near-real-time stream*, so the model
  sees one product, one resolution, one error character, in training and at sea. Option (a) would
  have shipped a 25 km-trained model fed 12.5 km inputs; option (b) would have left ~6 years of
  training data before the 2019 validation boundary.
- 25 km is the resolution both Antarctic reference models use (IceNet, ANTSIC-UNet —
  `COMPETITIVE_ANALYSIS.md` §2), and it is finer than the meshiphi cells the router actually
  consumes, so nothing downstream is starved.

**AMSR2 12.5 km (`NSIDC-0803`/`AU_SI12`) is retained — with a better job than it had.** It is *not*
a model input. It becomes an **independent second observation source for the fusion/disagreement
layer (§4) and a high-resolution ice-edge cross-check**. This is strictly more useful than feeding
it to the network: a 12.5 km product that disagrees with the 25 km CDR at the ice edge is exactly
the signal D3 is built to surface, and using it as an input would have destroyed that independence.

**Base-field archive and the honest problem with it.** Bias-correcting a *forecast* requires an
archive of past *forecasts*. CMEMS's `GLOBAL_ANALYSISFORECAST_PHY_001_024` retains only a rolling
window of past cycles — a multi-decade archive of its lead-k fields does not exist to be
downloaded. Swapping revision 1's impossible spec for a second impossible spec would be worthless,
so the training is deliberately split in two:

| Stage | Base field | Period | Purpose |
|---|---|---|---|
| **A — background correction (bulk training)** | GLORYS12 reanalysis SIC (`GLOBAL_MULTIYEAR_PHY_001_030`, 1993–present, daily, ~8 km → regridded to 25 km) used as a *model background*, paired with the CDR observation as truth | 1993–2018 train, 2019–2021 validate, 2022–2024 test (2023 reported separately) | Learn the model-minus-observation error structure of the Mercator/NEMO-LIM ice model that CMEMS's forecast is built on — same model family, same biases, deep archive |
| **B — forecast transfer (fine-tune + acceptance test)** | The **real** CMEMS 10-day forecast, harvested one cycle per day from Phase 0 onward | 2026-09 onward, accumulating | Fine-tune on true forecast-background statistics, and **verify that Stage A's correction transfers** |

Stage A is a documented **background substitution**: a reanalysis at lead 0 is not a forecast at
lead k, and we say so. It is defensible because the error being corrected — the MIZ concentration
bias of the underlying ice model against passive-microwave observation — is a property of the
model, not of the lead time, and lead time enters as its own input channel. It is not *assumed* to
transfer: Stage B is the test, on real forecast cycles, and §1.5's acceptance rule makes failure to
transfer a demotion trigger rather than a footnote.

**Corollary that must be acted on in Phase 0, not later:** the Stage B archive cannot be
back-filled. **Harvesting one CMEMS corridor forecast cycle per day must start the day the repo is
created** (~5–15 MB/day for a corridor subset via `copernicusmarine.subset()`). From 2026-09-01 to a
December finale that is ~100 real forecast cycles × 10 leads — thin for training, ample for
fine-tuning a residual and for the acceptance test. This is logged as a hard blocker in
`backlog.md`.

**Data volume.** 25 km south polar stereographic is ~332×316 ≈ 105 k cells (confirm exact
dimensions at first ingestion — `backlog.md`). At float16, one channel-day ≈ 210 KB; 19 channels ×
9,500 days (1993–2018) ≈ **~38 GB**, or **~19 GB** with SIC stored as scaled uint8. Chunked zarr on
local SSD; a corridor-only crop is ~15× smaller for iteration.

**Compute plan — named, with the arithmetic.**

| | Number |
|---|---|
| Model | ~3 M params, 3-level U-Net, 332×316 input |
| Forward+backward cost | ~8 GFLOP/sample (≈2× the ~4 GFLOP forward pass at this size) |
| Samples/epoch | 9,500 cycles × 10 leads, subsampled to 3 leads/cycle = ~28,500 |
| Cost/epoch | ~230 TFLOP |
| **On one NVIDIA T4** (~4 TFLOP/s achieved fp16, data-loader bound) | **~2–4 min/epoch**; 40 epochs ≈ **1.5–2.5 h/member**; ×5 members ≈ **8–12 GPU-hours total** |
| **On CPU only** (8-core, ~150 GFLOP/s achieved) | ~25 min/epoch → ~17 h/member → **~85 h for the ensemble** |

**Decision: GPU for training, CPU for inference.** Primary: **Kaggle Notebooks** (free, T4×2 or
P100, 30 GPU-h/week — the whole ensemble fits inside one week's free quota with room for two
retrains). Backup: **Google Colab Pro** (~₹1,000/month, T4/L4). Paid fallback if both are
throttled: a single spot **T4/L4 cloud instance at ~$0.35–0.60/h → $5–10 for the entire training
budget.** CPU-only training is explicitly **rejected** — 85 h leaves no room to iterate, and
iteration is where calibration gets fixed — but it is *feasible as a one-shot final re-run*, which
is the honest answer to "what if you have no GPU at the nodal centre": **nothing is trained at the
nodal centre.** Weights are frozen before travel (§`ARCHITECTURE.md` 2.4a).

**Inference is genuinely cheap and this is what makes the two-tier claim hold:** one forward pass
≈ 4 GFLOP; 5 members × 10 leads over the corridor crop ≈ 15 GFLOP → **~0.3–1 s on the 2.6 GHz
bridge laptop**, no GPU. Minimum bridge spec stated: 4-core x86-64, 8 GB RAM, 20 GB free disk.

### 1.4 Rejected alternatives, and the retained contingency

| Rejected | Reason |
|---|---|
| **From-scratch direct-forecast U-Net ensemble** (revision 1's own design) | Superseded, not deleted — see the **contingency** row below. It concedes the CMEMS comparison (§1.0), needs ~4× the parameters and ~4× the compute for a field the base model already gets mostly right, and its "offline" justification is weaker than the corrected version's (§7.2). |
| **Reusing the `icenet` library** | **[verified]** `icenet` 0.2.9 requires `python<3.12`, `tensorflow<2.16`, `netcdf4<1.6.1`, plus `motuclient` (a deprecated CMEMS client) across 51 dependencies. The `netcdf4<1.6.1` pin **directly conflicts** with `meshiphi`/`polar-route`, which resolve to `netcdf4==1.7.4`. The two cannot share a Python environment. Compounding this: IceNet's published validation is Arctic (`COMPETITIVE_ANALYSIS.md` §2), and no pretrained Southern-Hemisphere weights exist — it would need full retraining anyway. |
| **Reimplementing ANTSIC-UNet at 6-month seasonal lead** | Wrong horizon. A resupply voyage is planned over days-to-weeks; a 6-month seasonal outlook cannot inform a route decision. Also requires the CMIP6 pretraining corpus. |
| **CICE / LIM2 dynamical model** | Operational infrastructure run by national centres. Not standable-up by a hackathon team — and the pivot means we now *consume* the output of exactly such a system instead of pretending to rebuild one. |
| **LSTM on the NSIDC extent time series** | Predicts a scalar. The router needs a spatial field. |
| **Naive persistence as the headline baseline** | Too weak a bar; and the headline baseline is now raw CMEMS regardless (§1.5). |

**Retained contingency — the Phase-1 go/no-go.** The pivot depends on one thing that has not yet
been round-tripped: a real authenticated `copernicusmarine.subset()` pull of Antarctic sea-ice
concentration from `GLOBAL_ANALYSISFORECAST_PHY_001_024` (`backlog.md` flags that no CMEMS call has
ever been made from this project). **Gate: by the end of Phase 1 we must have (i) a real forecast
file on disk containing `siconc` over the corridor at leads 1–10, and (ii) a real GLORYS12 SIC
file.** If either fails — variable absent, licence restrictive, latency unusable — **revision 1's
from-scratch direct-forecast U-Net is reinstated verbatim as the primary model** (it is fully
specified above and in ADR-004), with packed CMEMS demoted to whatever we can still obtain. That
contingency is cheap to invoke because the data plumbing, grid, split, calibration machinery and
evaluation harness in §1.3/§1.5/§1.6 are identical either way; only the base-field channels drop
out. No time is lost by trying the stronger design first.

### 1.5 Evaluation protocol — with packed CMEMS as a mandatory baseline

**"What did you train, on what, how do you know it works, and why not just use CMEMS?"**

- **Split: strictly temporal.** Stage A: train ≤2018 (from 1993), validate 2019–2021, test
  2022–2024. Stage B: the harvested forecast archive is split by cycle date, with the most recent
  three weeks held out and never fine-tuned on. A random split on autocorrelated daily geophysical
  fields leaks adjacent days and inflates scores; this is the most common fatal flaw in
  ML-on-climate submissions and is stated explicitly for that reason.
- **Baseline 1 — MANDATORY, and it is the bar: raw packed CMEMS.** The exact field the voyage pack
  would carry with no model at all. Evaluated on the identical grid, corridor mask, dates and
  metrics.
  > **Pre-committed acceptance rule.** For each lead k, the corrected forecast must beat raw packed
  > CMEMS on **both IIEE at the 15 % threshold and CRPS**, in the corridor, on the Stage B held-out
  > real-forecast cycles — not merely on Stage A's reanalysis background. **A lead that fails is
  > not claimed:** the pack ships raw CMEMS for that lead, labelled `uncorrected`, and the declared
  > skill horizon shortens to the last lead that passes. If *no* lead passes, the model is demoted
  > to the §4 cross-check role, packed CMEMS becomes the routed field, and D1 is demoted per its own
  > falsifiability clause (`DIFFERENTIATION.md` D1). This is a build-blocking gate, not a
  > discussion point.
- **Baseline 2 — damped anomaly persistence**, `SIC(t+k) = clim + α^k · (SIC(t) − clim)`, α fitted
  on the training years. Retained as the *floor*, no longer as the headline: it shows the base
  field and the correction are both doing real work, and it is the only baseline that still exists
  if the CMEMS gate in §1.4 fails.
- **Baseline 3 — the trivial uncertainty proxy.** Per `WEAKNESS_ANALYSIS.md` §5: the calibrated
  bound must beat **inter-source disagreement alone** (NSIDC-CDR vs. AMSR2 vs. CMEMS spread, §4)
  as an uncertainty estimator, on interval score and on coverage-at-equal-width. If a free
  three-way difference predicts the error as well as the trained σ does, the trained σ is
  decorative and we say so.
- **Metrics:** RMSE (SIC %) per lead; **IIEE** (km², 15 % threshold) — the navigationally
  meaningful one; binary F1 at the vessel-relevant threshold; CRPS; interval score; skill scores
  against all three baselines, per lead, corridor and circumpolar.
- **Calibration — mandatory, and now the subject of §1.6** rather than a scalar afterthought.
- **Stress test: 2023, the Antarctic extreme-minimum year, evaluated and reported separately.**
  Post-2016 Antarctic sea ice is a documented distribution shift. Reporting degraded skill there
  honestly is worth more than hiding it — and under the pivot the base field has already
  assimilated the anomalous state, which is precisely the regime where correcting an assimilating
  model should beat forecasting from scratch. This is a falsifiable prediction of the pivot and it
  will be reported as one.
- **Declared skill horizon** is an *output* of this protocol (the last lead passing the acceptance
  rule), not an assumption. Beyond it, `ARCHITECTURE.md` §2.4a governs — the router does not go
  silent.

### 1.6 Calibration — conformal, stratified, with a pre-committed pass/fail rule

`WEAKNESS_ANALYSIS.md` §8 dismantles revision 1's single scalar variance-inflation factor on four
counts and is right on all four. Replaced wholesale.

**(1) The bound is conformal, not Gaussian.** `SIC_upper` is no longer `μ + 1.28σ`. We use
**split conformal prediction** with a σ-scaled nonconformity score, fitted on the validation years
and on the Stage B held-out cycles:

```
score s_i   =  ( y_i − μ_i ) / ( σ_i + ε )            # one-sided: we only bound from above
q̂(stratum) =  ⌈(n+1)(1−α)⌉ / n  empirical quantile of { s_i } within the stratum
SIC_upper   =  clip( μ + q̂(lead, regime) · σ , 0 , 1 )
```

This fixes §8.3 directly: it is distribution-free, so it makes no Gaussian assumption on a variable
bounded in [0,1]; it is one-sided and therefore handles the strong asymmetry of ice-edge error;
and the clip is explicit rather than an unnoticed overflow past 1.0.

**(2) Stratified, not global.** Strata are **lead × regime**: leads 1–10, and three regimes defined
on the *observed* field at t0 — **open water** (SIC < 15 %), **MIZ** (15–80 %), **pack** (> 80 %) —
giving 30 strata. Each gets its own `q̂`. This is the minimum the review demands, and it targets the
failure it names: miscalibration is worst in the MIZ at long leads, which is exactly where the
router consumes the bound. Where a stratum has too few validation residuals for a stable quantile
(n < 500), it is merged with its neighbouring lead and the merge is recorded in the pack metadata.

**(3) The slider is now labelled by measured coverage, not by a z-score.** The operator control is
`α` — target coverage 80 % / 90 % / 95 % — and each setting maps to its own set of `q̂`. The demo
line changes from "this is 1.28 sigma" to **"this says 90 % and it measured 90.4 % on held-out
2022–24 data"**, which is a materially stronger claim and the one `WEAKNESS_ANALYSIS.md` §8.3 asks
for.

**(4) The ensemble's job is smaller now.** σ supplies the *spatial shape* of the uncertainty
(where error is likely large); `q̂` supplies the *magnitude*, from measured residuals. A
5-member ensemble is a poor absolute σ estimator (§8.2, conceded) but an adequate relative one, and
input-perturbed members (§1.2) improve it further. See §7.1 for the one place we push back on the
review's framing here.

**(5) Pre-committed pass/fail rule — the branch revision 1 did not have.** Evaluated on the
2022–2024 test years and on the Stage B held-out cycles, at nominal α = 0.10:

| Check | Threshold | Rationale |
|---|---|---|
| Empirical coverage of `SIC_upper`, **MIZ cells, lead 5** | **≥ 85 %** | Conformal guarantees ≥ 90 % under exchangeability; 85 % is the tolerance we allow for the post-2016 distribution shift breaking exchangeability. Below it, the bound is not what the slider says. |
| Same, upper limit | **≤ 96 %** | Over-coverage is also failure: a bound that is right 99 % of the time is too wide to change a route, which makes D1 decorative in the other direction. |
| Mean width `SIC_upper − μ`, corridor, lead 5 | **< 25 SIC-%** | Beyond this the bound blockades rather than steers. |
| Interval score vs. Baseline 3 (disagreement proxy) | must **beat** it | Per `WEAKNESS_ANALYSIS.md` §5. |
| 2023 reported separately | no threshold — **must be published** | Honesty, not a gate. |

> **If any of the first four fails:** `SIC_upper` stops being the routed field. The router reverts
> to routing on corrected-mean SIC with a fixed conservative margin, the slider is removed from the
> UI rather than left as theatre, and **D1 is publicly demoted from "uncertainty reaches the routing
> decision" to "uncertainty is reported as a cross-check"** — per D1's own falsifiability clause.
> The pitch then leads on D3/D4/D7 and on the *decision architecture*, not on σ. This branch is
> written down now, before the numbers exist, so it cannot be quietly renegotiated after them.

**(6) One honestly probabilistic per-route number** (per `WEAKNESS_ANALYSIS.md` §1): each candidate
route reports **`P(encounter SIC > threshold anywhere along the route)`**, computed from the
per-cell conformal distributions along the path (independence across cells is *not* assumed — we use
the empirical joint over held-out cases, reported as a range). This makes D1's title honest: a
number derived from the distribution reaches the operator, not only a shifted threshold.

### 1.7 Beyond the skill horizon

The voyage is ~10–14 days and the corrected forecast reaches at most 10. What the router does for
the remaining days is specified in `ARCHITECTURE.md` §2.4a (forecast-grade / CMEMS-direct /
climatology-grade tiering, and daily re-optimisation). It is not left to the UI.

### 1.8 Honest positioning against CMEMS — restated after the pivot

Revision 1 said "we probably lose to CMEMS on RMSE and here is why we are still useful." That is no
longer the claim, because the comparison is no longer adversarial:

- **CMEMS is our base field.** We ship its forecast in the pack, unmodified, as the fallback for
  every lead our correction does not measurably improve (§1.5 acceptance rule). Any lead where we
  claim skill is a lead where we beat it *on its own output*, measured, on held-out real forecast
  cycles.
- **We add what it does not publish:** a routing-consumable, empirically-covered per-cell upper
  bound (§1.6), the innovation-anchored MIZ correction its own documented bias motivates
  (`COMPETITIVE_ANALYSIS.md` §2), and a three-way source-disagreement layer (§4) in which CMEMS is
  one voice rather than the ground truth.
- **The offline argument survives, narrowed and now true.** See §7.2: a packed CMEMS field is
  frozen; our correction head *runs aboard*, so a few KB of fresh observation arriving over Iridium
  re-corrects the whole packed forecast without re-downloading it. That is a real capability
  difference, not a rhetorical one — and it exists *because of* the pivot, not despite it.

---

## 2. Iceberg trajectory prediction

### 2.1 Decision

**Baseline (load-bearing): the Wagner, Dell & Eisenman (2017) closed-form analytical drift
model.**
**Stretch (explicitly optional): a gradient-boosted residual correction on top of it.**

### 2.2 Baseline — Wagner (2017) closed form

`v_i = v_w + γ(α k̂×v_a + β v_a)` as specified in `GAP_ANALYSIS.md` §2. Inputs: ocean current
(CMEMS), wind (ERA5 historical / GFS operational), berg length & width (BYU/USNIC records),
latitude (Coriolis). No fitted parameters beyond standard literature drag coefficients.

Committed as baseline because it needs **zero training data**, is closed-form (no ODE
integration and therefore no numerical-stability failure mode mid-demo), implements in ~100
lines, is unit-testable against the published reference implementation, and is the physics core
that IDRIFTNET itself builds on — so it is not a strawman baseline, it is the field's base case.

### 2.3 Stretch — residual correction, and why *not* a neural network

IDRIFTNET reports 67–82 % ADE reduction from residual learning (`GAP_ANALYSIS.md` §2) — a real
and attractive gain. But it publishes no code, and our training signal is sparse: BYU/USNIC give
weekly-to-daily positions for large tabular bergs only.

**Committed approach: gradient-boosted trees (or ridge regression) predicting the Wagner
model's 24 h displacement residual `(Δx, Δy)`** from tabular features — berg major/minor axis,
local wind speed and direction, current speed and direction, local SIC, latitude, distance from
coast.

This is a deliberate departure from copying IDRIFTNET's spectral neural network, and the
reasoning is the point:

- The residual problem is **small-data and tabular**. Gradient boosting is the correct tool for
  that regime; a neural network is not. IDRIFTNET's own stated motivation for going hybrid was
  that pure neural approaches converge poorly on the available data — the same logic pushes
  further, toward classical ML for the correction term.
- **Interpretable, and interpretability is a judging asset here.** Feature importances let us
  demonstrate that the model recovers known physics — wind dominating for smaller bergs, currents
  dominating for large tabular ones. A model that rediscovers the physics is far more convincing
  than one that merely scores well.
- **Clean fallback, specified as a rule rather than an intention.** `WEAKNESS_ANALYSIS.md` §3 is
  right that "outside the training distribution" and "a sanity bound" are a plan to have a plan,
  and that unspecified triggers silently never fire. Committed now, deliberately at the dumbest
  checkable end:

  ```
  fire_fallback(x, Δ)  =  ANY_OOD(x)  OR  |Δ| > c_sanity
  ANY_OOD(x)  : for any feature j,  x_j < min_j − 0.10·range_j  or  x_j > max_j + 0.10·range_j
                (min_j, max_j, range_j taken from the TRAINING fold only, frozen at fit time
                 and serialised into the model artefact next to the weights)
  c_sanity    : p99 of |residual correction| over the training fold, in km of 24 h displacement
                (a single number, written into the artefact; expected order ~10–25 km — the
                 measured value replaces this estimate when the model is fitted)
  ```

  Features checked: berg major/minor axis, wind speed, current speed, local SIC, latitude,
  distance from coast — the same six the model consumes, no dimensionality reduction, nothing
  that needs its own validation. Per-feature ranges beat Mahalanobis/isolation-forest here
  because they are inspectable in the UI ("berg B-15 fell outside the trained wind-speed range")
  and cannot themselves be miscalibrated.

  **Unit-tested, and the test is the point:** `test_ood_trigger_fires` feeds a feature vector with
  one value pushed past the frozen bound and asserts pure Wagner is returned and the degradation
  flag is set; `test_sanity_bound_fires` asserts the same for an inflated correction. (These are
  synthetic fixtures checking code plumbing, not a model — permitted, and necessary, because an
  untested fallback is an unfired fallback.)

### 2.4 Evaluation protocol

- **Split: leave-one-iceberg-out.** Segments from the same berg are heavily correlated; a random
  segment split leaks the same berg's trajectory into both sides and is meaningless. Holding out
  entire bergs is the only honest protocol.
- **Metrics:** Average Displacement Error and Final Displacement Error, in km, at 24 h / 48 h /
  72 h / 7 d horizons.
- **Two baselines:** (a) velocity persistence (berg continues at last observed velocity),
  (b) pure Wagner physics. The stretch model must beat *both* to ship; if it does not, the
  baseline ships alone and that is a perfectly good outcome.
- Reported on Southern Ocean bergs within the corridor sector.

### 2.5 Uncertainty → hazard buffer, and the horizon cap that keeps it navigable

The residual error distribution (or, for the baseline, the Wagner-vs-observed error distribution
measured on held-out bergs) yields a **drift uncertainty radius that grows with lead time**. That
radius becomes the routing exclusion polygon in §3.4 — an explicit, measured chain from model
error to navigational caution, not a guessed safety margin.

**`WEAKNESS_ANALYSIS.md` §3 identifies the failure this walks into and it is a real one.**
`GAP_ANALYSIS.md` §2 records physics-only ADE of **127–147 km** at IDRIFTNET's evaluation horizons.
An honest 7-day radius of that size around every tracked berg turns the hazard layer into either an
ocean-wide blockade (honest but useless) or a quietly shrunk buffer (useful but dishonest). Neither
is acceptable, so the projection horizon is capped where the buffer is still navigationally
meaningful:

- **Hard cap: drift is projected 72 h, never further.** Radius at lead h = measured **p90** of
  leave-one-berg-out displacement error at 24 / 48 / 72 h. Expect roughly tens of km at 24 h
  growing toward ~100 km at 72 h; the measured numbers replace this expectation and are printed in
  the UI legend.
- **Beyond 72 h, no projection is drawn.** The layer shows **last-known USNIC positions**, labelled
  `position as of <date>, not projected` — a stale fact, not a fabricated forecast.
- **Re-projected daily from fresh positions.** Each nightly pack carries that week's USNIC
  positions, so the 72 h window is always anchored to a recent observation rather than extrapolated
  from an old one. For a 10–14 day voyage the berg layer is therefore always ≤72 h old in the leg
  being executed — which is the only leg where a hard exclusion should bind.
- **Area-fraction auto-downgrade, because a cap alone is not enough.** Before a pack ships, the
  builder computes the fraction of navigable corridor area covered by hard exclusion polygons.
  **If it exceeds 5 %, the berg layer is downgraded from hard exclusion (`excluded_zones`) to a
  weighted cost term for that pack**, and the UI says so. This makes "the buffer blockaded the
  corridor" a detected, handled, visible condition rather than a demo-day surprise.
- **The cap is stated in the UI, not just here:** the berg panel reads *"drift projected to 72 h;
  beyond that, last observed position only."*

### 2.6 Stated limitation — surfaced in the product, not buried

**BYU/USNIC track only large tabular icebergs** (≥ ~10 nm axis for USNIC). Growlers and bergy
bits — the small ice that actually holes a hull — are neither in the training data nor predicted
by this system. This limitation is displayed in the UI next to the iceberg layer, not confined
to documentation. Competitors will present iceberg avoidance as solved; it is not, and saying so
is worth more than pretending otherwise.

---

## 3. Route optimisation

### 3.1 Decision

**Wrap and extend PolarRoute (BAS, MIT). Integration risk was measured, not estimated, and it is
low.**

`GAP_ANALYSIS.md` left this as a judgement call between "integrate PolarRoute" and "reimplement
grid A\*". The hands-on run in §0 settles it decisively in favour of integration.

### 3.2 Evidence behind the call

- **[verified]** Installs clean in ~90 s on Python 3.11 via `uv`, **all binary wheels, zero
  compilation** — the usual geospatial-stack nightmare (GDAL, PROJ, rasterio from source) simply
  does not occur.
- **[verified]** Complete pipeline — mesh → vessel performance → Dijkstra → smoothing — runs in
  **~9 s** for a 10°×20° box. Interactive speed; demo-safe.
- **[verified]** `meshiphi`'s native dataloader registry contains `amsr` (sea-ice concentration),
  `gebco` (bathymetry), `era5_wind`, `era5_sig_wave_height`, `era5_wave_period`,
  `duacs_currents` / `oras5_currents`. This is **almost exactly the source list independently
  confirmed live in `DATASET.md`**. The tool was built to eat our data.
- **[verified]** `ScalarCSVDataLoader` is ~15 lines: any DataFrame with `lat`, `long`, optional
  `time`, and a named value column becomes a mesh layer. **Injecting our own ML outputs requires
  essentially no integration code.**
- MIT licensed, authored by BAS — the institution that operates Antarctic research vessels —
  and v1.1.11 was released 2026-07-02, i.e. actively maintained.

Judge credibility follows from this too: using the domain's own open-source tool *and extending
it where it is provably weak* (§3.4) is a far stronger position than reimplementing A\* and
hoping nobody asks about prior art.

### 3.3 Resolved: does PolarRoute handle icebergs? (open question from `GAP_ANALYSIS.md` §3)

**Checked in source. Answer: no native iceberg model — but a clean, native extension point
exists.** `AbstractShip.model_accessibility()` reads a vessel-config list `excluded_zones` and
marks any cell inaccessible where the named mesh layer is truthy:

```python
if self.excluded_zones is not None:
    for zone in self.excluded_zones:
        try:    access_values[zone] = cellbox.agg_data[zone]
        except KeyError: ...
```

So drift-projected iceberg hazard is injected as a mesh layer named in `excluded_zones`. **No
fork of PolarRoute is required.** This was the specific risk flagged in the gap analysis; it is
now closed.

### 3.4 Our three extensions — where the real work is

PolarRoute is the engine. These extensions are the contribution, and each addresses a verified
limitation of the stock tool.

**(a) Uncertainty-aware ice thresholding.**
`meshiphi`'s own `IceNetDataLoader` ingests IceNet forecasts and **explicitly drops the
`sic_stddev` and `ensemble_members` columns** (verified in source — they appear in its
`df.drop(columns=[...])` call). BAS's own pipeline therefore routes on the *mean* forecast and
discards the uncertainty. We reinstate it:

- The §1 ensemble emits corrected `SIC_mean` and `SIC_std` per cell per lead.
- `fusion/` injects **`SIC_upper = clip(SIC_mean + q̂(lead, regime) · SIC_std, 0, 1)`** as an extra
  mesh layer, where `q̂` is the **conformal quantile** of §1.6 — not a Gaussian z-score. The
  operator-facing control is the **target coverage α (80/90/95 %)**, which selects a different set
  of `q̂`, and the UI reports the *measured* held-out coverage next to the slider.
- Our vessel subclass overrides `extreme_ice()` to threshold on `SIC_upper` instead of `SIC`.
- Each candidate route additionally reports `P(SIC > threshold anywhere along the route)` (§1.6.6),
  so a probability — not only a shifted threshold — reaches the operator.

The vessel then avoids cells that are *probably* passable but *might* not be. This is a real,
citable gap in the incumbent tool that we fill — and it makes an outstanding demo: move the
risk-tolerance slider, watch the route physically migrate. **If §1.6's coverage gate fails, this
extension is demoted rather than shipped decorative** — the branch is written in §1.6.5.

**(b) Iceberg hazard layer.** Drift-projected berg positions (§2), buffered by the §2.5
uncertainty radius, rasterised to the mesh and named in `excluded_zones` per §3.3.

**(c) Dominance-filtered candidate route set from a parameter sweep.** **[verified]**
`route_schema` accepts `objective_function` as a *single string* — PolarRoute is a single-objective
solver.

`WEAKNESS_ANALYSIS.md` §1 is correct that revision 1's three preset runs were **not a Pareto
frontier**: three points with no dominance filtering and no sampling of the trade-off surface is a
menu. We take the review's stronger option rather than the rename, because it costs two minutes:

- **Sweep:** 2 base objectives (`traveltime`, `fuel`) × 6 risk-tolerance settings (conformal α
  levels plus a σ-ignoring `k=0` control) = **12 solver runs**. **[verified]** ~7 s per run →
  **~84 s total**, still inside a demo.
- **Score every route on every objective.** Each of the 12 resulting polylines is then evaluated
  for *all three* quantities — passage time, modelled fuel, and route-integrated ice risk
  (`P(SIC > threshold along route)`, §1.6.6) — so the trade-off triple is measured on the route,
  not inherited from the objective it was solved under.
- **Dominance filter.** A route is discarded if another route is ≤ on all three and < on at least
  one. What survives is a genuine dominance-filtered non-dominated set, typically 3–6 routes.
- **Named honestly either way.** The UI and the pitch call it a **"dominance-filtered candidate
  set (12-run sweep)"**. If a sweep degenerates to a single surviving route, we display one route
  and say the trade-off collapsed — we do not manufacture a frontier.

This delivers the "multi-objective, not shortest-path" property the current literature expects
(`COMPETITIVE_ANALYSIS.md` §3) without forking the solver, and it survives the question "is that
actually a Pareto set?" — which the three-run version did not. Supersedes ADR-011 (see ADR-021).

### 3.5 Vessel model — and honesty about fuel

We subclass `AbstractShip` for MV Vasiliy Golovnin, reusing the published functional forms that
`SDA.py` implements (Riska-type ice resistance parameterised by hull type and beam; ITTC/Kreitner
wave resistance; the 8-heading wind-resistance model) with Golovnin's real published dimensions.

**But `SDA.py`'s fuel polynomial is empirically fitted to the RRS Sir David Attenborough**, and
we do not have Golovnin's power/fuel curve. Therefore:

- Fuel is reported as a **relative comparison between candidate routes**, which is what actually
  informs the decision.
- Any absolute tons/day figure is labelled **uncalibrated model output** in the UI.
- We never print a precise absolute fuel number as though it were validated.

Competitors will display confident absolute fuel savings they cannot possibly have calibrated.
Declining to do so is a differentiator, not a shortfall.

### 3.6 Ice thickness and density — disclosed provenance

`SDA.ice_resistance()` requires `thickness` and `density`. **[verified in source]**
`meshiphi`'s `ThicknessDataLoader` and `DensityDataLoader` docstrings read *"Creates a simulated
dataset of sea ice thickness/density based on scientific literature"* — they are hard-coded
regional/seasonal lookup tables, already carrying a `southern_seasons` mapping.

This independently confirms the concern raised in `DATASET.md` and `COMPETITIVE_ANALYSIS.md` §2:
**no Antarctic ice-thickness product is mature enough to use operationally**, and BAS's own
production tool falls back to a literature climatology. We adopt the same LUT and **disclose it
as a literature-derived climatological parameterisation, not a measurement.** This is a physical
parameterisation of the kind used throughout the field, not fabricated data — but it must be
labelled, because the ice-resistance figure inherits its uncertainty.

Also noted for the build: **[verified]** without `thickness` and `density` present in the mesh,
`SDA.model_speed()` silently skips ice-based speed adjustment entirely. The LUT loaders must be
wired in or the ice physics quietly does nothing.

### 3.7 Rejected alternatives

| Rejected | Reason |
|---|---|
| **Grid A\* reimplementation as the baseline** | Measured integration cost of PolarRoute is low (§3.2), so the usual justification for rolling our own evaporates. Reimplementing would also forfeit non-uniform meshing, physics-informed smoothing, and the vessel-performance framework — and invite "why did you ignore BAS's tool?" |
| **A separate A\* as a demo-safety net** | Unnecessary duplicate work. **[verified]** the unsmoothed Dijkstra path is produced in 0.7 s and is already a valid route; smoothing (6.1 s, the most failure-prone stage) is a *refinement*. If smoothing fails we serve the Dijkstra path flagged as unsmoothed. The fallback is inherent to the pipeline. |
| **Quantum-annealing CQM formulation** | Real in the current literature (`COMPETITIVE_ANALYSIS.md` §2) but requires D-Wave access, and buys optimisation speed we do not need at ~9 s per route. Complexity with no benefit at our scale. |
| **Isochrone method** | Classical and sound, but weaker optimality guarantees than Dijkstra on the discretised mesh, and no existing polar implementation to reuse. |

---

## 4. Multi-source ice fusion and disagreement

Not a model — a deliberate architectural component, grounded in the finding that Copernicus
systematically underestimates ice concentration relative to regional charts, especially in the
marginal ice zone (`COMPETITIVE_ANALYSIS.md` §2).

### 4.1 QC first — because without it, disagreement is meaningless

`WEAKNESS_ANALYSIS.md` §4 lands a point that would have quietly poisoned this whole component:
**a fusion layer with no quality control cannot tell a sensor artifact from genuine
inter-source disagreement**, and would widen the route around a phantom. Passive-microwave SIC has
well-known land spillover and weather-filter false ice; OISST ships `_preliminary` for days
(`DATASET.md` §4.2); GFS cycles go missing; swaths have gaps. `ingest/` therefore gains a **QC pass
that runs before anything is fused**, and its output is itself a first-class layer:

| Check | Action |
|---|---|
| **Land-spillover mask** | Cells within 1 grid cell (25 km) of the GEBCO coastline are flagged `near_coast`; SIC there is not allowed to *create* disagreement on its own. |
| **Weather-filter false ice** | Isolated SIC > 15 % cells with no ice within 2 cells, in open ocean, north of the climatological max extent for that day-of-year → flagged `suspect_false_ice`. |
| **Range checks** | SIC ∈ [0, 100] %, SST ∈ [−2.5, 40] °C, |wind| ≤ 60 m/s. Out-of-range → `invalid`, never silently clipped. |
| **Missing-swath detection** | Contiguous no-data regions above a size threshold → `swath_gap`, with the gap extent recorded, not interpolated away. |
| **Preliminary-data flag** | OISST `_preliminary` files are ingested but tagged; provenance carries the tag through to the pack. |
| **Staleness per source** | Each source's actual observation timestamp, not fetch time. |

Every flag lands in a **`qc_flags` provenance layer** the fusion step reads. **A cell with any flag
is excluded from the disagreement statistic** and its QC-flag fraction is fed to the model as an
input channel (§1.2), so the network can learn to distrust what the ingest layer distrusted. The
UI renders flagged cells distinctly from "sources disagree" cells — they are different facts.

### 4.2 One target grid, named interpolation, halo excluded

Sources arrive on different grids (NSIDC CDR 25 km polar stereographic, AMSR2 12.5 km, OSI SAF
10 km, CMEMS ~8 km, ERA5 0.25° lat/lon), and regridding in the MIZ creates edge artifacts
indistinguishable from disagreement. Fixed by decision rather than left implicit:

- **Target grid: NSIDC south polar stereographic, 25 km** — the observation product's native grid
  (§1.3), so the truth field is never resampled.
- **Interpolation: conservative area-weighted** for concentration fields (it preserves ice area,
  which is what IIEE measures); **bilinear** for continuous forcing (SST, wind, temperature);
  **nearest** for masks and flags.
- **A 1-cell halo around every regridded source boundary and every QC-flagged region is excluded
  from the disagreement statistic**, so a resampling edge cannot masquerade as a source conflict.

### 4.3 Disagreement layer

Where two or more independent, QC-clean SIC sources cover a cell (NSIDC CDR, AMSR2, OSI SAF,
CMEMS), we compute and retain **inter-source disagreement as its own mesh layer**. It is used
twice:

1. Added into the effective uncertainty: `SIC_upper` widens where sources disagree, so the router
   is automatically more cautious exactly where the observational record is least trustworthy.
2. Rendered in the UI as a distinct "sources disagree here" overlay.

The competitor default is to pick one source and present it as ground truth. Surfacing the
disagreement is more honest and produces a measurably different route.

---

## 5. What is actually trained — summary for the pitch

| Component | Trained? | On what real data | Evaluated how |
|---|---|---|---|
| **SIC bias-correction residual U-Net ×5** | **Yes** — trained from scratch (the *model* is ours; the *base field* is CMEMS) | GLORYS12 SIC background + NOAA/NSIDC CDR SIC (25 km) truth + ERA5 + OISST, **1993–2018 train / 2019–21 val / 2022–24 test**; fine-tuned and acceptance-tested on real CMEMS forecast cycles harvested daily from Phase 0 | Temporal hold-out 2022–24 **and** held-out real forecast cycles; RMSE, **IIEE**, F1, CRPS, interval score; **vs. raw packed CMEMS (mandatory, build-blocking), vs. damped anomaly persistence, vs. inter-source-disagreement as a σ proxy**; conformal coverage by lead × regime with a pre-committed pass/fail rule (§1.6.5); 2023 anomaly year reported separately |
| Iceberg drift (Wagner) | No — closed-form physics | ERA5/GFS wind, CMEMS currents, BYU/USNIC geometry | ADE/FDE vs. velocity persistence, leave-one-berg-out, at 24/48/72 h (projection capped at 72 h, §2.5) |
| Iceberg residual GBM *(stretch)* | **Yes** — gradient boosting | BYU/USNIC tracks + ERA5 + CMEMS | ADE/FDE vs. persistence **and** vs. pure Wagner, leave-one-berg-out; unit-tested OOD/sanity fallback (§2.3) |
| Vessel performance | No — published physics, uncalibrated for Golovnin | Vessel dimensions | Relative route comparison only; absolutes labelled uncalibrated |
| Routing | No — Dijkstra, exact on the mesh | All of the above | Route validity, mask compliance, dominance filtering over a 12-run sweep (§3.4c) |

**One trained deep model with measured, conformally calibrated uncertainty, improving a real
operational forecast; one physics model; one optional classical-ML correction.** No LLM, no RAG,
no agent framework appears anywhere in this system — there is no natural-language task in the
problem statement, and every component above is a numerical prediction or a graph search, for
which deterministic and classical methods are better suited here, cheaper, verifiable against
held-out data, and able to run offline on a ship. (Revision 1 said "strictly better suited";
`WEAKNESS_ANALYSIS.md` §2 is right that this was rhetoric. The claim is "better suited, and here
is why," and the why is the offline-inference and verifiability argument, not a universal.)

---

## 6. Riskiest assumption

**That the calibrated bound is well enough covered that routing on `SIC_upper` is genuinely
safer, rather than merely more conservative-looking.**

The pivot changes the shape of this risk but does not remove it. Two things could still break:
(a) conformal coverage assumes exchangeability between the calibration residuals and operations,
and the post-2016 Antarctic regime is a documented distribution shift that can violate it;
(b) Stage A's reanalysis background may not transfer to true forecast backgrounds (§1.3), in which
case the correction is fitted to the wrong error structure.

Mitigated by, in order of strength:

1. **A pre-committed numerical pass/fail rule with a written demotion branch** (§1.6.5) — the
   thing revision 1 did not have. Coverage below 85 % or above 96 % in MIZ cells at lead 5, or a
   bound wider than 25 SIC-%, or losing to the free disagreement proxy, demotes D1 publicly.
2. **A build-blocking baseline** (§1.5) — a lead that does not beat raw packed CMEMS on IIEE *and*
   CRPS is not claimed, and ships the raw field labelled `uncorrected`.
3. **Stage B acceptance on real forecast cycles**, not only on the reanalysis proxy (§1.3).
4. Stratified conformal calibration per lead × regime rather than one global scalar (§1.6.2), and
   input-perturbed rather than seed-only ensemble members (§1.2).
5. Separate reporting on 2023.

**This is testable, and it will be tested before any demo.** Tracked in `docs/backlog.md`.

The *second* riskiest assumption is now a data one and it is time-critical: **the Stage B forecast
archive cannot be back-filled.** If daily CMEMS harvesting does not start at Phase 0, the
acceptance test in §1.5 has nothing to run on in December. That is a scheduling risk with no
technical mitigation, only a calendar one.

---

## 7. Rebuttal notes — where we do not concede

`WEAKNESS_ANALYSIS.md` is adopted almost in full; §1.0, §1.3, §1.6, §2.3, §2.5, §3.4c and §4.1
above are all direct implementations of its findings. Three points are answered rather than
accepted, and they are recorded here rather than argued verbally.

### 7.1 "A 5-member seed-only ensemble is a weak σ estimator" (§8.2) — half-conceded

**Conceded:** seed-only ensembles capture parameter uncertainty alone and under-disperse. We have
added input perturbation (§1.2), which is the review's own cheap fix.

**Not conceded:** the implied remedy — that calibration quality is bounded by ensemble size — no
longer holds under the conformal design. Coverage now comes from **measured held-out residual
quantiles**, not from the ensemble. σ supplies only the *relative spatial shape* of the
uncertainty field; if σ is uniformly too small by a factor, `q̂` absorbs the factor exactly, and
coverage is unaffected. What ensemble size actually buys is the *sharpness* of the bound (a better
shape yields narrower intervals at the same coverage), which is a quality axis, not a safety one —
and it is measured directly by the interval-score and mean-width checks in §1.6.5. So growing the
ensemble to 10 members is an optimisation we may or may not fund; it is **not** a prerequisite for
the calibration claim, and we decline to spend the GPU budget there before the width check says
the shape is the binding constraint.

### 7.2 "The offline argument does not survive packed CMEMS" (§2) — narrowed, not abandoned

**Conceded, and it was the strongest point in the review:** the shore tier can pack CMEMS's
10-day forecast, so "runs offline" did not distinguish our model from *packed* CMEMS. That
observation is what forced the pivot.

**Not conceded — the residual distinction is real and the pivot makes it larger.** A packed CMEMS
field is **frozen at pack-build time**. Our correction head *runs on the bridge* and takes recent
observations as an input channel (§1.2). So when a fresh observation reaches the vessel, the whole
10-day packed forecast can be **re-corrected aboard without re-downloading it** — an operation a
packed third-party field cannot perform at any bandwidth. The payload for that is small: a corridor
SIC field at 25 km is roughly 180×110 ≈ 20 k cells; as scaled uint8, gzipped, an estimated
**5–15 KB**, inside even the legacy sub-50 KB Iridium message budget. *(Estimate, not measured —
`backlog.md` carries it as an item to measure in Phase 1, and if it fails to fit, the honest
position is that the pack is refreshed at whatever cadence the link allows, not that this
capability exists.)*

The claim is therefore narrowed from "our forecast runs offline" (which packed CMEMS also does) to
**"our forecast can be *updated* offline from a few KB of new observation"** — which packed CMEMS
cannot, and which only exists because the model is now observation-conditioned. This is the one
place where the review's kill shot, correctly applied, produced a *stronger* claim than the one it
killed.

### 7.3 "Router refuses to route is an availability failure" (§3) — accepted with a boundary

**Conceded:** a refusal with nothing behind it makes the tool go silent when the master most needs
it. `ARCHITECTURE.md` §2.4a now defines a climatology-grade floor.

**Boundary we insist on:** the floor is a **planning corridor, not a route**. It answers "which
side of the gyre, which longitude to cross the MIZ" at a resolution of hundreds of km — it must
never be rendered with the same line weight, the same waypoint list, or the same fuel/time
precision as a forecast-grade route, and it carries no berg exclusion polygons at all (§2.5 caps
projection at 72 h). StormGeo's human-analyst fallback, cited approvingly in D6, is a fallback that
changes *who* answers and *how confidently* — not one that pretends the same product is still
available. Ours does the same. A graceful floor that looks identical to the full product is a worse
failure than the refusal it replaced.
