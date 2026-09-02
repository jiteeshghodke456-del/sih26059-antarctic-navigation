# Presentation — 4 September 2026

Slide-ready points for the internal review. Every number here traces to a file
in this repo or a cited source. Nothing is rounded up, and the weak results are
included on purpose.

**The posture:** we are not claiming a finished product. We are claiming that we
understand this problem better than a team that has been building UI, and that
we have evidence for every sentence.

---

## Slide 1 — The problem is not the ocean. It's the last 100 km.

India resupplies Bharati and Maitri by sea each austral summer. The obvious
framing — "find the best route across the Southern Ocean" — is the wrong one.

**Measured, December 2019, MV Vasiliy Golovnin at an 80% ice limit:**

| | Days reachable | Days closed |
|---|---|---|
| Approach point, 100 km north of Bharati | **31 / 31** | 0 |
| Bharati station cell | 8 / 31 | **23 / 31 (74%)** |

> **The ship can always reach the approach. It usually cannot reach the station.**

This matches how resupply actually works — the vessel holds at the fast-ice edge
and moves cargo by helicopter and landing barge, which is why Golovnin carries
both. So the real decision-support question is:

> *When should we arrive, will the final approach be open when we get there, how
> long will it stay open, and if it is shut — do we wait or switch to air and
> barge operations?*

That is a **forecasting** question at a lead time of days. Which is exactly the
horizon our model targets.

*Source: `isih/destination_window.py`, `isih/figures/destination_window.json`.*

### This has already happened to an Indian expedition

**MV Magdalena Oldendorff**, chartered as support ship for the **20th Indian
Antarctic Expedition**, was **beset on 11 June 2002** near Novolazarevskaya on
her second voyage to Maitri. SA Agulhas lifted out 90 people by helicopter. The
Argentine icebreaker *Almirante Irízar* **failed to free her**. She overwintered
and self-released in late November — roughly **five and a half months beset**.

She was a ULA-class hull. **Golovnin is also ULA-class.**

And besetting is not only a winter problem: **MV Akademik Shokalskiy was beset on
25 December 2013** — peak austral summer. *Xue Long* became beset attempting the
rescue. What eventually freed her was **a change in wind direction**, not an
icebreaker.

> **The line:** "This is not a hypothetical optimisation problem. An Indian
> expedition's support ship spent five months stuck in the ice we are modelling."

*Caveat for the deck: source dates for the Oldendorff conflict and no primary
ATCM/COMNAP document has been located. Say "reported" until that is settled.*

---

## Slide 2 — We found that the ice data itself lies, at the worst possible place

Every ice service — IcySea, PolarView, national ice charts — sits on the same
passive-microwave retrievals. We audited ours.

The NOAA/NSIDC climate data record applies a **land-spillover filter** to coastal
cells whose 25 km microwave footprint overlaps land. When it fires it writes
**`0.0`** — not a missing value. Zero is inside `valid_range`, so every naive
reader accepts it as **open water**.

**How we caught it:** physically, not statistically. A block of exact zeros with
*zero gradient* sitting flush against cells reading 59–64%. Sea ice does not do
that. The file's own `cdr_seaice_conc_qa_flag` bit 4 confirmed it.

**How widespread — all 1096 days, 2018–2020:**

| | |
|---|---|
| Days the filter fires | **100%** |
| Cells suppressed per day | mean **118**, max 488 |
| Days with suspect cells in the Bharati 200 km approach box | **43.2%** |
| Worst single-day sensor outage | 59,350 cells |

**Why it matters operationally:** of the 8 December days Bharati appeared
reachable, **4 were days the raw product reported 0.0% ice.** A router reading
raw data plans into a station that is actually 80–95% ice.

**What we did:** `isih/ice_quality.py` reads the QA flag and treats those cells
as unknown. We then checked the fix moves risk the safe way — mean ice in the
Bharati box rises 46.8% → 54.6%, i.e. the router becomes **more** conservative.

> **The line:** "We did not just consume the data. We audited it, found it
> failing at the one place a ship most needs it, and fixed it in the safe
> direction."

---

## Slide 3 — The AI: it beats the baseline that actually matters

The model corrects an existing physics forecast rather than predicting ice from
scratch:

```
corrected SIC = clip( CMEMS forecast + model's predicted correction, 0, 1 )
```

The output head is zero-initialised, so an untrained model reproduces the
forecast exactly. **The floor is the physics model's skill, not zero.**

**Test-set RMSE, scored exactly once:**

| Lead | Our model | Persistence | Gain |
|---|---|---|---|
| 1 day | **0.0465** | 0.0570 | +18.5% |
| 3 days | **0.0720** | 0.0958 | +24.9% |
| 5 days | **0.0938** | 0.1204 | +22.1% |
| 7 days | **0.0968** | 0.1395 | **+30.6%** |

Two things make this trustworthy:

1. **Persistence is the honest baseline in sea-ice forecasting, and we beat it.**
   Most published work compares against climatology. In SIPN South — 22 groups,
   3000+ forecasts — only **51% of predictions beat plain climatology**, and the
   authors state they did *not* implement persistence benchmarks at all.
2. **Split by time, never randomly.** Sea ice barely changes overnight; a random
   split puts adjacent days in train and test and produces a spectacular,
   meaningless score. This is the most common way results in this field are
   inflated.

**The advantage grows with lead time** — our error rises 2.1× from day 1 to day
7 while persistence rises 2.5×. The further ahead you must plan, the more the
model is worth.

---

## Slide 4 — What we are honest about (put this ON a slide)

This is the slide that separates us. Judges have seen teams that only present
wins.

1. **We ran an experiment that did not favour us.** We replaced the old
   straight-line route comparison — a strawman, since no master sails a straight
   line into pack ice — with the same router given older ice. On the departure
   date tested, planning on stale ice cost **0.03 days**, and daily re-planning
   was *slower*. One departure date is one sample. We report the null result and
   the multi-date sweep is the next run.

2. **We withdrew our own headline number.** The previously reported 17.4-day
   transit was computed with the ship at roughly half its real speed (beam and
   max speed were both wrong). Corrected to 8.6 days — and that is *steaming
   time only*, with no weather, no bathymetry and no station operations.

3. **We found dead code in the library we depend on.** PolarRoute defines
   `wave_resistance()` and never calls it, so sea state imposes no speed or fuel
   penalty anywhere — including the Roaring Forties. Verified by reading the
   installed source.

4. **We do not quote a fuel figure.** The fuel polynomial is calibrated to a
   different hull.

5. **Our ice limit of 80% is invented.** The real framework is IMO POLARIS
   (MSC.1/Circ.1519), which indexes risk by ice *type*, not concentration — so a
   compliant system needs a thickness forecast, which is why production adds a
   thickness output channel.

> **The line:** "Every number on the previous slides has a caveat we wrote down
> before you asked."

---

## Slide 5 — How a 7-day forecast supports a 17-day voyage

The obvious objection: *you cannot forecast day 14.* Correct. We do not try.

**A voyage is not one decision.** We stratify the horizon and say what each band
is for:

| Band | Lead | Output |
|---|---|---|
| Committed | 0–2 days | A track the bridge can steer |
| Steering | 3–7 days | A **corridor**, with flagged decision points |
| Strategic | 8+ days | Climatology and ice-edge position, drawn as a fan and labelled *no forecast skill claimed* |

Three design commitments follow, and they answer "what if a model is wrong":

- **We never re-rank routes on raw cost.** A change is proposed only when it
  beats the current plan by more than the width of our own calibrated
  uncertainty. **On most days the correct output is "hold course"** — a system
  that flags 2 genuine decision points in 14 days is more trustworthy than one
  that redraws the line every morning.
- **Failure degrades to physics, not to nothing.** Corrected forecast → raw
  forecast → persistence → climatology. The system announces which rung it is on.
- **We verify ourselves daily.** Yesterday's 1-day forecast is checked against
  today's observation — a free skill measurement available every day at sea. Bad
  verification widens the corridor and moves decisions earlier.

> **The line:** "We do not claim the model is always right. We claim the system
> knows when it is wrong, and says so before it matters."

*Full design: `docs/DECISION_ARCHITECTURE.md`.*

---

## Slide 6 — Where we are, and what is next

**Done and verified**
- Real data pipeline: 1096 NSIDC daily files, 0 failed; GLORYS12 paired
- Bias-correction U-Net trained, beats persistence at every horizon
- Real routing computed with PolarRoute on real satellite ice
- Ice-data QC layer, with the artifact measured across the full archive
- Vessel specification verified and corrected

**Honest gaps, in priority order**
1. **Iceberg trajectory — not started.** It is one of the three pillars in the
   problem statement title. This is our largest gap and we are naming it.
2. Multi-date route-regret sweep — one sample proves nothing
3. Retrain with QA masking — the model was fitted on the fake coastal zeros
4. GEBCO bathymetry — no depth constraint on any route today
5. Ensemble + conformal calibration — turns disagreement into a safety margin
6. POLARIS RIO, which requires the thickness output channel

**The scope discipline:** the problem statement names three things. We are doing
those three properly rather than five badly. No autopilot, no COLREGs, no claim
to solve Southern Ocean traffic management.

### One genuine white space we found — and the risk attached to it

**No operational Antarctic ice-compression product exists anywhere in the
world.** Russia's AARI forecasts gridded compression for the Barents and Kara
Seas only; Canada's CAPS is Arctic-only; the Baltic services publish none. And
**IMO POLARIS is blind to it** — read end to end, MSC.1/Circ.1519 never uses the
words *pressure*, *compression*, *ridge* or *drift*.

Compression is the "sandwiching" hazard: ice converging on a stationary ship.
AARI's own normative statement names the worst case precisely —

> *compression at the fast-ice edge when the general drift sets into it at an
> angle*

— which is **exactly the geometry of a ship offloading at Bharati or Maitri**.

Two honest constraints come with it, and we state both:

1. **There is no observational Antarctic ice-drift field in our season.** OSI
   SAF's Southern Hemisphere drift product runs only 1 April – 31 October. The
   resupply season is December to March. Any compression layer must be built on
   modelled drift, not observed.
2. **The physics amplifies our own error.** Ice strength is exponential in
   concentration (Hibler: `P = P*·h·exp[−C(1−A)]`, C = 20), so `dP/P = 20·dA`.
   A 5-percentage-point concentration error becomes a **2.7× error in ice
   strength**; ten points becomes **7.4×**.

That second point is the strongest argument for the uncertainty work we already
plan — and the strongest argument against anyone shipping a compression number
without one.

### What we will never claim

**We will not warn about growlers.** A growler is under 5 m long with a ~7 m
keel, and it is the classic hull-holing hazard. Sentinel-1 detects icebergs
under 60 m at **5–13%** even in best-case conditions; the smallest berg the US
National Ice Center tracks in the Antarctic is ~13 km across. **The gap between
the smallest tracked object and the thing that sinks ships is three and a half
orders of magnitude.** That is a radar-and-lookout problem, and saying so is
what makes the rest of our claims credible.

---

## Anticipated questions

**"Your background is a reanalysis, not a forecast — isn't that leakage?"**
Partly defended: if GLORYS12 contained the answer its own RMSE would be near
zero, not 0.163 — worse than persistence at every horizon. But it may carry some
future signal and we do not claim otherwise. The clean test is the no-background
ablation; it is written and not yet run. Production corrects a real forecast
where this cannot arise.

**"Is 74% closure a data artifact rather than real ice?"**
The closed days read 80–99% consistently across neighbouring cells and across
consecutive days. It is the *open* days that are suspect — four of eight are
spillover artifacts. If anything the true closure rate is higher than 74%.

**"How is this different from IcySea?"**
Careful — we have not tested IcySea and will not claim it is inaccurate. What we
can say: published passive-microwave algorithms disagree with each other by
roughly **10× at the ice edge** (SD 2.8% to 28.8% at 15% SIC), and the producers
state their shipped uncertainty **excludes** melt-pond, thin-ice and
weather-filter effects. No study we found propagates that uncertainty into a
routing decision. That is the gap we are building into.

**"Has anyone done this route before?"**
Yes — there is an optimum-route study for the Bharati–Maitri leg (*Polar
Science*, 2021), deterministic ice and wind resistance only. That is a precedent,
not a competitor: same corridor, no uncertainty. *Verify this citation before
presenting — it came from a search that was cut short.*

**"Why should we believe your numbers?"**
Because we withdrew two of our own. The 17.4-day transit and the "route bends
around the thickest ice" claim were both measured to be wrong and both retracted
in writing before anyone asked.
