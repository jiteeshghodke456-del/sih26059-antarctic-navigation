# Synthetic Southern Ocean world model — design v1

**Status:** DESIGN. Not implemented. Written 2026-09-07 on branch `v3-compliance`.
**Supersedes:** the untracked draft `isih/sim/noise.py` + `isih/sim/fields.py` (§13 says exactly what survives).
**Audience:** whoever implements `isih/sim/`. Every number in this document is meant to be typed into `isih/sim/params.py` unchanged; every formula is meant to be coded as written.

Tags used on numbers: **Measured** (computed from data in this repo, method stated) · **Sourced** (literature/textbook value the author is confident of) · **UNVERIFIED** (plausible order of magnitude; verify before the finale — all listed in §14 and in `docs/backlog.md`).

---

## 0. The governing idea, and the two constraints that shape everything

> **Real physics, synthetic initial conditions.**

One seeded pressure field is the driver. Wind is its gradient. Waves grow from the wind. The ice edge moves because the wind pushed it and relaxes back because the water is warm. Fog forms where the wind carried warm air over freezing water. Bergs move because the current carried them. Route health degrades because the along-track samples of these fields crossed a limit — never because a timer fired.

Two constraints decide the architecture:

1. **Every field is a pure function of `(seed, t)`.** `t` is absolute seconds since a scenario epoch. There is no state, no step counter, no wall clock, no unseeded RNG. Two processes on two machines evaluating `(26059, 1_296_000)` produce bit-identical arrays.
2. **No 2-D time integration, ever.** The atmosphere, ocean, SST and ice *fields* are closed-form in `t`. The only integrals in the model are one-dimensional (the ice edge is a curve) and zero-dimensional (berg positions are points), and both are bounded-cost, memoised, pure functions of the seed.

Master prompt §27 governs the labelling: this is **SIMULATED INPUT** — "technically coherent", "never called live". §7.4 says how to label it on screen.

---

## 1. Conventions and invariants

| Item | Convention |
|---|---|
| Domain | lon 8°E–88°E, lat 78°S–26°S. Requests outside → HTTP 400 / `DomainError`. Nothing is clamped silently. |
| Coordinates | Public API: degrees, `lat` negative south. Internal: radians `λ, φ`. **No map projection.** Local metric on the sphere: `dx = R_E cos φ dλ`, `dy = R_E dφ`, `R_E = 6 371 000 m`. Round features are defined in the `cos φ_c` metric of their own centre; they are round on any conformal map — the bridge chart is Mercator (`chart.js`), so they render round. |
| Time | `t` float seconds since `epoch` (UTC datetime in the scenario). `doy` and `d` (days since 1 Dec of the season) derive from `epoch + t`. The model never reads the wall clock. |
| Vectors | `(u, v)` = eastward, northward, m/s. Wind and wave **direction FROM**, degrees true: `dir = atan2(-u, -v)` in degrees mod 360. Current direction **TOWARD** ("sets"). |
| Pressure | Pa internally, hPa at the API. |
| Ice | fraction 0–1 internally, integer percent at the API (matches `isih/demo/data.py:day_field`). |
| Hemisphere | `f = 2Ω sin φ < 0`. Flow is **clockwise** around a low, anticlockwise around a high. Surface wind is turned **clockwise** from geostrophic (toward low pressure). Free-drifting ice and Ekman transport go to the **left** of the wind. Buys Ballot: back to the wind, low is on your **right**. |
| Randomness | Only at world construction, only from `hashlib.blake2b(seed, tag, index)`. Never from `numpy.random` (§3.1 says why). |
| Land | `NaN` over land in every field; API serialises as `null`. |
| Season | The ice climatology is fitted for `d ∈ [-5, 100]` (26 Nov – 11 Mar). Outside that window `SeasonError` is raised: the model has no data-backed shape for other seasons and must not pretend. |

---

## 2. Module layout — `isih/sim/`

| Module | One-line purpose |
|---|---|
| `params.py` | Every constant in this document, nothing else. `SIM_VERSION = blake2b(file bytes)[:12]` is stamped into every API response so a screenshot names the physics that produced it. |
| `hashing.py` | `uniform(seed, tag, index, n)` → stable `[0,1)` draws from blake2b; `normal` via Box–Muller. |
| `geometry.py` | Metric factors, Coriolis with the guard, coast-latitude table, distance-to-coast, land mask from `isih/figures/coastline.json`, domain checks. |
| `spectral.py` | `PlaneWaves` (seeded Fourier modes in `(λ, φ, t)` with exact gradients) and `Blobs` (moving Gaussians with life cycles and exact gradients). The only two shape primitives in the model. |
| `synoptic.py` | Climatological MSLP, hash-indexed cyclone/anticyclone schedules, residual field; `mslp_grad()`. |
| `wind.py` | Geostrophic → 10 m: boundary-layer factor and turning, katabatic term, cap. |
| `ocean.py` | Front positions with standing meanders, streamfunction (jets + coastal current + eddies + Prydz gyre) → non-divergent current; frontal SST `T_F`. |
| `ice.py` | Edge climatology (fitted table), wind-driven edge relaxation integral (1-D, memoised), signed distance, MIZ profile, texture, fast ice, polynyas → SIC. |
| `thermo.py` | SST slaved to the edge, 2 m air temperature by back-trajectory, visibility (advection fog, precipitation proxy, blowing snow). |
| `waves.py` | Effective wind, fetch to the ice edge, PM/JONSWAP growth, swell floor, attenuation inside ice → Hs, Tp, direction. |
| `bergs.py` | Seeded berg population, Heun integration of `models/iceberg/drift.iceberg_velocity`, memoised tracks, `berg_state(t)`, WDE17 regime per berg. |
| `world.py` | `World(seed, epoch, …)` composition root; `fields(grid, t)` sharing intermediates; `point()`, `along_track()`, caches. |
| `scenario.py` | Scenario JSON (seed, epoch, horizon, berg count, notes) load/validate; env and query overrides. |
| `test_sim_properties.py` | §10. |

No module imports xarray, scipy, pyproj or pandas. `bergs.py` imports `models/iceberg/drift.py` (numpy only).

---

## 3. Primitives

### 3.1 Reproducible randomness: hashed draws, not a generator

```
u(seed, tag, i) = int.from_bytes(blake2b(f"{seed}|{tag}|{i}".encode(), digest_size=8).digest(), "little") / 2**64
```

`normal` = Box–Muller on `(u_{2i}, u_{2i+1})` with `u_{2i}` floored at `2**-53`. Discrete choice = `floor(n · u)`.

Why not `np.random.default_rng(seed)`: NumPy's NEP 19 freezes the *bit generator* stream but explicitly allows `Generator` distribution methods to change between releases. This demo runs on numpy 2.5 / Python 3.14 in the sandbox and on the user's WSL Python 3.12 venv; the same seed could give two different worlds on the two machines used for the demo. blake2b is RFC 7693 and part of `hashlib`; its output is identical everywhere, forever. It is also *random-access*: the cyclone schedule (§3.5) needs "the parameters of storm slot `j`" for any integer `j` without generating slots `0..j-1`.

Cost: a few thousand Python-level hash calls at world construction (< 10 ms), zero per request.

### 3.2 Geometry

- `coriolis(lat_deg)`: `f = 2Ω sin φ`, `Ω = 7.2921e-5 s⁻¹`. **Guard:** assert `φ ≤ -20°` (`|f| ≥ 5.0e-5`), raise `DomainError` otherwise. With that floor, `1/(ρ_a |f|) ≤ 1.6e4`, so a 1 hPa/100 km gradient can never produce more than 16 m/s geostrophic wind — nothing explodes, and nothing is clamped silently. In the 26°S–78°S domain `|f| ≥ 6.4e-5`, so the guard never fires in normal use; it exists for the day someone widens the domain.
- `coast_lat(lon_deg)`: linear interpolation of the table below (2° knots, 9°E…87°E). **Measured** from `isih/figures/coastline.json` (Natural Earth 1:50m, simplified 0.02°): northernmost land-ring vertex per 2° bin south of 60°S; the 81°E gap is the mean of its neighbours.

```
lon:  9     11     13     15     17     19     21     23     25     27     29     31     33     35     37     39     41     43     45     47
lat: -70.18 -70.51 -70.05 -69.73 -69.70 -70.20 -70.26 -70.40 -70.20 -70.07 -70.41 -70.23 -68.67 -68.70 -69.64 -68.97 -68.51 -68.10 -67.66 -67.27
lon:  49     51     53     55     57     59     61     63     65     67     69     71     73     75     77     79     81     83     85     87
lat: -66.70 -66.02 -65.86 -65.95 -66.37 -67.23 -67.39 -67.51 -67.62 -67.77 -67.74 -70.26 -69.74 -69.58 -69.07 -68.12 -67.70 -67.29 -66.52 -66.67
```

- `distance_to_coast_m(lat, lon)` = `R_E (φ − φ_coast(λ))` (positive offshore). First-order in the coast slope; error < 10 % inside the 100 km band where it is used (katabatics, fast ice, coastal current, polynyas). Sub-Antarctic islands (Kerguelen, Heard, Crozet, Marion) are **land mask only** — no katabatics, no fast ice.
- `land_mask(grid)`: vectorised crossing-number point-in-polygon against the 16 land rings in `coastline.json`; computed once per `Grid` and cached. `coastline.json` is a display extract by its own docstring; using it as a mask is acceptable for a synthetic world and the ADD upgrade already sits in the backlog.

### 3.3 `PlaneWaves` — seeded Fourier modes with exact gradients

Recommended for every smooth random field. Formula, for `N` modes:

```
θ_n(λ, φ, t) = m_n λ + l_n φ − ω_n t + ϕ_n                 (λ, φ radians; t seconds)
p'(λ, φ, t)  = E(φ) · Σ_n A_n cos θ_n
∂p'/∂x = −E(φ)/(R_E cos φ) · Σ_n A_n m_n sin θ_n
∂p'/∂y =  E'(φ)/R_E · Σ_n A_n cos θ_n  −  E(φ)/R_E · Σ_n A_n l_n sin θ_n
```

- `m_n` integer **zonal wavenumber** (cycles per 2π of longitude) — the natural language of Southern Ocean synoptics ("wavenumber 4–7"). A mode propagates *zonally everywhere* because the phase is linear in `λ`; a plane wave in a projected plane could not do that across an 80° sector.
- `l_n = ±2π/Λ_φ` with the meridional wavelength `Λ_φ` drawn in radians; the sign is a coin toss so tilts go both ways.
- `ω_n = m_n Ω_steer (1 + 0.3 ξ_n)`, `ξ_n ∈ [−1, 1]`, `Ω_steer = U_steer/(R_E cos 55°)`. `θ = mλ − ωt` puts crests at increasing `λ` as `t` grows: **eastward**. All `ω > 0`.
- Amplitudes `A_n ∝ k_n^{−2}` with the true wavenumber at the reference latitude `k_n = √((m_n/(R_E cos 55°))² + (l_n/R_E)²)`. An enstrophy-cascade kinetic-energy spectrum `E(k) ∝ k^{−3}` gives wind amplitude `∝ k^{−1}` per mode and pressure `∝ k^{−2}`. Scale so `RMS = σ`, using `RMS² = Σ A_n²/2` (for `E ≡ 1`).
- `E(φ)` is an optional latitude envelope; its derivative is included in `∂/∂y` (product rule), so the gradient stays exact.
- Closed-form exponentially-weighted time integral, if ever wanted: `∫_{−∞}^{t} e^{−(t−t')/τ} sin θ_n(t') dt' = τ [sin θ_n(t) + ω_n τ cos θ_n(t)] / (1 + ω_n² τ²)`. Not used in v1 (§4.4.2 explains).

Why this beats the alternatives for this use: hash-lattice value/gradient noise (Perlin) is only C¹ even with quintic fades, needs fade-derivative code for gradients, has no physical spectrum and no closed-form time behaviour; a sum of random Gaussians has no spectrum control. Fourier gives C^∞, exact gradients for free (one `sin` and one `cos` per mode yields value *and* both derivatives), a spectrum you can state, and eastward propagation by construction.

### 3.4 `Blobs` — moving Gaussian features with life cycles and exact gradients

Used for cyclones, anticyclones, ocean eddies, the Prydz gyre and polynyas. Feature `j`:

```
λ_j(t) = λ_j0 + Ω_j (t − t_j)          φ_j(t) = φ_j0 + Φ_j (t − t_j)
ξ = R_E cos φ_j(t) · (λ − λ_j(t))      υ = R_E · (φ − φ_j(t))
G_j = A_j · E_j(t) · exp(−(ξ² + υ²)/(2 R_j²))        E_j(t) = exp(−(t − t_j)²/(2 σ_j²))   (σ_j = ∞ → E ≡ 1)
∂G_j/∂x = −G_j · ξ · cos φ_j(t) / (R_j² cos φ)          ∂G_j/∂y = −G_j · υ / R_j²
Ω_j = c_j sin h_j / (R_E cos φ_j0)     Φ_j = c_j cos h_j / R_E     (c_j speed m/s, h_j heading ° from north)
```

`alive(t)`: keep `j` with `|t − t_j| ≤ 3.5 σ_j` (envelope ≥ 0.2 %). Round at the centre in its own `cos φ_j` metric; mildly egg-shaped in true km away from it (the southern half of a 500 km low at 60°S is ~15 % zonally narrower than the northern half in kilometres) — invisible on a conformal chart and irrelevant to any decision.

### 3.5 Hash-indexed schedules (an infinite, random-access storm calendar)

Slot `j ∈ ℤ` peaks at `t_j = (j + u(seed, tag, 9j)) · Δ`. All other parameters of slot `j` come from `u(seed, tag, 9j + 1..8)`. At time `t`, evaluate only slots `j ∈ [⌊(t − 3.5 σ_max)/Δ⌋ − 1, ⌊(t + 3.5 σ_max)/Δ⌋ + 1]`, then `alive()`. There is no list, no horizon, and `t = 400 days` costs the same as `t = 0`. This is the answer to "3–5 propagating lows, evaluable at any `t`": the calendar is a pure function of the seed.

---

## 4. The fields

### 4.1 Mean sea-level pressure — the driver

```
P(λ, φ, t) [Pa] = 100 · [ P_clim(φ) + Σ_lows G_j + Σ_highs G_j + p'_res(λ, φ, t) ]
P_clim(φ°) [hPa] = 1003 + 16 tanh((φ° + 52)/9) − 3 exp(−((φ° + 66)/5)²)
dP_clim/dφ° = (16/9) sech²((φ° + 52)/9) + (6 (φ° + 66)/25) exp(−((φ° + 66)/5)²)      → ∂/∂y = dP/dφ° · (180/π)/R_E · 100  [Pa/m]
```

`P_clim` targets (DJF zonal means, Indian sector; **UNVERIFIED ±3 hPa**): 30°S 1018 · 35°S 1019 · 40°S 1015 · 45°S 1010 · 50°S 1004 · 55°S 997 · 60°S 990 · 65°S 986 (circumpolar trough) · 70°S 988. The formula gives 1018.7 / 1018.3 / 1016.9 / 1013.4 / 1006.5 / 997.8 / 991.6 / 985.7 / 986.5. Its geostrophic wind at 52°S is 11.1 m/s, i.e. 7.8 m/s at 10 m after the boundary layer — the climatological westerlies (Sourced: DJF 10 m means 9–11 m/s in the 50s; the cyclones add the rest).

**Lows** (`tag="low"`, `Δ_L = 86 400 s`), per slot from uniforms `u1…u8`:

| Parameter | Draw | Range | Basis |
|---|---|---|---|
| central deficit `ΔP` | `−(12 + 33 u²)` hPa | −12…−45, median −20 | Sourced: SO cyclones 950–985 hPa on a ~995 ambient (Simmonds & Keay 2000) |
| radius of max wind `R` | `350 + 200 u` km | 350–550 | Sourced: RMW 300–500 km, outer radius ~1000 km |
| life-cycle `σ` | `(1.2 + 0.6 u)` d | 1.2–1.8 (≈5–6 d above 10 %) | Sourced: 3–6 d lifetimes |
| peak longitude `λ0` | `10 + 75 u` °E | inside the domain | so every low is deepest somewhere on the chart |
| peak latitude `φ0` | `−(50 + 14 u)` ° | 50–64°S | Sourced: storm track / trough |
| speed `c` | `9 + 6 u` m/s | 9–15 | Sourced: 10–15 m/s translation |
| heading `h` | `100 + 25 u` ° | ESE | Sourced: poleward-spiralling tracks |

One slot per day gives ~12 alive slots (envelope > 0.2 %), of which ~5 lie inside the sector at any instant and 2–3 are near peak — the "3–5 lows" a mariner expects on a sector chart. Tunable: `Δ_L`.

**Highs** (`tag="high"`, `Δ_H = 172 800 s`): `ΔP = +(8 + 10u)` hPa, `R = 700 + 300u` km, `σ = 1.5 + 1.0u` d, `λ0 = 10 + 75u`, `φ0 = −(36 + 8u)`, `c = 6 + 4u` m/s, `h = 90 + 20u`°. They give the ridge–trough alternation on the Cape Town → SAF leg and rotate anticlockwise automatically because `f < 0`.

**Residual** `p'_res`: `PlaneWaves` with `N = 16`, `m ∈ {5…12}`, `Λ_φ ∈ [8°, 25°]`, slope 2, `σ = 3.0 hPa`, `U_steer = 8 m/s`, envelope `E(φ) = exp(−((φ° + 55)/15)²)`. Its job is to bend the Gaussians into troughs and ridges so the chart does not read as "circles on a slope"; at 3 hPa RMS it modulates, never dominates.

Magnitude check (Sourced arithmetic): `ΔP = −30 hPa, R = 400 km` at 60°S → `v_g,max = ΔP e^{−1/2}/(ρ_a |f| R) = 28.9 m/s` → 20 m/s at 10 m. The deepest slot (−45 hPa, 350 km) → 30 m/s at 10 m: violent storm, rare, correct.

### 4.2 10 m wind

```
u_g = −(∂P/∂y)/(ρ_a f)      v_g = (∂P/∂x)/(ρ_a f)          ρ_a = 1.25 kg/m³, f signed (§3.2)
u10 = α (u_g cos θ + v_g sin θ)     v10 = α (−u_g sin θ + v_g cos θ)        α = 0.70,  θ = 15° · (−sign f) = +15° here (clockwise)
+ katabatic (below);  then |u10| capped at 40 m/s (count cap hits in tests — it should be ~never).
```

Gradients are **analytic** (§3.3, §3.4, `dP_clim/dφ`), never finite-differenced: one `sin`+`cos` per mode and one `exp` per blob give `P, ∂P/∂x, ∂P/∂y` together, which is both cheaper and free of step-size artefacts.

Boundary layer (Sourced, marine textbook values): speed factor 0.6–0.8, cross-isobar angle 10–20° over sea. Fixed `0.70 / 15°` in v1. Optional refinement (not v1): `α = 0.70 − 0.10 s`, `θ = 15° + 10° s`, `s = clip((T2m − T_sfc)/3, −1, 1)` — stable air over cold water turns more and blows less. It is omitted because it makes the wind depend on the ice via T2m and would need a two-pass evaluation (§5).

Katabatic / coastal easterlies (φ < −60°, `d_c > 0`):
```
K(t) = 7 · (0.6 + 0.8 S(t)) m/s,   S(t) = ½ + ¼ sin(2πt/2.3 d + ϕ1) + ¼ sin(2πt/3.7 d + ϕ2)   (seeded phases)
(u_k, v_k) = K e^{−d_c/80 km} · (sin 320°, cos 320°) = K e^{−d_c/80 km} · (−0.643, +0.766)
```
Drainage air runs seaward (north) and Coriolis turns it **left** in the SH → blows toward the NW, i.e. **from the SE** — the Mawson/Davis SE katabatic and the polar easterlies have the same sign (Sourced for the direction; 7 m/s mean amplitude **UNVERIFIED**, Mawson's annual mean is ~11 m/s).

### 4.3 Surface current — a streamfunction, so it cannot diverge

Everything is `ψ`; velocity is `u = −(1/R_E) ∂ψ/∂φ`, `v = (1/(R_E cos φ)) ∂ψ/∂λ`. A prescribed streamfunction is exactly non-divergent, which matters because this field advects bergs: any divergence would create fictitious convergence lines where bergs pile up.

**Frontal jets** (positions approximate from Orsi et al. 1995 / Sokolov & Rintoul 2009 for 8–88°E, **UNVERIFIED ±1.5°**; surface jet speeds Sourced 0.3–0.6 m/s):

| Front | `φ_F(λ°)` [deg] | `U_F` m/s | `w_F` deg | meander RMS |
|---|---|---|---|---|
| STF / Agulhas Return Current | `−40.0 − 0.010 (λ − 8)` | 0.50 | 0.45 | 0.5° |
| Subantarctic Front | `−45.5 − 0.040 (λ − 8)` | 0.45 | 0.50 | 0.8° |
| Polar Front | `−50.5 − 0.0375 (λ − 8)` | 0.35 | 0.50 | 0.8° |
| Southern ACC Front | `−56.0 − 0.025 (λ − 8)` | 0.25 | 0.60 | 0.4° |
| Southern Boundary | `−61.0 − 0.025 (λ − 8)` | 0.10 | 0.80 | 0.4° |

Standing meanders `δ_F(λ) = Σ_{n=1..6} a_n cos(2πλ/Λ_n + ϕ_n)`, `Λ_n` log-uniform in `[6°, 20°]`, `a_n ∝ Λ_n`, static (the ACC's meanders are topographically locked — Kerguelen, Conrad Rise — so they do not move in a month). `φ_F ← φ_F + δ_F`.

```
ψ_F = ΔΨ_F · ½[1 − tanh z],  z = (φ − φ_F(λ))/w_F   (radians),   ΔΨ_F = 2 U_F w_F R_E
∂ψ_F/∂φ = −ΔΨ_F/(2w_F) sech² z          ∂ψ_F/∂λ = +ΔΨ_F/(2w_F) sech² z · φ_F'(λ)
→ u = U_F sech² z  (eastward jet, max U_F on the front),   v = u · φ_F'(λ)/cos φ  (flow follows the meander)
```

**Antarctic Coastal Current** (westward, Sourced 0.1–0.3 m/s within ~100 km of the coast/shelf break):
`ψ_c = ΔΨ_c · ½[1 + tanh((d_c − 50 km)/35 km)]`, `ΔΨ_c = 2 · 0.15 m/s · 35 km = 1.05e4 m²/s`, with `d_c` from §3.2. Gives `u = −0.15 sech²` m/s (westward), `v` following the coast including around Prydz Bay, zero at the coast, zero far offshore.

**Mesoscale eddies:** `N_e = 30` `Blobs` with `λ_e ∈ [8°, 88°]`, `φ_e ∈ [−60°, −42°]`, `L_e ∈ [35, 70] km`, `U_e ∈ [0.15, 0.45] m/s`, sign `s_e = ±1` (p = ½), `A_e = s_e U_e L_e √e` (so the swirl speed peaks at `U_e` at `r = L_e`), no life cycle, eastward drift `c_e = 0.04 m/s` (**UNVERIFIED**; downstream propagation of a few cm/s). Sign convention derived, not assumed: `u = −∂ψ/∂y, v = ∂ψ/∂x` with `A > 0` gives southward flow east of the centre → **clockwise → cyclonic in the SH**, consistent with `ψ = gη/f`, `f < 0`: a low-SSH eddy is cyclonic. Test in §10.

**Prydz Bay gyre:** one blob at (−67.5°, 73.0°E), `L = 150 km`, `U = 0.10 m/s`, cyclonic (**UNVERIFIED** sense).

Not modelled: Ekman drift (the WDE17 closure takes the ocean current at keel depth; the Ekman layer is a small fraction of a berg's draft), the Agulhas Current proper along the shelf east of 22°E (the corridor leaves it to the east).

**Frontal SST** `T_F(λ, φ)` (static, cached per grid; °C):
```
T_F = 0.0 + Σ_F ΔT_F · ½[1 + tanh((φ − φ_F(λ))/w_T,F)] + 0.35 · max(0, φ° + 40) + 0.4 · T_sst(λ, φ)
ΔT (south→north):  SB 1.0 (w_T 1.0°) · SACCF 1.0 (1.0°) · PF 2.5 (0.6°) · SAF 3.5 (0.6°) · STF 7.0 (0.6°)
```
→ 0 °C south of the SB, 2.0 in the Antarctic Zone, 4.5 in the PFZ, 8.0 in the SAZ, 15 north of the STF, 17.1 at Cape Town's latitude (Sourced to ±1 °C for the PF/SAF/STF steps; Cape Town Jan SST 17–20). `T_sst` is a static unit-RMS `PlaneWaves` texture (100–500 km, `N = 10`, `ω = 0`) — mesoscale SST variance, ±0.4 °C.

### 4.4 Sea ice

#### 4.4.1 The edge climatology — fitted to real CDR data at design time (no runtime data)

**Measured.** From the NOAA/NSIDC CDR daily 25 km files already in `isih/data/nsidc_sic` (`SOURCE_ICE` in `isih/demo/data.py`), QA on, seasons 2018-19 and 2019-20 pooled, daily 1 Dec–28 Feb (≈180 days per bin), 4° longitude bins. Edge = northernmost 0.25° latitude bin whose bin-mean SIC ≥ 0.15 for three consecutive bins southward (rejects detached floes). Per bin, least-squares fit of a logistic in days-since-1-Dec `d`:

```
φ_clim(λ, d) = a + (b − a) · σ((d − m)/w),      σ(z) = 1/(1 + e^{−z})
```
`(a, b, m, w)` are linearly interpolated in `λ` between the knots below (clamped beyond the ends). Note `m = 0` bins start *at the midpoint*, so their 1 Dec value is `(a+b)/2`, not `a`.

| lon °E | a (pre-season asymptote) | b (late-summer asymptote) | m (days after 1 Dec) | w (days) | fit rms ° |
|---|---|---|---|---|---|
| 10 | −57.16 | −69.01 | 16 | 5 | 0.97 |
| 14 | −56.59 | −68.73 | 12 | 5 | 0.74 |
| 18 | −58.47 | −68.94 | 15 | 4 | 0.64 |
| 22 | −58.52 | −69.07 | 17 | 5 | 0.68 |
| 26 | −59.43 | −68.07 | 17 | 5 | 1.03 |
| 30 | −55.22 | −67.77 | 6 | 12 | 1.42 |
| 34 | −55.64 | −68.06 | 3 | 20 | 0.76 |
| 38 | −59.12 | −67.79 | 10 | 12 | 0.52 |
| 42 | −58.78 | −67.10 | 4 | 10 | 0.37 |
| 46 | −60.22 | −66.19 | 0 | 12 | 0.24 |
| 50 | −60.13 | −65.80 | 0 | 15 | 0.24 |
| 54 | −60.11 | −65.35 | 0 | 12 | 0.20 |
| 58 | −59.74 | −65.99 | 0 | 15 | 0.40 |
| 62 | −59.99 | −66.75 | 3 | 15 | 0.46 |
| 66 | −62.04 | −67.41 | 10 | 20 | 0.53 |
| 70 | −64.82 | −67.04 | 19 | 5 | 0.55 |
| 74 | −63.42 | −67.32 | 8 | 15 | 0.57 |
| 78 | −63.10 | −66.04 | 0 | 20 | 0.48 |
| 82 | −61.15 | −65.96 | 0 | 20 | 0.53 |
| 86 | −63.13 | −65.63 | 23 | 8 | 0.62 |

What the data says, and what an examiner will check: on 1 Dec the edge is **northernmost in the west** (57–59°S at 10–25°E, the Maud Rise tongue) and 63–65°S in the east; the west collapses to the coast in the second half of December (10–13° in a month, up to 40 km/day); the centre and east retreat 2–4° over the whole summer; in February 1–2° of pack remains off Princess Elizabeth Land (80–88°E) and off Enderby/Mac.Robertson Land. Evaluated fit (deg S):

```
lon   1Dec  15Dec  1Jan  1Feb  coast        lon   1Dec  15Dec  1Jan  1Feb  coast
10   -57.6  -61.9 -68.4 -69.0  -70.3        50   -63.0  -64.2 -65.2 -65.7  -66.4
22   -58.9  -62.3 -68.5 -69.1  -70.3        62   -63.0  -64.6 -65.8 -66.6  -67.5
34   -61.4  -63.5 -65.6 -67.4  -68.7        74   -64.9  -65.8 -66.6 -67.2  -69.7
42   -62.1  -64.9 -66.6 -67.1  -68.3        86   -63.3  -63.7 -65.0 -65.6  -66.6
```
Floor: `φ_clim ≥ φ_coast(λ) + 0.12°` (≈13 km of ice always remains; fast ice is added separately).

Day-to-day wobble of the real edge (7-day-detrended std): 0.10–0.20° (11–22 km) in the compact-pack regime (centre/east, Jan–Feb); 0.4–0.7° in December in the west where diffuse bands appear and vanish. The model reproduces the first with the relaxation integral (4.4.2) and the second with MIZ-width modulation (4.4.3) — the large December wobble is *diffuse ice appearing*, not the pack moving 50 km a day.

#### 4.4.2 Wind-driven edge displacement — a relaxation integral, not an advection equation

Physics: free-drifting ice moves at ~2 % of the **10 m** wind, 20–40° to the **left** of it in the SH — Nansen's (1902) near-surface rule, Sourced. Do **not** cite Thorndike & Colony (1982) for this: their regression is against *geostrophic* wind and gives 0.8–1.1 % at 5–18°; `docs/backlog.md` records an earlier draft getting this wrong. We use 0.02 and 20° because the model's wind is the 10 m wind. Plus the surface current. Ice blown north into water above freezing melts; ice blown south compacts. The edge therefore behaves as a **first-order relaxation** toward its thermodynamic position:

```
dη/dt = V_n(λ, t) − η/τ_E       ⇒      η(λ, t) = ∫_{−∞}^{t} e^{−(t−t')/τ_E} V_n(λ, t') dt'
(u_i, v_i) = 0.02 · Rot(+20°)(u10, v10) + (u_c, v_c)          Rot(+20°) = anticlockwise: u' = u cos20 − v sin20, v' = u sin20 + v cos20
V_n(λ, t') = v_i evaluated at (λ, φ_clim(λ, d(t')))            (northward component; the edge is quasi-zonal, slopes ≤ 0.2)
φ_E(λ, t) = φ_clim(λ, d) + η(λ, t)/R_E,   then the coast floor again.
τ_E = 3 days (UNVERIFIED — chosen so the model's own σ(η) lands in the measured 15–25 km; §10 asserts it)
```
Sanity: a 2-day 10 m/s northerly (on-ice) gives `η = −0.19 m/s · τ (1 − e^{−2/3}) = −24 km` (edge moves south, compaction); a 1-day 20 m/s storm gives −28 km; alternating synoptic winds give σ ≈ 20 km. Matches the measured wobble. Bounded for all `t` — no random walk, no dependence on the epoch.

**Evaluation — bounded quadrature, memoised, continuous in `t`:**
- 161 edge longitudes `λ_k = 8 + 0.5k`.
- Kernel window `6 τ_E = 18 d` (dropped tail weight 0.25 %), step `Δ = 3 h` → sample times `t_i = Δ⌊t/Δ⌋ − iΔ, i = 0…143`, **anchored to absolute multiples of Δ**, plus the exact current time `t`. Trapezoid weights with the kernel; the leading partial interval `[t_0, t]` is integrated exactly, so `η` is continuous as `t` crosses a sample boundary.
- Each sample `V_n(λ_k, t_i)` is a pure function of `(seed, i)`: memoise in a bounded dict keyed by `i` (≈400 entries × 161 floats). A slider tick computes 1–2 new samples; a cold cache costs **8.4 ms measured** (25 760 points × 35 blobs + 16 modes, sandbox numpy 2.5).
- This is not time-stepping: no state is carried between requests, the cost is bounded and independent of `t`, and identical `(seed, t)` gives identical `η` whatever was requested before.

Why not the closed form: the `PlaneWaves` part has one (§3.3); the cyclone part needs `erf` (not in numpy) and completing-the-square algebra with overflow traps. The quadrature is 30 lines, robust, and cheaper than the alternatives' bugs. Approximation accepted: `V_n` is sampled at the climatological edge, not the displaced one — error `O(η/R_cyclone) ≈ 5 %`.

#### 4.4.3 Concentration

Signed distance **inside** the edge (perpendicular, m): `s = R_E (φ_E(λ) − φ) / √(1 + (φ_E'(λ)/cos φ)²)`, `φ_E'` from the edge table.

```
MIZ scale      W(λ, t) = W_clim(d) · clip(exp(−V_on(λ, t)/6 m/s), 0.5, 2.0)      V_on = −v10 at the edge point (positive = wind toward the pack)
               W_clim(d) = 30 + 95 · [1 − σ((d − 14)/5)]  km                       (Measured: 15→80 % MIZ ≈ 2.03 W = 240 km early Dec → 70 km Jan → 60 km Feb)
pack interior  C_pack(d) = 0.93 + 0.05 σ((d − 20)/10)                                (Measured: interior medians 0.85–0.95 Dec, 0.95–1.0 Jan–Feb)
profile        s ≥ 0:  SIC₀ = C_pack [1 − 0.85 e^{−s/W}]           (= 0.15 C_pack at the edge, by definition of the 15 % edge)
               s < 0:  SIC₀ = 0.15 C_pack e^{s/(0.3 W)}            (outer skirt of bands; 60 km wide under off-ice winds, 8 km under on-ice)
texture        SIC₁ = SIC₀ · [1 + 0.12 T_ice(λ − Δλ_adv, φ)]       T_ice: unit-RMS PlaneWaves, 40–300 km, N = 12, static; Δλ_adv = u_adv t/(R_E cos φ), u_adv = −0.06 e^{−d_c/200 km} m/s
fast ice       SIC₂ = max(SIC₁, 0.97 · ½[1 − tanh((d_c − B)/10 km)])   B = 25 km (70 km for λ ∈ [70°, 78°], Prydz Bay) · [1 − 0.5 σ((d − 45)/10)]   (UNVERIFIED widths; break-out mid-Jan)
polynyas       SIC₃ = SIC₂ · Π_k [1 − A_k exp(−r_k²/(2L_k²))],   A_k = clip(0.3 + 0.07 V_off,k, 0, 0.95),   V_off,k = v10 at the site (offshore = northward)
               sites: Cape Darnley (−67.8, 69.5, L 35 km) · Mackenzie Bay (−68.4, 71.5, 30) · Lützow-Holm (−68.6, 38.5, 30) · Larsemann/Prydz-east (−69.0, 76.5, 25)   (Cape Darnley Sourced; others UNVERIFIED ±1°)
SIC = clip(SIC₃, 0, 1);  NaN on land.
```
On-ice wind → `W` halves (compact, sharp edge); off-ice wind → `W` doubles and the skirt widens (diffuse edge, bands 100+ km out) — Wadhams' classic MIZ phenomenology, and the mechanism behind the measured December wobble. The 80 % contour (the vessel's working limit) sits `W ln(0.85/(1 − 0.8/C_pack)) ≈ 2.0 W` inside the 15 % edge; the texture moves it ±10 km locally.

The leads texture is advected with the mean coastal drift (155 km westward in 30 days near the coast) — a linear-in-`t` displacement, directly evaluable, and enough for the pattern to be seen to *move* coherently. Individual leads are not tracked; the exact interior displacement changes no decision.

Mass conservation is deliberately **not** enforced: in summer the ice budget is dominated by melt, and an edge blown north loses area. What is enforced (§10): the seasonal area decreases monotonically in the 7-day mean, and on-ice wind reduces MIZ area while raising mean SIC inside.

### 4.5 Sea-surface temperature — slaved to the edge

```
outside (s < 0):  SST = T_F − (T_F − T_f) · e^{−(−s)/L_sst}     L_sst = 200 km,  T_f = −1.8 °C
inside  (s ≥ 0):  SST = T_f − 0.1 · SIC
```
Continuous at the edge (both → −1.8). Wherever the edge is — climatological, wind-displaced, or in a polynya — SST is at freezing there and warms to the frontal field 200 km out. The 1 Dec tongue at 57°S sits in Antarctic-Zone water (2 °C) and the slaving overrides it, which is what the real CDR/SST pair shows. Direction of causality is stated, not hidden: in this world the edge is the primary state and SST is diagnosed from it; the relaxation time τ_E is where "warm water melts displaced ice" lives.

### 4.6 2 m air temperature — a back-trajectory, so advection is real

```
T_sfc = (1 − SIC) · SST + SIC · (T_f − 4.0)                          surface the air feels; −5.8 °C over 100 % summer pack (UNVERIFIED)
upwind point:  λ_u = λ − 0.7 u_g τ_adv/(R_E cos φ),  φ_u = φ − 0.7 v_g τ_adv/R_E,   τ_adv = 12 h    (neutral wind, no BL turning: avoids any dependence on the ice)
T2m = T_sfc + 0.6 · (T_sfc(λ_u, φ_u) − T_sfc) − 1.0 − 3.0 e^{−d_c/100 km}·[φ < −60°]
```
`r = 0.6` = fraction of the upwind surface temperature the air still carries after ~400 km (UNVERIFIED); `−1.0` = mean air–sea difference over the summer Southern Ocean (UNVERIFIED ±0.5). Checks: 45°S → ≈7 °C (DJF 2 m ≈ 7–9); pack interior → ≈ −7 °C; ice edge with a northerly → ≈ −0.4 °C, with a southerly → ≈ −4 °C. The second `T_sfc` evaluation at `(λ_u, φ_u)` re-runs only the cheap chain (edge distance, `T_F`, `SIC₀`).

### 4.7 Visibility — fog where warm air meets freezing water, nowhere else

```
ΔT_fog = T2m − T_sfc                                       (> 0: warm air over a cold surface)
s_fog = clip((ΔT_fog − 1.5)/2.5, 0, 1) · clip((18 − |u10|)/8, 0, 1)    dew point ≈ T2m − 1.5 (RH ≈ 90 %, UNVERIFIED); fog dies above 18 m/s
s_p   = clip((−(P − P_clim)·0.01 − 8)/12, 0, 1) · clip(−v10/8, 0, 1)     deep low + northerly = warm-sector precipitation
s_bs  = clip((|u10| − 12)/5.5, 0, 1) · max(clip(SIC/0.5, 0, 1), [d_c < 50 km])   blowing snow; reaches 100 m at 17.5 m/s = AAD blizzard definition (NAVIGATION_RESEARCH.md:603)
vis_m = min(20 000·10^{−2.0 s_fog},  20 000·10^{−1.3 s_p},  20 000·10^{−2.3 s_bs})     → 200 m dense fog, 1 km heavy snow, 100 m blizzard, 20 km clear
```
With the T2m formula, `ΔT_fog > 1.5` requires the upwind surface to be ≥ 4.2 °C warmer than the local one ~400 km back: exactly the ice edge (freezing water 200 km from 3–5 °C water) under a **northerly**. Southerlies give cold clear air. Fog frequency in the MIZ band therefore equals the fraction of time with a northerly component — 25–40 % under the cyclone train — matching the (UNVERIFIED) 20–40 % summer fog climatology near the edge, without any fog noise field.

### 4.8 Waves — fetch/duration-limited growth, a swell floor, damped inside the ice

```
U_eff = ½ (|u10|(t) + |u10|(t − 6 h))                       the one place a second field evaluation is spent; the sea lags the wind
fetch to ice upwind:   F_ice = (−s)·|u10|/v10  if v10 > 0.15|u10| (southerly: ice lies upwind) else ∞;   F_eff = min(F_ice, 600 km)
wind sea:   Hs_ws = min(0.0246 U_eff²,  1.6e−3 U_eff √(F_eff/g))        [PM fully developed (WMO-702); JONSWAP fetch law g Hs/U² = 1.6e−3 (gF/U²)^½ (Hasselmann et al. 1973)]
            Tp_ws = min(0.75 U_eff,  0.286 (U_eff/g)(g F_eff/U_eff²)^{1/3})  s
swell:      Hs_sw = 3.0 · [0.55 + 0.45 e^{−((φ°+52)/12)²}] · M(t),   M = 1 + 0.20 sin(2πt/5 d + ϕ1) + 0.12 sin(2πt/9 d + ϕ2),   from 250°, T = 13 s   (UNVERIFIED: DJF swell 2.5–3.5 m in the 50s)
ice damping: inside (s > 0):  Φ = exp(−s/L_att),  L_att = 25 km · (T/10 s)² / max(C_pack, 0.5)      (Kohout et al. 2014: e-folding tens of km, longer for long waves)
             skirt (s < 0, SIC > 0):  Φ = 1 − 0.5 SIC
Hs = Φ √(Hs_ws² + Hs_sw²)  capped at 16 m;  Tp = Tp of the larger component;  direction = energy-weighted circular mean of (wind dir_from, 250°)
```
`F_eff = 600 km` is the fetch-equivalent of a 23 h, 20 m/s event (JONSWAP duration relation `g t/U = 68.8 (gF/U²)^{2/3}`): it stops a transient 25 m/s low from producing the 15 m fully-developed PM sea it never has time to build, and gives 10.5 m — a severe but real Southern Ocean storm sea. Checks: 11 m/s westerlies + swell → 4.2 m (DJF mean ≈ 4 m in the 50s, Sourced); 5 m/s at 35°S → 1.9 m; 100 km inside the pack a 13 s swell keeps 11 %, an 8 s wind sea 2 %.

The roughest-water-on-earth band is **emergent**: it is where the climatological westerlies, the storm track and the swell maximum coincide, 45–58°S. Nothing prescribes it; §10 asserts it.

---

## 5. Consistency graph — what derives from what, in evaluation order

```
seed ──hashing──► mode phases, storm calendars, eddies, meanders, textures            (construction, once)
grid ──geometry──► f, cos φ, d_coast, land mask, T_F(λ,φ)                             (per grid, cached)

[1]  P_clim(φ) + lows(t) + highs(t) + residual(t)          ──► P, ∂P/∂x, ∂P/∂y
[2]  (∇P, f)                                               ──► u_g, v_g
[3]  BL(0.70, 15° clockwise) + katabatic(d_c, t), cap        ──► u10, v10                         ← the served wind
[4]  φ_clim(λ,d) + ∫e^{−(t−t')/τ} V_n dt'  (V_n from [3] and [8] at the edge, 1-D, memoised) ──► edge table φ_E(λ), φ_E', V_on(λ)
[5]  s(φ_E), W(V_on), C_pack(d), texture(t), fast ice, polynyas(v10 at sites)   ──► SIC
[6]  (T_F, s, SIC)                                          ──► SST
[7]  (SST, SIC) → T_sfc;  back-trajectory with 0.7·u_g       ──► T2m
[8]  streamfunction(fronts, coastal, eddies(t), gyre)        ──► u_c, v_c        (independent of the atmosphere; feeds [4] and [10])
[9]  (u10 @ t, u10 @ t−6h, s, SIC, swell(t))                 ──► Hs, Tp, dir
[10] (T2m, T_sfc, u10, P−P_clim, SIC, d_c)                   ──► visibility
[11] (u_c, u10, SIC) ──Heun, memoised──► berg tracks         ──► berg_state(t), regime R
[12] along_track(route waypoints × ETA)                      ──► gates / route health   (outside isih/sim)
```
There is no cycle: the ice uses the wind, the thermodynamics use the ice, the wind never uses either (the stability refinement in §4.2 is deferred precisely to keep it that way). `World.fields()` evaluates once in this order and shares every intermediate; per-field endpoints call the same code path with a subset flag.

---

## 6. Icebergs — interface to the real drift closure

`models/iceberg/drift.iceberg_velocity(u_current, v_current, u_wind, v_wind, lat_deg, length_m, width_m)` is a **velocity** closure; positions are its time integral, and a trajectory has no closed form. So bergs are the one place the model integrates — in 0-D, once, as a pure function of the seed:

- **Population** (`seed_population`): `N_b` from the scenario (default 24). Length `L` log-uniform in `[150 m, 12 km]` (below USNIC's 10 NM naming floor — these are the *unnamed* bergs a bridge actually meets), `W/L ∈ [0.5, 0.9]`. Positions by rejection sampling from `ρ(λ, φ) ∝ exp(−((φ − φ_E(λ, 0))/2.5°)²)` for `φ > φ_E(λ,0) − 6°`, rejecting land, `SIC > 0.9` and `d_c < 10 km` — bergs cluster around and inside the initial edge and thin out northward to ~55°S, where the charted iceberg limit is.
- **Integration** (`integrate_tracks`): Heun (RK2), `Δt = 3600 s`, vectorised across bergs, from `t = 0` to `horizon` (default 60 d). Each step samples `world.current` and `world.wind10` at the berg positions (point evaluation, not a grid). Pack coupling: `v_b = (1 − χ) v_WDE + χ v_ice`, `χ = clip((SIC − 0.6)/0.3, 0, 1)`, `v_ice` the free-drift law of §4.4.2 — a berg locked in 90 % pack moves with the pack (WDE17 has no pack term). Grounding: land or `d_c < 5 km` → velocity 0 thereafter, flag set. Position update `Δλ = uΔt/(R_E cos φ)`, `Δφ = vΔt/R_E`.
- **Memo**: the `(N_b, N_t+1)` arrays of lat, lon, u, v, grounded are computed lazily once per `World` and cached; ~2880 point evaluations ≈ 1 s at startup (do it in the app's `lifespan` warm-up, like the existing NSIDC preload). `berg_state(t)` linearly interpolates position between the bracketing hourly samples; velocity from the nearest sample. Extending the horizon appends deterministically.
- **Regime**: `relative_wind_forcing()` per berg is reported with the position (R > 1 wind-dominated, R < 0.1 current-dominated) — the honest statement that a 10 km berg's track is the current field's track. Size decay is ignored (position is the decision variable; ~10–20 % length loss in 60 days, UNVERIFIED, does not change a separation).
- **Nothing is scripted.** A demo world in which a berg closes on the planned track is found by *searching seeds* and recording the one chosen in the scenario file ("seed 26059: berg 7 crosses leg 31 on day 9"). Emergent, reproducible, and the operator can prove it by changing the seed.
- **Forecast-uncertainty hook (not v1)**: `World.perturbed(k, t_issue)` = identical world for `t ≤ t_issue`, storm calendar re-drawn from `(seed, k)` after it. An ensemble of `k` gives a spread of edge positions and berg tracks after the issue time — the honest route to §48A.31 "robust routing" that `docs/backlog.md` lists as absent.

---

## 7. Seed, scenario, API surface

### 7.1 Where the seed lives
`isih/sim/scenarios/<id>.json` (committed):
```json
{ "id": "demo-season", "seed": 26059, "epoch": "2026-12-01T00:00:00Z", "horizon_days": 60, "bergs": 24,
  "notes": "seed chosen because berg 7 crosses leg 31 on day 9 and a 968 hPa low passes 55S 40E on day 4; nothing is scripted" }
```
Resolution order: `?seed=` query (exploration) → `ISIH_SCENARIO=<path>` env → the committed default. `World` instances are cached per `(seed, epoch)` in a small LRU. Every response carries `"world": {"seed", "epoch", "t", "sim_version"}` so any screenshot is reproducible from its own caption.

### 7.2 Endpoints (contract only)
- `GET /api/world/fields?t=<hours|ISO>&bbox=&nx=&ny=&which=mslp,wind,waves,current,sic,sst,t2m,vis` → axes + per-field grids + world stamp.
- `GET /api/world/point?lat&lon&t` → all fields at a point.
- `GET /api/world/edge?t` → 15 % edge polyline (from the edge table) and the 80 % contour.
- `GET /api/world/bergs?t` → id, lat, lon, u, v, L, W, R, grounded.
- `GET /api/world/track?depart=` → along-track samples at each planned waypoint's ETA, for the gates.

### 7.3 Serialisation
40 000 points × 10 fields as JSON lists costs more than the physics. Serve grids as base64 `float32` (or `uint8` for SIC %) with `nx, ny, lat0, dlat, lon0, dlon`; the chart decodes to a `Float32Array`. `null` for land via a separate `uint8` mask.

### 7.4 Provenance label (required change)
`isih/demo/static/provenance.js` currently marks `chart.ice / wind / wave / current` as **replay** ("real physics or real data, advanced to demo time"). This world has no real data in it. Add a fourth kind, `synthetic` (hollow dot), with why-text `"physics-based synthetic environment, seed N — real equations, synthetic initial state; SIMULATED INPUT, not a forecast"`. That is master prompt §27's label, verbatim in spirit, and it pre-empts the "so what else is fake" question the run-of-show warns about.

---

## 8. Performance budget (measured, sandbox numpy 2.5 / py3.14, single core)

| Piece | Cost per 200×200 request |
|---|---|
| P + ∇P: 14 blobs + 16 modes + climatology, and fronts/misc | **14.4 ms measured** (§3.3/3.4 term counts) |
| second wind evaluation at `t − 6 h` (waves) | ≈ 10 ms |
| SIC (edge interp, 12-mode texture, fast ice, 4 polynyas) | ≈ 6 ms |
| SST + T2m (second `T_sfc` at the upwind point) | ≈ 5 ms |
| waves, visibility | ≈ 4 ms |
| edge integral: cold 144 samples | **8.4 ms measured**; warm ≈ 0.2 ms |
| **Total** | **≈ 50 ms cold, ≈ 40 ms warm** — under the 100 ms budget with margin; §10 asserts < 100 ms and fails at 200 ms |

Static per-grid work (`T_F`, `f`, `cos φ`, `d_c`, land mask) is cached and costs nothing per request. Berg tracks: ≈ 1 s once per world at warm-up.

---

## 9. How this could look fake to an expert — and the decision that prevents it

| Tell-tale | Prevented by |
|---|---|
| Wind circulating anticlockwise around a low (NH sign) | `f` signed; test: east of every alive low centre `v10 < 0` |
| Surface wind exactly along the isobars | 15° clockwise cross-isobar turning; test: `u10·∇P < 0` wherever `|∇P| > 0.5 hPa/100 km` |
| Lows that sit still, or pop into existence | Hash-indexed calendar: each low peaks inside the sector, moves ESE at 9–15 m/s, deepens and fills over ~5 days; test: centre pressure is continuous in `t` and the low's position at `t+6 h` is 200–320 km ESE |
| Wind backing the wrong way as a low passes south of the ship | Emergent from clockwise flow + eastward motion: NW → W → SW (backing); test on a fixed point north of a track |
| Waves that jump the instant the wind changes; flat calm in light winds | `U_eff` lags 6 h; swell floor 1.9–3.6 m; test: `|dHs/dt| < 1 m/h` |
| Swell rolling through 90 % pack | Exponential attenuation with `L_att ≈ 25–45 km`; test: `Hs < 0.3 m` where `SIC > 0.8` and `s > 100 km` |
| A ruler-straight or stationary ice edge; an edge that moves without a wind to move it | Meandered climatology + relaxation integral driven by the on-ice wind; test: sign of `∂η/∂t` follows `V_n`; `|∂φ_E/∂t| ≤ 45 km/day` |
| Ice north of the Polar Front in February; a warm pool at the edge | Fitted climatology (Feb edge 65.5–69°S); SST slaved to the edge; test: `SST ≤ −1.5 °C` wherever `SIC > 0.15` |
| Fog painted as a noise blob | Fog only where the back-trajectory brings air ≥ 4 °C warmer than the local surface; test: no fog where `T2m − T_sfc < 1.5`; MIZ fog fraction 10–50 % over a month; < 5 % at 40°S in a southerly |
| ACC flowing west, bergs drifting west at 55°S, bergs converging into lines | Streamfunction with eastward jets; exactly non-divergent; test: zonal-mean `u_c > 0` in 45–58°S, `< 0` within 120 km of the coast; `|div| < 1e-7 s⁻¹` |
| A 10 km berg steered by the wind | WDE17 regime `R` reported per berg; test: `R < 0.1` for `L > 5 km` in 10 m/s wind |
| Perfect circles for lows and eddies | 3 hPa residual field bends them; meanders bend the jets. Still idealised — say so on the label (§7.4) rather than hide it |
| Two machines, two worlds for one seed | blake2b draws; golden-hash test of `fields(seed=26059, t=15 d)` |
| Diurnal cycle at 65°S in December | None modelled: 24 h daylight. Nothing to prevent |

---

## 10. Test plan — `isih/sim/test_sim_properties.py`

All tests use `World(seed=26059, epoch=2026-12-01)` and a 120×120 grid unless stated; "over a month" = 120 samples at 6 h.

**Determinism**
1. `fields(t)` from two `World` instances are bit-identical (`np.array_equal`), for `t ∈ {0, 15 d, 59 d}`.
2. Golden `blake2b` of `fields(t=15 d)` bytes equals the committed constant; the test file states how to regenerate it and that regenerating it is a physics change requiring a `SIM_VERSION` bump.
3. Same golden run in a subprocess with `PYTHONHASHSEED=0` and `=1`: identical.
4. `berg_state(t)` golden hash; extending the horizon does not change earlier samples.

**Domain and finiteness**
5. No NaN/inf off land in any field; NaN exactly on land.
6. `(lat, lon)` outside the box → `DomainError`; `d` outside `[−5, 100]` → `SeasonError`.

**Signs (the examiner's checks)**
7. For every alive low with `E > 0.3`: `v10 < 0` 300 km east of the centre, `v10 > 0` 300 km west, `u10 > 0` north, `u10 < 0` south.
8. `u10·∇P < 0` on ≥ 99 % of cells where `|∇P| > 0.5 hPa/100 km`.
9. Zonal-mean `u10 > 0` in 45–58°S and `< 0` south of 68°S (polar easterlies + katabatics).
10. Ice drift direction is left of the wind: angle(`v_ice − u_c`, `u10`) = +20° ± 1°.
11. Eddy with `A > 0`: `v < 0` east of the centre (clockwise).

**Magnitudes (over a month)**
12. 10 m wind p50 in 45–60°S ∈ [8, 14] m/s; p99 < 35; max < 40; cap hits = 0.
13. MSLP ∈ [935, 1045] hPa; count of alive lows with `E > 0.3` inside the sector ∈ [2, 6] on ≥ 90 % of samples.
14. Hs p50 in 45–58°S ∈ [3.0, 5.5] m and larger than in both 30–40°S and 62–70°S (emergent roughest band); Hs max < 16 m.
15. Current: max `|u_c| < 1.2 m/s`; jet cores 0.2–0.6 m/s; `|div| < 1e-7 s⁻¹` from finite differences on the grid.
16. SST monotone in the zonal mean from 78°S to 26°S; steps of 2–4 °C at PF/SAF/STF within 1° of the table.

**Ice coherence**
17. `SIC ∈ [0, 1]`; `SIC = 0` more than 150 km north of the edge; `SIC ≥ 0.85` within the fast-ice band.
18. 15→80 % MIZ width (per longitude, meridional) ∈ [40, 500] km; median on `d = 0` ∈ [150, 350] km, on `d = 60` ∈ [40, 120] km (matches §4.4.1 measurements).
19. Sector ice area, 7-day mean, decreases monotonically from `d = 0` to `d = 75`.
20. Construct `t` with a sustained northerly at 40°E (search samples): `η(40°E)` decreases and the MIZ narrows; sustained southerly: the reverse.
21. `σ(η)` over the month ∈ [10, 35] km at 46–62°E (calibrates `τ_E` against the measured 11–22 km).
22. `|SST + 1.8| < 0.5` wherever `0.15 < SIC < 0.9`; `SST ≤ −1.5` wherever `SIC > 0.15`.

**Thermo and visibility**
23. Where `T2m − T_sfc < 1.5`: `vis ≥ 10 km` unless `s_p` or `s_bs > 0`. Fog fraction (vis < 1 km) in the band `s ∈ [−150, +50] km` over a month ∈ [0.10, 0.50]; at 40°S with `v10 > 3 m/s` < 0.05.
24. Blowing snow: 20 m/s over `SIC = 0.9` → `vis ≤ 200 m`.

**Continuity in time**
25. Between `t` and `t + 60 s`: `max|ΔP| < 0.1 hPa`, `max|ΔHs| < 0.05 m`, `max|Δη| < 1 km`, `max|ΔSIC| < 0.01` — including across a 3 h quadrature boundary and a storm-slot boundary.

**Bergs**
26. `|v_b| ≤ |u_c| + 0.03 |u10| + 1e-6`; no berg on land; grounded bergs stay put; `R < 0.1` for all bergs with `L > 5 km` at 10 m/s.

**Performance**
27. `fields()` on 200×200, cold world: median of 10 < 100 ms (fail > 200 ms); warm < 60 ms.

---

## 11. Deliberate simplifications (crude on purpose; none changes a navigation decision)

- **No fronts as lines.** A cold front's operational content is the wind shift and the pressure kink; the passing low's clockwise circulation supplies the backing NW→W→SW, and the residual field supplies the trough.
- **No gradient-wind curvature correction** (sub-geostrophic cores, ≤ 25 % in the deepest lows). The 0.7 BL factor brackets it; decisions key on wind bands and Hs, not on 3 m/s.
- **Fixed BL stability.** The stability variant is written down (§4.2) and left out to keep the graph acyclic.
- **No tides, no diurnal cycle.** Irrelevant offshore in 24-h daylight.
- **Swell from remote storms not resolved** — a climatological WSW swell with slow seeded modulation.
- **Static SST fronts and meanders.** Eddies move the SST by < 1 °C; fog keys on the 4–6 °C edge contrast.
- **Scalar concentration only** — no thickness, stage or type, the same limitation the backlog records for the real product ([major][model]); POLARIS needs type and is out of scope here too.
- **Berg size decay ignored**; **Ekman drift ignored**; **precipitation only as a visibility proxy**; **islands are masks**.
- **`V_n` sampled at the climatological edge** (5 % error on a 20 km displacement).

---

## 12. Function signatures

```python
# isih/sim/hashing.py
def uniform(seed: int, tag: str, index: int, n: int = 1) -> np.ndarray          # float64 in [0, 1), shape (n,)
def normal(seed: int, tag: str, index: int, n: int = 1) -> np.ndarray

# isih/sim/geometry.py
R_EARTH: float = 6_371_000.0
OMEGA: float = 7.2921e-5
class DomainError(ValueError): ...
def check_domain(lat_deg, lon_deg) -> None                                        # raises DomainError
def coriolis(lat_deg) -> np.ndarray                                               # signed; raises DomainError if lat > -20
def coast_lat(lon_deg) -> np.ndarray
def coast_slope(lon_deg) -> np.ndarray                                            # dφ_coast/dλ, rad/rad
def distance_to_coast_m(lat_deg, lon_deg) -> np.ndarray                           # +offshore
def land_mask(lat2d: np.ndarray, lon2d: np.ndarray) -> np.ndarray                 # bool; cached per Grid by World

# isih/sim/spectral.py
@dataclass(frozen=True)
class PlaneWaves:
    m: np.ndarray; l: np.ndarray; omega: np.ndarray; phase: np.ndarray; amp: np.ndarray
    @classmethod
    def from_seed(cls, seed: int, tag: str, n_modes: int, m_range: tuple[int, int],
                  lam_phi_deg: tuple[float, float], slope: float, rms: float,
                  u_steer_ms: float, omega_jitter: float = 0.3) -> "PlaneWaves"
    def value(self, lam, phi, t: float) -> np.ndarray
    def value_grad(self, lam, phi, t: float, envelope=None) -> tuple[np.ndarray, np.ndarray, np.ndarray]   # (p, dp/dx, dp/dy) true metric
@dataclass(frozen=True)
class Blobs:
    lam0: np.ndarray; phi0: np.ndarray; omega: np.ndarray; phi_rate: np.ndarray
    t_peak: np.ndarray; sigma_t: np.ndarray; radius_m: np.ndarray; amp: np.ndarray
    def alive(self, t: float, threshold: float = 0.002) -> "Blobs"
    def value_grad(self, lam, phi, t: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]

# isih/sim/synoptic.py
def climatological_mslp(lat_deg) -> tuple[np.ndarray, np.ndarray]                # (hPa, hPa/deg)
def storm_slots(seed: int, t: float, kind: Literal["low", "high"]) -> Blobs       # hash-indexed calendar, alive subset
def mslp_grad(world: "World", lam, phi, t: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]   # Pa, Pa/m, Pa/m

# isih/sim/wind.py
def geostrophic(dpdx, dpdy, lat_deg) -> tuple[np.ndarray, np.ndarray]
def boundary_layer(ug, vg, lat_deg, alpha: float = 0.70, turn_deg: float = 15.0) -> tuple[np.ndarray, np.ndarray]
def katabatic(world, lat_deg, lon_deg, t: float) -> tuple[np.ndarray, np.ndarray]
def wind10(world, lat_deg, lon_deg, t: float, *, grad=None) -> tuple[np.ndarray, np.ndarray]

# isih/sim/ocean.py
def front_latitude(world, name: str, lon_deg) -> np.ndarray                       # with meanders, degrees
def front_slope(world, name: str, lon_deg) -> np.ndarray                          # rad/rad
def streamfunction_grad(world, lam, phi, t: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]   # (psi, dpsi/dx, dpsi/dy)
def current(world, lat_deg, lon_deg, t: float) -> tuple[np.ndarray, np.ndarray]
def sst_frontal(world, lat_deg, lon_deg) -> np.ndarray                            # °C, static

# isih/sim/ice.py
class SeasonError(ValueError): ...
def days_since_dec1(world, t: float) -> float                                      # raises SeasonError outside [-5, 100]
def edge_climatology(lon_deg, d: float) -> np.ndarray                             # fitted table, coast floor applied
@dataclass(frozen=True)
class EdgeTable:
    lon: np.ndarray; lat: np.ndarray; slope: np.ndarray; v_on: np.ndarray; t: float
def edge_table(world, t: float) -> EdgeTable                                       # memoised quadrature samples
def signed_distance_m(edge: EdgeTable, lat_deg, lon_deg) -> np.ndarray            # +inside
def miz_scale_m(edge: EdgeTable, d: float) -> np.ndarray                           # W(λ)
def sic(world, lat_deg, lon_deg, t: float, *, edge=None, u10=None, v10=None) -> np.ndarray

# isih/sim/thermo.py
def sst(world, lat_deg, lon_deg, t: float, *, s=None, sic_=None) -> np.ndarray
def t2m(world, lat_deg, lon_deg, t: float, *, sst_, sic_, ug, vg) -> np.ndarray
def visibility_m(world, lat_deg, lon_deg, t: float, *, t2m_, t_sfc, u10, v10, p_anom_pa, sic_) -> np.ndarray

# isih/sim/waves.py
@dataclass(frozen=True)
class WaveState: hs: np.ndarray; tp: np.ndarray; dir_from_deg: np.ndarray; hs_windsea: np.ndarray; hs_swell: np.ndarray
def fully_developed_hs(u10_speed) -> np.ndarray
def fetch_limited_hs(u10_speed, fetch_m) -> np.ndarray
def waves(world, lat_deg, lon_deg, t: float, *, u10, v10, u10_prev, v10_prev, s, sic_, c_pack) -> WaveState

# isih/sim/bergs.py
@dataclass(frozen=True)
class BergPopulation: ids: np.ndarray; length_m: np.ndarray; width_m: np.ndarray; lat0: np.ndarray; lon0: np.ndarray
@dataclass(frozen=True)
class BergTracks: t: np.ndarray; lat: np.ndarray; lon: np.ndarray; u: np.ndarray; v: np.ndarray; grounded: np.ndarray   # (N_b, N_t+1)
@dataclass(frozen=True)
class BergState: ids; lat; lon; u; v; length_m; width_m; regime_R; grounded
def seed_population(world, n: int) -> BergPopulation
def integrate_tracks(world, pop: BergPopulation, t_end: float, dt_s: float = 3600.0) -> BergTracks
def berg_state(world, t: float) -> BergState

# isih/sim/world.py
@dataclass(frozen=True)
class Grid:
    lat0: float; lat1: float; lon0: float; lon1: float; ny: int; nx: int
    def mesh(self) -> tuple[np.ndarray, np.ndarray]                                # (lat2d, lon2d)
class World:
    def __init__(self, seed: int, epoch: datetime, horizon_days: float = 60.0, n_bergs: int = 24): ...
    @classmethod
    def from_scenario(cls, path: str | Path) -> "World"
    def time_at(self, when: datetime | str) -> float                              # seconds since epoch
    def fields(self, grid: Grid, t: float, which: tuple[str, ...] = ALL_FIELDS) -> dict[str, np.ndarray]
    def point(self, lat_deg, lon_deg, t: float) -> dict[str, np.ndarray]
    def along_track(self, lat_deg: np.ndarray, lon_deg: np.ndarray, t: np.ndarray) -> dict[str, np.ndarray]
    def edge(self, t: float) -> EdgeTable
    def bergs(self, t: float) -> BergState
    def stamp(self, t: float) -> dict                                              # {"seed","epoch","t","sim_version"}
```

---

## 13. What survives from the draft `isih/sim/{noise,fields}.py`, and what is replaced

Keep (rewritten in place): the Fourier-with-exact-gradient idea (→ `PlaneWaves`, now hashed phases, radian `(λ, φ)` wavenumbers, physical `ω`, product-rule envelope); the sign conventions and the clockwise BL turning in `wind()`; the PM constant `0.0246 U²`; the "eddies are a streamfunction" idea (→ the whole current is one); the framing of fog as air–sea temperature difference.

Replace: `np.random.default_rng` streams (§3.1); the dimensionless "drift" frequencies (§3.3 — their comment claims long waves are slower, the formula makes them faster); no explicit cyclones (§4.1); fixed-latitude, purely zonal jets 300 km off the coast (§4.3); waves keyed to a latitude smoothstep and SIC value rather than to the edge and the distance inside it (§4.8); `Tp = 3.86√Hs` (PM gives `5.0√Hs`); air temperature and SST linear in `|lat|` with no fronts (§4.3, 4.6); fog modulated by a moisture noise field (§4.7); no sea-ice model at all — the draft takes `sic` as an input nothing provides (§4.4); no time semantics, seed placement, berg integration or tests.

---

## 14. UNVERIFIED register (also one-lined in `docs/backlog.md`)

Front positions ±1.5°; DJF zonal-mean MSLP ±3 hPa; katabatic mean 7 m/s; eddy drift 0.04 m/s; Prydz gyre sense; polynya sites other than Cape Darnley; fast-ice widths and mid-January break-out; `τ_E = 3 d`; summer pack surface −5.8 °C; `r = 0.6`, −1 °C air–sea offset; dew-point depression 1.5 °C; MIZ summer fog 20–40 %; swell 2.5–3.5 m; `F_eff = 600 km`; berg size decay. The **Measured** items — coast table, edge climatology, MIZ widths, interior SIC, edge wobble — are reproducible from the two scripts run for this document against `isih/data/nsidc_sic` and `isih/figures/coastline.json`; the implementer should commit those scripts under `isih/sim/fit/` so the table has provenance in code.
