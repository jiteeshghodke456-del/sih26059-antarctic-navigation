# Decision Log — SIH26059

ADR-style. One paragraph each: what was decided, what else was considered, why this won.
Full reasoning lives in `ML_ARCHITECTURE.md` and `ARCHITECTURE.md`; this is the index.
All decisions dated **2026-08-31** unless noted. **[verified]** marks a claim backed by a
hands-on run in this sandbox rather than by documentation.

---

**ADR-001 — Scope to the Cape Town → Bharati/Maitri corridor, austral summer.**
Build and tune for the real, sourced operational context — one chartered vessel (MV Vasiliy
Golovnin), one corridor, one season — rather than a generic "anywhere in Antarctica, any time"
system. *Considered:* circumpolar generality, which is what the one-line problem statement
literally implies. *Why:* a narrow scope can be validated against the real operational case and
tuned to genuinely higher fidelity, whereas circumpolar generality is unverifiable and dilutes
accuracy everywhere. For an MoES/NCPOR audience that knows this corridor, demonstrated fidelity
on the real route beats unfalsifiable breadth. The models train circumpolar (more data, free for
a fully convolutional net); only evaluation, tuning and deployment are corridor-scoped.

**ADR-002 — Two-tier architecture, with the boundary at "sync environmental state, not answers."**
Shore tier does ingestion, training and nightly pack building; vessel tier runs the full routing
engine locally against a cached pack. *Considered:* (a) thin client receiving finished routes,
(b) this, (c) full stack aboard. *Why:* (a) cannot re-plan, so the master's next question goes
unanswered and it stops being decision support; (c) is impossible over Iridium. **[verified]** the
whole PolarRoute pipeline runs in ~9 s and an environmental mesh compresses to 72 KB per 10°×20°
box, so putting the decision engine aboard is affordable — this measurement is what justifies (b)
over the brief's suggested "cached tiles and recommendations."

**ADR-003 — One codebase, two run modes (`MODE=shore|vessel`).**
A single FastAPI application switched by config, not two separate products. *Considered:* separate
shore service and vessel client. *Why:* roughly halves build time on an SIH schedule, guarantees
the routing behaviour is identical in both places, and is architecturally truthful — the routing
and inference code genuinely is the same on both sides. Only ingestion/training jobs and freshness
metadata differ.

**ADR-004 — Sea-ice forecasting: a 5-member deep ensemble of U-Nets, direct multi-lead, days 1–7.**
**SUPERSEDED as the primary model by ADR-018; RETAINED as the named contingency** if the CMEMS
base-field gate in `ML_ARCHITECTURE.md` §1.4 fails. The architecture, the anti-autoregressive
argument and the `icenet` rejection below all still stand and are reusable verbatim; what changed
is that forecasting the field from scratch concedes a comparison to CMEMS we can instead win by
correcting it. Do not delete this ADR — it is the fallback design, not a discarded one.
*Considered:* ConvLSTM, reusing the `icenet` library, reimplementing ANTSIC-UNet at seasonal lead,
CICE dynamical modelling, an LSTM on the extent time series. *Why:* U-Net beats ConvLSTM on
training stability, speed and ice-edge sharpness, and matches the architecture family both
Antarctic-relevant reference models actually use; direct multi-lead heads avoid the compounding
error and incoherent variance of autoregressive rollout, which matters because the router consumes
that variance. Days 1–7 is the horizon a voyage decision actually operates on. **[verified]**
`icenet` 0.2.9 pins `netcdf4<1.6.1` and `python<3.12`, which conflicts irreconcilably with
`meshiphi`/`polar-route` (`netcdf4==1.7.4`) — and its published validation is Arctic with no
Southern-Hemisphere weights, so it would need full retraining regardless.

**ADR-005 — The ensemble's uncertainty is a product feature, not diagnostics.**
**PARTIALLY SUPERSEDED by ADR-020**: the principle (uncertainty reaches the routing cost function,
`extreme_ice()` thresholds on an upper bound, k is an operator control) stands unchanged and is the
core of D1. The *construction* of the bound does not: `mean + 1.28·σ` assumed Gaussian errors on a
variable bounded in [0,1], which is wrong precisely at the ice edge. ADR-020 replaces it with a
stratified conformal quantile and re-labels the operator control by measured coverage.
Per-cell standard deviation is carried all the way into the routing cost function as
`SIC_upper = SIC_mean + k·SIC_std`, and our vessel subclass overrides `extreme_ice()` to threshold
on it. *Considered:* routing on the mean forecast, as is standard. *Why:* **[verified in source]**
`meshiphi`'s own `IceNetDataLoader` explicitly drops the `sic_stddev` and `ensemble_members`
columns — BAS's production tool routes on the mean and discards the uncertainty. This is a real,
citable gap in the incumbent that we fill, it changes the computed route rather than just the
display, and it makes the risk tolerance an operator-facing control.

**ADR-006 — Benchmark against damped anomaly persistence, on a strictly temporal split.**
**PARTIALLY SUPERSEDED by ADR-027 (baseline) and ADR-019 (window).** The temporal-split reasoning
below is the part that matters and it is unchanged and still binding. What changed: damped anomaly
persistence is demoted from headline baseline to floor, because ADR-027 makes raw packed CMEMS the
mandatory bar; the train window starts in 1993, not "≤2018" from an unstated beginning, because
ADR-019 fixed a chronologically possible product; and the "fit a scalar variance-inflation factor"
clause at the end is **withdrawn** — see ADR-020.
Train ≤2018 / validate 2019–21 / test 2022–24, with 2023 (extreme-minimum year) reported
separately. *Considered:* naive persistence as the baseline and a random train/test split — both
common in this space. *Why:* a random split on autocorrelated daily geophysical fields leaks
adjacent days across the split and inflates results to the point of meaninglessness; naive
persistence is too weak a bar to prove a model adds value. Damped anomaly persistence is the
honest short-lead baseline. Calibration (reliability diagram, CRPS) is mandatory because ADR-005
makes miscalibration a safety issue rather than a cosmetic one.

**ADR-007 — Iceberg drift: Wagner (2017) closed form as the load-bearing baseline.**
*Considered:* a pure ML sequence model on BYU/NIC tracks; the empirical 2 %-of-wind rule.
*Why:* it needs zero training data, is closed-form (so it has no numerical-integration failure
mode mid-demo), uses only inputs confirmed available, and is the physics core that the SOTA
hybrid itself builds on — so it is a real base case, not a strawman. The 2 % rule explicitly does
not hold for the large tabular bergs that dominate the Southern Ocean.

**ADR-008 — Iceberg residual correction: gradient boosting, and a stretch goal, not baseline.**
*Considered:* replicating IDRIFTNET's residual spectral neural network, which reports 67–82 % ADE
reduction. *Why:* IDRIFTNET publishes no code, and the available real training signal is sparse
and tabular (weekly-to-daily positions, large bergs only). Gradient boosting is the right tool for
a small-data tabular residual; a neural net is not — and IDRIFTNET's own stated motivation for
going hybrid was that pure neural approaches converge poorly on this data volume, which pushes
further toward classical ML for the correction term. Bonus: feature importances let us show the
model recovering known physics (wind dominating small bergs, currents dominating large tabular
ones), which is more persuasive than a score. Evaluated leave-one-iceberg-out, because random
segment splits leak the same berg into both sides. Falls back to pure Wagner out of distribution.

**ADR-009 — Routing: wrap and extend PolarRoute rather than reimplement A\*.**
*Considered:* grid A\* from scratch (the gap analysis's fallback), isochrone methods, a
quantum-annealing CQM formulation. *Why:* the integration risk was measured rather than estimated
and came back low — **[verified]** clean ~90 s install on Python 3.11 with all binary wheels and
zero compilation; complete mesh → vessel → Dijkstra → smoothing pipeline in ~9 s; and a native
dataloader registry (`amsr`, `gebco`, `era5_wind`, `era5_sig_wave_height`, `duacs_currents`) that
almost exactly matches the sources independently confirmed live in `DATASET.md`. Reimplementing
would forfeit non-uniform meshing, physics-informed smoothing and the vessel-performance framework
while inviting "why did you ignore BAS's own tool?" from a domain-literate judge.

**ADR-010 — Inject iceberg hazard through PolarRoute's `excluded_zones` hook; do not fork.**
This closes the open question flagged in `GAP_ANALYSIS.md` §3. *Checked in source:* PolarRoute has
**no** native iceberg model, but `AbstractShip.model_accessibility()` reads a vessel-config
`excluded_zones` list and marks cells inaccessible wherever the named mesh layer is truthy.
*Why:* drift-projected berg positions with uncertainty buffers become an ordinary mesh layer named
in that list. No fork, no patched dependency, and upstream updates stay consumable.

**ADR-011 — Deliver multi-objective routing as a 3-point Pareto set from three solver runs.**
**SUPERSEDED by ADR-021.** The single-objective finding about `route_schema` below is verified and
still true; the conclusion drawn from it was overclaimed. Three preset runs with no dominance
filtering is a menu, not a frontier, and calling it a "Pareto set" invited exactly the challenge
`WEAKNESS_ANALYSIS.md` §1 made.
*Considered:* forking PolarRoute for true multi-objective search; collapsing to a single weighted
cost. *Why:* **[verified]** `route_schema` accepts `objective_function` as a single string, so
PolarRoute is inherently single-objective. At ~7 s per run, running it three times (travel time,
fuel, risk-weighted) is nearly free and exposes the trade-off explicitly instead of hiding it in
one number — which is where the current literature sits — without touching their solver.

**ADR-012 — Report fuel as a relative comparison; label absolutes as uncalibrated.**
*Considered:* presenting absolute tons/day and percentage fuel savings, as commercial tools do.
*Why:* **[verified in source]** the fuel polynomial in PolarRoute's `SDA.py` is empirically fitted
to the RRS Sir David Attenborough, and we have no power/fuel curve for Golovnin. We reuse the
published resistance *functional forms* with Golovnin's real dimensions, but any absolute fuel
figure would be uncalibrated transfer. Route-to-route comparison is what informs the decision
anyway, and declining to print false precision is a credibility gain against competitors who will.

**ADR-013 — Use meshiphi's literature LUT for ice thickness/density, and disclose it.**
*Considered:* sourcing a real Antarctic thickness product; omitting ice resistance entirely.
*Why:* **[verified in source]** meshiphi's `ThicknessDataLoader` docstring reads *"Creates a
simulated dataset of sea ice thickness based on scientific literature"* — a hard-coded
seasonal/regional lookup table, already carrying a `southern_seasons` mapping. This independently
confirms that no Antarctic thickness product is mature enough to use operationally, and shows
BAS's own production tool falling back to climatology. We adopt the same parameterisation and
label it as literature-derived climatology rather than measurement. Note also **[verified]** that
without thickness and density present, the ice-resistance speed adjustment silently does nothing —
the LUT must be wired in or the ice physics is inert.

**ADR-014 — Surface multi-source disagreement as its own layer instead of picking a winner.**
Where sources overlap, inter-source SIC disagreement is retained as a mesh layer, widens
`SIC_upper`, and renders as a UI overlay. *Considered:* selecting the single best source, the
default approach. *Why:* Copernicus is documented to systematically underestimate concentration
versus regional charts, especially in the marginal ice zone (`COMPETITIVE_ANALYSIS.md` §2), so a
single source presented as ground truth is quietly building on a known bias. Making disagreement
widen the routing caution automatically is more honest and produces a materially different route.

**ADR-015 — No LLM, RAG, or agent framework anywhere in this system.**
*Considered:* a natural-language query layer over the data, which is the pattern four independent
teams converged on for the sibling FloatChat problem statement. *Why:* there is no natural-language
task in this problem statement. Every component is a numerical prediction or a graph search, for
which deterministic and classical methods are strictly better — cheaper, verifiable against held-
out data, and able to run offline on a ship with no inference endpoint. Adding an LLM would move
the visible "AI" away from the trained model and toward a retrieval wrapper, which is exactly the
shallow pattern identified as the predictable competitor failure mode.

**ADR-016 — Demo runs from committed scenario packs, never a live fetch.**
*Considered:* live API calls during the demo (Alternative C); a fully static precomputed site
(Alternative D). *Why:* this takes Alternative D's reliability without its inertness — the real
router really executes on stage, against a real cached pack, so nothing is faked, and no
third-party API or venue network can break the demo. It also happens to be exactly how the system
is designed to work at sea, so the demo setup *is* the product, not a special case.

**ADR-017 — Enforce the sync budget in CI.**
Daily incremental sync must fit in 50 KB compressed; a full corridor refresh under 1 MB. A test
fails the build if a generated pack exceeds budget. *Considered:* treating bandwidth as a
documented aspiration. *Why:* **[verified]** a route pack compresses to 796 B and a 10°×20°
environmental mesh to 72 KB, so these budgets are real and achievable — which means they should be
enforced rather than hoped for. It converts "bandwidth-honest design" from an adjective into a
build-breaking constraint. *Amended (rev. 2):* the budgets are unchanged, but the honest headline
is the **76 KB measured vessel-modelled mesh** and the **unmeasured daily delta**, not the 796 B
polyline; and the pre-committed response if the corridor mesh misses the target is to coarsen the
open-ocean mesh or lengthen the full-refresh cadence, **never to move the budget**
(`ARCHITECTURE.md` §1.2).

---

## Revision 2 — decisions taken in response to `WEAKNESS_ANALYSIS.md` (2026-08-31)

**ADR-018 — Re-aim the sea-ice model as a bias-correction / uncertainty-quantification head on the
CMEMS operational forecast. Supersedes ADR-004 as the primary model.**
The network learns a residual `ΔSIC` on the CMEMS 10-day forecast, conditioned on the last 7 days
of real observations and on the analysis-minus-observation innovation, and emits corrected SIC plus
a calibrated bound. *Considered:* (a) keeping the from-scratch direct forecaster and merely adding
packed CMEMS as a baseline — `WEAKNESS_ANALYSIS.md` §2's option 1; (b) this — its option 2; (c)
dropping the trained model and shipping packed CMEMS with a disagreement-based uncertainty proxy.
*Why:* (c) fails the "real AI" bar and abandons the differentiation. (a) leaves the routed field as
a third-party product with our model demoted to a cross-check, and does not answer "why should the
vessel route on your forecast instead of a packed copy of CMEMS's?" — it just makes the loss
official. (b) keeps a real trained model, reuses the identical data plumbing, targets a
*documented* deficiency of the base field (Copernicus underestimates concentration in the MIZ,
`COMPETITIVE_ANALYSIS.md` §2), cannot be worse than the bar by construction, is ~4× smaller and
cheaper to train than the from-scratch net, and converts the strongest attack on the design into
its strongest claim. **`GAP_ANALYSIS.md` §1 recommended exactly this and revision 1 missed it** —
because the row named TOPAZ4, an Arctic-only system, and revision 1 read a *method* as a *product*
(`ML_ARCHITECTURE.md` §1.0). The Antarctic-covering equivalent, CMEMS
`GLOBAL_ANALYSISFORECAST_PHY_001_024`, was already in `DATASET.md` §4.1 being used for currents.
*Gate:* a real authenticated pull of `siconc` at leads 1–10 must succeed by end of Phase 1, or
ADR-004 is reinstated.

**ADR-019 — Training product and window: the NOAA/NSIDC 25 km SSM/I–SSMIS CDR as the single
observation product; 1993–2018 train / 2019–21 validate / 2022–24 test; GLORYS12 as the training
background; a self-harvested CMEMS forecast archive for fine-tuning and acceptance.**
*Considered:* the review's two options — (a) train on the long 25 km CDR and serve on 12.5 km
AMSR2, documenting the mismatch, or (b) shrink training to the AMSR2 era (~2012–). *Why neither:*
(a) ships a model trained at one resolution and error character and fed another; (b) leaves ~6
years before the validation boundary. The CDR family runs 1979–present **including its NRT
operational stream**, so choosing it eliminates the train/serve mismatch rather than disclosing it,
and 25 km is what both Antarctic reference models use and is finer than the mesh cells downstream.
**AMSR2 12.5 km is reassigned**, from a model input to an independent second observation source for
the D3 disagreement layer — a better job, since feeding it to the network would have destroyed the
independence D3 depends on. The 1993 start is set by GLORYS12's coverage. *Known weakness, stated:*
a reanalysis background is not a forecast background; Stage B (real harvested forecast cycles) is
the transfer test, and failing it triggers ADR-027's demotion, not a footnote. *Hard consequence:*
the forecast archive cannot be back-filled, so daily harvesting starts at Phase 0.

**ADR-020 — Calibration by stratified split-conformal prediction with a pre-committed pass/fail
coverage rule. Supersedes ADR-005's `k = 1.28` and withdraws ADR-006's scalar variance-inflation
factor.** `SIC_upper = clip(μ + q̂(lead, regime)·σ, 0, 1)`, with `q̂` an empirical quantile of
σ-scaled one-sided residuals over 30 strata (leads 1–10 × open-water/MIZ/pack). *Considered:*
keeping the scalar VIF; per-lead-only calibration; training with CRPS loss so the distribution is
learned. *Why:* a single scalar cannot repair state-dependent miscalibration, and — worse — a VIF
fitted on pre-shift validation years is a pre-shift statistic being trusted under the very shift it
is meant to absorb. Conformal is distribution-free (so it makes no Gaussian assumption on a
bounded, asymmetric variable), one-sided (matching how ice-edge error actually fails), trivially
implementable from validation residuals, and lets the operator control be **target coverage**
rather than a z-score — so the slider is marketed by measured coverage, which is a stronger claim
than a sigma multiple. CRPS-loss heads remain a live option and are compatible; conformal is
committed because it delivers the guarantee without depending on training succeeding.
*Pre-committed gate, written before the numbers exist:* MIZ coverage at lead 5 must be ≥85 % and
≤96 %, mean bound width <25 SIC-%, and the calibrated σ must beat inter-source disagreement as an
uncertainty proxy. **Failing any of these demotes D1 publicly and removes the slider** rather than
leaving it as theatre (`ML_ARCHITECTURE.md` §1.6.5).

**ADR-021 — Multi-objective routing is a 12-run parameter sweep with dominance filtering, named
honestly. Supersedes ADR-011.** 2 base objectives × 6 risk-tolerance settings = 12 runs at
**[verified]** ~7 s each ≈ 84 s; every resulting route is then scored on *all three* quantities
(time, fuel, route-integrated ice risk) and dominated routes are discarded. *Considered:* renaming
the three-run version to "three candidate routes under named objectives" — the review's cheaper
option. *Why the more expensive one:* the sweep costs 84 seconds and produces a defensible
dominance-filtered set, whereas the rename permanently forfeits the "multi-objective constrained
optimisation" property `COMPETITIVE_ANALYSIS.md` §3 says the literature expects. When 84 seconds
buys back a real claim, take the claim. We still name it "dominance-filtered candidate set," not
"Pareto frontier," because 12 samples of a continuous trade-off surface is a set, not a frontier —
and if the filter leaves one route, we show one route and say the trade-off collapsed.

**ADR-022 — The router always plans the whole voyage; the *grade* of each leg degrades instead.**
Forecast-grade (corrected + conformal bound) → CMEMS-direct (raw packed CMEMS with a band measured
from the harvested archive) → climatology-grade (last-10-year day-of-year median with inter-annual
spread, rendered as a dashed planning corridor, not a route). Plus daily re-optimisation.
*Considered:* revision 1's "refuse to route past the declared horizon." *Why:* a 7–10 day horizon
against a 10–14 day voyage left a third of the departure plan undefined, and after a long comms
outage the tool went silent exactly when the master most needed it — an availability failure
dressed as a safety feature. The same tiering doubles as the **climatology-mode floor** for stale
packs, so one mechanism closes two holes. *Boundary we hold:* the floor must never be rendered like
the full product — no waypoint list, no fuel/time precision, no berg polygons — because a graceful
degradation indistinguishable from the real thing is worse than the refusal it replaced.

**ADR-023 — GPU ashore for training, CPU aboard for inference, nothing trained at the nodal
centre; weights ship by USB at port.** Primary compute: Kaggle Notebooks' free T4/P100 quota
(the 5-member ensemble needs ~8–12 GPU-hours, inside one week's allowance); backup Colab Pro;
paid fallback a spot T4/L4 at ~$5–10 for the whole budget. *Considered:* CPU-only training.
*Why not:* the arithmetic is ~85 h for the ensemble (`ML_ARCHITECTURE.md` §1.3), which permits one
run and no iteration — and iteration is where calibration gets fixed. CPU-only remains viable as a
one-shot final re-run, which is the honest answer to "what if there's no GPU in December": nothing
is trained in December. Inference is ~0.3–1 s on the stated minimum bridge spec (4-core x86-64,
8 GB RAM), which is what makes ADR-002's tier boundary hold. **Weights (~60 MB) and the frozen
calibration tables are never synced over Iridium** — port/USB only, versioned and signed like
packs; the mid-voyage response to a bad model is to fall back to the raw packed field, not to ship
new weights.

**ADR-024 — QC before fusion, one target grid, per-channel imputation, and an obs-only pack type.**
`ingest/` gains a mandatory QC pass (land-spillover masking, weather-filter false-ice detection,
range checks, missing-swath flags, preliminary-data tagging) emitting a `qc_flags` layer; all
sources are regridded to NSIDC 25 km polar stereographic with named interpolation (conservative
area-weighted for concentration, bilinear for forcing, nearest for masks) and a 1-cell halo
excluded from the disagreement statistic. *Considered:* leaving QC implicit and treating
"pack builds from remaining sources" as sufficient. *Why not:* without QC the D3 disagreement layer
cannot distinguish a sensor artifact from a genuine source conflict and would widen the route
around a phantom — which would discredit the differentiation it is meant to support; and
"builds from remaining sources" directly contradicted a model with fixed input channels. Every
imputed channel is flagged, and the flag **widens `SIC_upper`**, so degraded input makes the router
more cautious automatically. When the base field or the SIC observations are unavailable, the
system ships a declared `pack_type: obs_only` — real mesh, real bergs, real observed ice, zero
forecast leads — rather than failing or silently guessing.

**ADR-025 — Iceberg drift projection is capped at 72 h, with an area-fraction auto-downgrade.**
Exclusion radius = measured p90 leave-one-berg-out displacement error at 24/48/72 h; beyond 72 h
the layer shows last-observed USNIC positions with their date and draws no projection; polygons are
re-projected daily from each pack's fresh positions; and if hard exclusions cover >5 % of navigable
corridor area, the layer downgrades to a weighted cost term for that pack and says so.
*Considered:* projecting to the full 7-day forecast horizon for consistency with the SIC layer.
*Why not:* `GAP_ANALYSIS.md` §2 records physics-only ADE of **127–147 km**, so an honest 7-day
radius around every berg is either an ocean-wide blockade or a quietly shrunk buffer — the measured
chain from model error to caution is only admirable while the measured error stays navigationally
meaningful. The area-fraction rule exists because a horizon cap alone cannot guarantee that.
Also committed here: the **GBM→Wagner fallback trigger** is a frozen per-feature range check
(training min/max ± 10 % of range) plus a p99-of-training-residual correction cap, serialised with
the weights and unit-tested to fire — because an unspecified trigger silently never fires.

**ADR-026 — Depth margin is conditional on bathymetric provenance.** *(Corrected 2026-09-07: this ADR was written in the present tense and is DESIGNED, not built. Grep for GEBCO, bathymetry or TID across isih/ and models/ returns zero hits, every mesh cell reports null elevation, and the vessel's min_depth constraint is therefore inert — see isih/gates.py::chart_gate, which returns UNKNOWN and says so.)* The design is that GEBCO's TID grid be ingested
as a mesh layer; minimum under-keel clearance is 20 m in surveyed cells and max(50 m, 3 × draft) in
**predicted** (unsurveyed) cells, with a "predicted bathymetry" overlay in the UI. *Considered:*
treating GEBCO depth uniformly, as the router did. *Why:* much of the Antarctic corridor's GEBCO
bathymetry is altimetry-predicted rather than sounded — it is a model with large error, and the
router was consuming it as truth. The product also states plainly that it is decision support, not
a navigation system, and does not replace ENCs.

**ADR-027 — Raw packed CMEMS is a mandatory, build-blocking evaluation baseline, independent of
ADR-018.** For every lead, the corrected forecast must beat raw packed CMEMS on **both** IIEE and
CRPS in the corridor, on held-out *real forecast cycles*. A lead that fails is not claimed: the
pack ships the raw field labelled `uncorrected` and the declared skill horizon shortens. If no lead
passes, packed CMEMS becomes the routed field and the model is demoted to the §4 cross-check role.
*Considered:* benchmarking against damped anomaly persistence alone, as revision 1 did.
*Why:* `COMPETITIVE_ANALYSIS.md` §2 called CMEMS "the bar to beat" in our own words and revision 1
then quietly benchmarked something weaker — a direct internal contradiction a domain-literate judge
would find. This ADR stands even if ADR-018's gate fails, because a system that can pack CMEMS must
justify shipping anything else instead.
