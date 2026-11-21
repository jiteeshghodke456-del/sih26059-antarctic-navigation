> **Superseded for demo day — see `docs/RUN_OF_SHOW.md`.**
> This is the 31 Aug sprint plan. It describes a fuel-vs-safety toggle, an
> iceberg hazard layer and offline re-planning that were never built, so
> demoing from it promises three things the screen cannot do. Kept as the
> record of what was planned and what the week actually delivered.

# ISIH Demo Plan — Sept 8 Deadline

Status: proposed 2026-08-31, awaiting team confirmation. 8 working days (Sept 1–8).

## The core idea — this is not a separate throwaway demo

The demo IS Phase 0 + Phase 1 of `ARCHITECTURE.md`, compressed into a focused
sprint, plus a taste of Phase 3/4's most demo-worthy moments (the routing
slider, the offline story) pulled forward because they're cheap. **Nothing
built this week is thrown away** — every hour spent is exactly the work the
real build needs anyway. This is what "without hindering the main
application" actually means: don't build a second thing, build the first
real slice of the one thing, on a tight clock.

**What's deliberately NOT in scope for Sept 8**: the trained bias-correction
model (Phase 2, the "long pole," needs 1–2 weeks + GPU time it doesn't have
yet). Instead, the demo routes on the **real raw CMEMS forecast directly** —
which is not a downgrade or a fake, it's literally `ML_ARCHITECTURE.md`
§1.5's own mandatory baseline. Judges get told plainly: "this routes on the
real operational forecast today; our trained model, which improves on it
with calibrated uncertainty, lands in the following weeks" — a roadmap
shown as strength, not a gap hidden.

## Day-by-day (6 people, working in parallel per `TEAM_GUIDE.md` roles)

**Day 1–2 (Sept 1–2) — Foundation, all in parallel**
- *Data & Ingestion Lead*: ingest the **no-auth** sources first for speed —
  NSIDC SIC, GEBCO bathymetry, GFS wind, USNIC/BYU iceberg positions. Defer
  ERA5/EUMETSAT (auth-gated) — not needed for this slice.
- *Backend/Systems Engineer*: FastAPI skeleton, `MODE=shore` only for now,
  endpoints for route/ice-map/iceberg-positions.
- *Routing Engineer*: meshiphi mesh over the corridor box (verified ~2s
  build time), Golovnin vessel subclass skeleton.
- *Frontend Lead*: React + MapLibre shell, base map rendering.
- *Calibration & Iceberg Engineer*: implement the Wagner (2017) drift model
  — pure physics, ~100 lines, zero training data, real inputs only. Perfect
  fit for this timeline.
- *ML Engineer*: not blocked waiting on GPU access — spends this window
  parsing/validating the real harvested CMEMS files (already flowing daily)
  and prepping the Phase 2 training pipeline in the background, off the
  demo's critical path.

**Day 3–4 (Sept 3–4) — The pipeline connects, first real route**
Wire it end to end: real ingested data → mesh → PolarRoute single-objective
→ FastAPI → map. *Exit target*: a real Cape Town → Bharati route renders
over real bathymetry and real observed ice — this is `ARCHITECTURE.md`'s
own Phase 1 exit criterion, reached four days early.

**Day 5 (Sept 5) — The moment that wins the room**
Add one genuinely interactive, genuinely real control: a fuel-vs-safety
weighting toggle using PolarRoute's real multi-objective runs (already
verified at ~7s/run — cheap). Move the toggle, watch the route visibly
change on a real computation, live. Iceberg exclusion zones (from Wagner,
Day 1–2) rendered as a real hazard layer the route visibly avoids.

**Day 6 (Sept 6) — The offline moment**
The architecture already computes routes from locally cached data, not live
API calls — so "disconnect the network and keep planning routes" is nearly
free to demonstrate, not extra engineering. This is the single most
memorable, hardest-to-fake moment for a judge, and it costs almost nothing
because it's how the system was already designed to work.

**Day 7 (Sept 7) — Polish and rehearsal**
Staleness/data-source labels (honest, not decorative). 2–3 real demo
scenarios saved as committed scenario packs — this is `ADR-016`'s own
design, built now instead of later, so it's not thrown away either. Full
team run-through of the live demo flow, timed.

**Day 8 (Sept 8) — Demo.**

## What could slip, and the fallback

If Day 3–4's full pipeline isn't ready, the fallback is a strict subset,
not a fake: show PolarRoute computing a real route over real bathymetry and
real ice data with the multi-objective slider (Day 5's content), even
without the iceberg layer — still 100% real, just narrower. Never fill a
gap with placeholder data; narrow the demo instead.

## Why this doesn't hinder the main build

Every deliverable above is a literal line item already in `ARCHITECTURE.md`
§4's Phase 0/1/3/4 — this sprint just re-orders and compresses them, pulling
forward the cheap, high-impact pieces (routing slider, offline demo) that
don't depend on the expensive one (trained model) still being built in
parallel by the ML Engineer, off the critical path.
