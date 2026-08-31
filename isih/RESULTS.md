# ISIH Prototype — Results

Trained 2026-08-31 on Kaggle (T4 GPU). **These are the numbers to quote.**

## Headline

**Forecasting Antarctic sea-ice concentration 3 days ahead, the model beats
every baseline — including persistence, which is the one that matters.**

| Method | Test RMSE | Our model vs. it |
|---|---|---|
| **Our model** | **0.0765** | — |
| Persistence (carry last observation forward) | 0.0958 | **+20.2%** |
| Background + per-pixel bias map | 0.1461 | +47.6% |
| Background + constant offset | 0.1572 | +51.3% |
| Raw GLORYS12 forecast | 0.1630 | **+53.1%** |

Model: 1,929,601 parameters, 12 input channels, single model (not yet an
ensemble). Trained ~41 epochs, early-stopped.

## Why these numbers are trustworthy

- **Three-way temporal split.** Train (70%) → validation (15%, used only to
  pick the epoch) → test (15%, **scored exactly once**). An earlier run
  reported +27% by selecting the best of 30 epochs on the same set it then
  reported — that number was inflated and is not used.
- **Split by time, never randomly.** Sea ice barely changes overnight, so a
  random split would put adjacent days in both train and test and produce a
  spectacular, meaningless score. This is the most common way results in this
  field are inflated.
- **Persistence is included, and it is not a strawman.** Measured on real 2020
  NSIDC data it scores 0.0359 at 1-day lead — better than any background
  correction. At 3-day lead it is 0.0958, and we beat it. Had we evaluated at
  same-day lead, persistence would have won and the honest conclusion would
  have been that the model adds nothing.
- **Baselines were computed before training**, so the bar was fixed before the
  result was known.
- **Real data throughout.** NOAA/NSIDC CDR observations (1096 files, 0 failed)
  and CMEMS GLORYS12 reanalysis. No synthetic data anywhere.

## Known caveats — state these, do not hide them

1. **Validation 0.0608 vs test 0.0765 (26% gap).** Expected in part: validation
   was used for epoch selection so it is optimistically biased. The test period
   is also the most recent time slice and may cover a harder season. **Quote
   0.0765.**
2. **Single model, no uncertainty yet.** The production design trains five and
   uses their disagreement as a calibrated safety margin that changes the route.
   The prototype does not do this yet.
3. **12 channels, not 19.** Missing ERA5 wind/temperature and OISST sea-surface
   temperature, both of which need slow authenticated downloads. Everything
   here came from data already on disk.
4. **Corrects a reanalysis, not a live forecast.** GLORYS12 is a historical
   product. Production corrects the live CMEMS operational forecast, whose
   error structure differs — a transfer this prototype does not prove.
5. **~2 years of training data**, versus 1993–2024 for production.

## What the model actually is

```
corrected SIC = clip( GLORYS12 forecast + model's predicted correction, 0, 1 )
```

It predicts the *correction*, never the field. An untrained model outputs
exactly zero and reproduces the forecast unchanged — so it starts at the
forecast's skill and can only be judged on what it adds.

**12 input channels**: the forecast valid at target time; the last 7 days of
real satellite observations; the innovation (`background − newest observation`,
i.e. how wrong the forecast is right now at this cell); day-of-year sine and
cosine; and a validity mask.

The innovation channel is the important one. Version 1 of this model saw only
the background field — no observations at all — scored 0.1051, and lost badly
to persistence. Giving the model access to what the satellite actually saw is
what closed that gap.

## Reproducing

`isih/kaggle/isih_train.ipynb` on Kaggle: Internet **On**, Accelerator **GPU
T4 x2**, and `CMEMS_USERNAME` / `CMEMS_PASSWORD` in Kaggle Secrets. It
downloads its own data. Roughly 1–2 hours.

## Next improvements, in order of expected value

1. **Five-model ensemble + conformal calibration** — turns model disagreement
   into a measured safety margin that changes the route. This is the production
   differentiator, not a scaling exercise.
2. **More training years** — NSIDC is free and needs no authentication; going
   from 2 years to 10 is a download, not new engineering.
3. **ERA5 wind and temperature channels** — the physical drivers of ice motion
   are currently invisible to the model.
4. **Report per-lead skill (1, 3, 5, 7 days)** — persistence weakens with lead,
   so skill almost certainly grows with it. A curve is far more convincing than
   one number, and it is the same evaluation run several times.
