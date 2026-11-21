# Dakshin: physics, statistics and papers

Study document, written 2026-11-21 against the committed repository (HEAD `44e3efa` at the final check). It explains each physical or statistical concept the code uses, gives the equation exactly as implemented, says where in the code it lives, and records what the evidence in the repository does and does not show. Numbers come from repository files (paths given) or were measured while writing (marked "measured here"). Statements of general domain knowledge that the repository does not itself record are marked "outside the repository" so they are not mistaken for project findings. Pending U-Net results are marked "training re-run in progress".

Contents: 1 passive-microwave sea-ice concentration and its quality control; 2 the iceberg drift law (WDE17); 3 iceberg melt; 4 verification (RMSE, IIEE, persistence, discipline); 5 the U-Net; 6 routing; 7 ice edge, grounding and bathymetry; 8 POLARIS; 9 questions a physical oceanographer is likely to ask, with where the evidence is; 10 papers.

---

## 1. Sea-ice concentration from passive microwave, and why the quality control exists

### 1.1 The products used

| Product | Used for | Sensor | Grid |
|---|---|---|---|
| NOAA/NSIDC Sea Ice Concentration CDR, G02202 v6 (`sic_pss25_<date>_F17_v06r00.nc`) | training truth, QA audit, September-prototype routing (2018 to 2020, 1,096 files) | SSMIS on DMSP F17 | 25 km south polar stereographic, EPSG:3412, 332 x 316 |
| NOAA/NSIDC Near-Real-Time CDR, G10016 v4 (`sic_pss25_<date>_am2_icdr_v04r00.nc`) | truth for the 2026 real-forecast hindcast (2026-08-24 to 2026-11-20, 89 files) | AMSR2 (tag `am2`, since 2025-01-01 per `scripts/download_nsidc_nrt.py`) | same grid, 332 x 316 (measured here) |

The two share the grid and variable names (`cdr_seaice_conc`, `cdr_seaice_conc_qa_flag`, `cdr_seaice_conc_stdev`, interpolation flags) but not the sensor. The training truth is SSMIS; the 2026 scoring truth is AMSR2. That is a known distribution shift, carried in the caveats of `dakshin/figures/realforecast_hindcast.json` and not quantified anywhere in the repository. The flag names (`BT_weather_filter_applied`, `NT_weather_filter_applied`) show that the CDR combines the Bootstrap and NASA Team retrievals; outside the repository, the CDR concentration is built from those two algorithms, with NSIDC's weather and coastal filters applied afterwards.

The CDR is a 48-year homogeneous climate record (`docs/audit/MASTER_AUDIT.md` line 329: "built for climate records, not navigation"). Its `valid_range [0, 100]` accepts a 0 written by a coastal filter. That one property produced the finding below.

### 1.2 The QA flag, and the land-spillover zero

Bits of `cdr_seaice_conc_qa_flag` (from the file's own `flag_masks`, `dakshin/ice_quality.py`):

| Bit | Meaning |
|---|---|
| 1 | Bootstrap weather filter applied |
| 2 | NASA Team weather filter applied |
| 4 | land spillover filter applied |
| 8 | no input data |
| 16 | invalid ice mask applied |
| 32 | spatial interpolation applied |
| 64 | temporal interpolation applied |

`UNTRUSTWORTHY = 4 | 8` (spillover and no-input). Interpolation bits are kept on purpose: an interpolated value is still an estimate, and discarding them would remove most of the coastal record.

The physics. A 25 km passive-microwave footprint that overlaps land reads warm, because land emissivity resembles ice emissivity, and would be mistaken for open water or false ice depending on the algorithm; the product applies a spillover filter to coastal cells. When the filter fires it writes 0.0, not a fill value (`dakshin/ice_quality.py` docstring). Zero is inside `valid_range`, so every unguarded reader accepts it as open water. The literature, as recorded in `docs/NAVIGATION_RESEARCH.md` section 6.3, describes the uncorrected retrieval as overestimating coastal concentration (false ice) and the corrections as overshooting ("not perfect, and some false sea ice remains"; true coastal ice can also be removed; NSIDC's AMSR2 correction analyses a 7 x 7 pixel, 87.5 km neighbourhood and assumes land pixels radiate like 90% concentration). What bites a ship is the overcorrection at the cells nearest a station.

Measured consequences (`dakshin/figures/ice_quality_audit.json`, all 1,096 days of 2018 to 2020):

| Measure | Value |
|---|---|
| Days on which the spillover filter fires | 1,096 of 1,096 |
| Cells suppressed per day | mean 118.2, maximum 488 |
| No-input cells per day | mean 89.2, maximum 59,350 |
| "Hard zero flush against ice heavier than 50%" cells per day | mean 14.8, maximum 87, on 100% of days |
| Days with suspect cells in the 17 x 17 cell box (289 cells) around Bharati | 474 days, 43.2%; 4,966 suspect cell-days; worst day 2019-03-23, 38 cells |
| Same for Maitri | 262 days, 23.9%; 2,728 suspect cell-days; worst day 2020-08-28, 83 cells |

The detector in `hard_zero_next_to_ice` needs no QA flag: a physical ice edge has a gradient, so an exact zero touching (4-neighbourhood) a cell above 50% is an artefact. It was how the problem was first noticed, and works on products that ship no flags.

Case, measured here with `ice_quality.load_sic` on `sic_pss25_20191201_F17_v06r00.nc`: the Bharati grid cell (row 152, column 245) reads 0.0 with `apply_qa=False` and NaN with `apply_qa=True`; 112 cells on that day carry the spillover bit. The same case is quoted in `docs/PROTOTYPE_RESULTS.md` section 2: on 1 December 2019 the cell 35 km off Bharati reads 0.0 beside cells at 0.60 and three days later 0.90.

What it did to results (`docs/PROTOTYPE_RESULTS.md` section 2, `dakshin/figures/destination_window.json`, 31 days of December 2019, 80% working limit):

| Quantity | Value |
|---|---|
| Bharati's own cell, days closed | 23 of 31 (74.2%) |
| Approach point 100 km north, days closed | 0 of 31 |
| Days Bharati looked open | 8; four of them (1, 7, 8, 9 December) read exactly 0.0 raw (30.7, 33.7, 35.2, 36.3% after QA masking and parent-cell fill) |
| The other four open days (21, 29, 30, 31 December) | 80.0, 77, 79, 75%, at or just under the 80% limit, which is itself a working number |
| Mean SIC in the 200 km box around Bharati, raw to QA-masked | 46.8 to 54.6% (1 Dec 2019); 62.5 to 65.4% (10 Dec 2019) |

Masking makes the coast look heavier, so the router becomes more cautious, which is the safe direction. The stated residual: meshiphi's parent-cell fill still gives 30 to 36% on artefact days when the surroundings suggest 80 to 95%. The fix removes a confident wrong answer; it does not provide a confident right one. The recorded next step is to treat suspect cells as unknown and therefore high-risk rather than filling them.

The one place the QA mask is not applied is the training pipeline: the Kaggle notebook only maps out-of-range values to NaN, so spillover zeros are in the training targets and history channels, concentrated at the coast. The hindcast, by contrast, uses `load_sic` and masks them. So the model is evaluated on a truth that differs from the truth it was trained on, at the coast. The effect has not been measured.

### 1.3 Other known error sources recorded in the repository

From `docs/NAVIGATION_RESEARCH.md` section 6 (quoted as findings of the cited papers, not of this project):

- All algorithms underestimate concentration for ice thinner than about 25 cm and most keep about 5% negative bias above 30 cm (Ivanova et al. 2015). New and young ice, the ice a ship can break, is the ice the sensor is worst at.
- Weather filters delete real low-concentration ice: gradient-ratio filters wrongly zero 27% of pixels at a true 15% concentration and 9% at 20% (Ivanova et al. 2015). The marginal ice zone is where products are most aggressively censored.
- The between-algorithm spread is the honest error bar: in the 30-algorithm round robin the standard deviation at 15% concentration ranges from 2.8% (6H) through 5.4% (NASA Team), 13.5% (Bootstrap-P) to 28.5 to 28.8% (ASI, N90), the Northern Hemisphere values in the table of section 6.5. `docs/TRUE_CLAIMS.md` summarises this as about ten times more disagreement at the edge than in thick pack.
- The OSI SAF per-pixel uncertainty excludes melt-pond, thin-ice and weather-filter effects (Lavergne et al. 2019, as cited), so what ships is a precision estimate, not a total error budget.
- Against ship observations (Ozsoy-Cicek et al. 2009, as cited): R-squared 0.41, ice edge placed 38 to 102 km too far south by AMSR-E, area inside the edge underestimated by up to 14%. Antarctic summer surfaces are dominated by thick snow, flooding and snow-ice formation rather than melt ponds. Edge position from 25 km passive microwave can be off by 25 to 50 km (NSIDC, as cited).
- `cdr_seaice_conc_stdev` is a free per-pixel retrieval standard deviation, read by `ice_quality.load_stdev`. It is used to set the ice gate's MARGINAL band (section 8), and is otherwise unused in the model.

### 1.4 AMSR2 versus SSMIS, stated plainly

The 12.5 km AMSR2 product was reassigned in ADR-019 from a candidate model input to an independent second observation source for a disagreement layer (designed, not built), because feeding it to the network would destroy the independence the disagreement signal depends on. In the hindcast the sensor change is real and enters through the truth: the NRT G10016 v4 is AMSR2-based and the training truth is SSMIS-based. The model has never seen AMSR2-era statistics in training, and no experiment isolates the effect. A reader should treat the hindcast as measuring forecast skill plus a sensor-transfer penalty that is not separable with the data held.

---

## 2. Iceberg drift: Wagner, Dell and Eisenman (2017)

### 2.1 What the law says

WDE17 (J. Phys. Oceanogr. 47(7), 1605 to 1616; arXiv:1610.06403; reference MATLAB at tillwagner.me/wde17) starts from the momentum balance of a cuboid iceberg (`docs/ICEBERG_RESEARCH.md` section b.1):

M dv_i/dt = -M f k x v_i + F_w + F_a + F_p + F_r + F_i

with Coriolis, water form drag, air form drag, pressure gradient, wave radiation and sea-ice drag. Five assumptions reduce it to algebra: (1) negligible acceleration; (2) pressure gradient from the ocean velocity under geostrophy, F_p = M f k x v_w; (3) |v_i| much smaller than |v_a|, so v_a - v_i is approximately v_a (about 10 m/s against 0.1 m/s); (4) sea-ice drag and wave radiation dropped; (5) water drag dominated by the surface current, with no vertical shear over the draught. Drag acts on vertical faces only and is averaged over a random orientation. Berg height cancels exactly because drag and Coriolis both scale linearly with it, so geometry enters only through the harmonic length S = LW/(L+W).

Result, as implemented in `models/iceberg/drift.py::iceberg_velocity` (velocities east and north, m/s):

```
gamma  = sqrt( rho_a (rho_w - rho_i) / (rho_w rho_i) * C_a / C_w )        = 0.018747   (measured here)
f      = 2 Omega sin|lat|
S      = L W / (L + W)
Lambda = gamma C_w |v_a| / (pi |f| S)
alpha  = 2 Lambda / (1 + sqrt(1 + 4 Lambda^4))
beta   = sqrt(2) Lambda^3 / sqrt( (1 + x) sqrt(1 + 4x) + 1 + 3x ),  x = Lambda^4
u_i = u_w + gamma ( s alpha v_a + beta u_a )
v_i = v_w + gamma ( -s alpha u_a + beta v_a )
s   = -1 south of the equator (flip on), +1 north;  s = +1 if the flip is switched off
```

Constants are verbatim from the reference MATLAB: Omega = 7.2921e-5 rad/s, rho_a = 1.2, rho_w = 1027, rho_i = 850 kg/m3 (shelf ice, Silva et al. 2006), C_a = 1.3, C_w = 0.9. In words: the berg moves with the surface current plus a wind-driven correction that is partly along the wind (beta) and partly across it (alpha); Lambda is the single number deciding the regime. Lambda much greater than 1 gives drift along the wind (the old "2% of wind" rule is the Lambda >> 1 limit); Lambda much less than 1 gives drift at right angles to the wind, with magnitude Lambda. Asymptotes (series-expanded and checked numerically in `docs/ICEBERG_RESEARCH.md`): alpha tends to Lambda and beta to Lambda cubed as Lambda tends to 0; alpha to 1/Lambda and beta to 1 as Lambda tends to infinity. At Lambda = 1, alpha = 0.6180 and beta = 0.4859, the deflection arctan(alpha/beta) = 51.83 degrees (measured here; the docstrings of `drift.py` say "45 degrees", which is where the asymptotes cross, not the value at Lambda = 1).

The deflection angle is atan2(alpha, beta). The critical length at which Lambda = 1 is `critical_length_m`: S* = gamma C_w |v_a| / (pi |f|), L* = S* (1 + aspect). With |v_a| = 5.7 m/s, f = 1e-4 s-1 (latitude 43.29 degrees) and aspect 1.5 it returns 765.3 m, reproducing the paper's own 765 m (measured here; asserted in `models/iceberg/test_drift.py`, 23 tests).

### 2.2 Three implementation traps (all asserted in tests)

1. The drag coefficients are swapped in the arXiv preprint text, which says C_a = 0.9 and C_w = 1.3. The reference MATLAB says the opposite, and only the code's assignment reproduces the paper's own gamma = 0.018 and L* = 765 m. Because gamma goes as sqrt(C_a/C_w), the text's assignment would put gamma 44% low. The code uses C_a = 1.3 (air) and C_w = 0.9 (water). `GAMMA` evaluates to 0.01875; the paper quotes 0.018.
2. Lambda must use |f|. Eq. (9) prints f; with signed Southern Hemisphere f, Lambda is negative, beta is negative, and the along-wind term points backwards. It looks like a plausible drift, just the wrong way.
3. Alpha and beta as printed lose all precision at small Lambda. Every USNIC-tracked berg sits at Lambda below 0.07. The printed alpha, (1 - sqrt(1+4L^4)) / (2 L^3), is a difference of nearly equal numbers; the printed beta bracket decays as 2 L^12 and goes negative in float64 (NaN). Both are rewritten algebraically exactly (using sqrt(1+x) - 1 = x/(sqrt(1+x)+1) and the conjugate for beta), so no clipping or asymptotic switch is needed. The printed alpha is also negative; the code follows the MATLAB, uses the positive form and carries the sign in the velocity assembly.

### 2.3 The Southern Hemisphere deflection subtlety

The reference MATLAB takes sin|lat| and assembles the velocity with a fixed clockwise rotation, i.e. right-of-wind deflection at every latitude, because the paper's quantitative sections are Arctic. In the Southern Hemisphere the Coriolis sign reverses and the wind-driven component should deflect to the left. `iceberg_velocity(..., southern_hemisphere_flip=True)` flips the sign of alpha's contribution south of the equator. The repository marks the flip as inferred from the Coriolis sign in WDE17 eqs. (3) to (5) and unverified against observations; set `southern_hemisphere_flip=False` to reproduce the reference code exactly. Two consequences worth stating. For the giants USNIC tracks the wind term is small and the flip hardly matters. And since `forecast_track` sets wind to zero, the flip is not exercised at all in any hindcast number in this repository.

### 2.4 The relative wind forcing R, and why giants are current-driven

WDE17 eq. (14), `relative_wind_forcing`:

R = gamma sqrt(alpha^2 + beta^2) |v_a| / |v_w|

R above 1: wind-dominated. R below 0.1: current-dominated, the berg effectively moves with the current and v_i = v_w. WDE17's own conclusion (quoted in `docs/ICEBERG_RESEARCH.md` section b.6) is that for large tabular bergs the wind drag can be assumed negligible, becoming negligible (R below 0.1) for bergs larger than about 12 km. The regime table in that file, computed at 65 S with a 10 m/s wind and a 0.1 m/s current: a 70 x 40 km A23A-class giant has Lambda 0.0160 and R 0.030; the USNIC minimum, 18.5 x 9.3 km, Lambda 0.0658 and R 0.123; a 1000 x 600 m berg Lambda 1.08 and R 1.52; a 200 x 120 m bergy bit Lambda 5.42 and R 1.86. A consequence the repository draws: the 2% wind rule is wrong for exactly the bergs the catalogue contains (a 20 km berg would need a 200 m/s wind for Lambda >> 1), and forecast skill for the catalogue is inherited from the ocean-current product, not the drag coefficients.

That is the sharp version. The weaker, measured version is what the repository actually shows. R scales as 1/|v_w|, so it depends on the assumed wind and the local current. `models/iceberg/regime_report.json` sweeps wind (5, 10, 20, 30 m/s) against current (0.05, 0.1, 0.3 m/s) for the real 33-berg catalogue:

| Wind (m/s) | Current (m/s) | Median R | Maximum R | Bergs with R above 1 | Bergs with R below 0.1 |
|---|---|---|---|---|---|
| 5 | 0.05 | 0.0481 | 0.1202 | 0 | 32 |
| 10 | 0.1 | 0.0963 | 0.2404 | 0 | 20 |
| 10 | 0.05 | 0.1926 | 0.4808 | 0 | 4 |
| 20 | 0.05 | 0.7703 | 1.9193 | 9 | 0 |
| 30 | 0.05 | 1.7328 | 4.2821 | 28 | 0 |

So "current-dominated" holds in moderate winds over typical currents and fails in a 20 to 30 m/s storm over a weak current, which is an ordinary Southern Ocean event. And in the 88 USNIC segments of the hindcast, the per-segment R (assumed 10 m/s wind, the model's current speed at the berg) has median 0.25, range 0.037 to 1.73 (measured here from `dakshin/figures/berg_hindcast.json`), with 81 of 88 above 0.1. The text in `dakshin/berg_forecast.py` ("about 1% of drift") and `scripts/berg_resolution.py` ("R << 1 in every segment") is therefore too strong. Because R is a ratio to the current, a grounded berg in a region of weak modelled current gets a large R without there being much wind-driven motion in absolute terms.

What the wind-free forecast leaves out, quantified with the repository's own numbers: the neglected term has magnitude gamma sqrt(alpha^2+beta^2) |v_a|, which is R |v_w|, so it is of order 25% of the current speed (median R 0.25) in this sample. Wind is not yet wired into `forecast_track` (the argument is hard-coded to 0.0 inside `_step_velocity`), although a 10 m/s IFS wind archive now exists for one cycle.

### 2.5 Integration and the Lagrangian choices

`dakshin/berg_forecast.py`: positions advance by a midpoint (RK2) step of one hour. k1 is evaluated at the current position and time; the berg is moved half a step; k2 is evaluated at that midpoint and mid-time; the full step uses k2. Velocity at a point is WDE17 with the interpolated daily-mean surface current as v_w. Currents are bilinear in space over the four surrounding cells (NaN if any is NaN), linear in time between daily means, each taken as valid at 12:00 UTC, and held at the nearest day outside the first and last centres. A NaN current stops the berg and labels it "grounded or unknown".

What this does not model (all read from the code): no stochastic diffusion or ensemble, so no spread beyond the single track; no berg-berg or berg-coast interaction other than stopping at NaN; no sea-ice drag or locked-in regime (WDE17 assumption 4; for icebergs embedded in pack ice the repository points to Lichey and Hellmer 2001 and Hunke and Comeau 2011 and marks their treatment unverified); no change of berg size during the run (melt is a separate estimate); no vertical current shear over the draught (WDE17 assumption 5). The daily-mean surface current at 0.494 m is a proxy for the depth-averaged flow acting on a draught of order hundreds of metres, a limitation the repository never tests (this is a reading of the assumptions, not a finding recorded in the repository).

### 2.6 What validation shows

88 weekly USNIC fix pairs, 8 bergs, 2026-08-31 to 2026-11-20 (`dakshin/figures/berg_hindcast.json`). Errors are the distance between the integrated landing point and the later fix, divided by the interval in days.

| Quantity | Model | Persistence |
|---|---|---|
| Median error, 81 ok segments (km/day) | 4.35 | 0.0 |
| Mean error, 81 ok segments (km/day) | 5.06 | 0.43 |
| Moving segments (persistence displacement above 3 km), 13 of them: median (km/day) | 6.01 | 2.45 |
| Stationary segments, 68: model median (km/day) | 4.26 | |
| Segments stopped as "grounded or unknown" | 7 | |

Interpretation recorded in the repository: most corridor giants are grounded, and a current-advection model without grounding detection advects anchored ice, so it loses to "does not move". On the moving sample persistence also wins at weekly fix cadence. USNIC positions are accurate only to a few km and weekly fixes mix model error with fix timing; errors are not independent (successive intervals of one berg). For context, `docs/ICEBERG_RESEARCH.md` section c.2 records IDRIFTNET (arXiv:2507.00036) on A23A and B22A: displacement errors of 49.06 and 22.87 km (ADE) with a learned residual against 147.10 and 127.23 km for WDE17 alone, with a horizon the paper does not state; do not compare with the km/day figures here, and the same file notes WDE17 itself reports no quantitative skill score. The hindcast has no accuracy claim beyond the segment errors above; the "forecast cone grows at 4.35 km/day" rule is the median, not an upper bound.

Coarsening the currents (F3, `dakshin/figures/berg_resolution.json`): median error 4.35 (1/12 degree, 81 ok, 7 flagged), 4.07 (1/4 degree, 86 ok, 2 flagged), 3.49 km/day (1 degree, 88 ok, 0 flagged); on moving bergs 6.01, 5.93, 5.06. Coarser is better because smoothing suppresses the velocities that advect anchored bergs; it is not evidence that eddies are unimportant. Block-averaging a model's output is not running a coarser model.

---

## 3. Iceberg melt (an estimate, labelled as one)

### 3.1 Terms as implemented (`models/iceberg/melt.py`)

Three deterioration terms, in metres per day, following the set Keghouche et al. assembled for the Barents Sea (the repository cites the paper two ways, see the papers list):

```
Mb = 0.58 |v_w - v_i|^0.8 (T_w - T_f) / L^0.2           basal turbulent melt  (El-Tahan et al. 1987; Weeks and Campbell 1973)
Mv = 7.62e-3 T_w + 1.29e-3 T_w^2                         buoyant convection    (Bigg et al. 1997)
Me = (1/12) Ss (T_w + 2),  Ss = -5 + sqrt(32 + 2 Hs)     wave erosion          (Gladstone et al. 2001; Bigg et al. 1997)
```

T_w sea-surface temperature in degrees C, T_f = -1.92 C (freezing point at salinity about 34.5), v in m/s, L waterline length in m, Hs significant wave height in m. Negative temperature differences are clipped to zero (`np.maximum`). Bulk freshwater input in m3/day:

```
V = Mb * (L W)  +  (Mv + Me) * 2 (L + W) * (0.83 * h)
```

with h the thickness, assumed 250 m because USNIC publishes none, and 0.83 the submerged fraction by Archimedes (rho_i / rho_w). The wall terms act on the submerged perimeter, the basal term on the base area. Berg size is not updated along the track.

### 3.2 Differences from the WDE17 appendix, and from the call site

`docs/ICEBERG_RESEARCH.md` section b.8 transcribes WDE17's appendix (A1): Me = 0.5 Ss with Ss the Douglas sea state, itself parameterised from the wind-water relative speed (Martin and Adcroft 2010), i.e. Me = 0.75 |dv|^0.5 + 0.05 |dv|; the same Mb and Mv constants (0.58, 0.0076, 0.0013); and an iceberg temperature T_i = -4 C (El-Tahan et al. 1987) rather than the freezing point in the basal term. The repository's `melt.py` uses an Hs-based sea state, a temperature factor (T_w + 2) on wave erosion, and T_f in the basal term. These are different parameterisations of the same terms, not an error in either, but they should not be presented as WDE17's.

Two observations from reading the call site (`scripts/berg_melt.py`) and measured here with `melt.py`:

- The `rel_speed` argument is documented as the water-relative speed |v_w - v_i|, but the script passes the absolute current speed `hypot(u, v)`. For a giant that moves with the current, |v_w - v_i| is close to zero, so the proper basal term would be much smaller. For D37 (55.56 x 12.96 km) at T_w = -1.77 C, the basal term contributes 0.31, 0.64, 1.12 and 1.94 million m3/day at 0.02, 0.05, 0.1 and 0.2 m/s respectively, so the choice matters.
- With Hs = 0 the sea-state proxy is -5 + sqrt(32) = 0.657, so the wave-erosion term is not zero in a calm sea (0.0126 m/day at T_w = -1.77 C, about 0.36 million m3/day for D37). In the run, 72 of 80 daily Hs values are exactly 0 (waves are damped under ice and set to 0 when the cell is NaN) and the maximum is 0.64 m; SST ranges from -1.84 to -1.32 C. So the reported freshwater numbers are dominated by the basal term and this Hs = 0 floor.

### 3.3 The stated caveats, which every output must carry

The coefficients were tuned for Arctic bergs orders of magnitude smaller than USNIC giants; applying them to a 50 km tabular berg extrapolates far outside the calibration. Keel draught and thickness are unpublished. The result is a bulk estimate of freshwater input, not a deterioration forecast. `dakshin/figures/berg_melt.json` carries the label "ESTIMATE ... Arctic-calibrated ... assumed thickness 250 m". Results for the 2026-11-21 cycle: mean daily freshwater per berg from 157,451 m3/day (C18C, 53.07 km2) to 1,913,104 m3/day (D15C, 115.03 km2); D37 (477.77 km2) 1,001,936. `ATTRIBUTION.md` still says the melt terms are "noted as future work"; they are implemented.

---

## 4. Verification

### 4.1 RMSE, IIEE and the double penalty

Pooled RMSE (`features.rmse`, and the pooled form in `scripts/realforecast_hindcast.py`): square root of the total squared error over all valid cells and all cycles divided by the total cell count. Zero-fill convention: fields are zero-filled where NaN and the mask removes cells where forecast or truth is not finite.

Integrated Ice-Edge Error (Goessling et al. 2016, as cited in `features.py`): the area where the forecast and the observed ice-extent masks, thresholded at 15% concentration, disagree. `features.iiee_km2`:

```
IIEE = sum over valid cells of 625 km2 * [ (pred >= 0.15) XOR (truth >= 0.15) ]
```

which equals overestimated extent plus underestimated extent. Because the two partial errors can cancel in the net extent but not in IIEE, IIEE is at least the absolute extent error. It measures where the edge is, which is what passage planning needs.

The double penalty. A forecast that places a sharp feature in the wrong position is penalised twice by a squared-error score: once for the miss where the truth is and once for the false alarm where the forecast put it. A smoothed forecast spreads the error thinly and pays less. Illustrative arithmetic, not from the repository: truth is a box of height 1 and width 1; a sharp forecast displaced by more than its width has squared error 1 + 1 = 2; a mass-preserving blur to 1/3 over a width of 3 scores (2/3)^2 * 1 + (1/3)^2 * 2 = 0.667. RMSE therefore flatters blur.

What the resolution study showed (`dakshin/figures/resolution_study.json`, 76 cycles at lead 1, 2026-08-31 to 2026-11-18; the same forecasts block-averaged by 3 and 12 in each direction, repeated back to the native grid, scored on identical cells against the same NRT truth):

| Lead | RMSE 1/12 deg | RMSE 1/4 deg | RMSE 1 deg | Persistence RMSE | IIEE 1/12 deg (km2) | IIEE 1/4 deg | IIEE 1 deg | Persistence IIEE |
|---|---|---|---|---|---|---|---|---|
| 1 d | 0.10199 | 0.10035 | 0.10402 | 0.11977 | 195,058 | 189,688 | 203,298 | 187,706 |
| 3 d | 0.10479 | 0.10314 | 0.10598 | 0.14391 | 194,575 | 190,342 | 209,325 | 277,167 |
| 5 d | 0.10981 | 0.10816 | 0.10988 | 0.15508 | 200,203 | 197,652 | 222,652 | 319,189 |
| 7 d | 0.11530 | 0.11365 | 0.11417 | 0.16414 | 210,200 | 208,333 | 244,175 | 353,255 |
| U-Net, each resolution | training re-run in progress | | | | | | | |

Reading it. RMSE cannot see resolution: coarsening to 1/4 degree improves it slightly, 1 degree roughly ties. IIEE separates them: 1 degree is worse than 1/12 degree by 4.2% at lead 1 growing to 16.2% at lead 7 (33,975 km2). 1/4 degree is not distinguishable from, and by about 1 to 3% slightly better than, 1/12 degree on both metrics in this corridor and season. `docs/RESOLUTION_STUDY.md` states the correct caveat: coarsening one model's output is not running a coarser model, because the physics that shaped the mean was resolved at 1/12 degree. A true test needs the same model run at several resolutions, which is what the NEMO reader is for.

Four limits that bear on how far to push it: no confidence interval or significance test appears in any result file; daily forecasts from consecutive cycles are strongly correlated, so 76 cycles is far fewer independent samples; one spring season; and at lead 1 persistence has lower IIEE than every forecast resolution (187,706 against 189,688 to 203,298 km2), so the "forecast beats persistence at every lead" statement is true for RMSE, not for IIEE at 1 day. The persistence IIEE entries printed in `docs/RESOLUTION_STUDY.md` (211.7 at lead 3, dashes after) disagree with the JSON above; the JSON is the source.

### 4.2 Persistence, the baseline that matters

Persistence carries the newest observed concentration forward unchanged. It is free, it is very hard to beat at short lead (full-year 2020: 0.0359 at 1 day for same-day, so same-day correction of a background is not a real task, `dakshin/features.py`), and it degrades with lead, which is why a model's value lives at multi-day lead. The prototype's test slice is the melt season where persistence is worse than over the full year: 0.0570, 0.0958, 0.1204, 0.1395 at 1, 3, 5, 7 days against full-year 0.0610 (3 d) and 0.0893 (7 d). Never mix the two periods; `docs/PROTOTYPE_RESULTS.md` warns that quoting the full-year 0.0893 beside the model's 0.0968 would falsely suggest persistence wins at 7 days.

### 4.3 Why discipline about scoring once exists

An earlier run reported +27% over persistence by choosing the best of 30 epochs on the same set it then reported. That was selection on the test set and the number is withdrawn. The current protocol: train 70%, validation 15% to choose the epoch, test 15% scored once, baselines computed before training so the bar is fixed first. The hindcast script states "scored once, reported as it comes out, no re-tuning on this set, ever". Time ordering rather than random splitting is non-negotiable for autocorrelated fields. A residual weakness: no embargo gap between the blocks and a final-epoch checkpoint chosen on validation, which is optimistically biased (validation beats test at every lead in the training results, for example lead 3: 0.0611 against 0.0720).

### 4.4 The honest limits of the headline training result

The training-time table (`docs/PROTOTYPE_RESULTS.md`, model beats persistence by +18.5% at 1 day to +30.6% at 7 days) used a reanalysis background that has assimilated the target date. Raw GLORYS12 scores 0.1630 at lead 1 and 0.1637 at lead 7, essentially flat; a real forecast degrades with lead. The correct reading, from that file, is an upper bound on forecast skill, with the defence that 0.163 is mere bias withdrawn. The real-forecast scoring is the hindcast; the U-Net rows are training re-run in progress, and the no-background ablation has not been run.

---

## 5. The U-Net

### 5.1 Formulation and why it is a residual

`models/sic_correction/unet.py`: corrected = clip(background + delta, 0, 1), where delta is the network output (unbounded, in concentration-fraction units). The head is a 1 x 1 convolution whose weights and bias are zero-initialised, so an untrained network reproduces the background exactly. Three reasons recorded in the design (`docs/ML_ARCHITECTURE.md` section 1.1): the floor of the correction is the background's skill, not zero; the explicit innovation channel anchors the correction to how wrong the field is now at this cell; and a correction needs far less capacity than a forecaster. Clipping is applied to the sum, because it is the sum that must land in [0, 1].

### 5.2 Structure

Three encoder levels with `ConvBlock` = two 3 x 3 convolutions each followed by batch-norm and ReLU, no bias, at widths 32, 64 and 128 (base filters 32 doubled per level), 2 x 2 max-pooling between levels, a bottleneck at 256, three transposed-convolution upsamples with skip concatenations and decoder blocks, and the 1 x 1 head. Padding is replicate to a multiple of 2^depth = 8, then cropped back (332 x 316 becomes 336 x 320). Parameters, measured here: 1,929,601 at 12 channels, base 32, depth 3 (the prototype, quoted in `docs/PROTOTYPE_RESULTS.md`); 1,931,617 at 19 channels, base 32; 3,015,481 at the module defaults (19 channels, base 40), the production design. `ML_ARCHITECTURE.md` pairs "16 base filters" with "about 2 to 4 million parameters", which are inconsistent (16 filters gives 485,041); the code's docstring records this.

### 5.3 Channels and the innovation channel

The 12 prototype channels (`features.build_channels`): background at the target time, observations at `t, t-1, ..., t-6`, innovation `background[t] - observed[t]`, sine and cosine of the target day of year, and a validity mask. Version 1 of the model saw only the background field, no observations, scored 0.1051 and lost badly to persistence; giving it the newest observations and the innovation is what closed that gap (`docs/PROTOTYPE_RESULTS.md`). The production design adds ERA5 wind and 2 m temperature, OISST, a lead channel and a QC-flag channel for 19 inputs (`ML_ARCHITECTURE.md` section 1.2); none of those exist in the prototype, so the drivers of ice motion (wind, ocean heat) are invisible to it. The stated next steps are wind valid at `t`, not `t + lead`, to avoid a second leak (ERA5 2 m temperature is close to a function of the prescribed sea-ice lower boundary at the target date), and a wind-advected first guess: semi-Lagrangian advection of the ice at `t` by the free-drift rule (about 2% of the 10 m wind, deflected left in the Southern Hemisphere, to be verified against Thorndike and Colony 1982 and, per the repository, Nansen's rule against the near-surface wind).

### 5.4 Why same-day correction is not a real task

Persistence from yesterday's satellite scores 0.0359 for today's field in full-year 2020. A model correcting a background field cannot beat a near-perfect free baseline for the present time. The task is the multi-day lead, hence leads 1, 3, 5, 7, and baselines scored at the same lead.

### 5.5 Calibration

Not built. ADR-020 designs a stratified split-conformal upper bound, `SIC_upper = clip(mu + q(lead, regime) * sigma, 0, 1)` over 30 strata (leads 1 to 10, open water, marginal ice zone, pack), with a pre-committed pass gate (MIZ coverage at lead 5 between 85% and 96%, mean bound width below 25 SIC-%, calibrated sigma beating inter-source disagreement). It replaces the earlier mean plus 1.28 sigma, which assumed Gaussian errors on a variable bounded in [0, 1]. Nothing in the repository has been fitted or scored against that gate. The recorded riskiest assumption is exchangeability between calibration residuals and operations across the post-2016 regime shift.

---

## 6. Routing

### 6.1 Dijkstra with arrival-time costs (`dakshin/sim/router.py`)

Graph: regular lat/lon lattice (default 0.55 by 0.9 degrees), 8-neighbourhood so tracks run diagonally. A node is blocked if on land (`on_land`, even-odd ray casting over the committed coastline) or if the IBCSO/GEBCO depth is below the vessel minimum (20 m). Edge cost to a neighbour n:

```
hours = d_km / (v * 1.852),    d_km = haversine,    v = speed_kn(sic_n, hs_n)
step  = hours  (objective "time")   or   burn = fuel_t_per_km(v, sic_n, hs_n) * d_km  (objective "fuel")
```

with `sic_n` and `hs_n` taken at the destination node at the 6-hour slot corresponding to the time the ship reaches the current node. A neighbour with sic above the ice limit is skipped (a hard constraint, never priced). The goal is any navigable node within one lattice diagonal of the destination when the nearest node is blocked, because stations sit ashore and the 0.55 by 0.9 degree lattice cannot resolve the coast; the result reports `arrival_offset_km`.

Why the arrival time matters: a forecast is useless to a router that cannot ask what conditions will be when the ship gets there; PolarRoute meets day-zero ice on day nine.

Properties worth knowing before being asked (readings of the code, not claims made in the repository): ordinary Dijkstra is exact for time-dependent costs only when waiting is never beneficial (the first-in-first-out property). Here conditions change per slot and there is no waiting action, so the guarantee is not proven; the router keeps one label per node. Under the fuel objective the arrival time used to look up conditions is that of the cheapest-fuel path to each node, which is not necessarily the fastest, so the fuel result is an approximation of the time-dependent optimum. Conditions are read at the destination node, not integrated along the edge. Slots are quantised to 6 hours.

### 6.2 Time versus fuel, and the per-distance design

The vessel model (`VesselModel`) derates speed by ice and sea state: v_ice = v_max (1 - 0.92 (sic/limit)^1.35), times a voluntary sea-state factor 1 - 0.45 clip((Hs - 4)/5, 0, 1), floored at 2 kn, zero above the limit; defaults 16.4 kn, limit 0.80. The ice exponent slightly above linear reflects resistance climbing faster than concentration.

The docstring explains the trap. Expressed per hour, a burn that is cubic in speed makes slow cells cheap, so a fuel search happily crawls through a storm. Expressed per kilometre, one power of speed divides out and three independent resistances remain: calm water proportional to v^2, ice proportional to sic^1.5, added wave resistance proportional to Hs^2. Coefficients `0.000120 v^2 + 0.0200 sic^1.5 + 0.00035 Hs^2` tonnes per km, scaled so a calm 16.4 kn passage burns about 24 t/day, which is the right order for a ship of this size; the absolute value needs the hull's own power curve, which is not public, so fuel is reported as relative only (ADR-012). The aim was to restore a genuine trade-off: in the PolarRoute configuration, with zero currents and a dead wave-resistance function, fuel was a monotone function of time and solving for either returned a byte-identical path (`dakshin/alternatives.py` finding 1). Here a time-optimal track drives through weather and a fuel-optimal one goes round it. The model is a derating curve, not a hull performance model.

### 6.3 `critical_ice_limit`

Since 80% is an assumption, the honest daily output is the concentration limit at which the destination stops being reachable. `critical_ice_limit` solves at limits 0.85 down to 0.30 in steps and returns the last limit that works and the first that fails.

### 6.4 PolarRoute

For the prototype corridors: PolarRoute 1.1.11 with meshiphi 2.3.1 (BAS, MIT). It builds a non-uniform mesh from scalar data through `scalar_csv`, applies a vessel performance model (`SDA`: speed derated by ice resistance from thickness and density, with an inaccessibility rule), runs Dijkstra over cell crossings, then a physics-informed smoothing. Verified by source reading (`docs/NAVIGATION_RESEARCH.md`, `docs/backlog.md`): the planner has no time dimension, `wave_resistance()` is defined and never called, and the fuel polynomial is fitted to RRS Sir David Attenborough. Ice thickness and density come from a literature look-up table inside meshiphi (ADR-013); without them the ice-resistance speed adjustment silently does nothing. `force_limit` 96,634.5 is carried over from the Attenborough configuration and is uncalibrated; `max_ice_conc` 80 is a working threshold, not derived from the ice class (RS notation KM(*) ULA, whose modern equivalent is not sourced).

---

## 7. Ice edge, grounding and bathymetry

The ice edge here is the 15% concentration contour of a 25 km product. Edge position from 25 km passive microwave can be off by 25 to 50 km (NSIDC, as quoted in `docs/NAVIGATION_RESEARCH.md`), and a lead narrower than a cell cannot be seen, so the system routes to regions where leads are likely, never to a lead. The 25 km field cannot resolve a navigable lead and no product anywhere forecasts Antarctic ice compression (`docs/TRUE_CLAIMS.md` 2.5). The two quantities that decide what a ship can do, thickness and pressure, are exactly the ones the data do not carry. The repository notes that Hibler (1979) ice strength P = P* h exp[-C(1 - A)] with P* = 27,500 N/m2 and C = 20 makes dP/P = 20 dA, so a 5-point concentration error changes modelled strength by 2.7 times and a 10-point error by 7.4 times; any compression layer built on a 25 km product inherits that amplification, which is why no compression number ships without an error bar.

Grounding. The F3 finding is that grounding detection, not current resolution, is the first-order constraint on drift forecasts in this corridor: most giants are anchored, and a forecast that advects them is wrong by construction. `models/iceberg/` has no draught or grounding model in committed code; USNIC publishes no keel depth. The repository notes the missing capability and that IBCSO makes a bathymetry-and-draught check possible. An uncommitted working-tree change to `dakshin/berg_forecast.py` begins to add one (an assumed 0.83 x 250 m = 207 m draught compared against the bathymetry subset); it was not reviewed or run for this document. In the router, `NaN` current stops a berg and marks it "grounded or unknown", which is an absence-of-data stop, not a grounding physics.

Bathymetry: IBCSO v2 (Dorschel et al. 2022, Scientific Data 9, 275; dataset DOI 10.1594/PANGAEA.937574; CC-BY-4.0) south of 50 S, GEBCO_2020 north of it (public domain), box-reduced to 0.05 degrees by `scripts/subset_bathymetry.py`. Two choices matter. The ice-surface grid is used rather than the bed grid: over open water the two are the same seafloor, but under an ice shelf the bed grid gives the seafloor beneath the ice, which would read as hundreds of metres of water a ship cannot enter; the ice-surface grid gives the top of the shelf as positive elevation, so shelves block the router like land. And aggregation errs toward shallow: each box holds the shallowest source value in it and its eight neighbours (about a 5 km buffer), because a mean over the 20 to 150 source cells in a box hides exactly the shoal that matters, and because PolarRoute assigns each box to one cell by its centre, so a dry box on a cell edge had been invisible to the neighbouring cell (the regenerated Bharati route had ended in such a box, 2.9 km from the station).

Why the chart gate can never pass: IBCSO is a scientific compilation, not an official ENC; about 24% of the seafloor south of 50 S is actually surveyed (`dakshin/gates.py::chart_gate`); and the product's own caveat is that it is not to be used for navigation. The gate FAILs when any route point is shallower than the vessel's 20 m minimum and otherwise returns MARGINAL, never PASS (`dakshin/gates.py`, tests in `dakshin/test_gates.py`). The stated depth margin policy in ADR-026 (20 m in surveyed cells, the larger of 50 m and three times draught in predicted cells) is designed, not built.

The route-end finding: IBCSO places Bharati station above sea level, so the original 8.6-day route ended on land and the figure was withdrawn; the regenerated published route is 8.66 days, ending 16 km off the station with minimum depth 89 m (`docs/TRUE_CLAIMS.md` claim 1.11).

---

## 8. POLARIS and the working ice limit

IMO MSC.1/Circ.1519 (POLARIS), as extracted in `docs/NAVIGATION_RESEARCH.md` and `dakshin/polaris.py`:

RIO = sum over ice types i of C_i * RIV_i,  with C_i in tenths and RIV_i the Risk Index Value for that ice type at the ship's ice class (Table 1.3, standard, non-decayed).

Thresholds (Table 1.1): RIO of 0 or more is normal operation; between -10 and below 0 is elevated risk for classes PC1 to PC7 and special consideration for lower classes; below -10 is special consideration for all. Recommended speed limits under elevated risk (Table 1.2): PC1 11 kn, PC2 8 kn, PC3 to PC5 5 kn, below PC5 3 kn. In planning, areas needing special consideration should be avoided. The circular says (section 1.4) it should not be a go or no-go tool but a decision support tool.

Why the repository does not publish a RIO for Golovnin: the vessel carries a superseded Russian Register notation, KM(*) ULA, with no row in Table 1.3 and no entry in any regulator's equivalence schedule found; the Polar Code makes equivalence a per-ship, owner-initiated, flag-approved assessment with no lookup table. Across plausible candidate rows the same regime gives RIO from +19 to -21, so choosing a row is choosing an answer. RIO is also indexed by WMO stage of development, and the system has total concentration, not stage. `polaris.py` therefore computes the band across rows and reports where it crosses a tier boundary, requires the officer to declare a stage (no default, since a default would be an invented observation), and labels the single-stage reduction `RIO = C RIV[stage] + (10 - C) RIV[ice-free]` as not the IMO RIO. Table 1.4 (decayed ice) is not used because it requires confirmation of decay by observation.

The ice gate's 80% limit is therefore an assumption, and the MARGINAL band around it is derived rather than guessed: 7.4 concentration points, one median standard deviation of `cdr_seaice_conc_stdev` across the 70 to 90% band (December 2019: median 7.4, mean 8.0, p90 11.7). An earlier arbitrary 5-point band was narrower than the instrument's own uncertainty and would have reported a comfortable PASS the retrieval could not support. POLARIS never uses the words pressure, compression, ridge or drift, and is indexed by ice type, so a compliant implementation would need a thickness forecast (the GLO12 `sithick` variable is already harvested; no thickness product has been used).

---

## 9. Questions a physical oceanographer may ask, and where the answer is

| Question | Short answer and the evidence |
|---|---|
| What model is the forecast from, and at what resolution? | CMEMS GLOBAL_ANALYSISFORECAST_PHY_001_024 at 1/12 degree, daily means, 10 daily steps per cycle (`scripts/harvest_cmems.sh`); the repository describes the underlying ice model as the Mercator NEMO-LIM family (`docs/ML_ARCHITECTURE.md` section 1.3). The repository does not document its physics or data assimilation; the product manual should be the source for that. |
| Does 1/12 degree beat 1/4 degree for ice-edge skill? | In this corridor and season, no: 1/4 degree is 1 to 3% slightly better on both RMSE and IIEE, and 1 degree is worse on IIEE by 4% to 16% (section 4.1). Block-averaging is not a coarser model run. |
| So can you test eddy impact? | Not with these data. A same-model, multi-resolution run is needed; `dakshin/readers/nemo.py` exists to read such output but has not touched real NEMO files and lacks C-grid destaggering and velocity rotation. |
| Do eddies matter for iceberg tracks? | Evidence is inconclusive and the test is confounded: coarser currents give lower error (3.49 against 4.35 km/day) because most giants are grounded. On 13 moving segments the gap narrows but is too small a sample to resolve an eddy effect. |
| What currents drive the bergs? | CMEMS daily-mean surface (0.494 m) `uo`, `vo`, analysis currents for hindcast, forecast currents for the forecast. Daily means, so no sub-daily or tidal structure; shear over the draught ignored (WDE17 assumption 5). |
| Is there stochastic dispersion? | No. One deterministic track per berg. The 4.35 km/day cone is the measured median error, not a diffusion law. |
| What about wind? | Set to zero in forecast and hindcast. R computed with an assumed 10 m/s wind has median 0.25 in the hindcast segments, so the neglected term is of order a quarter of the current speed. |
| Sea-ice drag on bergs? | Not modelled (WDE17 assumption 4). For pack-ice embedded bergs the repository points to Lichey and Hellmer (2001) and Hunke and Comeau (2011) and marks them as not yet read in full. |
| Why not OpenDrift/OpenBerg? | GPL-2.0, so optional cross-check only and never imported (`ATTRIBUTION.md`). The melt terms are reimplemented from the papers. |
| How are cells regridded? | Unweighted mean of source cell centres per NSIDC cell, not a conservative remap (section 4.3 of the architecture document). |
| What is the truth, and can it be trusted at the coast? | NSIDC CDR; coastal cells are spillover-filtered and written as 0.0; the audit shows 43.2% of days affected in a 17 x 17 box around Bharati. QA masking sets them NaN. |
| Which sensor? | Training SSMIS (F17); 2026 scoring AMSR2. Not separable with held data. |
| Where is the leakage? | Training background is a reanalysis that has seen the target date; the training table is an upper bound; the operational hindcast uses real forecast cycles; the ablation is unrun; U-Net rows pending. |
| Does the U-Net beat CMEMS? | Not yet known. Training re-run in progress. By design the U-Net starts at CMEMS and cannot be much worse by construction; ADR-027 requires beating raw CMEMS on IIEE and CRPS, and the scorer computes no CRPS yet. |
| Why not a coupled model or data assimilation? | Out of scope; the pivot (ADR-018) is to correct an operational field, not rebuild one (`docs/ML_ARCHITECTURE.md` section 1.4). |
| What do the nine gates mean? | Evidence-derived states, no score; missing evidence caps health at DEGRADED (`dakshin/gates.py`, `dakshin/decision.py`). |
| What would you do with ANHA output? | Read it with `NemoReader`, regrid, and run the same hindcast metrics with that run in place of block-averaged GLO12. The regridder targets the south polar NSIDC grid, so a Northern Hemisphere configuration would need its own target grid and observations (outside the repository: ANHA is generally described as a Northern Hemisphere regional NEMO configuration; the repository says only "e.g. the ANHA family"). |

---

## 10. Papers and what each contributed

Bibliographic details are taken from repository files where those exist (path given). Entries marked "partial in repo" are cited by author and year only; their full details are not recorded in the repository and should be verified before being quoted in an interview.

| Reference | Contribution | Source in repo |
|---|---|---|
| Wagner, T. J. W., Dell, R. W., and Eisenman, I. (2017). An analytical model of iceberg drift. J. Phys. Oceanogr. 47(7), 1605 to 1616. doi:10.1175/JPO-D-16-0262.1; arXiv:1610.06403; reference code at tillwagner.me/wde17 | Closed-form drift law (section 2); regime analysis; drag-coefficient and |f| errata found against the reference code | `docs/ICEBERG_RESEARCH.md` section b |
| Goessling, H. F. et al. (2016), integrated ice-edge error | IIEE as a verification metric (section 4) | partial in repo (`dakshin/features.py` docstring only) |
| Bigg, G. R. et al. (1997) | Canonical iceberg momentum balance; buoyant convection and wave-erosion melt terms; drag coefficients | partial in repo (`docs/ICEBERG_RESEARCH.md`) |
| Gladstone, R. M., Bigg, G. R., and Nicholls, K. W. (2001) | Iceberg trajectory and melt-water injection in the Southern Ocean; wave erosion | partial in repo |
| El-Tahan, M. et al. (1987); Weeks, W. F. and Campbell, W. J. (1973) | Basal turbulent melt form and the iceberg temperature of -4 C | partial in repo |
| Keghouche, Bertino and Lisaeter (cited in `models/iceberg/melt.py` as 2010, JGR 114, C06012); "Keghouche et al. 2009" in `docs/ICEBERG_RESEARCH.md` | Parameterisation of the melt terms for the Barents Sea | The repository cites the paper with two different years, and volume 114 of JGR is not consistent with the year 2010. Verify the reference before quoting |
| Martin, T. and Adcroft, A. (2010); Roberts et al. (2014); Burton et al. (2012) | Douglas-sea-state parameterisation of wave erosion; model usage; capsize criterion adopted by WDE17 | partial in repo (`docs/ICEBERG_RESEARCH.md` b.1, b.8) |
| Silva, T. A. M. et al. (2006) | Shelf-ice density 850 kg/m3 | partial in repo |
| Weeks, W. F. and Mellor, M. (1978) | Original rollover criterion; WDE17 reports a sign error in its eq. (9) | partial in repo |
| Lichey, C. and Hellmer, H. H. (2001). Modeling giant-iceberg drift under the influence of sea ice in the Weddell Sea, Antarctica. J. Glaciol. 47(158), 452 to 460. doi:10.3189/172756501781832133 | Sea-ice coupling and the locked-in regime (not implemented) | `docs/ICEBERG_RESEARCH.md` b.7 |
| Hunke, E. C. and Comeau, D. (2011). Sea ice and iceberg dynamic interaction. J. Geophys. Res. 116, C05008 | Sea-ice / iceberg interaction (not implemented) | `docs/ICEBERG_RESEARCH.md` b.7 |
| IDRIFTNET, arXiv:2507.00036 (2025) | Hybrid WDE17 plus learned residual; physics-only displacement errors; the 24 h reliable-horizon statement | `docs/ICEBERG_RESEARCH.md` c.2 |
| Ivanova, N. et al. (2015), 30-algorithm sea-ice concentration round robin | Algorithm spread at 15% concentration; thin-ice underestimate; weather-filter deletion | partial in repo (`docs/NAVIGATION_RESEARCH.md` section 6) |
| Lavergne, T. et al. (2019), OSI SAF / CCI concentration records | Uncertainty excludes melt-pond, thin-ice and weather-filter effects; coastal correction imperfections | partial in repo |
| Lavergne, T. and Down, E. (2023). A climate data record of year-round global sea-ice drift from OSI SAF. ESSD 15, 5807 to 5834. doi:10.5194/essd-15-5807-2023 | Drift product considered for compression work | `docs/ICE_HAZARDS.md` |
| Ozsoy-Cicek, B. et al. (2009) | Antarctic AMSR-E against ship observations: R-squared 0.41, edge 38 to 102 km too far south | partial in repo (`docs/NAVIGATION_RESEARCH.md` 6.6) |
| Hibler, W. D. (1979) | Ice strength exponential in concentration | partial in repo |
| Thorndike, A. S. and Colony, R. (1982); Nansen (1902) | Free-drift rule; to be verified before a wind-advected first guess is used | partial in repo (`docs/PROTOTYPE_RESULTS.md`, `docs/research/MODEL_REUSE_MATRIX.md`) |
| Andersson, T. R. et al. (2021), IceNet, Nature Communications | Closest prior art: a purpose-built U-Net at 25 km for sea ice; rejected as a dependency because `icenet` 0.2.9 pins `netcdf4<1.6.1` and `python<3.12`, conflicting with `meshiphi` | partial in repo (`docs/backlog.md`, `docs/research/MODEL_REUSE_MATRIX.md`) |
| Meier, W. N. et al. NOAA/NSIDC Climate Data Record of Passive Microwave Sea Ice Concentration, Version 6 (G02202), doi:10.7265/efmz-2t65; Near-Real-Time CDR Version 4 (G10016), doi:10.7265/tgam-yv28 | Truth data | `ATTRIBUTION.md` |
| Dorschel, B. et al. (2022). The International Bathymetric Chart of the Southern Ocean Version 2. Scientific Data 9, 275. doi:10.1038/s41597-022-01366-7; dataset doi:10.1594/PANGAEA.937574 | Bathymetry south of 50 S | `ATTRIBUTION.md`, `scripts/subset_bathymetry.py` |
| GEBCO Compilation Group (2020). GEBCO 2020 Grid. doi:10.5285/a29c5465-b138-234d-e053-6c86abc040b9 | Bathymetry north of 50 S | `scripts/subset_bathymetry.py` |
| IMO MSC.1/Circ.1519 (2016-06-06), Guidance on methodologies for assessing operational capabilities and limitations in ice (POLARIS) | Risk index and thresholds | `docs/NAVIGATION_RESEARCH.md`, `dakshin/polaris.py` |
| Copernicus Marine products: Global Ocean Physics Analysis and Forecast, doi:10.48670/moi-00016; Waves Analysis and Forecast, doi:10.48670/moi-00017; Physics Reanalysis (GLORYS12), doi:10.48670/moi-00021 | Forecast, currents, waves, training background | `ATTRIBUTION.md` |
| ECMWF open data (IFS 10 m wind), CC BY 4.0 | Wind | `ATTRIBUTION.md` |
| Dijkstra (1959); Ronneberger et al. (2015), U-Net | The two algorithms underlying the router and the network | outside the repository; standard references |
