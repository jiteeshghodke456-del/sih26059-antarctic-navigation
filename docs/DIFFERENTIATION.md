# Differentiation — SIH26059

Rule for this document: **no adjectives.** Every claim below names a specific component, file,
config field, or measured number in `ARCHITECTURE.md` / `ML_ARCHITECTURE.md`. If a claim cannot
be traced to something buildable, it does not belong here.

Status: **revision 2, 2026-08-31**, after the adversarial review in `WEAKNESS_ANALYSIS.md`. Three
claims were weakened or restated because they did not survive it: **D1** now rests on conformal
coverage with a pre-committed numeric gate rather than a Gaussian `1.28σ`; **D4** leads with the
measured worst case instead of the 796 B route polyline; **D7-3** is a dominance-filtered 12-run
sweep instead of three preset runs called a "Pareto set." **D6** changed the most — the CMEMS
position went from "we probably lose but we're useful anyway" to "CMEMS is our base field and we
beat it on its own output or we don't claim the lead."

The baseline being differentiated *from* is the convergent architecture predicted in
`COMPETITIVE_ANALYSIS.md` §3: pull CMEMS + NIC data → a U-Net → a physics-or-ML drift model →
grid A\* → Leaflet dashboard, demo three cherry-picked scenarios.

---

## D1 — Uncertainty reaches the routing decision, not just the legend

**Claim:** we route on a probabilistic upper bound of ice concentration, not a point forecast.

**Verified gap in the incumbent.** `meshiphi`'s own `IceNetDataLoader` ingests IceNet forecasts
and explicitly discards the uncertainty — the `df.drop(columns=[...])` call removes `sic_stddev`
and `ensemble_members`. BAS's production polar router therefore plans on the mean and throws the
spread away. This is checked in installed source, not inferred.

**Architectural commitments:**
- `models/` trains a **5-member ensemble** — varied by seed **and input perturbation**, not seed
  alone — emitting per-cell corrected `SIC_mean` **and** `SIC_std` (`ML_ARCHITECTURE.md` §1.2).
- `fusion/` computes **`SIC_upper = clip(SIC_mean + q̂(lead, regime) · SIC_std, 0, 1)`**, where
  `q̂` is a **split-conformal quantile** fitted per lead × regime (open water / MIZ / pack) on
  held-out residuals — **not** a Gaussian `1.28σ` (ADR-020, superseding ADR-005's k). Conformal
  because SIC is bounded in [0,1] and its error at the ice edge — the only place that matters — is
  strongly asymmetric and non-Gaussian.
- Our Golovnin `AbstractShip` subclass **overrides `extreme_ice()`** to threshold on `SIC_upper`
  instead of `SIC` (ADR-005).
- The operator control is **target coverage α (80/90/95 %)**, not a sigma multiple, and the UI
  prints the **measured** held-out coverage beside it.
- Each candidate route also reports **`P(SIC > threshold anywhere along the route)`**, derived from
  the per-cell distributions — so a probability, not only a shifted threshold, reaches the operator.

**Falsifiable consequences — now three, and all pre-committed with numbers:**
1. Changing the coverage setting produces a *different route geometry*, not different shading. If
   moving the slider does not move the line, this differentiation has failed and we say so.
2. **Measured coverage must match the label.** On held-out 2022–24 data at nominal 90 %: empirical
   coverage of `SIC_upper` in MIZ cells at lead 5 must fall in **[85 %, 96 %]**, and mean bound
   width at lead 5 must be **<25 SIC-%**. Over-coverage fails too — a bound that is right 99 % of
   the time is too wide to steer by.
3. **The bound must beat the free alternative.** If calibrated σ does not beat **inter-source
   disagreement alone** as an uncertainty estimator (interval score, coverage at equal width), the
   trained σ is decorative and D1 has failed regardless of (1) and (2).

**What happens if a threshold is missed — written down before the numbers exist:** `SIC_upper` is
withdrawn as the routed field, the router reverts to corrected-mean SIC with a fixed conservative
margin, **the slider is removed from the UI rather than left as theatre**, and **D1 is publicly
demoted from "uncertainty reaches the routing decision" to "uncertainty is reported as a
cross-check."** The pitch then leads on D3/D4/D7 and on the decision architecture. This branch
exists so the falsifiability clause above cannot be quietly renegotiated after the numbers arrive
(`ML_ARCHITECTURE.md` §1.6.5).

---

## D2 — Physics-first drift with a classical-ML residual, and a stated blind spot

**Claim:** iceberg drift is neither an opaque black box nor physics-only.

**Architectural commitments:**
- Baseline is the **Wagner (2017) closed form** — real physics, zero training data, no numerical
  integration failure mode (ADR-007).
- Stretch is a **gradient-boosted residual** on 24 h displacement error, not a neural network —
  because the residual problem is small-data and tabular, and because feature importances let us
  demonstrate the model recovering known physics (wind dominates small bergs, currents dominate
  large tabular ones) (ADR-008).
- Evaluated **leave-one-iceberg-out**, against *both* velocity persistence and pure Wagner. If it
  fails to beat both, the baseline ships alone.
- Drift error statistics become the **uncertainty radius** that defines the routing exclusion
  polygon (`ML_ARCHITECTURE.md` §2.5) — a measured chain from model error to navigational caution,
  not a guessed safety margin.

**Honesty commitment — displayed in the UI, not just the docs:** BYU/USNIC track only large
tabular bergs (≥ ~10 nm axis). **Growlers and bergy bits — the ice that actually holes a hull —
are neither in the training data nor predicted.** Competitors will present iceberg avoidance as
solved. It is not.

---

## D3 — Multi-source disagreement is surfaced and acted on, not resolved away

**Claim:** where ice sources disagree, the system becomes more cautious automatically.

**Grounding:** Copernicus systematically underestimates ice concentration relative to regional
charts, especially in the marginal ice zone (`COMPETITIVE_ANALYSIS.md` §2). A team using one
source as ground truth is building on a documented bias without saying so.

**Architectural commitments:**
- `fusion/` retains **inter-source SIC disagreement as its own mesh layer** across NSIDC/AMSR2,
  OSI SAF and CMEMS wherever coverage overlaps (ADR-014).
- Disagreement **widens `SIC_upper`**, so the router is automatically most cautious exactly where
  the observational record is least trustworthy. It changes the route.
- It also renders as a distinct "sources disagree here" overlay.

**Falsifiable consequence:** disagreement is a routing input with a measurable effect on the path,
not a second basemap.

---

## D4 — Bandwidth-honest offline-first design, enforced in CI

**Claim:** the vessel tier runs with no connectivity, and the sync budget is a build-breaking
constraint rather than a documented aspiration.

**Worst case first** (`ARCHITECTURE.md` §1.2). The number that has to move daily is the
**vessel-modelled mesh plus the forecast delta**, not the route polyline — leading with the
polyline would be quoting the smallest payload in the system as if it were the representative one:

| Payload — the daily-moving quantities first | Gzip | Status |
|---|---|---|
| **Vessel-modelled mesh, 10°×20° box** (the representative unit) | **76 KB** | **measured** |
| **Full corridor mesh refresh** | **est. 0.5–1 MB** | **extrapolated, not measured** — the adaptive mesh splits hardest in the MIZ, exactly where the corridor crosses |
| **Daily incremental delta** | **unmeasured** | the load-bearing number; measured in Phase 1, not Phase 4 |
| Model weights (5 × ~3 M params) | ~60 MB | **never over Iridium** — USB at port only (ADR-023) |
| Route polyline + fuel/time summary | 796 B | measured — the *smallest* payload, quoted last on purpose |

**The honest claim: a full corridor refresh is a minutes-to-tens-of-minutes Iridium transfer, and
the daily delta is the number the design depends on and has not yet been measured.** What is
measured is that a representative vessel-modelled mesh block compresses to 76 KB, which makes the
50 KB delta target plausible — not proven.

**And the budget does not move if the measurement disappoints:** the pre-committed response is to
coarsen the open-ocean mesh or lengthen the full-refresh cadence to 2–3 days, never to renegotiate
the number. A bandwidth constraint that moves whenever the data moves is not a constraint.

**One real bandwidth capability that packed third-party forecasts do not have:** because our model
takes recent observations as an input, a fresh corridor SIC observation (~20 k cells as scaled
uint8, **estimated 5–15 KB gzipped**, unmeasured) **re-corrects the entire 10-day packed forecast
aboard** without re-downloading it. A packed CMEMS field is frozen at build time and cannot do
this at any bandwidth (`ML_ARCHITECTURE.md` §7.2).

**Architectural commitments:**
- Tier boundary set at **"sync environmental state, not answers"** — the vessel runs the full
  routing engine locally (~9 s measured), so the master can change waypoints and re-plan with zero
  connectivity (ADR-002). A thin client receiving finished routes was explicitly rejected because
  it cannot answer the operator's next question.
- **CI test fails the build** if a daily incremental pack exceeds 50 KB compressed or a full
  corridor refresh exceeds 1 MB (ADR-017).
- Delta sync is resumable; packs are versioned, signed, and rollback-capable; **sneakernet USB is
  a supported path**, not a degraded one.

**Demo consequence:** disconnect the network mid-demo and continue re-planning routes. This is
unfakeable, and it is how the system is designed to work at sea — the demo setup *is* the product
(ADR-016).

---

## D5 — Corridor- and season-specific, against the real vessel

**Claim:** built for MV Vasiliy Golovnin on the Cape Town → Bharati/Maitri austral-summer run,
not for "Antarctica" in general.

**Architectural commitments:**
- Corridor-scoped mesh, evaluation and tuning; metrics reported **both** circumpolar and
  corridor-restricted (ADR-001). Models still train circumpolar, because more data is free for a
  fully convolutional network — only the operational claim is scoped.
- A **Golovnin-specific `AbstractShip` subclass**, using published resistance functional forms with
  the vessel's real dimensions.
- Season-aware: the austral-summer resupply window is the design case, and meshiphi's
  `southern_seasons` mapping is already Antarctic-oriented.

**Why narrower wins here:** an MoES/NCPOR audience knows this corridor and this ship. Demonstrated
fidelity on the real operational case is verifiable; circumpolar generality is not.

---

## D6 — Honest quantification, including where we decline to quantify

**Claim:** we do not print numbers we cannot defend.

**Architectural commitments:**
- **Fuel:** reported as a **relative comparison between candidate routes**. Absolute tons/day is
  labelled *uncalibrated model output*, because PolarRoute's fuel polynomial is fitted to the RRS
  Sir David Attenborough and we have no Golovnin power curve (ADR-012, verified in source).
- **Ice thickness/density:** disclosed as a **literature-derived climatological lookup table** —
  which is what BAS's own tool uses, its docstring reading *"Creates a simulated dataset ... based
  on scientific literature"*. Labelled as parameterisation, never as measurement (ADR-013).
- **Forecast skill:** a **declared skill horizon that is an output of the evaluation, not an
  assumption** — the last lead that measurably beats raw packed CMEMS (ADR-027). Beyond it the
  router does not go silent; it **tiers down** through CMEMS-direct to a climatology-grade planning
  corridor, each grade visibly different in the UI (ADR-022). A leg we cannot forecast is drawn as
  a dashed band with no waypoints and no fuel figures — not as a confident line, and not as a blank
  screen.
- **Bathymetry:** disclosed as **largely predicted, not surveyed**, in this corridor. GEBCO's TID
  grid drives a provenance-conditional depth margin (20 m surveyed / max(50 m, 3 × draft)
  predicted), with a "predicted bathymetry" overlay. The product states that it is decision
  support and does not replace ENCs (ADR-026).
- **Iceberg drift:** projection is **capped at 72 h** because the honest 7-day uncertainty radius
  (~127–147 km physics-only ADE, `GAP_ANALYSIS.md` §2) would blockade the corridor. Past 72 h we
  show last-observed positions with their date and draw nothing (ADR-025).
- **Versus CMEMS — the position changed, and the change is the honest part.** Revision 1 said "we
  probably lose to CMEMS on RMSE but we are useful anyway." We stopped defending that and rebuilt
  the model as a **bias-correction head on CMEMS itself** (ADR-018). CMEMS is now our base field: we
  ship its forecast in the pack unmodified for every lead we do not measurably improve, and any lead
  where we claim skill is a lead where we beat it **on its own output**, on held-out real forecast
  cycles, on IIEE *and* CRPS — a build-blocking gate, not a claim. We add what it does not publish:
  a routing-consumable bound with measured coverage, an innovation-anchored correction to its own
  documented MIZ underestimate, and a three-way disagreement layer in which it is one voice rather
  than ground truth.

**Why this is differentiation and not weakness:** competitors will display confident absolute fuel
savings and a single authoritative ice number. Every one of those figures is undefendable under
questioning. Being the team that already knows which of its numbers are soft is the stronger
position in front of technical judges — and StormGeo, the actual commercial incumbent, keeps human
route analysts in the loop 24/7 precisely because full automation is not trusted at the edges.

---

## D7 — Real prior art reused and extended, with the extensions named

**Claim:** we use BAS's own polar routing tool and improve it in three specific places.

Reuse → adapt → extend → wrap → replace was applied in order, and the reuse candidate survived:
**[verified]** PolarRoute installs in ~90 s with all binary wheels and runs a complete pipeline in
~9 s, and its native dataloaders (`amsr`, `gebco`, `era5_wind`, `era5_sig_wave_height`,
`duacs_currents`) almost exactly match the sources independently confirmed live in `DATASET.md`.

**Our three extensions, each addressing a verified limitation:**
1. **Uncertainty-aware ice thresholding** — reinstating the `sic_stddev` its IceNet loader drops
   (D1).
2. **Iceberg hazard layer** — injected through the native `excluded_zones` vessel-config hook.
   Source-checked: PolarRoute has no native iceberg model, but needs no fork to accept one
   (ADR-010). This closes the open question left in `GAP_ANALYSIS.md` §3.
3. **Dominance-filtered candidate route set** — **[verified]** `route_schema` accepts only a single
   `objective_function` string, so PolarRoute is inherently single-objective. We sweep **12 runs**
   (2 objectives × 6 risk-tolerance settings, ~7 s each ≈ 84 s), score **every** resulting route on
   **all three** quantities — time, fuel, route-integrated ice risk — and discard dominated routes
   (ADR-021, superseding ADR-011's three preset runs). We call it a *dominance-filtered candidate
   set*, not a "Pareto frontier": 12 samples of a continuous trade-off surface is a set, not a
   frontier, and if the filter leaves one route we show one route and say the trade-off collapsed.

**Why this beats reimplementing A\*:** a domain-literate judge will know PolarRoute exists.
Arriving with "we used BAS's tool and here are three specific things it does not do that we
added" is a substantially stronger position than a from-scratch A\* that invites the question of
why the field's own open-source tool was ignored.

---

## Summary — the one-line contrast

| Dimension | Convergent competitor build | This system |
|---|---|---|
| Ice forecast | U-Net point forecast, from scratch, competing with CMEMS and losing | **bias-correction head on the CMEMS operational forecast**, observation-conditioned, 5-member input-perturbed ensemble, **bound routed on** |
| Baseline compared to | naive persistence | **raw packed CMEMS — build-blocking**, plus damped anomaly persistence as the floor and inter-source disagreement as a σ proxy; strictly temporal split; 2023 anomaly year separate |
| Uncertainty | none, or a σ shown in the legend | **stratified conformal bound with measured coverage**, slider labelled by coverage not sigma, and a **written demotion branch** if coverage misses [85 %, 96 %] |
| Iceberg drift | physics **or** ML | physics **+** classical-ML residual, leave-one-berg-out, unit-tested OOD fallback, **72 h projection cap** so the buffer stays navigable, blind spot stated |
| Routing | grid A\*, single cost | **PolarRoute extended**, 12-run sweep, **dominance-filtered** candidate set |
| Ice truth | one source, presented as ground truth | **multi-source, QC'd first, disagreement widens caution** |
| Data quality | assumed clean | **explicit QC pass**; artifacts cannot masquerade as disagreement; per-channel imputation; declared obs-only pack type |
| Beyond the horizon | silent, or a confident line anyway | **graded degradation**: forecast → CMEMS-direct → climatology planning corridor, re-optimised daily |
| Connectivity | assumes a live backend | **offline-first, 50 KB budget enforced in CI**; weights by USB at port; packed forecast **re-correctable aboard** from ~5–15 KB of new observation |
| Fuel figures | confident absolutes | relative only; absolutes labelled uncalibrated |
| Depth | GEBCO treated as truth | **predicted vs. surveyed disclosed**, provenance-conditional under-keel margin |
| Scope | "Antarctica" | **the real ship, corridor and season — as config, not constants** |
