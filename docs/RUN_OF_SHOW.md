# Run of show — ISIH bridge console

One page. What to click, what to say, and the caveat that belongs at each
moment. `docs/DEMO_PLAN.md` is the 31 August sprint plan and describes a fuel
toggle, an iceberg layer and offline re-planning that were never built — **do
not demo from it.**

The honesty rules in the master prompt are satisfied by someone saying the
caveat **out loud at the right moment**, not by a document nobody opens in the
room. Every caveat below is already true and already written down; this file
says when to speak it.

---

## Before anyone is in the room

```bash
cd <repo>/.claude/worktrees/v3-compliance
rm -rf .venv-demo                                    # sandbox venv links to the wrong python
uv venv .venv-demo --python 3.12
uv pip install --python .venv-demo/bin/python -r isih/demo/requirements.txt
.venv-demo/bin/python -m uvicorn isih.demo.app:app --port 8000
```

Wait for `[demo] 31 days x 2 QA modes warmed in ~3s — ready`, then open
<http://127.0.0.1:8000>.

**If it refuses to start, that is the product working.** It will not boot with
a missing satellite file, because rendering a gap as if it were data is the one
failure this system is built not to have. The error now names the likely cause:
`isih/data` is a **symlink into a sibling git worktree**, so removing that
worktree deletes the archive from this demo's view. See `RELEASE_AUDIT.md` P0-1.

Have ready in case you are asked to prove something: `isih/figures/`,
`docs/ISIH_RESULTS.md`, `docs/RELEASE_AUDIT.md`, and the GitHub Actions tab.

---

## The eight beats

**1 — The header. First sentence out of your mouth.**
Point at the amber badge: **HISTORICAL REPLAY · 1–31 December 2019.**
> "This is real NOAA/NSIDC satellite data from a past season, replayed. Not
> live, not simulated. We use 2019 because it has ground truth, so every claim
> on this screen can be scored."

Say it before anything moves. A judge watching ice change across a map will
otherwise assume it is live, and letting them assume it is the cheapest way to
lose the room.

**2 — Route health, and the coverage bar beside it. This is the thesis.**
> "Route health is DEGRADED, and the bar says why: three of nine decision gates
> have data behind them. The other six are grey — not red. Grey means we did not
> measure, and a gate we cannot evaluate is not a pass. This system will not
> certify a route it cannot see, and it tells you exactly which datasets it
> would need."

If you say nothing else all demo, say this. It is the difference between a
dashboard and a decision-support tool.

**3 — Own ship, then drag the day slider.**
The ship moves down its own track; position, course and speed update.
> "Position, course and speed are computed from the planned track and its
> per-leg transit times. This is where the ship *would* be, not a GPS fix —
> which is why cross-track error reads zero by construction, not by good
> steering."

**4 — Keep dragging to 5 December. The band turns magenta.**
> "INVALID. Bharati is not reachable for this ship today. That is not scripted
> — it comes from the vessel-performance mesh on that day's real observation."

**5 — Now approve on an open day, then step to a closed one.**
Type a name, click Approve, then move the slider.
> "The plan is approved, versioned, and attributed. Step forward and the system
> says: *the evidence has moved since this plan was approved — logistics: PASS
> to FAIL.* It names the gate that flipped. And if you step back to the day it
> was approved, it says nothing at all — because nothing changed. A route
> should degrade when an assumption breaks, not every time new data arrives."

That contrast is the single best thirty seconds in the demo. Do both halves.

**6 — Alternative corridors.**
> "Three corridors, and the third is the interesting one: at a 45 % ice limit
> **no route to Bharati exists at all**. Not slower — unreachable. Our 80 % limit
> is an assumption, because no ice class anywhere indexes ice *concentration* —
> they all index thickness. So this shows you where that assumption stops being
> survivable."

**If asked why B is worse:** tightening the limit from 60 % to 55 % *raises* the
worst ice sampled along the line from 74 % to 91 %. The router optimises 5°
cell means; that number comes from 25 km pixels. Volunteer this — it is a real
resolution seam and a judge who finds it first gets a different demo.

**7 — "Does the ship change the route?"**
> "Same ice, same day, two real ships. The answer is **partial, and we say so**:
> Golovnin and SA Agulhas II follow an identical 41-leg track. What changes is
> cost — 1.28 days and 9 % fuel. So do not let us claim different ships get
> different routes. The corridor *does* change when the ice constraint changes,
> 41 legs to 51, so the mechanism works — this pair of ships on this day just
> does not separate it."

**8 — Close on the model, and scope it yourself.**
> "The trained model beats persistence at every horizon, +18.5 % at one day to
> +30.6 % at seven, three-way temporal split, test set scored once. One scoping
> we volunteer: the background it corrected was a reanalysis that had seen
> observations near the target date, so treat that as an upper bound on forecast
> skill rather than a measurement of it. And the seven-day figure is our largest
> gain *and* our most contaminated one. The ablation that settles it is written
> and not yet run."

---

## If asked

**"Is the model running in this screen?"**
No. The screen serves the routing result and the satellite record. The trained
weights live in the Kaggle notebook output and are not in the repo. Say it
plainly; it is in the backlog.

**"Show me an iceberg."**
We hold the real USNIC catalogue — 11 icebergs inside this corridor, including
D15A at 3,037 km². It is **not** on this map, deliberately: the catalogue is
from September 2026 and this replay is December 2019, and drawing them together
would break the data-time synchronisation rule the rest of the system obeys. No
trajectory error has ever been measured either. It is roadmap.

**"Why isn't there weather?"**
We hold CMEMS sea-ice thickness and drift. Those are ice fields, not weather —
no wind, no waves, no visibility. The weather gate says exactly that rather than
dressing ice drift up as a forecast.

**"What is your POLARIS risk index?"**
We deliberately do not publish one, and the reason is the interesting answer —
`docs/research/POLARIS_APPLICABILITY.md`. POLARIS has no row for this hull, and
the Polar Code makes equivalency a per-ship flag-approved assessment rather than
a lookup. Guessing spans 40 RIO points.

**"Why not a foundation model?"**
We adjudicated nine — `docs/research/MODEL_REUSE_MATRIX.md`. None forecasts
sea-ice concentration or was trained on the passive microwave that observes it.
Aurora ships no sea-ice checkpoint at all. The whole daily record is around
17,000 frames, far too small for the premise that motivates foundation models.
Argue from the size of the problem, **never** from the size of our GPU.

**"Unplug the network."**
The page uses no tiles, no CDN and no external fonts, and a test fails if anyone
adds one. Do **not** claim offline re-planning — there is no re-plan button.

---

## Do not say

- "Live" — anywhere, about anything on this screen.
- "Different ships get different routes." The tracks are identical; the cost differs.
- "Fuel-optimised routing." Solving for fuel returns the same path as time.
- "We beat CMEMS's own forecast." We beat persistence and raw GLORYS12.
- "Maitri closed 31 of 31." That was a no-data artifact and is gone.
- "12 harvest runs, all green." 13 runs; the first failed at the Copernicus login.
- Any POLARIS number for this vessel.
