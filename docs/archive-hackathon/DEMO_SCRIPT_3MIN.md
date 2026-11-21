# 3-Minute Viva Demo Script — Bridge Console

Ground truth for this file is `docs/RUN_OF_SHOW.md` (the full, unhurried version)
and `docs/ISIH_RESULTS.md` (the numbers). This file is the **compressed,
say-it-out-loud** version for a strict 3-minute slot, timed at ~150 words/min.
Read it out loud twice before the viva — the second read is always tighter.

**Confirmed:** the app opens on "Who is on watch" → this is the `v3-compliance`
bridge-console build, not the older map+slider demo. Everything below assumes
that screen.

**Before anyone is in the room**, boot it exactly as `RUN_OF_SHOW.md` says:
```bash
cd .claude/worktrees/v3-compliance
.venv-demo/bin/python -m uvicorn isih.demo.app:app --port 8000   # or whatever port you've forwarded to 8100
```
Wait for `[demo] 31 days x 2 QA modes warmed in ~3s — ready`, then open the page
**yourself**, before the panel is watching, so a cold-start hiccup never happens
live.

---

## The one-line spine (repeat this in your head between beats)

> **Ordered. Honest. Nothing heavy runs live.**

Every beat below proves one of those three words. If you blank mid-demo, land
on whichever word matches what's on screen and rebuild from there.

---

## THE SCRIPT (438 spoken words — brisk ~150 wpm ≈ 2:55; leaves ~5s slack for clicks/load between beats. If you speak closer to 140 wpm, cut Beat 6 (Alternatives) entirely — it's the most self-contained, least load-bearing beat.)

**[0:00–0:20] Open on sign-in**
> "Three minutes — watch the workflow, this page *is* the pitch. It opens on
> 'Who is on watch,' not a map, because a real bridge doesn't start with a map
> either."
[Sign in.] Point at the amber badge.
> "Historical Replay, December 2019 — real NOAA and NSIDC satellite data,
> replayed. Not live, not simulated. Everything I show you next, we can score
> against what actually happened."

**[0:20–0:45] The ordered workflow**
[Click through: command centre → new voyage → mission.]
> "Command centre, new voyage, mission — and this radio button is the most
> consequential field in the app: the station cell was closed 23 of 31 days
> last December; the approach 100 kilometres north was open every day. Jump
> ahead — approve before mission is set — and the server refuses, 409, and
> names the step you skipped. Nothing here is a suggestion."
[Route → waypoints → review → approve.]

**[0:45–1:05] Route health — the thesis**
> "Route Health: Degraded. Not a failure — look at the bar. Three of nine
> decision gates have real data behind them right now. The other six are
> grey, not red. Grey means *unmeasured*, and we will not certify a route we
> cannot see."

**[1:05–1:30] The day slider**
[Drag toward 5 December.]
> "Position, course, speed — all computed live from the plan. Keep
> dragging... there — INVALID, in magenta. Bharati isn't reachable that day.
> That's not scripted; it comes straight from the vessel-performance mesh
> built on that day's real ice observation."

**[1:30–2:05] Stale evidence — the best 30 seconds**
[Step back, approve on a clear day.]
> "Approved, versioned, attributed. Now step forward again —"
[Step forward a day or two.]
> "— 'the evidence has moved since this plan was approved: logistics, pass
> to fail.' It names exactly what broke. Step back to the day it was
> approved instead, and it says nothing at all — because nothing changed.
> That's the whole staleness story: it only speaks up when something real
> shifts, never just because new data landed."

**[2:05–2:20] Alternatives**
[Open the decision workspace.]
> "Three corridors. Corridor B looks tighter on paper but samples *worse*
> ice — 91% against its own 55% limit — you see that before you pick it,
> not after. Tighten the limit further and the third corridor doesn't exist
> at all — not slower, unreachable."

**[2:20–3:00] Close — stack, model, connectivity, in one breath**
> "Under the hood: Python and FastAPI, plain HTML and JavaScript — no
> framework, no CDN, zero external calls after the page loads, a test
> enforces it, so this screen runs the same with the cable pulled out. The
> routes you saw were built offline by PolarRoute and meshiphi, the British
> Antarctic Survey's own open tools — nothing heavy computes live in front
> of you. And separately, scored once on held-out data: our sea-ice
> correction model beats the persistence baseline by 18.5% one day out,
> 30.6% seven days out — that model isn't running on this screen, its proof
> is in our results, and we say so rather than blur the two. Ordered,
> honest, built to work with almost no signal. That's the whole thing."

---

## If the viva panel asks — quick hits

Grouped by exactly the categories you'll get asked about. Full depth is in
`RUN_OF_SHOW.md` ("If asked" + "Do not say") and `VIVA_PREP.md` — read those
before the actual day; this is the fast-recall version.

**"What did you build this with?"**
Backend: Python, FastAPI, Pydantic. Data: `xarray` + `h5netcdf`/`h5py` reading
real NetCDF satellite files, `numpy`, `pyproj` for the polar-stereographic
grid. Frontend: plain HTML/CSS/JS, deliberately no framework and no CDN — a
test fails the build if one is added. Offline pipeline (runs ashore, not at
demo time): PolarRoute + meshiphi (BAS, open source) build the vessel meshes
and routes once; the app only ever serves those finished artifacts. Model
training: PyTorch, on a free Kaggle T4 GPU.

**"Why this model, and why not something bigger?"**
Ice: a small 3-level **residual U-Net** (~1.9M parameters this prototype)
that predicts *how wrong* the Copernicus/CMEMS forecast is, not the ice
itself from scratch — because CMEMS already runs full ocean physics
corrected by real satellites, and beating that from zero is a losing bet. If
our correction is ever zero we're exactly at the baseline — we can't be much
worse, only better. A small U-Net is also the field's own published choice
for this exact task (IceNet, Andersson et al., *Nature Communications*
2021), not a random pick — and the whole daily satellite record is only
~17,000 frames, far too small to justify a foundation model.
Icebergs: **no neural network at all** — the Wagner (2017) physics drift
model (wind, ocean current, Coriolis), because we get position updates on a
few hundred icebergs at most once a day. That's too little data for ML to be
honest; physics doesn't invent confident nonsense on scarce data.

**"How did you tweak it, and why?"**
The first design (revision 1) trained a from-scratch ensemble to forecast
ice directly, benchmarked only against persistence. Our own adversarial
review found the structural flaw before a judge could: it was quietly
conceding the comparison against CMEMS, needed ~4x the parameters, and its
"runs offline" justification was weaker. Revision 2 — what's trained and
measured now — corrects CMEMS's own forecast instead, reuses the same data
pipeline, and only has to beat a mistake CMEMS already documents, not model
ocean physics from nothing. That pivot is *why* the model beats persistence
by a growing margin the further out it forecasts (+18.5% at 1 day, +30.6% at
7).

**"What about internet connectivity and stale data?"**
Two separate, both real, on this build:
1. This screen itself makes **zero external network calls** after it loads
   — no tiles, no CDN, no external fonts, enforced by a test — so the
   interface works identically with no signal at all.
2. Every expensive step — satellite ingestion, model training, mesh and
   route building — already runs **ashore, offline, before demo time**; the
   FastAPI app only serves the finished result, so nothing heavy has to run
   live or at sea.
Staleness is handled explicitly in the workflow, not silently: every
approval is versioned, and moving to a day where new evidence flips a gate
(shown live in the demo) makes the system name exactly what changed. If
nothing changed, it says nothing.
**Be upfront if pushed further:** the production vision — one small
compressed daily pack radioed to the ship, full router running offline on
the bridge — is the target architecture in `ARCHITECTURE.md`, not something
this exact screen demonstrates today. Say that plainly if asked; it's on the
roadmap, not the desk.

**"Is the model actually running behind what I just watched?"**
No — say this plainly, don't let it blur. This screen serves the real
satellite record and the precomputed routing result. The trained model's
result lives in `docs/ISIH_RESULTS.md`, scored once on held-out data it
never trained on.

**"What's the honest weak point?"**
The background field the model corrects (GLORYS12) is a *reanalysis*, not a
live forecast — it has already seen some satellite observations near the
target date. So the measured gain is an **upper bound** on real forecast
skill, not a clean measurement of it. We say this ourselves rather than wait
to be caught.

---

## Land mines — do not say these on demo day

Pulled from `RUN_OF_SHOW.md`'s own list, because a previous draft used the
punchier, since-corrected phrasing and it's easy to reach for under pressure:

- "Live" — about anything on the main replay screen.
- "We beat CMEMS's own forecast." → We beat **persistence** and raw GLORYS12.
- "It re-plans automatically as new data arrives." → There is no auto-replan;
  the gate-flip you demo (Beat 5) is the real, built behaviour — describe
  that, not automation that doesn't exist.
- "1,096 files, zero failures" / "76 KB pack" / "8.4x, 42.6→5.0 MB" — real
  numbers, but from different pipelines/measurements than the one you're
  pointing at; don't attach them to this screen.
- Any specific POLARIS risk-index number for this vessel — we deliberately
  don't publish one (`docs/research/POLARIS_APPLICABILITY.md`).
- If a "future" or simulation toggle exists elsewhere in the UI and someone
  clicks it: that mode runs on a **synthetic** world model, not satellite
  observations — never call it a forecast or an observation if you end up
  there. Stay on the December-2019 replay screens above for the 3-minute
  slot; there's no need to open it.
