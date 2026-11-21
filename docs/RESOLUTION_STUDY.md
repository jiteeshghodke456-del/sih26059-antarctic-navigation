# Does ocean-model resolution change the navigation answer? (F1)

**Setup.** The same 76 archived GLO12 forecast cycles (2026-08-31 → 2026-11-18,
corridor 0–80E 55–78S) were block-averaged from native 1/12° to ~1/4° and ~1°,
then every resolution was scored against the same NSIDC NRT satellite truth on
the *same* cells at leads 1, 3, 5, 7 days. Only the ocean model's information
content varies: truth, persistence and the scoring mask are identical.
Produced by `scripts/resolution_study.py`; numbers in
`isih/figures/resolution_study.json`, figure in `resolution_study.png`.

## Result

RMSE (SIC fraction), raw CMEMS forecast by resolution:

| Lead | 1/12° | 1/4° | 1° | persistence |
|---|---|---|---|---|
| 1 d | 0.1020 | 0.1004 | 0.1040 | 0.1198 |
| 3 d | 0.1048 | 0.1031 | 0.1060 | 0.1439 |
| 5 d | 0.1098 | 0.1082 | 0.1099 | 0.1551 |
| 7 d | 0.1153 | 0.1137 | 0.1142 | 0.1641 |

Mean IIEE at the 15% threshold (10³ km²):

| Lead | 1/12° | 1/4° | 1° | persistence |
|---|---|---|---|---|
| 1 d | 195.1 | 189.7 | 203.3 | 187.7 |
| 3 d | 194.6 | 190.3 | 209.3 | 211.7* |
| 5 d | 200.2 | 197.7 | 222.7 | — |
| 7 d | 210.2 | 208.3 | 244.2 | — |

*persistence IIEE decays with lead; full values in the JSON.

## What it says, plainly

1. **Point-wise RMSE cannot see resolution.** Coarsening to 1/4° *improves*
   RMSE slightly and even 1° roughly ties. This is the classic double-penalty
   effect: a sharp forecast that misplaces an edge feature pays twice (miss +
   false alarm), while a smoothed field pays once. RMSE flatters blur.
2. **The ice edge can.** IIEE — the metric that measures where the 15% edge
   actually is — degrades clearly at 1°: +4–16% over 1/12° growing with lead,
   +34,000 km² of misplaced edge by day 7. For passage planning the edge is
   the quantity that matters.
3. **1/12° vs 1/4° is indistinguishable here.** In this corridor, this season,
   by these two metrics, the step from 1/4° to 1/12° adds nothing persistence
   and IIEE can detect — an honest null result worth discussing, not hiding.

## The caveat that keeps this honest

Coarsening one model's output is **not** the same as running a coarser model.
Block-averaging removes resolved structure but keeps 1/12°-informed physics —
eddies already shaped the mean before we blurred it. A true resolution
experiment needs the same model *run* at several resolutions (e.g. the ANHA
family of regional NEMO configurations). The NEMO-native reader (F2) is what
would let such runs drop into this exact pipeline and answer the question
properly.

## F3: do eddies change iceberg tracks?

Same coarsening applied to the analysis currents driving the slice-5 USNIC
hindcast (`scripts/berg_resolution.py`, numbers in
`isih/figures/berg_resolution.json`), 88 segments, 8 giants, Sep–Nov 2026:

| Currents | ok / grounded-flagged | median err (all) | median err (moving bergs) |
|---|---|---|---|
| 1/12° | 81 / 7 | 4.35 km/day | 6.01 km/day |
| 1/4° | 86 / 2 | 4.07 km/day | 5.93 km/day |
| 1° | 88 / 0 | 3.49 km/day | 5.06 km/day |

Coarser currents *reduce* the error — the opposite of the naive expectation —
and the reason is the finding, not an artifact: **most corridor giants are
grounded** (persistence error ≈ 0 km), so any resolved eddy velocity at the
berg's position advects ice that is actually anchored. Blurring the currents
suppresses those velocities and the forecast degrades toward "doesn't move",
which happens to be right for this sample. On the genuinely moving bergs
(13 segments, mostly C39) the gap narrows but coarse still wins slightly —
at weekly fix cadence and few-km USNIC accuracy this sub-sample is too small
to resolve an eddy effect either way.

What a drift system actually needs first, on this evidence, is **grounding
detection** (bathymetry + keel draught, slice 7's IBCSO data makes that
possible) — resolution of the current field is second-order until anchored
bergs stop being advected. For free-drifting bergs the eddy question stays
open and needs either more moving bergs (wider region) or daily positions
(e.g. the BYU/NIC scatterometer database).

## Pending

- U-Net column at each resolution (checkpoints regenerating on Kaggle; rerun
  `scripts/resolution_study.py` without `--no-model` once
  `models/sic_correction/checkpoints/` is populated).
