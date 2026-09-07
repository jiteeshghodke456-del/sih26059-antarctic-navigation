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

---

## N. Solution in one sentence

**For the master of India's chartered Antarctic resupply ship, who today decides whether to push the last 100 km into Bharati station on yesterday's ice picture and his own judgement, this is a laptop tool that, from real satellite ice and this ship's real dimensions, says each day whether that approach is open for this hull, what the alternatives cost, and — for the six of nine safety questions it has no data to answer — says so out loud instead of drawing a confident line over an unknown.**

The version a layperson keeps: *the ocean crossing is easy; the station door is shut three days in four (**Measured**: 23 of 31 December-2019 days); this tells the captain whether the door is open today, and refuses to pretend it can see what it cannot.*

What the sentence deliberately does not say: "AI", "forecast", "route optimisation". The demo runs no model, plans on one day's observed ice with no time dimension, and the route is a fixed 41-leg line solved once. **The honest product today is a reachability-and-evidence console, not a forecasting router.**

---

## O. Core innovation

### What the user had to do before
A master approaching Prydz Bay works from an AMSR2/PolarView image (yesterday's at best), the USNIC weekly berg list, helicopter reconnaissance, and experience. Every one of those shows *what was seen*; none says *what this hull can do with it*, and none says *what was not seen*. The professional aids that exist are binary or scalar: an ECDIS route check lights red or green; POLARIS returns one number. **In all of them, absence of evidence renders as absence of hazard.** The repo hit this on its own data twice: the CDR writes suppressed coastal pixels as `0.0` inside `valid_range`, so an unguarded reader saw open water on four of the eight days Bharati "looked open" (**Measured**); and a never-scored target rendered as "closed 31 of 31" until the code separated *unavailable* from *closed*.

### What the user can do now
Read one state — VALID / DEGRADED / CRITICAL / INVALID — *derived* as the worst of nine named questions, where a question without data is **UNKNOWN**, UNKNOWN caps health at DEGRADED, and each UNKNOWN names the dataset that would settle it. Approve under a named person; when a later observation flips a gate, the console names it ("logistics: PASS to FAIL") and stays silent when nothing changed (**Measured** on 1/5/9 December 2019: DEGRADED → INVALID → DEGRADED).

### The bottleneck that disappears
Not computation — the **reconciliation step** a master does in his head: *"the chart says X; what does the chart not know; does that change my plan?"* That step is unbounded, unrecorded and non-transferable at watch handover. The system makes it structural: nine fixed questions, each with provenance, evaluated automatically on each new observation, and the record survives handover. What used to be judgement about *coverage* becomes a displayed number: "3 of 9 gates evaluable".

### Why UNKNOWN is innovation and not an excuse for incompleteness
The accusation writes itself: *"six grey lights is a prototype that did not finish."* Four answers, and one condition that bounds them.

1. **It inverts the default failure mode of every dashboard, and it is enforced in code, not in a caveat.** `health_from_gates` treats UNKNOWN exactly like MARGINAL; an *empty* gate list is DEGRADED, not VALID; a test asserts a gate with no data can never read as a pass. A competitor cannot bolt this on later, because their whole visual language (green = fine) assumes the opposite default. It is the CATZOC "U — unassessed" principle applied to the whole decision rather than one attribute.
2. **It is what the regulation asks for.** Polar Code Part I-A §11.3.2 obliges the master to consider "any limitations of the hydrographic information … available"; MSC.1/Circ.1519 §1.4 says POLARIS is "not a 'Go/No Go' tool but a decision support tool". A tool returning "chart: UNKNOWN — no bathymetry in the mesh" is producing the §11.3.2 statement automatically.
3. **It generates operational value from missing data.** Each UNKNOWN is a costed request: the execution gate is closed by a live sensor feed *or a helicopter recon observation entered by the bridge*; the chart gate by GEBCO with its TID grid. "We don't know" becomes "here is what to go and get, in what order."
4. **It composes with change detection.** A paper checklist has the same nine questions. It does not flip on the 5 December observation, does not distinguish "an assumption changed" from "new data arrived", and does not version the approval it invalidates.

**The bounding condition — write it down, because it is where this claim dies.** UNKNOWN is innovation only while the count of UNKNOWNs *falls monotonically and each closure is measured*. The ice gate today evaluates an invented 80 % limit against a pixel maximum the router never optimised, on a cell 139 km wide at Bharati (**Measured**). If in December the same six gates are still grey and the three evaluable ones still rest on an assumed limit, the honest reading becomes "a scaffold with no building," and a judge will say so.

---

## P. Unique selling points

### Primary USP 1 — Evidence-gated route health with a first-class UNKNOWN

| | |
|---|---|
| **Problem** | Every incumbent renders no-data as no-hazard. The repo's own artefact — coastal pixels reading `0.0 %` on 43.2 % of days in the Bharati box (**Measured**) — is what that looks like in practice |
| **Mechanism** | Nine named gates → worst-state derivation → UNKNOWN caps at DEGRADED and names its blocker → approval versioned and attributed → divergence names the flipped gate and is silent on identical evidence. **Health is never a score** |
| **Evidence** | Health transitions on real observations: DEGRADED (1 Dec) → INVALID (5 Dec) → DEGRADED (9 Dec) (**Measured**). Re-evaluating the same day yields the same digest and no divergence (**Measured**) |
| **Advantage** | The master sees coverage — "3 of 9 gates have data" — *before* he sees a route; an approved plan is invalidated by a named assumption, not by every new file |
| **Defensibility** | Low as an *idea* (nine gates copy in a day); high as a *discipline*, because it forbids the green dashboard that wins demo rooms. Defensible exactly as long as §O's bounding condition holds |

### Primary USP 2 — The last-100-km reachability verdict for this hull, on an audited coastal record

| | |
|---|---|
| **Problem** | The PS reads as "route across the Southern Ocean". The measured problem is different: the open-ocean leg carries **mean 6 % ice**, while the station cell is closed **74.2 %** of December-2019 days and the approach 100 km north **0 %** (**Measured**). And the satellite record lies at exactly that cell |
| **Mechanism** | Daily NSIDC CDR → QA-flag masking → meshiphi mesh → PolarRoute vessel performance with this hull's verified beam and speed → per-day passability of station and approach cells → the mission's `destination_policy` decides which cell counts |
| **Evidence** | 23/31 vs 0/31 (**Measured**); four of eight "open" days are spillover artefacts (**Measured**); masking moves coastal mean ice *up*, 46.8 → 54.6 % — the safe direction (**Measured**); the filter fires on 1,096/1,096 days, mean 118 cells/day (**Measured**) |
| **Advantage** | Converts "which line" into the decision that actually exists on this run: arrive when, hold at the fast-ice edge, or switch to helicopter and barge |
| **Defensibility** | Rests on a data-quality finding a team that has not opened the QA flag will not have. **Weak points a judge with a ruler will find:** the 80 % limit is invented, the Bharati mesh cell is 139 × 49 km, and reachability flips at an assumed limit between 45 and 50 % |

### Basic USPs
1. **BAS's own router reused with three verified limitations named** — `wave_resistance()` dead code, no time dimension, `IceNetDataLoader` drops `sic_stddev`, all verified in installed source. Basic, because the extensions are designed, not built.
2. **A trained residual U-Net beating persistence +18.5 % to +30.6 % on a held-out melt season, scored once** — with its own caveat that this is an upper bound. Basic until the leak-free ablation runs.
3. **Offline by construction** — no tile, font, CDN or external URL, test-enforced; boot refuses on a missing satellite file rather than rendering a gap. Basic, because IcySea already ships Iridium-tested offline caching; ours is a zero-network page, not yet a sync design.

**Not a USP yet, and should not be sold as one:** the Wagner–Dell–Eisenman drift implementation. Correct, tested, three numerical traps fixed — and wired to nothing, fed no real forcing, with no trajectory error ever measured.

---

## Q. Killer feature

**"Approve on an open day; drag to 5 December; route health goes INVALID and the console names the gate that broke. Drag back; it says nothing changed."**

Visible (a band changes state, a sentence names a gate), operational (it is the hold-or-press-on decision), credible (nothing is scripted — it is the vessel mesh on that day's observation), demonstrable in thirty seconds offline, and tied to the primary pain.

| Stage | What actually happens | Honest gap |
|---|---|---|
| **Input** | NOAA/NSIDC CDR G02202 v6, 25 km, with QA flag | Observation of *that* day, not a forecast of arrival day |
| **Processing** | QA bits → NaN; polar stereographic → lat/lon; meshiphi 5° cells; vessel model marks cells inaccessible above `max_ice_conc: 80` | Bharati's cell was only split to 1.25° |
| **Model** | **None.** In production: corrected SIC at lead *k* from the residual U-Net | Weights absent; nothing consumes the model |
| **Risk** | `logistics_gate` → FAIL; `ice_gate` → MARGINAL (74 % vs 80 %, inside the 7.4-point band from the CDR's own stdev); six UNKNOWN → health INVALID | Ice gate uses a pixel max the router never optimised |
| **Route** | Unchanged — solved once on 1 Dec ice; A/B/C precomputed | No re-plan |
| **Recommendation** | "Bharati is not reachable for this ship today"; alternatives with ETA deltas; preview shows destination state on the *arrival* day | Arrival-day state is a replayed observation, not a forecast |
| **User decision** | Keep / edit / take alternative; keep re-approves as a new version; approve is 400 without a name | Log is in-memory; a reboot loses the plan of record |
| **Outcome** | In replay the closure is caught the day it is observed. Ship-days saved — **Target, unmeasured** | The outcome metric has no baseline |

**What must change for this to be a killer feature in December rather than a demo beat:** the trigger must be the *forecast for the ship's ETA at the approach*, not today's observation of a cell the ship is nine days from. Without that, the feature detects closures the master could see out of a porthole.

---

## R. Hyper-specific MVP

**One user:** the master. **One decision:** *inside D+7 of arrival, continue to the station cell, hold at the approach (68.5°S, 76.2°E), or switch to helicopter-and-barge?* **One workflow:** sign in → mission → route → waypoints → nine gates → approve → monitor → workspace on divergence → re-approve. **One measurable outcome:** ship-days lost at or before a closed approach per season, versus the previous seasons' record (baseline unknown).

**Bottleneck sentence:** *Today, the master cannot efficiently decide whether to commit to the station approach because the ice picture he receives shows concentration, not this ship's reachability, and it reports suppressed coastal pixels as open water on 43 % of days near Bharati (**Measured**). Our system reduces that by computing per-day reachability for this hull on a QA-masked record, and by declaring, per safety question, what it cannot see.*

**MUST-EXIST:** daily SIC ingest with QA masking (built) · vessel mesh at native 25 km in the coastal band (**partial** — coastal cell is 1.25°) · station/approach reachability per day (built, on the coarse cell) · nine-gate health with UNKNOWN, versioning, divergence (built) · **a forecast-grade input for the arrival day** (**absent** — without it the MVP answers "is it open today", not "will it be open when we get there") · valid/init/received time on every field (**absent**) · durable plan-of-record (**absent**) · offline page (built) / sync design (**absent**) · data-mode badge (built).

**USEFUL-BUT-OPTIONAL:** A/B/C sweep · two-vessel comparison · protected areas · coastline · dated berg overlay · POLARIS advisory *band* · waypoint ETAs.

**EXPLICITLY-EXCLUDED:** growler warning (3.5 orders of magnitude below any satellite product) · tactical steering · a POLARIS RIO *number* for this hull · absolute fuel figures · fleet coordination · any LLM/RAG in the decision path · compression risk field · time-expanded routing (v2, not MVP).

---

## S. Architecture verdict

| Component | Verdict |
|---|---|
| **Frontend** | Right for a bridge laptop — no build step, no CDN, 2,390 lines readable in an afternoon. Two real defects: a hand-rolled projection already shipped one geometry bug (2.92× error at Bharati, **Measured**); no polar-stereographic mode for the leg that matters |
| **Map engine** | Adequate for the demo, wrong for the approach. Draw in EPSG:3412/3031 directly and use BAS ADD coastline — ice-front vs grounding line are operational distinctions at Bharati. A tile server is unnecessary |
| **Backend** | Right shape, wrong persistence: **a reboot loses the approved plan** |
| **API layer** | Good — refusals are typed (409 out-of-order, 400 unattributed, 503 missing artefact). Missing: any field-level time metadata |
| **Ingestion** | The one piece of *operational* infrastructure, and it has two live bugs: files named from the wall clock (silent D−1 capture) and a harvest box that does not match the training corridor. **Unrecoverable data is being lost at the margins every day** |
| **Validation** | Present where it was needed most (coast); absent for CMEMS content beyond a size check |
| **Normalisation** | Correct and worth defending — truth is never resampled |
| **Database** | None. Fine for read-only replay; a product needs a pack store with manifest, versions and rollback — designed, zero code |
| **Sync** | The most-cited design claim in the docs and the least-built: no pack format, no delta, no signature, no key management |
| **Offline** | Page yes; re-planning no. "Cut the cable and keep planning" is not demonstrable today |
| **ML inference** | None aboard. The "Real AI" bar is met by the training artefact, not by the product |
| **Route engine** | Correct reuse; wrong configuration for the PS's "fuel-efficient" deliverable |
| **Risk engine** | The strongest module. Thin inputs |
| **Telemetry** | None. Own-ship position is computed from the planned track — correctly labelled, still absent |
| **Onboard deployment** | **Not deployable as-is**: two Python runtimes, per-machine venv rebuild, and data reached by a symlink into a sibling git worktree (P0) |
| **Monitoring** | Three numbers should be watched — pack age, gate coverage, route latency. None is |
| **Security** | Acceptable for a demo. For a bridge: signed manifests, read-only OS user, USB ingestion as an attack surface, pinned dependencies |

### Data flow, every boundary named

```
External   NSIDC CDR (HTTP, no auth, ~368 KB/day) · CMEMS GLO12 (auth, 42.6 MB → 5.2 MB)
           GLORYS12 (Kaggle only) · USNIC CSV (1.9 KB) · ATS shapefile · Natural Earth
   │ B1 network→disk. Contract: date-named file, size check.        [BUG: harvest names by wall clock]
Ingestion  download_nsidc.py · harvest_cmems.sh · compress_netcdf.py · catalogue.py · coastline.py
   │ B2 NetCDF/CSV/shapefile → arrays. Contract: dataset with conc + qa_flag.
Validation ice_quality.py::load_sic  (QA bits → NaN + suspect mask) · audit_ice_quality.py
   │ B3 (sic, suspect) in EPSG:3412. Contract: NaN means unknown, never 0.
Normalise  grid.py::GlorysToNsidcRegridder (area-average; truth never resampled)
   │ B4 DataFrame(lat, long, SIC) — meshiphi's scalar_csv contract.
Storage    nsidc_sic/ (1,096 files, symlinked — P0) · vessel_meshes/ · figures/*.json
   │ B5 JSON on disk. No manifest, no valid_time, no signature.
Processing meshiphi mesh (5°, split_depth 4) · VesselPerformanceModeller
   │ B6 vessel mesh JSON — cells carry SIC, speed[8], inaccessible.
Model      U-Net: trained on Kaggle, consumed by NOTHING
           Wagner drift: tested, fed by NOTHING, consumed by NOTHING
   │ B7 DOES NOT EXIST. Designed: corrected SIC → mesh layer; berg polygons → excluded_zones.
Route      PolarRoute Dijkstra + smoothing, offline, single day, single objective
   │ B8 GeoJSON paths + per-leg traveltime → routes.json / alternatives.json
Risk       gates.py::evaluate_all → decision.py::health_from_gates, gate_digest
   │ B9 list[GateResult] → Decision.as_dict().  [SEAM: consumes a pixel statistic the router never saw]
Decision   decision_service.py (DecisionLog: approve/supersedes/divergence) · workflow.py
   │ B10 JSON over HTTP, localhost.
UI         app.js (Canvas raster, SVG vectors, Mercator) · workflow.js · index.html
```

**Boundaries B7 and the model half of B9 are the ones the product's value rests on, and they are the two that do not exist.**

### Would I choose this architecture again for a real Antarctic deployment?
**The shape, yes. Four implementation choices, no.**

Keep: two-tier "sync environmental state, not answers" with the full router aboard; decision layer as pure functions over explicit evidence; committed extracts so the runtime has no geospatial dependency that can fail live; PolarRoute reused; no LLM anywhere.

Change, in order:
1. **Time.** A static single-day mesh cannot consume a forecast; the router meets day-0 ice on day 9. Either a time-expanded mesh stack or the two-phase solve (ocean leg on today's field, approach leg on the corrected field valid at the arrival band, solved backwards to a cost-to-go). **Without this the model has no path to the route and "AI-enabled routing" is a slide.**
2. **A pack format instead of loose JSON** — one signed manifest per pack, every field carrying init/valid/received time, tier, source, qc version; N previous kept; delta = changed cells.
3. **One runtime.** Pin to Python 3.11, vendor PolarRoute, ship one executable. The 3.11/3.12 split makes on-board re-planning impossible.
4. **Resolution where the decision is** — force native 25 km inside a 300 km coastal band so the router optimises the same quantity the gate reports.

Plus: an NMEA listener (the ship already logs position, heading, wind, echo sounder, shaft power — and speed-through-ice vs predicted is a *free daily model validation*), and a durable store for the plan of record.

---

## T. Tech-stack verdict

**Vanilla JS + Canvas + FastAPI is right for a bridge laptop with no internet, and is not a liability at the scale this problem has.** No build step means no toolchain to break on a ship; no CDN means the page is airtight; a single Python process is what a 4-core, 8 GB bridge laptop can run.

Where it breaks: **projection by hand** (one geometry bug already shipped — vendor `proj4js` or `d3-geo` *locally*, which does not violate the no-network rule); **raster draw cost** if drift animation is ever wanted (move to `ImageData` blit or WebGL — not needed now); **in-memory state** (SQLite with WAL, one file); **two Python versions** — the single biggest deployment liability in the repository; **no JS tests** (one offline Playwright smoke test would cost an hour).

What does *not* break: one bridge user; 10 leads × 5 members × ~25 k cells × uint8 ≈ 1.25 MB/day (**Derived**); a 12-route sweep at ~7 s each ≈ 84 s as a background job. Circumpolar, the mesh grows ~10× and Dijkstra is still seconds.

What I would **not** add: MapLibre/Leaflet (no tiles to serve, 800 KB for nothing), React (a build step on a ship), a message queue, Docker on the bridge. **The stack's virtue is that it contains nothing that can fail for a reason unrelated to ice.**

---

## U. Connectivity verdict

Geostationary VSAT does not reliably cover south of ~70°S; polar maritime data is Iridium-class — Certus peaks ~704 kbps and is usually far less; legacy Iridium is provisioned for sub-50 KB messages (SBD is 340 bytes each). Inmarsat-C SafetyNET reaches only to roughly 76° because the satellites are geostationary; **Iridium SafetyCast, operational since December 2020, is the only broadcast maritime-safety channel with true polar coverage.**

Built against this: a page that fetches nothing (**Measured**). Designed and unbuilt: everything else.

| State | Budget | What moves | What the system does |
|---|---|---|---|
| **Connected** (Cape Town) | GB | archive, CMEMS cycles, model weights (~60 MB), bathymetry, climatology tables, last season's log | Full pack build; **weights only here** |
| **Constrained** (Certus, metered) | ≤ 1 MB refresh, ≤ 50 KB delta (**Target**) | corridor forecast ~60–120 KB gzip (**Hypothesis**); delta 6–15 KB; USNIC ~2 KB | Daily pack; re-plan aboard |
| **Intermittent** (~2.4 kbps or SBD) | 50 KB ≈ 3 min, or 150 SBD messages (**Derived**) | P0 hazard alerts (~100 B); P1 observed SIC delta in a 300 km box (5–15 KB); P2 next-3-day leads | **On-board re-correction of the packed forecast from the fresh observation** — the one capability a packed third-party forecast cannot have |
| **Disconnected** (days) | 0 | nothing | Forecast ages past its horizon → tiering; berg projection stops at 72 h; ship sensors and rule gates become the evidence |

### Countering stale data — the question that decides whether this is a safety tool

Three distinct failures: **F1** a stale hazard field rendered as current (the ship steers around a ghost into the real thing); **F2** a forecast displayed past its horizon; **F3** "no update" read as "no change" — the most insidious, because silence from the link is indistinguishable from a benign world unless the system says otherwise.

Seven layers, cheapest and most data-independent at the bottom:

- **L0 — Nothing renders without a time and a tier.** Valid time, lead, age, tier badge. A field without a badge is a bug. Kills F1 and F3 as *display* failures. *Absent.*
- **L1 — Uncertainty grows with age from the project's own measured error curve.** An observation aged *k* days **is** a persistence forecast at lead *k*, and the curve is already measured: RMSE 0.0570 / 0.0958 / 0.1204 / 0.1395 at 1/3/5/7 days. So routed `SIC_upper = SIC_last + q(age)` — one lookup, no new science. **The ice gate then goes UNKNOWN by itself once the aged error (0.14 at 7 d) exceeds the 7.4-point band around the limit: the system can no longer tell "under" from "over", and says so.** The arrival-day cell is not "open"; it is *"last observed 31 %, 8 days ago, ±14 points — unknown against an 80 % limit."* *Absent; ingredients exist.*
- **L2 — Physics dead-reckoning with forcing the ship measures itself.** The ship has an anemometer regardless of link. Free drift moves ice at ~2 % of the 10 m wind, turned 20–40° left in the Southern Hemisphere. Semi-Lagrangian advection of the last observed field by the ship's own wind record beats persistence and costs nothing. Above ~90 % concentration the pack is locked and it should switch to packed drift. At 30 m/s a blizzard moves the field ~52 km/day — which is why a 25-hour event makes a two-day-old chart useless. *Absent.*
- **L3 — Decisions carry expiries; the plan is pre-committed with hold points.** Each gate gets a `valid_until` derived from L1; on expiry it flips to UNKNOWN and the existing divergence machinery names it. The approved plan carries decision points chosen while data was fresh: *"hold at 68.5°S unless recon confirms ≤ 6/10"*; *"abort if speed-through-ice below 3 kn for 2 h."* **The ship then arrives at the ice edge with a plan that does not depend on the link having worked.** *Machinery exists; expiry does not.*
- **L4 — The ship's own observations become primary evidence.** Speed-through-ice vs predicted (the vessel mesh predicts a derated speed per cell; slower means heavier ice — the same innovation channel as `background − observation`); radar and the lookout; **helicopter reconnaissance, which this ship carries two of and uses on this route.** Today there is no path for a recon observation into the system at all. *Absent.*
- **L5 — Rules that need no data.** Stand-off from the fast-ice edge when the wind has an onshore component (AARI: *"the most dangerous case for shipping is compression at the fast-ice edge when the general drift sets into it at an angle"* — **precisely the Bharati offloading geometry**); speed caps below the growler-detection threshold; no entry above a stated concentration without recon; point-of-no-return against bunker and the nearest capable asset. *Absent.*
- **L6 — The 100-byte request.** The ship cannot afford an image; it can afford a request. And the hazard broadcast channel exists whether or not our link does — METAREA VII warnings by SafetyNET/SafetyCast. *Absent.*

### If we never get fresh data and a hazard is ahead
Day 0: pack shows the approach open, arrival day beyond D+9 — climatology only, and the system may **not** say "open on arrival". Days 1–7: no link. Day 8, 66°S, last observation 8 days old. L0 shows every field aged 8 days, tier climatology-grade, route reduced to a dashed corridor with no waypoints into ice. L1 has widened the approach cell to "31 % ± 14 → unknown against 80 %" and the ice gate is UNKNOWN. L2 has advected the last field by the ship's own wind; if it was onshore for three days, the coastal band is drawn *heavier*, not lighter. L3 fires the pre-committed hold at 68.5°S — the cell open 31 of 31 days. L4: the helicopter flies, the observation is entered, the execution gate closes on a *fresh local* observation. L5 holds the ship off the fast-ice edge. L6 sends 100 bytes.

**The principle underneath all seven: a stale forecast is never an input to a route; it is an input to a widening.** The system's job when blind is not to keep recommending — it is to shrink what it claims, keep the pre-committed plan visible, and make the ship's own observations first-class.

### Degrades vs hard-fails

| Degrades (visibly) | Hard-fails (refuses) |
|---|---|
| Route line → dashed corridor, waypoints withdrawn | Rendering any field without valid/init/received time |
| Point ETA → range | A pack whose manifest hash or signature fails |
| Berg polygons → last-seen points with dates after 72 h | A bridge clock not synchronised to GPS time |
| Forecast-grade → CMEMS-direct → climatology | Approach-phase route solving with no bathymetry (today this only DEGRADES — too weak for a product) |
| Health VALID → DEGRADED as gates expire | **An ice-gate PASS from stale numbers once aged error exceeds the band — must return UNKNOWN** |
| Own-ship GPS → dead reckoning, labelled | An approval without a name; serving replay as live |

**Standing verdict:** the repository has the right *doctrine* and almost none of the *machinery*. Of L0–L6, only the health cap exists. **L0 and L1 are a schema and a lookup table, and should be built before any further model work** — without them, every other capability is a way to display stale numbers more confidently.

---

## V. Data-source verdict

"Real-time" appears nowhere below, because nothing in this stack is: the fastest product available (OSI SAF, 5 h) is not used, and the fastest thing that *is* used is a daily file.

| Source | Variable | Spatial | Temporal | Latency | Licence | Reliability / missing data | Bandwidth | Why this over alternatives |
|---|---|---|---|---|---|---|---|---|
| **NSIDC CDR G02202 v6** *(used)* | SIC, QA flag, stdev (unused) | 25 km EPSG:3412 | daily | final latency **conflicting** (~1 wk vs 3–6 mo, UNVERIFIED) | NOAA, open | 1,096/1,096 files. Spillover 118 cells/day mean, max 488; Bharati box suspect 43.2 % of days. Accuracy ~10 %, 0–100 % at coast/edge; summer melt bias 10–30 % low | ~368 KB/day | 48-year record, same family in NRT (no train/serve mismatch). Its weakness is exactly where the decision is — which is why the QA layer exists |
| **CMEMS GLO12 001_024** *(harvested, unused by model)* | siconc, sithick, usi/vsi, uo/vo | 1/12° | daily D+0…D+9 | "by 12:00 UTC"; missed bulletins unrecoverable | Copernicus | 13 runs, 1 login failure; wall-clock naming bug; box clipped on all four sides. **CMEMS underestimates summer Antarctic SIC — the unsafe direction** | 42.6 MB → 5.2 MB | The only Antarctic-covering ice-ocean *forecast* with SIC, thickness, drift and currents in one product. Also **the only product that can make fuel and time diverge** |
| **GLORYS12** *(training background)* | siconc | 1/12° | daily 1993– | reanalysis — **the leak** | Copernicus | flat 0.163 error at every lead | Kaggle only | Deep archive of the same model family; defensible only for Stage A with disclosure |
| **USNIC icebergs** *(archived once)* | bergs ≥ 10 nmi axis | point | weekly | days | US Gov, public | 33 bergs, largest 3,037 km². **No history endpoint — must be archived weekly or trajectories are impossible** | 1.9 KB | Authoritative positions; BYU consolidated DB (1978–2025, 4.1 MB) for validation history |
| **GFS + GFS-Wave** *(verified live, not ingested)* | wind, MSLP, Hs | 0.25° | 4/day to 384 h | ≤ 6 h 16 min | public | Hs corr > 0.9 to day 5 — global; **polar skill explicitly uncharacterised** | small corridor subset | Free, native southern grid over the whole corridor |
| **ERA5** *(planned forcing)* | wind, 2T, waves | 0.25° hourly | 5-day | C3S | −3.89 m/s bias above 20 m/s at the Antarctic coast | MBs | **Leak rule: forcing at *t*, never *t+lead*** |
| **OSI SAF 401/408/405** *(verified, unused)* | SIC, edge, type, drift | 10 km; drift 62.5 km | daily, 5 h | CC-BY-4.0 | SH target accuracy 15 %. **Drift produced 1 Apr–31 Oct only — the resupply season has no observational drift** | MBs | Best second observation for a disagreement layer |
| **GEBCO 2025 / IBCSO v2** *(not downloaded)* | depth, TID | ~450 m | static | open | East Antarctica singlebeam-dominant; **23.79 % direct measurement south of 50°S** | tens of MB | Only open bathymetry. Its absence keeps `min_depth` inert and the chart gate UNKNOWN |
| **ATS protected areas** *(used)* | 148 polygons | vector | static | Treaty Secretariat | **0 of 33 corridor polygons marine → none restricts transit** | 33 KB | Legal authority, no substitute |
| **Sentinel-1 EW** *(not ingested)* | C-band SAR | 20–40 m | ~24 h median at Prydz Bay, max 47.7 h | Copernicus | cloud/darkness-proof | 1–4 GB/scene — **far beyond Iridium** | The only source that sees leads, fast-ice edge and small bergs; shore-side only |
| **CMEMS 1 km Antarctic L3** *(not used)* | SIC (S1+AMSR2) | **1 km** | daily NRT | Copernicus | observation, not forecast | MBs | **25× finer than what the router reasons on** — worth a look before any coastal claim |
| **ISRO EOS-06 SCAT** *(not used)* | ice/water flag | 12.5 km | daily, ~1 d | UNVERIFIED | ~96 % agreement vs AMSR2 on heritage | small | Different physics (Ku-band) → an honest independent ice-edge check; cannot train a concentration model |
| **S-411 sea ice (JCOMM ILP)** *(not explored)* | ice chart, S-100, "Southern (Antarctica)" | chart | operational | — | — | — | **A live standards-based Antarctic ice source the project had not heard of. Look before building anything else ice-related** |

Two plumbing facts outrank every row: the NSIDC archive is a **symlink into a sibling git worktree** (an ordinary tidy-up deletes the demo's data), and **both irreplaceable archives are being lost daily** — CMEMS through a clipped box, USNIC through the absence of a weekly cron.

---

## W. AI/ML verdict

**Problem.** SIC on the 25 km grid over the corridor at leads 1/3/5/7 days, as a residual on a background field.

**Why ML at all.** Persistence is strong (0.0359 same-day over 2020) and the dynamical model carries a state-dependent MIZ bias. A residual learner conditioned on the *innovation* (`background − observed`) is the cheapest way to learn where the background is wrong; **the v1 model without observation channels scored 0.1051 and lost to persistence** — the experiment that justifies the architecture. Palerme et al. 2024 report 19–33 % for the same class of post-processing; +18.5–30.6 % sits inside that band — plausible, not spectacular.

**Model.** 3-level residual U-Net, 1,929,601 parameters, zero-initialised head so an untrained model reproduces the background, masked MSE, Adam 1e-3, batch 8, ≤ 60 epochs, early stop, seed 0. **Consistency hazard: `models/sic_correction/unet.py` defaults to 19 channels and 40 filters (3.0 M params); what was trained is 12 channels and 32 filters. The repo file describes a model that was never trained.**

**Training data.** NSIDC CDR 2019–2020 — about 730 days, corridor only. **The December 2019 replay window used by the demo lies inside the training slice.** Harmless today because the demo runs no model; **it becomes a leak the moment anyone shows model output on the demo dates.**

**Preprocessing — a defect stated plainly.** `isih/features.py` does not read the QA flag. **The model was fitted with land-spillover zeros present** — fake open water at the coast on 43.2 % of days in the Bharati box. The product's headline data-quality finding was applied to the router and *not* to the model.

**Splits and leakage.** Temporal 70/15/15, contiguous, test scored once — correct, and an earlier +27 % from epoch-selection on the test set was withdrawn. The remaining leak is structural: channel 0 is a *reanalysis* valid at the target date, which assimilated observations near that date. **The flat raw-GLORYS12 error (0.1630 → 0.1637 across leads) is the fingerprint.** The old defence ("if it leaked, its error would be near zero") was correctly withdrawn.

**Tuning.** None. No capacity sweep, no learning-rate search, one seed. **Any comparison between arms differing by a few percent is unresolvable at one seed.**

**Baselines.** Persistence, background + constant, background + per-pixel bias, raw background — all computed before training. **Missing: damped anomaly persistence, wind-advected persistence, and the one that matters — raw CMEMS forecast cycles** (build-blocking by the project's own rule; 7 cycles archived, zero scored).

**Metrics.** RMSE only, pooled over the whole box: 0.0465 / 0.0720 / 0.0938 / 0.0968 vs persistence 0.0570 / 0.0958 / 0.1204 / 0.1395. Missing: IIEE, CRPS, F1 at the vessel threshold, signed bias, and any stratification by distance to coast or MIZ. **The pooled box is dominated by open ocean and pack where model and persistence are trivially equal — the skill has never been measured where the pitch says the decision lives.** Also: day-1 RMSE 0.0465 is *below* the reference product's own ~10 % accuracy — **the absolute number cannot be distinguished from a perfect forecast by this reference; only the relative gain is defensible.**

**Uncertainty.** None. One model, no ensemble, no calibration. The conformal design is good and entirely paper.

**Failure conditions.** Melt season (the test slice, and the resupply season); coastal cells (trained on artefacts); post-2016 regime shift (no OOD year held out); transfer from reanalysis background to true forecast background (untested).

**Verdict, plainly.** *The model was correctly split and honestly scored, and it was not tuned, not validated on the field it will correct in production, trained on artefact-contaminated coastal data, and its headline contains a leak of unknown magnitude that inflates the largest number most. It is a proof of plumbing and of an honest evaluation habit, not a validated forecast product.*

**What the ablation must show — pre-committed, before it runs.** Two arms at lead 3 then all leads, three seeds each: **Arm A** (background zeroed) tests whether observation history alone beats persistence; **Arm B** (background = the analysis at initialisation) tests whether a background *available at forecast time* keeps the gain — **the arm that matters, because it is what production actually has.** Decision rule written now: if Arm B beats persistence by more than the seed spread at every lead, the headline stands and the current figures become a secondary "with perfect ocean analysis" bound. **If Arm B's gain falls inside the seed spread at lead 7, retire the +30.6 % figure from every slide and lead the pitch on the decision architecture.**

---

## X. Routing and decision-support verdict

**1. Prediction — in the product: none.** The demo routes on a single day's *observation*. Every "forecast" word on a slide about routing is therefore false today. The route-regret experiment compares two *no-forecast* arms; it says nothing about forecast value. **DAILY being slower than STATIC is a real finding about local re-planning without a global re-solve**, and it undercuts "daily re-optimisation" unless the re-plan is global and forecast-driven.

**2. Risk assessment.** Three gates evaluate: ice (pixel max vs an assumed 80 %, with a 7.4-point band derived from the CDR's own retrieval σ — **the one invented threshold that was replaced by a measured one**), logistics, contingency. Six UNKNOWN. No probabilistic risk, no route-integrated exposure, no iceberg risk, no weather, no compression. Health is a max over gates — correct, and consistent with "never a score". *(Fix the 15-vs-11 in-corridor berg discrepancy between two docs; "in corridor" is a longitude-band test and the largest berg is ~390 km from the station.)*

**3. Route planning.**

| Parameter | Value | Status |
|---|---|---|
| Objective | `traveltime` only | fuel never solved for; sweep unrun |
| Constraints | `max_ice_conc` 80 (**assumed**); `min_depth` 20 (**inert**); `max_wave` 3.0 (**inert**); `force_limit` (**borrowed from another hull**) | **three of four constraints are inert or borrowed** |
| Safety margins | none in the router | the band lives in the gate |
| Ice | concentration only; thickness/density from a climatological LUT | no type, no stage, no fast-ice edge |
| Icebergs | none | `excluded_zones` verified as the injection point |
| Weather | none; `wave_resistance()` dead in 1.1.11 | **the Roaring Forties cost nothing** |
| Time | 8.58 d steaming; ~15.2 d at the AIS average | a lower bound, never a voyage duration |
| Fuel | 309.7 units, another hull's polynomial | not to be quoted |

**4. Human decision support** — built and tested, and **this layer is the product's real substance today**.

### The fuel/time collinearity, honestly
With `zero_currents: True` and wave resistance dead, per-edge speed depends only on ice, so fuel is a monotone function of time along every edge and the two objectives share an argmin — solving for fuel returns a byte-identical path at every limit tested. **"Fuel-efficient routing" — one of the PS's three named deliverables — is therefore unsubstantiated.** What makes them diverge, in cost order: (1) **currents** — `uo`/`vo` are already in the harvested product; set `zero_currents: False`; expected divergence small (0.1–0.3 m/s is 1–4 % of ship speed); (2) **waves** — override `model_resistance` so `wave_resistance()` is actually called, fed by GFS-Wave; **this is where the trade-off surface will come from, because the Forties are where the fuel burns**; (3) only then the sweep. Until (2) exists, present one objective and say why.

### The identical two-ship track, honestly
The reason is mechanical: the only parameters that differ change edge *costs* roughly proportionally and change *accessibility* not at all — same ice limit, depth inert, same borrowed force limit. **A track changes only when accessibility or resistance is ship-specific, and all three ship-specific quantities are the missing ones.** The defensible version: fit the comparison ship's force limit from her sourced "5 kn in 1.0 m level ice", leave this hull's explicitly UNVERIFIED, and present *the asymmetry of evidence* as the finding. Never say "different ships get different routes"; do say **"vessel awareness is proven for cost, not for track, and here is exactly what would make it bite."**

### Three things the routing layer must do to be decision support rather than a drawing
1. **Unify the quantity.** The router optimises 5° cell means; the gate reports 25 km pixel maxima. Force native cells in the coastal band; report pixel max separately as "ice encountered", never as the optimised figure.
2. **Replace the boolean with a band.** Bharati is reachable at assumed limits ≥ 50 % and unreachable ≤ 45 %. Since 80 % is invented, **the honest daily output is the *critical assumed limit* at which reachability flips** — computable, cheap, and more useful to a master than "open".
3. **Give the router time.** Without it the model, the drift and the whole forecast vocabulary have no consumer.

Risk weights: **recommend none.** Use a lexicographic order — hard exclusions → objective → expose `P(closed on arrival)` and the critical assumed limit as separate numbers. A weighted sum would reintroduce the single score the decision layer was written to refuse.

**Standing verdict:** the human-decision layer is real and better than the competition will bring; the risk layer is a sound frame with three thin evaluators; the planning layer is a correctly reused engine in a configuration where three of four constraints cannot fire and the two objectives are one; **the prediction layer does not reach the route.** The routing claim that survives a domain judge today is: *"a real router, on real ice, for the real ship, tells you whether the station cell is passable at an assumed limit — and we can show you where that assumption stops holding."* Everything beyond that sentence is roadmap.

---

## Y. Industry survivability

**The governing finding, stated first.** Across every feature the chain
*detect → degrade safely → notify operator → recover* is **strong on detect,
adequate on degrade, and absent on notify** in the legacy console. §13 had no
implementation anywhere. **This is now built in the bridge console** (P1/P2/P3
with all nine mandated fields), which changes the verdict for the new product
but not for the old one.

The second finding: the system's degradation strategy is **refusal, not graceful
degradation**. Preflight refuses to boot on a missing satellite file; gates
return UNKNOWN rather than guessing; the router simply finds no path at a 45 %
limit. Refusal is the correct *safety* posture and the wrong *availability*
posture — "an availability failure dressed as a safety feature".

### Y.1 Missing data
| Feature | Detect | Degrade | Notify | Recover |
|---|---|---|---|---|
| Sea-ice raster | **Built** — preflight enumerates files and names the `isih/data` symlink | **Built, as refusal.** Rendering a gap as data is the one failure it is built not to have | **Now built** (alerting) | Manual |
| Destination window | **Built and hard-won** — `destination_open is None` returns UNKNOWN "never scored", after the demo once reported exactly this as *closed 31 of 31* | **Built** | Passive → alert | Built |
| Bathymetry / chart | **Built** — inspects mesh loaders, finds none, declares `min_depth` inert | **Built** | Passive | Blocked on a free GEBCO download |
| Iceberg layer | **Built** — a test forbids the words *none*, *clear*, *zero* | **Built** | **Now built** — CPA alerts | **Now built** — bergs are on the chart with projected tracks |

**The uncomfortable one:** the USNIC position archive contains **exactly one
snapshot**. The CSV publishes *current* positions only and cannot be back-filled.
This is a missing-data failure **accumulating irreversibly right now**, and
nothing detects it.

### Y.2 Incorrect data — the project's strongest result
- **Detect.** The CDR writes spillover-suppressed coastal pixels as `0.0 %` inside `valid_range`. Measured over all 1,096 files: fires on **100 % of days**, mean **118.2** cells/day, max 488; the Bharati 200 km box affected on **43.2 %** of days; worst single-day no-input outage **59,350 cells**.
- **Degrade.** Suspect cells → NaN; the mesh fills from the parent. **Verified to move risk in the safe direction**: mean SIC in the Bharati box rises 46.8 → 54.6 % on 1 Dec. Masking makes the coast look *heavier*.
- **Notify.** Both readings are served with a QA toggle, so an operator can see them disagree — raw 0.0 % against quality-checked 30.7 %.
- **Recover.** **Incomplete, and disclosed**: parent fill returns 30–36 % where neighbours read 80–95 %. *"The fix removes a confident wrong answer; it does not yet give a confident right one."*

**And the incorrect data is still in the training set** — `features.py` does not read the QA flag, so the model was fitted with fabricated open water at the coast on 43 % of days in the box that decides the voyage.

**Second class — our own configuration.** The withdrawn 17.4-day figure came from a vessel config with beam 18.6 m (real 22.4) and max speed 14.0 km/h (real 30.4) — the ship at half speed. Root cause: **two copies of the vessel config**. **Specification errors dominated model errors at that stage, and no gate would have caught it.**

### Y.3 Delayed data
Age and received-time are **structurally absent** — behavioural test 2 is a deliberate PARTIAL, and it *fails* if anyone starts reporting an age that replay cannot have. Staleness escalation is designed, not built. **The horizon problem is physical, not engineering**: at 8.6 kn the transit is ~15.2 days against a D+9 ceiling, so **at departure the system cannot see the arrival**. Naming that as an information horizon is a stronger result than pretending to have predicted it — but the product does not yet *display* a horizon boundary.

### Y.4 Conflicting data
Detect is built for the *intra-source* case (the QA flag contradicting its own concentration field). **48A.16 source conflict has no implementation** — nothing compares two independent sources. The scale of what is not addressed is sourced and large: published algorithms disagree **~10× more at the ice edge** than in thick pack (SD 2.8–28.8 % at low concentration), and OSI SAF's own producers state their per-pixel uncertainty **excludes** melt-pond, thin-ice and weather-filter effects. ISRO's EOS-06 is live on completely different physics and would be an independent check — **and we are not using it**.

### Y.5 Model failure
| Model | Detection | Degrade | Notify | Recover |
|---|---|---|---|---|
| SIC U-Net | **None.** No OOD check, no domain-of-validity boundary. It does not run in the product at all | Structurally safe: it predicts a *correction*, so an untrained model outputs zero and reproduces the forecast | Absent | Fall back to the raw packed field |
| Uncertainty layer | **Does not exist** | — | — | **The demotion branch is pre-written with numeric gates** — coverage at lead 5 in [85 %, 96 %], width < 25 SIC-%, and the slider is *removed* rather than left as theatre. Writing the demotion before the numbers arrive is the best governance decision in the project |
| PolarRoute | **Built and inherent** — smoothing failure falls back to unsmoothed Dijkstra in 0.7 s, flagged | Built | Passive | Built |
| WDE17 drift | **Tested against the paper** (23/23) but **no trajectory error ever measured against an observed track**; no term for the >90 % SIC regime, which is where the Bharati approach spends its time | 72 h cap | **Now built** | Validation data is free and unused |

### Y.6 Network failure
Nothing to detect: the page makes **zero external calls**, test-enforced. **This is a property, not a feature** — there is no pack to go stale, so "offline duration" is infinite and meaningless. The honest limit is recorded: resumable Iridium sync "will only ever be tested over throttled localhost — say **tested under emulated link constraints**, never tested over Iridium."

### Y.7 Operator disagreement — handled better than most of this list
The system evaluates the master's intended route first and treats a rejection as a success; approval is versioned, attributed and never overwrites; divergence names the gate that flipped; out-of-order transitions are refused 409. **Three failures, plainly:**
1. **Attribution is theatre.** Any string is accepted. An approval whose `by` field is unverifiable is not an audit trail.
2. **The decision log is in-memory** and does not survive a restart.
3. **The system does not stop arguing.** The departure-vs-underway mode split is unimplemented. *A tool that keeps re-litigating a rejected route gets switched off in week two.*

### Y.8 How uncertainty is actually communicated
Data-mode badge in the API, on the page and inside the decision object · **health is derived, never scored** — there is no `route_score = 0.82` · **UNKNOWN never reads as a pass** and caps health at DEGRADED · **the MARGINAL band is the instrument's own uncertainty**: it was 5 points "for no reason at all", it is now **7.4 points**, the median `cdr_seaice_conc_stdev` in the 70–90 % band — note the direction, **the invented band was narrower than the retrieval's own uncertainty** · the ice limit is labelled an assumption *inside the gate's reason text* · both readings served where the data contradicts itself · absence reported as absence · **corridor C published as a non-result**.

**What it does not do:** no per-cell σ, no ensemble spread, no conformal band, no ETA distribution, and **no field carries a forecast-tier badge**, though the project's own rule says *"a field with no tier badge is a bug, not a styling omission."*

---

## Z. Regulatory and operational constraints

> **Scope statement, before any other sentence.** This is **advisory decision
> support**. It is **not** an ECDIS, not type-approved, not a chart, and it
> satisfies **no** carriage requirement. It does not steer. It is designed to sit
> *beside* a type-approved ECDIS, in ECDIS's own planning/monitoring idiom, and
> any claim that steps past that line is one a surveyor can dismantle in a
> question.

**SOLAS V/34 §1** (via MSC.99(73)): *"the master shall ensure that the intended voyage has been planned using the appropriate nautical charts and nautical publications … taking into account the guidelines and recommendations developed by the Organization"* — the mechanism that makes the non-binding A.893(21) practically mandatory. **V/34 master's discretion** is the treaty-level statement of our authority model. **V/19** carriage: we satisfy none of it and consume none of it. **MSC.232(82)** (performance) and **MSC.282(86)** (carriage schedule) are two instruments — *conflating them is a tell*.

**A.893(21)** four stages map onto the built workflow: appraisal → command centre and mission; planning → route, waypoints, review; execution → approval and "begin navigation"; monitoring → the clock, health and divergence. **The mode split is ECDIS's own, not our invention.** Two clauses name things treated as our own ideas: **§3.2.2** *"allowance for the increase of draught due to squat and heel effect when turning"* and **§3.2.3** minimum under-keel clearance — both researched, unimplemented, and the squat coefficients are `UNVERIFIED` and must not enter a margin calculation until checked.

**Polar Code Part I-A Ch.11.** **§11.3.2** — *"any limitations of the hydrographic information and aids to navigation available"*. **Our chart gate returning UNKNOWN because the mesh carries no bathymetry is therefore compliance, not pedantry.** It is the strongest regulatory sentence available to this project and should be quoted, not paraphrased. **§11.3.9** — operation remote from SAR; most of the area is **GMDSS Sea Area A4** and we model none of it, though the data is static and would fit in a pack. **Five of the nine §11.3 factors are things we do not do.** §11.3.3 wants extent *and type*; we model scalar concentration only, which single-handedly blocks POLARIS, ice-numeral arithmetic and egg-code output. §11.3.4 wants prior-year statistics surfaced — **we hold 1,096 real daily files and the captain never sees a climatology**.

**POLARIS.** Our 80 % limit is an invented stand-in. A search for a published ice-*concentration* operating limit for either modelled vessel found **none** — every classification document is indexed by type or thickness. We deliberately publish no RIO, **and the submitted deck's claim that we replaced the threshold with POLARIS is contradicted by the code**. Separately: the repo extracts the POLARIS table with line-level rigour and **never once uses the words Arctic or Antarctic** — its Antarctic applicability rests on a single unsourced line.

**Antarctic Treaty System.** 148 polygons = 142 ASPA + 6 ASMA; **33 intersect this corridor; zero are marine.** ASPA entry is permit-only; ASMA needs no permit. **Bharati sits inside ASMA 6 (Larsemann Hills)**, which India co-proposed, and **ASPA 163 is India's own Dakshin Gangotri**. The backlog originally proposed wiring these through `excluded_zones` as no-go geometry — **that would have refused to route to India's own station.** Reading the legal regime first produced the correct model: these bind shore operations, not the sailed track. Two adjacent corrections: **do not reach for CCAMLR MPAs here** (both adopted MPAs are outside 0–80°E and restrict *fishing*), and **no IMO Area To Be Avoided exists in Antarctic waters**. *Caveat:* the zero-marine finding is a property of *this corridor*, not the system; a Ross Sea route hits marine areas and that code path has never been run against real marine geometry.

**MARPOL** — reinstated in this audit (§A.5, §7A of the standards doc). Annex I Reg. 43: HFO carriage **and** use prohibited south of 60°S since 1 Aug 2011. **The entire modelled route south of 60°S is inside the ban**, so the vessel runs MGO/MDO and any energy figure assuming residual fuel is wrong. It is a single latitude test, cheaper than the protected-areas layer already built, and **not implemented**. Do not conflate with Reg. 43A (the Arctic ban). Annexes I/II/V make the Antarctic a **Special Area**; Annex IV restricts sewage by distance **from ice shelves and fast ice**, not merely from land.

**Liability.** The product is advisory, computing on data whose known error at the ice edge is ~10× its error in thick pack, on a mesh with no bathymetry, with no sea-state penalty in the published router, against an invented ice limit, using a force limit borrowed from a different hull. Every one of those is disclosed. **The disclosure is the liability strategy**, and it is the right one at this maturity — but it is not a substitute for professional-indemnity and limitation-of-liability terms. **None exist. This needs validation with a lawyer before any pilot.**

**The operator's authority, as five rules:** (1) the master decides, the system advises — no actuator, no autopilot path; (2) the system evaluates the master's intended route *before* proposing its own; (3) no plan becomes current without an explicit attributed approval, and approval never overwrites; (4) a rejected recommendation is a valid outcome and is recorded; (5) the system must state what it did not check. Four are implemented; the identity behind (3) is not verified, and the stop-arguing half of (4) is not built.

**Human-in-the-loop is not a hedge — it is the market's own posture.** StormGeo, at ~13,000 vessels, keeps 24/7 human route analysts precisely because full automation is not trusted at the edges.

---

## AA. Experimental validation plan

| # | Experiment | Status | Outcome |
|---|---|---|---|
| E1 | Route comparison: practice vs ours | **RESULTS** | **Null, and against us** |
| E2 | Multi-date regret sweep | not run | **The experiment that decides the pricing model** |
| E3 | Regret with QA-suspect cells impassable | not run | The flagship number depends on a cell we say not to trust |
| E4 | Connectivity: normal/constrained/disconnected | not run | Only "disconnected by construction" is demonstrable |
| E5 | Prediction: model vs baselines | **RESULTS** | +18.5 → +30.6 %, scoped as an upper bound |
| E6 | **Leakage ablation** | not run | **Highest value per minute on the list** |
| E7 | Stratified re-scoring (coast/MIZ/edge) | not run | Skill is never measured where the decision lives |
| E8 | Seed replication (≥3) | not run | No error bar exists on any comparison |
| E9 | Packed-CMEMS acceptance | blocked | Archive is 7 days deep and cannot be back-filled |
| E10 | Data-freshness sweep | not run | E1's two arms are the degenerate case |
| E11 | Decision experiment (time-to-react) | not run | **No human has ever used this system in a task setting** |
| E12 | Route risk vs ice limit | **RESULTS** | Reachability cliff at 45–50 %; resolution mismatch found |
| E13 | Vessel sensitivity | **RESULTS** | Identical track; cost differs |
| E14 | Iceberg trajectory error | not run | Never measured; validation data is free |
| E15 | Bandwidth: daily delta | **RESULTS (new)** | **7.8 KB gzipped, measured by building the payload** |
| E16 | Conformal coverage gate | not run | Pre-committed pass/fail already written |

**Five run, eleven not. Three of the five that ran produced results that constrain or embarrass the pitch. That ratio is the project's credibility and its problem at once.**

**E1 in full**, because it is the one that matters most and it went against us. *Hypothesis:* planning on fresh ice each morning beats planning once on departure-day ice. *Baseline correction:* the previous figure compared our route to a great-circle line — **a strawman, retired**; no master sails a straight line into pack ice. *Result:*

| Arm | Planned | Actual | Regret | Blocked | Mean SIC |
|---|---|---|---|---|---|
| STATIC | 8.58 d | **8.61 d** | **0.03 d** | 0 h | 5.9 % |
| STATIC-noQA | 8.58 d | 8.58 d | 0.00 d | 0 h | 5.1 % |
| DAILY (9 re-plans) | — | **9.00 d** | — | **9.6 h** | 6.4 % |

**Daily re-planning was slower** by 0.39 d, because re-planning from the ship's live position takes locally-optimal turns a single global optimisation avoids. Reported against ourselves, and *explained*: ~5,800 km of the route carries 6 % mean ice, so fresh information buys nothing there. **The caveat that must be spoken with the number:** elapsed time is floored to whole days, so the STATIC arm arrives on a day identified as a spillover artifact — the 0.03-day result depends on a cell we ourselves say to distrust, and the cheaper answer comes from the arm that *believes* the artifact. **What may be said:** "planning on stale ice did not cost this voyage time." **What may not:** "it never does."

---

## AB. V1 → current

| V1 | Weakness | Change | Now | Improvement |
|---|---|---|---|---|
| Great-circle baseline | Strawman — no master sails into pack ice | Baseline redefined as the same router on older ice | Honest regret measurement | Turned a flattering number into a real one (**and the real one is 0.03 d**) |
| 17.4-day transit | Two copies of the vessel config; beam and max speed both wrong | Single source of truth for vessel parameters | 8.58 d steaming | Withdrawn, not quietly corrected |
| `margin <= 5` MARGINAL band | Invented, and **narrower than the instrument's own error** | Measured from `cdr_seaice_conc_stdev` | 7.4 points | The band is now the retrieval's uncertainty |
| Maitri "closed 31 of 31" | A no-data artifact reported as a closure | Separate *unavailable* from *closed* | UNKNOWN with a reason | The system stopped inventing a finding |
| +27 % model gain | Epoch selected on the test set | Three-way split, scored once | +18.5 → +30.6 % | Withdrawn and re-earned |
| Ice raster, linear lat/lon | 2.92× longitude error at Bharati | True Mercator with cos(lat) | Correct geometry | A mariner would have seen it instantly |
| Router meets day-0 ice on day 9 | No time dimension | Time-aware search | Conditions at arrival time | **The forecast can finally reach the route** |
| Fuel ≡ time | Zero currents, dead wave term | Fuel per distance with ice and wave resistance | 14 % fuel for 72 % time | A real trade-off surface |
| No alerting | §13 had zero code | P1/P2/P3, nine fields | Built | The largest §-level absence closed |

## AC. Measured impact

**Measured:** 1,096 real daily files, 0 failures · spillover fires on 100 % of days, 43.2 % in the Bharati box · masking moves coastal mean ice 46.8 → 54.6 % (safe direction) · Bharati closed 23/31, approach 0/31 · regret 0.03 d, daily re-planning 0.39 d *slower* · reachability cliff between 50 % and 45 % · two ships, identical track, +1.28 d / −8.9 % fuel · model +18.5/+24.9/+22.1/+30.6 % over persistence · route solve ~9 s (PolarRoute) and ~2 s (live search) · **daily pack 7.8 KB gzipped, 0.09 s at Certus** · 133 tests.

**Not measured, and not to be claimed:** ship-days saved (the pricing anchor is N=3; the only measurement is 0.03) · iceberg trajectory error · false-positive/negative rates (no passability ground truth exists) · operator decision time (no human has used it) · useful offline duration.

**Never convert a target into a result.** The 50 KB/day sync budget is a target; the 7.8 KB pack is a measurement of a *different, smaller* thing and must be described as what it is.

## AD. Limitations, classified

**Acceptable now:** synthetic environment in the new console (labelled) · no live inference in the page · in-memory decision log · corridor-only scope · scalar concentration.
**Pilot blocker:** no pack/delta sync · no age or tier on any field · unverified identity on approvals · no GEBCO, so UKC cannot be checked · no sensor ingest · no persistent plan of record · leakage ablation unrun.
**Production blocker:** no liability terms · no key management for signed packs · two Python runtimes · no monitoring · no type-approval path for anything touching the bridge display.
**Long-term research:** compression/pressure risk (no product exists anywhere, no summer SH drift field, and Hibler strength is exponential in concentration) · growler detection (3.5 orders of magnitude below any satellite product) · Antarctic ice-type retrieval at navigation resolution.

## AE. Scalability

**1 → 10 → 100 vessels is not the growth axis, and saying so is part of the case.** India runs one expedition a year. Compute is not a bottleneck and should stop being discussed as one: the full pipeline is ~9 s for 824 cells, unsmoothed Dijkstra 0.7 s, a U-Net forward pass milliseconds. **The expensive parts are ingestion and training, which is exactly why they stay ashore.**

What actually breaks, in order: **the decision log** (in-memory, single-process — every other component scales by adding boxes, this one needs replacing); **rendering** (the legacy raster's 1.35× cell fudge does not survive higher resolution — the fix, drawing in the native polar-stereographic grid, also fixes the projection); **ingestion latency, not volume** (CDS/ERA5 queue latency for multi-decade requests is hours-to-days and appears in no plan).

**Operational scalability is the real limit.** One window per year means **one learning cycle per year** — a product needing three seasons of evidence needs three years, and no engineering shortens it. There is no second attempt: 100 ± 30 days, and one lost day ≈ 1 % of the season's hire. **Support does not scale with software** — the polar market's own answer is not to: Drift+Noise is 7 core staff after twelve years with the two best-known polar research ships as customers. And congestion here is **temporal, not spatial**: everyone wants the same December–April window, so recommending one route to every user manufactures correlated failure.

**The most likely thing to kill this project is institutional continuity, and there is a precedent**: ISRO's SCATSAT-1 Antarctic sea-ice product **stopped in May 2019 while the satellite operated until February 2021**. Funding and ownership, not technology. That is the argument for reuse-first — PolarRoute, the CDR and the ATS register all outlive us.

## AF. Feasibility

**Hackathon MVP — finishable, ~11 people-days, in priority order:** leakage ablation (1 d, resolves the headline either way) · move the archive off the worktree symlink (0.25 d, a demo-day failure with no obvious cause) · GEBCO + TID into the mesh (2 d, closes the chart gate — smallest gap, largest regulatory payoff) · multi-date regret sweep (1.5 d, the number the business case rests on) · stratified re-scoring (0.5 d) · USNIC weekly cron (0.5 d, stops irreversible loss) · Bharati table at native 25 km (1 d, survives a judge with a ruler) · persist the fuel-objective run (0.25 d) · **reconcile the deck with the repo (1 d, the highest-risk finding in this audit)**.

**Not finishable, and must not be promised:** the calibrated ensemble, offline pack and delta sync, sensor integration, iceberg trajectories validated against observation, POLARIS compliance.

**Finale discipline:** weights, calibration tables, results, figures and scenario packs are **frozen and travel on USB**. Nothing is regenerated at the nodal centre — *"re-run training in a 36-hour window" is not a thing.*

**Pilot (one season):** feasible; 2–3 FTE for ~6 months plus presence through the season. **The binding constraint is calendar, not capability.** **Production:** not on a student timeline — realistic entry 2029, gated on a completed pilot. **Fleet scale:** not a goal.

## AG. Cost

**Hackathon: ₹0 infrastructure spend, and it is checkable** — Kaggle free T4, GitHub Actions free tier, all data free, MIT routing engine, existing laptops. **The entire result set in this repository was produced at zero infrastructure cost.**

**Pilot ₹20–50 lakh**, people-dominated (2–3 FTE) — which roughly breaks even at best against the ₹40–80 lakh season-contract estimate, *and only if N=3 saved days is real*. **Production ₹15–35 lakh/yr recurring**, of which maintenance is the line usually underestimated: NSIDC-0051 stopped forward processing 31 Dec 2025, NSIDC-0081 was retired 18 Jun 2026, and CMEMS deprecating a flag broke our harvest once.

**Iridium — the number the design turns on.** Measured payloads against three effective rates:

| Payload | @704 kbps | @64 kbps | @7 kbps |
|---|---|---|---|
| **7.8 KB measured daily pack** | 0.09 s | 1.0 s | 8.9 s |
| 76 KB mesh block | 0.9 s | 9.7 s | 89 s |
| 1 MB corridor refresh | 11.9 s | 2.2 min | **20 min** |
| 60 MB model weights | 11.9 min | 2.2 h | **20 h** |

Airtime *pricing* for this vessel is unknown — **and unusually, it is obtainable**: the charter bills comms as-per-actual, so the customer holds the invoice. **The cost argument that does not depend on price:** a season at the measured pack size moves about **1 MB**. The comparison that matters is not "we are cheaper on airtime" but **"we are possible on this link, and a live-API dashboard is not."**

## AH. Deployment

**Laptop demo (today):** one uvicorn process, no database, no external calls. *If it refuses to start, that is the product working.* Three defects before demo day: the archive symlink, the stale `.venv-demo`, and — now fixed — that nobody had opened the page in a real browser.

**Onboard pilot:** x86-64, 4+ cores, 16 GB, no GPU — justified by measurement, not guessed (pipeline ~9 s, live search ~2 s, U-Net forward pass ~0.3–1 s CPU). **A bridge laptop is genuinely sufficient, and saying so with numbers is stronger than specifying a workstation.** Weights and calibration tables ship **by USB at Cape Town and are never part of a delta sync**; a weights update mid-voyage is not a supported operation. **Sneakernet is a first-class path, not a degraded one** for a once-per-season voyage. Maps must move to EPSG:3031 for the southern leg and the BAS Antarctic Digital Database for the coastline, which separates ice-coastline, rock-coastline, grounding line and ice-shelf front — operationally real distinctions at Bharati.

**Vessel deployment** adds persistent identity, alert acknowledgement and escalation, and sensors **in standards order, not preference order**: the IEC 61162 data-exchange layer **before** any sensor, because skipping it makes every later sensor a bespoke integration. Then GNSS and gyro (cheapest, and they make *monitoring* mean something), AIS (spec is free), echo sounder (the live cross-check that catches a wrong chart), radar/ARPA last — and it is the one that matters most for ice, because growlers do not transmit AIS.

## AI. Post-hackathon roadmap

**0–3 months — close the evidence gaps, not the feature gaps.** Leakage ablation; GEBCO; multi-date regret sweep; stratified re-scoring; three seeds; USNIC cron; archive off the symlink; persistent log; real authentication. **One structured walkthrough with an ice-experienced officer, recorded — nothing has ever been tested with a user.** Open NCPOR as a *research collaboration, not a sales call*, and ask two questions we cannot answer ourselves: what ice information they use today, and what the charter day rate is. *Exit:* the ablation is published either way; the regret sweep has a p50 and p90; the chart gate passes or fails for a reason that is not "no data"; **zero contradictions between deck and repo**.

**3–6 months — production model and the offline tier.** Full-archive ingestion; 5-member ensemble; stratified conformal calibration; the packed-CMEMS acceptance test; pack build/sign/delta, staleness escalation, climatology mode. *Exit:* run the pre-committed coverage gate and **publish the demotion if it fails**; a full re-plan with networking disabled; the measured daily delta published, pass or fail.

**6–12 months — shore desk and a shadow season.** Ice-type output (unlocks POLARIS, ice numerals and egg-code together); iceberg trajectories validated leave-one-berg-out against BYU; SAR-remoteness and places-of-refuge tables; GNSS + AIS over IEC 61162; source-disagreement with EOS-06. **Run a shadow season**: produce a daily advisory for the 2027–28 expedition that nobody acts on, then write the post-season report. *A shadow season costs the customer nothing and produces the only asset that opens any other door.*

**12+ months.** 2028: first advisory season in the loop; success = renewal. 2029: Maitri II construction across a coast our own data says was shut 31 of 31 December days — position as **scheduling-risk software for a fixed-deadline programme**, not as a router. **The polar research vessel design window is open now and will close** — software specified during design gets a place on the bridge; software written after delivery gets bolted on.

**This roadmap does not end with "future scope."** It ends with a renewal decision by a named customer against a written report, and every stage has an exit condition that can fail.

## AJ. Startup path · AK. Market entry · AL. Revenue

**The wedge is in the customer's own tender.** NCPOR's charter tender is public: one vessel, `100 ± 30 days`, **financial bid = day rate × 100 days**, operating box 66–70°S / 80°E–06°E — *our corridor, written by the customer*. It contains an ice-failure clause: if ice makes overboard discharge unsafe, cargo goes by boat and barge *"provided the conditions of the coast permit such discharge."* **The contract anticipates ice stopping the discharge and has no clause for when the fallback is also blocked.** And **§11 requires the vessel to carry "ice-information receiving equipment"** — India buys the receiver and owns nothing on the other end of it. That is not a need invented for a pitch; it is a line item in a live government tender. Our measurement lands on the clause: Bharati closed 23 of 31, first closure **2 December — the second day of the month**.

**Stages.** (1) *Research tool* → no revenue; exit is **one named person inside NCPOR using an output to answer a question they actually had — a use, not a demo**. (2) *Operational pilot* → season service contract via GeM; exit is a completed season with a written verification report and a renewal. (3) *Multi-programme* → gated on whether that report is good enough to show a foreigner.

**Procurement mechanics favour a student team** — the single most practical fact here. A DPIIT-recognised startup on GeM is exempt from prior-turnover, prior-experience and EMD requirements under GFR Rule 173(i). **The normal reason a two-year-old company cannot bid is waived by rule. It is a form, not a fight.**

**The pricing ceiling is institutional and cuts both ways.** INCOIS — same ministry — has given away ship-route advisories since 2013. *Against us:* we cannot charge Indian mariners for an advisory the ministry already provides free, so any deck showing Indian per-vessel subscription revenue is wrong. *For us:* **an Antarctic ice extension to a national forecasting service is not a new idea to sell; it is an existing programme to extend.**

**Recommended model: a per-season programme service contract, priced as N saved ship-days, with the post-season verification report as a contracted deliverable.** It matches how the customer already buys; it is priced in the customer's own units (`N × their charter day rate` — we do not know their day rate, **they do**); it puts us present during the 100 days that matter; it survives the free-advisory precedent; and it renews annually against a written report, so **the evidence loop and the revenue loop are the same loop**. **Reject** per-vessel subscription (there is no fleet), enterprise licence (sells the wrong thing), and API/data services outright (**the raw ice field is not a product anyone can sell, and a judge who knows the field will say so**).

**The condition under which this fails, written in advance:** if the multi-date regret sweep shows saved ship-days near zero, the N-days pricing is dead and the honest fallback is to price on risk avoided and decision quality — a weaker, slower sale to a research institute rather than a logistics office. **That branch is written now so it cannot be quietly renegotiated after the numbers arrive.**

**The honest ceiling:** at full success this is a **USD 1–2 M/year specialist company of 8–12 people**, not a venture outcome — about the size Drift+Noise reached after twelve years with the two best-known polar research ships as customers. **Put that number on the slide.** A judge who has done the arithmetic will trust everything said afterwards; a hockey stick can be disproved in one question. **Single-market concentration is unmitigated:** if NCPOR declines, there is no substitute customer.

## AM. Future scope

**NOW** — a real satellite record audited and corrected; a real corridor solved by BAS's own router; the destination-window reframing; nine gates where six honestly say UNKNOWN; a route-health state that moves on evidence and names what moved it; the §4 workflow in ECDIS's idiom; versioned attributed approvals; protected areas modelled by legal regime; a trained model that beats the baseline that matters, scoped; **and now a time-aware router, first-class icebergs, alerting, and a measured pack size**. *That is a complete product thesis: a decision that names its own evidence and refuses to certify what it has not seen.*

**NEXT (0–12 months)** — every item is a download, a wire-up or a known engineering task; none needs a research breakthrough. The one genuine research risk, whether calibrated uncertainty survives coverage testing, has a written pass/fail rule and a demotion path.

**FUTURE** — time-expanded routing on real forecast fields · **compression/ice-pressure risk**, genuine white space and a genuine build-from-scratch risk (no operational Antarctic product exists, POLARIS has no compression term, there is no observational summer SH drift field) · Sentinel-1 ice edge and small-berg catalogues, which still do **not** touch the growler problem · a **detection-degradation advisory** that turns an honest limitation into an output — we cannot see growlers, but we can forecast when the *lookout* is blind · **ship-sensor feedback**, which is what turns software that ships once into something that gets better every voyage · local LLM as a bounded addition *on top of* the pipeline, never as a replacement for real models · **Baymax is unresearched, not merely unbuilt** — it stays on the future page, badged.

## AN. Competitive comparison

Legend: ● strong · ◐ partial · ○ absent · **†** better than us.

| Dimension | IcySea | PolarView | Ice services | ECDIS + overlay | StormGeo | PolarRoute | **This system** |
|---|---|---|---|---|---|---|---|
| Antarctic focus | ● | ● | ◐ | ○ | ○ | ● | ● |
| Sea-ice support | **●†** SAR, metres | ● AMSR2 | **●†** analyst | ◐ | ◐ | ◐ | ◐ 25 km, QA-corrected |
| Iceberg trajectory | ○ | ○ | ◐ positions only | ○ | ○ | ○ | ◐ **drift + CPA vs future track; error never measured** |
| Route planning | ○ | ○ | ○ | ◐ manual | ● mid-latitude | **●†** | ● by reusing PolarRoute |
| Dynamic re-planning | ○ | ○ | ○ | ○ | ● | ○ no time dimension | ◐ **time-aware search; measured slower on one test** |
| Vessel context | ○ | ○ | ○ | ◐ | ● | **●†** | ◐ real dimensions, borrowed force limit |
| Low bandwidth | **●†** in service | ◐ | ◐ | ● | ◐ | n/a | ◐ **7.8 KB measured, never tested on a link** |
| Offline | **●†** on real ships | ○ | ○ | ● | ◐ | ● | ◐ zero external calls |
| Explainable risk | ◐ | ◐ | ◐ | ◐ **CATZOC** | ◐ | ○ | **●** nine gates, UNKNOWN never passes |
| Integrated decision support | ○ | ○ | ○ | ◐ | ● own market | ○ no interface | **● the gap we occupy** |
| Deployment | commercial SaaS | portal | national service | **●†** type-approved | subscription + analysts | MIT library | **prototype, nothing deployed** |

**Where each is genuinely better.** *IcySea* — SAR in metres against our 25 km, decisive for close-quarters work; they have solved low-bandwidth polar distribution, which we have only designed; they are on real ships and we are a prototype. **We have never tested IcySea and will not claim it is worse.** Our claim is adjacent: *"They tell you what the ice is. We tell you whether your destination will be open on the day you arrive."* One condition narrows their strength: SAR tells you where the edge is **now**, and the Bharati decision is made 3–7 days out. *ECDIS* — **type-approved and legally sufficient; we are not, and must never imply otherwise**, and its CATZOC is better chart-confidence practice than anything we have. *PolarRoute* — the state of the art, **which we reuse rather than compete with**; arriving with "we used BAS's own tool and here are three things it does not do" is far stronger than a from-scratch A* that invites the question of why the field's open tool was ignored. *Ice services* — authority and analyst judgement; **an automated product does not replace a national ice service.** *StormGeo* — maturity at 13,000 vessels, and **their 24/7 human fallback is evidence for our position, not against it**.

**Where we are ahead, and only there:** closing the loop from observation to a versioned, approved, monitored decision for a named vessel on a named day; a health state that is derived rather than scored, where a gate we cannot evaluate caps confidence instead of being silently omitted; the destination-window reframing backed by measurement; detecting that the underlying data lies at the coast and correcting it in the safe direction; and protected areas modelled by legal regime where the naive implementation would have refused to route to India's own station.

**Two caveats.** **Nothing here has been benchmarked head-to-head** — every ○ for a competitor means "not documented as present", not "tested and absent". And **the nearest precedent is Indian and is not a competitor**: an optimum-route study for the Bharati–Maitri leg (*Polar Science*, 2021), deterministic, no uncertainty. *That is a precedent proving the problem is recognised inside the Indian programme. Say it that way.* The white space — no published study propagating sea-ice forecast uncertainty into a routing decision — is filed at **medium confidence** because the search was cut short. **Re-verify before claiming novelty; it is the easiest claim in this document to disprove and the most expensive to be wrong about.**

---

## AO. SIH judge score

Scored as a hostile judge who has read the code, not the slides.

| Axis | /10 | Why that number |
|---|---|---|
| Problem relevance | **9** | Exactly PS-26059, on the corridor the customer's own tender names |
| Problem depth | **9** | Root cause runs seven layers deep and reaches "the delivery point is not a port"; the crossing is shown to be the *wrong* problem |
| Problem scale | **5** | One ship, one voyage a year. Honest, and small |
| Urgency | **6** | Why-now is real (free data plane, open engine, a 2029 station deadline, a non-stationary ice regime) and not a crisis |
| User clarity | **8** | Primary user, decision-maker and economic buyer separated and evidenced from the tender — but **no user has ever seen it** |
| Innovation | **7** | The first-class UNKNOWN is genuine and structural. It is not flashy, and a judge looking for novelty-as-spectacle will undervalue it |
| MVP focus | **7** | One user, one decision, one workflow, one outcome — now. It sprawled before |
| Technical quality | **8** | 133 tests; real physics; three of my own errors caught by property tests rather than by a demo |
| Research credibility | **9** | The strongest axis. Prompt-compression audit, POLARIS applicability, standards correction, and a document that argues against its own project |
| Differentiation | **7** | Defensible and narrow. The loop from observation to versioned approved decision is genuinely unoccupied |
| **Measurable impact** | **4** | **The weak axis.** The pricing anchor is 3 saved ship-days; the only measurement is 0.03, and daily re-planning measured *slower* |
| Feasibility | **8** | Everything on the 0–3 month list is a download or a wire-up |
| Usability | **6** | Dense, professional, ECDIS idiom — and **untested with a navigator** |
| Deployment realism | **6** | Bridge-laptop spec justified by measurement; the pack tier is designed, not built |
| Scalability | **5** | Software scales; the market does not, and one learning cycle per year is the binding limit |
| Adoption | **5** | One institutional customer, slow procurement, no substitute if they decline |
| Security | **4** | Sign-in accepts any string; unsigned packs; no key management |
| ROI | **4** | Cannot be computed: the customer's day rate is unknown and saved days are unproven |
| Startup potential | **5** | A good 8–12 person company, not a venture outcome — and we say so |
| Presentation clarity | **6** | The story is strong; **the submitted deck contradicts the repo in eight places** |
| Defensibility | **8** | Almost every attack is already written down in our own documents |

**Total 146 / 210 → 70 / 100.**

**Current winning potential:** strong shortlist, plausible finalist, **not yet a winner**. The gap is not technical — it is that the two things judges reward most, *measurable impact* and *a demo that matches its claims*, are our two lowest scores, and both are fixable in days rather than months.

**Biggest weakness:** we cannot yet prove a saved ship-day. Everything commercial rests on N=3 and the only measurement is 0.03.

**Biggest competitive advantage:** a route-health state derived from nine named gates in which a gate we cannot evaluate **caps confidence instead of being omitted**. Every competitor's visual language assumes green-means-fine; they cannot bolt this on.

**Most dangerous judge question:** *"Your deck says you replaced the 80 % threshold with POLARIS. Show me the RIO number."* There isn't one, the code still says `"max_ice_conc": 80`, and our own research says a RIO cannot be computed for this hull. **Fix the deck before anything else.** Runner-up: *"You say AI-enabled routing — which line on this chart did the model move?"*

**Most impressive aspect:** the project found a bug in NOAA/NSIDC's own product as it affects this corridor, quantified it over 1,096 files, fixed it in the safe direction, and then said the fix is not yet a right answer.

**What a finalist team would do better:** run the ablation, run the regret sweep across a season, and put one navigator in front of the screen. All three are days of work and all three convert opinion into evidence.

**What could cause rejection:** a deck claim disproved live. Nothing else here is fatal.

**What would make judges remember us:** *"Six of our nine safety questions are grey. Grey means we did not measure, and a gate we cannot evaluate is never a pass. Here is the dataset each one needs."* No other team will say that, and it is the sentence that makes the rest believable.

## AP. Strengths · AQ. Weaknesses · AR. Attack points

**Strengths.** UNKNOWN as a first-class state, enforced in code. A data-quality finding in the incumbent satellite product, measured across the whole archive and corrected in the safe direction. The destination-window reframing — 23/31 against 0/31 — which relocates the problem from the ocean to the last 100 km. Reuse of BAS's own router rather than a home-grown one. A decision record that is versioned, attributed and names the assumption that changed. Research documents that argue against the project.

**Weaknesses.** No proven saved ship-day. No user has ever used it. The ice limit is invented and reachability has a cliff on it. Fuel figures use another hull's polynomial. The model is untuned, single-seed, trained on QA-contaminated coastal data, with a leak of unknown magnitude in its headline. Attribution is unverified. The plan of record does not survive a restart. **And the submitted deck contradicts the repository in eight places.**

**Attack points, with the honest answer to each.**
| Attack | Answer |
|---|---|
| "POLARIS — show the RIO" | We publish none. No row exists for this hull; guessing spans 40 RIO points. **The deck was wrong and is corrected.** |
| "Show me an iceberg trajectory error" | We have never measured one. The physics is tested against the paper; the validation archive is free and unused. **Roadmap, said out loud.** |
| "Your 30.6 % — is that leak-free?" | Not established. It is an upper bound; the ablation is written and unrun, and if it fails we retire the number. |
| "Is the model running in this screen?" | No. The screen serves the router and the environment. Weights are not in the repo. |
| "8.6 days?" | Ideal steaming only. A real expedition voyage is two to three weeks. |
| "Different ships, different routes?" | No. Identical 41-leg track; only cost differs. **Vessel awareness is proven for cost, not for track.** |
| "Fuel-optimised?" | In the published corridors, fuel and time were collinear. In the new router they are not — 14 % fuel for 72 % more time. Say which one you are showing. |
| "This environment is fake" | Yes, and it says so on the page. The **physics** is real and the initial conditions are synthetic; the 2019 replay console at `/legacy` is the real-observation evidence. |
| "Unplug the network" | Zero external requests, test-enforced. Do **not** claim tested-over-Iridium. |

## AS. What makes it memorable

One sentence and one gesture. The sentence: **"A gate we cannot evaluate is never a pass."** The gesture: approve a route, move the clock, watch health go INVALID and the console name the gate that broke — then move it back and watch it say nothing, because nothing changed.

## AT. New PPT blueprint

Audit of the current six slides — **KEEP / CORRECT / REMOVE / ADD**:

| Slide | Verdict |
|---|---|
| 1 Title | **KEEP** |
| 2 Solution idea + approach | **CORRECT**: remove "predicts the drift of **live** icebergs"; remove "re-plans automatically"; scope the 18.5/30.6 figures |
| 3 Technical / feasibility | **CORRECT**: "1,096 files… harvested every day, zero failures" merges two pipelines and one failed; the compression figure matches no run; "76 KB full pack" is a sample box. **Replace with the measured 7.8 KB daily pack** |
| 4 Impact | **ADD numbers** — it is currently qualitative only |
| 5 Results | **KEEP** the RMSE table, **ADD** the leakage caveat in the same eyeline |
| 6 Research | **REMOVE the POLARIS claim.** Replace with the POLARIS *applicability* finding, which is a stronger result |

**The rebuilt narrative** — problem → consequence → user → gap → why now → solution → differentiation → proof → architecture → impact → feasibility → deployment → business → future, compressed into six AICTE slides:

1. **Title** — unchanged.
2. **The problem is the last 100 km.** One number: *Bharati's own cell was closed 23 of 31 December days; the approach 100 km north was open 31 of 31; the 5,800 km crossing averages 6 % ice.* Then the consequence: one held day ≈ 1 % of the season's charter, and the customer's own tender has no clause for when the fallback is also blocked.
3. **What the system does.** The nine gates with six grey, and the sentence *"a gate we cannot evaluate is never a pass."* The killer demo in one line: approve, advance the clock, the gate that broke is named.
4. **Proof.** RMSE table with its caveat; the spillover finding (100 % of days, 43.2 % in the Bharati box, corrected in the safe direction); the reachability cliff; **the null result reported against ourselves**, because a team that publishes its own negative result is the team a judge believes.
5. **Architecture and feasibility.** Two tiers, router aboard, **7.8 KB measured daily pack, 0.09 s at Certus**; bridge laptop, no GPU; zero infrastructure spend to date.
6. **Business and honest limits.** Season service contract priced in the customer's own units; the 8–12 person ceiling stated; and the three things we have not proven — a saved ship-day, an iceberg trajectory error, and one navigator's opinion.

**Impact-first rule for every slide:** lead with what changed for the user, not with what technology was used. **Numbers-first:** every figure tagged Measured / Sourced / Derived / Target.

---

# FINAL VERDICT

**What we actually have.** A decision layer that is better than the competition will bring: nine named gates, a health state derived rather than scored, UNKNOWN that caps confidence, versioned attributed approvals, and divergence that names the assumption that moved. A real satellite record audited to the point of finding and quantifying a defect in the incumbent product. A reused state-of-the-art router. A trained model that beats the baseline that matters. And now a time-aware router in which the forecast can finally reach the route, first-class icebergs compared against the ship's *future* track, alerting with all nine mandated fields, and a measured offline pack.

**What we thought we had but do not.** POLARIS-based limits (we deliberately publish none). Iceberg trajectory prediction as a *capability* (the physics is tested; the error has never been measured). Automatic re-planning (the published router has no time dimension, and daily re-planning measured *slower*). Fuel-efficient routing in the published corridors (fuel and time were collinear). A validated forecast (the headline contains a leak of unknown magnitude). An offline product (a page with no network calls is a property, not a sync design).

**What is missing.** GEBCO and therefore under-keel clearance. Age and tier on every field. Source-disagreement. A durable, authenticated plan of record. Sensor ingest. Ice type, which alone blocks POLARIS, ice numerals and egg-code output. A measured saved ship-day. A user.

**What must be fixed, in order.** The deck, because it is the artefact judges read first and it contradicts the code in eight places. The leakage ablation, because our largest number is our most contaminated. The archive symlink, because it is a demo-day failure with no obvious cause. Then GEBCO, then the regret sweep.

**What is genuinely strong.** The refusal to certify what has not been measured — implemented in code, enforced by tests, and carried into the interface as the difference between grey and red.

**What judges will attack.** POLARIS. The 30.6 %. The absence of a measured impact. All three have honest answers already written.

**What gives us a chance to win.** No other team will stand in front of a judge and point at six grey lights. Doing that, and then naming the exact dataset each one needs, converts an incomplete system into a credible one — and it is the only posture that survives a judge who knows the domain.

**What must be proven before claiming victory.** That the model's skill survives a causal background. That a saved ship-day exists. That a navigator, given this screen, decides faster or better than with an ice chart. Until those three, this is an exceptionally well-evidenced prototype — which is the right thing to be, and should be said in those words.
