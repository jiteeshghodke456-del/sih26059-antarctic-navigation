# Gap Analysis — SIH26059 Antarctic Navigation

## Methodology landscape

Research pass for the three ML sub-problems (sea-ice forecasting, iceberg trajectory
prediction, ship routing) so the architecture decision is evidence-based, not guessed.
Dense/technical — engineering input for `docs/ML_ARCHITECTURE.md`, not a lit review.

---

### 1. Sea-ice concentration forecasting

**State of the art — deep learning**

- **IceNet** (British Antarctic Survey + Alan Turing Institute). Ensemble of U-Net CNNs
  trained on ~50 input variables (CMIP6 climate-simulation runs + observational
  reanalysis: SIC history, surface temp, radiation fields) to forecast monthly-mean sea
  ice **probability/concentration** up to 6 months ahead, on the EASE2 polar grid, 432×432
  px at **25 km resolution**. Research code: [tom-andersson/icenet-paper](https://github.com/tom-andersson/icenet-paper)
  (paper: [Nature Communications 2021, "Seasonal Arctic sea ice forecasting with
  probabilistic deep learning"](https://www.nature.com/articles/s41467-021-25257-4)).
  Operational refactor as an installable library: [icenet-ai/icenet](https://github.com/icenet-ai/icenet)
  (MIT license, pip-installable), now moving to daily-resolution operational forecasts
  and a multimodal pipeline (IceNet-MP) for raw non-gridded observations. Project page:
  [icenet.ai](https://icenet.ai/), [BAS project page](https://www.bas.ac.uk/project/icenet/).
  **Antarctic coverage confirmed**: [icenet-ai/icenet-sipn-south](https://github.com/icenet-ai/icenet-sipn-south)
  is a Southern-Hemisphere IceNet configuration/pipeline built for SIPN South (Sea Ice
  Prediction Network South), producing Antarctic circumpolar daily-mean sea-ice-area
  diagnostics — the repo states explicitly "this code is meant for the Southern
  hemisphere." Confirmed **research-stage, not a mature production drop-in**: it depends
  on the separate `icenet-pipeline` for training/inference, is documented as tested only
  on Linux x86, and there is no published pretrained Southern Hemisphere weight file
  found in this pass — a team would need to run the training pipeline against Antarctic
  reanalysis + SIC records themselves (same OSI-SAF/NSIDC products used for the Arctic
  configuration, see Data Reality Check below) rather than download finished weights.
  Net: the architecture and code are legitimately reusable/adaptable for Antarctic use
  (this is the strongest "reuse → adapt" candidate found for step 1), but "usable" means
  "adapt and retrain," not "download and run."
- Reported skill: DL sea-ice models beat persistence by up to **~41% lower RMSE**, and
  beat ECMWF's operational dynamical seasonal system **SEAS5** for lead times ≥2 months
  (transformer variant: +7.7–10.6% detrended ACC on Sept. extent vs SEAS5 depending on
  initialization month) — [Copernicus TC 2024/2025 papers](https://tc.copernicus.org/articles/18/2161/2024/),
  [Nature Comms 2021](https://www.nature.com/articles/s41467-021-25257-4). DL inference is
  reported as **>2000× faster** than running SEAS5 on a supercomputer, since SEAS5 is a
  full coupled dynamical run and IceNet-class models are a forward NN pass.
- Short-term post-processing DL (bias-correcting TOPAZ4) improves skill at **1–10 day**
  lead times too — this is the more relevant regime for a navigation-decision-support
  tool with a multi-day voyage horizon, not the 6-month seasonal regime IceNet targets.

**Physical/dynamical models**

- **SEAS5** (ECMWF) — coupled ocean-atmosphere-ice seasonal forecast system, operational
  since Nov 2017. Sea-ice component is **LIM2** (Louvain-la-Neuve Sea Ice Model v2,
  Fichefet & Maqueda 1997), part of the NEMO ocean framework on the same tripolar
  ORCA0.25° grid, dynamic-thermodynamic, single ice-thickness category, hourly timestep
  ([SEAS5 description paper, GMD 2019](https://gmd.copernicus.org/articles/12/1087/2019/)).
  Physically grounded, computationally expensive (full coupled dynamical run), and
  weaker than DL at seasonal sea-ice skill per above.
- **CICE** (Los Alamos Sea Ice Model) — the community dynamical sea-ice model used inside
  most operational coupled systems (NCAR CESM, UK Met Office, others). Combines a
  vertical thermodynamic model (conductive/radiative/turbulent heat fluxes + snowfall),
  an **elastic-viscous-plastic (EVP)** rheology for ice dynamics/velocity, incremental
  remapping for horizontal advection, and a ridging parameterization across thickness
  categories ([CICE documentation/user's manual](https://csdms.colorado.edu/w/images/CICE_documentation_and_software_user's_manual.pdf)).
  Not something a hackathon team stands up from scratch in the timeline available — it's
  infrastructure other operational centers run, not a component to reimplement.

**Statistical baselines**

- **Persistence** (tomorrow's SIC = today's SIC) and **climatological anomaly persistence**
  are the standard skill floor DL/dynamical papers benchmark against. Trivial to
  implement, zero training cost, and the number to beat to claim "the model adds value."

**Realistic accuracy/lead-time tradeoff**

| Lead time | Best approach | Typical skill vs persistence |
|---|---|---|
| 1–10 days | DL bias-correction on top of a short-range ice-ocean model (e.g. TOPAZ4), or a lightweight CNN/ConvLSTM trained directly on satellite SIC time series | Meaningful skill gain is well established at this range; this is the regime a prototype should target |
| Weeks–seasonal (2–6 mo) | IceNet-class ensemble U-Net | Beats SEAS5 and persistence, but needs the CMIP6 pretraining + large observational archive IceNet was built on |

**Simplest defensible baseline**: persistence + a short-lead ConvLSTM/U-Net trained
directly on the real satellite SIC time series (OSI-SAF/NSIDC, see Data Reality Check),
predicting a few days ahead at native ~10–25 km grid resolution. This is honestly
trainable inside an SIH timeline on real data and has literature precedent.
**What would justify going further**: only if (a) Southern-Hemisphere-adapted IceNet
weights or an equivalent pretrained Antarctic model surface, or (b) there's time/compute
to pretrain on CMIP6 the way IceNet did — neither is likely in-scope; going past the
short-lead DL baseline to a full seasonal ensemble should be treated as a stretch goal,
not the deliverable.

---

### 2. Iceberg trajectory prediction

**Physics-based drift models (Bigg / Wagner family)**

- **Bigg et al. (1990s)**, building on Crépon et al.: iceberg momentum balance = wind
  drag + ocean-current drag + Coriolis + (sometimes) sea-surface tilt/pressure-gradient
  force, integrated via Newton's second law over iceberg mass. Empirical "2% of wind
  speed" rule for drift is a simplification of this that **only holds for small
  icebergs / strong-wind regimes** — explicitly does *not* hold for large Antarctic
  tabular bergs, which move mainly with the ocean surface current.
- **Wagner, Dell & Eisenman (2017), "An Analytical Model of Iceberg Drift"** (*J. Phys.
  Oceanogr.* 47(7); [arXiv:1610.06403](https://arxiv.org/pdf/1610.06403),
  [DOI](https://journals.ametsoc.org/doi/abs/10.1175/JPO-D-16-0262.1),
  [MATLAB reference code](https://www.tillwagner.me/wde17)) gives a **closed-form
  solution**, not just a numerical integration: velocity
  `v_i = v_w + γ(α k̂×v_a + β v_a)`, where `v_w` = ocean current velocity, `v_a` = wind
  velocity, `γ = sqrt[(ρ_a(ρ_w−ρ_i))/(ρ_w ρ_i) · C_a/C_w]` is a dimensionless
  air/water-drag ratio, and `α, β` are dimensionless functions of
  `Λ ≡ γ C_w |v_a| / (π f S)` (f = Coriolis parameter, S = harmonic mean of iceberg
  length/width) that capture the Coriolis-deflection regime. Required inputs: iceberg
  horizontal dimensions (L, W) and draft/mass, local wind vector, local ocean-current
  vector, latitude (for f). This is genuinely runnable with only real, obtainable inputs
  — no fitted parameters beyond standard drag coefficients (C_a, C_w) from the
  literature.

**ML approaches**

- **BYU/NIC Antarctic Iceberg Tracking Database** — the standard real dataset: BYU
  scatterometer-derived daily positions (1978–1999-era Seasat/ERS/QuikSCAT, continuing
  with ASCAT/OSCAT-2) merged with NIC's weekly optical/IR-derived positions. Consolidated
  file covers 1978–Aug 2023, CSV format, publicly downloadable:
  [scp.byu.edu/data/iceberg_archives](https://www.scp.byu.edu/data/iceberg_archives/older_iceberg/database1.html),
  underlying methodology in [Budge & Long, IEEE JSTARS 2018](https://www.scp.byu.edu/long/papers/JSTARS2018_budge.pdf).
  **Important limitation for ML training**: this only tracks *large tabular* icebergs
  (scatterometer/optical detection threshold is on the order of km-scale), at daily
  (scatterometer era) or weekly (NIC era) cadence — sparse in time and covering only the
  large end of the size distribution that matters most for "does this berg calve into
  many smaller growlers a ship actually collides with." Not dense enough on its own to
  train a data-hungry sequence model without heavy augmentation or synthetic
  interpolation (which would violate the project's no-dummy-data rule if used as-is
  rather than as legitimate resampling of real tracks).
- **IDRIFTNET (2025)** — physics-driven hybrid: Wagner analytical drift as the base
  trajectory, plus a residual spectral neural network trained to learn the *mismatch*
  between the analytical prediction and observed USNIC positions (2014–2025), using
  ERA5 winds and CMEMS ocean currents as ML inputs
  ([arXiv:2507.00036](https://arxiv.org/html/2507.00036)). Reported gains over the pure
  Wagner physics baseline: **Average Displacement Error reduced ~67–82%**, Final
  Displacement Error reduced ~46–73%, across two evaluation datasets (physics-only ADE
  127–147 km vs. hybrid 23–49 km). The paper's own stated motivation for going hybrid
  rather than pure ML: iceberg drift is more nonlinear than typical trajectory-ML
  problems, and **pure neural approaches converge poorly on the amount of real data
  actually available** — physics-informed residual learning is used specifically to
  narrow the model's search space in this "data-scarce regime."
- Separate line of work: **random-forest / SAR-based classification** for iceberg
  *detection/tracking* from imagery (not trajectory forecasting per se) — relevant only
  if the product also needs to detect bergs from raw SAR, which is out of scope for a
  routing/forecast decision-support tool that can consume existing BYU/NIC/USNIC
  position feeds instead.

**Simplest defensible baseline**: implement the **Wagner (2017) closed-form drift model**
directly — it's real physics, needs only real inputs (wind reanalysis, ocean-current
reanalysis, iceberg geometry from tracking records), requires zero training data, and is
literally the physics component every ML paper in this space still uses as its base
case. This is the more honest choice for a prototype than a from-scratch ML trajectory
model, given BYU/NIC data sparsity.
**What would justify going further**: the IDRIFTNET literature shows the residual-ML
correction *does* meaningfully help (real, published, large error reduction) — so a
stretch goal is a physics-first drift model with a lightweight residual-correction layer
trained on whatever real BYU/NIC/USNIC track segments are available in the Antarctic
sector, framed explicitly as "physics baseline + learned correction," never a bare ML
model presented as if it were adequately trained (SIH judges will and should ask about
training-set size for a trajectory-ML claim).

---

### 3. Ship routing under ice/weather constraints

**Established algorithms**

- **Isochrone method** — originated specifically for ship navigation; builds successive
  wavefronts of "reachable in time T" points from the origin, subject to speed/fuel
  limits from local conditions, then traces back the optimal path. Classic and still
  used in weather-routing production tools; efficient but historically less rigorous
  about guaranteeing the true optimum than graph search.
- **Dijkstra / A\* on a cost-weighted grid or non-uniform mesh** — now the dominant
  approach in recent literature; both guarantee optimality on the discretized graph.
  A* has specifically been used for adaptive/ice-aware routing (heuristic-guided search
  reduces node expansion vs. plain Dijkstra on large polar grids). Representative recent
  literature: [modified-Dijkstra weather routing](https://www.researchgate.net/publication/308586823_Ship_weather_routing_based_on_modified_Dijkstra_algorithm),
  [CMEMS-driven A* weather routing](https://www.researchgate.net/publication/360721330_A_comprehensive_ship_weather_routing_system_using_CMEMS_products_and_A_algorithm),
  [state-of-the-art review, ScienceDirect 2025](https://www.sciencedirect.com/science/article/pii/S0029801825009114),
  [Arctic weather-routing review, Frontiers in Marine Science 2023](https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2023.1190164/full).
  Multi-objective variants jointly optimize distance/time/fuel/risk, with risk terms
  built from **ice concentration + ice thickness + deviation from a vessel's safe-speed
  envelope** as the cost inputs.

**Existing open-source polar routing tool — directly relevant, found via search**

- **PolarRoute** (British Antarctic Survey AI Lab / AMOP team) —
  [github.com/antarctica/PolarRoute](https://github.com/antarctica/PolarRoute), also
  mirrored at [bas-amop/PolarRoute](https://github.com/bas-amop/PolarRoute), installable
  via `pip install polar-route` ([PyPI](https://pypi.org/project/polar-route/)), MIT
  licensed, actively maintained (1,800+ commits). This is the closest thing to an
  existing solution to problem statement SIH26059 — built by the same institution (BAS)
  behind IceNet, explicitly for "safe and efficient navigation in the remote reaches of
  the Southern Ocean" ([BAS Logist AI project page](https://www.bas.ac.uk/project/logist-ai-for-environmentally-aware-decision-support/),
  [Maritime Executive coverage](https://maritime-executive.com/article/british-antarctic-survey-tests-ai-weather-routing-for-ice)).
  Three-stage pipeline: (1) discretize environmental conditions (ice, currents, weather)
  onto a **non-uniform mesh** via its companion library **MeshiPhi**, (2) compute
  mesh-optimal paths, (3) physics-informed path smoothing for a realistic vessel track.
  Vessel-specific speed/fuel-limit functions are data-driven, fit per mesh cell from
  vessel performance data. **Algorithm confirmed** via the underlying BAS methodology
  paper, [Fox-Kemper et al./Coles et al., "Long-Range Route-planning for Autonomous
  Vehicles in the Polar Oceans" (arXiv:2111.00293)](https://arxiv.org/pdf/2111.00293)
  and the companion aircraft-routing paper [arXiv:2209.02389](https://arxiv.org/pdf/2209.02389):
  the mesh is a graph with cell-centre vertices and edges to adjacent cells; **intra-cell
  optimal crossing points are solved with Newton's method, and the optimal route across
  the full mesh is then found with Dijkstra's algorithm** — the paper terms this the "3D
  dynamic shortest path" (3D-DSP) method (3D = 2 spatial + time, since the mesh/cost
  field is time-varying). This settles the open question: **Dijkstra, not A\***, over a
  non-uniform (variable-resolution) mesh rather than a regular grid. Repo/docs did not
  confirm dedicated iceberg-specific (vs. general ice concentration/thickness) hazard
  handling — worth checking the source directly before depending on it for iceberg risk
  specifically, since our step-2 output (drift-projected iceberg positions) may need to
  be injected as an extra masked/high-cost mesh layer rather than something PolarRoute
  natively models.
  **Given the "reuse → adapt → extend → wrap → replace" rule, this should be the first
  thing evaluated hands-on**: either integrate PolarRoute directly (wrapping it with our
  own SIC-forecast + iceberg-drift hazard layers as inputs to its mesh), or reimplement
  its core mesh+Dijkstra idea (regular-grid Dijkstra/A* is a reasonable simplification)
  if PolarRoute proves too heavy/inflexible for the prototype's UI integration needs.

**How hazard rasters from steps 1–2 combine with the routing graph**

Standard pattern across the literature: rasterize/regrid forecast SIC (step 1) and
iceberg positions + drift-model-projected future positions with an uncertainty buffer
(step 2) onto the same grid/mesh as the routing cost function, then combine into a
scalar or vector cost per cell, e.g. `cost(cell) = f(ice_concentration, ice_thickness,
iceberg_proximity_risk, wave_height, fuel_burn_rate(vessel, ice_state))`, with hard
exclusion (infinite cost / masked) above some concentration/thickness threshold the
vessel's ice class cannot transit, and continuous risk scaling below that. Multi-
objective formulations keep distance/time/fuel/risk as separate objectives and expose
a Pareto frontier or weighted-sum knob rather than collapsing to one number
(see [risk-expense Pareto routing, MDPI JMSE 2022](https://mdpi.com/2077-1312/10/7/862/htm)).

**Simplest defensible baseline**: A* over a regular lat/lon (or polar-stereographic)
grid, cost per cell = weighted sum of forecast SIC (step 1 output), iceberg-proximity
risk (step 2 output, buffered by drift-model position uncertainty), and distance/fuel —
hard-masking cells above a configurable safe-ice-concentration threshold. This is
straightforward to implement, matches the dominant pattern in the literature, and is
easy to demo/visualize.
**What would justify going further**: adopting or wrapping **PolarRoute**'s non-uniform
mesh + vessel-performance-function machinery gets closer to "real NCPOR/MoES-grade
tool" territory and demonstrates awareness of the actual prior art from the problem
statement's own domain (BAS runs Antarctic research vessels) — strong for judge
credibility if time allows hands-on integration; a plain grid A* is the fallback if
PolarRoute's mesh format proves too much integration overhead for the timeline.

---

### Data Reality Check (feeds all three sections above)

Real, currently-accessible sources confirmed during this pass — no synthetic data
required for any of the three sub-problems:

- **Sea-ice concentration**: OSI-SAF Global Sea Ice Concentration CDR/ICDR — daily,
  10 km resolution, Arctic + Antarctic, polar-stereographic, 1978–present (reprocessed
  OSI-450-a covers to 2020, OSI-430-a ICDR extends to present) — via
  [EUMETSAT OSI SAF](https://osisaf-hl.met.no/) / mirrored on
  [Copernicus Marine Service](https://data.marine.copernicus.eu/product/SEAICE_GLO_SEAICE_L4_NRT_OBSERVATIONS_011_001/description).
  NSIDC does not host OSI-SAF directly but documents/cites it
  ([NSIDC-0508](https://nsidc.org/data/nsidc-0508/versions/1)).
- **Wind/ocean-current reanalysis** (drift-model + routing inputs): ERA5 (wind) and
  CMEMS (ocean currents) — both used directly by IDRIFTNET and PolarRoute in the
  literature above, both real operational reanalysis products.
- **Iceberg tracks**: BYU/NIC consolidated Antarctic Iceberg Tracking Database, CSV,
  1978–Aug 2023, free download — real but sparse/large-berg-only as noted in §2.
- **Routing prior art**: PolarRoute is open source and directly reusable/inspectable.

No sub-problem requires fabricated placeholder data to get a real vertical slice
running; the honest gap is Antarctic-specific *pretrained* deep models (IceNet is
Arctic-only) and *dense* iceberg trajectory data (BYU/NIC is sparse) — both are reasons
to lean on physics-first baselines (short-lead DL trained directly on real OSI-SAF SIC;
Wagner drift model) rather than reasons to fabricate data.
