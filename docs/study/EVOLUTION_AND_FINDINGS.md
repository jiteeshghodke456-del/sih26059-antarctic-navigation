# Dakshin: evolution, findings, and what is still open

Scope: the project from the first commit (2026-08-31, `0020fba`) to the
night build of 2026-11-21. 332 commits on `main` in that window (as of 17:56 UTC on 2026-11-21). Every
number below comes from a file in this repository; the path is cited next to
it. Three labels are used throughout:

- **Measured**: a number in a file under `dakshin/figures/` or a log, produced
  by a script in `scripts/` or `dakshin/`.
- **Designed**: specified in `docs/DECISIONS.md` or a design doc, with no run
  behind it yet.
- **Claimed**: written in a narrative doc but not traced to a measured file.

Where the repository disagrees with itself, the disagreement is listed in
Appendix A rather than resolved here. Read Appendix A before quoting any
figure from the docs.

---

**Snapshot.** The repository was read between about 17:56 and 18:21 UTC on 2026-11-21. "In this pass" means the study pass that wrote this file. Commits and uncommitted edits by other agents that landed or appeared later are listed in Appendix C.

## 1. Stage timeline

Commit dates are from `git log --reverse --format='%h %ad %s' --date=short`.
Commit counts per month: August (from the 31st) 30, September 155, October 72,
November 75. Of the 332 commits, 168 are daily CMEMS harvest commits.

| Stage | Dates | What was built | Motivating question |
|---|---|---|---|
| 0. Scoping and first prototype | 2026-08-31 | Phase 1 research and architecture (`0020fba`); daily CMEMS harvest and GitHub Actions cron (`3d95515`, `ac4ccda`); Kaggle training notebook generated from repo sources (`c802288`); NSIDC truth downloader (`5ba8d30`); GLORYS12 to NSIDC regridding (`1c23670`); bias-correction U-Net (`698e827`); reframed as lead-time forecasting with baselines (`90fe99e`); multi-lead results and reanalysis-leakage ablation recorded (`27308ff`, `98c5e8c`); first route computation (`e165f79`) | Can a learned correction beat the baselines that matter for Antarctic sea-ice concentration at 1 to 7 days? And what data can never be recovered once it is missed? |
| 1. Data verification and first physical checks | 2026-09-01 to 09-04 | Research on the POLARIS framework and PolarRoute gaps (`8e3d6bd`); ice-data QC and the destination-window result (`73b0e44`); Wagner-Dell-Eisenman drift model (`16cef7c`), USNIC catalogue loader (`2fbf084`), drift regime measurement on real USNIC data (`6fc7034`); TRUE_CLAIMS ledger and verifier (`c5b5af4`); harvest compression from 42.6 to about 5 MB per day (`f2de08e`); first local demo (`4add2cd`) | Does the satellite record agree with itself at the destination? Is the drift model right on real icebergs? |
| 2. Audit and withdrawals | 2026-09-03 to 09-08 | Harvest made to fail loudly (`3f9f9a2`); claims withdrawn or corrected (`320cb17`, `fb20a3e`, `a2ab4c9`); protected areas modelled (`641e20f`); adversarial audit passes A to AT (`d71d67f` through `ecc82e0`); bridge console, live time-aware router, synthetic world model for the demo (`82242d3`, `97fd814`, `00f3c78`); one land mask shared by bergs, wind and router (`7288d80`) | Which of our own claims would not survive a reviewer? |
| 3. Archive growth | 2026-09-09 to 11-17 | Daily harvest continues; prompt pack and materials (`f568877`, 10-05); harvest fixes for late and stale bulletins (`1a00b3b`, 11-18) | Can the forecast archive be kept intact while the rest of the system changes? |
| 4. Pre-build measurement | 2026-11-18 to 11-20 | Stale-forecast rejection rule (`1a00b3b`); CMEMS forecasts scored against persistence (`5be27ca`); 13 weekly USNIC issues back-filled (`6d2a212`); login retries (`47e0ce1`) | What does the archive say about skill, before any model is retrained? |
| 5. Night build (2026-11-21) | 2026-11-21 | Seven slices (1, 2, 4, 5, 6, 7, 8), resolution studies F1 to F4, licence and claims verifier (slice 11), package rename to `dakshin` | Each slice answers one question: model loading (1), real-forecast skill (2), currents in the harvest (4), iceberg drift on real currents (5), real wind and waves (6), real bathymetry (7), AIS decoding (8), and the resolution, melt and rename work |

Slice numbers come from the handoff specification that `docs/CURRENT_STATE.md`
and `docs/backlog.md` refer to as HANDOFF_TONIGHT. That file is not in the
repository, so slices 3, 9 and 10 cannot be described from the repository.
Slice 10 (the site) and slice 3 are recorded as "in flight" in
`docs/CURRENT_STATE.md`.

---

## 2. Findings

Each finding has three parts: the question that was asked, what the data
said, and what changed because of it.

### 2a. The land-spillover QA discovery

**Question.** The satellite record shows open water where there should be
coast. Is that real, and does it change the route?

**What the data said.** The NOAA/NSIDC CDR applies a land-spillover filter to
coastal cells. When it fires, the product writes 0.0 rather than a fill value,
and 0.0 lies inside `valid_range [0, 100]`, so an unguarded reader accepts it
as open water. `dakshin/ice_quality.py` (module docstring) gives the specific
case: on 2019-12-01 the cell at 69.1 S, 75.9 E, about 35 km from Bharati,
reads 0.0 with `cdr_seaice_conc_qa_flag = 4` (`Land_spillover_filter_applied`),
beside cells reading 0.60; three days later the same cell reads 0.90.

Measured over the whole archive (`dakshin/figures/ice_quality_audit.json`,
1,096 daily files, 2018-01-01 to 2020-12-31):

| Measure | Value |
|---|---|
| Days on which the spillover filter fires | 1,096 of 1,096 |
| Cells suppressed per day | mean 118.2, max 488 |
| "Hard zero flush against heavy ice" | 100% of days, mean 14.8, max 87 |
| Worst no-input outage | 59,350 cells in one day |
| Days with suspect cells in the Bharati approach box | 474 (43.2%) |
| Days with suspect cells in the Maitri box | 262 (23.9%) |

The box is `APPROACH_RADIUS_CELLS = 8` in `dakshin/audit_ice_quality.py`: 8
cells in each direction around the station, 17 by 17 cells, about 400 km on a
side. The docs call it "the 200 km box". That is the half-width, not the full
width. The 43.2% and 23.9% figures are unchanged by this, but the phrase
should be corrected before it is quoted.

The consequence for the station (`dakshin/figures/destination_window.json`,
`docs/PROTOTYPE_RESULTS.md` §1 to §2): at the 80% working limit in December
2019, Bharati's cell was closed on 23 of 31 days (74.2%). This is an ice-only
figure. Once depth is in the mesh, the station cell is ashore and is closed on every day
(`docs/backlog.md`, the line added by `13861d9`), so the destination-window run has to be repeated
on depth meshes before the 23-of-31 figure is combined with the bathymetry results (Appendix C). The approach point
100 km north was open on all 31. Eight days read as open at Bharati, and four
of them (2019-12-01, 12-07, 12-08, 12-09) read exactly 0.0 with the QA flag
set. The other four open days (12-21 at 80.0%, and 12-29 to 12-31 at 75 to
79%) are real, but close to the working limit.

The masking moves coastal ice in the safe direction. Mean SIC in the Bharati
200 km box rises from 46.8% to 54.6% on 1 December 2019 and from 62.5% to 65.4%
on 10 December (`docs/PROTOTYPE_RESULTS.md` §2).

**What changed.**

- `dakshin/ice_quality.py` reads the QA flag and sets spillover and no-input
  cells to NaN. The mesh builder drops them, so an unknown coastal cell takes
  its parent cell's value rather than asserting open water.
- Parent-cell fill is not a correct answer, only a less wrong one. On the
  artifact days it gives 30 to 36% where the surrounding pixels read 80 to 95%
  (`docs/PROTOTYPE_RESULTS.md` §2). The backlog records the next step as
  treating these cells as unknown and high-risk (`docs/backlog.md`,
  `[critical][data]`), which is not built.
- The STATIC route arm in the regret experiment arrives on 2019-12-09, which is
  one of the four artifact days. Its 0.03-day "regret" therefore depends on a
  cell the document itself says should not be trusted (`docs/PROTOTYPE_RESULTS.md`
  §6). The arm that trusts spillover cells records 0.00 days.
- **Not fixed:** the prototype's training data. `dakshin/kaggle/make_notebook.py`
  builds its valid mask as `np.isfinite(bg) & np.isfinite(tr)` and does not
  import `ice_quality`. The model was trained with the spillover zeros as
  valid open water at the coast (`docs/backlog.md`, `[major][ml]`).

### 2b. Raw CMEMS beats persistence on real operational forecasts, on RMSE at every lead

**Question.** The prototype was tested against reanalysis background and
persistence. Does the raw operational forecast that the vessel would really
have received beat persistence, on real satellite truth, at the leads a voyage
plans over?

**What the data said.** `dakshin/figures/realforecast_hindcast.json`, written by
`scripts/realforecast_hindcast.py` (`--no-model` run, so the U-Net column is
null). Setup from the JSON: 76 archived CMEMS GLO12 cycles at lead 1 (2026-08-31
to 2026-11-18), 72 at lead 7; truth is NSIDC NRT G10016 v4 (AMSR2, QA-masked);
corridor 0 to 80 E, 55 to 78 S; four stale cycles excluded per
`data/cmems_forecast_archive/KNOWN_STALE.md`.

| Lead (days) | Scored cycles | RMSE raw CMEMS | RMSE persistence | CMEMS RMSE vs persistence | IIEE raw CMEMS (10³ km²) | IIEE persistence (10³ km²) | CMEMS IIEE vs persistence |
|---|---|---|---|---|---|---|---|
| 1 | 76 | 0.10199 | 0.11977 | 14.8% lower | 195.1 | 187.7 | 3.9% higher |
| 3 | 75 | 0.10479 | 0.14391 | 27.2% lower | 194.6 | 277.2 | 29.8% lower |
| 5 | 74 | 0.10981 | 0.15508 | 29.2% lower | 200.2 | 319.2 | 37.3% lower |
| 7 | 72 | 0.11530 | 0.16414 | 29.8% lower | 210.2 | 353.3 | 40.5% lower |

The percentages are computed from the JSON values. IIEE is the mean
ice-edge error at the 15% threshold (see the glossary, Section 4 of the
runbook). The RMSE values match `docs/TRUE_CLAIMS.md` §1.13.

**The qualification the repo's summary omits.** On RMSE, raw CMEMS beats
persistence at every lead. On IIEE, it does not beat persistence at lead 1: the
edge error of the operational forecast is 3.9% higher than persistence's. The
claim "raw CMEMS beats persistence at every lead" is therefore true for RMSE
only. ADR-027 (`docs/DECISIONS.md`) requires the corrected forecast to beat raw
CMEMS on both IIEE and CRPS at each lead before it is claimed. This table does
not test that rule, because it has no corrected forecast. It does show that raw
CMEMS is itself 3.9% worse than persistence on IIEE at lead 1, so any statement
about lead 1 has to rest on RMSE alone. CRPS is not computed in any file in
`dakshin/figures/`.

**Caveats.** One spring season, about 75 cycles, so the leads are strongly
autocorrelated and no confidence interval has been computed. The truth changes
sensor in the middle of the record: AMSR2 from 2025-01-01, where the training
truth was F17 SSMIS (the JSON's own caveat). Persistence is computed from the
NSIDC observation carried forward (`scripts/realforecast_hindcast.py`
docstring). The reanalysis-based figures in §2g are not comparable with this
table. They use a different region, truth product, period and background.

**What changed.**

- The metric that the mandatory baseline is judged by is now the operational
  forecast, not the reanalysis or the damped persistence (`docs/DECISIONS.md`
  ADR-027, which replaced ADR-006's baseline).
- The earlier scorer, `scripts/score_cmems_archive.py`, compared CMEMS against
  its own later day-0 field, which flatters it (`docs/backlog.md`, `[major][eval]`).
  The git history of that path starts on 2026-11-19 (`5be27ca`), although the
  backlog line that flags it is dated 2026-09-03. The discrepancy is recorded
  in Appendix A.
- The learned correction has not been scored on these cycles. The checkpoints
  are not in the repository (`models/sic_correction/` contains only `unet.py`),
  so the "U-Net" column is pending. `docs/CURRENT_STATE.md` lists the re-run as
  queued on Kaggle.

### 2c. RMSE cannot see model resolution; the ice-edge metric can

**Question.** Does the resolution of the ocean model change the answer a
captain would get? A standard score was the first thing to check.

**What the data said.** `scripts/resolution_study.py` block-averages the same
76 cycles from 1/12° to about 1/4° and about 1°, then scores each against the
same truth on the same cells. `dakshin/figures/resolution_study.json` holds the
numbers.

RMSE, raw CMEMS forecast:

| Lead | 1/12° | 1/4° | 1° | Persistence |
|---|---|---|---|---|
| 1 | 0.10199 | 0.10035 | 0.10402 | 0.11977 |
| 3 | 0.10479 | 0.10314 | 0.10598 | 0.14391 |
| 5 | 0.10981 | 0.10816 | 0.10988 | 0.15508 |
| 7 | 0.11530 | 0.11365 | 0.11417 | 0.16414 |

IIEE at the 15% threshold (10³ km²), with the change against 1/12°:

| Lead | 1/12° | 1/4° | vs 1/12° | 1° | vs 1/12° | Persistence |
|---|---|---|---|---|---|---|
| 1 | 195.1 | 189.7 | -2.8% | 203.3 | +4.2% | 187.7 |
| 3 | 194.6 | 190.3 | -2.2% | 209.3 | +7.6% | 277.2 |
| 5 | 200.2 | 197.7 | -1.3% | 222.7 | +11.2% | 319.2 |
| 7 | 210.2 | 208.3 | -0.9% | 244.2 | +16.2% | 353.3 |

**What it says.** RMSE gets slightly better when the model is coarsened. At 1°
it is worse at leads 1 to 3 and a tie at lead 5, then marginally better than
1/12° at lead 7. IIEE, which measures where the 15% edge sits, gets worse
at 1°, by 4 to 16% growing with lead. Between 1/12° and 1/4° the IIEE
difference is 1 to 3%, and the sign is in favour of 1/4°. The study calls
that difference "indistinguishable" (`docs/RESOLUTION_STUDY.md`). No
confidence interval was computed, so the statement that 1/12° adds nothing
measurable is weaker than the table suggests: the study does not show that the
two are the same, only that this sample cannot tell them apart.

The explanation the document gives for RMSE's blindness is the double-penalty
effect: a sharp forecast that misplaces an edge pays for a miss and a false
alarm, while a smoothed field pays once. That is the standard explanation and
it is consistent with the table, but the study does not include a separate
test of it (for example a displaced-edge synthetic case).

**Caveat stated in the document.** Coarsening one model's output is not the
same as running a coarser model. Block-averaging removes resolved structure but
keeps the eddy-informed physics. A real test needs the same model run at
several resolutions, for example the ANHA configurations (`docs/RESOLUTION_STUDY.md`).
The NEMO-native reader added on the night (`93ff026`, slice F2) is intended
for that. It is "untested on real NEMO output" by its own commit message.

**Pending.** The U-Net columns are pending the checkpoints, as in §2b.

**What changed.** RMSE is no longer used as a resolution criterion anywhere in
the docs. IIEE is the metric the decision layer should use. The 1/12° versus
1/4° question is recorded as an honest null in this sample, not as a result.

### 2d. Corridor giants are grounded; persistence beats the drift model; grounding detection matters more than resolution

**Question.** Can the Wagner-Dell-Eisenman drift model, driven by real currents,
forecast where a giant iceberg will be after a week?

**What the data said.** `scripts/berg_hindcast.py` integrates each USNIC
position fix forward to the next fix on CMEMS analysis currents
(`dakshin/berg_forecast.py`, midpoint RK2, dt = 1 h) and compares the landing
point with where USNIC places the berg. The reference is persistence: the
berg did not move. `dakshin/figures/berg_hindcast.json`:

| Quantity | Model | Persistence |
|---|---|---|
| Segments | 88 total, 81 usable, 7 "grounded or unknown" | |
| Median error, all usable segments | 4.35 km/day | 0.0 km/day |
| Mean error, all usable segments | 5.06 km/day | 0.43 km/day |
| Moving segments (persistence displacement > 3 km; 13 segments, 4 bergs) median | 6.01 km/day | 2.45 km/day |
| Stationary segments (68) median | 4.26 km/day | 0 |

Persistence wins on the stationary sample by construction: a berg that did not
move has zero persistence error. It also wins on the moving sample, at weekly
fix cadence. The JSON records this as the finding: a current-advection model
without grounding detection drifts anchored bergs.

The "grounded" label is an inference, not a bathymetric check. A segment is
classed as stationary when the USNIC displacement is at most 3 km. The "grounded
or unknown" status (7 segments) means only that a forecast step landed on a
NaN current, which is land or outside the data (`dakshin/berg_forecast.py`,
module docstring). Neither test uses IBCSO. The claim "most corridor giants are
grounded" is therefore a behavioural statement that has not been checked
against the seabed at each berg position.

Uncommitted edits in `dakshin/berg_forecast.py` at the snapshot add a `BathymetryGrid`
and an assumed keel draught (0.83 × 250 m, about 207 m) for grounding detection. They are not
part of any committed figure. The same diff changes how `wind_forcing_R` is computed. It does
not change the zero-wind default, as far as the diff shows.

**Resolution of the currents.** `scripts/berg_resolution.py` runs the same
segments on currents block-averaged to 1/4° and 1°
(`dakshin/figures/berg_resolution.json`):

| Currents | Usable segments | Grounded or unknown | Median error, all (km/day) | Median error, moving (km/day) |
|---|---|---|---|---|
| 1/12° | 81 | 7 | 4.35 | 6.01 |
| 1/4° | 86 | 2 | 4.07 | 5.93 |
| 1° | 88 | 0 | 3.49 | 5.06 |

Coarser currents give lower error, which is the opposite of the naive
expectation. The explanation the study gives: blurring the currents suppresses
the velocity at anchored bergs, so the forecast moves toward "does not move",
which happens to be right for this sample. The usable-segment count differs
between rows (81, 86, 88), so the medians are not computed over the same
segments. That is the most important caveat on this table. Comparing medians
over different subsets is not a clean comparison.

**Errors in the write-up of this finding.**

- The docstring in `scripts/berg_resolution.py` says that drift is "almost pure
  current (R << 1 in every segment)". The segment file records `wind_forcing_R`
  from 0.037 to 1.73, median 0.25. R above 1 is in at least one segment, so
  "every segment" is wrong.
- `dakshin/figures/berg_hindcast.json` says the wind is "zero (slice 6 pending)".
  Slice 6 (ECMWF wind harvest) is recorded as done in `docs/CURRENT_STATE.md`,
  and `data/ecmwf_wind/` holds the 2026-11-21 file. The JSON predates the
  forcing change. The hindcast has not been rerun with wind.
- The error figure that the document uses as the forecast cone rate, 4.35
  km/day (`docs/TRUE_CLAIMS.md` §1.15), is the median. ADR-025 (`docs/DECISIONS.md`)
  defines the exclusion radius as a p90 of leave-one-out error, which is not yet
  measured (`docs/backlog.md`, `[minor][ml]`). The median is not a
  conservative radius.

**What changed.**

- The drift model is kept as built and tested (23 tests in `models/iceberg/test_drift.py`,
  per `docs/TRUE_CLAIMS.md` §1.9), with the Ca/Cw swap fixed.
- The binding constraint is recorded as grounding detection, which needs
  IBCSO depth against the keel draught. Neither is in the drift model yet. The
  backlog lists it as `[major][bergs]` and it is the next iceberg item.
- Resolution of the current field is treated as second order until anchored bergs
  stop being advected (`docs/RESOLUTION_STUDY.md`, F3).

### 2e. IBCSO bathymetry exposed the old headline route ending on land; the claim was withdrawn twice, then re-derived

**Question.** Does the router respect the seabed? A route that ends at a
station needs to end in water.

**What the data said, in order.**

1. **17.4 days (superseded).** The first transit time was computed with a
   vessel configuration that had beam 18.6 m (real 22.4 m) and maximum speed
   14 km/h (real service speed 16.4 kn, 30.4 km/h). The ship was modelled at
   about half its real speed (`docs/PROTOTYPE_RESULTS.md`, routing section,
   correction paragraph).
2. **8.6 days (2026-09-02).** With the corrected vessel, the route on real
   NSIDC ice, day by day, gives 8.58 days of ideal steaming time. The document
   states this is steaming time only and is not a voyage duration
   (`docs/PROTOTYPE_RESULTS.md` §4).
3. **Withdrawn (2026-11-21).** The IBCSO v2 subset (`data/bathymetry/ibcso_v2_corridor_0p05.nc`)
   places the route's final point at +91 m. The chart gate now fails it.
   `docs/TRUE_CLAIMS.md` §1.11 withdraws the number. The same section of TRUE_CLAIMS
   records the earlier withdrawal of 17.4 days, so the 8.6-day figure has been withdrawn
   twice.
4. **Re-derived (same day, `13861d9`, on main after this document's reads; Appendix C).**
   With depth in the mesh (IBCSO south of 50 S, GEBCO_2020 north, subset built by `24317da`)
   and the router's nearest-node rule changed in `478ecd2`, the route on the same 1 December 2019
   ice is **8.66 days steaming**, arriving **16 km off** the station, never over water shallower than
   89 m. `docs/TRUE_CLAIMS.md` §1.11 now carries this number and calls it a lower bound. The route-regret,
   destination-window and alternatives experiments were computed on meshes without depth and have not
   been re-run (`docs/backlog.md`, `[major][eval]`). The 8.66-day figure is therefore not yet supported
   by the regret experiment.

**A caveat about the withdrawal's evidence.** The IBCSO subset is a
conservative block maximum: "the shallowest source elevation within one box of
this box" and its neighbours (about 5 km buffer), and its own comment says that
"zero or positive is land or ice-shelf surface" (`scripts/subset_bathymetry.py`
attributes and header). A value of +91 m therefore means land or ice shelf. The
repository does not separate the two at Bharati. `docs/backlog.md`
(`[minor][data]`) quotes the IBCSO v2 paper as giving 23.79% direct measurement
south of 50 S and naming East Antarctica as singlebeam-dominant, which describes
this corridor. That quotation was not re-checked against the paper in this pass.

**What changed.**

- `dakshin/gates.py` `chart_gate` returns UNKNOWN or MARGINAL and never PASS
  without an official ENC. A leg shallower than 20 m is refused in both routers
  (`docs/TRUE_CLAIMS.md` §1.17, slice 7 in `docs/CURRENT_STATE.md`).
- The day-0 Cape Town to Bharati route did not solve at the time of the earlier reads: IBCSO put the
  goal's lattice point in 85% simulated ice on day 0, and days 2 to 14 solved at 7.8 to 8.4 days
  (`docs/backlog.md`, `[major][demo]`, before `13861d9` removed that line). `478ecd2` changed the
  snapping rule that made day 0 hinge on one ice-locked node, and its commit message says the tests
  cover every departure day. Whether day 0 solves now was not re-run in this pass.
- `dakshin/figures/routes.json` was regenerated with depth in `13861d9` (item 4 above).
  The backlog line that asked for this regeneration was removed in the same commit.

### 2f. The Bharati approach was closed by real spring ice

**Question.** On a real forecast cycle, is the Bharati approach open to this
vessel at the working ice limit, and is the weather survivable?

**What the data said.** `scripts/real_route_run.py` on the 2026-11-21 cycle
(`dakshin/figures/real_route.json`). The goal is given as `[-69.4, 76.2]`; the
order is not labelled in the JSON. The values match Bharati's position as
described elsewhere (76.2 E in `docs/backlog.md`), which suggests latitude first.

| Field | Value |
|---|---|
| Approach closed at the ice limit | true |
| Closest reachable point | 50.6 km from the goal |
| Estimated time to closest point | 5.55 days |
| Worst SIC along the route found | 0.723 (72.3%) |
| Worst significant wave height along the route | 4.77 m |
| Worst wind | 14.9 m/s (Beaufort 7) |
| Weather gate | FAIL, waves 4.77 m against an assumed 3.0 m limit |
| Visibility | not assessed |

The "closed" state is computed as "no route under the limit to the goal". The
run then routes to the closest passable cell (`scripts/real_route_run.py`
lines 42 to 56). The worst SIC of 0.723 is below the 0.80 limit because it is the
maximum along the route to that closest cell, not at the goal, so the two
figures do not conflict.

**Caveats.** One cycle. The route covers only the segment south of 55 S,
because the wave and wind harvests do not cover further north (per the
`segment_note` in the JSON). The 80% ice limit is a stand-in that
`docs/PROTOTYPE_RESULTS.md` §5 states is not derived from the ice class; POLARIS
is indexed by ice type, which the repository does not yet model. The 3.0 m wave
limit is an assumption ("limits are assumptions, not this hull's PWOM", per the
JSON). The wind and wave values are real forecast values, and the gate decision
uses assumed thresholds.

**What changed.** The weather and traffic gates are implemented in
`dakshin/gates.py` (`weather_gate`, `traffic_gate`) and used by the real-route
run. `real_route.json` was generated before the router's nearest-node rule changed in `478ecd2`
(Appendix C), so a re-run may give a different closest approach. This pass did not re-run it. The traffic gate returns UNKNOWN without an AIS feed, which in the Southern
Ocean is the normal case (`docs/backlog.md`, `[minor][ais]`).

### 2g. Kaggle checkpoint forensics: the outputs were never in the store, and the training cell was not code

**Question.** Why did the scheduled training runs produce no checkpoints, and
can the 2026-08-31 numbers be reproduced?

**What the record says.** `docs/CURRENT_STATE.md`:

- The original 2026-08-31 checkpoints were never in Kaggle's output store.
- The training-loop cell in the saved notebook was typed as markdown, so
  batch runs executed nothing. Version 6 of the kernel is said to fix the cell type.
- CMEMS credentials are read from a private Kaggle dataset, because CLI batch
  runs cannot read Kaggle Secrets.
- At the time of writing, kernel `jiteeshghodke/notebookd39fdf7959` version 6
  was queued, and a background watcher polled every five minutes. I did not
  query Kaggle.

**What the repository shows.**

- `dakshin/kaggle/make_notebook.py` now builds the training loop with `code()`
  (around line 240). The committed `dakshin/kaggle/isih_train.ipynb` has a code
  cell containing `torch.manual_seed(0)`. The defect that the record describes
  was in the notebook as saved on Kaggle, not in this generator's current output.
- The split is a temporal 70/15/15 split of sorted dates over 2019 and 2020
  only (`YEARS = [2019, 2020]`, `i_tr, i_va = int(n*0.70), int(n*0.85)`). It is
  not the production split in ADR-019 (train 1993 to 2018, validate 2019 to 2021,
  test 2022 to 2024).
- The seed is `torch.manual_seed(0)`, set before each lead's model, so all four
  leads start from the same initialisation.
- There is no QA mask in the notebook's valid mask (finding 2a).
- `models/sic_correction/` in the repository contains `unet.py` and nothing
  else. The four `isih_prototype_lead{1,3,5,7}.pt` files and their
  `SHA256SUMS` are absent. The headline numbers in `docs/PROTOTYPE_RESULTS.md` (0.0465
  to 0.0968) therefore cannot be re-derived from this repository.

**A correction to the brief this document was written from.** The brief says
`docs/CURRENT_STATE.md` records the re-run with an identical seed and split. It
does not. `CURRENT_STATE` says nothing about the seed or split of the re-run.
The generator does fix the seed and the split, so the reproducibility argument
can be stated as "the generator fixes them", which is a weaker and accurate
claim.

**What changed.**

- `scripts/pull_checkpoints.sh` pulls the four files, writes `SHA256SUMS`, runs
  `dakshin/test_model_io.py`, and then reruns the hindcast and the resolution
  study with the model. It is written to be run once the kernel completes.
- `dakshin/model_io.py` loads the checkpoints only after their checksums match.
- The prototype numbers are labelled as an upper bound on forecast skill (see 2h),
  because the reanalysis background is in the input. The document states this
  next to the numbers.

### 2h. The reanalysis background leaks the target, and the leak is not yet measured out

**Question.** The prototype's input includes a reanalysis field. Does that field
contain the answer?

**What the data and code say.** `dakshin/features.py` (`build_channels`) sets
channel 0 to `background[t + lead]`, which is the reanalysis valid at the target
date. The reanalysis assimilates satellite observations, including ones near
the target date. The raw reanalysis error is flat across lead (0.1630 at lead 1,
0.1637 at lead 7; `docs/PROTOTYPE_RESULTS.md`), which the document calls "the
fingerprint of a field that has seen the target". The first version of the
argument defending the reanalysis was withdrawn (commit `fb20a3e`), because the
reanalysis error measures grid and model bias, not information about the target.

The no-background ablation is written. `docs/PROTOTYPE_RESULTS.md` says it "costs
~20 minutes" and that it has "not yet run". No ablation output exists in the
repository.

**What the innovation channel shows.** Channel 8 is `background[t] - observed[t]`
in code. Version 1 of the model saw the background only and scored 0.1051,
losing to persistence. Adding the observations closed the gap (`docs/PROTOTYPE_RESULTS.md`,
"What the model actually is").

**The second leak that was identified and avoided.** ERA5 2 m temperature at
t + lead would add a larger leak, because sea ice is a prescribed lower boundary
in ERA5 and 2 m temperature is close to a deterministic function of the observed
ice (`docs/PROTOTYPE_RESULTS.md` "Next improvements", item 4). The design uses
winds valid at t instead.

**What changed.** The prototype numbers are labelled an upper bound. The
ablation is the highest-value experiment in the backlog that is not yet run
(`docs/backlog.md`, `[critical][ml]`). The production path, which corrects real
forecast cycles rather than the reanalysis, is the test that would remove the
caveat, and it is the one the night build's hindcast (2b) starts.

### 2i. The early headline moved between commits, and the repository does not record why

**Question.** Is the 3-day result stable?

**What the data said.** The same results file, recorded on the same day
(2026-08-31), reports two different 3-day scores:

| Commit | File | Model RMSE, 3-day | Persistence | Headline |
|---|---|---|---|---|
| `27308ff` (record results), `fc366ad` (notebook v3) | `isih/RESULTS.md` | 0.0765 | 0.0958 | +20.2% vs persistence |
| `98c5e8c` (multi-lead results and ablation) | `isih/RESULTS.md`, now `docs/PROTOTYPE_RESULTS.md` | 0.0720 | 0.0958 | +24.9% vs persistence |

Both are labelled as the Kaggle run of 2026-08-31, on a single seed. The
repository does not record which run produced the 0.0720, or why the model
number changed.

**What changed.** The results document says "these are the numbers to quote".
The single seed means there is no error bar on any of this, which the backlog
records (`[major][ml]`, "One seed means no error bar"). The shift of about 6%
in the same model's 3-day score is a direct measure of how much a single run
can move. Three or more seeds are required before any comparison that differs
by a few percent is adopted (`docs/backlog.md`).

### 2j. The CMEMS archive has stale cycles, and the harvest's clock rule is the fix

**Question.** Is every archived forecast the forecast issued on its date?

**What the data said.** `data/cmems_forecast_archive/KNOWN_STALE.md` (found on
2026-11-18 by comparing each cycle with the one before) lists four files that
are copies of the previous day's forecast with its first day cut off: 9 daily
steps instead of 10, and identical sea-ice concentration on all 9 shared dates.
They are `cmems_siconc_2026-09-20`, `2026-10-11`, `2026-11-10` and `2026-11-17`.

Two causes are recorded. The 11-10 and 11-17 runs started after midnight UTC
and named the file from the clock while the server still held Monday's forecast.
The 09-20 and 10-11 runs started after 12:00 UTC, before Copernicus had
published that day's forecast, and both were Sundays. CMEMS overwrites each
forecast with the next, so the true forecasts for those four dates are gone.

**What changed.**

- `scripts/harvest_cmems.sh` derives the cycle date from the clock, with a
  rule: before 12:00 UTC the cycle is yesterday. It rejects any file whose step
  count is not 10 (`EXPECTED_DAYS`), and it records `not_published` rather than
  saving a wrong file.
- `.github/workflows/cmems-harvest.yml` runs three times a day at 12:23, 17:23
  and 21:23 UTC, always after the 12:00 UTC guarantee. Its header records that
  a scheduled run was four to five hours late on three consecutive days in the
  first week, and that the cron must never be on the hour.
- The four stale files are still in the archive, labelled in `KNOWN_STALE.md`.
  The realforecast hindcast excludes them, which is why the scored cycle counts
  are 76, 75, 74 and 72.
- **Still open.** The fix is clock-based, and the backlog's critical item
  is to derive the bulletin date from the dataset's own time axis
  (`docs/backlog.md`, `[critical][data]`). The backlog also asks for a sentinel
  that fails loudly when a bulletin is missed (`[high][ops]`).

### 2k. Melt and freshwater: an estimate with a known, large uncertainty

**Question.** How much freshwater do the giant bergs release along their forecast
tracks?

**What the data said.** `scripts/berg_melt.py` integrates the three
deterioration terms in `models/iceberg/melt.py` (basal turbulent melt, buoyant
convection, wave erosion; Keghouche et al. 2010 coefficient set, reimplemented
from the papers, not imported from GPL OpenDrift) along each giant's 10-day
track, on the 2026-11-21 cycle. `dakshin/figures/berg_melt.json` labels the
whole output "ESTIMATE". Thickness is an assumed 250 m, because USNIC publishes
no draught.

| Berg | Area (km²) | Mean freshwater (10⁶ m³/day) |
|---|---|---|
| D15C | 115.0 | 1.91 |
| D15D | 55.9 | 1.17 |
| D37 | 477.8 | 1.00 |
| B09G | 160.1 | 0.77 |
| D23 | 105.6 | 0.51 |
| C39 | 45.4 | 0.43 |
| C18B | 110.4 | 0.39 |
| C18C | 53.1 | 0.16 |
| **Total (8 bergs)** | | **6.35** |

**Caveats, in the module's own header.** The coefficients were tuned for Arctic
bergs orders of magnitude smaller than USNIC giants, so applying them to a 50 km
tabular berg extrapolates far outside their calibration. The output is a bulk
estimate of freshwater input, not a deterioration forecast.

Two further points. First, the berg with the largest area (D37, 478 km²) does not
have the largest melt rate, and the two bergs of nearly equal area (C18C at 53 km²
and D15D at 56 km²) differ by about 7 times. The melt terms depend on relative
speed, sea-surface temperature and wave height along each track, not on area
(`models/iceberg/melt.py` header). The JSON does not record per-berg speed or
temperature, so the attribution of the difference to a particular term is not
verified. Second, the wave height is set to 0 under ice ("ice-covered: waves
damped", `scripts/berg_melt.py` line 79), which removes the wave-erosion term
where pack ice damps waves. That is a physically reasonable choice, but it is a
choice.

**A provenance gap.** The script reads `data/cmems_forecast_archive/cmems_sst_<cycle>.nc`
and takes `thetao`. No script in the repository fetches that file. `scripts/harvest_cmems.sh`
fetches ice, currents and waves only, and `ATTRIBUTION.md` does not list an SST dataset.
The one SST file in the archive (2026-11-21) therefore came from a command that is
not recorded in the repository. The melt number cannot be regenerated from the
repository until that is fixed.

**What changed.** F4 (`7307f12`) is recorded as done. The output is labelled as
an estimate in the JSON and in the module, and is not used in any decision in
the routing code.

---

## 3. How we innovate

The claims below are limited to what the repository demonstrates. Each item
says whether it is built, designed, or claimed.

| Practice | Evidence in the repository | Status |
|---|---|---|
| **Gates that stay UNKNOWN when the data does not decide** | `dakshin/gates.py`: `capability_gate` returns UNKNOWN because no vessel threshold is sourced (line 69 comment cites the §48A.3 rule). `chart_gate` never returns PASS without an official ENC. The weather gate fails honestly at 4.77 m (`real_route.json`). The ice-gate MARGINAL band is 7.4 concentration points, derived in the module (`MARGINAL_BAND_BASIS`). | Built |
| **Claims ledger with withdrawals** | `docs/TRUE_CLAIMS.md` lists 17 claims, each with a file, and records two withdrawals (§1.11, §3). `scripts/verify_claims.py` runs 18 `check()` calls covering 29 claims against source files; on 2026-11-21, after `13861d9`, it printed `PASSED 29`. One of its checks still tests the pre-depth 8.6-day transit (Appendix A, item 27). | Built |
| **Score once, report as it comes out** | `scripts/realforecast_hindcast.py` docstring: "Scored once, reported as it comes out — no re-tuning on this set, ever." The prototype's test set is scored once. | Built, but see 2i: a single seed moved the headline by about 6% between commits. |
| **Operational-first data engineering** | Daily CMEMS harvest from 2026-08-31 (168 harvest commits). Stage B forecasts cannot be back-filled, so the harvest started on day 0 (`docs/DECISIONS.md` ADR-019). NSIDC NRT truth is downloaded before it rolls off. Harvest contract: never fail the ice cycle because of currents or waves (`scripts/harvest_cmems.sh`, `run_currents`, `run_waves`). Compression from 42.6 MB to about 5 MB per day (`f2de08e`). | Built |
| **Physics-grounded residual correction** | The network predicts a correction to the forecast, not the field: an untrained model returns zero and reproduces the forecast (`docs/PROTOTYPE_RESULTS.md`). The innovation channel is the observation-versus-background difference at each cell (`dakshin/features.py`, channel 8). | Built, but the 2b baseline has not been scored with the trained model. |
| **Iceberg drift from first principles, tested against the paper** | `models/iceberg/drift.py` implements the closed-form WDE17 model, with the drag-coefficient swap that changes wind-driven drift by 44% fixed (`docs/backlog.md`, `[resolved][ml]`). 23 tests reproduce the paper's coefficient table and its 765 m critical length (`docs/TRUE_CLAIMS.md` §1.9). | Built |
| **Choosing the metric the decision depends on** | IIEE, the ice-edge error, is the metric for the decision, because RMSE does not register resolution (2c). | Built |
| **Calibrated uncertainty by stratified conformal prediction, with a pre-committed pass/fail gate** | ADR-020 in `docs/DECISIONS.md`: coverage in the marginal ice zone at lead 5 must be 85% to 96%, mean width below 25 SIC points, and calibrated spread must beat inter-source disagreement. | Designed. Not implemented. The gate has not been run. |
| **A five-member ensemble whose disagreement widens the route** | ADR-005 and ADR-020. | Designed. The prototype is a single model per lead (`docs/PROTOTYPE_RESULTS.md` caveat 3). |
| **A time-expanded routing graph** | `docs/TRUE_CLAIMS.md` §2.3 and §5, item 1. PolarRoute's router has no time dimension, verified by reading its source. | Designed. The router is still static (`docs/backlog.md`, `[critical][routing]`). |
| **A 12-run dominance-filtered route sweep** | ADR-021. | Designed. `objective_function` is hard-coded to `traveltime` in two scripts (`docs/backlog.md`, `[major][routing]`). |
| **Robust routing across scenarios** | Not built. `docs/backlog.md` records it as a gap against the research matrix. | Gap |
| **A synthetic world model for the bridge demo** | `docs/backlog.md` "synthetic world model": designed in `docs/audit/WORLD_MODEL_DESIGN.md`, partly built in `dakshin/sim/`, and labelled as simulated input. Changed again by `f67493b` (Appendix C). | Partly built |

The strongest evidence of honest reporting is the withdrawals in
`docs/TRUE_CLAIMS.md`. The weakest is the reanalysis background, whose leakage has
been named but not measured (2h). The project's own audit passes (`d71d67f`,
`77cb1d9`, `787f2c2`, `ecc82e0` and others) are the process that produced most of
the withdrawals; their commit messages are the record of which claims were
corrected in which pass.

Novelty claims are not made here. The backlog records that "no study propagates
sea-ice forecast uncertainty into a routing decision" is medium confidence
because the search was cut short (`docs/TRUE_CLAIMS.md` §2.1 and `docs/backlog.md`).

---

## 4. What's next

Grouped by what it blocks, and ordered within each group. Each line states the
item, its severity from the backlog, and whether the code still matches the
item. Items the backlog marks as resolved are listed in Appendix B, not here.

### Data continuity (do first; these cannot be recovered later)

1. **NSIDC NRT truth rolls off.** `data/nsidc_nrt/` holds 89 files from
   2026-08-24 to 2026-11-20 (`scripts/download_nsidc_nrt.py`). The NRT archive
   keeps about three months (commit `5f32ae3`), so the first file reaches that
   age on or about 2026-11-24. The directory is gitignored and not on origin.
   Without a copy elsewhere, the real-forecast hindcast cannot be re-run from
   scratch after roll-off. This is not an item in `docs/backlog.md`.
2. **CMEMS file dates come from the clock.** `[critical][data]`. Still open;
   mitigated by the 12:23, 17:23 and 21:23 UTC schedule.
3. **Missed-bulletin sentinel.** `[high][ops]`. Still open.
4. **SST input has no producer.** `berg_melt.py` reads `cmems_sst_<cycle>.nc`.
   Not in the harvest, not in ATTRIBUTION. This is not in the backlog.
5. **Pin harvest dependencies.** `[minor][ops]`. Still open.

### Model validity (the claims the prototype makes)

6. **Run the no-background ablation.** `[critical][ml]`. Written, not run
   (`docs/PROTOTYPE_RESULTS.md`).
7. **Run the conformal gate on held-out 2022 to 2024 and on real forecast cycles.**
   `[critical][ml]`, the riskiest assumption in `docs/ML_ARCHITECTURE.md` §6. Not built.
8. **Mask the land-spillover zeros in training.** `[major][ml]`. The notebook's
   valid mask is `isfinite`, not the QA-masked field (2a).
9. **Pull the checkpoints and score the U-Net column.** `[major][model]`. Pending
   the Kaggle kernel. `scripts/pull_checkpoints.sh` is ready.
10. **Three or more seeds before adopting or rejecting any forcing or architecture
    change.** `[major][ml]`. Not started (2i).
11. **Stratify skill by distance to coast, marginal ice zone and ice edge.**
    `[major][eval]`. The current error pools the whole box, which is dominated by
    open ocean and pack where model and persistence agree trivially.
12. **Use the CDR's per-pixel uncertainty.** `[major][ml]`. `cdr_seaice_conc_stdev` is
    shipped and unused.
13. **Feed the wind-advected first guess, not raw wind.** `[minor][ml]`. Designed.

### Iceberg behaviour

14. **Grounding detection.** `[major][bergs]`. IBCSO depth against draught. This is
    the binding constraint according to 2d. Partly in progress: uncommitted code in `dakshin/berg_forecast.py` at the snapshot (2d). Not wired into any committed figure.
15. **Lock-in above 90% concentration.** `[major][model]` (Lichey and Hellmer 2001).
    The drift model has no term for it. The cheap fix (switch to the drift field
    above about 90%) is unbuilt (`docs/research/FORECAST_HORIZONS.md` §3.4, as cited
    in the backlog).
16. **Rerun the hindcast with the ECMWF wind.** The JSON still says "zero (slice 6
    pending)" (2d).
17. **Measure the p90 leave-one-out errors at 24, 48 and 72 hours.** `[minor][ml]`.
    ADR-025 names these as the exclusion radii.

### Routing claims

18. **Route-regret sweep over departure dates, with QA-suspect cells impassable.**
    `[critical][routing]` and `[critical][eval]`. One departure date is one sample (2e, 2a).
19. **Time-expanded router.** `[critical][routing]`. Designed. The single change
    that lets a forecast affect a route.
20. **Implement the 12-run sweep and report fuel relatively.** `[major][routing]`.
    ADR-021 is accepted in `docs/DECISIONS.md` but not implemented. Fuel is computed
    but never reported.
21. **Re-run the route-regret, destination-window and alternatives experiments on depth meshes.**
    The route is regenerated (`13861d9`, 8.66 days), but the experiments behind claims 1.6, 1.7 and the
    regret result were computed without depth (`docs/backlog.md`, `[major][eval]`).
22. **Confirm the day-0 route.** `478ecd2` changed the snapping rule that made day 0 hinge on one
    ice-locked node. Its commit message says the tests cover every departure day. The backlog line that
    reported day 0 as not solving was removed in `13861d9`. Not re-run in this pass.
23. **Maitri's offload point.** `[major][data]`. Unknown, so Maitri is excluded from
    the destination window.
24. **Vessel calibration.** `force_limit` is borrowed from another hull (`[major][vessel]`);
    the ice class is single-source (`[major][vessel]`); `max_ice_conc = 80` is a
    stand-in (`[major][routing]`) that POLARIS can only replace with a thickness
    output (`[major][ml]`).
25. **Mesh cell size at the station.** The cell containing Bharati spans 1.25 degrees,
    about 139 by 49 km (`[major][routing]`). The "station cell closed, approach open"
    comparison is between two neighbouring cells of that size.

### Documentation and claims hygiene

26. **Correct the claims listed in Appendix A.** Several are in the ledger itself.
27. **README rewrite for a physical oceanographer.** Queued in `docs/CURRENT_STATE.md`
    as the owner's second end-of-build ask. Not done in committed form. `README.md` was modified and uncommitted at the snapshot, so it is in progress elsewhere.

---

## Appendix A. Known inconsistencies between documents and figures

Listed, not fixed. Each entry names the files on both sides.

1. **Persistence IIEE at lead 3.** `docs/RESOLUTION_STUDY.md` gives 211.7 (10³ km²);
   `dakshin/figures/resolution_study.json` and `realforecast_hindcast.json` give
   277.2.
2. **Persistence IIEE "decays with lead".** `docs/RESOLUTION_STUDY.md` says so.
   The JSON rises with lead: 187.7, 277.2, 319.2, 353.3.
3. **"Raw CMEMS beats persistence at every lead."** `docs/TRUE_CLAIMS.md` §1.13.
   True for RMSE. Not true for IIEE at lead 1 (2b).
4. **8.6 days in the prototype results.** `docs/PROTOTYPE_RESULTS.md` now has an update note
   (`13861d9`) giving 8.66 days, but its routing section still headlines 8.58 days and §4 and §5 use
   the older figures. `docs/TRUE_CLAIMS.md` §1.11 gives 8.7 days (8.66) as re-derived.
5. **"200 km box" around Bharati.** `docs/TRUE_CLAIMS.md` §1.5 and
   `docs/PROTOTYPE_RESULTS.md` §2. The box is ±200 km, so 400 km on a side
   (`dakshin/audit_ice_quality.py`).
6. **D15A "beside Bharati's approach".** `docs/TRUE_CLAIMS.md` §1.10. The backlog
   records it at 66.63 S, 81.92 E, about 390 km from the station
   (`docs/backlog.md`, `[minor][pitch]`).
7. **Wind in the berg hindcast.** `dakshin/figures/berg_hindcast.json` says
   "zero (slice 6 pending)". `docs/CURRENT_STATE.md` says slice 6 is done.
8. **"R << 1 in every segment."** Docstring in `scripts/berg_resolution.py` and
   `dakshin/berg_forecast.py`. `berg_hindcast.json` segments give R from 0.037 to 1.73.
9. **Stationary count.** `docs/backlog.md` says "persistence 0 km on 75/88 segments".
   The segments give 75 of 88 at 3 km or less, including the 7 unknown. Exactly
   zero is 63 of the 81 usable segments.
10. **Seed and split of the re-run.** The brief says `docs/CURRENT_STATE.md`
    records an identical seed and split. It does not (2g).
11. **Test count.** `docs/CURRENT_STATE.md` gives both 186 passed (Done tonight)
    and 194 passed (Progress since). The later figure is probably current.
12. **F2 and F4 status.** `docs/backlog.md` (`[minor][features]`) says "not started".
    `docs/CURRENT_STATE.md` and the git history (`93ff026`, `7307f12`) say done.
13. **`dakshin/data` as a symlink.** `docs/backlog.md` BLOCKER and item 10 of
    `docs/audit/CORRECTIONS.md` (status OPEN, "P0") say it is a symlink into a
    sibling worktree. In this pass it is a real directory with 1,096 files
    (403 MB), and the `.gitignore` comment still describes the symlink. Either
    the fix was made without the registers being updated, or the registers are right
    and the directory listing is wrong. The first is more likely; check with `ls -la dakshin/data`.
14. **`min_depth` inert.** `docs/backlog.md` (`[major][routing]`) says the constraint
    can never fire. `docs/TRUE_CLAIMS.md` §1.17 and `docs/CURRENT_STATE.md` (slice 7)
    say the block is in both routers.
15. **Feature channel definitions.** `dakshin/features.py` docstring: channel 8 is
    `background(t) - observed(t-1)`; channels 1 to 7 are `observed(t-1)` to
    `observed(t-7)`. The code uses `background[t] - observed[t]` and
    `observed[t-lag+1]`, i.e. observations t to t-6. The docs in `docs/PROTOTYPE_RESULTS.md`
    describe the code.
16. **Checkpoint size.** `docs/DECISIONS.md` ADR-023 says weights are about 60 MB.
    `scripts/pull_checkpoints.sh` says about 8 MB each (about 32 MB for four).
17. **Checkpoint location.** `.gitignore` names `dakshin/checkpoints/` for committed
    weights. `dakshin/model_io.py` and `scripts/pull_checkpoints.sh` use
    `models/sic_correction/checkpoints/`.
18. **ADR-021 status.** `docs/DECISIONS.md` gives it no status, and the text reads
    as adopted. `docs/backlog.md` says it is designed and never implemented.
19. **Corrections register path.** `.gitignore` cites `docs/CORRECTIONS.md`. The file
    is at `docs/audit/CORRECTIONS.md`.
20. **Duplicate USNIC file.** `docs/backlog.md` says `data/icebergs/usnic_antarctic_20260902.csv`
    is byte-identical to the archived 2026-08-27 issue. Not verified in this pass.
21. **SST source.** `scripts/berg_melt.py` reads `cmems_sst_<cycle>.nc`. No script produces
    it and `ATTRIBUTION.md` does not list it (2k).
22. **Store of the prototype's numbers.** `docs/PROTOTYPE_RESULTS.md` says the figures
    are the numbers to quote. The checkpoint and output that produced them are not
    in the repository (2g).
23. **Stale backlog line on score_cmems_archive.** The backlog entry is dated
    2026-09-03. The file's git history begins 2026-11-19 (`5be27ca`).
24. **Weights, GitHub.** `docs/CURRENT_STATE.md` says commit the checkpoints and attach to
    a release; ADR-023 says weights are never synced over Iridium. Both can hold. They
    are different questions.
25. **Inputs removed during this pass.** `data/bathymetry/raw/` (the 254 MB IBCSO file) was present at 18:11 and absent at 18:21. `/home/agent/.venvs/isih-demo` was present at about 18:08 and absent at 18:27. This pass did not delete either. The cause is not identified. Anyone running the subset or demo steps should check both first.
26. **Snapshot date.** This document reads the repository between about 17:56 and 18:21 on 2026-11-21. Commits `478ecd2`, `24317da`, `f67493b` and `13861d9` reached `main` at 18:21, after the reads. Statements about the route, bathymetry, router and demo are dated to the earlier state. Appendix C lists those commits.
27. **The claims verifier tests a withdrawn figure.** `scripts/verify_claims.py` checks
    `transit days (rounded)` = 8.6 against `dakshin/figures/route_regret.json`. That file was computed without
    depth, and `docs/TRUE_CLAIMS.md` §1.11 now uses 8.66 days. The "PASSED 29" result therefore includes a
    check on the superseded figure.

---

## Appendix B. Items marked resolved, checked against the code

- F1, F3: resolution study and currents study, done (`1a81215`, `d548eff`).
- F2: NEMO-native reader, done, untested on real NEMO output (`93ff026`).
- F4: melt estimate, done, labelled as an estimate (`7307f12`).
- Slice 7 bathymetry block: `dakshin/gates.py` `chart_gate` and the router's min-depth
  check (`ce236c7`).
- Iceberg drag-coefficient swap and the lambda sign: fixed in `models/iceberg/drift.py`
  (backlog `[resolved][ml]`).
- Harvest login failure and stale cycles: rejection rule and retries (`1a00b3b`,
  `47e0ce1`).
- The "Pareto set" naming: renamed; the sweep itself is still open (see 4.20).

---

## Appendix C. Commits that reached main after this document's reads (2026-11-21, 18:21)

Listed in the order they appear in `git log`. Each is on `main`; this document was
written before they landed.

| Commit | Message (abridged) | Effect on the findings |
|---|---|---|
| `478ecd2` | Router: arrive anywhere navigable within one lattice cell of a station ashore | Changes how the router snaps the destination. The commit message says routes whose nearest node is navigable are unchanged. The commit message says the day-0 hinge is addressed; not re-run here. Affects §2e, §2f and §4 item 22. |
| `24317da` | Bathymetry to Cape Town: GEBCO_2020 north of 50 S, exact 0.05° grid over the whole sim box, 5 km shallowest buffer | Rewrites `scripts/subset_bathymetry.py` (243 lines). The subset grows from 1.36 MB to 3.50 MB. Adds the GEBCO attribution to `ATTRIBUTION.md`. Affects §2e and the runbook's data inventory. |
| `f67493b` | Demo: real seabed under the ship, chart light never PASS, decision chart gate on real route depths | Changes the demo's seabed and chart panels. Affects the synthetic-world row in §3. |
| `13861d9` | Regenerate the published route with depth in the mesh: 8.66 days, 16 km off Bharati; claim 1.11 re-derived | Replaces the 8.6-day route with 8.66 days and an endpoint 16 km off the station. Updates `docs/TRUE_CLAIMS.md` §1.11 and `docs/PROTOTYPE_RESULTS.md` (an update note at the top of its routing section). Removes the backlog line that asked for regeneration, and removes the line "GEBCO still not downloaded". Adds backlog items: re-run the three depth-free experiments; GEBCO north of 50 S from ERDDAP; `RealWorld` does not return depth. |

The `raw/` IBCSO file was absent at 18:21, the same minute that `24317da`
landed. That commit's script downloads its inputs to `data/bathymetry/raw/`. This document
does not establish whether the removal and the commit are related.

Uncommitted at the snapshot, and not in any commit: `dakshin/berg_forecast.py` (`BathymetryGrid`, assumed draught), `README.md`, and a new study file `docs/study/PHYSICS_AND_PAPERS.md` written by another agent. Later commit by another agent, on top of this document's commit: `aaddb78` (backlog inconsistencies).

**Working tree at the final commit (about 18:35 UTC).** The numbers in this document are the committed values at the snapshot. The checks above confirmed them against HEAD for `berg_hindcast.json`, `destination_window.json`, `realforecast_hindcast.json` and `real_route.json`. The working tree has since changed. `dakshin/figures/destination_window.json` reports Bharati closed on 31 of 31 days, against 23 of 31 committed (the earlier figure was ice-only). `berg_hindcast.json`, `route_regret.json`, `alternatives.json` and `vessel_comparison.json` are modified and uncommitted. A later regeneration will not match this document. Re-read the committed files before quoting.
