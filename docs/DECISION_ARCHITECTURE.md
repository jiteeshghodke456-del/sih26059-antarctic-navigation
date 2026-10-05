# Decision Architecture

*How a 7-day forecast supports a 17-day voyage, why the system usually says
"hold course", and what it does when a model is wrong.*

Status: design, agreed 2026-09-02. Nothing here is built yet except where a
section says otherwise. Evidence for the physical claims is in
`NAVIGATION_RESEARCH.md`; the measured route experiment is
`isih/route_regret.py`.

---

## 0. The premise everything else follows from

**Ship navigation is not Google Maps.** Three differences drive the whole
design:

1. **There are no do-overs.** A car that misses a turn loops the block. A ship
   that commits to the wrong side of a closing lead can lose days, or be beset.
2. **The map moves.** The ice reorganises under wind on the same timescale the
   ship moves through it. We are routing over a field that is itself drifting.
3. **The human is in command, and should be.** The master has decades of ice
   experience the model does not have and cannot acquire. Our output is
   evidence for their decision, never a substitute for it. The problem
   statement says *Decision Support System*, and we take that literally.

---

## 1. The horizon problem

A Cape Town → Bharati voyage takes roughly 14–17 days. Our sea-ice forecast has
useful skill to about 7 days and degrades with lead time. So the obvious
objection is fatal-sounding:

> *"You cannot forecast day 14. So how can you plan a 17-day voyage?"*

**The answer is that a voyage is not one decision.** It is a sequence of
decisions taken at different times, and they do not all need the same lead time.
Nobody needs a committed track for day 14 on day 0. What they need on day 0 is
to not be walking into a trap on day 3, and to be heading somewhere that still
has options on day 14.

So we stratify the horizon and are explicit about what each band is for:

| Band | Lead | What we claim | What the output is |
|---|---|---|---|
| **Committed** | 0–2 days | Real forecast skill; changes need strong evidence | A track the bridge can steer |
| **Steering** | 3–7 days | Declining but real skill | A **corridor**, not a line, with flagged decision points |
| **Strategic** | 8+ days | **No forecast skill claimed** | Climatology + ice-edge position, drawn as a fan and labelled as such |

The strategic band is drawn deliberately vague **because it is vague**. A system
that renders a crisp line at day 14 is lying, and an experienced master will
know it is lying, and will then distrust days 1–3 as well — which are the days
that were actually worth something. Honest uncertainty at long range is what
buys credibility at short range.

> **Line for the viva:** "We do not forecast day 14. We make sure that on day 14
> you still have a choice."

---

## 2. Why the system usually says "hold course"

The obvious failure mode of daily re-planning is **whipsaw**: the plan flips
between alternatives as noisy forecasts flip their ranking, the crew loses
confidence, and the tool gets switched off. This is a well-known pathology of
naive receding-horizon control, and it is exactly what the user's question
identified.

We never re-rank routes on raw cost. A change is proposed only when the
challenger beats the incumbent by more than the uncertainty in the comparison:

```
switch  only if   Cost(current) − Cost(alternative)  >  τ

τ  =  manoeuvre cost
   +  width of the conformal prediction interval on the cost difference
   +  an explicit incumbency margin
```

The middle term is the important one: **τ is derived from our own calibrated
uncertainty, not tuned by hand.** When two routes' cost distributions overlap,
there is no justified reason to switch, and the system says so.

Consequences, stated plainly because they are features and not excuses:

- **On most days the correct output is "no change."** A system that recommends
  holding course on 12 of 14 days and flags 2 genuine decision points is far
  more trustworthy — and far more useful — than one that redraws the line every
  morning.
- **Detours are proposed early or not at all.** A large deviation is only
  actionable while it is still cheap. Past the commitment point, the honest
  advice is a micro-adjustment plus a warning, and we say which one we are
  giving.
- **"Hold course" is a real output with real evidence.** It carries the same
  reasoning payload as a change: what we checked, what would have changed our
  mind, and when we will look again.

---

## 3. Decision points, not continuous steering

Real ice navigation has **irreversible commitment points**: choosing east or
west of a large floe field, entering a bay, committing to a lead system.
Reversal after the fact costs days.

So the system's job is not to nudge the heading continuously. It is to:

1. **Identify the gates in advance** — places where the route topology forks and
   reversal is expensive.
2. **Report the cost of being wrong at each gate**, not just the preferred branch:
   *"Day 4, east or west of the Fimbul ice tongue. East is 6 h faster today.
   If the forecast is wrong, east costs 2.5 days to undo and west costs 0.5."*
3. **Compute the value of waiting.** Sometimes the right move is to hold the
   decision for 24 h because tomorrow's observation will resolve it. That is a
   recommendation the system should be able to make explicitly.

This is how mariners already think. Matching that structure is worth more than
any additional decimal place of forecast accuracy.

---

## 4. When a model is wrong

The user's sharpest question: *one day's prediction fails, the maths ahead is
disturbed, and the ship cannot take back a decision. What then?*

### 4.1 The architecture already contains the answer

Our model does not predict sea ice. It predicts the **correction** to a physics
forecast:

```
corrected = clip(CMEMS_forecast + model_delta, 0, 1)
```

The prediction head is zero-initialised, so an untrained or failing model
contributes nothing and the output *is* the physics forecast. **The floor is
CMEMS's skill, not zero.** A model failure is a degradation to the physics
baseline, not a fall off a cliff. This is a genuine safety property of the
design and we currently under-sell it.

### 4.2 The degradation ladder

Every rung is always available, and the system announces which rung it is on:

| Rung | Product | Available when |
|---|---|---|
| 1 | Corrected forecast + calibrated interval | Normal operation |
| 2 | Raw CMEMS forecast | Our model fails verification |
| 3 | Persistence from newest observation | Forecast feed lost |
| 4 | Climatology for the date | No recent observation at all |

Falling to rung 3 or 4 **widens the corridor and moves decision points earlier**
— less information means committing later, not sailing the same line with less
confidence.

### 4.3 We verify ourselves, daily, out loud

Yesterday's 1-day forecast is checked against today's observation. That is a
free, honest skill measurement available every single day at sea. It drives:

- **Drift detection.** Sustained verification failure means the regime has moved
  (see the non-stationarity section of `NAVIGATION_RESEARCH.md`) and the model
  is outside its training distribution.
- **Automatic rung demotion.** Below a skill threshold the system drops to rung
  2 by itself rather than waiting to be caught.
- **A visible confidence state** the master can see: *"Forecast verifying
  poorly at lead 3+ since 4 Dec. Recommendations advisory only."*

> **Line for the viva:** "We do not claim the model is always right. We claim
> the system knows when it is wrong, and says so before it matters."

---

## 5. The sailor is the decision maker

The interaction is deliberately inverted from the usual routing demo. We do not
open by drawing our line over theirs.

1. **The master proposes or holds a route.**
2. **The system evaluates *their* route first** — transit time distribution,
   maximum ice, where the risk sits, which segments are exposed.
   *"Your intended track: 16.2 days, worst ice 71% on day 9, two elevated-risk
   segments."*
3. **Alternatives are offered as annotated deltas, never replacements.**
   *"Shifting 40 nmi south on day 4 avoids a convergence zone. Costs 3 hours."*
4. **Every recommendation carries its reason and its trigger** — what we saw,
   and what would change our mind.

A route we produce that the master rejects is a **successful** interaction if
the reasoning was sound and legible. The failure mode we care about is an
unexplained recommendation, not a rejected one.

### 5.1 A point ETA is a lie

We never report a single arrival time. *"17.4 days"* implies a precision we do
not have. We report a distribution: *"17.4 days, 80% between 16.1 and 19.8"* —
and the width of that interval is itself decision-relevant information for
cargo, fuel and station planning.

---

## 6. Where the computation happens

Antarctic connectivity is the binding constraint, not GPU time.

| | Shore (NCPOR / cloud) | Vessel (laptop, offline) |
|---|---|---|
| Ensemble inference, conformal calibration | ✅ | ❌ |
| Mesh construction over the corridor | ✅ | ❌ |
| Route optimisation and re-planning | ✅ | ✅ (must work offline) |
| Verification and drift monitoring | ✅ | ✅ (needs no uplink) |

The two tiers are joined by a compressed **voyage pack**. Measured so far:
a vessel-modelled mesh compresses 551 KB → **76 KB gzip**; a route polyline
1.6 KB → 796 B. The full-corridor pack is estimated 0.5–1 MB and the daily
delta is **not yet measured** — that number is load-bearing and is called out in
`docs/backlog.md`.

**The vessel must be able to re-plan with no uplink at all.** If the satellite
link fails, the laptop still has the last pack, the ship's own observations, and
the degradation ladder in §4.2. A tool that stops working when the weather is
bad is worthless precisely when it is needed.

---

## 7. What this design deliberately does not do

Scope discipline, so the three pillars of the problem statement get done
properly instead of five things getting done badly:

- **No autopilot, no collision-avoidance, no COLREGs.** Tactical steering stays
  on the bridge. We operate at hours-to-days and tens of kilometres.
- **No claim to solve Southern Ocean traffic management.** We address fleet
  coordination for the Indian programme; the Indian Ocean sector sees
  single-digit vessels and claiming congestion control would be overclaiming.
- **No sub-grid ice features.** A 25 km concentration field cannot see growlers,
  leads narrower than a cell, or pressure ridges. §8 says this out loud.
- **No fabricated fuel figures.** The fuel polynomial is calibrated to a
  different hull (ADR-012), so fuel is reported relatively or not at all.

---

## 8. The honest limit of a 25 km product

Stated plainly because a judge will ask, and because a mariner already knows:

- **Growlers and bergy bits are invisible** at 25 km, and they are the classic
  hull-holing hazard. This is a radar-and-lookout problem, not a satellite
  problem, and we do not pretend otherwise.
- **Leads narrower than a cell are invisible**, so the very feature a master
  most wants to exploit is below our resolution. We route to the *region* where
  leads are likely, not to a lead.
- **Coastal cells are actively suppressed** by the CDR's land-spillover filter
  and written as 0.0. Measured: this affects the 200 km approach box to Bharati
  on **43.2% of days** in 2018–2020. We now read the QA flag and treat those
  cells as unknown (`isih/ice_quality.py`); before that fix our own router
  planned through them as open water.
- **Concentration is not thickness, and POLARIS needs thickness.** IMO
  MSC.1/Circ.1519 indexes risk by ice *type*. A concentration-only system cannot
  compute a compliant RIO, which is why the production model gains a thickness
  output channel.

The correct posture is not to hide these. It is to make the system's confidence
shrink where they apply, and to say which of them is biting today.
