# Master audit — PS-26059 Antarctic Navigation Decision Support System

**Date:** 7 September 2026 · **Branch:** `v3-compliance` · **Method:** original
master prompt → compressed six-stage bundle → repository, compared by reading and
diffing files, not by trusting documentation claims.

> **Operating rule, reinstated.** The master prompt's §49 SEMANTIC-LOSSLESS
> OPERATING INSTRUCTION was *lost* in compression (see §A). Its rule governs this
> audit and is restated here because it is the safeguard that would have caught
> every other gap: **when in doubt, assume it matters.** Do not delete
> information because it looks repetitive — first determine whether it adds a
> separate constraint.

Every number in this document carries a tag:
**Measured** (produced by running something, artifact exists) ·
**Sourced** (external citation) · **Derived** (computed from other numbers) ·
**Target** (specified, not achieved) · **Hypothesis** (untested).

---

## A. Lost requirements from the original master prompt

### A.1 What was compared

| Artefact | Identity |
|---|---|
| Original | `Claude_Code_Antarctic_Master_Prompt_SEMANTIC_LOSSLESS_UPDATED_v3.md`, **5,197 lines**, sha256 `5d4905c7…` |
| Compressed | the six-stage bundle `00_`–`06_` extracted from `Claude_Code_Antarctic_PROMPT_ORDERED.zip` |
| Claimed mapping | `01_COVERAGE_MANIFEST.md` |
| Repository | this branch |

The original **embeds its own verbatim source** at `# 48. SOURCE PRESERVATION /
AUDIT APPENDIX` (lines 2237–4573), so restructured-vs-original is diffable inside
a single file. The manifest states "Source lines: 5198"; the file has 5,197 — a
trivial off-by-one, recorded only because a manifest that miscounts its own
source is weak evidence for a losslessness claim.

### A.2 The real number

The original contains **78 top-level (`#`) content sections**: §1–§47 (47, no
gaps), the §48A umbrella plus its 32 subsections, §48, §49, and **28 unnumbered
tail sections that the manifest never lists at all**.

| Group | Count | Represented in the six bundle files? |
|---|---|---|
| §1–§47 | 47 | **All 47**, verbatim |
| §48A umbrella + 32 subsections | 1 (+32) | **All 32**, verbatim, duplicated across up to five files |
| §48 audit appendix | 1 | No — routed to `MASTER_SOURCE_UNTOUCHED.md`. **Disclosed** (manifest line 56); legitimate archival routing |
| §49 operating instruction | 1 | **No — lost entirely.** Zero hits for its distinctive language in all six files |
| 28 unlisted tail sections | 28 | 21 survived (mostly an undocumented dump into `02_`); **7 absent entirely** |

> **9 of 78 top-level sections are unrepresented. 1 is a disclosed archival
> routing. The other 8 are gaps the manifest never acknowledges.**

The manifest's headline claim — *"Every original top-level requirement section is
assigned to at least one execution stage"* — is **accurate for §1–§48A** and
**false for 8 sections it never accounts for**.

### A.3 Correcting a plausible misreading

The manifest routes four items to a stage called **"REVIEW"**, which is not one of
the six execution files: §25 Baymax, §26 Local LLM, §48A, §49. It is tempting to
read all four as lost. **Three of the four are not.** §25 and §26 survived
verbatim into `04_FUTURE_SCOPE_DEPLOYMENT_AND_STARTUP.md` (lines 102–128,
including the phrase "surreally simulated"), and §48A migrated so thoroughly that
individual clauses appear in three to five files at once. Only §49 was genuinely
dropped. The "REVIEW" tag is *misleading bookkeeping*, not *content loss* — a
distinction worth making, because the compression's actual fidelity is high and
overstating the damage would be its own kind of dishonesty.

### A.4 What was actually lost — and why it is the worst possible subset

Body fidelity is excellent. The six most operationally consequential sections
were diffed line-for-line and are **byte-for-byte identical**:

| Section | Original | Bundle | Loss |
|---|---|---|---|
| §4 END-TO-END USER WORKFLOW | 117–192 | `03_` 73–147 | **none** |
| §13 ALERTING PHILOSOPHY | 483–518 | `06_` 468–503 | **none** |
| §14 SENSOR / BRIDGE INTEGRATION | 520–553 | `06_` 506–539 | **none** |
| §23 OFFLINE / LOW-BANDWIDTH | 758–791 | `06_` 695–728 | **none** |
| §32 UI CONTENT STRUCTURE | 999–1071 | `03_` 185–257 **and** `06_` 798–870 | **none** (duplicated) |
| §45 ACCEPTANCE CHECKLIST | 1361–1415 | `05_` 142–196 | **none** |

What was lost is the *newest hardening material* — the opposite of what a
compression usually drops, and precisely the material a losslessness audit exists
to protect:

| # | Lost section | What it carried | Priority |
|---|---|---|---|
| 1 | **§49 SEMANTIC-LOSSLESS OPERATING INSTRUCTION** | The interpretive safeguard itself: "when in doubt, assume it matters"; "do not delete information merely because it is repetitive — determine whether it adds a separate constraint first" | **P0** |
| 2 | **CORE TECHNICAL MILESTONE BEFORE EXPANSION** (5112) | The end-to-end definition of done as a 13-stage pipeline, and *"Do not consider the project technically mature merely because the GUI is polished"* | **P0** |
| 3 | **IMPLEMENTATION QUALITY GATE** (5134) | An ordered 10-point pre-feature checkpoint: real data? provenance? freshness? uncertainty? baseline? validated? improves a decision? fails safely? captain understands it? architecturally compatible? — *"If the answer is no, fix the underlying capability before adding decorative complexity."* | **P0** |
| 4 | **FINAL IMPLEMENTATION DISCIPLINE** (4590) | *"Do NOT allow the project to become an 'Antarctic operating system' before the PS-26059 core is technically demonstrated"*, plus the litmus test "What real operational decision does this feature improve?" | **P1** |
| 5 | **MARPOL** citation (5028) | Named nowhere in §1–§48A; §48A.17 says only "marine pollution and waste requirements" generically | **P1** |
| 6 | **COMPETITIVE / OPERATIONAL BENCHMARK** (5070) | A 12-question adversarial framework materially more rigorous than §30's bullets — "What decision does it support?", "What can this system demonstrate that they cannot?" | **P1** |
| 7 | **NAVIGATION DATA QUALITY** (5037) | "chart update status", "source authority" as named concepts | P2 |
| 8 | **HUMAN FACTORS** (5054) | "trust calibration", "discoverability" — §48A.22 has automation/confirmation bias instead | P2 |

Two candidates were investigated and **downgraded** rather than reported:
"station-specific operating constraints" (5031) is a reordering of §6's "station
operational constraints", verbatim present in `06_` line 235; and "ROUTE VERSION"
as a provenance step already exists at §4 line 181, §11 line 388 and §47 line
1452. Reporting either as lost would have inflated the count.

### A.5 Reconstruction

All eight are reinstated as **enforceable artefacts rather than prose**, because a
requirement that lives only in a document is what got lost in the first place:

| Lost item | Reinstated as |
|---|---|
| §49 operating rule | The callout at the head of this audit |
| CORE TECHNICAL MILESTONE | `docs/QUALITY_GATE.md` §1 — the 13-stage pipeline as a checklist with per-stage status |
| IMPLEMENTATION QUALITY GATE | `docs/QUALITY_GATE.md` §2 — the 10 questions, applied per feature in the PR template |
| FINAL IMPLEMENTATION DISCIPLINE | `docs/QUALITY_GATE.md` §3 — scope-creep litmus test |
| MARPOL | `docs/research/STANDARDS_ALIGNMENT.md` — Annex I/IV/V and the Antarctic Special Area |
| Competitive benchmark | `docs/COMPETITIVE_ANALYSIS.md` — the 12 questions asked of each competitor |
| Navigation data quality | Chart-confidence indicator in the UI; CATZOC line in `docs/backlog.md` |
| Human factors | Trust-calibration and discoverability criteria in the alerting design |

---

## B. Broken / partial requirements

Distinct from §A: these survived compression intact and were then **implemented
incompletely, or claimed beyond what was built**.

| Requirement | Status | Evidence |
|---|---|---|
| §13 ALERTING PHILOSOPHY | **Absent from code entirely.** No P1/P2/P3 model, no alert object, none of the nine mandated fields | every `p1`/`p2` match in the repo is a haversine variable or a draw.io node id |
| §14 SENSOR / BRIDGE INTEGRATION | **Absent.** No NMEA parser, no AIS ingest, no GNSS reader. `execution_gate(live_sensors=False)` is hardcoded at its only call site | `isih/gates.py:285-293`, `isih/demo/decision_service.py:161` |
| §9 WEATHER / OCEAN | **Absent from the router.** PolarRoute's wave-added-resistance function exists in the library and is **never called** — dead code. The weather gate returns UNKNOWN unconditionally | `isih/gates.py:266-274`, `isih/ice_meshes.py:50` |
| §8 ICEBERG MODEL | **Half-built.** Drift *velocity* physics correct and tested (23/23); forward trajectory, uncertainty propagation, and comparison against the ship's future track — the back half of §8 — do not exist. Not wired to the route or the map | `models/iceberg/drift.py`; `isih/demo/decision_service.py:192` "held but not wired into the route" |
| §32 UI CONTENT STRUCTURE | **Two panels have no UI at all**: weather, hazard timeline. Route health shows `top_reasons[0]` only, not the mandated top three. Decision log captures the approval "why" but never renders it | `isih/demo/static/app.js:426-441, 548-567` |
| §45 Challengeability | **API-only.** `assumptions[]`, `constraints[]`, `hazards_considered[]`, `recommendation_answers()` are served by `/api/decision` and referenced by **zero** lines of front-end code | `isih/decision.py:234-300` vs `grep` of `static/*.js` |
| §45 Contingency triggers | `trigger_conditions` are **three hardcoded English sentences**, not data-derived thresholds, and appear only on the simulated `/future` page | `isih/demo/decision_service.py:213-217` |
| §18 VOYAGE PHASE MODEL | **Absent.** Not to be confused with the §4 passage workflow, which is built — different concept | no matches for the nine operational voyage phases |
| §19 MISSION STOPPAGE / SCIENCE | **Absent** | — |
| §21 ROUTE INTELLIGENCE / HISTORY | **Doc-only.** Researched in `research/RESEARCH_MATRIX.md` row 16; no incident database, no learning component | `docs/backlog.md:189` |
| §23 / §28 OFFLINE + PENDRIVE | **Partial.** Genuinely zero runtime network calls — but that is a property, not a feature. No pack format, no delta sync, no bandwidth-mode switching, no stale-data flag | `docs/ARCHITECTURE.md:87-89` "specified but NOT enforced" |
| §24 SHORE / EMERGENCY COMMS | **Absent.** No SOS, no station contact, no icebreaker roster | `docs/backlog.md:145` |
| §27 "REAL DATA ONLY" | **Held** — no synthetic data in the product today | — |
| §28 "CAPTAIN AUTHENTICATION" | **Distorted.** The sign-in screen states it is "identity, not access control, and there is no user store behind it." Any string is accepted | `isih/demo/static/index.html:31-33` |
| §42 MLflow | **Backfill only.** `mlflow_backfill.py` republishes numbers already in `ISIH_RESULTS.md`; no training run was ever observed by MLflow | `isih/mlflow_backfill.py:1-40` |
| 48A.4 POLARIS | **Deliberately not computed, and correctly so** — but the submitted deck claims otherwise (see §D.4) | `docs/research/POLARIS_APPLICABILITY.md:546` |
| 48A.16 SOURCE CONFLICT | **Absent.** Nothing in the codebase compares two sources and flags disagreement | — |
| 48A.19 BATHYMETRY / UKC / CATZOC | **Honestly absent.** `chart_gate()` looks for a bathymetry loader, finds none, returns UNKNOWN rather than a false PASS. This is the correct behaviour, not a defect | `isih/gates.py:93-132` |
| 48A.20 RESCUE CONSEQUENCE | **Doc-only.** SAR-remoteness research exists (COMNAP 5–6 day best-case help arrival); no code | `research/RESEARCH_MATRIX.md` row 11 |
| 48A.21 ICEBREAKER / ESCORT | **Doc-only** | `research/POLARIS_APPLICABILITY.md:115` |

---

## C. Referenced-document findings

**C.1 The embedded verbatim source (§48, lines 2237–4573).** The master carries
its own unedited original inside itself. This is the single most useful artefact
in the whole set: it makes the losslessness claim *testable* rather than
assertable, and it is what allowed §A to be settled by diff instead of by
argument. It should be preserved in any future restructure.

**C.2 `MASTER_SOURCE_UNTOUCHED.md`.** Byte-identical to the master (md5
`a9e369861cb2e2f819c0abeed20abf1d` for both). It is a copy, not a second source;
nothing depends on it that does not depend on the master.

**C.3 `01_COVERAGE_MANIFEST.md`.** Its mapping is the claim §A tests. It is
correct for §1–§48A, silent on 28 tail sections, and uses a "REVIEW" destination
that does not exist as a stage. Its execution-order rationale — research →
architecture → UI → future scope → validation → demo last, "so that it is rebuilt
using the completed research" — is sound and was followed.

**C.4 The scanned SIH guidance — unavailable, stated plainly.**
`/mnt/data/Scanned_20260907-2144.pdf` **does not exist in this environment.** It
was not read. Its substance is, however, quoted at length in the instructions
that commissioned this audit — underserved segments, hyper-specific scope,
feasibility-first development, data-backed gaps, root-cause analysis, precise user
mapping, pain-point prioritisation, beneficiary feedback, MVP discipline,
experimentation, measurable impact, judge psychology, presentation discipline, and
a list of common SIH failure modes. Those **principles are applied throughout this
document**; no fact about Antarctica is sourced from it, and its illustrative
figures from unrelated domains are deliberately not reused. Recording this
distinction is itself an application of the rule the audit is written under: a
document that was not opened must not be cited as if it had been.

**C.5 The submitted presentation.** `Antarctic Navigation Decision Support System
(2).pdf`, 6 pages, Canva, 1440×810. Audited in §D.4 and §AT.

---

## D. Current repository reality

Three buckets. Nothing is listed as built unless a file backs it.

### D.1 Demonstrated today
Real NSIDC sea-ice raster with QA toggle and day slider · the §4 passage workflow
sign-in → command centre → voyage → mission → route → waypoints → review →
approved → active/workspace, with out-of-order transitions rejected 409 · route
health with nine gates · A/B/C alternative corridors · two-vessel comparison ·
decision log with versioning and a `supersedes` chain · master's approval ·
ASPA/ASMA protected areas · Natural Earth coastline · own-ship computed position
card · a panel stating what the prototype can and cannot claim · a `/future`
screen carrying Baymax and a templated assistant, both badged simulated.

### D.2 Implemented but not demonstrated
Iceberg catalogue + WDE17 drift velocity (`models/iceberg/`) · the decision
object's `recommendation_answers()`, `assumptions[]`, `constraints[]`,
`hazards_considered[]` · the approval "why" note · the MLflow backfill.

### D.3 Absent
Alerting · sensors/NMEA/AIS · weather and waves in the router · voyage phase model
· mission stoppage · route intelligence/history · shore and emergency comms ·
icebreaker/escort · rescue consequence · bathymetry/UKC/CATZOC · offline pack and
delta sync · iceberg forward trajectory and uncertainty vs own-ship route.

### D.4 The submitted deck contradicts the system

This is the highest-risk finding in the audit, because the deck — not the repo —
is what judges read first.

| Deck claim (slide) | Verdict | What the repo says |
|---|---|---|
| "Replaced the initial 80 % ice threshold with the POLARIS risk-index framework" (6) | **CONTRADICTED** | `isih/alternatives.py:77` `"max_ice_conc": 80, # same assumption, deliberately`. `POLARIS_APPLICABILITY.md:546`: "this project cannot compute a real POLARIS RIO today." `RUN_OF_SHOW.md:194` lists "Any POLARIS number for this vessel" under **Do not say** |
| "A proven physics model predicts the drift of **live** icebergs, including within our shipping corridor" (2) | **CONTRADICTED** | Physics is real and tested; it has never been fed real forcing, is wired to nothing, and **no trajectory error has ever been measured**. `decision_service.py:192`: "held but not wired into the route" |
| "re-plans automatically as new data arrives" (2) | **NOT BUILT** | `RUN_OF_SHOW.md:182`: "there is no re-plan button." Worse, `route_regret.py` measured daily re-planning as **slower** than one global optimisation |
| "1,096 daily satellite files processed with zero failures, harvested automatically every day" (3) | **CONTRADICTED** | Merges two different pipelines. 1,096 is a one-time NSIDC bulk download; the daily cron has ~7 files and **failed once** (commit `f42972a`) |
| "Compression cuts each daily file from 42.6 MB to 5.0 MB, 8.4× smaller" (3) | **NO MATCHING RUN** | Production logs show 8.2–8.3× / 5.1–5.2 MB. The 8.5× figure is a one-off docstring measurement |
| "A full data pack is 76 KB" (3) | **MISCHARACTERISED** | 76 KB is an 824-cell sample box. The full corridor mesh is **estimated** 0.5–1 MB and explicitly not measured |
| "improving accuracy by 18.5 % at 1 day and 30.6 % at 7 days" (2, 3) | **MEASURED, caveat dropped** | `ISIH_RESULTS.md:88-91`: "an **upper bound on forecast skill, not a measurement of it**". The 7-day figure is the largest gain *and* the most contaminated |
| "already compute our 8.6-day route" (3) | **MEASURED, caveat dropped** | Ideal steaming time only. `ISIH_RESULTS.md:342`: "Do not present it as a predicted voyage duration" — a real ISEA voyage is 2–3 weeks |

**The repository's own guard rails missed three of these.** `RUN_OF_SHOW.md`'s
"Do not say" list and `RELEASE_AUDIT.md`'s "claims that must not be made" do not
cover automatic re-planning, the 1,096-files framing, or the compression and pack
figures. So this is not simply a deck that drifted from a disciplined repo — the
discipline had a hole in it. Both are repaired in §AT and in the corrections
register.

---

## E. Exact problem

**Tag legend, used through E–M.** `[M]` measured in this repository (file cited) · `[S]` sourced from an external document already cited in `docs/` · `[D]` derived by arithmetic from M/S values · `[T]` design target, not yet achieved · `[H]` hypothesis — unverified, a validation gap.

### E.1 The causal chain

**Root cause — the delivery point is not a port.** Cargo for Bharati and Maitri is craned overboard onto fast ice or an ice-shelf edge and hauled inland `[S: NCPOR tender NCPOR/14(102)/21]`. Whether that edge is workable on a given day is set by wind-driven ice motion on a one-to-three-day timescale: Prydz Bay fast ice breaks out between mid-December and late January with passing cyclones `[S: NAVIGATION_RESEARCH.md §7.5]`, and free drift at 30 m/s is ≈52 km/day `[D]`. Measured on real NSIDC ice, December 2019, at the vessel's 80% working limit: **Bharati's own cell was closed 23 of 31 days; the approach 100 km north was open 31 of 31** `[M: isih/figures/destination_window.json]`. The 5,800 km ocean crossing carries **mean 6% ice** `[M: isih/figures/route_regret.json]`. The whole voyage's uncertainty is compressed into the last 100 km and into a day-to-day clock.

**Information gap — the state of that edge on arrival day is not knowable when the commitment is made.**
- The only operational Antarctic-covering ice forecast reaches **D+9** `[M]`. At the ship's AIS-observed average of 8.6 kn the transit is ≈15.2 days, so at departure **41% of the route (2,372 km) — the part that matters — lies beyond any forecast** `[D]`. At the 16.4 kn service speed the forecast would just cover it; the ship does not sail at service speed `[M]`.
- The observation is coarsest where the decision lives. The 25 km grid is finer than the 70×45 km SSMIS footprint that produces it; the passive-microwave ice edge can be 25–50 km off `[S]`. The CDR's land-spillover filter writes suppressed coastal cells as **0.0% ice on 100% of days**, ~118 cells/day, touching the 200 km Bharati box on **43.2% of days**; **four of the eight** December-2019 days on which Bharati looked reachable were that artifact `[M: isih/figures/ice_quality_audit.json]`.
- No ice type or thickness (POLARIS needs eleven stage-of-development classes; the best free Antarctic chart resolves five) `[S]`; no compression product exists anywhere for the Antarctic `[S]`; no observational Antarctic drift field in December–March (OSI-405-d runs 1 Apr–31 Oct only) `[S]`; no visibility forecast in any product in the stack `[S-absence]`; icebergs tracked weekly and only ≥18.5 km `[S]`.
- The ship's own limit is unknown in the terms the data provide. No ice-class system anywhere indexes ice *concentration* `[S]`; the 80% limit is an assumption; and below a 45% assumed limit **no route to Bharati exists at all** `[M: isih/figures/alternatives.json]`.

**Decision difficulty.** One master, exercising SOLAS V/34 discretion, integrates sources arriving in different projections, formats and latencies, with no forecast for the destination, against an asymmetric loss (a needless detour costs hours; besetment costs months), at commitment points that cannot be reversed. Two things make it worse than a hard forecasting problem: the honest system output on most days is "hold course", which naive daily re-planning turns into whipsaw; and the single most consequential input — must the ship reach the station, or is the approach acceptable — **is not the master's to decide**. That one field flips route health on **23 of 31 days** `[M]`.

**Operational failure**, ascending: waiting at the ice edge; partial resupply or helicopter fly-off from the edge (Mawson 2021: the ship got no closer than ~30 km); besetment (MV *Magdalena Oldendorff*, supporting the 20th Indian expedition, beset June 2002 near Novolazarevskaya for ~5.5 months; *Akademik Shokalskiy* 2013–14, freed by a wind shift, not by icebreaking) `[S]`. Help is 5–6 sailing days away in COMNAP's best case; Shokalskiy took 8–9 days with three nations responding `[S]`.

**Financial and safety consequence.** The charter is `day rate × 100 days` plus fixed terms, so **one lost day ≈ 1% of the season's hire** `[D]`; the day rate itself is unknown `[gap]`. Maitri II — ₹2,000 crore, completion January 2029 `[S, secondary]` — means several consecutive seasons of heavy cargo across a coast the repo measured as shut most December days. Shokalskiy's rescue was reported at AUD 2.4 M plus >AUD 0.9 M for the diverted resupply `[S]`. Frequency: >25 Southern Ocean incidents needing emergency response 2006–2019, about two a year continent-wide `[S]` — serious and rare, which is why the insurance buyer is weak `[H]`.

### E.2 The nine questions

| Question | Answer |
|---|---|
| Real operational problem | Not "is the Southern Ocean dangerous" but *will the last 100 km be open on the day we arrive, how long will it stay open, and if it shuts do we wait or switch to air-and-barge?* `[M]` |
| Who experiences it | The master at the edge; the NCPOR expedition leader whose cargo and personnel programme depends on the window; NCPOR logistics ashore who pay by the day; station leaders waiting for fuel and relief |
| When dangerous or expensive | Expensive from the first held day (≈1%/day `[D]`). Dangerous at the fast-ice edge when drift sets into it at an angle — AARI's own "most dangerous case for shipping", and exactly the offloading geometry `[S]` — and in blowing snow, when the growler lookout and radar degrade together `[S]` |
| Decisions to be made | Departure date · mission policy (station vs approach) · Southern Ocean track (little to decide at 6% ice) · approach-or-hold at the edge · go/no-go on the last 100 km (24–72 h out) · cargo by crane, barge or helicopter · iceberg CPA · when to leave |
| Who makes them | Master: navigation and vessel safety (SOLAS V/34). Expedition leader/NCPOR: mission policy, cargo sequence, air and barge ops. NCPOR/MoES: season, charter, deadline. The owner holds the certificate and PWOM that define what the ship may do |
| Missing at decision time | At departure: any forecast for the arrival day `[D]`. At sea: ice type, compression, summer drift, visibility, bathymetry confidence (IBCSO v2 is 23.79% direct measurement south of 50°S), and the ship's own certificated limit |
| When the decision is wrong | Wrong-optimistic: besetment, hull damage, days-long SAR. Wrong-pessimistic: hours to days of hire and a partial resupply. These differ by orders of magnitude, so a system tuned for accuracy trades them one-for-one and is wrong to |
| Lose internet / fresh data | E.3 |
| Download fails / stale / wrong | E.4 |

### E.3 Losing the link

Geostationary VSAT does not reliably cover south of ~70°S; polar maritime comms are Iridium-class — Certus peaks around 704 kbps and is often far less `[S]`. The charter bills communications per actual `[S]`. **"Offline" is the normal case on the decision-relevant part of the corridor**, and every byte has a price the charterer sees.

A forecast field carries a lead time *and* an age, and they add: "a 3-day-lead field from a 4-day-old cycle is a 7-day-lead field wearing a disguise" `[S: FORECAST_HORIZONS.md §0]`. On the held-out melt-season test, persistence error rises from 0.0570 at 1 day to 0.1395 at 7 days — a week-old picture is ~2.5× worse `[M]`. One 25-hour Maitri blizzard at 52 kt moves the ice field ~30 km `[D]`.

Designed `[T]`: shore/vessel split with the whole routing engine aboard (~9 s on a laptop CPU `[M]`); a nightly voyage pack (representative vessel-modelled mesh block 76 KB gzip `[M]`; full corridor 0.5–1 MB `[D, unmeasured]`); model weights (~60 MB) by USB at Cape Town, never over Iridium; a four-rung degradation ladder — corrected forecast → raw CMEMS → persistence from newest observation → climatology — each rung announced, with the corridor widening and decision points moving earlier as rungs are lost.

Built `[M]`: the demo makes no external call at all, test-enforced. **The rest is absent** — no pack, no `age_hours`, no re-plan control, no climatology floor. **So today, losing the link changes nothing on the screen, which means the screen cannot yet tell the operator its picture is ageing.** That is the honest state and the cheapest gap on this list.

### E.4 The download fails, or what arrives is stale or wrong

Every mode below has happened in this repository or is documented in the product's own quality notes. None is hypothetical.

| Mode | Evidence | Direction of harm |
|---|---|---|
| **Late** | CMEMS guarantees the bulletin only "by 12:00 UTC". The harvest names files from the wall clock, so a run firing before delivery archives bulletin D−1 as D, and the already-have guard then blocks the correct capture all day `[M]` | Silent: a stale field wearing today's date |
| **Missing** | A missed bulletin is unrecoverable — CMEMS overwrites each with the next `[M]`; nothing alerts on a miss; the first harvest run failed at the Copernicus login `[M: 13 runs, 1 failed]`; the harvest box is clipped on all four sides relative to the training corridor `[M]` | Gap, or an unnoticed switch to an older product |
| **Stale by construction** | AARI–NIC–NMI Antarctic charts: specified weekly, observed roughly fortnightly, posted 1–3 days late `[M]`; USNIC weekly; BYU archive ~16 months behind `[M]`; Sentinel-1 over Prydz Bay: 31 passes in 30 days, median gap 23.9 h, worst 47.7 h `[M]` | Decision made on last fortnight's ice |
| **Wrong, unsafe direction** | Coastal spillover cells written as 0.0% `[M]`; CMEMS QUID: SIC "underestimated in the Antarctic during austral summer" — the resupply season `[S]`; ERA5 under-reads wind by −3.89 m/s above 20 m/s `[S]`; CMEMS surface-current regression slope ≈0.5, so berg advection from it is biased **short** `[S]`; weather filters zero 27% of pixels at a true 15% SIC `[S]` | Route through ice that is there |
| **Wrong, over-cautious** | Land emissivity contaminates retrievals tens of km offshore (false ice) `[S]`; our own QA fix returns 30–36% where neighbours read 80–95% — it removed a confident wrong answer without producing a right one `[M]` | Unnecessary detours; erosion of trust |
| **Self-contradictory** | The CDR's QA flag contradicts its own concentration field on the same day (raw 0.0% vs quality-checked 30.7% at Bharati, 1 Dec 2019); **both readings are served** `[M]` | Exposes the problem rather than hiding it — correct |
| **Temporally inconsistent** | A September-2026 iceberg catalogue over December-2019 ice; the demo refuses to draw them together `[M]` | Prevented by rule |
| **Wrong about the ship** | `force_limit` is RRS Sir David Attenborough's; ice class single-source; concentration limit invented; draft 9.0 m found but not wired `[M/S]` | Every derated speed and the reachability cliff rest on borrowed numbers |

**The governing rule, built:** a gate with no data behind it returns UNKNOWN, and UNKNOWN caps route health at DEGRADED — missing evidence is a reason to be less confident, never a reason to be silent or to pass `[M: isih/decision.py, isih/gates.py]`. The demo refuses to start if any day's satellite file is missing rather than rendering a gap as open water `[M]`.

---

## F. Root cause — why the gap exists

Seven layers, each necessary. "Satellites are coarse" is the second.

1. **Physics puts the hazard below every observable scale.** Compression — the thing that traps ships (9 of 10 Northern Sea Route losses 1922–1990) — is a sub-grid pressure field with no observable at any resolution; a ship is 10⁻³ of a cell `[S]`. Ice strength is exponential in concentration (Hibler, C = 20), so a 5-point concentration error is a 2.7× strength error and a 10-point error 7.4× `[D]`. The decisive object at the delivery point is the fast-ice edge, which passive microwave misplaces even at 6.25 km `[S]`.

2. **The observing system was built for climate records, not navigation.** The CDR is a 48-year homogeneous concentration series; its `valid_range` accepts a 0.0 written by a coastal filter, and its producers state that shipped per-pixel uncertainty *excludes* melt-pond, thin-ice and weather-filter effects `[S: Lavergne et al. 2019]`. Thirty published algorithms disagree by ~10× at the ice edge (SD 2.8–28.8% at 15% SIC; Southern Hemisphere worse) `[S: Ivanova et al. 2015]`. Human ice analysts agree exactly only 39% of the time `[S: Cheng et al. 2020]`. **There is no "the" sea-ice concentration.**

3. **There is no Antarctic ice forecasting system.** The Arctic has neXtSIM; Antarctica is served by the global physics run with ice bundled in, to D+9 `[S]`. Half of SIPN South seasonal forecasts fail to beat climatology `[S]`; Antarctic subseasonal ice-edge skill is ~30% below the Arctic's and worst in East Antarctica — this corridor `[S: Zampieri et al. 2019]`.

4. **The regulatory frameworks are indexed on quantities the data do not carry.** POLARIS RIO is indexed by WMO stage of development; it contains no word for pressure, compression, ridge or drift `[S: MSC.1/Circ.1519]`; its IMO-mandated review was due ~2021 and has not happened `[S]`; it is explicitly "not a Go/No Go tool" `[S]`. This hull's pre-1999 Russian Register notation has no row in POLARIS and no entry in Canada's equivalence schedule, and the Polar Code makes equivalency a per-ship, owner-initiated, flag-approved assessment **with no lookup table by design** `[S]`. The three documents that would settle it — Polar Ship Certificate, current class certificate, PWOM — are not public. **So the master's certificated envelope and the satellite's concentration field cannot be joined without an inference nobody is entitled to make.**

5. **Nobody owns the integration, and the Indian side owns least.** NCPOR's tender requires the vessel to carry "ice-information receiving equipment" and specifies nothing on the other end `[S]`. NCPOR's portals hold station observations and a static archive — no ice forecast, no routing, no live tracking `[M]`. INCOIS ship-route advisories stop at 30–45°S, north of the ice `[M]`; IMD's 3 km Polar-WRF for Maitri and Bharati is charts only `[S]`; ISRO's SCATSAT-1 Antarctic ice product stopped in May 2019 while the satellite ran to 2021 `[S]`. No published ice-routing SOP exists for NCPOR, AAD, BAS or AWI `[S-absence]`. Fragments arrive in EPSG:3031/3412 rasters, SIGRID-3 shapefiles, GRIB2, NetCDF and PNG meteograms, at latencies from 5 h to a fortnight — **and the person who fuses them is on watch.**

6. **The loss is asymmetric, so the rational bias is to wait — and waiting is the cost.** Because the errors differ by orders of magnitude, the safe policy is conservatism, which converts risk into held days at ≈1%/day `[D]`. The measured null result confirms where the money is *not*: on the one departure date tested, planning the crossing on departure-day ice cost 0.03 days, and daily re-planning was **slower** (9.00 vs 8.61 d) `[M: route_regret.json]`. **There is nothing to optimise in the crossing.** The value is in deciding earlier which day to arrive and what to do if the edge is shut.

7. **One voyage a year, and the master's climatology is degrading.** No besetting incident for any Indian-flagged or Indian-chartered vessel is documented anywhere public `[S-absence]`. There is no institutional learning loop. Meanwhile Antarctic sea ice has sat in a post-2016 low-extent state with record lows in 2022, 2023 and 2025 and "different seasonal persistence characteristics" — a regime in which "climatology is, by definition, not meaningful" `[S]`. Experience-based heuristics, which is what a master without a forecast actually uses, are being invalidated by the environment.

An eighth, internal: **our own tool reproduces the resolution problem it describes.** The routing mesh cell containing Bharati spans 1.25°, roughly **139 × 49 km — larger than the "last 100 km" the pitch calls the whole problem** `[M]`. Tightening the ice limit from 60% to 55% *raises* the worst 25 km pixel sampled along the route from 74% to 91%, because the router optimises 5° cell means `[M]`. Stated here so it is not discovered by a judge.

---

## G. User mapping

**No beneficiary interviews, observations or usability sessions exist. No master, navigator, expedition leader or NCPOR officer has ever seen this system's output** `[M-absence]`. Everything below is derived from the tender, press releases, the Polar Code and the vessel record, and is a hypothesis about people until validated.

### G.1 Who decides what

| Decision | Master | Expedition leader (aboard) | NCPOR logistics (shore) | MoES | Owner |
|---|---|---|---|---|---|
| Departure date, season, charter | consulted | consulted | **decides** | approves | contracts |
| Mission policy: station vs approach | — | **decides** | sets | — | — |
| Track, speed, approach-or-hold | **decides** (SOLAS V/34) | advises | — | — | bound by PWOM |
| Crane vs barge vs helicopter | jointly | **decides** | — | — | provides assets |
| Whether the ship may enter an ice regime | executes | — | — | — | **holds** certificate/PWOM |
| Pays for waiting days | — | — | **pays** | funds | is paid |

Derived incentive structure `[D]`: under a time charter the owner is paid by the day regardless and bears hull risk; the charterer pays for every held day and bears mission risk; the master answers to the owner for the ship and to the charterer for the mission. **A tool whose main output is a legible "wait until day N, because…" reduces friction between two parties whose incentives diverge at exactly the moment of the hold.** Inference, not observation `[H]`.

### G.2 Personas

**Primary user — the Master.** Objective: deliver ship and cargo without damage. Workflow: passage plan under A.893(21) appraisal → planning → execution → monitoring; at the edge, helicopter reconnaissance to ~100 nmi and yesterday's observed ice `[S]`. Pain: **he can see today's ice and nothing about the day he needs.** Workaround: experience, recon, conservatism. Authority: absolute on navigation. Required: observed ice with age, expected change over 1–3 days, iceberg CPA, **where the tool is blind** (growlers, compression), and what his certificate permits — in ice-navigator vocabulary (egg code), which the product does not yet speak `[M-absence]`. Adoption: unknown `[H]`. Specific risks: a Russian-speaking bridge and an English product; a crew that has sailed this hull into this coast for years and will discount a tool that argues with a route it has already rejected; and IMO's own text that decision support is not go/no-go. **Note honestly: this crew is not the party with the least ice expertise; the unserved decision is the charterer's** `[H]`.

**Decision-maker for the mission — the NCPOR expedition leader aboard.** Objective: land cargo, fuel and personnel inside a 100 ± 30-day charter. Pain: the single field that flips route health on 23 of 31 days — station-required vs approach-acceptable — **is his, and today nothing computes its consequence for him** `[M]`. Required: per-day probability the offload point is workable, an ETA distribution not a point, what the fallback costs. Adoption `[H]`; plausibly the most receptive, because the tool answers his question directly.

**Economic buyer — NCPOR logistics.** Objective: one voyage, on time, within contract. Pain: **buys the receiver, owns no content; prices scheduling risk at zero** `[S]`. Authority: charter, season, budget; procurement via GeM, where a DPIIT startup is exempt from turnover, experience and EMD requirements `[S]`. Adoption: institutional and slow; the precedent that MoES already funds a free ship-routing advisory (INCOIS OSF since 2013) says the money is a **service contract, not a licence** `[S]`. Single point of failure: if NCPOR declines there is no substitute customer.

**Funder — MoES.** Maitri II by 2029; indigenous polar research vessel MoU June 2025 (design-preparatory only); Arctic policy 2022 and a 2027 Northern Sea Route pilot `[S]`.

**Certificate holder — the owner.** Holds the three documents that would settle the ship's real envelope. Willingness to share `[H]`, and a real dependency: without them the capability gate stays UNKNOWN.

**Beneficiaries with no seat at the decision** — station leaders at Bharati and Maitri; helicopter and barge crews (visibility ≤100 m in blizzard, and no forecast exists for it `[S]`); expedition passengers. Their failure consequence is the human one; their information need is a date.

**Secondary stakeholders.** NCPOR's sea-ice research group (the Stage-1 user and the door in); IMD; INCOIS (global WW3 to 80°S; the 2025 glider deployed from this very ship); ISRO/MOSDAC (EOS-06 SCAT ice, 12.5 km daily since June 2024); **MRCC Cape Town, whose gazetted region runs along 75°E — Bharati at 76.2°E sits ~50 km outside it** `[S; Australian boundary UNVERIFIED]`; **Russia's Progress station 5–10 km from Bharati with an Il-76-capable airfield — the nearest capable asset is not Indian** `[S]`; COMNAP peers (55 vessels, 24 countries).

**Validation gaps to close before any persona claim goes on a slide:** what ice product the bridge receives today and from whom; who at NCPOR sets destination policy and when; bridge language and display; whether the master would accept a "hold" recommendation from shore; whether the owner will release the three documents.

---

## H. Underserved segment

| Segment | Connectivity | Onboard ice expertise | Window rigidity | Institutional buyer | Incumbent coverage |
|---|---|---|---|---|---|
| National-programme research vessels | Iridium-class | High — own ice desks | Seasonal, multi-voyage | Yes | **Served** — AWI/AAD pay for IcySea; Polarstern has MapViewer |
| **Chartered ice-class cargo on national resupply** | Iridium-class, **metered to the charterer** | High on the bridge, **none on the programme side** | **One voyage, 100 ± 30 days, no second sailing** | Yes — recurring tender, GeM startup exemptions | **Unserved** — the tender buys a receiver with nothing behind it |
| Expedition cruise | Some VSAT north of 70°S | Contracted ice pilots | Flexible itineraries | Commercial | Served (Ponant, Hapag-Lloyd, Lindblad buy IcySea) |
| Krill / toothfish | Commercial | High | Quota race | Commercial, foreign | Partly served; not reachable from India |

**The first customer: the national-programme resupply voyage run on a chartered ice-class cargo vessel — India's first.** It is the intersection of four criteria: the worst connectivity *and* the only party billed for it; the most rigid window (one sailing, a contractual `day rate × 100 days`, and for 2026–29 a station build with a hard deadline); an institutional buyer that already tenders for this and has written "ice-information receiving equipment" into the specification; and — decisively — **the unserved decision is not the master's steering but the charterer's window decision**, for which no tool exists in the Indian programme at all.

Two honest qualifications. **The nearest neighbour on this coast is already served:** CHINARE runs a fast-ice prediction system (FIPS, 0.125°, 10-day) over 68.4–69.75°S / 73.5–79°E — precisely the Bharati approach — and SOIPS was run at Zhongshan, 5 km from Bharati, using convergence rate at 24/48/72 h for the go/no-go `[S]`. **The gap is India's, not the coast's.** And the segment is one hull deep in India and perhaps six to ten reachable programmes abroad `[H]`; the realistic ceiling is a specialist company of eight to twelve people `[D]`. That is a good business and a bad venture story, and saying so is part of the case.

---

## I. User journey

Ten stages: available `[A]`, missing `[X]`, decision `[Dn]`, interaction `[U]`, system `[Sys]`, failure `[F]`.

**1. Voyage planning (weeks–months out).** [A] Charter window and box; 1,096 daily ice files that could be a climatology but are never surfaced to a planner `[M-absence]`. [X] Any forecast; a departure-date sweep (built, run for one date). [Dn] Departure date, cargo priority, mission policy. [Sys] Design: climatological probability the offload point is workable in the arrival window, with interquartile range — the *correct* claim at this tier `[T]`. [F] Treating "23 of 31" (one December) as a general rate `[M, n=1 season]`.

**2. Departure (Cape Town).** [A] GFS/GFS-Wave to D+5 routed; CMEMS to D+9; observed CDR ice; USNIC weekly bergs; 148 protected-area polygons, 33 in corridor, **zero marine** `[M]`. [X] Ice at Bharati on arrival day; bathymetry (GEBCO not downloaded, `min_depth: 20` inert `[M]`); the ship's certificated limit. [Sys] Nine gates, three evaluable, health capped at DEGRADED; corridors A/B/C precomputed. [F] A point ETA (8.6 d) mistaken for a voyage duration — **it is ideal steaming only** `[M]`.

**3. Environmental update (daily, at sea).** [A] By design a nightly pack <1 MB `[T]`; by measurement a 5 MB/day compressed corridor subset ashore `[M]`. [X] The link south of 70°S; an age field; the pack machinery. [Sys] Design: delta sync, rollback, imputation flags that widen the routed bound. [F] Bulletin D−1 archived as D `[M]`; a missed bulletin lost forever `[M]`; **today, nothing tells the user any of this**.

**4. Hazard detection.** [A] SIC with QA flags; 33 USNIC bergs, 15 in the corridor band, largest D15A 3,037 km² — ~390 km from Bharati, and "in corridor" is a longitude test `[M]`. [X] **Growlers (5 m vs 18.5 km tracked: 3.5 orders of magnitude** `[S]`); leads narrower than a cell; compression; the fast-ice edge; visibility. [Sys] Design: 72 h berg projection with a measured p90 exclusion radius `[T]`; today **no berg has been stepped forward and no trajectory error measured** `[M]`. [F] The >90% SIC regime where a berg locks into the pack, which the drift model has no term for — the regime at the Bharati approach `[S]`.

**5. Route evaluation.** [A] Worst ice against the working limit, with a MARGINAL band of 7.4 points derived from the CDR's own per-pixel stdev in the 70–90% band `[M]`. [X] Six gates UNKNOWN, each naming its dataset. [Sys] Health derived, never scored; binding gate carried as the reason. [F] The 5° mean vs 25 km pixel seam (74% → 91%) `[M]`.

**6. Decision.** [X] The τ rule (manoeuvre cost + conformal width + incumbency margin) that prevents whipsaw — designed, not built `[T]`. [Sys] Versioned, attributed, never overwrites. [F] A change proposed on new data rather than a changed assumption (the gate digest prevents this `[M]`).

**7. Execution.** [A] Own-ship position computed from the plan's per-leg transit times — **not a GPS fix; cross-track error is zero by construction** `[M]`. [X] Any bridge sensor; NMEA/IEC 61162; ECDIS overlay — no design exists `[M-absence]`. [F] The tool cannot tell that the ship is not where the plan says.

**8. Change (heads-up).** [A] Divergence from the standing approval names the gate that flipped ("logistics: PASS → FAIL", 5 December) `[M]`. [X] Alerting of any kind; a re-plan cadence (no regulator sets one; CIS uses 12 h for a closing lead `[S]`). [Sys] A transition only when the gate digest changes.

**9. Replanning.** [A] Decision workspace: keep / edit / alternative, preview recomputed for the current day with an arrival column. [X] Live re-plan; the D+7 and D+3 re-decision gates `[T]`; **time-expanded routing — PolarRoute has no time dimension, so a static router cannot consume a forecast** `[M]`. [F] Whipsaw; the DAILY arm being slower than STATIC on the one date tested `[M]`.

**10. Post-voyage review.** [A] The decision log — in memory, lost on restart, deliberately for a demo `[M]`. [X] Any incident database; a written post-season verification report — the Stage-2 exit condition. [F] No learning loop across n = 1 voyage per year.

### The single highest-value pain point

**The approach-or-hold decision for the last 100 km — taken 3–7 days before arrival from near the ice, and re-taken at 24–72 h — with its consequence for cargo mode and for the charterer's mission policy.** It is where the voyage's uncertainty is concentrated (23/31 closed vs 0/31 `[M]`), where forecast skill actually exists (SOIPS RMSE 0.16 at 72 h; our own +18.5–24.9% over persistence inside 3 days), where the Chinese programme has already built a tool for the same coast and India has none, and where each wrong day costs ≈1% of the season. **The crossing, which every existing routing product optimises, is not the problem** `[M: null result]`.

---

## J. Pain-point prioritisation

Scores 1–5 on severity (S), frequency (F), consequence (C), feasibility now (Fe). All `[D]` judgements on the cited evidence.

| # | Pain point | S | F | C | Fe | Product | Reasoning |
|---|---|---|---|---|---|---|---|
| 1 | Coastal data integrity and forecast-age honesty | 5 | 5 | 4 | 5 | **500** | Fires on 100% of days, 43.2% in the Bharati box `[M]`; age fields are a day's work |
| 2 | **The last-100-km window decision** | 4 | 5 | 4 | 4 | **320** | 74% closure `[M]`; ≈1%/day `[D]`; skill measured inside 7 days |
| 3 | Contingency corridors + a decision record naming why | 3 | 5 | 3 | 5 | **225** | Built; the third corridor's value is proving no route exists ≤45% `[M]` |
| 4 | Link loss and graceful degradation | 3 | 5 | 3 | 4 | **180** | Normal south of 70°S; single-tier today |
| 5 | The ship's real envelope | 4 | 5 | 4 | 2 | **160** | Reachability has a cliff between 50% and 45% on an assumed number `[M]` |
| 6 | Tracked-iceberg CPA (≥18.5 km, ≤72 h) | 4 | 3 | 4 | 3 | **144** | Physics tested; needs a current field the QUID says under-reads by half |
| 7 | SAR remoteness and places of refuge | 5 | 1 | 5 | 5 | **125** | Static table, zero bandwidth |
| 8 | Ice-type/thickness interpretation | 3 | 5 | 3 | 2 | **90** | Forced by regulation; blocks three things |
| 9 | Open-ocean sea state and fuel | 2 | 5 | 2 | 3 | **60** | A PS deliverable, but the regret null result says there is nothing to optimise |
| 10 | **Besetment / compression at the fast-ice edge** | 5 | 2 | 5 | 1 | **50** | The deadliest item and the only one with no intervention available anywhere |
| 11 | Visibility for helicopter and barge ops | 4 | 2 | 3 | 1 | **24** | No forecast source exists |

**How to read this.** Feasibility is a multiplier on purpose: it pushes cheap enabling work up and unsolvable hazards down. That is right for a **build order** and wrong for a **risk register** — #10 carries the largest expected harm and scores last. The two must be presented together.

- **Primary:** #2, with #1 as its non-negotiable precondition.
- **Secondary:** #3, #4, #5, #6, #7, and the honest minimum of #9.
- **Future / white space:** #10, #8, #11.

---

## K. Existing solutions

Six alternatives, each as *X solves A well, but under condition B, limitation C appears*, with where it is **better than us** stated first.

**1. IcySea (Drift+Noise, AWI spin-off, 7 core staff, since 2014).** Better than us at everything about delivery: near-real-time imagery within ~1 h of recording, Iridium-tested, offline browser cache, click-a-point drift forecast, and real customers — RV Polarstern and RSV Nuyina. Solves *"what does the ice look like right now, on a bad link"* well. Under the condition that the question is *"can this named ship reach this named station on this date, and what does waiting cost"*, the limitation is that it is an ice-information app: no vessel model, no destination window, no decision record. **We have not tested it and do not claim it is inaccurate.**

**2. PolarView / Bremen AMSR2.** Better than us: free, established, the source many operators open first; the Australian programme reports crews found them "easy to use" and "accurately reflected ice conditions encountered". Under the condition of a station approach, AMSR2 at 6.25 km **overestimates the Prydz Bay fast-ice edge versus MODIS** `[S]`, and it is an observation, not a forecast.

**3. Ice charts — AARI–NIC–NMI Antarctic analysis, USNIC icebergs.** Better than us: the only source with WMO stage of development for the Antarctic; USNIC is the authoritative iceberg record since 1978. Under the condition of a day-to-day approach decision, the limitation is cadence — specified weekly, observed roughly fortnightly `[M]` — and the analyst error floor (exact agreement 39%); five classes against POLARIS's eleven leave the RIO ambiguity spanning **all three operational tiers**.

**4. Polarstern MapViewer (AWI).** Better than us: layer breadth we cannot approach — MODIS, Sentinel-1, onboard Sigma S6 ice radar, AMSR2, 9-day drift forecast, EPSG:3031, backed by a data-logistics team. Under the condition of a chartered cargo ship on a different programme, it is internal to one operator's fleet and is not a product anyone else adopts. **Note that Polarstern and Nuyina are both IcySea customers, so #1 and #4 are partly the same thing.**

**5. Type-approved ECDIS with ice overlays.** Better than us, permanently: type approval under MSC.232(82), carriage-mandated under SOLAS V/19.2.10, and ownership of the bridge screen. **An operational S-411 sea-ice service already covers "Southern (Antarctica)" through the JCOMM Ice Logistics Portal** — a standards-based Antarctic ice feed this project had never heard of `[S]`. Under the condition of ice-aware, vessel-specific reachability support, that is not what they sell; and for us the limitation is the reverse — **no ECDIS integration of any kind is designed**, so today our output reaches the bridge as a laptop screen beside it.

**6. Commercial weather routing (StormGeo ~13,000 vessels, 75,000 voyages/yr, 24/7 human route analysts; DTN-class).** Better than us: mature, multi-objective at scale, commercially proven — and **the human-in-the-loop fallback is evidence that full automation is not trusted at the edges**. Under the condition of a 55-hull polar niche with a single-window supply chain, the limitation is structural: a company serving 13,000 hulls will not build for 55.

**Closest functional precedents, honestly.** (a) **PolarRoute/meshiphi (BAS, MIT)** — the routing engine we reuse; better than anything we would write. Limitations verified in source: no time dimension, IceNet loader drops `sic_stddev`, no iceberg model, `wave_resistance()` never called, fuel polynomial fitted to a different hull `[M]`. (b) **CHINARE FIPS / SOIPS** — **the nearest existing system to our highest-value pain point, on our exact coast, and ahead of us on it**. (c) The **Bharati–Maitri optimum-route study (*Polar Science*, 2021)** — deterministic, no uncertainty; proves the problem is recognised inside the Indian programme. (d) **INCOIS Ocean State Forecast along ship routes** (since 2013) — the institutional home and delivery precedent; stops at 30–45°S.

---

## L. Data-backed gaps

| Dimension | Evidence | Gap |
|---|---|---|
| **Update latency** | OSI SAF ~5 h; CMEMS by 12:00 UTC; Sentinel-1 over Prydz Bay median 23.9 h, max 47.7 h `[M]`; AARI ~fortnightly `[M]`; IcySea ~1 h `[S]`. Ours: historical replay, **no age field** | Incumbents deliver within hours; we deliver nothing live |
| **Spatial resolution** | CDR 25 km from a 70×45 km footprint, edge 25–50 km off `[S]`; AMSR2 6.25 km; **CMEMS 1 km Antarctic L3 exists and is unused** `[S]`; routing mesh cell at Bharati ~139 × 49 km `[M]` | **Our finest cell is larger than the problem.** The 1 km product is a free upgrade for observation |
| **Temporal horizon** | CMEMS D+9; voyage ≈15.2 d at AIS speed `[D]` | **41% of the voyage is beyond any forecast at departure.** No product closes this; the correct display is climatology |
| **Replanning** | PolarRoute has no time dimension `[M]`; re-plan ~9 s `[M]`; DAILY arm **slower** than STATIC `[M]` | A static router cannot consume a forecast |
| **Iceberg prediction** | Trajectory errors measured: **0** `[M]`; physics-only ADE 127–147 km with no attributable lead `[S]`; currents slope ≈0.5; >90% SIC regime unmodelled; USNIC floor 18.5 km | **One third of the PS has no measured capability** |
| **Sea-ice interpretation** | Algorithms disagree 2.8–28.8% SD at 15% SIC `[S]`; analysts 39% exact `[S]`; five stage classes vs eleven | Neither we nor incumbents can give a POLARIS-grade input; we can at least show the band |
| **Connectivity** | VSAT unreliable <70°S; Certus ≤704 kbps; **demo makes zero external calls, test-enforced** `[M]` | Design offline-first; build single-tier |
| **Bandwidth** | 76 KB vessel-mesh block `[M]`; 796 B route polyline `[M]`; full corridor 0.5–1 MB `[D]`; **daily delta unmeasured**; weights ~60 MB `[D]` | The load-bearing number has never been produced |
| **Offline capability** | Climatology floor, obs-only pack, rollback — all `[T]` | IcySea ships an offline cache today; we do not |
| **Vessel-specific context** | Two ships, identical 41-leg track; ETA +1.28 d, fuel −8.9% `[M]`; limit assumed; cliff ≤45% `[M]` | Vessel-awareness is load-bearing for **cost, not track** |
| **Explainability** | 9 gates, health derived, binding gate carried, divergence names the flipped gate `[M]` | **Ahead of incumbents on decision record**; behind on vocabulary and ECDIS integration |
| **Operator workload** | No data. **No navigator has seen the output** `[M-absence]` | **This needs validation** — the most consequential unknown in the project |
| **Prediction uncertainty** | None quantified `[M]`; day-1 RMSE 0.0465 is inside the reference product's own uncertainty `[M/S]`; no published study propagates SIC uncertainty into a routing decision `[S]` | The white space is real but unbuilt; quote relative gain over persistence only |

Two numbers not to manufacture: the false-positive/false-negative *rate* of the ice gate (no passability ground truth exists), and the value of a saved ship-day (the day rate is unknown, and the one stale-data experiment returned 0.03 days).

---

## M. Why now

**1. The data plane is free, daily and Antarctic — for the first time in one place.** CMEMS publishes an operational global physics forecast with SIC, thickness and drift to D+9, and this project has archived it daily since 31 August 2026 `[M]`. NSIDC's CDR is no-auth back to 1979 `[M: 1,096 files, 0 failures]`. GFS-Wave runs natively to −79.5° with no login `[M: verified live]`. Sentinel-1 gives the Bharati approach a new scene roughly daily — **measured, not assumed: 31 passes in 30 days** `[M]`. An S-411 standards-based Antarctic ice service is operational `[S]`. A solo team can now assemble most of a national ice desk's data plane for nothing.

**2. The engine is open.** PolarRoute and meshiphi are MIT-licensed and actively maintained (v1.1.11, 2026-07-02), installing in ~90 s and running a full mesh→vessel→Dijkstra→smoothing pipeline in ~9 s on a laptop `[M]`. Three years ago the honest options were a from-scratch A* or a commercial contract.

**3. The decision computation fits on the bridge.** A 1.93 M-parameter U-Net beats persistence at 1–7 days and trains in 1–2 hours on a free T4 `[M]`; inference ~0.3–1 s on a 4-core CPU `[T]`; weights ~60 MB; re-planning 9 s `[M]`. **None of this needs a GPU at sea.** The field's own choice for this target — IceNet — is also a small U-Net at 25 km, not a foundation model; the whole daily record is ~17,000 frames.

**4. Regulation has caught up with the hazard and is still moving.** Polar Code in force since 1 January 2017, with Chapter 11 duties naming hydrographic limitations, ice type, SAR remoteness and places of refuge `[S]`; **IMO now requires bridge-controlled ice-detection searchlights on existing ships from 1 January 2027 — a concession that radar alone does not find ice** `[S]`; S-100 ECDIS usable from January 2026, mandatory for new installations 2029.

**5. India's programme is expanding on a fixed clock.** Maitri II: ₹2,000 crore, completion January 2029 `[S, secondary]`. The 44th ISEA sailed December 2025 and deployed an INCOIS glider from this very ship `[S]`. An indigenous polar research vessel MoU was signed June 2025 — **the window in which bridge software gets specified rather than bolted on.** ISRO's EOS-06 has produced a daily 12.5 km Antarctic ice-extent product since June 2024 `[M]` — the first live Indian Antarctic ice product since SCATSAT-1's lapsed in 2019, which cuts both ways: an independent Indian check exists now, and **the precedent says unowned Indian polar data services lapse.**

**6. The environment has changed — the non-manufactured urgency.** Antarctic sea ice has sat in a post-2016 low-extent regime with record lows in 2022, 2023 and 2025 and "different seasonal persistence characteristics"; the literature's own words are that climatology is "by definition, not meaningful" in a non-stationary state `[S]`. **A master without a forecast navigates on a personal climatology, and that is exactly the quantity a regime shift degrades.** "Ships already go" was true under a climate that held still.

**What has not changed, stated so the argument is not oversold.** Connectivity below ~70°S is still Iridium-class in every source this repo holds; the claim that LEO broadband is absent there was not assessed `[H]` — if Starlink-class coverage reaches the corridor, the bandwidth argument weakens, the metered-comms argument remains, and **the decision layer is unaffected**. Growlers remain invisible to everything in orbit. No Antarctic compression product exists anywhere. The market is fifty-odd hulls, and the closest competitor has been seven people for twelve years. The customer's tender already anticipates that ice will stop the discharge, with **no clause for when it is not workable** — and that clause has been in the contract for years. The point of starting now is that, for the first time, the inputs to answer it are free, the engine to compute it is open, and the programme that needs it is about to move a station across that coast on a deadline.
