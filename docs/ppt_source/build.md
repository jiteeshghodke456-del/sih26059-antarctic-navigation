# Feasibility, Roadmap, Deployment, Strengths and Weaknesses — SIH26059

Draft working notes for the master prompt's §39/§40 deliverables (roadmap,
deployment plan, strengths/weaknesses, industry survival). This is not the
6-slide submission — it is the source material a deck gets built from, and
it should stay boring and correct rather than exciting and wrong. Every
number here has a file behind it. Where something is designed but not
built, it says ROADMAP, in capitals, every time.

Sources: `docs/ARCHITECTURE.md`, `docs/WEAKNESS_ANALYSIS.md`,
`docs/TRUE_CLAIMS.md`, `docs/backlog.md`, `docs/DEMO_PLAN.md`,
`docs/ISIH_RESULTS.md`, `isih/protected_areas.py`.

---

## 0. Where the project actually stands today

Two planning documents describe two different moments of the same build.
`docs/WEAKNESS_ANALYSIS.md` (31 Aug) is a pre-build review that says "do not
start Phase 2 as specified" — from-scratch U-Net, impossible training
window, no compute plan. `docs/backlog.md` records that every one of those
objections was resolved before Phase 2 ran: the model was re-aimed to
bias-correct CMEMS instead of forecasting from scratch, the training
product/window was fixed, and a GPU (Kaggle T4) was named. Phase 2 then
ran, in reduced form, and produced the real numbers in
`docs/ISIH_RESULTS.md`. So the roadmap below is not the original plan
re-typed — it is that plan checked against what actually happened.

**One line of feasibility, stated plainly:** nothing left on this roadmap
requires a research breakthrough. Every open item is either a data
download, a config wire-up, or an engineering task with a known shape. The
one genuine research risk — whether the calibrated uncertainty (conformal
`SIC_upper`) survives real coverage testing — has a written, pre-committed
pass/fail rule and a demotion path if it fails. That is what "feasible"
means here: not "everything works," but "we know exactly what happens if
it doesn't."

---

## 1. Roadmap — phases, what each delivers, what gates the next one

| Phase | Delivers | Status today | What gates moving on |
|---|---|---|---|
| **0 — Spine** | Repo, FastAPI + web shell, daily CMEMS forecast harvest cron | **DONE.** Harvest is 12/12 green, 7 consecutive days archived, fails loud on a bad bulletin rather than archiving a wrong one. | Nothing — this keeps running in the background for every later phase. |
| **1 — Real routing on real data** | Real ice + bathymetry ingestion, QC pass, a real Cape Town → Bharati route from a real router | **MOSTLY DONE.** NSIDC satellite ice (1,096 real files, 0 failures) is ingested and quality-checked — the land-spillover bug (below) was found and fixed here. PolarRoute computes a real 8.6-day route on real observed ice. **GEBCO bathymetry is not yet downloaded** — depth and land constrain nothing in the route today. | GEBCO is a free download and a config wire-up, not new engineering — smallest remaining item on this list. |
| **2 — The trained model** | A model that beats the operational baseline, evaluated once, honestly | **PROTOTYPE DONE.** Beats persistence at every horizon, 1–7 days, by +18.5% to +30.6% (`docs/ISIH_RESULTS.md`). Single model per horizon, 12 of the planned 19 channels (no ERA5 wind/temperature yet), ~2 years of training data, corridor-only. **Production version** — 5-member ensemble, conformal calibration, full 1993–2024 history, all 19 channels — is not built. | GPU time (each extra year of NSIDC history is a download, not new code) and running the calibration pass/fail gate the architecture already specifies. |
| **3 — Uncertainty and hazards** | Calibrated `SIC_upper` driving the route, iceberg exclusion, protected-area constraints | **PARTIALLY DONE.** Iceberg drift physics (Wagner-Dell-Eisenman 2017) is implemented and tested — 23/23 tests reproducing the paper's own coefficient table, run on the real live USNIC catalogue (33 bergs, 15 inside the corridor). Protected areas are modelled by legal regime today (§3 below). **Not yet done:** the iceberg polygons are not wired into PolarRoute's `excluded_zones` hook; the conformal uncertainty layer does not exist because it needs the Phase 2 ensemble first. | Phase 2's ensemble (uncertainty has nothing to calibrate against without it); wiring the already-computed berg polygons into the router's existing extension point. |
| **4 — Offline tier** | Signed, versioned packs; shore/vessel mode split; staleness banner; climatology-mode floor | **DESIGNED, NOT BUILT.** What exists today is a single-tier local demo: FastAPI + canvas serving real cached satellite and route data, refusing to start if a day's satellite file is missing. That fail-loud habit is the right instinct for Phase 4, but the actual pack build/sign/delta-sync machinery, the `MODE=shore\|vessel` switch, and the climatology-mode floor are specified in `docs/ARCHITECTURE.md` §2 with real measured numbers (a representative mesh block compresses to 76 KB) but none of that code exists yet. | This is the next phase to build, not a research question — the design is the most fully worked-out part of the whole architecture. |

**Stretch, explicitly ordered, cut first if the schedule slips:** GBM
iceberg-residual correction, NCPOR NPDC validation data, a Sentinel-1
ice-edge validation figure, POLARIS-compliant thickness output. None of
these are load-bearing for the pitch; the trained model and the offline
architecture are.

---

## 2. Deployment plan — reconciling the pendrive concept with the architecture

The master prompt's deployment picture is: pendrive into a bridge laptop,
software starts, a login screen, then the command centre, which talks to
shore when it can and keeps working when it can't. `docs/ARCHITECTURE.md`
independently designed a two-tier shore/vessel split to solve the same
problem from the bandwidth side. They agree almost exactly. One piece of
the brief has no answer anywhere in the docs, and it is said here rather
than glossed over.

**What runs aboard, with no network required at all:**
- The full FastAPI service in `MODE=vessel`, plus the web UI.
- PolarRoute re-planning on demand — measured at ~9 seconds, CPU only.
- The trained model's re-correction of the packed forecast when fresh
  observations arrive — measured at 0.3–1 second, CPU only, once built
  (Phase 2's production model). No GPU is needed on the ship at any point.
- The local pack store: the current voyage pack plus previous ones, so a
  corrupt or wrong-looking pack can be rolled back without a network call.

**What comes from shore, and how:**
- A nightly "voyage pack" — the corrected forecast, uncertainty layer,
  iceberg positions, hazard mesh — built where the bandwidth and the GPU
  are. Model weights (~60 MB) are never part of this; they load once from
  USB at Cape Town before departure, because 60 MB is three orders of
  magnitude past even a good Iridium day.
- Delta sync only: changed mesh cells and new forecast leads, not a full
  refresh, target under 50 KB compressed per day. This is a target, not
  yet a measurement — the measured number so far is a representative mesh
  block at 76 KB, which is what makes 50 KB/day plausible rather than
  proven.
- Sneakernet is a first-class path, not a fallback: a pack arriving on USB
  at a port call is a legitimate way to update a system that sails once a
  season.

**What must keep working with zero link, indefinitely:**
- Full re-planning on the last cached pack.
- A staleness indicator that escalates green → amber → red as the pack
  ages, always shown, never inferred.
- Past the pack's validity, the plan is designed to fall back to
  ROADMAP: a climatology-mode floor — a wide, honestly-labelled planning
  corridor built from the last 10 years of ice on that date, not a route
  line and not a silent refusal. This is specified but not implemented.

**The gap nobody has answered: the login screen.** The brief describes an
authentication step between plugging in the pendrive and reaching the
command centre. No document in this repository designs one, and the
running demo has none — it opens straight to the map. This is a small,
well-understood piece of engineering (a local auth gate in front of the
FastAPI UI), not a hard problem, but it does not exist today and should
not be presented as if it does.

---

## 3. What is new today: protected areas modelled by legal regime

`isih/protected_areas.py`, built against the Antarctic Treaty
Secretariat's own shapefile (`apa_shape_2024.zip`, 148 polygons, 33
intersecting this corridor). The finding is more useful than "avoid the
protected areas," because that instruction is wrong for this corridor:

- **Bharati sits inside ASMA 6** (Larsemann Hills), which India
  co-proposed. An ASMA does not require a permit to enter — it means
  activity there follows a management plan. A system that treated it as a
  no-go polygon would refuse to route to India's own station.
- **ASPA 174 (Stornes)** is 1.9 km away, and **ASPA 163 (Dakshin
  Gangotri)** — an Indian-designated protected area — is 4.7 km from
  Maitri. ASPAs *do* require a permit to enter at all (Antarctic Treaty
  Annex V, Art. 3).
- **Of the 33 corridor polygons, zero are flagged marine** in the
  Secretariat's own data. So none of them restricts the ship's transit —
  they bind what happens ashore (landing, small-boat, helicopter,
  personnel), not the sailed track.

That is the correct legal reading, not a simplification for the demo: a
different corridor (the Ross Sea, say) does have marine protected areas in
the same national dataset, and the code path for that case — a permit-gate
constraint on the vessel, not a routing exclusion — already exists and is
tested; it has simply never been exercised against real marine geometry,
because none exists here.

---

## 4. Strengths — specific, and checkable in under a minute each

- **The trained model beats the real baseline, honestly measured.**
  +18.5% to +30.6% over persistence across 1–7 days, on a three-way
  temporal split (never random), scored on the test set exactly once, with
  every baseline fixed before training started. The advantage *grows* with
  lead time — the model matters most at the horizon a voyage is actually
  planned over. `docs/ISIH_RESULTS.md`.
- **The real operational finding reframes the whole problem.** The ocean
  crossing is not where the difficulty is — Bharati's own cell was closed
  23 of 31 December 2019 days while the approach point 100 km north was
  open all 31. That matches how Indian resupply actually works (hold at
  the fast-ice edge, move cargo by helicopter and barge), and it means the
  decision that matters is *when to arrive and whether to wait*, not which
  line to draw across open water. That is a domain insight, not a demo
  trick.
- **A real bug was found in the standard satellite product, and fixed.**
  The NOAA/NSIDC record's land-spillover filter writes suppressed coastal
  pixels as 0.0% — reading as open water — on 100% of days, affecting
  43.2% of days in the 200 km box around Bharati. Four of the eight
  apparently-open December days at Bharati were this artifact, not real
  ice retreat. The fix moves the corridor's coastal ice reading *up* (more
  cautious), which is the safe direction, and it was checked, not assumed.
- **The iceberg physics is a real, published, tested model.** Wagner,
  Dell & Eisenman (2017), reproduced from the paper's own coefficient
  table and its 765 m critical length, 23/23 tests passing, run on the
  live USNIC catalogue rather than a synthetic one (33 tracked bergs, 15
  inside this corridor).
- **Protected areas are modelled correctly, not conveniently.** ASPA vs.
  ASMA is the actual legal distinction in Annex V, and the corridor's own
  data — zero of 33 polygons marine — was checked rather than assumed. A
  weaker team would have drawn 33 no-go blobs and called it done.
- **The engineering culture is fail-loud, not fail-quiet.** The demo boots
  in 3.1 seconds, passes 43/43 tests, and refuses to boot at all if a
  day's satellite file is missing rather than rendering a gap as data; the
  CMEMS harvest is 12/12 green with the same discipline. This is the
  property that stops a demo — or a real voyage — from confidently showing
  something false.
- **The project corrects itself in writing, before anyone else finds the
  error.** A 17.4-day transit figure was withdrawn when a wrong ship speed
  was found and corrected to 8.6 days; a route-figure caption was
  withdrawn when measurement contradicted it; a null result (static
  planning cost only 0.03 days versus daily replanning, on the one date
  tested) was reported instead of hidden. That paper trail is itself a
  competitive asset in front of judges who check.

---

## 5. Weaknesses — specific, and paired with the honest mitigation

- **The sharpest one: the model was corrected against a GLORYS12
  reanalysis background, not a live forecast.** A reanalysis assimilates
  observations near the date it is describing, so there is a real
  question of whether the model is quietly seeing the answer.
  *Partial defence:* the raw background alone scores 0.163 — worse than
  persistence at every horizon — so it plainly does not hand over the
  target. *Not yet run:* the clean ablation (zero the background channel,
  retrain, see if the score barely moves) that would settle the question
  either way. *The real fix, already in motion:* production corrects the
  daily-harvested live CMEMS forecast (running now, 7 days archived),
  where a forecast issued today structurally cannot know a future day's
  true observation.
- **No calibrated uncertainty layer yet.** Today there is one model per
  horizon and no conformal `SIC_upper`. Until it exists, a fair critic can
  say this is "PolarRoute plus a corrected forecast," not yet the
  uncertainty-aware router the pitch claims. *Mitigation:* the calibration
  method (stratified conformal) and its pass/fail gate (MIZ coverage in
  85–96% at day 5, beats a trivial disagreement proxy, or the claim is
  publicly demoted) are fully specified in `docs/ML_ARCHITECTURE.md` — the
  gap is compute time and data volume, not an unanswered design question.
- **Bathymetry constrains nothing today.** GEBCO has not been downloaded,
  so the 8.6-day route ignores seabed depth entirely. *Mitigation:* it is
  a free download with the provenance-conditional depth margin (surveyed
  vs. predicted seabed) already designed — the smallest gap on this list
  to close, and it is on the roadmap, not stuck.
- **Wave resistance is dead code in the router.** Verified by reading
  PolarRoute's installed source: `wave_resistance()` is defined and never
  called, so the Roaring Forties — where most of the fuel actually burns —
  cost nothing in the model. *Mitigation:* named plainly rather than
  hidden; the transit time is presented as a lower bound, never a
  prediction, until the vessel subclass overrides the resistance function.
- **Vessel physics is partly borrowed, and the project says so.**
  `force_limit` is carried over from a different hull (the RRS Sir David
  Attenborough); Golovnin's ice class (ULA) has no confirmed modern
  Arc/PC equivalent; no fuel figure is quoted at all rather than guessed.
  *Mitigation:* the ship's own shaft-power telemetry is a free daily
  calibration source once wired in — see §6 below — and until then the
  team declines to state a number it cannot back.
- **The offline architecture is designed, not built.** Pack signing,
  delta sync, the shore/vessel mode switch, and the climatology-mode floor
  exist as a specification with real measured numbers behind them (a
  representative mesh block at 76 KB), not as running code. *Mitigation:*
  this is squarely the next phase, not an open research question, and the
  measured mesh number is exactly what makes the design's central bet —
  that a daily update fits in 50 KB — plausible rather than hopeful.
- **No login screen, though the brief describes one.** Stated in §2 above
  and repeated here because it is a weakness, not a footnote: the deployed
  concept has an authentication step that nothing in this repository
  designs or builds yet.
- **The "zero marine protected areas" finding is about this corridor,
  not a general property of the system.** It is correct for Cape Town →
  Bharati/Maitri today. A different route (Ross Sea, for instance) would
  hit marine protected areas in the same national dataset, and while the
  code already has the right constraint type for that case, it has never
  been run against real marine geometry.

---

## 6. Why these features still matter after the demo — industry survival

A judge sees this once. An NCPOR operations officer, or a shipping
company running the Cape Town corridor every summer, would use parts of
this daily in year two — and other parts would go stale fast if nothing
changes. Both halves are stated here on purpose.

**What carries into daily use, concretely:**

- **A places-of-refuge and SAR-remoteness table.** Static data, no
  bandwidth cost, and it answers a question the master currently has no
  tool for: who is nearest, and how far is help really. Progress station
  is 5–10 km from Bharati with an airfield; SANAE IV is ~530 km from
  Maitri; COMNAP's own best case for help arriving is 5–6 sailing days.
  This is a one-time build that pays out on every single voyage.
- **Prior-year ice history surfaced to the bridge.** The system already
  holds 1,096 real days of satellite history — used today only for
  training. "What should I expect here in late December" is currently
  unanswerable to the captain even though the data to answer it is
  sitting in the repository. Cheap to add, useful every voyage.
- **The ship's own sensors feeding back into the model.** Shaft
  power/torque is a real, measured ice resistance that would calibrate
  `force_limit` instead of borrowing another hull's number; speed achieved
  versus speed predicted is a free daily model check; the ship's own
  anemometer corrects the -3.89 m/s ERA5 wind bias in precisely the high
  winds that beset ships. This is what turns the tool from software that
  ships once into something that gets more accurate every voyage it
  rides, without a retraining cycle.
- **Speaking the bridge's own language.** An advisory that reads "9/10
  close pack, thick first-year, ridged" survives contact with a working
  ice navigator. One that reads "lots of ice" gets ignored after the
  first week, however good the model behind it is.
- **Stop arguing after the decision is made.** At departure the system
  should argue its route against the captain's plan. Once he has chosen,
  it needs to switch to micro-adjustments and things he might actually
  miss — a tool that keeps re-litigating a rejected route is a tool a crew
  turns off.
- **Turning an honest limitation into a daily output.** The system will
  never see a growler — smallest tracked Antarctic berg is roughly
  18,000× larger — and it says so. But it can forecast when the lookout
  is blind (visibility under 100 m, or seas over four feet by the growler
  spotting rule), which is a genuinely new, genuinely usable output built
  entirely from the limitation itself.
- **A tactical imagery request path.** The request costs a few bytes
  uplink; the image itself is what the link cannot afford today. Ship
  asks, shore fulfils into the next pack. It fits the bandwidth budget
  exactly and is the kind of small feature a working bridge crew actually
  reaches for, repeatedly.

**What breaks first if nothing is added:** a router that keeps arguing for
a rejected route; an advisory that never learns from the ship carrying it;
and any claim to being POLARIS-compliant, which needs an ice-*type* signal
this system does not yet output. Each of those has a named fix already on
the roadmap (§1) or the backlog — none of them is a surprise.
