# Walkthrough script — every control, why it exists, and where it breaks

For the presenter. Left column is what you click; the rest is what to say and
what a judge is really asking. **Bold** = say it out loud. Numbers tagged
**[M]** are measured in this repo and reproducible.

Two rules for the whole demo:

1. **Say the environment is synthetic in your first thirty seconds.** It is on
   the badge. A judge who discovers it themselves stops believing everything
   else. A judge who is told immediately gives you credit for the discipline.
2. **When something is not built, say "not built" and move on.** Every honest
   gap in this system has a stronger answer behind it than the feature would
   have been. That is the whole strategy.

---

## 0 · Before anyone is in the room

```bash
cd ~/sih/SIH26059-antarctic-navigation/.claude/worktrees/v3-compliance
.venv-demo/bin/python -m uvicorn isih.demo.app:app --port 8100 --reload
```

Open **http://127.0.0.1:8100**, hard-refresh, and leave it on the sign-in
screen. Have `/legacy` open in a second tab — that is the real-satellite console
and it is your evidence if anyone pushes on "is any of this real".

---

## 1 · Sign in — "Who is on watch"

| Control | What it does | Why it is there |
|---|---|---|
| **Name and rank** field | Records who holds the watch | Every approval later is attributed to this string |
| **Take the watch** | Enters the console | The app **cannot** be entered any other way |

**"This is passage-planning software, so it starts where a bridge starts. There
is no bypass, and a test enforces that."**

**Where it fails, and say so if asked:** any string is accepted. There is no
user store. **It is identity, not access control** — an approval record whose
name is unverifiable is not yet an audit trail, and that is a pilot blocker we
have written down.

---

## 2 · The frame — read the chrome before anything moves

| Element | What it says |
|---|---|
| `ISIH · PS-26059` | Problem statement, top left |
| **ROUTE PLANNING / ROUTE MONITORING** | ECDIS's own two modes. **Not our invention — that is the point** |
| **SYNTHETIC ENVIRONMENT** (purple) | Say it now. Real physics, invented initial conditions |
| Clock `00:00 2026-12-11 UTC` | Voyage clock, not wall clock |
| **ALM** + count | Open alerts. Turns red at P1 |
| **DAY / DUSK / NGT** | S-52's three bridge palettes. Click DAY — **"a bridge dims its screens at night; a chart standard has three palettes and so do we"** |
| **FUT** | Future-scope screen (Baymax, local assistant), everything badged simulated |

**Competitor gap #1 — nobody else has a mode.** IcySea, PolarView and the ice
services are *viewers*: one state, always the same. ECDIS has planning and
monitoring because a passage plan is a document with a lifecycle. We took the
lifecycle, not the look.

---

## 3 · Command centre → Voyage → Mission

| Stage | Controls | Why |
|---|---|---|
| Command centre | vessel, IMO, watch, corridor · **New voyage** | Establishes *which ship*. Every threshold below is this hull's |
| Voyage | **Departure day** (−20…+30), **Destination** (Bharati / Maitri / pack-edge hold) | Departure day is a decision variable, not a setting |
| Mission | **Station cell required** vs **Pack-edge approach acceptable** | Stop here |

**Stop on the mission radio.** **"This one radio button is the most
consequential field in the application. In the real December-2019 record,
Bharati's own cell was closed 23 of 31 days and the approach 100 km north was
open 31 of 31."** **[M]**

**"That is the whole thesis. The 5,800 km ocean crossing averages 6 % ice —
there is nothing to optimise out there. The entire voyage's uncertainty is in
the last 100 km, and this radio button decides which question we are answering."**
**[M]**

**Competitor gap #2 — every routing product optimises the crossing.** We
measured the crossing and found the null result: planning on departure-day ice
cost **0.03 days**, and *daily re-planning was slower* — 9.00 d against 8.61 d.
**[M]** We publish that against ourselves.

---

## 4 · Route stage — the engine

| Control | What it does | Why |
|---|---|---|
| **Objective**: Least time / Least fuel | Two different searches | They are **not** the same path |
| **Ice limit**: 85/80/70/60/55/45 % | The assumed working limit | Labelled *assumed* everywhere |
| **Solve** | Runs the live search (~2 s) | |
| **Waypoints** | Enabled only after a solve | Ordering is enforced |

**Say while it solves:** **"This is a time-aware search. Each cell is costed
with the ice and sea state valid at the hour the ship would actually arrive
there. That sounds obvious and it is the thing our own audit found missing — the
published router had no time dimension, so it met day-zero ice on day nine."**

**Then switch Objective to Least fuel and Solve again.** **[M]** 10.66 d / 195 t
against 17.06 d / 154 t, on tracks sharing 9 waypoints of about 100. **"14 %
less fuel for 72 % more time. In the earlier configuration these were the same
line, because with zero currents and no wave term fuel was just a function of
time. Expressing fuel per distance — v² for speed, C^1.5 for ice, Hs² for sea —
gives a real trade-off surface."**

**Then set the limit to 45 % and Solve.** **"No route exists. Not slower —
unreachable."** **[M]** **"Our 80 % is an assumption; no ice class anywhere
indexes ice *concentration*, they all index thickness. So the honest daily output
is not 'open' but the assumed limit at which reachability flips, which we
compute."**

**Competitor gap #3 — BAS PolarRoute is the state of the art and we reuse it,
we do not compete with it.** It has no time dimension, its wave-resistance
function is dead code, and its IceNet loader drops the ensemble spread. Arriving
with *"we used the field's own open tool and here are three things it does not
do"* is far stronger than a from-scratch A\*.

---

## 5 · Waypoints and Review — the nine gates

Waypoints: number, lat, lon, ETA, ice and sea state **at that leg's arrival
time**.

**Review is the heart of the demo. Slow down.**

| Gate | Reads from |
|---|---|
| ice | worst concentration on track vs the assumed limit |
| logistics | is the mission's destination reachable |
| contingency | how many corridors survive |
| weather | sea state and visibility at the ship |
| chart | **under-keel clearance** from the seabed model |
| traffic | AIS picture |
| capability | ice at the ship vs the working limit and its 7.4-point band |
| communications | latitude — geostationary cover fails below ~70°S |
| execution | on plan |

**"Nine questions, each with a state and a reason. Health is the worst of them
and is never a score — there is no `route_score = 0.82` anywhere in this
codebase. And the rule that matters: a gate we cannot evaluate returns UNKNOWN,
UNKNOWN never passes, and it caps health at DEGRADED."**

**On the 7.4-point band:** **"That number is the CDR's own retrieval standard
deviation in the 70–90 % band. It used to be 5 points, for no reason at all —
and the invented band was *narrower* than the instrument's own uncertainty, so
it reported comfortable passes for routes the sensor cannot distinguish from the
limit."** **[M]**

Then **name + optional note → Approve.** **"Attributed and versioned. The
previous plan is never overwritten."**

**Competitor gap #4 — this is the gap we occupy.** Every product in this space
renders no-data as no-hazard. Our own archive shows why that is dangerous: the
satellite product writes land-spillover-suppressed coastal pixels as **0.0 % —
open water — on 100 % of days**, and **43.2 % of days** it lands inside the
Bharati box. **Four of the eight days Bharati looked open were that artifact.**
**[M]** We detect it, mask it, and the correction moves coastal mean ice from
**46.8 % to 54.6 %** — *heavier*, the safe direction. **[M]**

---

## 6 · Begin navigation — the thirty seconds that matter

Mode badge flips to **ROUTE MONITORING**.

**Now drag the time slider forward.** Watch the health band.

**[M]** VALID from departure through about D+5.5 → **DEGRADED at D+7** as the
ship works into the ice and drops below geostationary cover.

**"Health moves, and every transition names the gate that moved it. It is not a
colour someone chose — it is derived."**

**Say this too, because it is the honest bit:** **"An earlier build had this
stuck on DEGRADED for the whole voyage, because two gates were hardcoded
UNKNOWN. The rule was right and the implementation was a stuck light. Gates now
have inputs. UNKNOWN did not go away — it moved to where it is earned: a layer
older than its own skill horizon retires its gates with the age stated."**

---

## 7 · The time bar

| Control | What | Why |
|---|---|---|
| **HOME** | Fits the working area | Recovery. An errant scroll used to cost the whole session |
| **◀ / ▶▶** | ±6 h | The re-assessment interval |
| **▶ / ❚❚** | Play / pause | Coarser field while running |
| **Slider** | 0–168 h | Seven days — beyond that we do not claim skill |

**If asked why the slider stops at 168 h:** **"Because the only Antarctic-covering
ice forecast reaches D+9, and at this ship's real 8.6 kn the transit is 15.2
days. At departure, 41 % of the voyage is beyond any forecast that exists."**
**[M]** **"We show the horizon rather than pretending past it."**

---

## 8 · The tool rail — eleven layers

| Code | Layer | Note |
|---|---|---|
| **ICE** | Concentration field | Ramp in the Ice panel |
| **BRG** | Icebergs | Filled = catalogue-tracked, faded = below the tracking floor |
| **WX** | Wind barbs | Shares one slot with CUR — it tells you |
| **CUR** | Surface current | The ACC frontal jets |
| **RTE** | Planned route + waypoints | Magenta, S-52's cautionary colour |
| **SHP** | Own ship + heading line | |
| **AIS** | Traffic | Simulated — no receiver |
| **WRN** | NAVAREA warnings | Radius circles |
| **ASPA** | Protected areas | Tiny by nature — zoom in |
| **LND** | Coastline | Natural Earth, public domain |
| **GRD** | Graticule | Degrees and minutes, with the Antarctic Circle |

**"Every layer that is not real data carries a dot: one dot synthetic, two dots
simulated. Hover it and it tells you what it would take to make it real."**

**Competitor gap #5 — Polarstern's MapViewer has more layers than we ever will,
and it is internal to one operator's fleet.** Breadth is not the differentiator;
what you do with the layers is.

---

## 9 · The right rail — ten panels

**Alerts** — P1/P2/P3 with all nine mandated fields: what changed, where, when,
severity, source, confidence, **route consequence**, suggested action, expiry.
Click to acknowledge (it persists server-side). **"The anti-spam rule is
structural: nothing is raised without a named route consequence. An event that
does not change the plan is a reading on a panel, not an alarm."**

**Own ship** — position, COG/SOG, next waypoint, ETA, XTE, progress.
**"XTE reads 0.00 by construction, not by good steering — this is where the ship
*would* be, not a GPS fix. The dot on the panel says so."**

**Ice** — at ship, worst on track, working limit (assumed), marginal band, ramp.

**Weather in corridor** — wind, Hs/Tp, visibility, air/sea, MSLP, current,
**depth / UKC**. **"Corridor, not station weather — §9 is explicit about that."**

**Hazard timeline** — 6/12/24/48 h ahead, colour-coded. **"This forecasts along
the track, not at a point."**

**Icebergs** — count, catalogue-tracked, below the 18.5 km floor, and the closest
CPAs. **Click a row** → projected track with an uncertainty circle that grows
and **stops at 72 h**.

**"Two things here. First, only a handful of these are catalogue-tracked —
USNIC's floor is 18.5 km, so most icebergs are invisible to the record, and
absence of a tracked berg is never absence of a berg. A test forbids this system
from ever printing 'none', 'clear' or 'zero'."** **[M]**

**"Second, the CPA is against the ship's *future* track, not its current
position. And the projection stops at 72 hours because beyond that the current
field underneath it has no demonstrated skill."**

**Alternatives** — A/B/C/D with ETA delta, fuel, worst ice. **Hover one** and its
track previews on the chart.

**Decision log** — versioned, attributed, with the supersedes chain.

**Data freshness** — per layer.

**Link & pack** — **[M]** the daily pack is **7.8 KB gzipped, 0.09 s at Iridium
Certus**, measured by building and compressing the real payload. **"Network
calls: zero, and a test fails the build if any external URL appears in the
page."**

---

## 10 · The status strip

POS · COG · SOG · SIC · WIND · Hs · VIS · ETA · FUEL · HEALTH — always visible,
health turns red when it is not VALID. Borrowed from OpenCPN's always-on strip.

---

## Where we excel — the four things to land

1. **UNKNOWN is a first-class state, enforced in code.** An empty gate list is
   DEGRADED, not VALID; a test asserts a gate with no data can never pass. **A
   competitor cannot bolt this on — their entire visual language assumes
   green-means-fine.**
2. **We found a defect in the incumbent satellite product** as it affects this
   corridor, quantified it across 1,096 files, corrected it in the safe
   direction — **and then said the fix is not yet a right answer.** **[M]**
3. **We reframed the problem with a measurement**, not an opinion: 23/31 against
   0/31.
4. **We report our own null results.** Daily re-planning was slower. Two
   different ships give an identical track. We publish both.

## Where it could fail — rehearse these

| Attack | Answer |
|---|---|
| "Show me a POLARIS number" | **We publish none.** No row exists for this hull, the Polar Code makes equivalency a per-ship flag-approved assessment, and guessing spans 40 RIO points. *(The submitted deck claimed otherwise; that deck is corrected.)* |
| "Is the environment real?" | **No, and the badge says so.** Real physics, synthetic initial conditions. `/legacy` is the real-satellite console |
| "Show me an iceberg trajectory error" | **Never measured.** The physics is WDE17, tested against the paper, three numerical traps fixed. The validation archive is free and unused. Roadmap |
| "Is your 30.6 % leak-free?" | **Not established.** It is an upper bound; the background had seen observations near the target date. The ablation is written and unrun, and if it fails we retire the number |
| "Is the model running here?" | **No.** This screen serves the router and the environment. Weights are not in the repo |
| "8.6 days?" | Ideal steaming only. A real expedition voyage is two to three weeks |
| "Different ships, different routes?" | **No.** Identical 41-leg track; only cost differs. Vessel awareness is proven for **cost, not track** |
| "What's your saved-ship-day number?" | **We do not have one.** The only measurement is 0.03 d on one departure date. The sweep that would settle it is designed and unrun |
| "Has a mariner used this?" | **No. Nobody has.** Largest evidence gap in the project, and we say so first |
| "Unplug the network" | Zero external requests, test-enforced. Do **not** claim tested-over-Iridium — it has only been tested under emulated link constraints |

## The closing line

**"Six of our nine safety questions used to be grey. We gave them data and now
they move — but the rule never changed: a gate we cannot evaluate is never a
pass, and every grey one names the dataset that would settle it. No other team
will stand here and point at what their system cannot see."**
