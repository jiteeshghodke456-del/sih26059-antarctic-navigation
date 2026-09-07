# Competitive Analysis — SIH26059 (Antarctic Sea-Ice / Iceberg Trajectory / Navigation Decision Support)

Status: initial research pass, 2026-08-31. Feeds architecture selection. Dense findings, not narrative — cite before you assume.

PS text (verbatim, all we were given): "Develop an AI/ML-enabled decision support platform capable of forecasting Antarctic sea-ice concentration, predicting iceberg trajectories, and identifying safe and fuel-efficient navigation routes for research vessels using satellite, oceanographic and meteorological datasets." — MoES / NCPOR, Software.

---

## 1. Prior SIH-style submissions in this domain

**No direct prior SIH submission found on sea-ice forecasting, iceberg tracking, or polar navigation** — searched GitHub, Devpost-style writeups, YouTube demo titles across SIH years. This is either a genuinely new PS for NCPOR or prior attempts weren't published publicly. Do not assume "everyone has done this before" — verify claim, treat as unconfirmed rather than assert non-existence definitively.

**Best available analog: sibling MoES problem statements from SIH 2025**, same ministry, same "real satellite/oceanographic dataset → AI decision layer" shape:

- **SIH25XXX "FloatChat" — AI-powered conversational interface for ARGO ocean data discovery/visualization.** At least 4 independently-built public implementations found: [ARPANPATRA111/Float-Chat](https://github.com/ARPANPATRA111/Float-Chat) (RAG + local LLM + PostGIS, NL→SQL), [Aryanthakur7/FloatChat-AI-Assistant](https://github.com/Aryanthakur7/FloatChat-AI-Assistant) (LangChain/Pandas), [AdithyaSM31/FloatChat-AI](https://github.com/AdithyaSM31/FloatChat-AI) (Llama 3.3 70B via Groq, 12-language dashboard), [uranium24/float-chat-app](https://github.com/uranium24/float-chat-app) (3D globe UI). All converge on the same pattern: chatbot/RAG wrapper over a real dataset (ARGO NetCDF), with the "AI" being retrieval + NL-to-SQL translation, not a trained predictive model.
- **SIH25039 "Integrated Platform for Crowdsourced Ocean Hazard Reporting and Social Media Analytics"** — also MoES/Disaster Management. Multiple teams ("Ocean Watch", "AquaSentra", team Snapby) built near-identical crowdsourcing + social-media-analytics dashboards.

**Finding, framed as inference not citation** (no direct judge quote was found anywhere in the search — the medium.com critique piece on SIH judging surfaced general complaints about judge domain-expertise gaps and opaque scoring, not a specific "just a dashboard" quote): the FloatChat/Ocean-Hazard convergence — 4+ teams independently building the same chatbot-over-real-data wrapper for one PS — is direct evidence of what "obvious architecture" convergence looks like for an MoES data-access PS. The predictable failure mode for SIH26059 is the same shape: teams pull CMEMS/NIC data, put a map + chat/dashboard UI on top, and call the retrieval layer "AI," without a trained forecasting or trajectory model underneath. **Decision: any UI/dashboard layer must sit on top of a genuinely trained/fitted model (forecasting, drift, or routing optimization) — never let the demo's most visible surface (chat, map, dashboard) be the only "AI" component.**

---

## 2. Real operational/research systems already solving pieces of this

### Sea-ice concentration forecasting

- **IceNet** (British Antarctic Survey + Alan Turing Institute). Ensemble of U-Nets, MIT-licensed, actively maintained (~1000+ commits): [github.com/icenet-ai/icenet](https://github.com/icenet-ai/icenet), project site [icenet.ai](https://icenet.ai/), original paper [Nature Communications 2021](https://www.nature.com/articles/s41467-021-25257-4). Outputs: daily sea-ice-concentration forecasts up to 2 weeks, monthly-mean forecasts up to 6 months, 25 km resolution. Outperforms ECMWF SEAS5 dynamical model on summer extremes.
  - **Verified: IceNet's published validation is Arctic.** The Nature Comms paper title is "Seasonal *Arctic* sea ice forecasting," and follow-on work (MT-IceNet) is also Arctic-only. No confirmed Antarctic/Southern-Hemisphere validation was found for IceNet itself.
  - **A distinct Antarctic-specific model exists: ANTSIC-UNet** — [The Cryosphere, 2025](https://tc.copernicus.org/articles/19/6381/2025/). U-Net trained on ERA5 + ORAS5 + NSIDC ice-concentration records (1979–2011), 14 atmospheric/oceanic input variables, 25 km grid, monthly forecasts to 6 months lead. Beats linear-trend/persistence/SEAS5 baselines on RMSE and integrated ice-edge error, and specifically demonstrates skill on 2017/2022/2023 extreme-minimum events (the exact anomalous post-2016 Antarctic sea-ice regime that makes this PS non-trivial). Inputs are all public (NSIDC/ERA5/ORAS5); the paper does not state whether the model code itself is released.
  - **Decision implication:** a team that just fine-tunes/reuses IceNet weights for Antarctica is extrapolating a model outside its validated domain — Antarctic sea ice is far more wind/ocean-driven and less predictable than Arctic (documented instability since 2016). Cite ANTSIC-UNet's architecture and inputs as the credible reference point for Antarctic-specific forecasting, not IceNet directly.

- **Copernicus Marine Service (CMEMS)** — the actual near-real-time backbone we'd fuse from. [SEAICE_GLO_SEAICE_L4_NRT_OBSERVATIONS_011_001](https://data.marine.copernicus.eu/product/SEAICE_GLO_SEAICE_L4_NRT_OBSERVATIONS_011_001/description): daily sea-ice concentration/edge/type/drift, both hemispheres, 10 km polar-stereographic, produced by the OSI-SAF Sea Ice TAC. CMEMS forecasts sea ice **10 days ahead** by feeding NRT observations into a model — this is the operational baseline any "novel forecasting" claim has to beat, and it's a hard bar since it's already assimilating live satellite data. [ANTARCTIC_OMI_SI_extent](https://data.marine.copernicus.eu/product/ANTARCTIC_OMI_SI_extent/description) gives reanalysis Antarctic extent back to 1993 (15% concentration threshold) — good for training/validation, not operational forecasting.

- **ESA CCI Sea Ice** — [climate.esa.int/en/projects/sea-ice](https://climate.esa.int/en/projects/sea-ice/), higher-res (near-90GHz AMSR-E/AMSR2) concentration CDR 2002–present, also redistributed via Copernicus Climate Data Store. Good long-baseline training data, not a forecast product.

- **NSIDC** — sea ice concentration CDR (SSM/I-derived), long historical record via ERDDAP/OPeNDAP, requires Earthdata login. Standard training-data source, used by ANTSIC-UNet above.

- **DTU Space** — could not verify a specific DTU Space Antarctic operational product in this search pass (mark unverified, don't assert). What is well-established in the literature is **CryoSat-2 sea-ice freeboard/thickness retrieval over Antarctica** ([The Cryosphere, 2020, ICESat-2+CryoSat-2 freeboard/snow-depth/thickness](https://tc.copernicus.org/articles/14/4453/2020/)) — and the literature is explicit that Antarctic freeboard retrieval is *harder and less mature* than Arctic because snow-depth-on-ice is poorly constrained and biases CryoSat-2 freeboard by multiple cm. **This is a genuine, citable reason ice-thickness (not just concentration) is a weak point across the whole field for Antarctica** — worth naming explicitly rather than pretending thickness data is solved.

### Iceberg tracking and trajectory prediction

- **US National Ice Center (USNIC)** — [usicecenter.gov/Products/AntarcIcebergs](https://usicecenter.gov/Products/AntarcIcebergs), the authoritative operational source. Names and tracks Antarctic icebergs ≥20 sqNM or ≥10 NM on longest axis, weekly updates, using SAR/visible/IR imagery, tracking since 1978. Consolidated with a BYU scatterometer-derived daily database — see [BYU/NIC database](https://www.scp.byu.edu/iceberg/database1_recent.html). This is real, positional, time-series iceberg-drift ground truth — the closest thing to a "labels" dataset for a trajectory model.
- **A six-year circum-Antarctic iceberg dataset (2018–2023)**, [ESSD 2026](https://essd.copernicus.org/articles/18/147/2026/), publicly downloadable at [doi.org/10.5281/zenodo.17165466](https://doi.org/10.5281/zenodo.17165466). Sentinel-1 SAR (40 m), whole Southern Ocean south of 55°S, icebergs >0.04 km² (first dataset to catch small ones), shapefiles + GEE code + processing scripts. **Caveat: this is one annual October snapshot per year, not a trajectory/time-series product** — useful for size/distribution census and validation, not directly for drift-model training without pairing it with the BYU/NIC positional series.
- **IDRIFTNET** — [arXiv 2507.00036](https://arxiv.org/abs/2507.00036), 2025, tested specifically on Antarctic icebergs A23a and B22a (the giant tabular bergs). Hybrid physics + ML: analytical drift-force equations (wind drag, current drag, Coriolis, pressure gradient) plus a residual/rotate-enhanced spectral neural network that learns the mismatch between the analytical solution and observed drift. Beats pure statistical/pure-physics baselines on displacement error. **No public code/data found.** This is the SOTA architectural pattern worth emulating for iceberg-trajectory modeling: physics gives the first-order motion, ML corrects the residual — not an opaque end-to-end black box, and not a naive physics-only model either.

### Ship routing under ice constraints

- All prior ice-routing literature (ant-colony 3D routing, great-ellipse waypoint GA/PSO optimization, POLARIS-risk-index frameworks) is **Arctic-focused**; nothing found specific to the Southern Ocean/Antarctic research-vessel context. This is itself a finding: routing-under-ice research assumes Arctic shipping-lane economics (Northern Sea Route, commercial transit), not the very different Antarctic case (single seasonal resupply run, no commercial traffic, no fixed lanes).
- **Very recent (Nov–Dec 2025) papers, genuinely current state of the art:**
  - [Integrating Regional Ice Charts and Copernicus Sea Ice Products for Navigation Risk in Alaskan Waters](https://arxiv.org/pdf/2512.11083) — fuses regional ice charts + CMEMS satellite data + AIS vessel tracks via the IACS POLARIS Risk Index Outcome framework. Key finding: **Copernicus systematically underestimates ice concentration vs. regional charts, especially nearshore/marginal ice zone**, and ~36% of AIS observations in ice-affected waters corresponded to negative (elevated-risk) POLARIS outcomes. Explicit conclusion: single-source ice data is not authoritative — multi-source fusion with disagreement quantified is necessary, not optional.
  - [Hybrid Quantum Annealing for Multi-Criteria Constrained Quadratic Optimization in Arctic Ship Routing](https://arxiv.org/pdf/2512.10544) — formulates routing as a Constrained Quadratic Model on real CMEMS environmental data, D-Wave hybrid solver vs. Gurobi/CPLEX, 10–100x faster convergence, smoother/shorter routes. Shows the field is already past naive greedy/A* routing toward proper multi-objective constrained optimization on real data.
  - [Trans-Arctic route feasibility on a pan-Arctic grid under bathymetric and sea-ice constraints](https://arxiv.org/pdf/2512.08434) and [SWR-Viz: AI-assisted visual analytics for ship weather routing](https://arxiv.org/pdf/2511.15182) — both confirm bathymetry + ice + weather multi-constraint routing and explainable/interactive visualization are treated as first-class requirements in current research, not afterthoughts.
- **Commercial**: **StormGeo** ([s-Routing / s-Planner](https://stormgeo.com/products/s-routing)) is the real incumbent — voyage optimization with "ice conditions" as an explicit input parameter, partnered with Bearing AI for vessel-performance modeling, 24/7 human route analysts as a fallback layer (notable: even the market leader keeps a human-in-the-loop fallback, not pure automation). **Sofar Ocean** — confirmed real and directly relevant: solar-powered **Spotter buoys deployed in the Southern Ocean since 2018** (Drake Passage crossing, MetOcean Solutions/DTA), and the **Brazilian Navy uses Sofar as its connected-sensor partner for Antarctic/South Atlantic operations** ([sofarocean.com/posts/how-spotter-buoys-support-the-brazilian-navys-antarctic-weather-mission](https://www.sofarocean.com/posts/how-spotter-buoys-support-the-brazilian-navys-antarctic-weather-mission)). This is a real in-situ wave/wind/SST sensor network physically in the operational region — a genuine ground-truth source distinct from satellite-only data, though we have not confirmed Indian/NCPOR access to this network's data.

### NCPOR's own infrastructure

- Public portals found: [data.ncpor.res.in](https://data.ncpor.res.in) (MET-Data), [npdc.ncpor.res.in](https://npdc.ncpor.res.in) (National Polar Data Centre), [las.ncaor.gov.in](http://las.ncaor.gov.in) (Live Access Server). Content/dataset catalogue of these portals **could not be confirmed** in this pass (pages didn't render enough detail via fetch) — needs manual browsing, not a fetch-tool limitation to paper over.
- NCPOR site references a "Research Vessel Movements" section — **existence of vessel tracking is confirmed, but whether it includes any route-planning, ice-avoidance, or forecasting capability (which would make part of this PS redundant) is NOT confirmed.** Do not assume NCPOR has nothing — verify directly (NCPOR portal manual check or a direct question to the ministry) before building as if this is greenfield.
- **The real vessel and route, confirmed via press releases**: India's Antarctic resupply uses the **chartered Russian diesel-electric vessel MV Vasiliy Golovnin** (FESCO), running **Cape Town → Bharati/Maitri stations**, roughly Dec–Feb (austral summer), one voyage per Indian Scientific Expedition to Antarctica (ISEA) — e.g. [43rd ISEA press release](https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=1993769). This is not a hypothetical "any vessel, anywhere" problem — it's a **known, narrow, single-corridor, single-season operational context** (South Atlantic/Indian Ocean sector of the Southern Ocean, roughly the Queen Maud Land approach). This materially changes scope: a system tuned to this corridor and season can be far higher-fidelity than a generic global Antarctic router.
- **Connectivity reality**: geostationary VSAT does not reliably cover south of ~70°S; polar-region maritime comms rely on **Iridium** (LEO constellation, genuinely global/polar coverage), with Iridium Certus topping out around 704 kbps and legacy/basic Iridium services provisioned for critical/small messages (sub-50KB), not bulk data. **A "decision support platform" that assumes a live API call to CMEMS/NIC from the vessel is assuming infrastructure the vessel likely doesn't reliably have.** This is a real, sourced constraint, not a generic "add offline mode" nicety.

---

## 3. What a strong competing team plausibly builds (the "obvious" architecture) — and where it's shallow

Given only the one-sentence PS, every competent team converges on roughly:

1. Pull CMEMS sea-ice concentration + NIC/BYU iceberg positions + ERA5/CMEMS ocean-current/wind data.
2. Fine-tune or reimplement a U-Net-style CNN for short-horizon ice-concentration forecasting (IceNet/ANTSIC-UNet-shaped, since these are the only public architectures to copy).
3. Do iceberg trajectory as either (a) pure physics drift model, or (b) an LSTM/GRU on historical BYU/NIC tracks — rarely both.
4. Do routing as A*/Dijkstra over a grid with ice-concentration as an edge-cost penalty — a static shortest-path, not a real multi-objective optimizer.
5. Wrap it all in a Leaflet/Mapbox dashboard with a chat/query layer on top (the FloatChat pattern), demo three cherry-picked scenarios.

**Where this is shallow, concretely:**
- **Single-source ice truth.** The Alaska ice-chart paper found real, systematic disagreement between Copernicus and regional/ground observations. A team using CMEMS alone and presenting its numbers as ground truth is building on an acknowledged-biased source without saying so.
- **Physics-free or ML-free trajectory modeling.** IDRIFTNET (2025 SOTA) is explicitly hybrid because pure statistical or pure physics both underperform. A team picking one is behind the literature by months, not years — genuinely beatable gap.
- **Routing as static shortest-path.** Current research (quantum-annealing CQM paper, trans-Arctic feasibility paper) treats routing as multi-objective constrained optimization (fuel, time, ice risk, bathymetry) with the constraint surface itself uncertain (ice forecast has its own error bars) — not a fixed-cost grid search.
- **No uncertainty propagation.** None of the "obvious" pieces above carry forecast uncertainty forward into the route decision. A 6-month-ahead ice concentration forecast has real, growing error; routing on the point forecast as if it were certain is a documented failure mode judges in ML-literate domains (MoES reviewers plausibly include NCPOR scientists) will catch immediately.
- **Assumes always-on connectivity.** The dashboard-and-chat pattern assumes a live backend. On the actual operational vessel (Iridium-class links), that assumption is simply wrong for the real deployment context — a strong differentiator if we get it right, a credibility problem for competitors if a judge who knows the vessel's comms asks about it.
- **No route corridor specificity.** Building for "Antarctica" in general when the real, sourced operational corridor is Cape Town–Bharati/Maitri in austral summer is over-scoping the problem in a way that dilutes fidelity everywhere instead of concentrating it where it matters.

---

## 4. Differentiation angles (grounded, not "better UI")

1. **Physics + ML residual for iceberg drift, not black-box or physics-only** — replicate the IDRIFTNET pattern (analytical wind/current/Coriolis drag equations + learned residual correction), validated against real BYU/NIC positional data for Southern Ocean bergs. This is a specific, citable, currently-unreplicated-in-public-code architecture — genuine technical differentiation, not hand-waving.
2. **Explicit multi-source ice-data fusion with disagreement surfaced, not hidden.** Fuse CMEMS (10km NRT) with NIC/regional-style products where available; when sources disagree (as the Alaska paper shows they systematically do), show that disagreement in the UI as a confidence band, not a single authoritative number. This is honest and directly grounded in a documented, real phenomenon — and it's the one thing every "obvious" competitor skips because it complicates the demo.
3. **Uncertainty-aware routing, not point-forecast routing.** Propagate the ice-forecast model's own error/confidence into the routing cost function (wider/costlier "possible ice" buffer as forecast lead time grows), and route optimization as genuine multi-objective (fuel vs. time vs. risk) rather than single-cost shortest path — matching where the Nov/Dec 2025 literature already is, not where 2023-era SIH-tier routing sits.
4. **Corridor-specific, season-aware scoping**: build and tune for the real, sourced Cape Town–Bharati/Maitri corridor during the austral-summer resupply window, rather than a generic "anywhere in Antarctica, any time" claim nobody can actually validate against real vessel data. Narrower, verifiable scope beats broader, unverifiable scope with an MoES/NCPOR audience who will recognize the real operational context.
5. **Bandwidth-honest design, grounded in Iridium reality**: design the on-vessel component to run on cached/pre-synced forecast tiles with explicit staleness indicators and degrade gracefully (last-known-good ice edge + confidence decay over time since last sync) rather than assuming a live connection — sourced directly from the Iridium Certus ~704kbps / sub-50KB-message reality of actual polar vessel comms, not a generic "PWA offline mode" checkbox.
6. **Honest fallback behavior**: when the model's own confidence is low (sparse recent satellite passes, conflicting sources, forecast horizon beyond validated skill — ANTSIC-UNet's own paper shows skill degrading with lead time), say so explicitly in the decision-support output rather than always emitting a confident-looking route. StormGeo, the actual commercial incumbent, keeps human route analysts in the loop 24/7 specifically because pure automation isn't trusted at the edge cases — our system should model that honesty rather than pretend full automation.

---

## Open items (deferred, not resolved here)

- Whether NCPOR's own NPDC/MET-Data/Live-Access-Server portals or "Research Vessel Movements" tooling already provide ice-forecast or route-planning capability that would overlap this PS — unconfirmed, needs manual portal review or a direct question to NCPOR. Logged in `docs/backlog.md`.
- Whether Sofar Ocean Southern Ocean buoy data (or equivalent in-situ wave/wind data) is actually accessible to us for this project — confirmed to exist in the operational region, access/licensing not checked.
- DTU Space's specific Antarctic product catalogue was not confirmed in this pass; only the broader CryoSat-2 Antarctic freeboard/thickness literature was verified.

---

# The operational incumbents, and why they were missing from this file

*Added 2026-09-07.* An audit found this document evaluated the **research**
rivals seriously — IceNet, ANTSIC-UNet, CMEMS, IDRIFTNET, USNIC/BYU — and left
out every **product** a domain judge would name first. IcySea, PolarView,
Polarstern MapViewer and the ECDIS vendors sat in `docs/ppt_source/market.md`,
a marketing draft, rather than here. That is the wrong place for them: a
competitor you only discuss in a pitch document is a competitor you have not
actually analysed.

## The products

| Product | What it does | Where it is better than us | What it leaves |
|---|---|---|---|
| **IcySea** (Drift+Noise, AWI spin-off, ~7 staff) | Near-real-time ice imagery and drift forecast to the bridge, Iridium-tested, delivery within ~1 h of satellite recording, offline browser cache, click-a-point-to-forecast-drift. Customers include **RV Polarstern and RSV Nuyina** | Everything about delivery. They have solved low-bandwidth polar distribution, which we have only designed. They are a real product on real ships; we are a prototype | It answers *"what does the ice look like"*. It does not answer *"can this named ship reach this named station on this date"* — which is the gap we occupy |
| **PolarView** (University of Bremen lineage) | AMSR2 sea-ice concentration, publicly served, the same product Laura Bassi's dashboard consumes | Free, established, trusted, and the source many operators already open first | A data service, not a decision-support tool. No vessel model, no route, no approval |
| **Polarstern MapViewer** (AWI) | Institutional multi-layer viewer aboard an icebreaker, backed by a documented data-logistics team with SLA-like onboarding (mission data <10 min, new permanent product ~4 weeks) | Layer breadth we cannot approach, because it rests on institutional data infrastructure and staff, not on UI | Internal to one operator's fleet. Not a product anyone else can adopt |
| **ECDIS vendors** (Furuno, Kongsberg, Wärtsilä/Transas, NAVTOR, ChartWorld) | Type-approved bridge systems meeting MSC.232(82), carriage-mandated under SOLAS V/19.2.10 | Type approval, which we will never have as a prototype, and the bridge itself — they own the screen | Ice-aware, vessel-specific, destination-reachability decision support is not what they sell. We are a layer that would have to live beside them, not replace them |
| **StormGeo** (~13,000 vessels) | Commercial voyage optimisation with 24/7 human route analysts | Mature, genuinely multi-objective at scale, commercially proven | A different market: global commercial shipping on subscription, no Antarctic resupply specialisation. Their human-in-the-loop fallback is evidence that full automation is not trusted at the edges — which is the posture we argue for too |

## The failure analysis this file did not have

The audit's sharpest finding was that **no competitor failure analysis existed
anywhere in the repository** — zero hits for "shut down", "discontinued",
"failed because", "lessons from". A competitive analysis with no failures in it
is a survivorship-biased list.

What can honestly be said, which is less than a full post-mortem:

- **ISRO's own SCATSAT-1 Antarctic sea-ice product stopped in May 2019 while
  the satellite kept operating until February 2021.** The product was
  discontinued nearly two years before the platform failed. And the VEDAS polar
  GeoServer, which served those daily Antarctic layers in EPSG:3031, carries
  **nothing after March 2021** — it was never continued onto EOS-06. This is the
  clearest documented case available to us of a capable polar data service
  lapsing, and the cause looks like continuity of funding and ownership rather
  than any technical failure. It is the failure mode most likely to kill *this*
  project too, and it argues for our reuse-first posture: PolarRoute, the CDR
  and the ATS register all outlive us.
- **IceNet's published validation is Arctic**, and its operational Antarctic
  support exists in source code rather than in a second peer-reviewed paper.
  That is a scope limitation rather than a failure, and it should be described
  as one.
- We have **never tested IcySea** and will not claim it is worse. Our claim is
  adjacent, not superior.

**Still open:** a genuine post-mortem of a discontinued polar navigation or ice
service — why it ended, who paid for it, what replaced it. Filed in
`docs/backlog.md`. Writing one would be worth more than another feature.

---

# The 12-question benchmark

Reinstated from the master prompt, where a `# COMPETITIVE / OPERATIONAL
BENCHMARK` section (line 5070) was **lost in compression** — only §30's weaker
bullet list survived (`docs/MASTER_AUDIT.md` §A.4). The lost version is
materially more rigorous, because it refuses the question "what software already
exists?" and replaces it with twelve questions about what that software actually
*does for a decision*.

> Do not merely ask "What software already exists?" Ask:
> what decision does it support · what data does it use · at what latency · what
> forecast horizon · what vessel assumptions · what risk methodology · what
> routing methodology · what uncertainty does it expose · what does the user
> actually see · what is genuinely better · what remains unsolved · what can this
> system demonstrate that they cannot.
>
> **Do not create a strawman competitor.**

Answers below are marked `UNVERIFIED` wherever they could not be confirmed from
public documentation. An unverified answer is not a weakness in the competitor.

## IcySea (Drift+Noise Polar Services)

| Question | Answer |
|---|---|
| Decision supported | "Where is the ice edge and what does the imagery show me right now" — situational awareness for the ice pilot |
| Data | Sentinel-1 SAR, AMSR2 passive microwave |
| Latency | Near-real-time on acquisition; hours (`UNVERIFIED` exact) |
| Forecast horizon | **None — it is observation, not forecast** |
| Vessel assumptions | None; vessel-agnostic viewer |
| Risk methodology | None published; interpretation is left to the mariner |
| Routing methodology | **None** — it does not route |
| Uncertainty exposed | Imagery quality is visible to the eye; no quantified uncertainty (`UNVERIFIED`) |
| User sees | High-resolution SAR imagery, bandwidth-adapted for shipboard links |
| Genuinely better than us | **SAR resolution.** Metres against our 25 km passive microwave. For close-quarters ice navigation this is a decisive advantage and we should not pretend otherwise. Also a real product with real customers — Polarstern and Nuyina both use it |
| Remains unsolved | Forecast, route, vessel-specific consequence, decision record |
| What we can show that they cannot | A route whose validity is tied to named evidence, and a refusal to certify what has not been observed |

## PolarView

| Question | Answer |
|---|---|
| Decision supported | Ice information distribution to polar operators |
| Data | Multi-mission SAR and passive microwave, ice charts |
| Latency | Product-dependent (`UNVERIFIED`) |
| Forecast horizon | Distributes forecasts produced elsewhere |
| Vessel assumptions | None |
| Risk methodology | None of its own |
| Routing methodology | None |
| Uncertainty exposed | Inherits whatever the source product carries |
| User sees | A portal of layers |
| Genuinely better | Breadth of sources and institutional continuity |
| Remains unsolved | Turning layers into a decision — the exact gap this project targets |
| What we can show | Fragmented layers reduced to one route-health state with its reasons |

## BAS PolarRoute / meshiphi

| Question | Answer |
|---|---|
| Decision supported | Optimal path under ice and vessel-performance constraints |
| Data | Whatever mesh you supply — SIC, thickness, currents, bathymetry |
| Latency | Offline; a corridor solve takes ~9 s (**Measured**, this repo) |
| Forecast horizon | Inherits the input mesh's |
| Vessel assumptions | **Explicit and well modelled** — speed/ice-resistance curves, fuel |
| Risk methodology | Constraint-based; not a published risk index |
| Routing methodology | Dijkstra / A* over a non-uniform mesh, with smoothing |
| Uncertainty exposed | None natively |
| User sees | A Python API and JSON — **no operational interface** |
| Genuinely better | The routing itself. It is the state of the art and **we reuse it rather than compete with it** |
| Remains unsolved | Provenance, freshness, human approval, monitoring, the bridge |
| What we can show | The workflow around the solver: mission definition, gates, approval, versioning, divergence detection |

## National ice services (AARI, AWI, NIC/USNIC)

| Question | Answer |
|---|---|
| Decision supported | Authoritative ice charting and iceberg cataloguing |
| Data | Multi-sensor, analyst-interpreted |
| Latency | Daily to weekly depending on product |
| Forecast horizon | Some short-range; principally analysis |
| Vessel assumptions | None |
| Risk methodology | Ice charts feed POLARIS externally; the chart itself is not a risk index |
| Routing methodology | None |
| Uncertainty exposed | Egg-code conventions carry stage and concentration, not error bars |
| User sees | Charts, and for USNIC a public iceberg catalogue we consume |
| Genuinely better | **Authority and human analyst judgement.** An automated product does not replace a national ice service and should not claim to |
| Remains unsolved | Ship-specific consequence; anything at decision time on the bridge |
| What we can show | The catalogue joined to a specific hull, a specific track, and a specific date |

## Commercial ECDIS + ice overlay (Kongsberg, Furuno, Wärtsilä)

| Question | Answer |
|---|---|
| Decision supported | Certified navigation and passage planning |
| Data | ENC + overlays |
| Latency | Chart update cycle; overlay-dependent |
| Forecast horizon | Overlay-dependent |
| Vessel assumptions | Draft, safety contour, manoeuvring data |
| Risk methodology | Depth/UKC alarms, not ice risk |
| Routing methodology | Manual waypoint planning with route check |
| Uncertainty exposed | CATZOC on the chart — genuinely good practice we borrow |
| User sees | The certified bridge display the crew already trusts |
| Genuinely better | **It is type-approved and legally sufficient. We are not, and must not imply otherwise.** It is also already installed, already trained on, and already in the workflow |
| Remains unsolved | Antarctic ice forecasting, iceberg trajectory, ice-constrained optimisation |
| What we can show | A decision layer that sits *beside* ECDIS, in ECDIS's own planning/monitoring idiom, without pretending to replace it |

## What this table changes

Two honest conclusions fall out of asking the twelve questions rather than
listing products:

1. **No competitor is weak.** Each is strong at the thing it was built for; the
   gap is that none of them closes the loop from observation to a versioned,
   approved, monitored route decision for a *named vessel on a named day*.
2. **The two we should be most careful about are IcySea and ECDIS** — IcySea
   because its data is genuinely better than ours, and ECDIS because it is
   certified and we are not. Any claim that steps on either is a claim a judge
   can dismantle.
