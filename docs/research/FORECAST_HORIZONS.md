# Forecast Horizons — what this system may honestly claim to see, and for how long

Settles master-prompt **§48A.7 "Forecast horizons must be explicit"** and the late
section **"Forecast Horizon Discipline"**: *do not use the word "forecast" without
defining the relevant horizon.*

Research file. Every number below is either read out of a primary source named
inline, measured from this repository this session, or marked **UNVERIFIED** with
the specific thing that would settle it. Nothing here is a design decision —
proposals go to `docs/backlog.md` until an ADR is written. Two things in §3 and
§4 contradict text already in the repo; both are flagged where they occur.

Register and evidence rules follow `docs/NAVIGATION_RESEARCH.md`.

---

## 0. The rule this file enforces

"Forecast" without a horizon is not a claim, it is a mood. Every predicted field
this system displays or routes on must carry three numbers, not one:

1. **Valid time** — the instant the prediction is *about*.
2. **Lead time** — valid time minus the cycle's initialisation time. This is what
   determines the error.
3. **Forecast age** — now minus initialisation time. A 3-day-lead field from a
   4-day-old cycle is a 7-day-lead field wearing a disguise, and it is the single
   easiest way for a decision-support tool to lie to a bridge team.

The distinction between (2) and (3) is the reason §48A.15's data-freshness
contract and §48A.24's model-time synchronisation exist as separate requirements.
They are the same failure seen from two ends.

---

## 1. Tier vocabulary — two authorities, and they do not say the same thing

There are two established taxonomies. The producer-side one is normative; the
user-side one is what a master actually thinks in. Use both, and say which.

### 1.1 Producer side — WMO

**Source: WMO-No. 485, *Manual on the Global Data-processing and Forecasting
System*, 2019 update, Appendix 1.1 "Definitions of meteorological forecasting
ranges"** (full text retrieved and parsed;
`https://www.nmc.cn/userfiles/ueditor/userid/files/cms/article/2019/07/1562050831112.pdf`).
Referenced normatively by §1.2.1.1 of the same Manual.

| # | Range | Bounds, verbatim |
|---|---|---|
| 1 | Nowcasting | current weather parameters and forecast parameters **0 to 2 hours** ahead |
| 2 | Very short-range weather forecasting | up to **12 hours** ahead |
| 3 | Short-range weather forecasting | **12 to 72 hours** ahead |
| 4 | Medium-range weather forecasting | **72 to 240 hours** ahead |
| 5 | Extended-range weather forecasting | **10 to 30 days** |
| 6 | Long-range forecasting | **30 days up to two years** |

Note what falls out of this immediately: the Cape Town → Bharati transit, at the
project's own measured 8.6 days of ideal steaming, is a **medium-range** problem
end to end, and the moment the ship falls below service speed it becomes an
extended-range problem — a range in which no operational sea-ice product this
project can obtain produces anything at all.

### 1.2 User side — how ice-going operators actually tier it

**Source: Wagner, P. M., Hughes, N., Bourbonnais, P., et al. (2020),
"Sea-ice information and forecast needs for industry maritime stakeholders",
*Polar Geography* 43(2–3), 160–187, doi:10.1080/1088937X.2020.1766592.** Full
text read via NERC Open Research Archive
(`https://nora.nerc.ac.uk/id/eprint/527976/`).

The paper divides forecasts into "long (climate), medium (sub-seasonal 5–10
days) to seasonal (3 months), and short (daily to weekly) range lead times",
and maps these onto stakeholder decisions:

- **Tactical** — "basic security of people and operations (weather forecast
  horizon)". Navigators adjusting routes daily, "searching for openings or areas
  of minimal ice cover". Needs NRT imagery, short-range met/ocean, and ice drift
  and pressure forecasts.
- **Operational** — "immediate planning (sub-seasonal)". Sub-seasonal to
  seasonal. Shipping schedules, window selection.
- **Strategic** — climate, 1–10 years. Season length, ice-class selection,
  commercial viability.

★ **This is the tiering that matters for us**, because the Bharati access
decision is *tactical* in Wagner's sense (hours to days, taken by the master,
near the ice) while the departure decision is *operational* (a schedule choice
taken weeks earlier). Presenting both in the same colour on the same map is
precisely what §48A.7's last sentence prohibits.

---

## 2. Sea ice

### 2.1 What this project can actually obtain, and its true lead length

**Product: CMEMS `GLOBAL_ANALYSISFORECAST_PHY_001_024`.**
Sources: Product User Manual **CMEMS-GLO-PUM-001-024, Issue 2.4, July 2026**
(`https://documentation.marine.copernicus.eu/PUM/CMEMS-GLO-PUM-001-024.pdf`) and
Quality Information Document **CMEMS-GLO-QUID-001-024, Issue 1.3, May 2025**
(`https://documentation.marine.copernicus.eu/QUID/CMEMS-GLO-QUID-001-024.pdf`).
Both PDFs downloaded and text-extracted this session.

| | |
|---|---|
| Product type | Near-real-time analysis **and** forecast |
| Available time series | **−2 y to 10 days-forecast** |
| **Forecast update frequency** | **Daily** |
| **Forecast target delivery** | **daily at 12:00 (noon) UTC** |
| Analysis update frequency | **Weekly**, delivered **Thursdays 12:00 UTC**; 14-day hindcast |
| Horizontal resolution | 1/12° (≈ 8 km), 50 levels |
| System / model | GLO12v4, NEMO 3.6, **LIM3** sea ice, EVP rheology, **11 ice categories** |
| Atmospheric forcing | **ECMWF IFS HRES**, 1/10°, 1–3–6-hourly |
| Wave forcing | MFWAM 1/10°, 3-hourly, **temporally extrapolated for the last 12 h of the forecast** |
| Assimilated | L3S SST (ODYSSEA), **SIC (OSI SAF)**, SLA (AVISO), T/S profiles (CORIOLIS) |
| Ice variables | `siconc`, `sithick`, `usi`, `vsi`, plus age, albedo, surface temperature, snow thickness |

★ **Measured in this repository, 2026-09-07** — `data/cmems_forecast_archive/cmems_siconc_2026-09-06.nc`
carries **10 daily time steps, 2026-09-06T00:00 through 2026-09-15T00:00**, over
the harvest box **55–78 °S, 0–80 °E** (note this is *not* the ISIH training
corridor, which is 48–80 °S / 5 °W–85 °E — the two boxes differ and should be
reconciled), variables `siconc, sithick, usi, vsi`.
The first step is the cycle date itself. **The real forecast lead the project
holds is therefore D+0 through D+9 — nine days ahead, not ten.** Say "nine-day"
in the deck, or say "10 daily steps including the analysis day". Do not say
"10-day forecast" and then plot a D+10 field, because there isn't one.

`scripts/harvest_cmems.sh` requests `CYCLE_DATE` to `CYCLE_DATE +10 days`; the
server returns 10 steps. The workflow's 12:23 / 17:23 UTC cron slots are correct
and load-bearing: the PUM guarantees delivery only *by* 12:00 UTC, so anything
earlier risks archiving yesterday's bulletin under today's name.

### 2.2 CMEMS's own declared sea-ice skill, and the direction of its bias

QUID Table 5, calibration year 2019, sea ice concentration in **%**, against
CMEMS Sea Ice TAC observations, for the **ACC** (Antarctic Circumpolar) region:

| Region | Hindcast mean bias | Hindcast RMSD | Forecast day 3 mean bias | Forecast day 3 RMSD |
|---|---|---|---|---|
| ARC (Arctic) | 5 | 10 | −5 | 18 |
| **ACC (Antarctic)** | **2** | **8** | **−0.7** | **10** |

The QUID states that the day-3 estimated-accuracy numbers for SST, SLA and sea
ice cover were recomputed in 2023 "not using background model first trajectory
of the hindcast simulation but the real-time forecasts" — so the ACC day-3 RMSD
of 10 % is a genuine forecast number, not a hindcast in disguise.

★ **The bias direction is the operationally important part.** QUID §I.2.5:
*"Sea ice concentration is underestimated in the Antarctic during austral
summer (also due to atmospheric forcing errors)."* The Indian resupply season
**is** austral summer. The background field this project corrects is biased
**low on ice** in exactly the season and region it will be used, and low-on-ice
is the dangerous direction. Any claim about the corrected product must state
whether the correction removes that bias or inherits it — currently unmeasured
(`docs/ISIH_RESULTS.md` reports RMSE only, not signed bias).

### 2.3 The Antarctic short-range benchmark that matters most

★ **Source: Zhao, F., Liang, X., et al. (2024), "Southern Ocean Ice Prediction
System version 1.0 (SOIPS v1.0): description of the system and evaluation of
synoptic-scale sea ice forecasts", *Geoscientific Model Development* 17,
6867–6886, doi:10.5194/gmd-17-6867-2024.** Open access; full PDF read this
session.

This is the closest published analogue to what this project is building, and it
is set in **our exact region**. SOIPS is an Antarctic regional coupled sea
ice–ocean–ice shelf model with a 12-member ensemble Kalman filter (LESTKF)
assimilating near-real-time AMSR2 SIC, **forced by operational GFS** — the same
atmospheric product `docs/DATASET.md` verifies. It was run operationally for the
38th CHINARE expedition. Evaluation period: a complete melt–freeze cycle,
1 Oct 2021 – 30 Sep 2022, verified against **independent, non-assimilated**
EUMETSAT OSI SAF data.

**Sea ice concentration RMSE, annual mean, DA_Forecast run:**

| Lead | 24 h | 72 h | 120 h | 168 h |
|---|---|---|---|---|
| SIC RMSE | **0.15** | **0.16** | **0.17** | **0.19** |

**Sea ice drift, MAE (Table 1 of that paper):**

| Lead | 24 h | 72 h | 120 h | 168 h |
|---|---|---|---|---|
| Drift magnitude (cm s⁻¹) | 2.14 | 2.09 | 2.17 | **2.22** |
| Drift direction (°) | 2.13 | 2.08 | 2.42 | **2.81** |

Observed NSIDC drift magnitudes for scale: **10.22 cm s⁻¹** (Oct–Dec),
4.78 (Jan–Mar), 10.55 (Apr–Jun), 13.26 (Jul–Sep). At 168 h the magnitude error
is **23 % of the observed magnitude**. Ice thickness MAE at 24 h is **< 0.3 m**,
which the authors note is inside the ICESat-2 observational uncertainty.
Integrated ice-edge error is **≈ 0.5 × 10⁶ km² at 24 h** and **below
1.0 × 10⁶ km² at 72 h** in most freezing months.

Three conclusions follow, and they are the backbone of this file:

1. **Antarctic SIC error grows slowly out to 7 days when the model is
   assimilating.** 0.15 → 0.19 is +27 % over six days of extra lead. The field
   reorganises far faster than that; data assimilation is what holds the error
   down. A free-running model does not get this curve — SOIPS's own
   `NoDA_Forecast` run "performs the worst in most months".
2. **Persistence is not a strawman here and is not trivially beaten.** SOIPS's
   `PE_Forecast` run (which carries observed SIC information) beats the
   no-assimilation run and loses to the full DA run — but *"during late
   March–early June, the PE_Forecast run performs worse than the other two runs
   at a lead time of 168 h, suggesting that sea ice changes rapidly in response
   to the oceanic and atmospheric forcing during this onset-to-rapid-freezing
   period."* Persistence degrades when the ice is actually doing something.
3. ★ **The error is the same size as the observations disagree with each
   other.** The paper measures AMSR2 against OSI SAF directly: RMSE between the
   two products *"increase in the melting season, reaching a maximum value of
   0.24 in February; thereafter … maintaining below 0.15 in the rest of the
   freezing season."* **A 7-day Antarctic SIC forecast error of 0.19 sits inside
   the disagreement between two satellite SIC products in the melt season.**
   That is the noise floor, and it caps what any amount of modelling can be
   *shown* to achieve.

★ **And SOIPS's operational use case is our problem exactly.** §3.5 of that paper
describes navigating MV *Xue Long* to Zhongshan Station — **69°22′24.76″ S,
76°22′14.28″ E**, which is ≈ 5 km from Bharati's grid cell at 69.4 °S, 76.2 °E.
The decision is the timing of the open-water band between the drifting pack and
the landfast ice, and the tool is a **sea ice convergence rate forecast at
24, 48 and 72 h**. Independent confirmation of `docs/ISIH_RESULTS.md`'s finding
that "the last 100 km is the entire problem" — and a demonstration that the
operational answer to it is a *three-day* forecast taken from near the ice, not
a nine-day forecast taken from Cape Town.

### 2.4 The Antarctic-versus-Arctic predictability gap — real, documented, and it bites

- **Zampieri, L., Goessling, H. F., & Jung, T. (2019), "Predictability of
  Antarctic Sea Ice Edge on Subseasonal Time Scales", *Geophysical Research
  Letters* 46, doi:10.1029/2019GL084096.** Antarctic sea-ice prediction skill is
  **on average 30 % lower than in the Arctic**, and only ECMWF's system was more
  skilful than climatological and persistence benchmarks, remaining so to
  **≈ 30 days**. Skill highest in the **west** Antarctic sector during the early
  freezing season.
- **Gao, Y., Xiu, Y., Nie, Y., et al. (2024), "An Assessment of Subseasonal
  Prediction Skill of the Antarctic Sea Ice Edge", *JGR Oceans* 129(11),
  e2024JC021499, doi:10.1029/2024JC021499.** Newer S2S/C3S generation, Spatial
  Probability Score. ECMWF/C beats the 10-year climatology benchmark (CLIM-B) to
  **≈ 38 days**; UKMO to **≈ 25 days**; a multi-model forecast to **≈ 60 days**.
  On the IIEE metric UKMO reaches **47 days** and ECMWF/C **≈ 42**. But DWD,
  ECCC/C, MF/C, IAP-CAS, JMA and MF/S *"consistently fall below"* the damped
  anomaly persistence benchmark (DAMP-B) — i.e. most operational systems do not
  beat a well-constructed statistical baseline in the Antarctic at all.

★ **Two caveats before any of this is carried into our claims.** First, these
are *ice-edge, basin-scale, subseasonal* results — they say nothing about
corridor-scale SIC at 1–9 days, which is our problem. Second, Gao et al. report
that dynamical systems predict the ice edge better in **West** Antarctica than
in **East** Antarctica. Our corridor (5 °W–85 °E) is East Antarctic. The
published skill numbers are therefore an *upper* bound on what applies to us,
not an average.

### 2.5 Where this project's own measured curve sits

From `docs/ISIH_RESULTS.md` (test-set RMSE in SIC fraction, corridor
5 °W–85 °E / 48–80 °S, NOAA/NSIDC CDR reference):

| Lead | This project | Persistence | Gain |
|---|---|---|---|
| 1 day | 0.0465 | 0.0570 | +18.5 % |
| 3 days | 0.0720 | 0.0958 | +24.9 % |
| 5 days | 0.0938 | 0.1204 | +22.1 % |
| 7 days | 0.0968 | 0.1395 | +30.6 % |

★ **The season the test slice falls in is a horizon fact, not a footnote.**
`docs/ISIH_RESULTS.md` records that the held-out slice — the last 15 % of
2019–2020 — falls in the **austral melt season**, and that full-year 2020
persistence is substantially easier to beat than melt-season persistence
(0.0610 at 3 days and 0.0893 at 7 days full-year, against 0.0958 and 0.1395 on
the test slice). The document's instruction to always quote the table, never the
full-year number, is correct and matters here for two reasons beyond the
period-mismatch trap it names:

1. **The melt season is the resupply season.** The model was scored on the
   season the voyage actually happens in, not on the annual average. That is the
   right test and it should be said out loud — most sea-ice papers report annual
   means, which are flattered by winter days when the ice barely moves and
   persistence is nearly free.
2. **It is also the season in which the reference product is worst** — see §2.6.
   Both the model's score and its benchmark are measured through a noisier lens
   than an annual mean would be. That cuts against the project, not for it, and
   is worth volunteering before a judge finds it.

**Placing it — what is comparable and what is not.**

The **only** honest cross-comparison is the *relative* gain over persistence,
and there is a close published analogue for exactly that:

★ **Palerme, C., Lavergne, T., Rusin, J., Melsom, A., Brajard, J., Kvanum, A. F.,
Macdonald Sørensen, A., Bertino, L., & Müller, M. (2024), "Improving short-term
sea ice concentration forecasts using deep learning", *The Cryosphere* 18,
2161–2176, doi:10.5194/tc-18-2161-2024.** Deep-learning post-processing of the
TOPAZ4 operational forecast's SIC, **separate models per lead from 1 to 10
days**, AMSR2 reference, 2022 test year. Reported RMSE reductions:

| Against | Mean | Range across leads |
|---|---|---|
| Raw TOPAZ4 forecast | 41 % | 28–62 % |
| **Persistence of AMSR2 SIC** | **29 %** | **19–33 %** |
| TOPAZ4 bias-corrected | 23 % | 19–26 % |
| Anomaly persistence | 27 % | 21–31 % |

Integrated ice-edge error reduced 44 % vs TOPAZ4 and 32 % vs persistence.

**This project's +18.5 % to +30.6 % over persistence sits inside Palerme's
19–33 % band.** That is the right thing to say to a judge: the result is neither
implausibly good — which would invite a leakage accusation the project already
half-concedes — nor trivially small. It is what a competently executed
post-processing model of this class achieves.

Caveats, stated inline rather than buried: **Palerme is Arctic**; it corrects a
genuine operational *forecast* while the ISIH prototype's background channel is
the GLORYS12 *reanalysis* (`docs/ISIH_RESULTS.md` caveat 1, unresolved pending
the no-background ablation); it uses AMSR2 as reference where we use NSIDC CDR;
and it trains one model per lead as we do. Palerme also records, citing Röhrs et
al. (2023), that TOPAZ4's raw forecasts *"in most cases [are] not better than
persistence of the SIC observations for short lead times"* — a reminder that
beating persistence at 1–3 days is a real achievement, not a formality.

**What is NOT comparable:** our 0.0465–0.0968 against SOIPS's 0.15–0.19. Different
reference product, different domain (corridor box versus circumpolar, and a
circumpolar mean is dominated by the marginal ice zone where errors are largest),
different period, and a reanalysis background versus a true forecast. Do not put
those two columns side by side. **State the shape agreement instead**, which is
real and defensible: both curves grow sub-linearly and both grow more slowly than
persistence.

### 2.6 The observation floor — why the absolute RMSE is the wrong headline

**Source: NOAA CDR Program, *Sea Ice Concentration Climate Algorithm Theoretical
Basis Document*, CDRP-TMP-00060107, Rev. 12**
(`https://nsidc.org/sites/default/files/documents/technical-reference/cdrp-atbd-rev12-sea-ice-concentration-final.pdf`).
Full text read.

§4.2.2: *"Several assessments … indicate a precision of ~5 % with an accuracy of
~10 % during mid-winter conditions away from the coast and the ice edge …
However, uncertainties are higher under some conditions — most notably near the
ice edge and when the surface is undergoing melt."* Partington et al. (2003) found
the difference against operational charts *"rose to more than 20 % in summer"*.

Table 10, error budget, in % concentration:

| Error source | Typical magnitude and bias | Regime |
|---|---|---|
| Sensor noise | ± 1 % | all |
| IFOV / gridding | < 5 % | winter pack ice |
| **IFOV / gridding** | **0–100 %** | **sharp gradients — ice edge, coast** |
| Physical temperature | < 5 %, low | winter, cold |
| **Thin ice** | **~30–50 %, low** | **near ice edge, fall freeze-up** |
| **Surface melt** | **~10–30 %, low** | **summer** |
| Wind | 5–20 %, high | open water |
| Water vapour / liquid water | 0–20 %, high | open water and ice near edge |

For comparison, EUMETSAT **OSI SAF OSI-401-b** (10 km sampling, daily, **5 h
timeliness** from sensing to dissemination, `https://osi-saf.eumetsat.int/products/osi-401-b`)
declares a **target accuracy of 10 % for the Northern Hemisphere and 15 % for the
Southern Hemisphere**, verified against high-resolution manual ice charts. The
Antarctic figure is worse *by design*, not by accident.

★ **Consequence, and it is uncomfortable but it is the honest reading.**
This project's day-1 test RMSE of **0.0465** is *below* the ~10 % stated accuracy
of the record it is scored against and at the ~5 % stated precision. Its day-7
RMSE of **0.0968** is *at* that accuracy. **At short leads the model's error is
inside the observational uncertainty of its own reference, so the absolute score
cannot distinguish it from a perfect forecast — and cannot be improved in a way
this reference could detect.**

And it is worse than the headline figures suggest, because of §2.5: **the test
slice is the austral melt season, which is the single worst regime in the CDR's
own error budget.** Surface melt contributes a ~10–30 % low bias in summer
(Table 10); Partington et al. (2003) found the difference against operational
charts *"rose to more than 20 % in summer"*; and SOIPS measured the AMSR2-versus-
OSI SAF disagreement peaking at **0.24 in February**. The reference is at its
noisiest in precisely the season the model was scored in — and in precisely the
season the ship sails.

Three things follow:

- The defensible headline is the **relative gain over persistence measured on
  the same reference**, where the shared observational error largely cancels.
  `docs/ISIH_RESULTS.md` already leads with the gain. Keep it that way.
- Any future claim of the form "we reduced RMSE from 0.047 to 0.041" is not
  supportable against this reference. It would need a higher-resolution
  validation source — SAR-derived ice edge, or NCPOR ship observations.
- The **coastal cells are the worst case in the table** (0–100 % at sharp
  gradients), which is independent confirmation of the land-spillover artefact
  the project found and masks in `isih/ice_quality.py`. That work is not
  defensive over-engineering; it is addressing the single largest term in the
  reference product's own published error budget, at the single location that
  decides the voyage.

### 2.7 Where the sea-ice prediction stops being operationally useful

**Not where skill runs out — where the product runs out.** The binding constraint
is availability, not error growth:

| Product | Ceiling |
|---|---|
| CMEMS `GLO_ANALYSISFORECAST_PHY_001_024` | **D+9** (measured in repo) |
| SOIPS | 7 days (168 h) |
| IceNet (BAS / Alan Turing Institute, `https://icenet.ai/`) | daily forecasts to ~2 weeks; monthly means to 6 months |
| S2S / C3S ice-edge systems | 25–47 days *at basin scale, ice edge only* |

Nothing operational, obtainable and Antarctic gives corridor-scale SIC beyond
about **10 days**. Between day 10 and the seasonal range there is a genuine hole,
and the correct thing to display in it is **climatology with its interquartile
range**, explicitly labelled as climatology.

The useful-skill statement for this project, stated tightly:

> **Corridor SIC prediction is operationally useful to D+7, degraded but
> defensible to D+9, and unavailable beyond D+9. Inside D+7 the model beats
> persistence by 18–31 % on the project's own held-out test. Beyond D+9 the
> system shows climatology and says so.**

---

## 3. Iceberg trajectories

### 3.1 What Wagner, Dell & Eisenman (2017) actually validated — read the paper, not the abstract

**Source: Wagner, T. J. W., Dell, R. W., & Eisenman, I. (2017), "An Analytical
Model of Iceberg Drift", *Journal of Physical Oceanography* 47(7), 1605–1616,
doi:10.1175/JPO-D-16-0262.1.** Full PDF retrieved from the authors' site
(`https://eisenman.ucsd.edu/papers/Wagner-Dell-Eisenman-2017.pdf`) and read in
full this session.

★ **The Antarctic validation in WDE17 is explicitly qualitative. The paper
reports no position error, in any unit, at any lead time.** §3b, verbatim:

> *"We qualitatively validate the model against Antarctic tabular icebergs using
> the observed trajectories of large icebergs as catalogued in the Antarctic
> Iceberg Tracking Database."*

Forcing was **ECCO2 3-day-mean surface velocities and SST plus JRA-25 winds on a
1° grid**, interpolated to 0.25° and to 1-day steps, integrated with **forward
Euler at a 1-day time step**. Grounding is not resolved; velocities are zeroed
within one grid box of land. The paper's own quantitative results are about
*regimes*, not accuracy: the critical length **L\* ≡ 770 m** (reproduced by
`models/iceberg/drift.py`'s test suite), and the finding that water drag
dominates (R < 0.1) **for icebergs larger than L ≈ 12 km**.

**Implication for the repo.** `models/iceberg/drift.py` implements a model whose
Antarctic accuracy its own authors never quantified. That is not a criticism of
the choice — `docs/GAP_ANALYSIS.md` is right that it is the honest baseline and
the physics component every ML paper in this space still builds on — but it means
**the exclusion radius cannot be derived from the source paper.** It has to be
measured here, which is what `docs/backlog.md`'s open item already says.

### 3.2 What the literature does report for drift-error growth

There is no published, validated p50/p90 position-error curve for Antarctic
tabular icebergs at 24/48/72 h. What exists, in descending order of relevance:

**(a) Antarctic sea-ice drift, which is the closest measured proxy for a
current-and-wind-driven object in this region.**

- **SOIPS (Zhao et al. 2024, above):** drift magnitude MAE **2.14 → 2.22 cm s⁻¹**
  from 24 h to 168 h; direction MAE **2.13° → 2.81°**. Integrating a 2.2 cm s⁻¹
  speed error over 72 h gives a **≈ 5.7 km** along-track displacement error, and
  a 2.4° heading error on a 10.2 cm s⁻¹ drift over 72 h gives **≈ 1.1 km**
  cross-track. *Inference, labelled as such: this is a lower bound on iceberg
  error, because it is the error of an assimilating model for the medium it
  assimilates, not for an object drifting through it.*
- **Vos, M., Barnes, M., Biddle, L. C., Swart, S., Ramjukadh, C.-L., & Vichi, M.
  (2021), "Evaluating numerical and free-drift forecasts of sea ice drift during
  a Southern Ocean research expedition: An operational perspective", *Journal of
  Operational Oceanography*, doi:10.1080/1755876X.2021.1883293.** Buoys deployed
  in the Southern Ocean marginal ice zone on two cruises. The numerical forecast
  achieved 24-h trajectory position errors of **16.6 km in winter and 9.2 km in
  spring**. *The publisher returned HTTP 403 to every retrieval route attempted;
  these figures are taken from the abstract as surfaced in search and are marked
  **second-hand**. Settle by obtaining the PDF through an institutional
  subscription or by emailing the corresponding author.*
- A figure of **6.3 km at 24 h and 14 km at 72 h** for floe position error,
  attributed in the same context to Schweiger and Zhang, appears in search
  results. **UNVERIFIED — attribution not confirmed against the primary paper.**
  Do not quote it until the source is in hand.

**(b) A physically defensible bound from the current field itself.** WDE17
establishes that bergs larger than ≈ 12 km move essentially with the water
(R < 0.1). Every berg in the project's USNIC catalogue clears that threshold by
a wide margin — USNIC's own floor is 10 NM ≈ **18.5 km** on the long axis
(`https://usicecenter.gov/Products/AntarcIcebergs`). So a tracked giant is,
to first order, a Lagrangian particle in the CMEMS surface current field, and
CMEMS publishes exactly that error. QUID Table 6, **averaged separation distance
against undrogued PhOD drifters, computed with PARCELS**:

| Field | Global | Pacific south | Mid-latitudes |
|---|---|---|---|
| `cmems_mod_glo_phy_anfc_0.083deg_PT1H-m` (`uo`) | **42.7 km / 3 d** | 40.5 | 42.3 |
| `cmems_mod_glo_phy_anfc_merged-uv_PT1H-i` (`utotal`) | **39.9 km / 3 d** | 32.8 | 38.1 |

★ **≈ 40 km per 72 h is the order of magnitude of a current-following object's
position error in this model.** *Inference, labelled: it is a drifter-derived
number at 15 m depth in mostly mid-latitude water, not a berg-keel number in the
Southern Ocean.* The QUID says so itself — only **1.5 × 10³** Lagrangian
simulations fall in its Antarctic region, and *"Antarctic, Arctic and Guinea Gulf
region results shouldn't be given too much credit."*

**(c) The hybrid-ML literature, and a correction to what the repo currently
says.**

**Source: "IDRIFTNET: Physics-Driven Spatiotemporal Deep Learning for Iceberg
Drift Forecasting", arXiv:2507.00036.** Preprint, **not peer-reviewed**. Full PDF
read this session. Table 3, physics-only WDE17 baseline versus the hybrid, on
Antarctic giants A23A and B22A, geodesic:

| Dataset | Method | ADE (km) | FDE (km) |
|---|---|---|---|
| A23A | Physics-only (WDE17) | **147.10** | 117.54 |
| A23A | IDRIFTNET | 49.06 | 63.32 |
| B22A | Physics-only (WDE17) | **127.23** | 39.50 |
| B22A | IDRIFTNET | 22.87 | 10.87 |

★ **`docs/DECISIONS.md` ADR-025 cites "physics-only ADE of 127–147 km" as its
reason for capping projection at 72 h. Those numbers do not carry a lead time,
and the paper does not supply one.** Verified by reading the full text: §4.2
states only that the model uses "sliding windows consisting of five consecutive
timesteps" on daily USNIC positions; §4.3 describes an autoregressive rollout
"repeated iteratively across the entire prediction horizon"; and **the paper
never states the train/test split boundary or the number of rollout steps behind
ADE and FDE.** ADE is by construction an average over all steps of a rollout of
unstated length on a dataset spanning 2014 to February 2025. A 147 km ADE over a
multi-hundred-day autoregressive rollout is a different claim from a 147 km error
at 72 h, and only the second would justify a 72-hour cap.

The ADR's *conclusion* is very likely right. Its *stated reason* is not
load-bearing and a domain-literate reviewer who opens arXiv:2507.00036 will find
that in about four minutes. This should be corrected in the ADR text, and the
argument in §3.3 substituted.

### 3.3 Does the evidence support the 72 h cap? Yes — for a different reason

Assemble what is actually established:

1. Giant bergs are current-dominated (WDE17, R < 0.1 above L ≈ 12 km) —
   **established, from the primary source.**
2. A current-following particle in the CMEMS field separates from reality by
   **≈ 40 km per 72 h** (QUID Table 6) — **established for drifters, inferred for
   bergs.**
3. Southern Ocean drift forecasts show 24-h errors of order **9–17 km**
   (Vos et al. 2021) — **second-hand.**
4. Nothing in the literature reports a validated Antarctic tabular-berg position
   error at any lead — **established by exhaustion**: WDE17 is qualitative,
   IDRIFTNET reports lead-free aggregates, Lichey & Hellmer is a single
   multi-year trajectory, Wesche & Dierking is a 5-day search-area exercise, and
   every quantified operational verification (Turnbull et al. 2015 NW Greenland;
   Allison/Crocker ensemble on 216 Grand Banks tracks; Andersson et al. 2018) is
   **North Atlantic or Arctic, small bergs, and not transferable without saying
   so.**

★ **The honest justification for the 72 h cap is (4), not (1)–(3): 72 h is where
the evidence stops, not where the physics stops.** That is a *stronger* argument
than a fabricated error curve, and it is the one to give a judge. Beyond 72 h the
system would be drawing a circle whose radius nothing published can bound. ADR-025's
companion rule — show last-observed USNIC positions with their date and draw no
projection beyond 72 h — is exactly the right response to an unbounded quantity.

### 3.4 The Antarctic regime break that WDE17 does not model

★ **Source: Lichey, C., & Hellmer, H. H. (2001), "Modeling giant-iceberg drift
under the influence of sea ice in the Weddell Sea, Antarctica", *Journal of
Glaciology* 47(158), 452–460, doi:10.3189/172756501781832133.**

Giant berg C-7 was simulated across the Weddell Sea from day 355 of 1989 to day
54 of 1992. Applying classical wind and ocean forcing alone produced *significant
discrepancy* between modelled and observed velocities in the western Weddell Sea.
The realistic trajectory required **adding a sea-ice force representing the
ability of a dense sea-ice cover (≥ 90 % concentration) to lock in icebergs and
collect the momentum of the wind over an area much larger than the iceberg
proper**. C-7's mean observed velocity was 0.11 m s⁻¹.

**This is a hard boundary on `models/iceberg/drift.py`'s validity, and it lands
precisely on this project's decision point.** `docs/ISIH_RESULTS.md` measures
Bharati's own cell as closed to MV *Vasiliy Golovnin* on **23 of 31 December 2019
days at an 80 % concentration limit**, with the raw product reading 87–99 % on
most closed days. **At those concentrations a berg is not drifting in water — it
is embedded in the pack and moving with it**, and the WDE17 closed form, which
has no sea-ice term at all, is outside its validated regime in exactly the cells
that matter.

Two consequences, neither of which is currently in the repo:

- **Gate the drift model on concentration.** Above roughly 90 % SIC, project the
  berg with the *ice* drift field (`usi`/`vsi`, already harvested by
  `scripts/harvest_cmems.sh` and validated by SOIPS at 2.1–2.2 cm s⁻¹ MAE),
  not with the WDE17 closed form. Below it, WDE17 applies.
- This is a *cheaper* fix than it sounds: both fields are already in the archive.
  It belongs in `docs/backlog.md` alongside the existing melt/deterioration and
  time-integration items.

Supporting: **Wesche, C., & Dierking, W. (2016), "Estimating iceberg paths using
a wind-driven drift model", *Cold Regions Science and Technology*** — a
wind-driven model with an *added sea-ice component*, tested over **five days** on
ENVISAT wide-swath SAR scenes in the Weddell Sea against GPS buoys on bergs. The
authors' own summary of its utility, from the AWI presentation of the work
(`https://epic.awi.de/id/eprint/38909/1/Icebergs_Dierking.pdf`): the results are
*"useful for narrowing the search area for icebergs in satellite images"* — a
search-area tool, not a closest-point-of-approach tool. The same deck records
two conclusions worth carrying verbatim: *"tests with more complex models do not
reveal significantly better results"*, and *"largest problem of forecasts of
iceberg drift: in most cases input parameters cannot be provided with required
accuracy."*

### 3.5 p50 / p90 at each horizon — what can and cannot be stated

| Lead | p50 position error | p90 position error | Status |
|---|---|---|---|
| 24 h | — | — | **No Antarctic tabular-berg source exists.** Nearest proxies: 9.2–16.6 km (Southern Ocean *sea ice* buoys, Vos et al. 2021, second-hand); 10.1 ± 6.6 km training / 11.5 ± 7.3 km cross-validated for an ML berg model (Yulmetov 2021, POAC, **Arctic**, second-hand via search) |
| 48 h | — | — | Nothing published |
| 72 h | ≈ 40 km *(inferred from CMEMS Lagrangian separation, not measured for bergs)* | — | **The p90 does not exist in the literature.** |
| > 72 h | — | — | Unbounded by evidence — this is why the cap exists |

★ **The repo's own plan is the only route to these numbers.** `docs/backlog.md`
already specifies the measurement: **p90 leave-one-berg-out displacement error at
24/48/72 h** against the BYU Antarctic Iceberg Tracking Database (1978–2025, no
authentication). Until that runs, the exclusion radius is a design placeholder
and **must not be presented as a measured safety margin**. The distinction
between "we cap at 72 h because the evidence stops" and "we cap at 72 h because
we measured 40 km at p90" is exactly the distinction §48A.7 is asking for.

Two standing constraints, both already correct in the repo and both restated here
because they are horizon claims:

- **POLARIS §1.7.3 (IMO MSC.1/Circ.1519)** requires a recorded stand-off distance
  from glacial ice in the PWOM. The *regulatory* requirement exists; the
  *operational value* is unsourced (`docs/backlog.md`). A stand-off distance is
  not a forecast horizon and must not be derived from one.
- **USNIC's floor is 10 NM (18.5 km) on the long axis or 20 square NM.** No
  iceberg product at any horizon says anything about growlers. Stated in
  `catalogue.py`; keep it in the deck.

---

## 4. Weather

### 4.1 Where global NWP skill decays, and the threshold that defines "decays"

**Source: ECMWF Forecast User Guide, §6.2.2 "Anomaly Correlation Coefficient"**
(`https://confluence.ecmwf.int/display/FUG/Section+6.2.2+Anomaly+Correlation+Coefficient`):

> *"Where the ACC value falls below 0.6 it is considered that the positioning of
> synoptic scale features ceases to have value for forecasting purposes."*
> … *"Typically ACC falls to 0.6 at around day 8 or day 9 for ensemble control
> (CTRL), and at around day 10 for the ensemble mean (EM)."*

Corroborating for the American system this project uses: a NOAA coupled-GEFS
study (`https://repository.library.noaa.gov/view/noaa/55248/noaa_55248_DS1.pdf`)
reports that the 500 hPa ensemble-mean anomaly correlation *"provides a useful
skillful forecast of nearly 10 days (60 % AC score threshold)"* for the
**Northern Hemisphere** extratropics (20–80 °N), and states that the Southern
Hemisphere (20–80 °S) coupled run *"has a most useful skillful forecast (60 % AC
score threshold)"* — but **the SH number itself appears only in that paper's
Figure 1b and is not stated in the text. UNVERIFIED numerically.** Settle by
reading the figure, or by pulling NCEP EMC's own operational verification series
(`https://www.emc.ncep.noaa.gov/gmb/STATS/`, which publishes NH and SH 500 hPa
anomaly-correlation time series since 1996).

**Working statement, honestly bounded:** synoptic-scale atmospheric skill in the
Southern Hemisphere extratropics runs out at **day 8–10**. The historic NH/SH gap
has narrowed substantially as satellite assimilation improved (ECMWF: *"the skill
of forecasts in areas with few in-situ observations, such as the southern
hemisphere, increased sharply"*), but this project should not assert SH parity
with NH without the verification figures in hand.

### 4.2 Wind — and a bias that points the wrong way, twice

`docs/DATASET.md` verifies **NOAA GFS 0.25°** as live, no-auth, 4 cycles/day,
384 h. Re-confirmed this session: `gfs.20260907` present on NOMADS; at **12:16
UTC** the 00z and 06z cycles each carried **209** `pgrb2.0p25` files and the 12z
directory was empty. **Measured upper bound on availability latency: the 06z
cycle was complete within 6 h 16 min of cycle time.** (A tighter bound needs
polling; NCEP's normal figure is 3.5–5.5 h. Not measured here.)

★ **Direction of the wind error matters more than its magnitude, and two
independent products agree on it.**

- **Campos, R. M., Abdolali, A., Alves, J.-H., et al. (2024), "Development and
  Validation of NOAA's 20-Year Global Wave Ensemble Reforecast", *Weather and
  Forecasting* 39(11), 1651–…, doi:10.1175/WAF-D-24-0043.1.** Global altimeter
  validation, 34.6 million deep-water matchups: *"the bias of U10 is negative
  (model underestimation) across great parts of the domain, **especially in the
  Southern Ocean**, where the altimeter winds are more intense than the GEFSv12
  reforecast."*
- `docs/NAVIGATION_RESEARCH.md` §7.5 already records ERA5 at mean bias
  −0.51 m s⁻¹ against ASCAT for summer Antarctic coastal easterlies, but
  **−3.89 m s⁻¹ above 20 m s⁻¹**.

**Both the reanalysis this project trains on and the forecast ensemble it would
route on under-predict strong Southern Ocean wind.** That is the same conclusion
NAVIGATION_RESEARCH reached from a different source, and it is safety-critical
in the same direction: the system will under-warn on exactly the winds that beset
ships. Any wind-driven hazard layer must bias-correct or say so — and now it must
say so about two products, not one.

### 4.3 Sea state — GFS-Wave is now verified live, closing an open item

★ **This closes the `docs/DATASET.md` gap.** `DATASET.md` §5 lists only ERA5 (a
reanalysis) for waves, so the project has had **no verified operational wave
forecast**. It does now.

**Verified live this session, 2026-09-07, no authentication:**
`https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/gfs.20260906/00/wave/gridded/`
returned **209 files** named `gfswave.t00z.global.0p25.f000 … f384.grib2`, plus a
separate `gfswave.t00z.gsouth.0p25.*` series. The GRIB index for `f072` lists:

```
WIND  WDIR  UGRD  VGRD  HTSGW  PERPW  DIRPW  WVHGT
SWELL(1,2,3)  WVPER  SWPER(1,2,3)  WVDIR  SWDIR(1,2,3)
```

`HTSGW` is significant wave height — the field `meshiphi`'s `swh` accessibility
cutoff needs and PolarRoute's dead `wave_resistance()` would need
(`docs/NAVIGATION_RESEARCH.md` §2, Gap 1).

**Source for the grid geometry: NCEP/EMC, "Operational global wave model:
GFS-Wave"** (`https://polar.ncep.noaa.gov/waves/Model_Description.pdf`, downloaded
and read):

| Grid | Range | Resolution | Role |
|---|---|---|---|
| `global.0p16` | −15 : 52.5 | 16 km | computational |
| `arctic.9km` | 50 N : 90 N | 9 km | computational |
| **`gsouth.0p25`** | **−10.5 : −79.5** | **25 km** | **computational** |
| `global.0p25` | −90 : 90 | 25 km | post-processed |

Hourly to 120 h, 3-hourly to 384 h, 4 cycles per day, unified with the GFS run.
**The `gsouth` computational grid spans −10.5° to −79.5°, which covers the entire
Cape Town (33.9 °S) → Bharati (69.4 °S) corridor.** This is the native grid, not
an interpolation from a northern domain.

**Skill, from Campos et al. 2024** — significant wave height against **98 buoys**
(NDBC + Copernicus, deep water, ≥ 80 m depth, ≥ 50 km offshore):

| Lead | Bias (m) | RMSE (m) | Scatter index | Correlation |
|---|---|---|---|---|
| Day 1 (ens. mean) | 0.03 | **0.37** | 0.15 | **0.95** |
| Week 1 (ens. mean) | 0.05 | 0.57 | 0.23 | 0.88 |
| Week 2 (ens. mean) | 0.10 | 0.87 | 0.36 | 0.70 |
| Week 3 (ens. mean) | 0.10 | 0.94 | 0.39 | 0.62 |
| Week 5 (ens. mean) | 0.11 | 0.96 | 0.40 | 0.60 |

Against altimeters globally (34.6 M matchups): correlation starts at **0.96** and
stays **above 0.9 on day 5**; **normalised RMSE stays below 20 % within the first
5 forecast days**. The paper's own summary: *"the degradation of predictability
and the increase in scatter errors predominantly occur in the forecast lead time
between days 4 and 10"*, and after day 10 correlation falls below 0.70.

★ **Two caveats, and the second is the paper's own.** First, the buoy tables are
NDBC/Copernicus — overwhelmingly Northern Hemisphere. Second, verbatim from
Campos et al.: *"The global maps show elevated errors in both U10 and Hs within
polar regions near the Arctic and the Antarctic. This might be associated with
model limitations in the wind–wave–ice interaction or associated with constraints
in altimeter measurements near ice-covered areas. At present, no definitive
conclusions can be drawn, emphasizing the need for dedicated validation specific
to these regions."*

**So: GFS-Wave is obtainable, covers the corridor natively, and runs to 384 h —
but its skill is only validated to ~day 5 globally and NOAA explicitly declines
to characterise it near the ice. The system may route on Hs to day 5, display it
to day 7, and must not present anything past day 10.** That 384 h number is a
product length, not a skill horizon, and conflating the two is the exact error
§48A.7 forbids.

An alternative with published Antarctic coverage: CMEMS
`GLOBAL_ANALYSISFORECAST_WAV_001_027` — **10-day forecast, updated twice daily
(00:00 and 12:00 UTC), 0.083°, hourly, latitude −80° to 90°**, with wind-wave and
swell partitions and Stokes drift
(`https://data.marine.copernicus.eu/product/GLOBAL_ANALYSISFORECAST_WAV_001_027/description`).
Same account as the SIC harvest. Worth evaluating against GFS-Wave before either
is wired in.

### 4.4 Visibility — the real gap, and it is not small

**No global NWP product forecasts Antarctic coastal visibility usefully.**
Visibility is not in the GFS-Wave inventory. `docs/NAVIGATION_RESEARCH.md` §7.5
already establishes why it matters: the Australian Antarctic Division defines an
Antarctic blizzard as gale force or stronger for at least one hour, temperature
< 0 °C, **visibility ≤ 100 m**; Maitri sees ~21 blizzards a year affecting the
station on 45 days, mean duration 25 h, longest 168 h.

**Blowing snow degrades the growler lookout at precisely the moment radar is also
degraded by sea state, and no product in this project's stack predicts it.**

The candidate is **AMPS** (Antarctic Mesoscale Prediction System, polar WRF):
domains at 24 / 8 / 2.67 / 0.89 km, **120 h outer domain, 39 h nests**, free —
already noted in NAVIGATION_RESEARCH §7.5 with the caveat that *"whether any
sub-8 km nest covers Dronning Maud Land or Prydz Bay is unconfirmed — the
domain-map pages 404'd."* **That remains UNVERIFIED and is now the single largest
weather gap in the horizon table.** Settle by requesting the current AMPS domain
configuration from UCAR/MMM or NCAR's AMPS team, or by fetching a live AMPS GRIB
and reading its grid definition.

Until then the honest statement is: **visibility is a nowcast-only quantity in
this system, sourced from observation and station reports, with no forecast
horizon at all.**

---

## 5. Ocean

All from CMEMS-GLO-QUID-001-024 Issue 1.3 and CMEMS-GLO-PUM-001-024 Issue 2.4,
same product the SIC harvest already uses. **Horizon and cadence are identical to
§2.1: D+0 to D+9, updated daily, delivered by 12:00 UTC.** One harvest, one
horizon, four physical fields — which is an architectural convenience worth
stating in the deck.

**Sea surface temperature** (QUID Table 3, global, 2019, vs SST TAC):

| | Mean bias | RMSD |
|---|---|---|
| Hindcast | −0.06 °C | **0.4 °C** |
| **Forecast day 3** | 0.1 °C | **0.6 °C** |

A 50 % RMSD growth from analysis to day 3. SST enters this project only through
iceberg melt/deterioration (Bigg 1997 / Martin & Adcroft 2010, still a backlog
item), where 0.6 °C is comfortably adequate — melt rates are not the binding
uncertainty in a 72-hour projection.

**Surface currents.** QUID §IV.6.1: against undrogued drifters and ARGO surface
trajectories, correlation exceeds 60 % but **the regression slope is only ≈ 0.5 —
the model underestimates current speed**, improving to ≈ 70 % for velocities
around 50 cm s⁻¹. Median direction difference 3°, *"the angle bias mainly concerns
the southern hemisphere"*, mostly at low speeds.

Lagrangian separation (QUID Table 6, PARCELS, against the PhOD hourly drifter
database) is reproduced in §3.2(b): **42.7 km / 3 d** for `uo`, **39.9 km / 3 d**
for the merged `utotal`.

★ **Three warnings, all from the QUID itself:**

1. The Antarctic Lagrangian sample is **1.5 × 10³** simulations, and the document
   states plainly that *"Antarctic, Arctic and Guinea Gulf region results
   shouldn't be given too much credit."* **The 40 km / 3 d figure is a global
   number applied to the Southern Ocean by inference, not a Southern Ocean
   measurement.**
2. Latitudes above 60° are *"practically not observed"* by the validation drifter
   array. Below 60 °S — which is more than half our corridor and all of the
   decision-relevant part — CMEMS surface currents are effectively **unvalidated
   against in-situ data**.
3. The systematic slope of ≈ 0.5 means advection distances computed from this
   field are **biased short**. For iceberg projection that is a *non-conservative*
   error: a berg projected with an under-strength current lands closer to its
   last-observed position than it really will. The exclusion polygon must not
   inherit that optimism.

**Useful horizon for ocean fields:** currents are usable for advection to **72 h**
at ≈ 40 km uncertainty (inferred, global); SST to the full D+9 for melt purposes.
Beyond 72 h no Antarctic-relevant current validation exists at any lead.

---

## 6. The operational synthesis — what the system can and cannot see at departure

This is the part that decides what the demo may claim.

### 6.1 The voyage, measured

From `docs/ISIH_RESULTS.md`: Cape Town (33.9 °S, 18.4 °E) → Bharati (69.4 °S,
76.2 °E), **5,813 km**, PolarRoute 1.1.11 on real NSIDC ice. STATIC arm: 8.58 d
planned, **8.61 d actual**. DAILY arm: 9.00 d with 9.6 h blocked.

And the caveat the project states about its own number, which is the hinge of
everything below: **8.58 days is ideal steaming time.** No sea-state penalty
(PolarRoute's `wave_resistance()` is defined and never called), no station time,
no weather holds, no bathymetry — and it assumes the vessel sustains **16.4 kn
service speed**, where the AIS-observed average across all conditions is
**8.6 kn**.

### 6.2 Distance covered versus forecast reach

| | at 16.4 kn service (729 km/d) | at 8.6 kn AIS average (382 km/d) |
|---|---|---|
| D+3 (short-range ceiling) | 2,187 km — **38 %** of route | 1,147 km — **20 %** |
| D+5 (wave-skill ceiling) | 3,645 km — **63 %** | 1,912 km — **33 %** |
| D+7 (SIC-skill ceiling) | 5,102 km — **88 %** | 2,676 km — **46 %** |
| **D+9 (product ceiling)** | 6,560 km — **whole route** | **3,441 km — 59 %** |
| Beyond D+9 | nothing | **2,372 km remaining — 41 % of the voyage, unforecast** |

At the AIS-observed average speed the transit is **≈ 15.2 days**. The arrival day
therefore sits **roughly six days beyond the last forecast step available at
departure**.

★ **This is the headline of the whole file. At departure from Cape Town, this
system cannot see the arrival at Bharati.** Anything it displays about the
destination on arrival day is climatology wearing a forecast's clothes.

### 6.3 The project's own data already demonstrates this

`isih/destination_window.py`'s docstring records the case directly:

> *"On 1 December 2019 the ice at Bharati looks passable, so a planner commits to
> it. Nine days later the same cell is 96 % ice and closed to this vessel."*

**Nine days is exactly the edge of the harvested horizon.** The closure the
project found is the first event a departure-day forecast structurally cannot
resolve. It is not a routing failure and not a model failure — it is an
information horizon, and naming it as such is a stronger result than pretending
to have predicted it.

This also explains the null result the project honestly reports in
`docs/ISIH_RESULTS.md` §3, where the STATIC arm was not punished (regret 0.03
days) and DAILY re-planning was *slower*. Of course it was: **the tier with the
most forecast skill covers the leg with the least to decide.** About 5,800 km of
the 5,813 km route carries mean 6 % ice. There is nothing to optimise in the
open-ocean crossing, so fresh information buys nothing there. The entire decision
is compressed into the final approach — which is the part that falls outside the
horizon at departure.

### 6.4 Which decision belongs to which tier

| Decision | Taken when | Tier | Evidence it can rest on |
|---|---|---|---|
| Sail / don't sail; departure date | weeks–months out | **strategic / long-range** | Climatology and the historical record only. `docs/ISIH_RESULTS.md`: Bharati's cell closed **74.2 %** of December 2019 days at an 80 % limit while the approach 100 km north was open **31/31**. That is a climatological statement and it is the right kind of claim at this tier. |
| Great-circle vs ice-avoiding track across the Southern Ocean | at departure | **medium-range** | GFS wind to D+8–10, GFS-Wave Hs to D+5, CMEMS currents/SIC to D+9. Genuine forecast skill, but **little to decide** — 6 % mean ice. |
| Speed / routing for weather avoidance in the Forties and Fifties | rolling, 1–5 days ahead | **short to medium** | Hs normalised RMSE < 20 % to day 5; wind ACC useful to day 8–10; both **under-predicting strong SH wind** (§4.2). |
| **Approach or hold at the fast-ice edge** | **3–7 days before arrival, from near the ice** | **short to medium** | SOIPS-class SIC skill: RMSE 0.16 at 72 h, 0.19 at 168 h. Ice drift MAE 2.1 cm s⁻¹. This is where a forecast actually earns its keep. |
| **Timing the open-water band; go / no-go on the last 100 km** | **24–72 h out** | **short-range** | SOIPS's own Prydz Bay case at Zhongshan (5 km from Bharati) uses **sea ice convergence rate at 24, 48 and 72 h** for precisely this. |
| Iceberg avoidance / CPA | ≤ 72 h | **short-range** | WDE17 projection capped at 72 h; beyond that, last-observed USNIC positions with their date and no projection (ADR-025). |
| Cargo by helicopter and barge vs alongside | 24–48 h | **short-range** | Wind, visibility and SIC. **Visibility has no forecast at all in this stack (§4.4)** — the weakest link in the chain. |

### 6.5 What the system may and may not claim — put this on a slide

**May claim at departure:**
- The planned track across the Southern Ocean, with wind and sea-state exposure
  to D+5 (routed) and D+9 (displayed with growing uncertainty).
- A **climatological** probability that Bharati is accessible in the arrival
  window, with the measured December-2019 figure of 74 % closed as the anchor and
  the interquartile range shown.
- The ETA, with the honest caveat that 8.6 days is ideal steaming and the AIS
  average implies roughly double.

**May NOT claim at departure:**
- Any statement about ice at Bharati on arrival day. Not "will be open", not
  "will be closed", not a percentage. There is no forecast there.
- Any iceberg position beyond 72 h.
- Any wave or wind field beyond day 10, notwithstanding that GFS-Wave publishes
  to 384 h.

**Must do en route:** re-take the destination decision when the ship is inside
D+7 of arrival, and again inside D+3, from the ship's actual position — and show
the operator that it has done so, with both the old and new answer. §48A.23's
provenance requirement and this horizon discipline are the same requirement seen
from two sides: the reason to keep the decision trail is that **the decision
legitimately changes when it moves into a tier where evidence exists.**

---

## 7. The horizon table

Numeric bounds, their source, and what the system is permitted to assert inside
each tier. WMO tier names are used verbatim where they apply; the fifth row is
not a WMO tier and is labelled accordingly.

| Tier | Bounds | Bound comes from | Sea ice | Icebergs | Weather | Ocean | **Permitted assertion** |
|---|---|---|---|---|---|---|---|
| **Nowcast** | **0–2 h**, extended to **now − observation latency** in practice | WMO-No. 485 App. 1.1; latencies: OSI SAF OSI-401-b **5 h**; CMEMS SEAICE L4 NRT **daily 05:00 UTC**, 62.5 km, drift vectors spanning **2 days** | Observed SIC, QA-masked (`isih/ice_quality.py`). Reference accuracy **~10 %** mid-winter, **0–100 % at coast and ice edge** (NSIDC C-ATBD Table 10) | Last-observed USNIC position, **dated**. Floor **10 NM / 18.5 km** long axis | Observed wind, pressure. **Visibility: observation only, no forecast** | Analysis fields | **"This is what was observed, at this time, with this uncertainty."** Never call it a forecast. Never call a 0.0 coastal cell open water. |
| **Short-range** | **12–72 h** | WMO-No. 485 App. 1.1 | SOIPS Antarctic RMSE **0.15 → 0.16**; CMEMS ACC day-3 RMSD **10 %**; project's own **0.0465 → 0.0720**, +18.5 → +24.9 % over persistence | **WDE17 projection valid here and only here.** Radius = measured p90 LOO error — **not yet measured** | Hs RMSE **0.37 m** day 1; ACC ≫ 0.6 | Currents to **≈ 40 km / 3 d** separation (inferred) | **Full operational confidence.** Go/no-go on the last 100 km. Convergence-rate timing of the open-water band. Iceberg CPA. This is the tier that changes a route. |
| **Medium-range** | **72–240 h**, product-limited to **D+9** | WMO-No. 485 App. 1.1; **D+9 measured in this repo**, 2026-09-07 | SOIPS **0.17 (120 h) → 0.19 (168 h)**; project's own **0.0938 → 0.0968**, +22.1 → +30.6 % over persistence | **No projection.** Last-observed positions with dates | Hs normalised RMSE **< 20 % to day 5** (altimeter, global); ACC 0.6 at **day 8–9 CTRL / day 10 EM** | SST day-3 RMSD **0.6 °C**; currents unvalidated below 60 °S | **Planning confidence with stated uncertainty.** Track selection, weather avoidance, approach-versus-hold. Show the ensemble spread or the conformal band, never a single line. |
| **Extended-range** | **10–30 days** | WMO-No. 485 App. 1.1 | **Nothing obtainable at corridor scale.** Basin-scale ice edge: ECMWF ≈ 38 d, UKMO ≈ 25 d vs climatology (Gao et al. 2024) — and Antarctic skill is **30 % below Arctic** (Zampieri et al. 2019), worse in **East** Antarctica, which is us | Nothing | Nothing deterministic | Nothing | **Climatology only, labelled climatology.** The correct display is a distribution, not a field. |
| **Long-range planning** *(not a WMO tier — Wagner et al. 2020 "strategic")* | **30 days – seasons** | Wagner et al. 2020, *Polar Geography* 43(2–3) | Historical record and ice atlas. Anchor number: **Bharati's cell closed 74.2 % of December 2019 days at an 80 % limit; the approach 100 km north open 31/31** | Climatological berg density | Blizzard climatology: Maitri **~21/yr, 45 station-days, peak August** (NAVIGATION_RESEARCH §7.5) | Seasonal SST/ice-edge climatology | **Season and window selection. Frequency statements, never a date.** "Historically open on N of M days", never "will be open on the 14th". |

**Every field the UI renders carries a tier badge, a valid time, a lead time and
a forecast age. A field with no tier badge is a bug, not a styling omission.**

---

## 8. What this implies for the build

Consequences that follow directly from the above and belong in `docs/backlog.md`
as one-liners:

1. **Say "D+9", not "10-day".** The archive holds ten steps of which one is the
   analysis day. Verified in repo.
2. ★ **The harvest box does not match the training corridor.**
   `scripts/harvest_cmems.sh` sets `MIN_LAT=-78 MAX_LAT=-55 MIN_LON=0
   MAX_LON=80`; `docs/ISIH_RESULTS.md` states the corridor as **48–80 °S,
   5 °W–85 °E**. The harvest is clipped on all four sides — it is missing
   48–55 °S (the northern ice-edge approach), 78–80 °S, 5 °W–0 °E and
   80–85 °E. Since this archive **cannot be back-filled**, every day the boxes
   disagree is a permanent hole in the Stage B training set at the corridor
   margins. Reconcile the two before the next harvest, not after.
3. **ADR-025's stated justification is wrong even though its conclusion is
   sound.** The 127–147 km ADE from arXiv:2507.00036 has no attributable lead
   time; the paper does not state the rollout length. Replace with the §3.3
   argument: 72 h is where the published evidence stops.
4. **Gate the iceberg drift model on sea-ice concentration.** Above ≈ 90 % SIC,
   Lichey & Hellmer (2001) show the berg locks into the pack; WDE17 has no
   sea-ice term. Use the already-harvested `usi`/`vsi` there. This is the regime
   the last 100 km at Bharati is actually in.
5. **GFS-Wave is verified live and covers the corridor natively** on the
   `gsouth.0p25` grid (−10.5 to −79.5, 25 km), 384 h, 4 cycles/day, `HTSGW`
   present. `docs/DATASET.md` §5 should be updated. Route on it to day 5, display
   to day 7, never past day 10.
6. **Two independent products under-predict strong Southern Ocean wind** — ERA5
   (−3.89 m s⁻¹ above 20 m s⁻¹) and GEFSv12 (negative U10 bias, "especially in
   the Southern Ocean"). A bias correction or an explicit disclaimer is now
   mandatory, not optional.
7. **CMEMS underestimates Antarctic SIC in austral summer** — the resupply
   season, and the unsafe direction. Measure the corrected product's *signed*
   bias, not only its RMSE.
8. **Quote the relative gain over persistence, not the absolute RMSE.** The
   absolute number is inside the reference product's own stated uncertainty.
9. **Measure the iceberg p90 leave-one-berg-out error at 24/48/72 h** against the
   BYU database. Until then the exclusion radius is a placeholder and must be
   labelled one.
10. **Visibility has no forecast in this stack.** Confirm AMPS nest coverage of
   Prydz Bay / Dronning Maud Land or state the gap in the deck.
11. **Re-plan gates belong at D+7 and D+3 before arrival**, from the ship's real
    position, with both answers shown.

---

## 9. Explicit uncertainties in this file

Carried here rather than smoothed over, because they bound what may be claimed.

- **Vos et al. (2021) 24-h errors of 16.6 km (winter) / 9.2 km (spring)** are
  **second-hand** — taken from the abstract as surfaced in search; the publisher
  returned HTTP 403 to every retrieval attempt. *Settles by:* institutional
  access to *Journal of Operational Oceanography*, or emailing the corresponding
  author (M. Vichi, University of Cape Town — geographically convenient for this
  project).
- **The 6.3 km / 14 km floe-position figures at 24 h / 72 h** attributed to
  Schweiger and Zhang are **UNVERIFIED** — the attribution has not been checked
  against a primary paper. Do not quote until it has.
- **Yulmetov (2021, POAC) ML iceberg drift errors of 10.1 ± 6.6 km (training) and
  11.5 ± 7.3 km (cross-validated) at 24 h** are **second-hand** and **Arctic**.
  Not transferable to Antarctic tabular bergs without stating so.
- **Southern Hemisphere 500 hPa anomaly-correlation skill in days is
  UNVERIFIED numerically.** The NOAA coupled-GEFS study states the NH figure
  (≈ 10 days at 60 % AC) in text but leaves the SH figure in Figure 1b.
  *Settles by:* NCEP EMC's published NH/SH verification series at
  `https://www.emc.ncep.noaa.gov/gmb/STATS/`.
- **No Southern Ocean-specific wave verification by forecast lead was found.**
  Campos et al. explicitly decline to characterise polar Hs and U10 error.
  *Settles by:* the WMO Lead Centre for Wave Forecast Verification seasonal
  intercomparison reports (Part I significant wave height, Part III 10 m wind
  speed, ~61 pp each) at `https://confluence.ecmwf.int/spaces/WLW`, which are
  region-resolved.
- **AMPS nest coverage of Prydz Bay / Dronning Maud Land remains unconfirmed**,
  carried forward from `docs/NAVIGATION_RESEARCH.md` §7.7 and unresolved here.
- **The ≈ 40 km / 72 h iceberg position error is an INFERENCE**, built from
  WDE17's current-dominance result plus CMEMS's drifter-derived Lagrangian
  separation. It is a global, 15 m-depth, mid-latitude drifter number applied to
  a Southern Ocean iceberg keel. It is the best-grounded number available and it
  is **not a measurement of iceberg error**. Label it as an inference everywhere
  it appears.
- **NSIDC G02202 final-CDR latency is UNVERIFIED.** Search returned both
  "approximately 1-week latency" and "final CDR updates occurring every three to
  six months", which cannot both describe the same thing. The verified statement
  is that G10016 (NRT CDR, 25 km) exists to fill that gap and holds the most
  recent three months. *Settles by:* the G10016 and G02202 user guides on
  nsidc.org.
- **GFS availability latency is bounded, not measured.** The 06z cycle was
  complete on NOMADS by 12:16 UTC on 2026-09-07 — an upper bound of 6 h 16 min,
  not the actual figure. *Settles by:* polling the cycle directory at intervals
  through one run.
- **Palerme et al. (2024) report lead-by-lead RMSE only in figures**, not as
  tabulated numbers. The 19–33 % improvement band over persistence is stated in
  text and is what is used here; per-lead values are not available without
  digitising Figure 4.
- **SOIPS and this project's model are not directly comparable** — different
  reference product, domain, period, and a reanalysis versus a forecast
  background. Only the *shape* of the two error curves is compared, and that
  comparison is qualitative.
