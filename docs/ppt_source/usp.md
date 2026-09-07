# USPs, killer feature, competitors — working draft

Rule for this document, same as `DIFFERENTIATION.md` and `TRUE_CLAIMS.md`: if a
claim is marked **BUILT**, it runs today and the file that proves it is named.
If it's marked **ROADMAP**, say so in the sentence that makes the claim, not in
a footnote. Nothing here gets to be vague about which one it is.

Sources cross-checked while writing this: `docs/DIFFERENTIATION.md` (D1-D7),
`docs/TRUE_CLAIMS.md` §1/2/3/5/6, `docs/COMPETITIVE_ANALYSIS.md`,
`docs/WEAKNESS_ANALYSIS.md` §5/§7, `docs/ISIH_RESULTS.md`,
`isih/protected_areas.py`, and the CMEMS harvest log (`data/cmems_harvest.log`,
`data/cmems_forecast_archive/`). Where DIFFERENTIATION.md's D1-D7 describe
something not yet in the code, I checked the code (`grep` for `excluded_zones`,
for a fusion/disagreement module) before writing BUILT or ROADMAP — I did not
take the architecture doc's word for its own status.

**One correction that has to happen before D6 goes on a slide:** DIFFERENTIATION.md
says "CMEMS is our base field... a bias-correction head on CMEMS itself."
ISIH_RESULTS.md says, in its own words, the background used for the trained
+18.5%–+30.6% numbers is **GLORYS12, a reanalysis, not CMEMS's operational
forecast** — and says so as the sharpest question the team expects to be
asked. The CMEMS forecast-cycle archive (`data/cmems_forecast_archive/`) only
starts 2026-08-31, seven days of files as of today — nowhere near enough to
retrain and re-score against real CMEMS forecast cycles yet. So: **we beat
persistence and we beat raw GLORYS12, measured. We have not yet beaten CMEMS's
own operational forecast** — that comparison is queued, not run. Say the
first two on the slide. Do not let "CMEMS is our base field" imply the third
happened.

---

## 1. D1–D7, scored

Format: the claim in one sentence — hardest evidence — BUILT/ROADMAP — how it
survives a hostile expert.

### D1 — Uncertainty reaches the routing decision

**Claim:** the route changes when the ice model is unsure, not just the shading.

**Hardest evidence:** `meshiphi`'s (PolarRoute's) own `IceNetDataLoader` runs
`df.drop(columns=[...])` on `sic_stddev` and `ensemble_members` — verified by
reading installed source, not inferred. The field's own open-source router
throws uncertainty away before it ever reaches a route.

**Status: ROADMAP.** `ISIH_RESULTS.md` says it in five words: "no uncertainty
layer yet." One model per horizon, one seed, no ensemble, no conformal bound.
`TRUE_CLAIMS.md` §5 lists "five-model ensemble + conformal calibration" as
priority 3 of the honest roadmap, "specified with a pre-committed pass/fail
gate" — a plan, not a result. No fusion or disagreement code exists in `isih/`
either (checked by grep).

**Survives a hostile expert on two things, fails on a third if pushed today:**
survives on "the incumbent throws this away" (true today, in someone else's
code, cheap to demonstrate live by installing PolarRoute and reading the
loader). Survives on discipline: the gate numbers (coverage in [85%, 96%] at
lead 5, bound width <25 SIC-%, must beat inter-source disagreement as a free
alternative) and the written demotion clause are pre-committed, which is rarer
than the feature itself. **Fails** if a judge asks "show me the slider moving
the route" — it can't, yet. Answer honestly: "not built, here is the gate it
has to pass, here is what we do if it fails."

### D2 — Physics-first iceberg drift, ML residual as a stated stretch

**Claim:** iceberg drift is real physics first, with a named blind spot, not a
black box.

**Hardest evidence:** Wagner/Dell/Eisenman (2017) closed-form drift model,
reproduces the paper's own coefficient table and its 765 m critical length —
**23/23 tests pass** (`models/iceberg/test_drift.py`) — and runs today on the
real USNIC catalogue: 33 tracked icebergs, 15 inside the routing corridor,
including a 3,037 km² berg beside Bharati's approach.

**Status: BUILT (physics baseline).** The gradient-boosted residual on top of
it is `ADR-008`, not yet trained — that part is ROADMAP.

**Survives well.** It's a real published physics model, tested against its
own paper, run on a real named-iceberg catalogue today — not a toy. The
disclosed blind spot (growlers and bergy bits, the ice that actually holes a
hull, are ~3.5 orders of magnitude smaller than anything tracked from orbit)
pre-empts the obvious attack instead of hiding from it.

### D3 — Multi-source disagreement widens caution automatically

**Claim:** where ice sources disagree, the route gets more cautious by itself.

**Status: ROADMAP.** No fusion or disagreement module exists in `isih/` today
(checked directly). The grounding fact — Copernicus systematically
underestimates concentration versus regional charts in the marginal ice zone —
is real and citable (2025 Alaska ice-chart paper), but nothing in this repo
acts on it yet.

**Survives poorly if presented as built; survives fine as "we know exactly
what to wire up and why it matters."** Don't lead with this one.

### D4 — Bandwidth-honest, offline-first design

**Claim:** the vessel tier runs with zero connectivity, and that's a design
constraint, not a slide aspiration.

**Hardest evidence, partial:** the actual demo boots in 3.1 s, makes no live
API calls at runtime, and **refuses to start** if a day's satellite file is
missing rather than render a gap as data. That refusal-to-fake is real and
checkable right now by pulling the network cable and restarting it.

**Status: MIXED, and the CI-enforced budget is ROADMAP.** `WEAKNESS_ANALYSIS.md`
§6 is explicit: the 50 KB/1 MB CI gate, pack signing, and resumable Iridium
delta sync are "demo-only," and pack signing specifically is called
"theater — no key-management story." Delta sync has only ever run over
throttled localhost, never Iridium.

**Does not survive as "we solved offline sync."** Survives as "the demo
already lives by the rule it claims to live by (no live calls, fails loud on
missing data), and the harder parts — the CI budget gate, delta sync, signing
— are named, not hidden, as not done." A hostile expert who reads
`WEAKNESS_ANALYSIS.md` will find that admission before they find the gap
themselves, which is the point of writing it down first.

**Also relevant to how strong this can ever be as a USP:** IcySea, a real
commercial polar-ice app (Drift+Noise GmbH / AWI spin-off, co-developed with
the Norwegian Met Institute), already advertises data delivery "tested and
proven with an Iridium connection." So "we thought about bandwidth" is not
white space — a real competitor ships it. What we could still have that they
don't is the full routing engine running locally (not just charts), but that
piece is exactly the ROADMAP part above. Don't claim more than the demo does.

### D5 — Corridor- and vessel-specific: MV Vasiliy Golovnin, Cape Town → Bharati/Maitri

**Claim:** built for this ship and this run, not "Antarctica" in general.

**Hardest evidence:** the vessel is the one NCPOR actually charters (IMO
8723426, confirmed via ISEA press releases), the corridor is the real one, and
the destination-window result (below) is scored against this specific ship's
draft and this specific approach.

**Status: BUILT**, as scope discipline — the demo and the ISIH results are
already corridor- and vessel-scoped, not generic.

**Survives well, with a size limit.** An MoES/NCPOR audience recognizes this
ship and this run instantly, so fidelity here is verifiable in a way
"circumpolar Antarctica" isn't. It is scope discipline, not a technical
invention — any team that reads the same press releases can claim the same
scoping. What makes it hard to *fake* is that the vessel's real dimensions and
the real 31-day December window are what the destination-window number below
is computed against — copying the claim without doing the computation is
visible immediately under questioning.

### D6 — Honest quantification, including where we decline to quantify

**Claim:** no number goes on the slide that we can't defend under
cross-examination.

**Hardest evidence:** three numbers were already withdrawn or corrected in
this project's own history — a 17.4-day transit computed at half the ship's
real speed, corrected to 8.6 days; a route-figure caption claiming it "bends
around the thickest ice" when it measurably crosses *more* average ice (19.6%
vs 8.4%); and the straight-line baseline, replaced with an honest one after it
made the system look better than it is.

**Status: BUILT as a practice**, evidenced by the corrections above and by the
fuel/thickness/bathymetry/forecast-horizon disclosures already written into
`TRUE_CLAIMS.md` §4 and `DIFFERENTIATION.md` D6 (fuel reported relatively
only; thickness a literature lookup, not a measurement; bathymetry disclosed
predicted-vs-surveyed). **Caveat, per the correction at the top of this
file:** the CMEMS-vs-our-model comparison in D6 is still aspirational —
today's numbers beat persistence and raw GLORYS12, not CMEMS's own forecast.

**Survives very well precisely because it costs something.** A team that
prints a confident absolute fuel number and a single authoritative ice
percentage looks more finished for about ninety seconds, until a judge asks
where the number came from. This is the one category where disclosing a
limitation is not a tax on credibility, it *is* the credibility.

### D7 — PolarRoute reused, three extensions named

**Claim:** we use BAS's own open-source polar router and extend it in three
specific, checked places.

**Hardest evidence:** PolarRoute installs in ~90 s with binary wheels and runs
a full pipeline in ~9 s — verified, and the working demo serves real
PolarRoute routes today (8.6-day computed transit, Cape Town → Bharati, on
real satellite ice).

**Status: reuse is BUILT. All three named extensions are ROADMAP.**
Uncertainty-aware thresholding needs D1 (not built). The iceberg hazard layer
via PolarRoute's `excluded_zones` hook is not wired up — grepped, no hits in
`isih/`. The 12-run dominance-filtered sweep is a designed evaluation
protocol, not a routine that has run.

**Survives as "we reused the field's own tool instead of reinventing A*,
which is the right call and a judge who knows the field will recognize it."**
Does **not** survive as "and we already extended it three ways" — say "reused,
running, and here are the three specific gaps we're closing next," not "and
here are our three extensions."

---

## 2. Ranking

| Rank | USP | Built today? | Why it lands where it does |
|---|---|---|---|
| **1 (extremely strong)** | Destination-window result — Bharati closed 23 of 31 December days | **Yes, measured** | See §3. Answers the question a captain actually asks. |
| **2 (extremely strong)** | Protected areas modelled by legal regime, not as no-go blobs | **Yes, shipped today** | See §3. Master-prompt-mandated, regulation-correct, and gets India's own station right where the naive version gets it wrong. |
| 3 (good) | D6 — honest quantification as a practice | Yes, as a discipline | Costs something, which is why it's credible — but it's a posture, not a feature a judge can click on. |
| 4 (good) | D5 — corridor/vessel specificity | Yes, as scope | Verifiable and hard to fake in substance, easy to claim in words — any competing team can say the same sentence. |
| 5 (good) | D2 — tested physics iceberg baseline | Yes (baseline only) | Real and tested, but a physics-only drift model is the *floor* the 2025 literature (IDRIFTNET) already expects a serious team to clear, not a ceiling. |
| 6 (roadmap, don't oversell) | D1 — uncertainty reaches the routing decision | No | The single strongest **innovation** claim in the whole set if it ships — see §4 — but it is not demonstrable today, and TRUE_CLAIMS.md itself says so. |
| 7 (roadmap) | D4 — bandwidth-honest design | Partial | The ethos is real in the demo; the proof machinery (CI gate, signed packs, Iridium-tested sync) is not, and a real competitor (IcySea) already ships Iridium-tested delivery. |
| 8 (roadmap, weakest) | D3 — multi-source disagreement | No | Grounded reasoning, zero code. |
| — | D7 — PolarRoute reuse | Reuse yes, extensions no | Correct move, but claim only the reuse until the extensions exist. |

**Why these two and not D1 — and a flag that this is a judgment call, not a
mechanical scoring.** The task's own criterion (a) for "extremely strong" is
"true today **or clearly roadmapped**." Read literally, D1 clears that bar:
`TRUE_CLAIMS.md` §5 lists it as priority 3 with a pre-committed pass/fail
gate, which is about as "clearly roadmapped" as a roadmap item gets. On
criterion (b) — hard to copy this season — D1 arguably *beats* both of my
picks: it needs an ensemble, held-out calibration, and a numeric gate, not
just new code wired to old data. So a literal reading of the task's three
criteria does not obviously rule D1 out, and if the room prioritizes the
strongest *idea*, D1 belongs in the top two instead of one of these.

I ranked it below both anyway, and I want the reason on the record rather
than folded silently into the ranking: the user's own framing of what judges
respond to is "if they actually work... not just appear sparkly." A USP that
is "clearly roadmapped" but has never run — no slider, no measured coverage
number, nothing on screen — is exactly the shape of thing that framing warns
against, even though the task's written criterion (a) technically allows it.
That is me tightening (a) to require something demonstrable, on purpose,
because of that stated judging philosophy — not the task's literal text doing
it for me. **If the call is made to weight the literal roadmap allowance
instead, D1 replaces D6 or D5 in the top two**, and it should be argued the
way §5 and §7 argue it: the strongest, hardest-to-copy idea in the set, not
yet demonstrable.

Under either reading, the destination-window result and the protected-areas
work clear all three criteria without qualification: (a) true today, code and
figures exist; (b) about as hard for a rushed competing team to replicate
this season as D1's ensemble would be — one required three years of
quality-audited satellite data and finding a bug nobody else looked for, the
other required reading Annex V of the Antarctic Treaty instead of drawing
polygons; (c) both are things a captain, or an NCPOR operations desk, would
immediately recognize as useful. That's why they hold rank 1 and 2 regardless
of how the D1 judgment call above is resolved.

---

## 3. The two extremely strong USPs, in full

### USP-1 — "Can I actually get in?" not "here is the ice"

**One sentence:** for the 200 km approach to Bharati in December 2019, the
system says the cell was closed to this ship on 23 of 31 days, while the
water 100 km further north was open every single day.

**Why it's extremely strong and not just "good":**
- **True today.** `isih/figures/destination_window.json`, cited in
  `TRUE_CLAIMS.md` §1.6–1.8.
- **Hard to copy this season.** Getting this number required finding that the
  satellite record reports suppressed coastal pixels as 0.0% ice — open water
  — on 100% of days, affecting ~118 cells/day and 43.2% of days in the 200 km
  Bharati approach across 2018–2020, then re-checking which of the "open"
  Bharati days were real (four of the original eight readings were exactly
  this artifact). A team that hasn't done that audit will publish a wrong,
  more optimistic closure number without knowing it — and the honest fix
  makes the coastal ice number go **up** (46.8% → 54.6% mean), i.e. the
  correction makes the system *more* cautious, which is the direction that
  matters at sea.
- **A captain cares.** Every existing product (CMEMS, USNIC, IceNet) answers
  "what does the ice look like." None of them, as far as this project's own
  search found, answer "will my ship specifically fit through, on this date."
  That's the actual decision-support question, not a map.

**What could break it:** it's one December, one ship's draft, three years of
data behind it. State the sample size on the slide — don't imply it's a
general climatological law.

### USP-2 — Protected areas modelled by the law that actually applies, not by fear

**One sentence:** of 33 Antarctic-Treaty protected-area polygons in the
corridor, none are marine, so the system correctly finds none of them restrict
the ship's transit — while still correctly telling the master that Bharati
sits inside a managed area India itself co-proposed, and that India's own
protected area (ASPA 163, Dakshin Gangotri) is 4.7 km from Maitri.

**Why it's extremely strong and not just "good":**
- **Shipped today.** `isih/protected_areas.py`, sourced from the Antarctic
  Treaty Secretariat's own 2024 shapefile (148 polygons, CRS read from the
  `.prj`, not assumed).
- **Directly answers what the master prompt asked for by name** (§48A.17):
  don't treat every protected area as an identical no-sail blob — determine
  whether the regime is a prohibition, a permit requirement, or an
  operational condition. This module does exactly that: ASPA (Art. 3, entry
  prohibited without permit) versus ASMA (Art. 4, no permit needed, activity
  governed by a management plan) are coded as different constraint types, not
  the same red polygon.
- **Hard to copy under deadline, for a specific reason:** the *easy*, wrong
  version — draw all 148 polygons as no-go — is exactly what a team under
  time pressure reaches for, and it would have refused to route to India's
  own station, since Bharati sits inside ASMA 6. Getting this right requires
  reading Annex V of the Environmental Protocol, not just downloading a
  shapefile. That is a genuinely different amount of work than "add a
  no-fly-zone layer," and it shows up as a specific, checkable design
  decision in the code, not a claim.
- **A captain, and an NCPOR compliance desk, both care.** This is the
  difference between a system that would tell you your own station is
  off-limits and one that gets the actual legal picture right.

**What could break it:** the honest finding this season is "nothing here
restricts transit" — which is correct, but also means this feature currently
changes zero routes. Its value is *correctness and trust*, not a route that
looks different. Say that plainly rather than implying it moves the line the
way D1 would.

---

## 4. The three "good" USPs (basic tier)

1. **D6 — we don't print numbers we can't defend**, evidenced by three
   corrections already made against ourselves (transit time, a route caption,
   the baseline itself). Credible because it cost something; not a feature a
   judge interacts with.
2. **D5 — the real ship, the real corridor, the real season**, evidenced by
   using the Golovnin's real dimensions and the real December resupply
   window. Verifiable and specific, but any team reading the same ISEA press
   releases can claim the same scoping in a sentence — the substance is in
   the destination-window number (USP-1) that this scoping makes possible.
3. **D2 — a published, tested physics model for iceberg drift**, evidenced by
   23/23 tests against the paper's own coefficient table, run today on 33
   real tracked bergs including one 3,037 km² berg beside Bharati's approach.
   Real and working, but a physics-only baseline is table stakes against the
   2025 literature (IDRIFTNET already treats physics-plus-residual as the
   expected architecture) — it's a floor cleared, not a differentiator on its
   own.

---

## 5. The killer feature

The master prompt asks for exactly one thing that beats another team on the
same PS. Candidates, argued straight:

**Candidate A — D1, uncertainty reaching the routing decision.** The best
*idea*. If it ships, nothing else on this list is as hard to copy in one
season, because it needs an ensemble, held-out calibration, and a
pre-committed gate — not a UI toggle. But it is not built, and "our killer
feature is a thing we have not demonstrated" is a bad sentence to say out
loud in December. Nominate it as the thing to build toward, not the thing to
lead with today.

**Candidate B — the offline/bandwidth-honest design (D4).** Real in spirit
(the demo makes zero live calls and refuses to fake missing data), but the
web search done for this document found a real commercial product, IcySea,
that already advertises Iridium-tested low-bandwidth delivery. This
disqualifies it as *the* killer feature — it is not white space, it is a
place we currently match a chart-display competitor at best, and lag the
parts of D4 that are still marked ROADMAP.

**Candidate C — the destination-window result (Bharati closed 23/31 days).**
Built, measured, and it is the one output on this entire list that answers
the actual question a master mariner asks before a resupply run: not "what
does the ice look like" but "will I get in, and on which days." Every
incumbent this project searched for — CMEMS, USNIC, IceNet, PolarView,
IcySea — publishes ice state or ice charts. None of them, on the evidence
gathered for this project, publish a ship-specific, date-resolved closure
answer for a named destination. It also required work a rushed competing team
is very unlikely to have done in one season: a three-year satellite-quality
audit that found and corrected a coastal data artifact, in the direction that
made the system *more* cautious rather than more impressive.

**Candidate D — protected areas by legal regime.** Built, correct, and
directly responsive to the master prompt's own instruction. But by its own
honest accounting it changes zero routes this season (§3), which makes it a
trust feature, not a "beats the room" feature.

**Pick: Candidate C, the destination-window result.** It is the only
candidate that is simultaneously (a) built and measured today, (b) answers
the PS's actual ask — "safe... navigation routes" — in the unit a captain
uses (can I get in, which days), and (c) required a specific, hard-to-shortcut
piece of work (the coastal-artifact audit) that a team without three years of
data behind them cannot fake in a demo. Candidate A is the best long-term bet
and belongs at the top of the roadmap slide with an honest "not yet" attached.

---

## 6. Competitors — named, with the real gap each one leaves

| System | What it actually is | Where it's genuinely better than us | The specific gap we fill |
|---|---|---|---|
| **IcySea** (Drift+Noise GmbH, AWI spin-off, co-developed with the Norwegian Met Institute) | Commercial chart-based ice-navigation app: NRT Sentinel-1 imagery + "optimized bias corrected ice drift modeled data," delivered to a bridge client over low-bandwidth links, Iridium-tested | Deployed and operating today; Iridium delivery already proven in the field, which our sync story has not been (`WEAKNESS_ANALYSIS.md` §6); polished bridge-facing UI | It's a chart-and-data display, not a route optimizer with fuel/time output; no evidence of Antarctic corridor coverage or a Golovnin-specific vessel model; no destination-window-style closure answer; no protected-area regime modelling |
| **Polar View** (ESA/EC-funded consortium, incl. BAS) | Near-real-time sea-ice information service: enhanced ice charts, ice-edge and iceberg monitoring, a documented "ship routing in ice-covered areas" use case built on Copernicus data | Long-running, multi-agency, credible provenance; genuine iceberg monitoring at operational scale | Consortium chart/advisory service, not a trained forecasting model competitors can point to beating a stated baseline; no evidence it's tuned to any specific vessel or the Cape Town–Bharati corridor; no published uncertainty-into-routing mechanism either |
| **StormGeo (s-Routing/s-Planner)** | The real commercial incumbent in voyage optimization; ice conditions as one input parameter; partnered with Bearing AI for vessel performance; keeps human route analysts in the loop 24/7 | Mature, commercial-grade, genuinely multi-objective voyage optimization at scale; the human-in-loop fallback is itself evidence that full automation isn't trusted at the edges — which is the same posture D6 argues for | Different market entirely: global commercial shipping, subscription, not deployable on an NCPOR bridge laptop, no Antarctic-resupply specialisation. Not a strawman to attack — a precedent that validates keeping a human in the loop |
| **PolarRoute / BAS** | The open-source router this project reuses directly (installs in ~90s, ~9s per run) | It's the field's own tool, actively maintained by domain experts; we did not reinvent it | It drops forecast uncertainty (`IceNetDataLoader` discards `sic_stddev`), plans on one frozen mesh with no time dimension, and has no iceberg layer at all — verified in installed source, and this is the honest basis for the ROADMAP extensions in D1/D7, not a claim they're already built |
| **NSIDC / USNIC ice and iceberg products** | The authoritative raw observational and iceberg-tracking data — this project's own inputs | Ground truth; nothing here competes with it, we build on it | It publishes state (concentration, tracked positions), never a route decision or a ship-specific reachability answer |
| **IceNet (BAS/Turing) and ANTSIC-UNet** | Published Arctic (IceNet) and Antarctic-specific (ANTSIC-UNet) sea-ice forecasting U-Nets | ANTSIC-UNet is validated specifically on 2017/2022/2023 Antarctic extreme-minimum events, a genuinely hard regime | Research artifacts, not decision-support products — no routing, no vessel model, no destination-window answer; IceNet's validation is Arctic-only and should not be extrapolated to Antarctica without saying so, which is exactly the mistake `COMPETITIVE_ANALYSIS.md` warns a competing team into |

No strawmen above: every entry is a real, sourced system, and every "where
it's genuinely better" column has something in it, per
`COMPETITIVE_ANALYSIS.md`'s own warning against pretending otherwise. The two
found by web search for this document (IcySea, Polar View) were verified
against their own project/vendor pages before being written down, not
recalled from memory and left unchecked.

---

## 7. Innovation, stated plainly

The one thing this project's own research could not find anywhere in the
published literature: **a system that propagates sea-ice forecast uncertainty
into the routing decision itself**, rather than showing it as a colour on a
map (`TRUE_CLAIMS.md` §2.1). That is D1. It is not built. It is the correct
thing to describe as the innovation this team is aiming at, with the honest
caveat attached every time: designed, gated, not yet running.

What *is* built and is closer to "innovation" than "feature" today is the
destination-window method itself — turning three years of satellite ice data
plus a found-and-fixed data bug into a ship-specific, date-resolved answer.
It is not a new algorithm; it is a new *question asked of old data*, answered
honestly including the direction the correction moved the number (more
cautious, not less). That is the innovation a judge can actually see work,
today, live.

---

## 8. What was asked for but this repo does not support

- **A live, on-vessel-tested bandwidth story.** The offline ethos is real in
  the demo; the CI-enforced sync budget, signed packs, and Iridium-tested
  delta sync do not exist yet (`WEAKNESS_ANALYSIS.md` §6). Don't claim D4 as
  a killer feature until this closes the gap with IcySea, which already has
  it.
- **A demonstrable D1.** The idea is the strongest innovation claim available,
  but there is nothing to click on. Keep it off the USP slide; put it on the
  roadmap slide with its own gate numbers attached.
- **D3, multi-source disagreement as a routing input.** Zero code exists.
  Cite the grounding research, don't claim the mechanism.
- **A CMEMS-forecast-vs-our-model comparison.** The measured wins are against
  persistence and raw GLORYS12 reanalysis. The archive needed to run the
  CMEMS-forecast comparison only started accumulating 2026-08-31 and has
  seven days in it as of today — not enough to retrain or re-score against.
  Say "beats persistence and beats GLORYS12," not "beats CMEMS."
