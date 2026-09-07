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
