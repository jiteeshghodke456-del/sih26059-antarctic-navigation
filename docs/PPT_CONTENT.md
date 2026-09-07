# PPT Content — SIH 2026, PS-26059

**AI-enabled Antarctic sea-ice forecasting, iceberg trajectory prediction, and
safe / fuel-efficient route identification.**
Ministry of Earth Sciences / NCPOR. Corridor: Cape Town → Bharati / Maitri.
Vessel: MV *Vasiliy Golovnin* (IMO 8723426), the hull NCPOR actually charters.

Written 2026-09-07. Every number below was checked against the file that produces
it before it was written down. Where something is designed but not running, the
sentence says **ROADMAP**. Where something is a longer-term idea, it says
**FUTURE**. Nothing in this document blurs the two.

---

## What this is, and why it matters

Once a year, one chartered ship carries a year of supplies from Cape Town to
India's Antarctic stations. There is no second sailing, the charter is paid by
the day, and the cargo is craned onto sea ice rather than onto a quay. We built a
decision-support system for that voyage: it corrects the sea-ice forecast with a
trained model, carries the published iceberg-drift physics — tested, not yet
moving real bergs forward — plans the route with the polar research community's
own open-source router, and answers the one question
the existing tools do not — **will the destination actually be open on the day
the ship arrives?** We measured it for December 2019 and the answer was no, on 23
days out of 31.

---

## WHAT IS REAL TODAY

> This box is the point of the whole document. Everything in it runs right now
> and can be shown in front of a judge in under a minute.

| Runs today | The number | Where it lives |
|---|---|---|
| **Trained sea-ice correction model** beats persistence at every horizon | **+18.5 %** (1 day), **+24.9 %** (3), **+22.1 %** (5), **+30.6 %** (7). Test slice is the last 15 % of 2019–2020, which falls in the melt season — the season the ship sails. **Read as an upper bound on forecast skill, not a measurement of it**: the background was a reanalysis (see below) | `docs/ISIH_RESULTS.md` |
| Three-way temporal split, test set scored **exactly once**, baselines fixed before training | RMSE 0.0465 / 0.0720 / 0.0938 / 0.0968 vs persistence 0.0570 / 0.0958 / 0.1204 / 0.1395 | same |
| **Destination-window result** — the finding that reframes the problem | Bharati closed **23 of 31** December 2019 days; the approach 100 km north open **31 of 31**. No Maitri number yet — see below | `isih/figures/destination_window.json` |
| **A bug found in the standard satellite product**, and fixed | Land-spillover filter writes suppressed coastal pixels as **0.0 % ice** on **100 % of days**, ~118 cells/day; **43.2 %** of days in the 200 km Bharati box | `isih/figures/ice_quality_audit.json` |
| The fix moves risk **the safe way** | Coastal mean ice **46.8 % → 54.6 %** — the router becomes *more* cautious | `docs/ISIH_RESULTS.md` §2 |
| **Real route on real satellite ice**, real open-source router | **8.6 days** steaming, Cape Town → Bharati. Sampled on the 25 km satellite grid, the route peaks at **79 %** ice and never crosses the vessel's 80 % limit (the router's own coarser mesh reports a 54 % maximum on the same track). For illustration only: a straight line hits **92 %** and breaches the limit at 55 sampled points — that line is not a baseline, no master sails it; the honest baseline is the same router on older ice, §16 | `isih/figures/routes.json`, PolarRoute 1.1.11 |
| **Iceberg drift equations, published physics, tested** | Wagner–Dell–Eisenman (2017) closed form reproduces the paper's coefficient table and its 765 m critical length, **23/23 tests pass**. The real USNIC catalogue is read — **33 bergs, 15 within a 10°W–100°E band spanning the corridor**, largest D15A at **3,037 km²** — and each berg is classified wind- or current-dominated under a declared wind/current sweep. **No berg has been moved forward in time yet, and no error against an observed track has been measured** — see below | `models/iceberg/test_drift.py`, `regime_report.json` |
| **Protected areas modelled by legal regime** | **33** corridor polygons, **zero marine**; Bharati sits inside **ASMA 6**, which India co-proposed | `isih/protected_areas.py` |
| **Working demo**, real data end to end | FastAPI + canvas, boots in under 4 seconds, **refuses to start** if any day's satellite file is missing | `isih/demo/app.py` |
| **Test suite** | **55 tests pass** — 24 demo, 23 iceberg drift, 8 protected areas | run today |
| **Daily forecast harvest on GitHub Actions** | **13 runs. The first, a manual run on 31 Aug, failed at the Copernicus login step and stopped there; the 12 since are green. 7 consecutive days archived** (31 Aug – 6 Sep 2026) | `.github/workflows/cmems-harvest.yml` |
| **Real data only** | **1,096** real daily NOAA/NSIDC satellite files, **zero failures**. No synthetic data anywhere in the product. | `docs/ISIH_RESULTS.md` |

### And what is NOT real today — said here, not buried

- **The trained model's background is a reanalysis, not a live forecast.**
  GLORYS12 absorbs satellite observations near the date it describes, so part
  of the +18.5 % to +30.6 % may be the answer leaking in. We used to defend this
  by saying raw GLORYS12 scores 0.163, worse than persistence; that defence is
  withdrawn — 0.163 is grid and ice-model mismatch, and a field can score badly
  and still carry the target. So the figures are **an upper bound on forecast
  skill, not a measurement of it**. The no-background ablation that settles it
  is written and not yet run. **ROADMAP, top of the list.**
- **No Maitri closure number.** Maitri is inland in the Schirmacher Oasis and
  is resupplied across the ice shelf from an offload point we have not sourced,
  so `destination_window.py` deliberately does not score it. An earlier run
  scored a "Leningradskaya coast" point that fell outside the routing mesh and
  returned no data on all 31 days; the script counted no-data as closed and
  produced a "31 of 31 closed" that is not a measurement. **That number is
  withdrawn and must not appear on a slide.** Nothing else in this document
  quotes it.
- **No iceberg has been drifted anywhere yet.** The drift equations are
  implemented and tested against their paper. What has been run on the real
  catalogue is a regime check — is each berg wind- or current-dominated — under
  a declared sweep of assumed winds and currents, because we do not have wind or
  current at the bergs' positions and did not invent them. Stepping a berg
  forward needs an ocean-current field; scoring it needs the observed-track
  archive. Neither is wired in. **No trajectory error has been measured.
  ROADMAP.**
- **No calibrated uncertainty layer.** One model per horizon, no ensemble, no
  conformal bound. Today this is PolarRoute plus a corrected forecast. **ROADMAP.**
- **No multi-source disagreement mechanism.** The research is real; there is no
  code. **ROADMAP.**
- **The offline tier is designed, not built.** Pack signing, delta sync, the
  `MODE=shore|vessel` switch and the climatology floor are specified with real
  measured numbers. What runs today is a single-tier local demo. **ROADMAP.**
- **No bathymetry.** GEBCO is not downloaded, so depth constrains nothing in the
  8.6-day route. **ROADMAP.**
- **No login screen**, although the deployment concept describes one. It is not
  designed anywhere in this repository. **GAP.**
- **We beat persistence and we beat raw GLORYS12 reanalysis. We have not yet
  beaten CMEMS's own operational forecast** — the archive that comparison needs
  has seven days in it.

---

## 1. Two extremely strong USPs

### USP 1 — We answer "can I get in?", not "here is the ice"

> **For the approach to Bharati in December 2019, the station cell was closed to
> this ship on 23 of 31 days — while the water 100 km further north was open
> every single day.**

- **Measured, not asserted.** `isih/figures/destination_window.json`, computed
  from real NOAA/NSIDC satellite ice against this vessel's real capability.
- **It reframes the problem.** The ocean crossing was never the difficulty. About
  5,800 km of the 5,813 km route carries a mean of 6 % ice. The whole decision is
  compressed into the last 100 km.
- **It matches how Indian resupply actually works** — the ship holds at the
  fast-ice edge and moves cargo the rest of the way by helicopter and barge. That
  is why *Golovnin* carries both.
- **It is hard to copy this season.** Getting this number right required auditing
  three years of satellite data and finding that the record reports suppressed
  coastal pixels as open water. Four of the eight days Bharati looked reachable
  were that artifact. A team that skips the audit publishes a wrong, more
  optimistic closure number and does not know it.
- **Every existing product answers a different question.** CMEMS, USNIC, IceNet,
  Polar View and IcySea all publish ice state. None of them, on our search,
  publishes a ship-specific, date-resolved answer for a named destination.

**Say the limit out loud:** one December, one ship's ice limit, three years of
data behind it. It is a measurement, not a climatological law.

### USP 2 — Protected areas modelled by the law that applies, not by fear

> **Of 33 Antarctic Treaty protected-area polygons in this corridor, none are
> marine — so none restricts the ship's transit. The system still tells the
> master that Bharati sits inside a managed area India itself co-proposed, and
> that India's own protected area is 4.7 km from Maitri.**

- **Shipped today.** `isih/protected_areas.py`, built from the Antarctic Treaty
  Secretariat's own 2024 shapefile: 148 polygons, coordinate system read from the
  `.prj` rather than assumed.
- **The legal distinction is the feature.** An **ASPA** (Annex V, Art. 3) may not
  be entered without a permit. An **ASMA** (Art. 4) needs no permit — activity
  follows a management plan. They are coded as different constraint types.
- **The easy version would be wrong.** Draw all the polygons as no-go and the
  system refuses to route to India's own station, because Bharati is inside ASMA 6
  (Larsemann Hills). ASPA 174 Stornes is 1.9 km away. ASPA 163 Dakshin Gangotri —
  India's own designation — is 4.7 km from Maitri.
- **The finding is checkable and it is the honest one:** these areas bind what
  happens ashore — landing, small boats, helicopters, people — not the sailed
  track.

**Say the limit out loud:** because nothing here is marine, this feature changes
zero routes this season. Its value is correctness and trust. Elsewhere in
Antarctica there are eight marine protected areas — the Ross Sea has some — and
the code path for that case is tested on those eight real polygons. But no route
has ever been planned around one.

---

## 2. Three basic USPs

**1. The model beats the baseline that matters, under rules that make the number
hard to inflate.**
+18.5 % to +30.6 % over persistence across 1–7 days. The margin *grows* with lead
time — our error rises 2.1× from day 1 to day 7, persistence rises 2.5×. The
further ahead the ship must plan, the more the model is worth. The split is
three-way and temporal, never random; the test set was scored once; the baselines
were computed before training started. **One honest scoping, said before a judge
says it:** the background the model corrects is a reanalysis, which has seen
observations near the target date — and a leaked answer produces exactly a
"margin grows with lead time" pattern. So we quote these figures as an upper
bound on forecast skill until the no-background ablation is run. For context on
the state of the field, a 22-contributor Antarctic *seasonal* forecast comparison
(SIPN South, 2023 — months ahead, a different horizon from ours) found only 51 %
of forecasts beat plain climatology, and did not run a persistence benchmark at
all.

**2. We found a bug in the satellite record everybody uses — and the fix makes us
more cautious, not less.**
The NOAA/NSIDC record's land-spillover filter suppresses coastal pixels and
writes them as `0.0`, which any unguarded reader accepts as open water. It fires
on 100 % of days, ~118 cells per day, and touches 43.2 % of days in the 200 km box
around Bharati. Masking those cells moves the coastal ice reading **up**, 46.8 %
to 54.6 %. Corrections that make your own system look worse are the ones a judge
believes.

**3. Iceberg drift is published physics, reproduced and tested — and we say
exactly how far it has been run.**
Wagner, Dell & Eisenman (2017), reproducing the paper's own coefficient table and
its 765 m critical length. 23 tests, 23 pass. Pointed at the real USNIC catalogue
— 33 tracked bergs, 15 within a 10°W–100°E band spanning the corridor, including
one of 3,037 km² beside Bharati's approach. What that run measured is regime, not
position: under a typical 10 m/s wind 20 of 33 bergs move with the current; under
a 30 m/s katabatic with a weak current 28 of 33 flip to wind-driven — so both
terms stay in the equation. No berg has been stepped forward in time yet (that
needs an ocean-current field), and no drift error has been measured against an
observed track. The blind spot is stated in the product, not hidden: a growler
is about 5 m; the smallest berg tracked in the Antarctic is about 18.5 km. That
gap is three and a half orders of magnitude and nothing in orbit closes it.

---

## 3. What this is, in plain language

**The situation.**
India runs research stations in Antarctica. Once a year, one ship leaves Cape
Town carrying a year of food, fuel, equipment and people. There is no second
sailing. The ship is hired by the day. When it arrives, there is no port — the
cargo is lifted onto the fast ice — sea ice frozen to the shore — or flown in by
helicopter, or carried in on a barge.

**The problem.**
Sea ice moves. It closes a coast in a day and opens it a week later. If the ship
arrives when the ice is shut, it waits — and every waiting day is a day of hire
spent on nothing. If it waits too long, cargo does not land at all. This has
happened to comparable programmes: at Australia's Mawson station in 2021, thick
ice stopped a full resupply and eighteen people went short for months.

**What we built.**
Four things, in a chain:

1. **A model that corrects the ice forecast.** We do not forecast ice from
   scratch. We take an existing forecast and train a model to fix its mistakes,
   using what the satellite actually saw over the last seven days. Correcting is
   a smaller, more honest job than replacing, and we can measure whether we did it.
2. **The equations for how an iceberg drifts.** Published physics — wind,
   current, Coriolis — reproduced from the paper and unit-tested, and pointed at
   the real list of tracked bergs. It does not yet move a berg forward in time:
   that needs an ocean-current field we have not wired in.
3. **A router that plans the voyage.** We use the British Antarctic Survey's own
   open-source polar router rather than writing our own. It plans a real route
   over real observed ice.
4. **An answer, not a picture.** For each day, for this ship, at this station:
   open or closed.

**What it looks like on a bridge.** A laptop. No internet needed. A map of the
ice, a route, a plain answer about the destination, and a clock showing how old
the data is. If a day of satellite data is missing, the software refuses to
start rather than draw a gap as open water.

**What it does not do.** It does not steer the ship. It does not see the small
ice that actually holes a hull. It does not replace the master's judgement — it
puts evidence in front of it.

**Three sentences for a slide:**

> Antarctic resupply is a supply chain with one ship, one window and no second
> attempt.
> We measured the delivery point: Bharati was shut 23 days out of 31, while the
> water 100 km out was open every single day — so the crossing was never the
> problem.
> We tell the ship which day it can get in, and what it costs to be wrong.

---

## 4. Implementation roadmap

Nothing on this roadmap needs a research breakthrough. Every open item is a data
download, a configuration wire-up, or engineering with a known shape.

| Phase | What it delivers | Status today | What gates the next step |
|---|---|---|---|
| **0 — Spine** | Repo, FastAPI + web shell, daily forecast harvest | **DONE.** Harvest: 12 green runs after a day-one credentials failure that stopped at the login step; 7 days archived; fails loud on a bad bulletin instead of archiving the wrong day. | Nothing. It keeps running underneath every later phase. |
| **1 — Real routing on real data** | Satellite ice + bathymetry ingestion, quality pass, a real route from a real router | **MOSTLY DONE.** 1,096 real daily files ingested, zero failures; the coastal-artifact bug found and fixed here; PolarRoute computes a real 8.6-day route. **GEBCO bathymetry is not downloaded**, so depth constrains nothing. | GEBCO is a free download and a config change — the smallest item left. |
| **2 — The trained model** | A model that beats the operational baseline, scored honestly, once | **PROTOTYPE DONE.** +18.5 % to +30.6 % over persistence. Single model per horizon, 12 of 19 planned channels, ~2 years of training data, corridor only. The production version — 5-member ensemble, conformal calibration, full history, all channels — is **ROADMAP**. | GPU time and more downloaded years. Then the calibration gate has to be run. |
| **3 — Uncertainty and hazards** | Calibrated bound driving the route, iceberg exclusion, protected areas | **PARTLY DONE.** Iceberg physics is implemented and tested. Protected areas are modelled by legal regime and shipping today. **Not done:** no berg is stepped forward in time yet (needs a CMEMS current field), no drift error is measured against the observed-track archive, the berg polygons are not wired into the router's `excluded_zones` hook, and the uncertainty layer does not exist because it needs the Phase-2 ensemble first. **ROADMAP.** | The Phase-2 ensemble. Uncertainty has nothing to calibrate against without it. |
| **4 — Offline tier** | Signed versioned packs, shore/vessel mode split, staleness banner, climatology floor | **DESIGNED, NOT BUILT.** What exists is a single-tier local demo that makes no live calls and refuses to render missing data. The pack machinery is specified in `docs/ARCHITECTURE.md` §2 with real measured numbers (a representative mesh block compresses to 76 KB) — as a specification. **ROADMAP.** | Nothing external. This is the next thing to build, and it is the most fully worked-out design in the project. |

**Cut first if the schedule slips:** the gradient-boosted iceberg residual, NCPOR
validation data, a Sentinel-1 ice-edge figure, POLARIS-compliant thickness
output. None of these carry the pitch. The trained model and the offline
architecture do.

**The single highest-value experiment still unrun:** the multi-date route-regret
sweep — plan on day 0 under each ice input, then replay the voyage through the
ice that actually occurred. It converts "18–31 % lower forecast error" into days
and tonnes. It is built. It can come out against us; on the one date tested so
far, it did.

---

## 5. Futuristic scopes

All **FUTURE**. None of the following exists in the codebase. They are listed
with what actually grounds them, because a forward arc built on nothing is worth
nothing.

- **The ship's own sensors feeding the model.** Shaft power and torque are a
  *measured* ice resistance — they would calibrate the one vessel number we
  currently borrow from another hull. Speed achieved versus speed predicted is a
  free daily model check. The ship's own anemometer would correct a known −3.89
  m/s wind-forecast bias in exactly the high winds that beset ships. Grounding:
  SA *Agulhas II* was instrumented this way for a 68-day Antarctic voyage, so
  there is a published blueprint on a comparable hull. **No sensor protocol or
  data contract has been scoped.**
- **Learning from historical incidents.** Besetting case studies are already
  assembled in our research — including the *Magdalena Oldendorff*, chartered for
  the 20th Indian Antarctic Expedition and beset near Novolazarevskaya in 2002.
  **Honest gap:** no besetting incident could be documented for any Indian-flagged
  vessel, and NCPOR expedition reports have never been reviewed. There is no
  incident database and no learning component.
- **Emergency notification to the nearest ship or station.** Grounding: our own
  research established that Southern Ocean traffic is genuinely thin — 255 unique
  vessels across the entire ocean 2014–2018, 88 % of them in the Peninsula sector
  — and that the nearest capable asset to Bharati is Russian, not Indian
  (Progress station, 5–10 km, with an airfield). **Blocked on the same missing
  piece:** there is no off-the-shelf Antarctic vessel-density product, so any
  "nearest icebreaker" logic must be built from raw satellite AIS.
- **Passive crew health monitoring.** Named in the brief. The two-tier
  architecture is the natural attachment point for one more synced stream.
  **Unresearched, not merely unbuilt** — no wearable, data source or health model
  has been evaluated.
- **A local language model on the bridge.** A bridge officer asks "what's the ice
  like near Bharati this week" and gets an answer sourced from the trained model's
  own output, running offline. This sits *on top of* the pipeline. It does not
  reverse our decision to refuse a chatbot as the visible "AI" — that decision was
  about not putting retrieval where a real model belongs.
- **The Arctic.** The physics transfers; the model does not. Ours is validated on
  Antarctic data only, and Arctic ice is a different regime that needs retraining
  and revalidation. The commercial hook is real — India announced a first pilot
  cargo vessel on the Northern Sea Route for 2027 — but this is an adjacency, not
  a capability.

---

## 6. Deployment plan

The deployment concept is: a pendrive goes into a bridge laptop, the software
starts, the user signs in, and the command centre loads. It talks to shore when
it can and keeps working when it cannot. Our two-tier architecture was designed
independently from the bandwidth side and lands in almost the same place.

**Why offline is a constraint and not a feature.** Geostationary satellite
coverage is unreliable south of about 70°S. Polar ships run on Iridium, which is
provisioned for small messages, not bulk data. A decision-support platform that
calls a live data API from the bridge is assuming infrastructure the ship does
not have.

**What runs aboard, with no network at all:**
- The whole application and web UI.
- Route re-planning on demand — measured at about 9 seconds, CPU only.
- Re-correction of the packed forecast when a fresh observation arrives —
  0.3–1 second, CPU only, once the production model exists. That figure is
  worked out from the network's arithmetic, not yet timed on a laptop. **No GPU
  is ever needed on the ship.**
- The local pack store: this voyage's pack plus previous ones, so a bad pack can
  be rolled back without a network call.

**What comes from shore, and how:**
- A nightly voyage pack — corrected forecast, iceberg positions, hazard mesh —
  built where the bandwidth and the GPU are.
- **Model weights never travel over the link.** Five members at ~3 M parameters
  is about 60 MB, three orders of magnitude past the message budget. They load
  once from USB at Cape Town before departure.
- Changed cells only, not a full refresh. Target: under 50 KB compressed per day.
  **This is a target, not a measurement.** What is measured is that a
  representative mesh block compresses to 76 KB, which makes 50 KB plausible
  rather than proven.
- **A pack arriving on a USB stick at a port call is a supported path**, not a
  degraded one. For a ship that sails once a season, sneakernet is legitimate.

**What must keep working with zero link, indefinitely:**
- Full re-planning on the last cached pack.
- A staleness indicator that escalates green → amber → red as the pack ages,
  always visible, never inferred.
- Past the pack's validity: **ROADMAP** — a climatology floor. A wide, honestly
  labelled planning corridor built from the last ten years of ice on that date.
  Not a confident route line, and not a blank screen. Specified, not implemented.

**Stated plainly, three ways this is not finished:**
1. **The login screen does not exist.** No document in this repository designs
   one and the running demo opens straight to the map. It is small, well
   understood engineering — a local authentication gate in front of the service —
   but it is a **GAP**, not a footnote.
2. **The pack machinery does not exist.** Signing, delta sync and the
   shore/vessel switch are a specification. Pack signing in particular has no
   key-management story, and delta sync has only ever run over a throttled local
   connection. We say *"tested under emulated link constraints,"* never *"tested
   over Iridium."*
3. **What is deployable today is the single-tier demo** — real cached satellite
   ice, real routes, no live calls, fails loud on missing data. That habit is the
   right instinct for the offline tier. It is not the offline tier.

---

## 7. The one killer feature

**The destination window: for this ship, on this date, is the station reachable?**

Three reasons this and not something else:

1. **It is built and measured today.** Not a design. A number with a file behind
   it, computed from real satellite data: 23 of 31 days closed at Bharati, 0 of
   31 at the approach 100 km north. (Maitri has no number yet: its offload point
   is unsourced, and we withdrew an earlier figure that was a no-data read.)
2. **It is the question the customer's own contract asks.** NCPOR's charter
   tender contains a clause for what happens if ice prevents discharge at Prydz
   Bay, and makes the fallback conditional on the coast being workable. There is
   no clause for what happens when it is not. Every routing product on the market
   answers "how fast is the transit." The customer is not asking that.
3. **It required work a competing team cannot shortcut.** The number is only
   correct because of a three-year satellite-quality audit that found a coastal
   data artifact — and the correction moved the answer in the direction that made
   our own system look *more* pessimistic. That is not something you produce in a
   demo week.

**The line to say:**

> Everyone else can tell you what the ice looks like. We tell you whether your
> destination will be open on the day you arrive.

**And the honest footnote we volunteer:** the strongest *idea* in this project is
carrying forecast uncertainty into the routing decision itself. We could not find
a published system that does it. It is not built, so it is not the killer
feature. It is the top of the roadmap, with a written pass/fail gate attached.

---

## 8. Innovation

**What is innovative and running today: a new question asked of old data.**
Nobody had to invent an algorithm to produce the destination-window result. What
it took was three years of audited satellite data, a vessel model for the real
ship, a found-and-fixed data bug, and the decision to ask "is this cell passable
for this hull on this date" instead of "what is the ice concentration here." The
answer inverted the problem: the ocean crossing is not the difficulty, the last
100 km is. That is an operational insight, and a judge can watch it work.

**What is innovative and honestly not built yet: uncertainty that reaches the
route.** **ROADMAP.**
- **The gap is verified in someone else's source code, not inferred.** The polar
  research community's own router ingests forecasts and then explicitly drops the
  uncertainty — `sic_stddev` and `ensemble_members` are removed by a
  `df.drop(columns=[...])` call. The field's best open-source router plans on the
  mean and throws the spread away.
- **Our search found no published study that propagates sea-ice forecast
  uncertainty into a routing decision.** We record that as medium confidence,
  because the search that established it was cut short.
- **What is unusual is the discipline attached to it.** The acceptance test was
  written before any numbers existed: coverage between 85 % and 96 % on held-out
  marginal-ice cells at 5-day lead, mean bound width under 25 concentration
  points, and it must beat inter-source disagreement as a free alternative. If it
  misses, the feature is withdrawn, the control is removed from the interface
  rather than left as theatre, and the claim is publicly demoted. That branch is
  written down so it cannot be renegotiated after the numbers arrive.
- **What a judge can ask us to show today:** the gate, the demotion clause, and
  the line in the incumbent's source. Not a slider moving a route. There is no
  slider.

**A third piece of innovation that is purely design discipline:** modelling
Antarctic protected areas by their legal instrument rather than as identical red
polygons. The brief asked for it by name. The naive version would refuse to route
to India's own station.

---

## 9. Feasibility

**The single sentence:** nothing left on this roadmap requires a research
breakthrough. Every open item is a download, a wire-up, or engineering with a
known shape.

| Question | Answer |
|---|---|
| Does the AI work? | Yes, measured against persistence: +18.5 % to +30.6 %, three-way temporal split, test scored once. One scoping we volunteer: the background was a reanalysis, so that figure is an upper bound on forecast skill until the no-background ablation is run. |
| Can it run on a bridge laptop? | Yes. Routing is measured at ~9 s on CPU. Model inference is estimated at 0.3–1 s on CPU from the network's arithmetic, not yet timed on a laptop. GPU is needed only ashore, for training. |
| Is the compute affordable? | The prototype trained on a free Kaggle T4 in 1–2 hours. |
| Is the data available and free? | Yes. NOAA/NSIDC needs a free login; Copernicus, ERA5, USNIC/BYU icebergs and GEBCO are all open. 1,096 real files already ingested with zero failures. |
| Do we have to build a router? | No. PolarRoute (British Antarctic Survey, MIT licence) installs in ~90 seconds and runs a full pipeline in ~9 seconds. We reuse it. |
| What is the one genuine research risk? | Whether calibrated uncertainty survives real coverage testing. It has a written, pre-committed pass/fail rule and a demotion path if it fails. |
| What happens if the model slips? | Stated in advance: ship the system with the packed operational forecast as the routed field, and promote the gradient-boosted iceberg model — which trains in minutes on data already on disk — so a trained model still ships. |

That last row is what "feasible" means here. Not "everything will work," but "we
know exactly what happens if it doesn't."

---

## 10. The research behind this

Six things we found by reading primary sources, running audits, or reading
installed code — not by reading summaries. Pick five for a slide.

1. **We red-teamed our own architecture and it broke.** A ten-section adversarial
   review of our own design document found three structural faults, not cosmetic
   ones: a training-data specification that was chronologically impossible (it
   named a sensor that did not exist for most of the stated period); a calibration
   method that could produce an ice concentration above 100 %; and a direct
   contradiction between two of our own documents about what baseline we had to
   beat. The third of those forced the model's entire redesign. The review is in
   the repository. So is the reply that argues back on three points.

2. **We read the international ice standard end to end, and found what it is
   blind to.** IMO MSC.1/Circ.1519 — the framework named on every Polar Ship
   Certificate — gives a risk formula and speed limits by ice class. Read in full,
   it never contains the words *pressure*, *compression*, *ridge* or *drift*.
   Compression is the hazard that traps ships: of ten vessels lost on the Northern
   Sea Route between 1922 and 1990, nine were lost to it. That is a gap in the
   standard itself.

3. **We read the router's source instead of its documentation, and found two
   things its docs do not say.** Its wave-resistance function is defined in three
   vessel classes and called from none — so the Roaring Forties, where most of the
   fuel actually burns, cost nothing in the model. And the route planner has no
   time dimension: a multi-week voyage is planned as though it will meet day-zero
   ice on the final day. That second one is exactly why a forecast is worth having
   and why time-expanded routing is at the top of our roadmap.

4. **There is no such thing as *the* sea-ice concentration at the ice edge.** A
   30-algorithm comparison found published algorithms disagree with each other by
   roughly ten times more at the ice edge than in thick pack — standard deviations
   from 2.8 % to 28.8 % at low concentration, worse in the Southern Hemisphere.
   At high concentration the spread collapses to 2.9–9.0 %. The producers of
   shipped uncertainty state themselves that it excludes three known error
   sources. And human analysts reading the same radar imagery agreed with
   automated segmentation only 39 % of the time. This is the argument for
   calibrated intervals rather than one confident number.

5. **Half of published Antarctic seasonal forecasts do not beat climatology.** A
   22-contributor, 3,000-forecast comparison found 51 % beat a plain
   climatological forecast, and its authors state they did not implement a
   persistence benchmark at all, calling it "not always straightforward." That is
   precisely the benchmark our result is measured against.

6. **Indian and foreign sources were compared source by source, and the honest
   finding is not the patriotic one.** NCPOR's own National Polar Data Centre is
   live and real — a genuine catalogue with dataset search — and Bharati publishes
   live meteorological observations. But these are station-scale, not global
   satellite grids, so their right role is ground-truth validation near India's
   own stations, not a primary model input. Every global input we use was retained
   because no Indian equivalent exists at the required resolution and coverage —
   not because a domestic option was passed over. **Open item:** the NPDC search
   endpoint was never confirmed programmatically usable; it needs an interactive
   browser session, not a fetch.

**Regulatory research we did and have not yet wired into code** — stated as
research, not as a feature: heavy fuel oil is banned south of 60°S under MARPOL
Annex I Reg. 43, so this vessel burns marine gas oil for the whole Antarctic leg;
the responsible search-and-rescue authority changes partway along this corridor
near 75°E; and there is no IMO Area To Be Avoided anywhere in Antarctic waters,
so no system should claim to honour one.

---

## 11. How this becomes a startup

Three stages. Each one names what has to be true before the next begins. That is
the difference between a roadmap and a wish.

**Stage 1 — Research tool (now → about March 2027).**
What exists today: the trained correction model, the tested iceberg physics, the
working demo on real satellite ice and real routes, the daily forecast harvest,
the protected-areas layer. Users: NCPOR scientists and the Indian polar research
community — not mariners yet. Revenue: none, and none expected. Possible support:
DPIIT startup recognition, an MoES-funded research project, a collaboration
through NCPOR's own sea-ice research group.
**Exit condition:** one named person inside NCPOR uses an output of this system to
answer a question they actually had. Not a demo. A use.

**Stage 2 — NCPOR operational pilot (about 2027 → 2029).**
A shore-side planning desk for one expedition season, a bandwidth-light package on
the ship, and a written post-season report comparing what we predicted with what
happened. The job: answer, before departure and again every day at sea, *when will
Bharati and the India Bay approach be workable, with what confidence, and what
does the ship do if that changes?* Revenue: a season service contract, procured
through the Government e-Marketplace under startup exemptions.
**Exit condition:** a completed season with a written verification report, and
NCPOR renewing. One season of real operational use is the only asset that opens
any other door.

**Stage 3 — Multi-programme and Arctic (2029 onward).**
The same engine offered to other national Antarctic programmes and to ice-going
commercial operators, with the corridor tuning made configurable rather than
hard-coded. Two things gate it and both are outside our control: whether India's
indigenous polar research vessel reaches a build contract, and whether the Stage-2
season produced a report good enough to show a foreign programme.

**The procurement fact that makes this practical.** A DPIIT-recognised startup on
the Government e-Marketplace is exempt from prior-turnover requirements, prior-
experience requirements and earnest-money deposit. The three normal reasons a
two-year-old company cannot bid for a government contract are waived by rule. The
path from working prototype to purchase order is short and written down.

---

## 12. Market entry

The sequence follows credibility, not market size. Each step is only possible
because the one before it happened.

**Step 1 — Publish the honest paper trail.** The self-review, the true-claims
list, the withdrawn 17.4-day number, the experiment that came out against us. In a
scientific-institution market, a team that documents its own failures is buying
trust with the only currency that works there. It costs nothing and is already
done.

**Step 2 — Go through the door that is already open.** NCPOR has a sea-ice
research group, a national polar data centre and an annual expedition. The entry
is a research collaboration, not a sales call. Nobody in this market buys from a
cold email.

**Step 3 — Attach to a purchase that already exists.** Two are live. NCPOR's
charter tender already requires the vessel to carry **"ice-information receiving
equipment"** — India buys the receiver and, as far as we could establish, owns
nothing on the other end of it. Who feeds that receiver today is a question we
could not answer, and it is the first one to ask NCPOR. And Maitri II is a
multi-season heavy-cargo build to a fixed deadline, on a coast for which nobody —
including us, yet — has published a day-by-day record of when a ship can work
it. We hold the data and the method; producing that record is the first thing a
collaboration would do.

**Step 4 — Be in the ship design conversation while it is still a design.**
India's indigenous polar research vessel is at the memorandum-and-design-
preparatory stage with GRSE and Kongsberg. Software specified during a ship's
design gets a place on the bridge. Software written after delivery gets bolted on.
**Be precise on the slide: there is no contract, no announced cost and no delivery
date** — and do not confuse it with the ₹839.55 crore Ocean Research Vessel
contracted in July 2024, which is a different hull for the Deep Ocean Mission.

**Step 5 — Only then go abroad,** with one verified season behind us, to the
programmes most likely to buy: those already paying a commercial vendor for ice
information, and those without a large in-house capability.

**What we will not do:** try to displace a national ice service, sell satellite
data, or pitch insurers before we have loss evidence. All three look good on a
slide and are dead in the field.

---

## 13. How it makes money

### First, the arithmetic that kills the obvious model

Every hackathon deck proposes a per-vessel subscription. Count the ships.

```
national programme vessels genuinely working fast ice    30 – 40   [ASSUMPTION on a sourced count of 55]
ice-going expedition ships beyond the Peninsula          10 – 15   [ASSUMPTION — no source gives this split]
krill vessels in the main fishing area                       14   [SOURCED]
                                                         ---------
serviceable fleet worldwide                              54 – 69
```

At the top of the published weather-routing price band — USD 20,000 per
vessel-year, which is trade-press for the mid-latitude market, not a polar quote:

```
60 hulls × $20,000                    = $1.2 M / year   at 100 % of every hull on earth
60 hulls × 25 % share × $20,000       = $300 k / year   at a realistic share
```

**Three hundred thousand dollars a year is the honest ceiling of the subscription
business.** It supports a handful of people — about the size (seven core staff)
the one real polar-ice specialist company reached after twelve years with the two
best-known polar research ships in the world as customers.

Put that number on the slide. A judge who has done this arithmetic will believe
everything that comes after it.

### So the money comes from programme contracts, not seats

The value is not spread thinly across many hulls. It is concentrated in a few
programmes where one bad decision costs more than a decade of subscriptions.
There is also an Indian precedent that settles the pricing question: MoES already
runs a national ship-routing advisory through INCOIS and gives it away free. We
cannot charge Indian mariners for an advisory when the ministry's own equivalent
is free — but the institutional home, the delivery channel and the belief that
this is worth funding all already exist. **The customer is the ministry. The
product is a service contract.**

**Three pricing anchors, in decreasing order of how well they are sourced:**

1. **The saved ship-day. [SOURCED ratio, ASSUMPTION on the count.]** The charter's
   own financial formula is a day rate multiplied by 100 days plus fixed terms.
   **So one lost day is about 1 % of the season's hire.** That statement needs no
   dollar figure and cannot be argued with. Price the service as N saved ship-days
   and let the customer substitute their own rate:
   `service price = N × the customer's own day rate`.
   **The honest warning:** N = 3 is unproven, and our own stale-data experiment
   came back at 0.03 days on the single date tested. The multi-date route-regret
   sweep either validates this pricing model or kills it. That is the weakest link
   in the plan and we are naming it before a judge does.
2. **The station build. [SOURCED, secondary.]** Maitri II is a ₹2,000 crore,
   seven-year programme to a January 2029 deadline, across a coast whose
   day-by-day workability nobody has measured — we have not either, yet, because
   the offload point is unsourced. Planning support at a hundredth of one percent
   of that programme is ₹20 lakh. The argument is not that we are cheap. It is
   that a fixed-deadline programme currently prices its ice scheduling risk at
   zero.
   *(These figures rest on secondary reporting; the primary approval document was
   not located.)*
3. **The metered link. [SOURCED, tender §15.4.]** Communication charges on the
   charter are payable as per actual. A design that moves kilobytes instead of
   megabytes is a line-item saving on a bill NCPOR already receives, not an
   engineering preference.

### Rough shape of revenue — every figure is an assumption, shown so it can be argued with

| Stage | Model | Rough annual | Basis |
|---|---|---|---|
| 1 (to 2027) | Research collaboration / grant | ₹0 – 25 lakh | Non-dilutive only |
| 2 (2027–29) | One programme service contract per season | ₹40 – 80 lakh | ~3 saved ship-days at an assumed day rate — **unverified** |
| 2b | Maitri II logistics planning support | ₹20 – 50 lakh / yr | A fraction of a hundredth of the programme |
| 3 (2029+) | 3–6 foreign programme licences | $60 – 120 k each | Above the sourced weather-routing band; polar niche |
| 3 | 10–20 commercial vessel subscriptions | $15 – 25 k each | Within the sourced band |
| **Stage 3 total** | | **≈ $1 – 2 M / yr** | 8–12 people |

**Said plainly: at full success this is a one-to-two-million-dollar-a-year
specialist company.** That is a good business and a poor venture story. We say so
because it is true, and because the version of this slide with a hockey stick on
it is disprovable by anyone who has counted the ships. The scale case, if it
comes, is the Arctic — and that is **FUTURE**, unbuilt, and needs retraining on a
different ice regime.

**Two buyers we assessed and are not pitching.** Insurers and P&I clubs: the
evidence shows underwriters manage polar exposure through warranties and permanent
exclusion zones, not by buying analytics — and Southern Ocean loss frequency is
about two incidents a year, too thin to price on. Parked, not pitched. And
Southern Ocean commercial fishing: a real segment with real money-shaped ice
problems, but a commercial fleet with commercial procurement we have never sold
into. Not our beachhead.

---

## 14. Competitors, and where we stand

No strawmen. Every entry is a real system and every one of them is genuinely
better than us at something.

| System | What it actually is | Genuinely better than us at | The specific gap we fill |
|---|---|---|---|
| **IcySea** (Drift+Noise, a research-institute spin-off, seven core staff, founded 2014) | Commercial chart-based ice-navigation app: near-real-time radar imagery plus bias-corrected drift data, delivered to a bridge client over low-bandwidth links, **advertised as Iridium-tested** | Deployed and operating today, with national programme ships as named users. Their low-bandwidth delivery is in service at sea; ours is not. Polished bridge interface. | It is a chart and data display, not a route optimiser. No vessel-specific model, no destination-window answer, no protected-area regime modelling. |
| **Polar View** (European public-good service) | Near-real-time ice information: enhanced charts, ice edge, iceberg monitoring, with a documented ship-routing-in-ice use case | Long-running, multi-agency, credible provenance; real iceberg monitoring at operational scale | A chart and advisory service, not a trained model measured against a stated baseline. No evidence of tuning to any specific vessel or this corridor. |
| **StormGeo** (the commercial voyage-optimisation incumbent, ~13,000 vessels) | Global voyage optimisation with ice as one input among many; 24/7 human route analysts on call | Mature, commercial-grade, genuinely multi-objective at scale | A different market: global commercial shipping, subscription, no Antarctic resupply specialisation. **Not a strawman — a precedent.** Their human-in-the-loop fallback is evidence that full automation is not trusted at the edges, which is the posture we argue for too. |
| **PolarRoute** (British Antarctic Survey, open source) | **The router we reuse.** Installs in ~90 s, runs a full pipeline in ~9 s. | It is the field's own tool, maintained by domain experts. We did not reinvent it, and that was the right call. | Verified in its installed source: it drops forecast uncertainty, plans on one frozen mesh with no time dimension, and has no iceberg layer. Those are the honest basis for our roadmap — **not for a claim that we have already extended it.** |
| **IceNet / ANTSIC-UNet** | Published sea-ice forecasting neural networks | ANTSIC-UNet is validated on Antarctic extreme-minimum years, a genuinely hard regime | Research artifacts, not decision-support products. No routing, no vessel model, no reachability answer. IceNet's published validation is **Arctic** — its own paper title says so — and extrapolating it to Antarctica without saying so is a mistake a competing team can easily make. |
| **NSIDC / USNIC** | The authoritative observational and iceberg-tracking data | Ground truth. Nothing here competes with them — they are our inputs. | They publish state. They never publish a route decision or a ship-specific reachability answer. |

**Where we honestly stand:** we are not ahead of IcySea on delivery, and we do not
claim to be. We are not ahead of StormGeo on voyage optimisation at scale. What
none of them publishes is the destination-window answer, and none of them models
Antarctic protected areas by legal regime.

**And the competitor we expect at SIH.** Four teams independently built the same
chatbot-over-real-data wrapper for last year's sibling ocean-data problem
statement. The predictable build for this one is: pull the public data, fit a
U-Net, add a physics *or* an ML drift model, run A* over a grid, wrap it in a map
with a chat box, demo three chosen scenarios. That build has single-source ice
truth, no uncertainty carried anywhere, a static shortest path, and assumes a
live internet connection on a ship that does not have one.

---

## 15. Strengths

Each of these is checkable in under a minute.

- **The trained model beats the baseline that matters, and honestly.** +18.5 % to
  +30.6 % over persistence across 1–7 days. Three-way temporal split, never
  random. Test set scored exactly once. Baselines fixed before training. **The
  advantage grows with lead time** — the model matters most at the horizon a
  voyage is actually planned over. And we scope it ourselves: the background was
  a reanalysis, so this is an upper bound on forecast skill until the
  no-background ablation is run.
- **The operational finding reframes the whole problem.** The crossing is not
  where the difficulty is. Bharati's own cell was closed 23 of 31 December days
  while the approach 100 km north was open all 31. That is a domain insight, not a
  demo trick, and it matches how Indian resupply already works.
- **A real bug was found in the standard satellite product, and fixed in the
  cautious direction.** 100 % of days affected, 43.2 % of days in the Bharati
  approach box, four of eight apparently-open December days explained. The fix
  makes the ice look heavier, not lighter.
- **The iceberg physics is published, tested, and pointed at the real
  catalogue.** 23/23 tests reproducing the paper's own coefficient table; 33 real
  tracked bergs classified by drift regime. Not yet a trajectory — and we say so.
- **Protected areas are modelled correctly rather than conveniently.** The legal
  distinction is the real one from Annex V, and the corridor's own data — zero of
  33 polygons marine — was checked rather than assumed.
- **The engineering culture is fail-loud.** The demo refuses to boot if a day's
  satellite file is missing rather than render a gap as data. 55 tests pass. The
  daily harvest fails loudly on a bad bulletin rather than archiving the wrong
  day — its very first run failed loudly at the login step rather than archiving
  nothing quietly. This is the property that stops a demo — or a voyage — from
  confidently showing something false.
- **The project corrects itself in writing, before anyone else finds the error.**
  A 17.4-day transit figure was withdrawn when a wrong ship speed was found, and
  corrected to 8.6 days. A figure caption was withdrawn when measurement
  contradicted it. A "Maitri closed 31 of 31" figure was withdrawn when it turned
  out to be a no-data read, not a measurement. A defence of the model's leakage
  question was withdrawn when it turned out not to follow. A null result — static
  planning cost only 0.03 days on the one date tested — was reported instead of
  buried. That paper trail is itself an asset in front of judges who check.
- **We reused the field's own router instead of reinventing one.** A judge who
  knows this domain will recognise that as the right call.

---

## 16. Weaknesses

Each paired with what we actually do about it.

- **The sharpest one: the model was corrected against a reanalysis, not a live
  forecast.** A reanalysis absorbs observations near the date it describes, so
  there is a real question of whether the model is quietly seeing the answer.
  *The defence we no longer make:* that raw GLORYS12 scores 0.163 on its own,
  worse than persistence, so it cannot be handing over the target. That does not
  follow — 0.163 is grid and ice-model mismatch between a 1/12° ocean model and a
  25 km satellite product; it is bias, and a field can score badly and still
  carry the target. The model sees the background valid *at* the target date
  and the background at issue time, so the assimilated change between them is a
  difference the first layer can form. The flat raw-GLORYS12 error across lead
  time is the fingerprint of a field that has seen the target, and "the
  advantage grows with lead time" is what a leaked tendency would produce.
  *So:* the +18.5 % to +30.6 % is an upper bound on forecast skill, not a
  measurement of it. *Not yet run:* the no-background ablation that settles it
  either way, about twenty minutes of GPU time. *The real fix, already in
  motion:* the production model corrects a live forecast harvested daily, where a
  forecast issued today structurally cannot know a future day's observation.
- **We beat persistence and raw reanalysis. We have not beaten CMEMS's own
  operational forecast.** That is the comparison our own architecture document
  sets as the bar. The forecast archive needed to run it started on 31 August 2026
  and has seven days in it. Quote the two wins we measured, not the third.
- **One third of the problem statement — iceberg trajectories — has no
  trajectory yet and no measured error.** The drift physics is implemented and
  tested against its paper; the real catalogue has been read and each berg
  classified by regime. But no berg has been stepped forward, because that needs
  an ocean-current field we have not wired in, and nothing has been scored
  against the observed-track archive. For the giant bergs anyone tracks, the
  paper's own conclusion is that they move with the current — so our forecast
  skill will be set by the quality of the current field, not by these equations.
  Published physics-only drift errors at multi-day horizons are of order 100 km
  or more. *Mitigation, designed not built:* projections capped at 72 hours,
  re-projected daily from fresh USNIC fixes, and an exclusion radius set by
  measured leave-one-berg-out error — never a hand-picked buffer.
- **Maitri has no destination-window number.** Its offload point is unsourced,
  so the script does not score it. An earlier "31 of 31 closed" was a no-data
  read counted as closed; it is withdrawn.
- **No calibrated uncertainty layer.** One model per horizon, no ensemble, no
  bound. Until it exists, a fair critic can say this is PolarRoute plus a corrected
  forecast, not the uncertainty-aware router the pitch aims at. *Mitigation:* the
  method and its numeric pass/fail gate are fully specified; the gap is compute and
  data volume, not an unanswered design question.
- **Bathymetry constrains nothing today.** GEBCO is not downloaded, so the 8.6-day
  route ignores seabed depth entirely. *Mitigation:* free download, provenance-
  conditional depth margin already designed. Smallest gap on this list.
- **Waves cost nothing in the router.** Verified by reading the installed source:
  the wave-resistance function is defined and never called, so the Roaring
  Forties — where most of the fuel burns — impose no penalty. *Mitigation:* we
  present the transit time as a lower bound, never a prediction.
- **8.6 days is steaming time, not a voyage.** No sea state, no station time, no
  cargo operations, no weather holds, and it assumes sustained service speed when
  this ship's observed average across all conditions is about half that. A real
  expedition voyage takes two to three weeks.
- **Vessel physics is partly borrowed and we say so.** One resistance parameter
  is carried over from a different hull. The ship's ice class was verified from
  the registry, but its modern equivalent could not be sourced — one source
  explicitly denies the obvious mapping, so we assert none. No fuel figure is
  quoted at all rather than guessed.
- **The offline architecture is designed, not built**, and a real commercial
  competitor already ships field-proven low-bandwidth delivery. We are not ahead
  here. *Mitigation:* the design is the most fully worked-out part of the project,
  with a measured 76 KB mesh block behind its central bet — and we describe our
  sync as tested under emulated link constraints, never as tested over Iridium.
- **No login screen**, though the deployment concept describes one. Nothing in
  this repository designs it.
- **The "zero marine protected areas" finding is about this corridor**, not a
  general property of the system.
- **One departure date is one sample.** The route-regret result is a null result
  on a single date. We report it and we do not generalise from it.
- **The commercial plan has an unmitigated single point of failure.** If NCPOR
  declines, Stage 2 has no substitute customer. We have no answer to that and we
  are not pretending otherwise.

---

## 17. How these features survive real industry use

A judge sees this once. An NCPOR operations officer would use parts of it every
day in year two — and other parts would go stale fast. Both halves belong on the
slide.

**Why the core features survive:**

1. **It answers the question the contract actually asks.** The charter's failure
   clause is about whether ice permits discharge at Prydz Bay. The
   destination-window output answers exactly that. Most routing tools answer a
   question this customer is not asking.
2. **It works on the link the ship actually has.** Communications are billed as
   used, and satellite coverage is unreliable in the operating area. A design that
   assumes a live API call is a design for a ship that does not exist.
3. **It refuses to run on missing data.** On a bridge, a product that quietly
   renders a gap as open water is worse than no product. This is a small
   engineering decision that becomes a large trust decision the first time it
   fires.
4. **It states what it cannot do.** No growlers. No steering. No fuel number. No
   compliance claim we cannot back. Systems that overstate get switched off after
   the first season. Systems that state their limits get used within them.

**What we would add in year two, because a working crew would ask for it — all
ROADMAP:**

- **A places-of-refuge and rescue-distance table.** Static data, no bandwidth
  cost, and it answers a question the master has no tool for: who is nearest and
  how far is help really. The nearest capable asset to Bharati is a Russian
  station 5–10 km away with an airfield; the nearest to Maitri is about 530 km. The
  polar community's own best case for help arriving is 5–6 sailing days.
- **Prior-year ice history shown to the bridge.** We already hold 1,096 real daily
  files and use them only for training. "What should I expect here in late
  December" is currently unanswerable to the captain even though the data to
  answer it is sitting in the repository.
- **The ship's own sensors feeding back.** This is what turns software that ships
  once into something that gets more accurate every voyage it rides.
- **Speaking the bridge's own language.** An advisory that reads "9/10 close pack,
  thick first-year, ridged" survives contact with a working ice navigator. One
  that reads "lots of ice" gets ignored after a week, however good the model
  behind it.
- **Stop arguing once the decision is made.** At departure the system should argue
  its route against the captain's plan. After he chooses, it must switch to
  micro-adjustments and things he might miss. A tool that keeps re-litigating a
  rejected route is a tool a crew turns off.
- **Turn the honest limitation into a daily output.** We will never see a growler.
  But we can forecast when the lookout is *blind* — visibility under 100 m, or seas
  above the height at which growlers stop being visible at all. That is a genuinely
  new, genuinely usable output built entirely out of a limitation.

**What breaks first if nothing is added:** a router that keeps arguing for a
rejected route; an advisory that never learns from the ship carrying it; and any
claim to regulatory compliance, which needs an ice-*type* output this system does
not yet produce. Each has a named fix already on the roadmap. None is a surprise.

---

## The architecture diagram

Editable diagrams for the deck are already in the repository:
`docs/v1.drawio` (system), `docs/v1_tiers.drawio` (shore/vessel split) and
`docs/DECISION_FLOW.drawio` (how a forecast becomes a decision). Open them in
draw.io directly.

---

## The one sentence to leave with a judge

> Every other system tells a captain what the ice looks like — we measured that
> India's own station was shut 23 days out of 31 while the water 100 km out was
> open every day, and we built the thing that tells him which day he can get in.
