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

## Pending

- U-Net column at each resolution (checkpoints regenerating on Kaggle; rerun
  `scripts/resolution_study.py` without `--no-model` once
  `models/sic_correction/checkpoints/` is populated).
- F3: the same coarsening question for iceberg-drift currents
  (`scripts/berg_hindcast.py` machinery, eddy-resolving vs smoothed).
