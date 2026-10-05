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
bullet list survived (`audit/MASTER_AUDIT.md` §A.4). The lost version is
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

---

# Pass 2 — IcySea audit, the Indian precedent, and the wider landscape

Status: second research pass, 2026-09-02. Appended, not overwriting. Sections 1–4 above stand unchanged; where this pass touches ground already covered there (IceNet/ANTSIC-UNet/CMEMS error budgets, PolarRoute, StormGeo, USNIC/BYU), it cross-references rather than re-derives. Every non-trivial claim below is tagged **VERIFIED** (with source), **INFERRED**, or **UNVERIFIED**.

*Merged into main on 2026-10-05.* This pass was written in a parallel session on 2 Sep and stayed on an unpushed branch until then. The two parts above, added on 7 Sep, were written without it, so both cover IcySea, PolarView, AARI and Wärtsilä. They have not been reconciled yet, so check both before quoting either on those products.

---

## 5. IcySea — feature-by-feature audit

### 5.1 What it is, and who builds it

**VERIFIED** ([driftnoise.com/icysea.html](https://driftnoise.com/icysea.html), [unoceanprediction.org/en/halls/driftnoise](https://www.unoceanprediction.org/en/halls/driftnoise)): IcySea is built by **Drift+Noise Polar Services GmbH** (Bremen, Germany), a spin-off of the Alfred Wegener Institute, co-developed with the **Norwegian Meteorological Institute (MET Norway)**. Self-described as "an ice information app for navigation in polar regions… near real time sea ice information for activities in the polar regions, reducing cost and risk, **in a Polar Code compliant way**."

**VERIFIED** (Drift+Noise project list, [driftnoise.com](https://driftnoise.com/)): funded/developed through a chain of ESA and EU projects — ESA InCubed (IcySea), FAST-CAST / FastCast2, EisKlass2, MARSAT, PRIIMA, MAP-BORealis, and current CROSCIM / HIRLOMAP. It is also listed as one of the platforms in the **Polar View** portfolio ([polarview.org/sample-data](https://polarview.org/sample-data/)) — i.e. IcySea and PolarView are not independent competitors; IcySea sits inside the Polar View ecosystem.

**VERIFIED** (customer references and testimonials on driftnoise.com; expedition pages): real operational users include PONANT's PC2 icebreaker *Le Commandant Charcot*, HANSEATIC spirit, the *Polarstern* PS137 expedition, and the **Endurance22** expedition (Weddell Sea, Antarctic). Drift+Noise also lists *Aurora Australis* among icebreaker users.

### 5.2 Data layers and satellite sources

| Layer | Source | Evidence |
|---|---|---|
| High-resolution SAR imagery | **Sentinel-1** | VERIFIED — [unoceanprediction.org](https://www.unoceanprediction.org/en/halls/driftnoise), driftnoise.com |
| High-resolution SAR imagery | **RADARSAT Constellation Mission (RCM)** | VERIFIED — [arcticfocus.org interview](https://www.arcticfocus.org/stories/navigating-frozen-frontier-how-icysea-revolutionizes-polar-ice-navigation/) ("high-resolution radar images until the North Pole") |
| Sea-ice concentration | **CMEMS `SEAICE_GLO_SEAICE_L4_NRT_OBSERVATIONS_011_001`** (OSI-SAF; the same product logged in §2 above) — "updated 8 times a day", "near-real time delivery, up to 1 hour after satellite recording" | VERIFIED — [CMEMS use case page](https://marine.copernicus.eu/services/use-cases/icysea-new-ice-information-app-navigation-polar-regions) |
| Ocean/ice model fields | **CMEMS Arctic Ocean Physics Analysis and Forecast** | VERIFIED — same CMEMS page |
| Ice drift (modelled, bias-corrected) | Drift+Noise in-house merge: "optimized **bias corrected** ice drift modeled data" merged with SAR "in an automated fashion" | VERIFIED — [unoceanprediction.org](https://www.unoceanprediction.org/en/halls/driftnoise) |
| Optical imagery | "optical and radar satellite imagery" | VERIFIED — [Eurisy case study](https://www.eurisy.eu/stories/icysea-real-time-ice-navigation-support-for-polar-waters/) |
| Icebergs | **not documented anywhere** | see §5.7 |

**Note for our own architecture:** the CMEMS SIC product IcySea consumes is *the same one* §2 above identifies as our NRT backbone — and the same one the Alaska ice-chart paper (§2) shows systematically **underestimates** concentration nearshore/in the MIZ. IcySea inherits that bias and does not, as far as any public documentation shows, correct or flag it. **INFERRED** (no public statement either way).

### 5.3 Forecast horizon

**UNVERIFIED — Drift+Noise does not publish a forecast horizon for IcySea anywhere I could reach.** What is documented:
- **VERIFIED** ([Eurisy](https://www.eurisy.eu/stories/icysea-real-time-ice-navigation-support-for-polar-waters/)): the user "can select a point of ice on an image to forecast its drift" — i.e. a Lagrangian point-drift forecast seeded from a SAR feature, driven by the merged bias-corrected drift model. This is a *trajectory* forecast of a chosen ice feature, not a gridded ice-concentration forecast.
- **VERIFIED** ([CMEMS use case](https://marine.copernicus.eu/services/use-cases/icysea-new-ice-information-app-navigation-polar-regions)): "improved and intuitively displayed sea-ice drift forecast **in the Svalbard region**" — the drift-forecast improvement is regionally scoped to Svalbard, i.e. Arctic. No equivalent Antarctic drift-forecast claim was found.
- **INFERRED:** IcySea's forecasting is short-range ice *drift/advection*, not multi-day/seasonal ice-*concentration* prediction. There is no evidence of an ML forecast model, an ensemble, or a lead-time-dependent skill statement.

This matters: **the entire IceNet/ANTSIC-UNet class of capability (§2) is absent from IcySea.** IcySea's forecast surface is a drift extrapolation, not a learned seasonal/sub-seasonal predictor.

### 5.4 The "ship risk assessment tool" — what it actually computes

The single most-cited feature, and the one with the thinnest public methodology.

- **VERIFIED** ([Eurisy](https://www.eurisy.eu/stories/icysea-real-time-ice-navigation-support-for-polar-waters/)): "a ship risk assessment tool, which **evaluates the navigability of ice-covered areas depending on the vessel type entered in the system**."
- **VERIFIED** ([Polar View data platforms page](https://polarview.org/sample-data/)): the Polar View portfolio (which includes IcySea) lists **"IMO Polar Code POLARIS data"** among its data layers.
- **VERIFIED** ([driftnoise.com/icysea.html](https://driftnoise.com/icysea.html)): the marketing framing is explicitly "in a Polar Code compliant way".
- **INFERRED, not verified:** the tool is a **POLARIS Risk Index Outcome (RIO)** implementation — user enters a Polar Class, the tool multiplies the per-ice-type Risk Index Values by the ice-type concentration fractions in each cell and colours the map by RIO (normal / elevated / not-recommended). The three bullets above make this the overwhelmingly likely design, and it matches how the field does it (the IACS POLARIS/RIO framework is the same one used by the Alaskan-waters paper in §2, [arXiv 2512.11083](https://arxiv.org/pdf/2512.11083)). **But Drift+Noise publishes no methodology document, no equations, no validation, and no peer-reviewed paper describing it that I could reach.** Do NOT state in the deck that IcySea "uses POLARIS" as a fact — state that it does vessel-class navigability assessment and that the method is undocumented.
- **VERIFIED by absence:** no public source states the risk tool ingests forecast ice, ice *thickness*, or any uncertainty. It is **INFERRED** to be a per-cell, present-tense, deterministic index over the observed ice field — a *colouring of the map*, not a cost surface fed to an optimiser.

### 5.5 Bandwidth, offline behaviour, and platform

- **VERIFIED** (raw HTML of [icysea.app](https://icysea.app/), fetched 2026-09-02): "It looks like IcySea is being started for the first time. In that case **all application data will be downloaded into the browser's cache**… This makes it possible to use IcySea even if you have a low bandwidth internet connection **or even no network connection**."
- **VERIFIED** (fetched [icysea.app/manifest.json](https://icysea.app/manifest.json)): IcySea is a **Progressive Web App** — `"display":"standalone"`, `"scope":"/"`, full installable icon set 36→512 px, `theme_color #1D809F`. Platform answer: **browser-based PWA, installable on desktop and mobile, no native app store build.** Unknown-route probing confirmed the app is a single-page shell (`/docs`, `/faq` all return the same shell), so the documentation is behind the token wall.
- **VERIFIED** ([unoceanprediction.org](https://www.unoceanprediction.org/en/halls/driftnoise)): transmission "optimized for low bandwidth" and **Iridium-tested** — the same Iridium constraint §2 above establishes for the Indian Antarctic vessel. This is important: *IcySea has already solved the bandwidth problem we identified as a differentiator in §4.5.* Our bandwidth story is not novel against IcySea; only what we send over that pipe can be.
- **VERIFIED** ([arcticfocus.org](https://www.arcticfocus.org/stories/navigating-frozen-frontier-how-icysea-revolutionizes-polar-ice-navigation/)): the mechanism is user-selected AOI tiling — imagery processed "into kilobyte or megabyte size so that you can still get the data you want for the specific area you are in, but you don't have to download all the data." A customer testimonial confirms the commercial framing: "Each vessel may take the amount of information it needs and not overpay for unnecessary information."
- **VERIFIED** ([Eurisy](https://www.eurisy.eu/stories/icysea-real-time-ice-navigation-support-for-polar-waters/)): mentions PDF-optimised download and access via "a phone-sized GPS plug" for positioning. **Not independently confirmed elsewhere** — treat the GPS-dongle detail as single-sourced.

### 5.6 Pricing model

- **VERIFIED** ([icysea.app](https://icysea.app/), [driftnoise.com/icysea.html](https://driftnoise.com/icysea.html)): **14-day free trial**, no obligation; registration with name/email/organisation/vessel; **access-token gated**; after trial, "Access to new data after the initial trial period requires an IcySea subscription"; enterprise route is "IcySea contract partner"; quotes via sales@driftnoise.com.
- **VERIFIED by absence: there is no published price list, no tier table, no per-seat or per-vessel figure anywhere public.** Anyone quoting an IcySea price in a deck is fabricating it.
- **INFERRED** from the testimonial about "not overpay for unnecessary information": pricing is likely metered on data volume / AOI, not flat per-seat. Do not assert.

### 5.7 The two decisive answers

**Does IcySea do ROUTING (path optimisation)? — NO.**
- **VERIFIED** ([arcticfocus.org interview with Drift+Noise](https://www.arcticfocus.org/stories/navigating-frozen-frontier-how-icysea-revolutionizes-polar-ice-navigation/)): "automatic route suggestions for ships through the ice based on ship and ice characteristics" is listed as **"an idea in development"** — i.e. explicitly not shipped.
- Every self-description is situational-awareness language: "display near-real time ice relevant information", "strategic planning, risk assessment and monitoring, operational and navigational support and decision-making", "map-based application".
- **Watch the trap:** the PONANT testimonial on driftnoise.com reads "Thanks to your outstanding app, **we performed** an efficient ice routeing to the pole." That is a *human navigator* routing with the app as an information display. It is not the app computing a route. If a judge quotes that line at us, this is the answer.
- **Consequence:** the routing half of SIH26059 is genuinely open ground against the strongest commercial polar-ice app in the world. That is a defensible, verifiable claim.

**Does IcySea handle ICEBERGS? — No documented capability.**
- **VERIFIED by absence** across driftnoise.com, icysea.app, the CMEMS use case, the Eurisy case study, the UN OceanPrediction profile, and the Arctic Focus interview: **the word "iceberg" appears in none of them.** Every data layer named is sea ice (concentration, type, drift) or raw SAR.
- Notably, its sibling platform **PolarView.AQ *does* list Antarctic iceberg tracking** (§9.1) — so within the same consortium, icebergs live in a different product. **INFERRED:** IcySea is a sea-ice product; iceberg detection/tracking is not in it.
- Caveat, stated honestly: high-resolution Sentinel-1/RCM imagery *displays* large bergs to a human eye. "No iceberg product" ≠ "bergs invisible". The claim to make is that IcySea has **no iceberg detection, no iceberg catalogue, and no iceberg drift forecast** — not that you cannot see a berg on its SAR.

**Arctic, Antarctic, or both? — Both, but asymmetrically.**
- **VERIFIED** ([icysea.app](https://icysea.app/)): "Covering both the Arctic and Antarctic". Confirmed operationally in the Antarctic by Endurance22 (Weddell Sea) and *Aurora Australis*.
- **VERIFIED** ([CMEMS use case](https://marine.copernicus.eu/services/use-cases/icysea-new-ice-information-app-navigation-polar-regions)): the CMEMS-funded development work is Arctic-centric — Arctic Ocean Physics Analysis and Forecast, "improved… drift forecast in the **Svalbard** region", customer sectors framed around Svalbard.
- **INFERRED:** Antarctic coverage is real but is the base observational layers (SAR + global OSI-SAF SIC), while the *model-derived and forecast* value-add has been developed and validated in the Arctic. Same structural asymmetry as IceNet (§2). Do not overstate — the honest form is "IcySea covers Antarctica; its forecast development work is documented in the Arctic."

### 5.8 What I could not verify about IcySea

Stated explicitly rather than papered over:
- The in-app layer catalogue. The app is token-gated; `/docs` and `/faq` return the SPA shell, and the pre-auth JS bundle (145 KB, fetched and grepped) contains no layer, forecast, iceberg, or POLARIS strings. **The only layer list available is what the marketing and partner pages disclose.**
- The risk tool's actual formula, thresholds, and whether it is POLARIS/RIO.
- Any forecast horizon in hours or days.
- Any accuracy, skill, or validation number. Drift+Noise publishes none.
- Any price.
- `https://www.drift-noise.com/icysea/` (hyphenated domain) — **proxy refused the connection**; the live site is the unhyphenated `driftnoise.com`.

---

## 6. The direct Indian precedent — Mishra et al. 2021, Bharati ↔ Maitri

The closest thing to a direct competitor for SIH26059, and previously unresearched in this repo.

**Citation (VERIFIED):** Mishra, P., Alok, S., Rajak, D.R., Beg, J.M., Bahuguna, I.M., Talati, I. (2021). *Investigating optimum ship route in the Antarctic in presence of sea ice and wind resistances – A case study between Bharati and Maitri.* **Polar Science 30, 100696.** [doi:10.1016/j.polar.2021.100696](https://doi.org/10.1016/j.polar.2021.100696). Affiliations: Space Applications Centre (ISRO), Ahmedabad + Pandit Deendayal Energy University. 19 citations as of this pass ([OpenAlex](https://api.openalex.org/works/doi:10.1016/j.polar.2021.100696)).

**Full-text access — stated honestly.** OpenAlex reports `oa_status: bronze` with the free PDF at ScienceDirect. **I could not obtain it.** ScienceDirect returns HTTP 403 to both WebFetch and direct curl (Cloudflare challenge shell, `<title>ScienceDirect</title>`); ResearchGate returns 403; the NIPR institutional-repository record ([nipr.repo.nii.ac.jp/records/16868](https://nipr.repo.nii.ac.jp/records/16868)) is **metadata-only — its `files` array is empty**. So the characterisation below is built from (a) the publisher abstract via the Semantic Scholar and OpenAlex APIs, and (b) — more valuable — **an independent peer-reviewed systematic review that tabulated this paper as one of its 32 studies** (§8). Grid resolution, the exact resistance equations, and the quantitative validation numbers remain **UNVERIFIED**. Someone with institutional access should pull the PDF before the deck is finalised; logged in `docs/backlog.md`.

### 6.1 What it actually does

**VERIFIED (abstract, via [OpenAlex](https://api.openalex.org/works/doi:10.1016/j.polar.2021.100696) / [Semantic Scholar](https://api.semanticscholar.org/graph/v1/paper/DOI:10.1016/j.polar.2021.100696)):**
> "This paper presents a technique of ship route optimization in the Antarctic sea ice regions using **Dijkstra's algorithm**… The study region is divided into **grids that result into unique nodes**, which are studied for sea ice parameters and wind velocity. **Resistances caused due to ice and wind** are considered to calculate expected **ship velocity** between nodes. The calculated ship velocities are then used to estimate **durations** to cover distances from a node to all the neighbouring nodes… forms a mathematical route from source to destination through various nodes **with time as weight**, that is then optimized through Dijkstra's algorithm… Results were **validated against the actual 33rd Indian Scientific Expedition to Antarctica voyage**."

**VERIFIED, independently, from Tran, Browne et al. (2023) — the Cold Regions systematic review, which tabulates Mishra et al. (2021) explicitly:**

| Review question | Tabulated answer for Mishra et al. (2021) | Where |
|---|---|---|
| Optimisation objective | **Voyage time only** — single objective. Not fuel, not distance, not multi-objective. | Table 2; review §4.1 |
| Ship performance model | **Riska (1997)** semi-empirical ice-resistance method | Table 3 |
| Ice data source | **NSIDC** | Table 6 |
| Optimisation method | **Graph-based (Dijkstra)** | Table 5 |
| Dynamic/time-varying ice? | **NO** — one of the 28 of 32 studies that hold ice fixed | **Table 7** |
| Route validated? | **YES** — one of only 6 of 32; validated against **historical AIS** for a comparable voyage | **Table 8**; review §4.7 |

### 6.2 The honest read

- **Confirmed: no machine learning.** Nothing in the abstract, and nothing in the review's tabulation (which classifies ML/data-driven methods separately — genetic algorithms, LASSO regression, etc. — and does not put Mishra there), indicates any learned component. **VERIFIED to the extent the review's taxonomy allows; INFERRED as an absolute.**
- **Confirmed: no forecasting.** The review places it in the "ice environment does not change" bucket. It routes over a **static, single-date observed ice field** — no ice forecast at all, let alone an ML one.
- **Confirmed: no uncertainty.** Not in the uncertainty-aware set (which contains only Schütz 2014 and, adjacently, Choi et al. 2015 — see §8).
- **Confirmed: no icebergs.** Resistance model is sea ice + wind. Icebergs are absent from the abstract and from the review's constraint taxonomy for this paper.
- **Its genuine strength, which we must respect:** it is **one of only six ice-routing studies in the entire reviewed literature that validated against real voyage data**, and it did so on *our exact corridor* with *our exact expedition programme* (33rd ISEA). Validation is the field's weakest link and this paper is above the field's median on it. Attacking it as "just Dijkstra" while shipping something we never validate would be a losing exchange in front of an MoES panel.
- **Scope nuance worth getting right:** Bharati (Larsemann Hills, Prydz Bay, ~69°S 76°E) ↔ Maitri (Schirmacher Oasis, Queen Maud Land, ~70°S 11°E) is the **inter-station coastal leg along East Antarctica** — a different problem from the Cape Town→station approach leg identified in §2. A complete Indian system needs both; this paper covers only the first. **INFERRED from station geography; VERIFIED that the paper's case study is Bharati↔Maitri.**

---

## 7. Indian in-house operational tooling — new findings beyond §2

These are new; they do not duplicate the "NCPOR's own infrastructure" bullets in §2.

**7.1 SAC/ISRO + MoES already ran an operational Sea Ice Advisory for an actual ISEA voyage.** **VERIFIED:** Joshi, P., Srigyan, M., Oza, S.R., Ray, Y., Beg, J. (2022). *Bringing SAR capability to a safer ice navigation during Indian Antarctic Expedition in near real-time mode.* **Polar Science**, [doi:10.1016/j.polar.2022.100900](https://doi.org/10.1016/j.polar.2022.100900). Affiliations (via [OpenAlex](https://api.openalex.org/works/doi:10.1016/j.polar.2022.100900)): **Indian Space Research Organisation ×3, Ministry of Earth Sciences ×2**. Full abstract retrieved from the NIPR repository API ([record 16984](https://nipr.repo.nii.ac.jp/records/16984)):
> "…providing sea ice advisory during the **40th Indian Scientific Expedition to Antarctica (ISEA)**… The radar can distinguish between more navigable thinner/weaker sea ice and the hazardous, much thicker sea ice **along with icebergs**… we have standardized the procedure to find the **penetrable passage within the sea ice packs**… for intensity images of **Interferometric Wide (IW) and Extra Wide (EW)** mode… use of **ERA5 reanalysis** for better interpretation of SAR data due to the presence of the **blizzard footprint** in the acquired image… a significantly improved **near real-time Sea Ice Advisory (SIA) surrounding two Indian Antarctic Research Stations** was produced and utilised to support safer navigation during the 40th ISEA voyage."

**This is the most important single finding of this pass for scoping.** Implications:
- The problem statement is **not greenfield**. India already has an operational, expedition-deployed Antarctic sea-ice advisory built on Sentinel-1. A team that presents "we will give NCPOR ice information from SAR" is offering them something they have had since at least the 40th ISEA.
- **It is manual/semi-automated expert SAR interpretation, not an algorithm.** "We have standardized the procedure" is a human-in-the-loop image-interpretation protocol. There is no forecast, no optimiser, no learned model. **VERIFIED from the abstract's own language.**
- **It does mention icebergs** — as objects a trained interpreter distinguishes in SAR backscatter, not as a tracked catalogue with drift prediction.
- **The `ERA5 → blizzard footprint` detail is a real operational failure mode we should handle:** wind events contaminate SAR backscatter and make ice-type classification unreliable. Any automated SAR-based classifier we build inherits this problem and must either flag or correct for it. **VERIFIED as a stated problem by the operators themselves.**

**7.2 The lineage goes back further.** **VERIFIED** (OpenAlex/Semantic Scholar author record for D. Ram Rajak): Rajak, D.R., Singh, R.K.K., Maheshwari, M., Jayaprasad, P., Oza, S.R., Beg, J., Sharma, R. — *Sea Ice Advisory using Earth Observation Data for Ship Routing during Antarctic Expedition* (2015, [doi:10.13140/rg.2.1.5073.8725](https://doi.org/10.13140/rg.2.1.5073.8725) — a ResearchGate-minted DOI, so likely a conference/technical paper rather than a journal article; **full text not retrieved, UNVERIFIED content**). Same SAC/ISRO group that later authored the 2021 Bharati–Maitri routing paper. **INFERRED:** SAC/ISRO has a continuous ~decade-long Antarctic ship-routing programme. Treat SAC/ISRO as a domain incumbent whose work will be known to MoES judges, not as absent.

---

## 8. Does any published ice-routing study propagate forecast uncertainty into the route? — the white-space check

§4.3 above claims uncertainty-aware routing as our differentiator, on this project's own reasoning. This section tests that claim against an external, citable, peer-reviewed systematic review. **The claim survives, but it needs to be stated more precisely than "nobody does this."**

**The source (VERIFIED, full text obtained):** Tran, T.T., Browne, T., et al. (2023). *Pathfinding and optimization for vessels in ice: A literature review.* **Cold Regions Science and Technology 211, 103876.** [doi:10.1016/j.coldregions.2023.103876](https://doi.org/10.1016/j.coldregions.2023.103876). Full text read via the open NRC Canada copy ([nrc-publications.canada.ca](https://nrc-publications.canada.ca/eng/view/ft/?id=b323558e-366a-4933-aa60-1570ac4237b2)); **32 articles**, sourced from Scopus, ScienceDirect, and Web of Science, seven research questions.

### 8.1 What the review found — verbatim

On static vs. dynamic ice (review §4.6, and its Table 7):
> "**Almost all of the research literature assumes that the ice estimation for a specific day is unchanged.** A few others incorporate sea ice dynamics in their pathfinding and optimization, including May et al. (2020), Schütz (2014), Voitkunskaia et al. (2019), and Zvyagina and Zvyagin (2022)."

**Table 7 — "Is the ice environment changing or not?": Yes = 4. No = 28.**

On uncertainty specifically (review §4.6):
> "**Schütz (2014) used a scenario tree to evaluate uncertainty in ice prediction. The author showed the effect of uncertainty on route planning decision-making.** The work used the non-anticipativity principle, which means the decision is valid at a time, and it does not consider future events."

And in the introduction, on constraints:
> "Depending on the sophistication of the routing models, these solutions consider more constraints, such as the operational regulations to ensure safety in ice (e.g. Browne et al., 2022; Lee et al., 2021) and **the uncertainty of the models (e.g. Choi et al., 2015)**."

The conclusion (review §6), verbatim:
> "The temporal changes in the environment and route validation are important, but just a few studies considered them… **The suggested directions for subsequent research are to implement more operational constraints and to treat the ice navigating problem under uncertainties.**"

And from §5, Future research suggestions:
> "…there are many machine learning approaches to pathfinding problems, such as reinforcement learning. This method helps solve the route planning when the environment is not deterministic, such as **the increasing uncertainties associated with visibility at night, and differences between actual ice conditions and the conditions reported in ice charts**."

### 8.2 The honest verdict on our §4.3 claim

**The white space is real, and now externally citable — but it is not empty.**

- **CORRECT and now VERIFIED:** the field overwhelmingly routes over a frozen, deterministic ice field. **28 of 32 (87.5%)** published ice-routing studies hold ice constant. A peer-reviewed systematic review names "treat the ice navigating problem under uncertainties" as *the* forward direction, in its concluding sentence. This is exactly the claim §4.3 makes, and it is no longer just our assertion.
- **CORRECTION we must make:** it is **not true that nobody has done it.** Two prior studies must be acknowledged or we will be caught:
  - **Schütz (2014)** — stochastic dynamic programming with a **scenario tree over ice prediction uncertainty**, explicitly measuring the effect of uncertainty on the route decision. This is genuinely uncertainty-propagating routing, twelve years old.
  - **Choi, M., Chung, H., Yamaguchi, H., Nagakawa, K. (2015).** *Arctic Sea route path planning based on **an uncertain ice prediction model**.* Cold Reg. Sci. Technol. 109, 61–69. Uses the Ice–Princeton Ocean Model (Ice-POM) forecast, genetic-algorithm-adjacent path planning, distance+time objectives.
  - **Both are Arctic. Both predate the ML sea-ice-forecasting era entirely** (IceNet is 2021). Neither uses a learned forecast, and therefore neither has a *model-derived* uncertainty to propagate — Schütz's scenarios are hand-constructed, Choi's uncertainty comes from a dynamical model.
- **Therefore the precise, defensible form of our claim is:** *no published ice-routing study propagates the uncertainty of a **machine-learned** sea-ice forecast into the route cost, and none of the four studies that handle time-varying ice, nor either of the two that handle uncertainty, is Antarctic.* Every one of the 32 that touches the Southern Ocean — i.e. Mishra et al. 2021 — is in the static, deterministic, single-objective bucket.
- **Secondary finding, equally useful:** **Table 8 — route validated? Yes = 6, No = 26.** And within those six, "**Only Jeong et al. (2018) conducted a real voyage for validation**" — with results showing "the mismatching between estimated speed and actual speed varied from **0 to 50%**." That 0–50% speed error on a real ice voyage is the field's honest state of the art on ship-performance-in-ice prediction, and it is a number worth having when someone asks how accurate our ETAs are.
- **Third finding:** the review flags AIS-based validation's own trap — "when comparing against AIS data, an assumption is that the navigators on that ship perform perfectly… If the optimized route is different from the AIS data, the pathfinding performance is considered to be poor. However, **it could be that the AIS data reflect a non-optimal route.**" This applies directly to Mishra et al. 2021's validation *and* to ours. Anticipate it.

---

## 9. The wider landscape — other operational systems

### 9.1 Polar View / PolarView.AQ — the sharpest comparison after IcySea

**VERIFIED** ([polarview.org](https://polarview.org/), [polarview.org/sample-data](https://polarview.org/sample-data/), [polarview.aq](https://www.polarview.aq/)): Polar View is a consortium platform provider; its portfolio includes **Polar TEP** (Thematic Exploitation Platform), **PolarView.AQ**, the **Ice Logistics Portal** (central ice-chart repository for the International Ice Charting Working Group), **IcySea**, and **Cerulean**.

**PolarView.AQ — this is the one that matters.** **VERIFIED** from [polarview.aq](https://www.polarview.aq/):
- **Operated by the British Antarctic Survey** (NERC).
- Purpose: "Delivers **sea ice and iceberg information to ships** in polar oceans."
- Layers: Sentinel-1 **SAR imagery**; **AMSR2 sea-ice concentration**; **national ice charts from USNIC and MET Norway**; **iceberg tracking — Antarctic only**.
- **Explicit "low bandwidth mode"** alongside a high-bandwidth mode, with the preference stored in a cookie.
- **Free web access**, Arctic and Antarctic regional viewers.
- **No routing.** Framed as "Operational Sea Ice Information" and monitoring. **VERIFIED by absence of any routing language.**
- **Forecast horizon: none published** — it is an observation/chart delivery service. **UNVERIFIED whether any forecast layer exists.**

**This is the most uncomfortable finding of the pass and must not be buried.** PolarView.AQ already combines *Antarctic sea ice + Antarctic icebergs + low-bandwidth ship delivery + free access*, operated by BAS — the same organisation behind both IceNet (§2) and PolarRoute (§2). Three of the five "differentiators" in §4 (multi-source ice, bandwidth honesty, Antarctic scope) are individually already shipped by a free BAS product. **What PolarView.AQ does not do: forecast anything, quantify anything, or route anything.** That is where our claim has to live.

### 9.2 Baltic ice services — BALTICE / IBNet and IBPlott

- **BALTICE ([baltice.org](https://baltice.org/))** — **VERIFIED** from the live site: operated for Baltic Icebreaking Management; contact `winternavigation@ftia.fi` (**Finnish Transport Infrastructure Agency**). Provides: **Assistance Restrictions** by port/region (FINSWE and Other), a **Traffic & Ice Situation Map**, downloadable **ice charts**, weather, and reporting/instructions; email-subscription accounts to follow ships and ports. **This is icebreaker-assistance coordination and traffic restriction publishing, not route optimisation** — VERIFIED by absence of any optimisation feature on the site.
- **IBPlott** — **VERIFIED** (via [Canadian Journal of Remote Sensing 33(5), doi:10.5589/m07-042](https://www.tandfonline.com/doi/abs/10.5589/m07-042), "A system for icebreaker navigation and assistance planning using spaceborne SAR information in the Baltic Sea"): a **GIS-type workstation developed by VTT Technical Research Centre of Finland**, used by **captains and mates on Finnish and Swedish icebreakers**, which "combines and displays all available relevant information required for making routing and ship assistance decisions", fed with **RADARSAT and Envisat ASAR** imagery. **INFERRED:** decision *support* for a human icebreaker officer — the same category as IcySea, one generation earlier and regionally scoped. Not an optimiser.
- Relevance to us: **the Baltic is the most operationally mature ice-navigation region in the world and it still runs on human decision-making over a GIS display.** Useful counterweight to any claim that full automation is the obvious answer — and consistent with StormGeo keeping human analysts (§2).

### 9.3 AARI (Arctic and Antarctic Research Institute, Roshydromet)

- **VERIFIED** ([aari.ru](https://www.aari.ru/)): operational real-time data (`data/realtime`) and climate data portals; a **Department of Ice Regime and Forecasts** producing "долгосрочных прогнозов ледовой обстановки в Арктике" — **long-range forecasts of Arctic ice conditions**; institutional framing "helps ships safely traverse icy seas"; operates Antarctic stations.
- **VERIFIED** (Tran et al. 2023 review, §4.5 and Table 6): AARI is used as an ice-forecast data source by 2 of the 32 reviewed routing studies (May et al. 2018, 2020) — so its forecast products are real and consumable by routing systems.
- **UNVERIFIED and important:** whether AARI publishes **Antarctic** operational ice charts or forecasts as a product, and whether any of it is accessible outside Russia. The site's forecast department is described as Arctic. Given the institute's name and its Antarctic station operations, Antarctic capability plausibly exists, but I found no product page. Do not claim it either way.
- Language/access barrier is real: the site is Russian-only in the sections reached, and no English product catalogue was found.

### 9.4 Canadian Ice Service (ECCC)

**VERIFIED** by reading the live operational product catalogue at [iceweb1.cis.ec.gc.ca/Prod/page1.xhtml](https://iceweb1.cis.ec.gc.ca/Prod/page1.xhtml) (the canada.ca landing pages returned 403/404 to automated fetch — stated so rather than skipped). The full published product taxonomy:
- **Ice Charts:** Daily (colour and B&W), Regional, Image Analysis (WMO colour / CIS colour), St. Lawrence River, and — notably — **Iceberg Chart**.
- **Ice Bulletins:** Ice Forecasts, and **Iceberg Bulletins**.
- **Ice Forecast:** **Thirty (30) Day** and **Seasonal Outlook**.
- **Ice Graphs:** Ice Cover Graphs.
- **Regions:** Arctic Ocean, Western Arctic, Eastern Arctic, Hudson Bay, East Coast, Great Lakes. **No Antarctic coverage** — VERIFIED from the region list.
- **No routing product** in the catalogue — VERIFIED by absence.
- **No probabilistic/ensemble product** in the public catalogue — VERIFIED by absence, though a "Seasonal Outlook" plausibly carries qualitative confidence language in its text. **UNVERIFIED** whether it does.

CIS is the useful *product-design* reference: it is the only major ice service that ships an operational **30-day** forecast and a **seasonal outlook** alongside daily charts *and* a separate iceberg product line. That layered horizon structure (nowcast / 30-day / seasonal) is worth copying as an information architecture even though the region is wrong.

### 9.5 Northern Sea Route routing tools

**Weak evidence base — flag this honestly.** **UNVERIFIED at the technical level.** What could be established: Rosatom became sole operator of NSR infrastructure in 2018 with responsibility for navigational support and shipping organisation; Russian government funding of roughly **4 bn ₽** was allocated for an NSR "ice navigator", and a digital navigation platform worth ~**2.9 bn ₽** was reported created in August 2021 with Rosatom implementing ([tadviser.com NSR article](https://tadviser.com/index.php/Article:Northern_Sea_Route), secondary source; [moderndiplomacy.eu](https://moderndiplomacy.eu/2025/10/24/how-rosatom-is-turning-arctic-geopolitics-into-infrastructure/), secondary). **No public technical specification, no methodology, no accessible product page, no peer-reviewed description was found.** Sources are news/secondary, not agency documentation. Treat as: a substantial state-funded Arctic routing platform very likely exists; nothing about its method, accuracy, uncertainty handling, or iceberg capability can be responsibly asserted. Not a usable benchmark.

### 9.6 ArcticWeb — dead

**VERIFIED as unreachable:** `https://arcticweb.e-navigation.net/` — **proxy refused the connection** on 2026-09-02. ArcticWeb was a Danish Maritime Authority / DTU e-Navigation prototype (route exchange, voyage planning and reporting for Arctic waters, ~2012–2015 era). **INFERRED, not verified: the service is defunct / absorbed into the Maritime Connectivity Platform lineage.** I did not confirm its fate and am not asserting it. Do not cite ArcticWeb as a live competitor.

### 9.7 Wärtsilä / NAPA — ice-aware voyage optimisation

**VERIFIED, and the answer is negative.** Reading [NAPA Voyage Optimization](https://www.napa.fi/software-and-services/ship-operations/napa-fleet-intelligence/voyage-optimization/) directly: the page contains **no mention of sea ice, ice class, ice charts, or polar navigation**. It considers "all weather conditions and the shallow water effect", optimises for "arrival time, constant speed, RPM, engine load, maximum daily profit, or overall cost reduction", using "vessel-specific performance models and weather forecasts". No uncertainty quantification is described. [Wärtsilä Voyage Optimiser](https://www.wartsila.com/marine/products/fleet-optimisation/voyage-and-ports/voyage-optimiser-tool) is likewise framed as weather/commercial voyage planning — **no ice capability documented; UNVERIFIED whether an unpublished ice module exists.**

**Conclusion:** the mainstream commercial voyage-optimisation vendors are open-water weather-routing products. Only StormGeo (§2) documents ice as an explicit input. The "ice-aware voyage optimisation" market is far thinner than the general voyage-optimisation market — which is why the routing half of this PS is genuinely open.

### 9.8 One more research competitor worth knowing — Prydz Bay, 2025

**VERIFIED** ([IEEE JSTARS 2025, doi:10.1109/jstars.2025.3593948](https://doi.org/10.1109/jstars.2025.3593948), gold OA): *Satellite-Borne and Airborne Sea Ice Remote Sensing for Antarctic Applications in Safe Navigation between the Icebreaker and Research Station: A Case Study in Prydz Bay.* An integrated framework for safe path planning in **Prydz Bay, East Antarctica** — the same bay as **Bharati** — supporting the Chinese programme at Zhongshan Station. Extracts landfast sea ice, **icebergs**, and bare rock from large-scale satellite imagery plus surface smoothness; adds **UAV** data on landfast-ice melt and microtopography; feeds all of it into a **cost path analysis** to determine optimal routes across landfast ice.

Why this matters: **a foreign national Antarctic programme published, in 2025, an icebreaker-to-station route-planning framework for the bay Bharati sits in, and it does include icebergs.** It is still a static, deterministic, snapshot cost-path method with no forecast, no ML, and no uncertainty — but it is more recent and more multi-source than Mishra et al. 2021, and a well-read judge could raise it. Know it exists.

### 9.9 Also relevant, for horizon-setting

**VERIFIED** ([ERL 2025, doi:10.1088/1748-9326/adf3ce](https://doi.org/10.1088/1748-9326/adf3ce), gold OA): *Future Antarctic marine accessibility in a warming world* — CMIP6-based projections of Southern Ocean accessibility for open-water and **Polar Class 6** vessels at 1.5/2/3 °C warming, finding near-complete February accessibility even at 1.5 °C and >50% winter PC6 accessibility at 3 °C. Not a competing system, but the citation to use if asked "why build this if the ice is going away" — the answer is that accessibility increases *on average* while the post-2016 Antarctic variability that makes any given season hard (§2) does not.

---

## 10. Comparison table

Cross-referenced rows marked **[§2]** were established in the first pass and are reproduced here only for contrast — no new research claim is made about them.

| System | Operator | Routing? | Icebergs? | Forecast horizon | Uncertainty quantified? | Antarctic? | Offline / low-bandwidth? |
|---|---|---|---|---|---|---|---|
| **IcySea** | Drift+Noise Polar Services + MET Norway | **No** — "automatic route suggestions… an idea in development" (VERIFIED) | **Not documented** (VERIFIED by absence across all public sources) | Point ice-**drift** forecast, horizon **not published**; SIC refreshed 8×/day (VERIFIED) | **No** (VERIFIED by absence) | **Yes**, both poles — but forecast dev work documented in Arctic/Svalbard (VERIFIED) | **Yes** — PWA, full browser cache, works with no network, Iridium-tested (VERIFIED) |
| **PolarView.AQ** | British Antarctic Survey (Polar View) | **No** (VERIFIED by absence) | **Yes** — iceberg tracking, Antarctic only (VERIFIED) | None published — observation/chart delivery | **No** | **Yes** — dedicated Antarctic viewer (VERIFIED) | **Yes** — explicit low-bandwidth mode (VERIFIED) |
| **Polar View Ice Logistics Portal** | Polar View / IICWG | No | Via national charts | n/a (chart repository) | No | Partial (repository of national charts incl. USNIC) | Unverified |
| **PolarRoute (MeSAPro)** **[§2]** | British Antarctic Survey | **Yes** | No | Inherits input product | No | Yes | No — server-side toolchain |
| **StormGeo s-Routing / s-Planner** **[§2]** | StormGeo (DTN) | **Yes** | Not documented | Weather-routing horizon | Not published | Not documented | Onboard client; specifics unverified |
| **NAPA Voyage Optimization** | NAPA Ltd | Yes (weather/fuel) | No | Weather forecast horizon | No | **No — ice not mentioned at all** (VERIFIED) | Unverified |
| **Wärtsilä Voyage Optimiser** | Wärtsilä | Yes (weather/commercial) | No | Weather forecast horizon | No | **No ice capability documented** | Unverified |
| **BALTICE / IBNet** | Baltic Icebreaking Management (FTIA + SMA) | **No** — icebreaker-assistance coordination & traffic restrictions (VERIFIED) | No | Ice charts + weather, nowcast | No | **No** — Baltic only | Web + email subscription |
| **IBPlott** | VTT Finland; Finnish & Swedish icebreakers | **No** — GIS decision-support workstation for human officers (VERIFIED) | No | SAR-driven NRT | No | **No** — Baltic | Onboard workstation |
| **AARI** | Roshydromet (Russia) | No (advisory) | Unverified | **Long-range Arctic** ice forecasts (VERIFIED); horizon unspecified | No | **Unverified** — Arctic products documented; Antarctic products not found | No |
| **Canadian Ice Service** | ECCC (Canada) | **No** (VERIFIED by absence from product catalogue) | **Yes** — Iceberg Chart + Iceberg Bulletins (VERIFIED) | Daily charts, **30-day forecast**, **Seasonal Outlook** (VERIFIED) | Not in public catalogue | **No** — Canadian waters only (VERIFIED from region list) | Web download |
| **NSR digital services / "ice navigator"** | Rosatom / NSR Directorate | Claimed, **UNVERIFIED** | Unverified | Unverified | Unverified | **No** — Arctic | Unverified |
| **ArcticWeb** | Danish Maritime Authority / DTU | Was route exchange + voyage planning | No | n/a | No | No | **DEAD — site unreachable** (VERIFIED 2026-09-02) |
| **USNIC Antarctic iceberg product** **[§2]** | US National Ice Center | No | **Yes** — named bergs ≥20 sq NM or ≥10 NM longest axis, weekly | Position updates only, no drift forecast | No | **Yes** | File download |
| **CMEMS SEAICE L4 NRT** **[§2]** | Copernicus / OSI-SAF | No | No | **10 days** | No (deterministic L4) | Yes | No |
| **SAC/ISRO Sea Ice Advisory (ISEA)** | SAC/ISRO + MoES/NCPOR | **Advisory only** — "penetrable passage" found by standardised *human* SAR interpretation (VERIFIED) | **Yes** — bergs distinguished in SAR by interpreter (VERIFIED) | **None** — NRT nowcast only | No | **Yes** — around both Indian stations (VERIFIED) | Delivered to vessel; mechanism unverified |
| **Mishra et al. 2021 (Bharati–Maitri)** | SAC/ISRO + PDEU (research) | **Yes** — Dijkstra, **min voyage time only** (VERIFIED via Tran et al. 2023 Tables 2/5) | **No** | **None** — static single-date ice (VERIFIED via Table 7) | **No** | **Yes** — the exact corridor | n/a — offline research code |
| **Prydz Bay framework 2025** | Chinese Antarctic programme (research) | **Yes** — cost-path over landfast ice | **Yes** — iceberg distribution mapped | **None** — snapshot | No | **Yes** — Prydz Bay (Bharati's bay) | n/a |
| **Schütz 2014 / Choi et al. 2015** | research | Yes | No | Ice-POM forecast (Choi) | **Yes** — scenario tree (Schütz); uncertain ice prediction model (Choi) | **No** — Arctic | n/a |
| **THIS PROJECT (SIH26059)** | *target* | **Yes** — multi-objective, uncertainty-weighted | **Yes** — physics+ML residual drift forecast (§4.1) | ML SIC forecast, lead-time-resolved | **Yes** — forecast uncertainty carried into route cost (§4.3) | **Yes** — Cape Town→station + inter-station corridors | **Yes** — cached tiles + staleness/confidence decay (§4.5) |

---

## 11. The gap we can honestly claim

**Every individual capability in our design already exists somewhere in the table. The claim is about composition, and about one cell that is empty everywhere.**

What we cannot claim, and must stop claiming:
- Not "the first Antarctic ice information system for ships" — **PolarView.AQ** (BAS, free) already delivers Antarctic sea ice *and* Antarctic iceberg tracking to ships in a low-bandwidth mode.
- Not "the first to work offline at Iridium bandwidth" — **IcySea** is a PWA that runs with no network, Iridium-tested, in commercial service.
- Not "the first to route in Antarctic ice" — **Mishra et al. 2021** did it on the Bharati–Maitri corridor and validated against a real ISEA voyage; **PolarRoute** (§2) does Antarctic routing; the **Prydz Bay 2025** framework does station-approach path planning with icebergs.
- Not "the first to consider uncertainty in ice routing" — **Schütz (2014)** used a scenario tree over ice-prediction uncertainty; **Choi et al. (2015)** planned paths on an explicitly uncertain ice prediction model.
- Not "the first to use ML on Antarctic sea ice" — **ANTSIC-UNet** (§2) exists.

What is defensibly ours, stated as a single sentence:

> **No system or published study — operational or academic — takes a machine-learned sea-ice forecast, carries that model's own lead-time-dependent uncertainty into a multi-objective route cost alongside an iceberg-drift forecast, and does it on the Antarctic corridor an actual national programme sails.**

Each clause of that sentence is load-bearing and each is backed by a specific row of the table:
1. **Learned forecast + routing are disjoint today.** The ML forecasting work (IceNet, ANTSIC-UNet) publishes forecasts; the routing work (all 32 studies in Tran et al. 2023) consumes ice charts or dynamical-model output. **Table 6 of the review lists every ice source used by every reviewed routing study: CIS, HELMI, Ice-POM, NSIDC, TOPAZ4, HIROMB, NMEFC, UK Met Office, AARI, and customised models. Not one is a machine-learned forecast.** (VERIFIED.)
2. **Uncertainty propagation is the review's own named open direction**, in its concluding sentence — "treat the ice navigating problem under uncertainties" — and only 2 of 32 studies attempt it at all, neither with a learned model's uncertainty. (VERIFIED.)
3. **Static ice is the field's default:** 28 of 32 studies hold ice fixed. (VERIFIED, Table 7.)
4. **Icebergs and sea ice are in separate products everywhere.** IcySea has sea ice, PolarView.AQ has both but forecasts neither, USNIC has berg positions but no drift model, CIS has an iceberg line but no Antarctic. **No system in the table forecasts iceberg drift and sea ice and routes on both.** (VERIFIED by absence.)
5. **The Antarctic asymmetry is systematic, not accidental.** IceNet is Arctic-validated (§2); IcySea's forecast development is Svalbard; AARI's forecast department is Arctic; CIS is Canadian; the Baltic services are Baltic; NSR is Arctic; NAPA/Wärtsilä are open-water. The Southern Ocean gets observation products, not prediction products.

**One more honest caveat to carry into the deck:** claim (1) has a soft edge. IcySea's ice-drift layer is "bias corrected" model output; if that bias correction is itself learned, the disjointness is narrower than stated. Drift+Noise publishes no method, so this is **UNVERIFIED in both directions** — phrase the claim as "no *published* system", which is true and checkable.

---

## 12. Benchmark bar

The specific, measurable things this project must beat. These are the numbers to put on a slide, and the experiments to actually run.

### 12.1 Against Mishra et al. 2021 — the direct precedent

The paper's own quantitative results are **UNVERIFIED** (full text unobtainable, §6). So the bar cannot be "beat their published number" until someone pulls the PDF. Instead:

1. **Reimplement their method as our own baseline, on our own data.** Dijkstra over a grid, edge weight = traversal time, ship speed from **Riska (1997)** ice resistance + wind resistance, ice field from **NSIDC** SIC, held **static**. This is fully specified by the review's tabulation — we can build it without the paper. **Everything we claim must be measured against this baseline, not against a strawman A\*.**
2. **Beat it on their own metric, on their own corridor, on held-out seasons.** Same Bharati↔Maitri leg, multiple ISEA seasons, evaluate **voyage time**. If our uncertainty-aware, forecast-driven router does not beat static-Dijkstra on plain voyage time, we have no story — an MoES judge will ask exactly this.
3. **Beat it on metrics it structurally cannot address**, and say why: (a) **fuel** — it optimises time only (Table 2), so a multi-objective time/fuel/risk frontier is new ground; (b) **feasibility under a moving ice field** — replay each route forward through the *actually observed* subsequent ice and count how often the static-optimal route becomes blocked or enters a higher POLARIS risk band that the moving-ice-aware route avoids. This is the single most persuasive demo available to us and it directly exercises the 28-of-32 gap.
4. **Match its validation standard or lose the argument.** It is 1 of only 6 of 32 studies that validated at all. **Validate against real ISEA voyage tracks (AIS / expedition logs) for at least 3 seasons** — that alone puts us above 90th percentile of the published literature. And pre-empt the review's own critique of AIS validation (§8.2): report agreement with the sailed track *and* state explicitly that the sailed track is not assumed optimal.

### 12.2 Component bars

| Component | Must beat | Metric | Source of the bar |
|---|---|---|---|
| Sea-ice concentration forecast | **CMEMS 10-day operational forecast**, plus persistence and climatology | RMSE and **Integrated Ice-Edge Error (IIEE)** per lead day, on held-out austral summers, restricted to the corridor | §2 (CMEMS); ANTSIC-UNet uses IIEE |
| Forecast **uncertainty** | Nothing to beat — **nobody publishes one**. So the bar is *calibration*, not comparison | **CRPS**, reliability diagram / PIT histogram, and empirical coverage of the stated interval. An 80% band must contain truth ~80% of the time | §8 — the claim is uncertainty-*aware*, so the uncertainty must be shown to be honest, or the whole differentiator collapses |
| Iceberg drift | Pure-physics drift and persistence baselines | Displacement error (km) at 24/48/72 h against **BYU/NIC** positional tracks, Southern Ocean bergs | §2 (IDRIFTNET pattern, BYU/NIC data) |
| Ship speed in ice | The field's honest state of the art | Speed-prediction error. **Jeong et al. (2018) — the only real-voyage validation in the reviewed literature — reported estimated-vs-actual speed mismatch of 0–50%.** Beating a 50% worst case is the realistic target; claiming single-digit error without a real voyage is not credible | Tran et al. 2023, §4.7 |
| Routing | Reimplemented Mishra-style static Dijkstra | Voyage time, fuel, and **blocked-route rate under replayed real ice** | §12.1 |
| Bandwidth | **IcySea** — a PWA that runs fully offline after first cache, at Iridium rates | Bytes per corridor-day sync; must be in the same order of magnitude or the offline claim is empty rhetoric | §5.5 |

### 12.3 The one-line bar for the deck

> Against a faithful reimplementation of the published Indian precedent (Dijkstra + Riska resistance + static NSIDC ice, minimising voyage time — Mishra et al., *Polar Science* 2021), on held-out real ISEA voyage seasons on the Bharati–Maitri corridor: **equal or better voyage time, lower fuel, a measurably lower rate of routes that become blocked when the ice field is replayed forward, and a calibrated uncertainty band — the last of which nothing in the published literature provides.**

---

## Open items from pass 2

- **Mishra et al. 2021 full text not obtained.** ScienceDirect 403 (Cloudflare), ResearchGate 403, NIPR repository record 16868 is metadata-only (empty `files`). Grid resolution, exact ice/wind resistance equations, and all quantitative validation numbers are **UNVERIFIED**. Needs institutional access. → `docs/backlog.md`
- **IcySea's risk-assessment methodology is undocumented.** POLARIS/RIO is inferred from three converging signals, not confirmed. Do not state it as fact. A 14-day trial registration would settle it, along with the real layer catalogue and forecast horizon — the app is token-gated and its pre-auth JS bundle contains none of it.
- **IcySea pricing is not published anywhere.** Any figure in a deck would be fabricated.
- **AARI Antarctic products unconfirmed.** Arctic forecast capability verified; Antarctic product catalogue not found. Russian-only site.
- **NSR / Rosatom "ice navigator" is news-sourced only.** No technical specification, no methodology, no accuracy figures. Not usable as a benchmark.
- **ArcticWeb unreachable** (proxy refused). Its fate is inferred, not verified.
- **Canadian Ice Service canada.ca landing pages returned 403/404** to automated fetch; the product taxonomy above came from the operational portal `iceweb1.cis.ec.gc.ca` directly. Whether the Seasonal Outlook carries probabilistic content is unverified.
- **`drift-noise.com` (hyphenated) refused the connection**; only `driftnoise.com` is live.
- **Whether IcySea's "bias corrected" ice drift is machine-learned** is unverified in both directions and softens differentiation claim (1) in §11 if it is.
- Schütz (2014) and Choi et al. (2015) were characterised **only through Tran et al. (2023)'s description**; neither primary text was read.
