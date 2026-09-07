# Release audit — pre-demo

**Method.** Stage 05's instruction is "attack the completed project rather
than trusting its documentation." So nothing below is accepted because a
document says it. Every claim was checked by running the system, reading the
file it rests on, or computing the result again. Where a check could not be
made, the row says UNKNOWN rather than assuming the benign answer.

**Date:** 2026-09-07. **Suite:** 77 tests pass, including the twelve
mandatory behavioural tests in `isih/test_behavioural.py`.

---

## 1. The twelve behavioural tests

| # | Test | Result | Evidence |
|---|---|---|---|
| 1 | Same environment, different vessel | **PARTIAL** | Golovnin and SA Agulhas II follow an **identical 41-leg track**; ETA differs by +1.28 d and fuel by −8.9%. Vessel-awareness is load-bearing for *cost*, not for *track*. `isih/figures/vessel_comparison.json` |
| 2 | Data freshness | **PARTIAL** | Source and valid time are recorded for every environmental value. No received-time or age exists, because replay from an archive has no arrival timestamp. The test fails if anyone starts reporting one. |
| 3 | Source disagreement surfaced | **PASS** | Real, not synthetic: the CDR's own QA flag contradicts its own concentration field. Both readings are served; at Bharati on 1 Dec, raw reads 0.0% where quality-checked reads 30.7%. |
| 4 | Stale communications degrade gracefully | **PASS** | The page fetches nothing external — a test now fails if any `http(s)://` reference appears in the HTML. Absent optional layers report `available: false` instead of taking the service down. |
| 5 | Missing iceberg record | **PASS** | The decision reports icebergs as "not on this screen", never as absent. The test forbids the words *none*, *clear*, *zero*. |
| 6 | Route health changes on evidence | **PASS** | Health moves across the window on real observations: DEGRADED 1 Dec, **INVALID** 5 Dec, DEGRADED 9 Dec. Re-evaluating the *same* day produces an identical gate digest and no divergence. |
| 7 | Alternatives differ measurably | **PASS** | A: 41 legs / 8.58 d. B: 51 legs / 8.66 d / worst ice 91%. C: **no route exists**. |
| 8 | Prediction vs observation | **PASS, scoped** | Scored once on a held-out melt season with ground truth. The upper-bound caveat sits in the same document as the numbers. |
| 9 | Baseline comparison | **PASS** | Persistence at 1/3/5/7 days. Every persistence figure must carry its period — this has bitten once already. |
| 10 | Simulated features labelled | **PASS** | `HISTORICAL REPLAY` in the API, on the badge, and in the decision object. Nothing here is simulated; replay is labelled anyway because a moving ice map reads as live. |
| 11 | Existing tests pass | **PASS** | 77/77. The invariant asserted: a gate with no data can never read as a pass. |
| 12 | Demo runs unaided | **PASS, with a P0 caveat** | Every endpoint answers; preflight refuses to start on missing data rather than rendering a gap. See P0-1. |

---

## 2. Claims ledger

### VERIFIED — supported by a file or a run in this repository

- Sea-ice data is NOAA/NSIDC CDR G02202 v6 at 25 km; 1,096 daily files, 2018–2020.
- The route is computed by PolarRoute 1.1.11 + meshiphi 2.3.1 (BAS, MIT), not drawn.
- Protected areas come from the Antarctic Treaty Secretariat register: 148 polygons,
  142 ASPA + 6 ASMA. Bharati sits **inside ASMA 6**; of 33 corridor polygons, **zero are marine**,
  so none restricts transit.
- Bharati's own cell was closed **23 of 31 days**; the approach 100 km north, **0 days**.
- The trained model beats persistence at every horizon on a held-out melt season,
  +18.5% at 1 day to +30.6% at 7 — **as an upper bound on forecast skill**, disclosed.
- Route health is derived from nine gates and changes on real evidence.
- Approval is versioned, attributed, and never overwrites the previous plan.
- Divergence from an approved plan names the gate that flipped.
- SA Agulhas II is IACS Polar Class PC5 under DNV, with a twice-sourced
  "5 knots through 1 m pack ice".

### PARTIAL — true with a scope that must be spoken aloud

- **Vessel-aware routing.** Proven for ETA and fuel; *not* proven for the track.
  Say "the same route costs this ship 1.28 days more and 9% less fuel."
- **Multi-objective routing.** Fuel and traveltime are **collinear** in this
  configuration — solving for fuel returns a byte-identical path. There is no
  trade-off surface until a current or wave field makes them diverge.
- **Alternatives.** Two corridors solve; the third's contribution is proving that
  below a 45% assumed limit *no route exists*.
- **Freshness.** Source and valid time yes; age and received time no.
- **Ice class.** Golovnin's RS `KM(★) ULA[2]` is **SINGLE-SOURCE** (two enthusiast
  registries, not RS's own register or a certificate).

### FAILED — claims that must not be made

- ~~"Different ships get different routes."~~ The tracks are identical.
- ~~"We beat CMEMS's own forecast."~~ We beat persistence and raw GLORYS12.
- ~~"Fuel-optimised routing."~~ It returns the same path as time-optimised.
- ~~"Iceberg trajectory prediction."~~ The equations are implemented and tested;
  no trajectory error has ever been measured.
- ~~"POLARIS risk index for this vessel."~~ Deliberately not published, and the
  reason is the interesting answer.

### UNKNOWN — not established either way

- **Six of nine decision gates**: capability, chart, weather, traffic,
  communications, execution. Each names the dataset that would settle it.
- Golovnin's modern IACS/Arc ice-class equivalent — structurally unverifiable from
  open sources; needs FESCO/NCPOR.
- IMO Polar Ship Category for **both** ships — GISIS requires authentication.
- Whether the model's skill survives the leak-free ablation. This is the single
  most valuable unrun experiment we have.

---

## 3. Priorities

### P0 — fix before demo day

**P0-1. The satellite archive is a symlink into another git worktree.**
`isih/data` resolves to `.claude/worktrees/foamy-seeking-allen/isih/data`. Removing
that worktree — an ordinary tidy-up — deletes 1,096 NSIDC files from this demo's
view, and the app then refuses to start. This is a realistic pre-demo failure with
no obvious cause at the moment it bites.
*Mitigated:* the preflight error now names the symlink and says whether its target
is present, so the message no longer sends someone to re-download files they have.
*Fix properly:* move the archive to a path outside every worktree and repoint the
link. Not done here because the data belongs to another worktree and moving it
would break that one.

### P1 — worth doing before the finale

1. **The leak-free ablation** — channel 0 = `background[t]` instead of
   `background[t+lead]`, plus a no-background arm. One Kaggle day. If the causal
   variant still beats persistence, the headline stops needing its caveat. The leak
   inflates the 7-day figure most, so **+30.6% is our most contaminated number**.
2. **Three seeds minimum** before comparing anything that differs by a few percent.
3. **A stronger short-lead baseline** — damped anomaly persistence, already named in
   `GAP_ANALYSIS.md` and never scored.
4. **Bathymetry into the mesh.** It closes the chart gate and makes the vessel's
   `min_depth: 20 m` constraint real instead of inert.

### P2 — deferred, filed

Tracked in `docs/backlog.md`. The recurring theme is capability that exists in the
repository but never reaches the screen: the USNIC iceberg catalogue, the CMEMS
forecast archive with its `sithick` and drift fields, and the Wagner drift model.

---

## 4. Judge questions, and the answers

**"Is any of this live?"**
No, and the badge says so before you ask. December 2019 is used because it has
ground truth to score against. The same pipeline ingests the live CMEMS forecast;
that harvest has been running daily since 31 August 2026.

**"Your route is only better than a straight line."**
Correct, and the straight line is an illustration of why routing is needed, not a
baseline we claim to beat. The real baseline is the same router given older ice.

**"Why is the route never VALID?"**
Because six of nine decision gates have no data behind them, and a gate we cannot
evaluate is not a pass. We would rather show you the three we can evaluate and name
the six we cannot than light nine lights.

**"So the ship doesn't actually change anything?"**
It changes the cost, not the corridor — 1.28 days and 9% fuel between these two
ships on this day's ice. The corridor does change when the ice constraint changes,
41 legs to 51. The mechanism works; this pair of ships on this day does not
separate it, and we say so in the artifact rather than in a footnote.

**"Why not use a foundation model?"**
We adjudicated nine. None forecasts sea-ice concentration or was trained on the
passive microwave that observes it. The whole daily record is roughly 17,000 frames
— too small for the premise that motivates foundation models.

**"What would make you distrust your own number?"**
The seven-day figure. It is our largest gain and our most leak-contaminated one,
and the ablation that settles it is written and not yet run.

---

## 5. Release readiness

**Demo-ready: yes, conditional on P0-1.**

The system starts, serves every endpoint, renders in a real browser with no errors,
and its headline behaviour — route health moving from DEGRADED to INVALID on real
observations, and naming the assumption that broke — is reproducible from the
committed artifacts.

**Not release-ready as an operational product, and nothing here claims to be.**
Six of nine gates are unevaluated, there is no live sensor feed, no bathymetry, and
no measured iceberg trajectory. The honest framing is a decision-support prototype
whose scaffolding is real and whose coverage is stated on the screen.

The condition worth restating: **do not demo from `docs/DEMO_PLAN.md`**, which is
the 31 August sprint plan and promises three capabilities that do not exist. Use
`docs/RUN_OF_SHOW.md`.
