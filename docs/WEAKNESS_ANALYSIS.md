# Weakness Analysis — SIH26059 (adversarial review, 2026-08-31)

Role: skeptical technical judge, post-architecture / pre-build. Nothing below is softened.
Every finding cites the exact claim it attacks and states what would fix it.
Severity: **[fatal-if-unfixed]** / **[major]** / **[minor]** / **[solid]** (explicitly conceded).

---

## 1. Why this and not the obvious alternative — what is innovation vs. plumbing?

**[solid]** The offline two-tier split (ADR-002) is genuinely earned: the tier boundary was
chosen from measured numbers (72 KB mesh, ~9 s pipeline), not vibes, and it maps to a real,
sourced constraint (Iridium south of 70°S). The meshiphi `IceNetDataLoader` drops-`sic_stddev`
find (D1, ADR-005) is a real, source-verified gap in the incumbent tool. These two are the
project's legitimate claims to innovation.

**[major] But strip the framing and count the actual novel engineering:** (a) one extra mesh
layer `SIC_upper = mean + k·σ` plus one overridden method `extreme_ice()`; (b) one rasterised
polygon layer named in an existing config list (`excluded_zones`); (c) running an existing
solver three times. Each "extension" in D7 is days of work, not weeks. The architecture's
real substance is *integration discipline plus honesty engineering*, and the team should say
that plainly — because a judge who counts lines of novel algorithm will. Specifically:

- **ADR-011 / D7-3 overclaims.** Three solver runs with three preset objective strings is not
  "multi-objective routing"; it is three single-objective routes displayed together. A 3-point
  "Pareto set" with no dominance filtering and no sampling of the trade-off surface is a menu,
  not a frontier. COMPETITIVE_ANALYSIS.md §3 itself says the literature bar is "genuine
  multi-objective constrained optimization." *Fix:* either call it what it is ("three candidate
  routes under named objectives") or sweep the risk weight k and the objective mix to produce
  a real dominance-checked set (still cheap at ~7 s/run — 10–15 runs is 2 minutes).
- **D1 is uncertainty-aware *thresholding*, not uncertainty-aware *routing*.** Routing on a
  shifted deterministic field is the simplest possible use of σ. There is no chance-constrained
  path, no expected-cost-under-uncertainty, no along-route probability of encountering
  >X% SIC. Defensible for the timeline — but D1's title ("uncertainty reaches the routing
  decision") promises more than a threshold swap delivers. *Fix:* add one derived per-route
  number that is honestly probabilistic (e.g. route-integrated probability of crossing the
  15 % edge, computed from the per-cell distributions) so the claim survives scrutiny.

---

## 2. Where is AI necessary — and is ADR-015 (no LLM/RAG) defensible?

**[solid on ADR-015 itself.]** There is no natural-language task in the PS; every component is
numerical prediction or graph search; the FloatChat convergence evidence
(COMPETITIVE_ANALYSIS.md §1) is real. Declining an LLM is not avoidance of something harder —
a RAG wrapper is *easier* than what they committed to. This decision stands. Two caveats:
(a) "strictly better suited" (ML_ARCHITECTURE.md §5) is rhetoric — say "better suited, and
here's why," with the offline-inference argument, not "strictly"; (b) prepare the one-slide
answer for the judge who expects a GenAI checkbox, because at SIH one will.

**[fatal-if-unfixed] The harder thing being avoided is not an LLM — it is CMEMS.** This is the
single most serious structural weakness in the ML design:

- COMPETITIVE_ANALYSIS.md §2 states, in the team's own words, that the CMEMS 10-day
  assimilating forecast is "the operational baseline any 'novel forecasting' claim has to
  beat, and it's a hard bar." ML_ARCHITECTURE.md §1.5 then quietly sets the bar at **damped
  anomaly persistence** instead, and §1.6 concedes CMEMS likely wins on RMSE. The
  architecture directly ducks the bar its own competitive analysis set.
- The §1.6 justification (a) — "an independent forecast that runs entirely offline on the
  vessel" — **does not survive the team's own architecture.** The shore tier has full
  bandwidth (ARCHITECTURE.md §2.1). It can download CMEMS's 10-day forecast every night and
  put it in the voyage pack exactly as it packs the U-Net output. Packed-CMEMS is offline on
  the vessel too, reaches 10 days instead of 7, and needs zero training. The offline argument
  distinguishes the U-Net from *live-API CMEMS*, not from *packed CMEMS* — and packed CMEMS
  is the obvious build. As written, the trained model's genuinely load-bearing roles reduce
  to (b) routing-consumable per-cell σ and (c) the disagreement second opinion — plus,
  unstated, "SIH judges require a trained model."
- GAP_ANALYSIS.md §1 identified the strongest 1–10-day approach as **"DL bias-correction on
  top of a short-range ice-ocean model (e.g. TOPAZ4)"** — i.e. learn to correct the
  operational forecast. ML_ARCHITECTURE.md §1.4's rejection table never mentions it. The
  team's own research recommended the one design that could honestly *beat* CMEMS
  (corrected-CMEMS > raw CMEMS is an achievable, headline-grade claim); the architecture
  silently dropped it in favour of a from-scratch U-Net that concedes the comparison.

*Fix (pick one, before build):* (1) add **packed CMEMS forecast** as a mandatory evaluation
baseline in §1.5 — if the U-Net + calibration does not beat packed CMEMS on IIEE or CRPS in
the corridor, its role must be demoted in the pitch to "independent cross-check feeding the
disagreement layer," and packed CMEMS becomes the primary routed field; or (2) re-aim the
U-Net as a **bias-correction/uncertainty-quantification head on the CMEMS forecast** (inputs:
CMEMS forecast + recent obs; outputs: corrected SIC + σ), which keeps a real trained model,
uses the same data plumbing, and turns "we lose to CMEMS" into "we improve CMEMS and add the
σ it doesn't expose." Option 2 is the stronger system *and* the stronger pitch.

---

## 3. Model wrong / low-confidence / no connectivity — are the fallbacks real?

- **[solid]** Unsmoothed-Dijkstra fallback: verified (0.7 s), structurally inherent, no extra
  code. This one is genuinely robust.
- **[solid]** Pack rollback / staleness-as-first-class-field / sneakernet: sound design.
- **[major] "Router refuses to route + last-known-good ice edge" is an availability failure
  dressed as a safety feature** (ARCHITECTURE.md §2.4, §2.5; D6). The Antarctic MIZ edge can
  move tens of km/day in a storm. After N days dark, the system's answer is a stale edge and
  a red banner — i.e. the tool goes silent exactly when the master most needs help. Refusing
  to emit a confident line is right; having *nothing* behind the refusal is not. StormGeo's
  human-analyst fallback (cited approvingly in D6) exists precisely because the tool must
  still say something. *Fix:* define the degraded product now: climatological ice edge for
  the date ± historical edge-position variability as an explicit wide band, routed with a
  heavily inflated SIC_upper and labelled "climatology mode." That is buildable from data
  already ingested and turns the refusal into a graceful floor.
- **[major] The GBM→Wagner fallback trigger is a plan to have a plan.** ML_ARCHITECTURE.md
  §2.3 says fallback fires "when features fall outside the training distribution, or the
  predicted correction exceeds a sanity bound" — neither is specified. OOD detection on
  tabular features is a design decision (per-feature range check? Mahalanobis? isolation
  forest?), and the sanity bound is a number nobody has picked. Unspecified triggers
  silently never fire. *Fix:* commit now to the dumbest checkable rule (per-feature min/max
  from training ± margin; correction magnitude ≤ p99 of training residuals) and unit-test
  that it fires.
- **[major] Wagner-error-derived exclusion radii may blockade the corridor.**
  ML_ARCHITECTURE.md §2.5 derives the berg exclusion buffer from held-out Wagner error.
  Per GAP_ANALYSIS.md §2, physics-only ADE is **127–147 km** at IDRIFTNET's horizons. An
  honest 7-day uncertainty radius of ~100–150 km around every tracked berg turns the hazard
  layer into either an ocean-wide blockade (honest but useless) or a quietly shrunk buffer
  (useful but dishonest). The "measured chain from model error to navigational caution" is
  admirable right up until the measured error is enormous. *Fix:* cap drift projection at
  the horizon where the buffer stays navigationally meaningful (likely 48–72 h), re-project
  daily from fresh USNIC positions in each pack, and state the cap in the UI.
- **[minor] On-vessel re-inference is under-specified.** ARCHITECTURE.md §2.1 [6] says
  "U-Net inference if fresh forcing arrives." The 14-channel forcing for even a corridor box
  (GFS wind/temp + SST + 7 days of SIC history) has never been sized against the 50 KB
  daily budget — the budget was measured for the *mesh*, not for forcing tensors. Also,
  boundary (b) in §1.1 lists "model weights" in the sync payload: 5 × 8–15 M params is
  160–300 MB fp32 — two-plus orders of magnitude over any Iridium budget. Presumably weights
  ship once via USB at Cape Town; no document says so. *Fix:* one paragraph in
  ARCHITECTURE.md: weights are port-loaded only; forcing-tensor delta measured and either
  fits the budget or on-vessel inference is dropped (pack-only forecasts is a fine design).

---

## 4. Dirty/missing input data, and 10× scale

- **[major] There is no QC layer.** `ingest/` (ARCHITECTURE.md §2.2) does retries, caching,
  provenance — and no quality control. Passive-microwave SIC has known land-spillover and
  weather-filter false-ice artifacts; OISST arrives as "preliminary" for days (DATASET.md
  §4.2); GFS cycles go missing; swath gaps happen. None of this is handled or even named.
  The fusion disagreement layer will happily interpret a sensor artifact as "sources
  disagree" and widen the route around a phantom. *Fix:* add a QC pass to `ingest/`
  (mask known artifact zones, range checks, missing-swath flags) and make "cells with QC
  flags" a provenance layer the fusion step can see.
- **[major] "Pack builds from remaining sources" contradicts a fixed-input U-Net.**
  ARCHITECTURE.md §2.5 says a down source means the pack builds from the rest — but the
  U-Net (§1.2) requires all 14 channels. If ERA5/GFS or OISST is missing, inference is
  impossible unless an imputation rule exists (climatology fill? persistence fill? skip
  forecast, ship obs-only pack?). No rule is stated. *Fix:* define per-channel imputation
  and a "forecast omitted, obs-only pack" degraded pack type now, because this failure
  *will* happen during the build phase, let alone operations.
- **[minor] Regridding is silently assumed.** NSIDC 12.5 km polar stereographic, OSI SAF
  10 km, CMEMS ~8 km, ERA5 0.25° lat/lon — the fusion and disagreement layers require
  everything on one grid, and regridding in the MIZ creates its own edge artifacts that
  will be indistinguishable from "disagreement." Not mentioned in any document. *Fix:* pick
  the target grid, name the interpolation, and exclude a 1-cell regrid halo from the
  disagreement statistic.
- **[minor] 10× scale mostly holds, with two caveats the team already half-knows.**
  Compute scales fine (~9 s for 824 cells; a circumpolar mesh is minutes). But (a) the
  1 MB pack budget fails at circumpolar scale (~45× the measured box ≈ 3+ MB) — acceptable
  only because ADR-001 scopes to a corridor, so say so; (b) backlog.md already flags that
  the corridor estimate (0.5–1 MB) is extrapolated from a box that may not include dense
  MIZ splitting — the adaptive mesh splits hardest exactly where the corridor crosses the
  MIZ, so the real number could exceed 1 MB and break ADR-017's own CI test. Measure early
  in Phase 1, not Phase 4.

---

## 5. Could PolarRoute / CMEMS / StormGeo just replace this? Is D1–D7 overclaiming?

- **PolarRoute alone:** no — it has no forecast, no iceberg layer, routes on the mean, and
  has no offline pack story. The extensions are thin (see §1) but real. D7 stands, with the
  Pareto overclaim trimmed.
- **CMEMS alone:** *partially yes, and the docs don't admit how far.* See §2: packed CMEMS +
  PolarRoute + the iceberg layer + the offline pack machinery delivers most of the user-facing
  value with no training at all. What CMEMS does not provide is routing-consumable forecast
  σ and an independent cross-check. The differentiation survives **only** if the calibration
  work in §8 succeeds; if σ is decorative, the honest system description becomes "PolarRoute
  + packed CMEMS + iceberg buffers + offline sync," and a judge can legitimately ask what the
  team's model added. D1's own falsifiability clause ("if moving the slider does not move the
  line, this differentiation has failed") is the right spirit — extend it: *if calibrated σ
  does not beat a trivial uncertainty proxy (e.g. inter-source disagreement alone), D1 has
  failed too.*
- **StormGeo:** different market (commercial, human-in-loop, subscription, no Antarctic
  resupply specialisation, nothing deployable on an NCPOR bridge laptop). Not a replacement
  threat for this audience. D6's use of StormGeo as an honesty precedent is fine.
- **[major] D4's headline number is rhetorically inflated.** "A route update is two orders of
  magnitude inside the sub-50 KB budget" — 796 B is the *output polyline*, the trivial
  payload; the thing that actually has to move daily is the mesh + forecast delta, which is
  the unmeasured quantity (backlog.md flags it). Leading with the polyline number invites a
  judge to catch the switch. *Fix:* lead with the measured worst case (full corridor mesh),
  not the best case.
- **[major] The NCPOR-overlap question (backlog.md, [major][scope]) is still open and the
  architecture proceeded as if greenfield.** If NCPOR's "Research Vessel Movements" tooling
  already does any of this, D5's "built for the real operational case" flips from strength
  to embarrassment in front of the one audience that would know. This is a 1-hour manual
  portal check that has been deferred through two document passes. Do it before build.

## 6. Demo-only vs. deployable — is ADR-001 a dodge?

**[solid, with one condition.]** Corridor scoping is a legitimate call: the operational
context is real and sourced, models train circumpolar, and evaluation is reported both ways.
It is *not* a dodge **provided the corridor is config, not constant** — the AOI, vessel
parameters, and season must demonstrably be a config file so the team can answer "and for a
different vessel or the Ross Sea?" with a 30-second re-run, not a shrug. No document commits
to config-driven AOI; make it an explicit requirement.

Honest demo-only inventory (fine for SIH, but the team should be able to recite it):
pack *signing* (no key-management story — theater until there is one); *resumable Iridium
delta sync* (will only ever be tested over throttled localhost — say "tested under emulated
link constraints," never "tested over Iridium"); Golovnin vessel model (resistance functional
forms with uncalibrated fuel — already honestly labelled, ADR-012 **[solid]**); the
2.6 GHz-laptop assumption for the bridge machine (fine, CPU-only inference is genuinely
cheap, but state the minimum spec).

---

## 7. What a strong competing team would say (concrete)

1. "Your 'uncertainty-aware routing' is one added mesh layer and a threshold swap
   (ADR-005); your 'multi-objective optimisation' is running BAS's solver three times
   (ADR-011). What did *you* build?" — see §1 fixes.
2. "Your own competitive analysis calls CMEMS the bar to beat (COMPETITIVE_ANALYSIS.md §2);
   your eval protocol (ML_ARCHITECTURE.md §1.5) benchmarks damped persistence and §1.6
   concedes the CMEMS comparison. Why should the vessel route on your forecast instead of a
   packed copy of CMEMS's?" — see §2. This is the kill shot as currently written.
3. "AMSR2 launched in 2012. Your training table (ML_ARCHITECTURE.md §5) says
   'NSIDC/AMSR2 SIC … 1979–2018 train.' Which product are you actually training on?" —
   see §9; the training-data spec is internally impossible as written.
4. "Your 7-day skill horizon (§1.5) is shorter than the ~10–14-day Cape Town→Bharati
   voyage. What does the router use for days 8–14 of the departure plan, given ADR/§2.4
   says it *refuses* to route past the horizon?" — Nothing in any document answers this.
   *Fix:* explicit policy — beyond day 7, route on packed-CMEMS days 8–10 and climatology
   beyond, with widening uncertainty; the plan re-optimises daily as packs arrive. This is
   easy to design and currently simply absent.
5. "Your iceberg system tracks only ≥10 nm bergs and you admit growlers hole hulls
   (§2.6). So the PS's 'iceberg trajectory prediction' is solved only for the bergs that
   are trivially visible from the bridge?" — the honesty banner is right, but pair it with
   the mitigation that exists: SAR-based detection as the named stretch, and MIZ-proximity
   as a proxy hazard for small-ice risk in the routing cost.
6. "Where's the GPU?" — no compute plan anywhere; see §9.

## 8. The riskiest assumption (ML_ARCHITECTURE.md §6) — is the mitigation sufficient?

**No — as specified it is wishful on three counts, fixable on all three.**

1. **A scalar variance-inflation factor cannot repair conditional miscalibration.** Ensemble
   overconfidence is state-dependent: worst in the MIZ, at long leads, and in anomalous
   regimes — exactly where the router consumes σ. One global scalar fitted on 2019–21
   reliability re-scales everything uniformly; SIC_upper stays wrong where it matters and
   becomes over-wide where it doesn't. Worse, a VIF fitted on pre-shift validation years is
   itself a pre-shift statistic being trusted under the very distribution shift it is meant
   to absorb. *Fix:* calibrate per-lead and stratified by regime (MIZ vs. pack vs. open
   water) at minimum; better, use conformal prediction on the corridor (distribution-free
   coverage, trivially implementable from validation residuals) or train the heads with
   CRPS loss so the distribution is learned, not bolted on.
2. **A 5-member seed-only ensemble is a weak σ estimator.** Same data, same architecture,
   same inputs — seed ensembles capture parameter uncertainty only, systematically
   underestimate total uncertainty, and a 5-sample standard deviation is itself very noisy
   per cell. *Fix (cheap):* add input perturbation (train members on jittered/forcing-varied
   inputs) or at least acknowledge and absorb the known low bias into the calibration step.
3. **k = 1.28 ⇒ "90th percentile" (D1, ADR-005) assumes Gaussian errors on a variable
   bounded in [0,1].** Near the ice edge — the only place that matters — SIC error is
   strongly non-Gaussian and asymmetric; mean + 1.28σ is not a 90th percentile there, and
   can exceed 1.0. *Fix:* clip and report empirical coverage of SIC_upper on held-out data
   (what fraction of true SIC values fall below it, by regime); market the slider by
   *measured coverage*, not by a z-score.
4. **"2023 held out and reported separately" is reporting, not mitigation.** Honest, yes.
   But if 2023 shows σ badly under-dispersed, the plan has no branch — no "then we widen k
   floor / switch to conformal / demote the model" decision rule. *Fix:* pre-commit the
   decision rule: minimum acceptable held-out coverage (e.g. SIC_upper ≥ true SIC in ≥85 %
   of MIZ cells at day 5), below which D1 is publicly demoted per its own falsifiability
   clause.

## 9. Timeline reality check (ARCHITECTURE.md §4)

**Phase 2 slips. It is the long pole and the plan underestimates it on three counts:**

- **The training-data path has never been exercised.** DATASET.md's "verified live" for the
  load-bearing inputs means HTTP 200 on landing pages: gridded NSIDC SIC needs Earthdata +
  `.netrc` bulk auth (never round-tripped — only the scalar extent CSV was fetched); ERA5
  needs a CDS account (reachability = one HTTP 202, no file ever retrieved); CMEMS subset()
  never called (backlog.md). **Not one byte of actual training data has been downloaded.**
  CDS queue latency for multi-decade requests is notoriously hours-to-days per request and
  appears nowhere in the plan.
- **The training spec is internally impossible as written.** ML_ARCHITECTURE.md §5: "NSIDC/
  AMSR2 SIC … 1979–2018." AMSR2 exists from mid-2012 (AMSR-E 2002–2011, gap Oct 2011–Jul
  2012); OISST starts Sep 1981. Training 1979–2018 requires the 25 km SSM/I-family CDR — a
  *different product, resolution, and error character* than the 12.5 km AMSR2 stream DATASET.md
  §1.1 verifies for operations. Train/serve input mismatch is either accepted and documented,
  or the training window shrinks to the AMSR2 era (2012–2018 ≈ 6 years — is that enough for
  5 U-Nets + a 3-year validation + 3-year test split? Nobody has checked). *Fix:* resolve the
  product choice on paper this week; it changes the data volume, the split, and possibly the
  architecture's viability.
- **No compute plan exists.** Five U-Nets on ~decades of daily circumpolar 14-channel data;
  INFRASTRUCTURE_AUDIT.md shows torch not installed and no GPU mentioned in any document.
  "1–2 weeks" for Phase 2 is a guess with no hardware under it.

**Honest fallback if Phase 2 slips (currently unstated — state it):** ship Phase 1 + 3 + 4
with **packed CMEMS forecast** as the routed field and inter-source disagreement as the
uncertainty proxy driving SIC_upper. That system still demos the offline pack, the slider,
the iceberg layer, and the Pareto routes — and it degrades the pitch from "our trained model"
to "our decision architecture," which must be beaten into shape *now* so it is a planned
fallback, not a scramble. Note this fallback conflicts with the "Real AI only" bar unless the
GBM residual or a bias-correction model survives — one more reason to prefer §2's option 2
(bias-correct CMEMS: a smaller model, less data, faster training, and a stronger claim).

Phases 0, 1, 4 are realistically sized. Phase 3 depends on Phase 2's σ existing; with the §2
restructure it survives a Phase 2 slip. The plan also never states what is prep vs. what is
rebuilt in the 36-hour finale — decide, because "re-run training at the nodal centre" is not
a thing.

## 10. What the architecture silently ignored or contradicted in its own research docs

1. **GAP_ANALYSIS.md §1's top 1–10-day recommendation** (DL bias-correction of an operational
   short-range ice-ocean model) is absent from ML_ARCHITECTURE.md §1.4's rejection table —
   the one alternative that was never argued against is the strongest one. (See §2.)
2. **COMPETITIVE_ANALYSIS.md §2's "CMEMS is the bar to beat"** vs. §1.5's damped-persistence
   bar. Direct internal contradiction. (See §2.)
3. **DATASET.md §1.1 (AMSR2, 12.5 km, Earthdata-gated)** vs. **ML_ARCHITECTURE.md §5's
   "AMSR2 … 1979–2018"** — chronologically impossible; training product undecided in fact
   while presented as decided. (See §9.)
4. **Operational wave forecasts have no verified source.** The hazard fusion includes waves
   (ARCHITECTURE.md §2.1 [3]); DATASET.md verifies ERA5 waves (reanalysis, not forecast) and
   GFS *wind* only. GFS-Wave exists but was never checked. Either verify it or drop waves
   from the operational hazard claim.
5. **backlog.md's [major] NCPOR-overlap item** — architecture proceeds greenfield with the
   question still open. (See §5.)
6. **COMPETITIVE_ANALYSIS.md §2's OSI SAF ice-drift product (OSI-405-d, 62.5 km)** — a free
   observational drift field that could validate Wagner or feed the fusion layer; never
   mentioned again. Cheap win, currently ignored.
7. **DATASET.md §6.2's ENC/charted-hazard gap** is honestly logged, but the routing layer
   never states its consequence: GEBCO-predicted (unsurveyed) bathymetry means depth in this
   corridor is a *model*, and the router treats it as truth. One sentence of disclosure plus
   a conservative depth margin fixes it; silence invites the question from anyone who has
   read the Antarctic ENC coverage story.

---

## Verdict

The system-architecture skeleton (two-tier offline pack, PolarRoute wrap, honesty
engineering) is sound and better-verified than typical SIH work — the [verified] discipline
is real and the strongest thing about these documents. But the ML core has a structural
justification problem (§2), a calibration mitigation that will not survive contact (§8), and
a training-data spec that is currently impossible as written with zero bytes downloaded and
no compute plan (§9). **Do not start Phase 2 as specified.** Fix order: (1) resolve the
CMEMS positioning — add packed-CMEMS as a baseline or pivot to bias-correction; (2) resolve
the SIC training product/window contradiction and round-trip one real download of each of
NSIDC-gridded, ERA5, CMEMS, plus name the GPU; (3) upgrade the calibration plan from scalar
VIF to per-lead/regime or conformal, with a pre-committed pass/fail coverage rule; (4) close
the day-8-to-14 routing-horizon hole and the NCPOR-overlap check. Phases 0–1 can start
immediately in parallel — nothing above blocks the non-ML vertical slice.
