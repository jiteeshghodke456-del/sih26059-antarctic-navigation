# Run of show — ISIH demo

One page. What to click, what to say, and the caveat that belongs at each
moment. `docs/DEMO_PLAN.md` is the 31 Aug sprint plan and describes a fuel
toggle, an iceberg layer and offline re-planning that were never built — do not
demo from it.

The honesty rules in the master prompt are satisfied by someone saying the
caveat **out loud at the right moment**, not by a document nobody opens in the
room. Every caveat below is already true and already written down somewhere;
this file just says when to speak it.

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

**If it refuses to start, that is the product working.** It will not boot with a
missing satellite file, because rendering a gap as if it were data is the one
failure this system is built not to have. Fix the data; do not bypass the check.

Have ready, in case you are asked to prove something is real: `isih/figures/`,
`docs/ISIH_RESULTS.md`, and the GitHub Actions tab.

---

## The eight beats

**1 — The header, first sentence out of your mouth.**
Point at the amber badge: **HISTORICAL REPLAY · 1–31 December 2019.**
> "This is real NOAA/NSIDC satellite data from a past season, replayed. It is
> not live and it is not simulated. We use 2019 because it is a season with
> ground truth, so every claim on this screen can be scored."

Say this before anything moves. A judge watching ice change across a map will
otherwise assume it is live, and letting them assume it is the cheapest way to
lose the room.

**2 — The map, and the question nobody else answers.**
Green line is the computed route; dashed orange is the straight line.
> "The straight line meets 92 % ice and is blocked. That is an illustration of
> why routing is needed, not a baseline we are beating — our real baselines are
> in the results doc."

**3 — The destination cards. This is the finding.**
> "Bharati's own cell was closed 23 of 31 days. The water 100 km north was open
> every single day. The problem is not the ocean crossing. It is the last
> 100 km, and no ice map on the market answers that question for a named ship on
> a named date."

**4 — The day slider. Two caveats, both load-bearing.**
Drag it. The ice moves; the route does not.
> "The route is solved on 1 December ice and stays put. The router has no time
> dimension — it assumes a frozen environment for the whole voyage. A
> time-expanded mesh is the next build, and it is in the backlog, not in this
> screen."

Stop on **7, 8 and 9 December** (and 1 December):
> "These four show open. They are the artifact we found ourselves: the CDR
> suppresses coastal pixels and writes them as 0.0 % ice. Our QA layer flags
> them. Four of the eight days Bharati looked reachable were this."

Then stop on **21, 29, 30 and 31 December**:
> "The other four 'open' days sit at 75–80 % ice against a working limit of
> 80 % that we invented — it comes from no ice class and no POLARIS row. At a
> 60 % limit, Bharati is open on zero non-artifact days that December."

That ordering matters. The finding gets **stronger** when you volunteer this,
and a judge who spots it first gets a different demo than the one you planned.

**5 — The quality-checked / raw toggle.**
> "Same satellite, same day. Raw reads 0.0 % ice at the station. Quality-checked
> says unknown. We shipped the more cautious reading, which made our own headline
> number worse."

**6 — Protected areas.**
> "Bharati sits inside ASMA 6, a managed area India co-proposed. Annex V of the
> Environmental Protocol needs no permit to enter an ASMA — but entering an
> ASPA is prohibited without one, and Stornes is 1.9 km away. Of the 33
> protected areas on this corridor, none is marine, so none of them restricts
> our transit at all. They constrain what happens ashore. A team that drew them
> all as no-go zones would have refused to route to India's own station."

**7 — The route card.**
> "8.58 days is steaming time only — no weather, no bathymetry, no station
> operations. A real voyage is two to three weeks. Do not read this as a
> predicted voyage duration."

**8 — Close on the model, and scope it yourself.**
> "The trained model beats persistence at every horizon, +18.5 % at one day to
> +30.6 % at seven, three-way temporal split, test set scored once. One
> scoping we volunteer: the background it corrected was a reanalysis that had
> seen observations near the target date, so treat that as an upper bound on
> forecast skill rather than a measurement of it. The ablation that settles it
> is written and not yet run."

---

## If asked

**"Is the model running in this screen?"**
No. The screen serves the routing result and the satellite record. The trained
weights live in the Kaggle notebook output and are not in the repo. Say it
plainly; it is in the backlog.

**"Show me an iceberg trajectory."**
We have not drifted one. The Wagner–Dell–Eisenman equations are implemented and
tested against the paper's own coefficient table, and we ran a regime check on
the real USNIC catalogue under a declared sweep of assumed winds and currents —
because we do not have wind and current at those positions and did not invent
them. No trajectory error has been measured. It is one third of the problem
statement and it is roadmap.

**"What is your POLARIS risk index?"**
We deliberately do not publish one for this ship, and the reason is the
interesting answer — see `docs/research/POLARIS_APPLICABILITY.md`. POLARIS has
no row for her class, and the Polar Code makes that equivalency a per-ship
flag-approved assessment rather than a lookup. Guessing spans 40 points of RIO
across all three operational tiers.

**"Unplug the network."**
The page uses no tiles, no CDN and no external fonts, so it keeps working. Do
**not** claim offline re-planning — there is no re-plan button, the pack signing
and delta sync are designed and not built.

---

## Do not say

- "Live" — anywhere, about anything on this screen.
- "We beat CMEMS's own forecast." We beat persistence and raw GLORYS12.
- "Maitri closed 31 of 31." That was a no-data artifact and is now removed.
- "12 harvest runs, all green." 13 runs; the first failed at the Copernicus login.
- Any fuel number. Fuel is computed and never reported; no fuel-objective run
  has been done.
