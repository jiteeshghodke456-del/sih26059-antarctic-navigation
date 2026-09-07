# The research slide — evidence of depth, PS-26059

Purpose: this file assembles the specific, hard-won findings behind the deck's "justified
research slide" (master prompt §39/§40, item 10 — "a justified research slide demonstrating
hard work and depth of research into the problem statement"). Every item below cites the file
and section where it lives, so a judge's follow-up question can be answered by opening that
file, not by trusting the slide. Nothing here is invented for the deck; it is pulled from
research already on disk, dated when the primary source was actually read.

Deck note: this is a mining document, not the slide itself. Pick 5-6 of the starred (★) items
for a single slide — depth reads better as a few sharp, sourced facts than as a wall of them.

---

## 1. The strongest single piece of evidence: we reviewed our own architecture and it broke

This is the one item that proves depth by itself, before any domain fact is quoted, because it
shows the *process*, not just the output.

`docs/WEAKNESS_ANALYSIS.md` is a ten-section adversarial self-review of `docs/ML_ARCHITECTURE.md`
revision 1, written by the same team, against itself. It found three structural problems, not
cosmetic ones:

- **§9 — the training-data spec was chronologically impossible.** Revision 1 said "NSIDC/AMSR2
  SIC … 1979–2018." AMSR2 did not exist before mid-2012 (AMSR-E ran 2002–2011, then a gap to
  2012). The fix required picking a real product — the 25 km SSM/I-family CDR — and saying so
  (`docs/ML_ARCHITECTURE.md` §1.3).
- **§8 — the calibration method was "wishful on three counts."** A single global variance-inflation
  scalar cannot repair miscalibration that is worst exactly in the marginal ice zone at long
  lead times — precisely where the router consumes it — and a Gaussian 90th-percentile bound on
  a variable bounded in [0,1] can exceed 1.0. This forced a full replacement: **stratified
  split-conformal prediction, 30 strata (lead × regime), with a pre-committed numerical
  pass/fail rule** (`docs/ML_ARCHITECTURE.md` §1.6) — coverage must land between 85% and 96% on
  held-out MIZ cells at lead 5, or the uncertainty feature is **publicly demoted** in the pitch,
  a branch written down before the numbers exist "so it cannot be quietly renegotiated after
  them."
- **§2 — a direct contradiction inside our own documents.** `COMPETITIVE_ANALYSIS.md` §2 names
  CMEMS as the bar to beat; the original eval plan benchmarked only damped persistence. This is
  the finding that produced the model's entire pivot (§2 below).

`docs/ML_ARCHITECTURE.md` §7 then does something rarer than accepting a review: it **argues back
on three specific points**, on the record, rather than complying reflexively — e.g. conceding
that a 5-member seed-only ensemble under-disperses variance, while showing why conformal
calibration makes ensemble size a sharpness question, not a safety one, so growing it isn't the
free win the reviewer assumed.

★ **The line for the deck:** "We didn't just build a model. We red-teamed our own design
document, found it was training on data that didn't exist yet, and rebuilt the uncertainty
method from scratch with a numeric rule for when to stop trusting it."

---

## 2. The pivot: why the model corrects a forecast instead of replacing one

`docs/ML_ARCHITECTURE.md` §1.0, §1.8, §7.2. The original design trained a sea-ice model to
forecast SIC from scratch and argued "runs offline" as its edge over CMEMS. `WEAKNESS_ANALYSIS.md`
§2 pointed out the flaw: CMEMS's own 10-day forecast can simply be packed and shipped offline too,
so "runs offline" distinguished nothing.

The team's answer was not to abandon the differentiator but to **relocate it**: the model was
re-scoped to correct CMEMS's own forecast rather than compete with it (`docs/ML_ARCHITECTURE.md`
§1.1, "re-aim as a bias-correction / uncertainty-quantification head," ADR-018 in
`docs/DECISIONS.md`). This produces a claim that survives the objection: a packed CMEMS field is
**frozen at pack-build time**; the correction head takes fresh satellite observations as an input
channel and can **re-correct the whole 10-day packed forecast from an estimated 5–15 KB of new
observation, without re-downloading it** — an operation a static packed field cannot do at any
bandwidth (`docs/ML_ARCHITECTURE.md` §7.2). That 5–15 KB figure is explicitly flagged as an
**estimate, not measured** — `docs/backlog.md` carries it as a Phase-1 item to actually measure.

This is the finding behind the measured result: **the RMSE numbers in `docs/ISIH_RESULTS.md`
are the model beating CMEMS on CMEMS's own output**, not beating a strawman.

---

## 3. Regulatory research a shallow team would skip entirely

### 3.1 IMO POLARIS — read from the primary source, not a summary

`docs/NAVIGATION_RESEARCH.md` §1. **IMO MSC.1/Circ.1519**, the framework named on every Polar Ship
Certificate, was retrieved and parsed in full, not cited secondhand. Findings used directly in the
system:

- The Risk Index Outcome formula (`RIO = Σ Ci·RIVi`) and its decision thresholds — below −10,
  "subject to special consideration," which §1.5.3 says planning **should avoid**.
- Ice-class speed limits under elevated risk (PC1: 11 kn down to below-PC5: 3 kn).
- ★ **What POLARIS is provably blind to.** Read end to end, `MSC.1/Circ.1519` never contains the
  words *pressure*, *compression*, *ridge*, or *drift* — RIO is concentration × ice-type only
  (`docs/NAVIGATION_RESEARCH.md` §7.2). This is a real limitation of the international standard
  itself, not of our system, and it directly justifies why our own compression-risk work
  (§4 below) is white space rather than a solved problem we're reinventing.

### 3.2 MARPOL Annex I Reg. 43 — the heavy-fuel-oil ban, and why it matters to this vessel

`docs/backlog.md` line 130: **MARPOL Annex I Regulation 43 bans the carriage and use of heavy
fuel oil south of 60°S**, mandatory since 1 August 2011 (SAR/safety operations exempt). The whole
Cape Town → Bharati/Maitri corridor sits inside that line, so **MV Vasiliy Golovnin runs
MGO/MDO, not HFO, for the entire Antarctic leg** — a real regulatory constraint on the vessel our
fuel-routing objective is computing for. The research also distinguishes this from Reg. 43A (the
*Arctic* HFO ban, MEPC.329(76), in force 2022) — a distinction a team that skimmed one Wikipedia
page would conflate. **Status: researched and documented, not yet wired into the fuel model** —
disclosed here rather than implied as built.

### 3.3 Antarctic Treaty protected areas, modelled by legal regime — not as no-go blobs

`isih/protected_areas.py` (module docstring), added today. The master prompt (§48A.17) requires
determining whether a protected-area regime imposes a prohibition, a permit requirement, or an
operational condition — not treating every polygon the same. The research distinguishes the two
actual instruments under Annex V of the Antarctic Treaty's Environmental Protocol:

- **ASPA** (Art. 3) — entry is **prohibited except by permit**.
- **ASMA** (Art. 4) — entry needs **no permit**; activity must conform to a management plan. An
  operational condition, not a prohibition.

★ That distinction has a sharp, checkable consequence: **Bharati sits inside ASMA 6**. A system
that modelled ASMAs as no-go zones would refuse to route to India's own station. ASPA 174
Stornes is 1.9 km from Bharati; **ASPA 163 Dakshin Gangotri — India's own protected area** — is
4.7 km from Maitri, requiring a permit to enter, which India as the proponent already holds a
clear administrative path to.

The data-level finding matters as much as the legal one: **of 33 protected-area polygons
intersecting this corridor, zero are flagged marine** in the Antarctic Treaty Secretariat's own
dataset. So the honest conclusion, stated plainly in the code rather than glossed over, is that
**no ASPA or ASMA in this corridor restricts the ship's transit** — they restrict what happens
ashore, and (for ASPAs) require a permit to land at all. The module therefore models them as
station-operation constraints, not routing obstacles — because manufacturing a routing hazard
that the evidence doesn't support "would make the route look cleverer than the evidence
supports" (module docstring, verbatim reasoning).

---

## 4. Reading the router's own source code, not its documentation

`docs/NAVIGATION_RESEARCH.md` §2, PolarRoute/meshiphi v1.1.11 read directly at
`site-packages/polar_route/` and `site-packages/meshiphi/`.

★ **Gap 1 — `wave_resistance()` is dead code in all three vessel classes.** The method is
*defined* in `SDA.py:223`, `example_ship.py:222`, and `SDA_wind.py:243`, and a repo-wide grep
for its name returns only those three definitions — it is called from nowhere.
`model_resistance` sums wind resistance and ice resistance only. Waves therefore act **only as a
binary accessibility cutoff** (a cell becomes inaccessible above a max significant wave height);
there is no wave penalty on fuel or speed anywhere in the router. This matters because the
open-ocean Roaring Forties leg — where most of the voyage's fuel is actually burned — is modelled
by PolarRoute today with **zero sea-state fuel penalty**, which is exactly the "avoid severe
weather, minimise fuel" half of the problem statement. The research also caught a latent bug in
the dead code itself: it reads capitalised `"Beam"`/`"Length"` keys while `__init__` uses
lowercase — it would raise `KeyError` on first use if anyone ever wired it up as-is.

★ **Gap 2 — the router has no time dimension.** A repo-wide search for
`time_dependent|timestep|time_step|dynamic` across both packages returns nothing in the route
planner. The mesh's time bounds select and aggregate a slice; they do not produce per-timestep
layers. **The router assumes the environment is frozen for the entire 17.4-day computed voyage.**
The problem statement explicitly asks for routes that "dynamically recalculate ... based on the
daily or hourly movement of ice layers" — this is the exact gap that makes a forecast worth
having, because a static router has no notion of "the ice you will meet when you actually
arrive," and it is why time-expanded routing sits at the top of the roadmap
(`docs/TRUE_CLAIMS.md` §5, priority 1).

- Also found by reading the loader code, not assuming it: `gebco.py` exists as a bathymetry
  loader, but the GEBCO file was simply never downloaded for this run, so **the computed route
  currently has no depth constraint at all** — a mesh reported "no elevation data" for every
  cell.
- On the positive side, the same reading found real reusable capability worth keeping rather
  than rebuilding: a genuine 8-heading apparent-wind resistance model against ERA5 winds, and a
  Newton-method route-smoothing pass (Snell's-law-style refraction at cell boundaries) that turns
  a kinked Dijkstra path into something a master would actually sail.

---

## 5. Why the data layer itself is the weak point every ice service shares — quantified

`docs/NAVIGATION_RESEARCH.md` §6, researched against the primary algorithm-comparison literature,
not asserted from general knowledge. This is the evidence base for a claim a shallow team would
either not know or would state as an unsupported slogan ("existing tools are inaccurate").

- ★ **Algorithms disagree with each other by roughly 10× more at the ice edge than in thick
  pack.** A 30-algorithm round robin (Ivanova et al. 2015) reports standard deviations at 15%
  concentration ranging from 2.8% (best) to 28.8% (worst) in the Northern Hemisphere, and the
  Southern Hemisphere is worse still (35.0% for one algorithm). At 75% concentration the spread
  collapses to 2.9–9.0%. The deck line this licenses, stated carefully: "There is no such thing
  as *the* sea-ice concentration at the ice edge."
- **Shipped uncertainty is admitted to be incomplete, by the producers themselves.** OSI SAF ships
  per-pixel algorithm and smearing uncertainty; smearing uncertainty reaches 40% SIC at the ice
  edge. Lavergne et al. 2019 states explicitly that melt-pond misinterpretation, the thin-ice
  effect, and the open-water-filter effect are **not included** in those shipped numbers — what
  ships is a precision estimate, not a total error budget.
- **This connects directly to our own measured coastal-data finding**, not just literature: the
  coastal-contamination correction that fixes false coastal ice can overshoot and remove true
  ice, and our own audit (`isih/ice_quality.py`, `docs/ISIH_RESULTS.md` §2) found the NOAA/NSIDC
  CDR's land-spillover filter zeroing coastal cells to a value that reads as open water — on
  **100% of days**, ~118 cells/day, affecting 43.2% of days in the 200 km approach to Bharati
  specifically. Masking those cells moves the true coastal-ice picture **up** (46.8% → 54.6%
  mean concentration), i.e. the fix makes the router *more cautious*, not less — the opposite
  direction a team cutting corners would guess.
- **Half of published Antarctic seasonal forecasts don't beat climatology.** SIPN South
  (Massonnet et al. 2023), 22 contributors, >3,000 forecasts: only 51% beat a plain climatological
  forecast on CRPS. The authors state they did **not** implement a persistence benchmark at all,
  calling it "not always straightforward" — which is the exact benchmark our own result is
  measured against (`docs/ISIH_RESULTS.md`). That is a genuine methodological edge over the
  published state of the art, not a marketing line.
- **Manual ice charting is not ground truth either.** Cheng et al. 2020: trained analysts
  reading the same RADARSAT-2 imagery matched automated segmentation exactly only 39% of the
  time, and inter-analyst agreement was Krippendorff's α = 0.779 — experts disagree with each
  other materially. This is the argument for calibrated intervals over a single confident number,
  which is the system's own differentiator (D1 in `docs/ML_ARCHITECTURE.md`).

*Caveat carried forward, not dropped for punch:* the Antarctic-specific thin-ice error magnitude
(Stentella et al. 2026) has conflicting figures between the journal page and the preprint summary
(up to 70% vs up to 30%) — flagged in the source as needing verification against the published
figure before it is quoted with a number on a slide.

---

## 6. Physical hazards the 25 km satellite field cannot see at all

`docs/NAVIGATION_RESEARCH.md` §7. This section exists because the problem statement asks for
*safe* routing, and a concentration map alone cannot deliver that — the research names precisely
what closes on a ship that a concentration field cannot show.

- ★ **Ice compression ("sandwiching") is a genuine global white space, and POLARIS is blind to
  it.** No operational Antarctic ice-pressure product exists anywhere — AARI forecasts it only
  for the Barents/Kara Seas; Canada's CAPS is Arctic-only. The physical driver (AARI,
  Buzin/Klyachkin/Frolov 2022) is a computable geometric test: onshore wind component ×
  concentration × distance to a blocking boundary, and their own normative finding is that
  *"the most dangerous case for shipping is compression at the fast-ice edge when the general
  drift sets into it at an angle"* — **which is exactly the Bharati and Maitri offloading
  geometry**, a ship sitting at the fast-ice edge.
- ★ **The uncertainty-amplification finding.** Hibler (1979) ice strength is exponential in
  concentration (`P = P*·h·exp[−C(1−A)]`, C = 20), so `dP/P = 20·dA`: **a 5-percentage-point SIC
  error changes modelled ice strength by 2.7×; a 10-point error by 7.4×.** Any compression layer
  built on a 25 km passive-microwave field inherits that amplification — the strongest available
  argument for shipping uncertainty with any compression number, not a bare figure.
- ★ **A directly relevant Indian-programme incident.** The **MV Magdalena Oldendorff**, chartered
  as the support ship for the **20th Indian Antarctic Expedition**, was beset near Novolazarevskaya
  on 11 June 2002 and was not freed by another icebreaker — she self-released roughly 5.5 months
  later. She is the same ice class (ULA-class) as Golovnin. *Flagged in the source itself: dates
  conflict across sources and no primary ATCM/COMNAP document was located — verify before
  presenting as fact rather than as a researched lead.* No besetting incident could be documented
  for any Indian-flagged vessel specifically (Sagar Kanya, Ivan Papanin, Golovnin) — recorded as
  an evidence gap, not a null result.
- **The growler gap, stated as a number, not a hand-wave.** A growler is <1 m above water, <5 m
  long, glacier ice that doesn't fail in bending the way sea ice does. The smallest object USNIC
  operationally tracks is ~18.5 km. **That is a 3.5-order-of-magnitude gap** between the smallest
  tracked hazard and the classic hull-holing one — best-case Sentinel-1 detection of the smallest
  bergs it can see at all (<60 m) is only 5–13%. This is why the product explicitly never implies
  a growler warning; that stays radar-and-lookout territory (`docs/TRUE_CLAIMS.md` §4).
- **Summer blizzards, quantified from Indian station data.** At Maitri (*Mausam*, 1990–2005 data):
  ~21 blizzards/year, mean wind 52 kt during a blizzard, mean duration 25 h (longest 168 h, June
  1997). The source states blizzard frequency is highest in winter, lowest in summer; the
  Dec–Mar resupply window plausibly sees 0–2 blizzards per season — a figure the research
  explicitly labels **derived, not directly stated in the source**. A single 25-hour event at
  52 kt moves the ice field roughly 30 km, which is the operational point: rare is not absent.
- **ERA5 under-forecasts exactly the winds that beset ships**: it correlates well with observed
  Antarctic coastal winds generally (r = 0.91) but has a mean bias of −3.89 m/s above 20 m/s,
  worst near complex orography — any wind-driven hazard layer built on it must bias-correct or
  disclose that it hasn't.

---

## 7. Indian versus foreign data sources — evaluated, not assumed (§29)

`docs/DATASET.md`, every entry checked live from the sandbox on 2026-08-31, both via web fetch
and direct `curl`, so "verified live" means bytes actually returned, not a reachable landing page.

**Indian sources evaluated directly:**

- **NCPOR's National Polar Data Centre** (`npdc.ncpor.res.in`) — confirmed live (HTTP 200), a
  real Struts-based catalog with genuine functionality: dataset search by location, by science
  keyword, raw-data search, a data-policy page. **Honest verdict, stated plainly rather than
  inflated**: this is India's own polar-data catalog, real and not vaporware, but it is
  metadata/station-scale (Automatic Weather Station data from Maitri/Bharati), not global
  satellite-grid data — so its role is **local ground-truth and validation near the Indian
  stations**, not a primary input feed for the ML models. `docs/DATASET.md` §7 recommends a
  follow-up pass to explore the search endpoint interactively, since it likely needs a browser
  session rather than a REST call — logged as unresolved, not glossed over.
- **`synopticdata.ncpor.res.in`** ("Synoptic-Bharati") — confirmed live meteorological
  observations directly from Bharati station.
- **`las.ncaor.gov.in`**, a Ferret-based Live Access Server, suggesting NCPOR also serves some
  gridded oceanographic products, not checked in depth this pass.

**Where a foreign source was retained, and why — stated objectively, not nationalistically:**
every primary satellite/reanalysis input this system uses (NOAA/NSIDC sea-ice CDR, Copernicus
CMEMS ocean forecast/reanalysis, ECMWF ERA5, NOAA GFS, USNIC/BYU iceberg tracks, GEBCO
bathymetry) was retained because **no Indian equivalent global product exists at the required
resolution, cadence, or Antarctic-wide coverage** — NCPOR's own portals are explicitly
station-scale, not a competing global product this system passed over. That is the honest
finding: this is not a case of choosing a foreign source over an available Indian one, it is a
case where the Indian source fills a role (ground-truth validation near India's own stations)
that the foreign sources cannot, and vice versa. The deck should say exactly that, not overstate
either direction.

**The one real, disclosed data gap** (`docs/DATASET.md` §6.2): no dedicated "Antarctic ice-affected
shipping lane" dataset exists from IHO or any body, Indian or foreign — Antarctic ENC coverage
is licensed/paywalled and notoriously sparse because the seafloor there is mostly
GEBCO-*predicted*, not ship-sounded, bathymetry. This is not a sourcing failure; it is
confirmation that safe-route computation is the actual product this platform builds, not an
input it should expect to find pre-made.

---

## 8. The competitive landscape — read the code and the papers, not the pitch decks

`docs/COMPETITIVE_ANALYSIS.md`.

- ★ **The FloatChat pattern, named as a predictable failure mode before it could be repeated.**
  Four independently-built public implementations of last year's sibling MoES problem statement
  (FloatChat, ARGO ocean data) were found on GitHub, and all four converge on the identical
  shape: a chatbot/RAG wrapper over real data, with "AI" meaning retrieval and NL-to-SQL
  translation, not a trained predictive model. This is direct, checkable evidence of what
  "obvious architecture" convergence looks like for an MoES data-access PS, and it is exactly
  why `docs/DECISIONS.md` ADR-015 explicitly rejects an LLM/RAG layer as the visible "AI" for
  this system — a decision made *because* the failure mode was documented, not by instinct.
- **IceNet is validated for the Arctic, not the Antarctic, and the paper title says so.** The
  Nature Communications 2021 IceNet paper is titled "Seasonal *Arctic* sea ice forecasting"; a
  team that fine-tunes IceNet weights for Antarctica is extrapolating a model outside its
  validated domain. A genuinely Antarctic-specific reference architecture exists
  (**ANTSIC-UNet**, The Cryosphere 2025) and is cited as the credible comparison point instead.
- **IDRIFTNET (2025) is the field's current state of the art for iceberg drift, and it's
  hybrid, not black-box.** Tested specifically on the giant tabular bergs A23a and B22a: physics
  drift equations plus a learned residual correction, because pure statistical and pure physics
  approaches both underperform alone. This is the architectural pattern this system's iceberg
  module deliberately follows (Wagner physics baseline + gradient-boosted residual), with the
  reasoning for *not* copying IDRIFTNET's neural residual recorded explicitly
  (`docs/ML_ARCHITECTURE.md` §2.3): the correction problem is small-data and tabular, which is
  gradient boosting's regime, not a neural network's, and a boosted-tree correction is
  interpretable enough to show it rediscovers real physics (wind dominating small bergs,
  currents dominating large ones) — which is a stronger judging story than a black box that
  merely scores well.
- **A 2025 Alaska paper is the closest published precedent to our fusion argument**: it found
  Copernicus systematically underestimates ice concentration versus regional ice charts, worst
  near the coast/MIZ, and that ~36% of AIS observations in ice-affected waters corresponded to
  elevated-risk POLARIS outcomes — direct published evidence that single-source ice data is not
  authoritative, which is the finding this system's multi-source disagreement layer
  (`docs/ML_ARCHITECTURE.md` §4) is built to answer rather than assert on its own authority.
- **The market incumbent keeps a human in the loop by design, not as a limitation.** StormGeo
  (s-Routing/s-Planner), the real commercial voyage-optimization leader with ice conditions as an
  explicit routing input, still runs 24/7 human route analysts as a fallback layer. That is
  evidence for this system's own honest-fallback design (§9 in `docs/COMPETITIVE_ANALYSIS.md`),
  not a competitor weakness to attack.
- **Southern Ocean traffic is genuinely small**, which reframes what "solving Antarctic
  navigation" should even mean here: 255 unique vessels across the *entire* Southern Ocean,
  2014–2018, with 88% of visits in the Antarctic Peninsula/South Shetlands (Leihy et al., PNAS
  119(3), 2022) — the Indian Ocean sector this project routes through is in the remaining 12%.
  There is no off-the-shelf Antarctic vessel-density product, so any traffic layer would have to
  be built from raw satellite AIS (`docs/backlog.md`). **This is a researched finding, not yet
  built into the system** — it is the evidence behind the deliberate, disclosed decision to
  *not* claim to solve Southern Ocean traffic management (`docs/TRUE_CLAIMS.md` §4), only fleet
  coordination for the Indian programme specifically.

---

## 9. A question the team asked itself before a judge could

`docs/ISIH_RESULTS.md` §"Known caveats." The headline result (the model beats persistence by
18.5%–30.6% across 1–7 day leads) is trained against a **reanalysis** background (GLORYS12), not
a live operational forecast. The team wrote out the exact question a technically literate judge
would ask — *"your background already saw the observations you are predicting; isn't that
leakage?"* — before being asked it, and gave the honest partial answer available today: GLORYS12's
own RMSE (0.163) is far from zero and worse than persistence at every horizon, so it is not simply
handing over the answer, but it may still carry some future signal the model exploits. **The
ablation that would settle this cleanly (retrain with the background channel zeroed) is specified
in the document and explicitly marked as not yet run** — this is disclosed as an open question,
not glossed over as answered, and production is scoped to correct a real CMEMS forecast where the
question cannot arise at all.

---

## Sources worth naming on the slide itself

A judge can verify any of the above by asking to see, in order of how quickly they resolve a
challenge: `docs/ML_ARCHITECTURE.md` (the pivot and the calibration rebuild), `docs/
WEAKNESS_ANALYSIS.md` (the self-review that forced it), `docs/NAVIGATION_RESEARCH.md`
(POLARIS, PolarRoute source-reading, the data-quality and hazard literature),
`docs/COMPETITIVE_ANALYSIS.md` (the field survey), `docs/DATASET.md` (the source-by-source
audit), `isih/protected_areas.py` (the ASPA/ASMA legal-regime module), and `docs/ISIH_RESULTS.md`
(the trained model's actual numbers and its own leakage question).

---

## ROADMAP — futuristic scopes named in the master prompt (§14, §21, §24, §25, §26)

None of the following exists in the codebase today. They are presented here, clearly labelled
future work, because the master prompt asks for a credible forward arc and because Tier-3
features must never be described as built when they are not — the master prompt is explicit that
Tier-3 must not displace the core, and this project's whole positioning depends on that
discipline holding on this slide as much as anywhere else.

- **§26 — a locally run LLM for natural interaction.** `docs/DECISIONS.md` ADR-015 deliberately
  excludes an LLM/RAG layer from this system **today**, and the reasoning matters here: ADR-015
  rejects an LLM as a *replacement* for the trained prediction and routing components — the exact
  FloatChat failure mode documented in §8 above, where four competing teams put a chatbot in
  place of a real model. A future natural-language layer that lets a bridge officer ask "what's
  the ice like near Bharati this week" and get an answer **sourced from the existing trained
  model's output**, running locally so it needs no connectivity offshore, does not touch that
  decision — it sits on top of the pipeline, not instead of it. This is a bounded addition, not
  a reversal of ADR-015.
- **§25 — "Baymax Mode": passive captain health monitoring via a wearable.** Named as a
  Tier-3 scope in the master prompt. The two-tier architecture already in place
  (`docs/DECISIONS.md` ADR-002, ADR-003 — shore/vessel sync boundary, `MODE=shore|vessel`) is the
  natural place a wearable-data stream would attach as one more synced input, but no wearable
  integration, health model, or data source has been evaluated. Flagged as unresearched, not
  merely unbuilt.
- **§24 — emergency/SOS notification to the nearest icebreaker and station.** This has real
  research to build on that this project has already done for other reasons: the USNIC/BYU
  iceberg feeds and the Southern Ocean traffic finding (§8 above, Leihy et al. 2022) establish
  that vessel density in this sector is genuinely low and mostly undocumented as a live product,
  so "nearest icebreaker" would need to be built from raw AIS, which is exactly the same
  data-sourcing gap already logged in `docs/backlog.md` for the traffic-layer idea. Any SOS
  routing logic inherits that same open dependency.
- **§14 — onboard sensor integration.** The `MODE=vessel` runtime tier is where this would live
  architecturally, but no sensor protocol, hardware, or data contract has been scoped. The
  besetting and compression research (§6 above) already identifies what such sensors would need
  to detect that satellites cannot — ice pressure, local wind-direction change — so the research
  exists to justify *why* onboard sensing would matter; the integration itself does not.
  Recorded here so the roadmap item is at least grounded in a real gap, not a generic feature.
- **§21 — learning from historical incidents.** The besetting case studies already assembled in
  research (`docs/NAVIGATION_RESEARCH.md` §7.3 — Magdalena Oldendorff, Akademik Shokalskiy,
  the 1922–1990 Northern Sea Route besetting statistics) are exactly the kind of incident record
  such a system would need to learn from, and they demonstrate the *research* for this scope
  already exists even though no incident database or learning component has been built. The
  honest gap, stated in the source itself: **no besetting incident could be documented for any
  Indian-flagged vessel** (Sagar Kanya, Ivan Papanin, Golovnin) — a real evidence gap that an
  NCPOR expedition-report review would need to close before this scope could even start.

**What the architecture already leaves room for, stated precisely:** the two-tier
shore/vessel split and the offline-pack design (ADR-002, ADR-003, ADR-016, ADR-017) mean any of
the above that needs to reach the vessel would arrive the same way the ice and route packs
already do — synced, budgeted, and bandwidth-honest — rather than assuming a live connection
these scopes would otherwise silently require. That is a real, load-bearing architectural
property already built and tested (`docs/DECISIONS.md` ADR-017 — a route pack compresses to
796 B, an environmental mesh to 72 KB, enforced by a CI budget test); it is not a claim that any
of the five scopes above is designed, only that none of them would break the pattern the system
already follows.
