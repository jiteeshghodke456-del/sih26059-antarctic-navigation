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

Recomputed 2026-09-02 with PolarRoute 1.1.11 (British Antarctic Survey, MIT) on
real NSIDC satellite ice, day by day. Scripts: `isih/route_regret.py`,
`isih/destination_window.py`, `isih/ice_quality.py`.

> **Correction to the previous version of this section.** The earlier figure of
> **17.4 days** was computed with a vessel configuration that was wrong in two
> places: beam 18.6 m (real: **22.4 m**) and maximum speed 14.0 km/hr (real
> service speed: **16.4 kn = 30.4 km/hr**, i.e. we had the ship at roughly half
> its true speed). Both are now verified against four independent registries.
> The old 17.4-day number should not be quoted. It is superseded by 8.6 days
> below — and that number carries its own large caveat, stated up front.

---

## 1. Headline: the destination, not the ocean, is the problem

The interesting result is not the line across the Southern Ocean. The open
ocean is easy. The result is **when the destination is reachable at all.**

For MV Vasiliy Golovnin at an 80% ice limit, through December 2019:

| | Days open | Days closed | % closed |
|---|---|---|---|
| **Bharati station cell** | 8 / 31 | **23 / 31** | **74.2%** |
| Approach point, 100 km north | 31 / 31 | 0 / 31 | 0% |

**The ship can always reach the approach. It usually cannot reach the station.**
The last 100 km is the entire problem.

This is exactly how Indian Antarctic resupply actually works: the vessel holds
at the fast-ice edge and moves cargo the remaining distance by helicopter and
landing barge — which is why Golovnin carries both. So the decision-support
question is not *"which line do we draw across the ocean"*. It is:

> **When should we arrive, will the last 100 km be open when we get there, how
> long will it stay open, and if it is shut — do we wait, or switch to air and
> barge operations?**

That is a forecasting question with a lead time of days, which is precisely the
horizon our model addresses.

---

## 2. The finding that changes how we read the data

Look at *which* December days appear open at Bharati:

| Date | With QA masking | Raw product | Status |
|---|---|---|---|
| Dec 1 | 30.7% | **0.0%** | open |
| Dec 2–6 | 81–88% | 81–88% | closed |
| Dec 7, 8, 9 | 33.7 / 35.2 / 36.3% | **0.0%** | open |
| Dec 10–20 | 87–99% | 87–99% | closed |
| Dec 21 | 80.0% | 80.0% | open (exactly at the limit) |
| Dec 29–31 | 75–79% | 75–79% | open |

**Four of the eight "open" days are days on which the raw product reports
exactly 0.0% ice.** Those are not open water. They are cells where the NOAA/NSIDC
CDR's **land-spillover filter** fired — it suppresses coastal pixels whose 25 km
microwave footprint overlaps land — and wrote the result as `0.0`, which sits
inside `valid_range [0, 100]` and is therefore accepted by any unguarded reader
as open water.

The tell was physical, not statistical: a block of exact zeros with **zero
gradient** flush against cells reading 0.59–0.64. Sea ice does not do that. The
file's own `cdr_seaice_conc_qa_flag` confirms it — bit 4,
`Land_spillover_filter_applied`, is set on exactly the bad days and clear on the
good ones.

### How widespread (measured over all 1096 days, 2018–2020)

| Measure | Result |
|---|---|
| Days on which the spillover filter fires | **1096 / 1096 (100%)** |
| Cells suppressed per day | mean **118**, max 488 |
| "Hard zero flush against heavy ice" | **100% of days**, mean 14.8 cells |
| Worst single-day no-input outage | **59,350 cells** |
| **Days with suspect cells in the 200 km box around Bharati** | **43.2%** |
| Same, around Maitri's grid cell | 23.9% |

### What we did about it

`isih/ice_quality.py` reads the QA flag and sets `Land_spillover_filter_applied`
and `No_input_data` cells to NaN. The mesh builder then drops them and meshiphi
fills from the parent cell, so an unknown coastal cell **inherits its
surroundings instead of asserting open water**.

We checked the fix moves risk in the safe direction rather than assuming it:

| | Raw mean SIC in Bharati 200 km box | After QA masking |
|---|---|---|
| 1 Dec 2019 | 46.8% | **54.6%** |
| 10 Dec 2019 | 62.5% | **65.4%** |

Masking makes the coast look **heavier**, so the router becomes more
conservative. That is the correct direction for a safety system.

**Residual caveat, stated plainly:** parent-cell fill still gives 30–36% on the
artifact days, when the surrounding pixels suggest 80–95%. The fix removes a
confident wrong answer; it does not yet give a confident right one. Treating
these cells as *unknown and therefore high-risk* — rather than filling them — is
the correct next step and is in `docs/backlog.md`.

---

## 3. The baseline ladder — replacing the straight-line strawman

The previous figure compared our route to a great-circle line. That is a
strawman and has been retired: no master sails a straight line into pack ice.
The honest baseline is **the same router given older ice**.

Departure 1 Dec 2019, Cape Town → Bharati, identical vessel and engine:

| Arm | What it represents | Planned | Actual | Blocked | Arrived |
|---|---|---|---|---|---|
| **STATIC** | plan once on departure ice, sail blind (today's practice) | 8.58 d | **8.61 d** | 0 h | yes |
| **STATIC-noQA** | same, trusting spillover cells as open water | 8.58 d | 8.58 d | 0 h | yes |
| **DAILY** | fresh observed chart every morning, no forecast | — | **9.00 d** | 9.6 h | yes (9 re-plans) |

**Read this result honestly: on this departure date, the static plan was not
punished.** Regret was 0.03 days. Daily re-planning was *slower*, not faster,
because re-planning from the ship's live position takes locally-optimal turns
that a single global optimisation avoids.

We are reporting a null result on the arm we expected to win. That matters:

- The open-ocean leg — about 5,800 km of the 5,813 km route — carries **mean
  6% ice**. There is nothing to optimise there, so a stale chart costs nothing.
- The whole decision is compressed into the final approach, where §1 shows the
  station is shut 74% of the time.
- **One departure date is one sample.** A single voyage cannot support a general
  claim in either direction. The sweep across many departure dates is not yet
  run and is the honest next step.

> **What we can say:** planning on stale ice did not cost this voyage time.
> **What we cannot yet say:** that it never does. The experiment that would
> settle it is built and takes one command per departure date.

---

## 4. Transit time — and why 8.6 days is a lower bound

`8.58 days` is **ideal steaming time only**. It is optimistic, for reasons we
can name precisely:

1. **No sea-state penalty anywhere.** PolarRoute defines `wave_resistance()` in
   `SDA.py:223` and *never calls it* — verified by reading the installed source.
   `model_resistance` sums wind and ice only. Waves act solely as a binary
   `swh > max_wave` cutoff. So the Roaring Forties impose no speed or fuel cost
   in this model at all.
2. **No station time, cargo operations, or weather holds.**
3. **Service speed assumed sustained.** The vessel's AIS-observed average across
   all conditions is **8.6 kn**, roughly half the 16.4 kn service speed we feed
   the router.
4. **No bathymetry.** GEBCO is still not downloaded; the mesh reports "no
   elevation data" for every cell, so depth and land are not constraining the
   route.

A real 43rd-ISEA-style voyage takes two to three weeks. Our 8.6 days is the
steaming component of that, not the voyage. **Do not present it as a predicted
voyage duration.**

---

## 5. Vessel configuration, and what is still uncalibrated

MV Vasiliy Golovnin (IMO 8723426), Project 10620, built Kherson 1988.

| Parameter | Value | Status |
|---|---|---|
| Beam | 22.4 m | verified, 4 registries |
| Length overall | 163.9 m | verified |
| Service speed | 16.4 kn (30.4 km/hr) | verified |
| AIS average speed, all conditions | 8.6 kn | verified |
| Ice class | RS old-system **KM(*) ULA** | **verified** (registry entry for this hull) |
| ULA → modern Arc/PC equivalent | — | **not sourced.** One Russian source explicitly denies ULA = Arc5. We do not assert an equivalence. |
| `force_limit` 96634.5 | — | **uncalibrated**: carried over from BAS's RRS Sir David Attenborough |
| `max_ice_conc` 80% | — | **a working stand-in**, not derived from the ice class. Production replaces it with an IMO POLARIS RIO calculation, which is indexed by ice *type*, not concentration. |
| Fuel | — | not quoted (ADR-012); polynomial is fitted to a different hull |

The ice class being ULA — the top non-icebreaker tier of the pre-1999 Russian
scale — is new information this session. It was previously recorded as "not
found".

---

## 6. What is honest to claim from this section

**Claim:** Bharati's own grid cell was closed to this vessel on 74% of December
2019 days, while the approach 100 km north was open every day. The operational
problem is the final approach, not the ocean crossing.

**Claim:** The NOAA/NSIDC CDR suppresses coastal cells and writes them as 0.0%.
This affects the Bharati approach box on 43.2% of days across 2018–2020, and
four of the eight days Bharati appeared reachable in December 2019 were such
artifacts. We detect and mask them.

**Claim:** Fixing the vessel specification changed computed transit from 17.4 to
8.6 days. Specification errors dominate model errors at this stage.

**Do not claim:** that daily re-planning beats static planning. On the one
departure date tested it did not.

**Do not claim:** 8.6 days as a voyage duration. It is steaming time with no
weather, no bathymetry, and no station operations.

**Do not claim:** any fuel figure.
