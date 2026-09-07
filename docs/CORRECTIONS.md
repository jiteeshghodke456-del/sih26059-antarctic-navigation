# Corrections register

The bridge between the audit and the build. Every finding in
`docs/MASTER_AUDIT.md` that forces a change appears here as one checkable line.
A finding that does not become a line has not been acted on; a build change with
no line is scope creep.

Status: **DONE** (in this branch) · **OPEN** (filed, not built) · **BLOCKED**.

## P0 — must be fixed before anyone presents this

| # | Finding | Correction | Status |
|---|---|---|---|
| 1 | Deck: "replaced the 80 % threshold with POLARIS". Code says `"max_ice_conc": 80`; our own research says no RIO can be computed for this hull | Remove the claim; replace with the POLARIS *applicability* finding, which is stronger | **DONE** — `docs/SIH_PPT_V2.md` |
| 2 | Deck: "predicts the drift of **live** icebergs" — never fed real forcing, wired to nothing, no error ever measured | Claim only what is built: drift physics + CPA against the ship's future track, error unmeasured | **DONE** |
| 3 | Deck: "re-plans automatically as new data arrives" — no such control existed, and daily re-planning measured *slower* | Removed. The new console has a time-aware search; the measured null result is reported | **DONE** |
| 4 | Deck: "1,096 files … harvested automatically every day, zero failures" merges two pipelines; the daily cron has ~7 files and failed once | Split into the two true statements | **DONE** |
| 5 | Deck: "42.6 MB → 5.0 MB, 8.4×" matches no recorded run (logs show 8.2–8.3× / 5.1–5.2 MB) | Quote the log range, or the new measured pack | **DONE** |
| 6 | Deck: "a full data pack is 76 KB" — that is an 824-cell sample box; the full corridor is *estimated* 0.5–1 MB and unmeasured | Replaced with the **measured 7.8 KB daily pack** | **DONE** |
| 7 | Deck states +18.5/+30.6 % without the repo's own leakage caveat | Caveat carried in the same eyeline as the number | **DONE** |
| 8 | Deck: "8.6-day route" presented as a voyage duration | Labelled ideal steaming time | **DONE** |
| 9 | The repo's own "Do not say" list missed corrections 3, 4, 5 and 6 | Extend the list; the guard rails had a hole, not just the deck | **DONE** — `docs/RUN_OF_SHOW.md` |
| 10 | `isih/data` is a symlink into a sibling git worktree; an ordinary tidy-up deletes the archive | Move the archive out of any worktree | **OPEN** — P0, one command, needs the user's disk layout |

## P1 — honesty and correctness of the system itself

| # | Finding | Correction | Status |
|---|---|---|---|
| 11 | §49, the semantic-lossless operating instruction, was lost in compression — the safeguard that would have caught the other losses | Reinstated at the head of the audit and in `docs/QUALITY_GATE.md` | **DONE** |
| 12 | CORE TECHNICAL MILESTONE and the 10-point IMPLEMENTATION QUALITY GATE were lost | Reinstated as a checklist with per-stage status, applied to what exists | **DONE** — the iceberg row fails it |
| 13 | MARPOL was named in the master prompt and lost | Reinstated with the one place it touches this software | **DONE** — `STANDARDS_ALIGNMENT.md` §7A |
| 14 | The 12-question competitive benchmark was lost; only §30's weaker version survived | Reinstated and applied to five competitors | **DONE** — `COMPETITIVE_ANALYSIS.md` |
| 15 | World-model fields were labelled "replay"; they contain no real observation | Relabelled **synthetic** — §27's SIMULATED INPUT — with a tooltip saying so | **DONE** |
| 16 | The bridge console had per-panel provenance but no global data-mode declaration | SYNTHETIC ENVIRONMENT badge; behavioural test 10 now covers both consoles | **DONE** |
| 17 | `np.random.default_rng` is not guaranteed stable across NumPy versions; the demo runs on a different Python than it was built on | All draws moved to blake2b; verified identical across `PYTHONHASHSEED` | **DONE** |
| 18 | `isih/features.py` never reads the QA flag: the model was trained **with** the land-spillover zeros that are the project's own headline finding | Retrain with `ice_quality.load_sic` | **OPEN** — needs a Kaggle run |
| 19 | `models/sic_correction/unet.py` defaults describe a 3.0 M-parameter model that was never trained (the trained one is 1.93 M) | Make the defaults match what was trained, or delete them | **OPEN** |
| 20 | The December 2019 replay window lies inside the model's training slice | Harmless while the demo runs no model; **becomes a leak the moment model output is shown on those dates.** Recorded in the audit and the run-of-show | **DONE** (as a rule) |
| 21 | Two docs disagree on in-corridor iceberg count (15 vs 11), and "in corridor" is a longitude-band test | Reconcile and define the test | **OPEN** |

## P2 — capability gaps the audit says to close, in order

| # | Gap | Correction | Status |
|---|---|---|---|
| 22 | §13 alerting had **zero code** | P1/P2/P3 with all nine mandated fields, raised by gate transitions and world events, no alert without a route consequence | **DONE** — `isih/demo/voyage.py` |
| 23 | §8 back half: forward trajectory, uncertainty growth, comparison against the ship's **future** track | Built; projection stops at 72 h; uncertainty grows 13 km/day | **DONE** |
| 24 | §32: weather-in-corridor and hazard-timeline panels had no UI at all | Both built, 6/12/24/48 h | **DONE** |
| 25 | The router had no time dimension, so the forecast could never reach the route | Time-aware search: each cell costed with the conditions valid at arrival | **DONE** — `isih/sim/router.py` |
| 26 | Fuel and time were collinear, so "fuel-efficient routing" was unsubstantiated | Fuel expressed per distance with independent ice and wave resistance; measured 14 % fuel for 72 % time on different tracks | **DONE** |
| 27 | Reachability was a boolean resting on an invented 80 % limit | `critical_ice_limit()` returns the assumed limit at which reachability flips | **DONE** |
| 28 | §14 sensors: no NMEA, no AIS | NMEA 0183 with correct checksums derived from the real track; AIS targets on the chart | **DONE**, badged simulated |
| 29 | §23/§28 pack size asserted, never measured | Measured by building and gzipping the real payload: **7.8 KB** | **DONE** |
| 30 | 48A.19 bathymetry/UKC/CATZOC absent | Download GEBCO + TID; wire `min_depth`; close the chart gate | **OPEN** — smallest gap, largest regulatory payoff |
| 31 | 48A.16 source disagreement has no implementation | Adopt EOS-06 as an independent ice-edge check | **OPEN** |
| 32 | §18 voyage phase, §19 mission stoppage, §21 route intelligence, §24 comms, 48A.20 rescue, 48A.21 escort | Designed; not built | **OPEN** |
| 33 | No age, no valid/issue/received time, no tier badge on any field | The project's own rule says a field with no tier badge is a bug | **OPEN** — cheapest large gap |
| 34 | Decision log is in-memory and does not survive a restart; sign-in accepts any string | SQLite plan of record; real identity | **OPEN** — pilot blocker |

## P3 — evidence that must be produced

| # | Experiment | Why | Status |
|---|---|---|---|
| 35 | Leakage ablation (causal background) | Our largest number is our most contaminated. **If it fails, retire +30.6 % from every slide** | **OPEN** — highest value per minute |
| 36 | Multi-date regret sweep | The pricing model rests on 3 saved days; the only measurement is 0.03 | **OPEN** |
| 37 | Stratified re-scoring (coast / MIZ / edge) | Skill has never been measured where the decision lives | **OPEN** |
| 38 | Iceberg trajectory error, leave-one-berg-out against BYU | One third of the PS title has no measured capability | **OPEN** |
| 39 | One navigator in front of the screen | No human has ever used this system in a task setting | **OPEN** — largest evidence gap relative to the claim "decision support" |
