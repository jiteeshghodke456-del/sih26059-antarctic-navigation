# ISIH Prototype — Results

Trained 2026-08-31 on Kaggle (T4 GPU). **These are the numbers to quote.**

## Headline

**Forecasting Antarctic sea-ice concentration 1–7 days ahead, the model beats
every baseline at every horizon — including persistence, the baseline that
matters.**

| Lead | Our model | Persistence | bg + pixel bias | Raw GLORYS12 | Gain vs persistence |
|---|---|---|---|---|---|
| 1 day | **0.0465** | 0.0570 | 0.1461 | 0.1630 | **+18.5%** |
| 3 days | **0.0720** | 0.0958 | 0.1461 | 0.1630 | **+24.9%** |
| 5 days | **0.0938** | 0.1204 | 0.1468 | 0.1637 | **+22.1%** |
| 7 days | **0.0968** | 0.1395 | 0.1468 | 0.1637 | **+30.6%** |

Model: 1,929,601 parameters, 12 input channels, single model per horizon (not
yet an ensemble). Same seed at every lead so the horizons are comparable.

## The claim this supports

**Our error grows more slowly than the baseline's.** From day 1 to day 7 our
RMSE rises 2.1x (0.0465 → 0.0968) while persistence rises 2.5x (0.0570 →
0.1395). The advantage is *largest at 7 days* — which is the horizon a voyage
is actually planned over.

> "The further ahead the ship needs to plan, the more the model matters."

That is an operational claim, not a benchmark score.

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

**1. The background is a reanalysis, not a forecast — and this is the sharpest
question we will be asked.**

Notice raw GLORYS12 scores 0.1630 at lead 1 and 0.1637 at lead 7 — essentially
flat. A real forecast degrades with lead time; this does not, because GLORYS12
is a *reanalysis*: it assimilates satellite observations, including near the
date being predicted. So channel 0 may carry information about the target that
a genuine forecast would not have.

*The expected question:* "Your background already saw the observations you are
predicting. Isn't that leakage?"

*The honest answer:* Partly defended by the numbers — if GLORYS12 contained the
answer, its own RMSE would be near zero rather than 0.163, which is worse than
persistence at every horizon. So it is not handing over the target. But it may
carry some future signal, and we do not claim otherwise. **The clean test is the
ablation below**, and production corrects a real CMEMS forecast where this
cannot arise.

**2. Validation scores better than test at every lead** (e.g. lead 3: val 0.0611
vs test 0.0720). Expected: validation selects the epoch, so it is optimistically
biased, and the test slice is the most recent period, possibly a harder season.
**Always quote the test numbers.**

**3. Single model per horizon, no uncertainty layer yet.** Production trains
five and turns their disagreement into a calibrated safety margin that changes
the route. This prototype does not do that.

**4. 12 channels, not 19.** No ERA5 wind/temperature, no OISST sea-surface
temperature — the physical drivers of ice motion are currently invisible to the
model. Everything here came from data already on disk.

**5. ~2 years of training data** (2019–2020), versus 1993–2024 for production.

**6. Corridor region only** (5°W–85°E, 48°S–80°S), not circumpolar.

## The ablation that settles caveat 1

Retrain with channel 0 (the background) zeroed, leaving only real past
observations and derived channels:

- **If the score barely moves** — the background contributes little, leakage is
  a non-issue, and the model's skill comes from observation history. Strongest
  possible answer to the question.
- **If the score drops sharply** — the background is doing real work, and we
  must state that the prototype's numbers may not transfer to a live-forecast
  setting until production tests it.

Either outcome is worth having before a viva. Not yet run.

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

1. **The no-background ablation** (above) — costs ~20 minutes and either kills
   the leakage objection outright or tells us something we are obliged to
   disclose. Highest value per minute of anything on this list.
2. **Five-model ensemble + conformal calibration** — turns model disagreement
   into a measured safety margin that changes the route. The production
   differentiator, not a scaling exercise.
3. **More training years** — NSIDC needs no authentication; 2 years to 10 is a
   download, not new engineering.
4. **ERA5 wind and temperature channels** — the physical drivers of ice motion
   are currently invisible to the model.

---

# Routing Result — Cape Town → Bharati

Computed 2026-08-31 with PolarRoute 1.1.11 (British Antarctic Survey, MIT) on
real satellite ice for **1 December 2019**, the start of the real resupply
season. Figure: `isih/figures/route_map.png`.

| | Value |
|---|---|
| Voyage time | **17.4 days** |
| Waypoints | 59 |
| Max ice on our route | **79%** |
| Max ice on the straight line | **92%** |
| Vessel ice limit (`max_ice_conc`) | 80% |

## The claim, and how it was verified

**"The direct path is blocked; our route stays passable."**

Sampled ice concentration densely along both paths against the same satellite
field: the straight line exceeds the ship's 80% limit over 3.7% of its length,
peaking at 92%. Our computed route never exceeds 79%.

## A claim we had to withdraw

The first version of this figure said the route *"bends around the thickest
ice."* Measuring showed that is **false**: the time-optimal route crosses
*more* average ice than the straight line (19.6% vs 8.4%), because it trades
moderate ice for a shorter path. Only the maximum matters, and there the route
genuinely wins.

The figure now computes its own numbers at render time, so the annotation
cannot drift from the data if the route or date changes.

**If asked "does your route avoid ice?"** — the honest answer is: it avoids
*impassable* ice, and accepts moderate ice where that is faster. That is what
optimising travel time under a hard ice constraint actually means, and it is a
better answer than a vague claim about avoidance.

## Caveats

1. **No bathymetry.** GEBCO is not downloaded, so depth is not constraining the
   route. The mesh reported "no elevation data" for every cell. Shallow water
   and land are therefore *not* being avoided — this must be added before any
   claim about navigational safety.
2. **Optimised for travel time only.** Fuel and risk-weighted objectives are
   not yet run, so this is one route, not a Pareto set.
3. **Observed ice, not forecast ice.** This route uses what the satellite
   measured that day. Wiring the trained forecast model into the router is the
   next step and is what makes it a *decision-support* tool rather than a
   hindsight map.
4. **Fuel figure is uncalibrated** and deliberately not quoted (ADR-012).
