# STAGE 01 — RESEARCH FOUNDATION (GATED)
## ENTRY GATE
Before doing research, inspect the repository and ask whether this stage has already been completed. Verify any existing dossier, sources, dataset/model matrix, and research artifacts before deciding to redo anything.

MISSION
Research the project completely before making major architecture or AI/ML decisions. DO NOT redesign or implement the system in this stage.

PRIMARY OUTPUT
Create a research dossier in the repo that is authoritative, traceable, and implementation-ready.

MANDATORY RESEARCH QUESTIONS
- What exactly does PS-26059 require?
- What are the actual scientific subproblems: sea-ice concentration forecasting, iceberg trajectory prediction, and safe/fuel-efficient routing?
- What datasets are genuinely available for each?
- Which Indian and foreign sources are best for each capability?
- What are their spatial/temporal resolution, latency, coverage, historical depth, licensing, cost, processing needs, and operational maturity?
- What professional maritime/polar standards and operating constraints affect the system?
- What vessel information must be known before a route can be judged?
- How should Polar Ship Category, Polar Class, ice class, Polar Ship Certificate, PWOM, Polar Service Temperature, vessel machinery/propulsion, draft, loading/stability, maneuvering, endurance, and other vessel-specific factors be represented?
- What is POLARIS; what are RIV and RIO; where is it appropriate; what are its Antarctic limitations; and what alternatives such as AIRSS or operator/class methods should be considered?
- What Antarctic environmental/legal restrictions exist?
- What navigation/chart-quality/UKC concepts must be considered?
- What historical voyage, incident, climate, and route information exists for Cape Town → Maitri/Bharati?
- Which competitors/open-source systems already solve parts of the problem?
- What does each competitor do better or worse?
- What should be reused rather than rebuilt?

HUGGING FACE MODEL REUSE RESEARCH
Investigate Hugging Face models as reusable building blocks, NOT as automatic drop-in solutions. Verify model card, license, inputs, domain, training data, inference cost, and whether Antarctic data/fine-tuning are required.

Candidates currently identified for evaluation include:
- ibm-nasa-geospatial/Prithvi-WxC-1.0-2300M
- ibm-nasa-geospatial/Prithvi-WxC-1.0-2300M-rollout
- ibm-nasa-geospatial/Prithvi-EO-2.0-300M
- ibm-nasa-geospatial/Prithvi-EO-2.0-600M
- ibm-esa-geospatial/TerraMind-1.0-small
- ibm-esa-geospatial/TerraMind-1.0-base
- microsoft/aurora
- OneScience-Group/Pangu_Weather
- OneScience-Group/SatMAE

Current web evidence to verify during research:
- Prithvi WxC is a weather/climate foundation model; its rollout variant is specifically optimized for forecasting and uses 6-hour autoregressive rollout in the published model card; the base model carries a CDLA-Permissive-2.0 license. citeturn635825search4turn635825search7
- Prithvi EO 2.0 is a spatiotemporal Earth-observation foundation model, with Apache-2.0 licensing on the base 300M repository; it is designed for spatiotemporal EO inputs rather than being an Antarctic sea-ice model out of the box. citeturn731561search4turn731561search8
- TerraMind 1.0 is a multimodal EO foundation model from IBM/ESA/Jülich; the base and small repositories are available on Hugging Face, with the base repository listing Apache-2.0. citeturn731561search0turn731561search1turn731561search9
- Microsoft Aurora is an Earth-system foundation model on Hugging Face with an MIT license and includes atmospheric/ocean-wave related Earth-system modeling capabilities; determine whether it is useful for this project's weather/ocean layer rather than assuming it is a sea-ice forecaster. citeturn635825search0
- The OneScience Pangu-Weather repository is an Apache-2.0 Hugging Face implementation/reproduction trained on ERA5 and intended for global short-to-medium-range weather forecasting; verify whether its implementation and weights are suitable for this project. citeturn635825search1
- The OneScience SatMAE repository uses a CC-BY-NC-4.0 license, so commercial/startup reuse requires careful licensing review. It is intended for temporal/multispectral remote-sensing representation learning, not direct sea-ice forecasting. citeturn635825search2

IMPORTANT:
Do NOT conclude that any of these models is suitable simply because it appears on Hugging Face.
Determine:
- direct applicability;
- adaptation/fine-tuning requirement;
- required input variables;
- whether Antarctic data are represented;
- inference requirements;
- license compatibility;
- whether the model should be used, adapted, benchmarked only, or rejected.

RESEARCH OUTPUT FORMAT
For every major claim/source/model:
SOURCE → CAPABILITY → EVIDENCE → LIMITATIONS → LICENSE → COST → DATA REQUIREMENTS → ANTARCTIC RELEVANCE → RECOMMENDATION.

STOP after the research dossier and source/model decision matrix are complete.

# 17. ANTARCTIC / INDIA-SPECIFIC CONTEXT

Use the Indian Antarctic Programme as a concrete design reference.

NCPOR is India’s nodal organisation for the Antarctic Programme.

Maitri is in the Schirmacher Oasis at approximately 70°45'52"S, 11°44'03"E and is inland from the coast.

Bharati is in the Larsemann Hills near Prydz Bay at approximately 69°24.41"S, 76°11.72"E.

The maritime operating pattern has commonly involved Cape Town staging and chartered-vessel service to Bharati and Maitri.

NCPOR’s 2025-26 planning material used a tentative:

Cape Town → India Bay → Larsemann Hills → India Bay → Cape Town

sequence.

The 45th ISEA departed Cape Town on 25 Dec 2025 aboard MV Vasiliy Golovnin.

The official documents establish voyage patterns/timings but not every bridge waypoint. Treat planning itineraries as planning baselines, not guaranteed actual tracks.

DO NOT fabricate exact bridge waypoints, mooring points, chart depths, ice limits, or current-voyage tracks unless provided by authoritative data.

PUBLIC AIS IS NOT THE SAME AS THE SHIP’S PRIMARY NAVIGATION RECORD.

---


# 20. ECOLOGY / RESTRICTED / HAZARDOUS AREAS

The system should not hinder ecology and should not deliberately enter hazardous or forbidden zones.

Research Antarctic voyage policies, dangerous/restricted areas, environmental constraints, and areas where a ship should not sail or should not enter.

Safety and ecological restrictions must be represented as route constraints / no-go logic where authoritative data support them.

---


# 21. ROUTE INTELLIGENCE / HISTORY / CLIMATE CHANGE

Research whether past incidents occurred along the routes used toward Maitri and Bharati from Cape Town.

The system should understand:

- common occurrences along the route;
- commonly used routes for different times of year;
- historical incident/near-incident patterns where reliable data exist;
- that climate change/global warming can produce less predictable occurrences.

A future model scope is to learn from past mistakes/incidents and use those lessons while suggesting routes.

Where this future scope is demonstrated in the prototype, it should be clearly marked as future/simulated unless trained/validated data genuinely exist.

---


# 29. DATA SOURCE STRATEGY — INDIA + FOREIGN, OBJECTIVE COMPARISON

Use Indian government/research sources where technically competitive, but do NOT prioritize Indian infrastructure for ideological, nationalistic, or “local-for-local” reasons.

Treat every Indian government/research source as a candidate to be evaluated objectively against the best foreign alternative for the same capability.

For each data source, model, compute platform, communication service, API, map layer, weather product, ocean product, satellite product, or infrastructure component, compare:

- scientific accuracy;
- spatial resolution;
- temporal resolution;
- update interval / latency;
- Antarctic and Southern Ocean coverage;
- historical depth;
- reliability and availability;
- API/data accessibility;
- licensing and usage restrictions;
- cost;
- processing requirements;
- interoperability;
- operational maturity.

Use an Indian government/research source when it is demonstrably competitive or superior on the dimensions relevant to the component.

Use a foreign source when it is materially better, more current, more accurate, more complete, more reliable, unavailable from India, or necessary for validation.

Where scientifically useful, combine Indian and foreign sources:

- Indian primary ingestion + foreign validation;
- foreign primary ingestion + Indian independent cross-check;
- multi-source ensemble/fusion when this improves prediction quality.

Never assume an Indian service covers Antarctica merely because the organization operates internationally. Verify actual spatial coverage, update frequency, resolution, and current availability before integrating it.

Do not hard-code architecture around provider nationality. Build provider-agnostic adapters so the system can switch between Indian and foreign sources based on measured data quality and availability.

Objective:

> BEST AVAILABLE SYSTEM = MAXIMUM USE OF CAPABLE EXISTING INDIAN INFRASTRUCTURE + FOREIGN SOURCES WHERE THEY ARE TECHNICALLY BETTER OR NECESSARY.

The final system must contain a documented justification for every major source choice, including why an Indian source was selected over a foreign alternative or why a foreign source was retained.

Research Indian websites and sources, including https://data.ncpor.res.in/ and other relevant NCPOR/MoES/Indian sources, alongside foreign sources.

Also investigate open-source material available through the provided Hugging Face access/MCP/plugin, GitHub, Kaggle, and other useful open-source projects.

---


# 30. OPEN-SOURCE / COMPETITOR RESEARCH

Research existing competitors and related systems, including systems similar to IcySea and professional polar/navigation visualization tools.

Determine:

- which competitors already exist;
- what they do;
- where they are better than this project;
- where they failed;
- why they failed;
- what gaps they leave;
- what can be borrowed/reused legally and technically from open-source implementations;
- what a strong team would likely build for the same SIH problem statement;
- how this system can be materially better.

Do not create a strawman competitor. Evaluate serious alternatives fairly.

---


# 31. RESEARCH / POLICY / STANDARDS BASE

Use authoritative sources where available, including the material already identified in the research brief:

- IMO Polar Code
- IMO Shipping in Polar Waters
- IMO Voyage Planning A.893(21)
- IMO ECDIS
- IHO ENC / S-100 ecosystem
- WMO Sea-Ice Guidance
- WMO Manual 558
- US National Ice Center Antarctic Ice Charts
- USNIC Antarctic Icebergs
- British Antarctic Survey Mapping / Polar View
- BAS Sea Ice Observations for Ship Navigation
- NCPOR Research Stations
- NCPOR 2025 Planning Advisory
- NCPOR 45th ISEA update
- PIB / MoES 43rd ISEA voyage
- COMNAP Antarctic facilities / vessels

Retain the URLs and source mappings from the source appendix below.

The system should be aligned with the professional digital navigation stack including:

- ENC / ECDIS;
- IHO S-101 electronic navigational charts;
- S-102 bathymetric surfaces;
- S-104 water-level information;
- S-111 surface currents;
- S-124 navigational warnings;
- AIS;
- radar / ARPA;
- GNSS;
- gyro;
- echo sounder;
- weather/ocean products;
- GMDSS safety communications.

The research brief notes that IHO S-101 is the operational ENC product specification from 1 January 2026 and identifies the wider S-100 ecosystem. Verify current details before implementation decisions.

---


# 41. OPENAI / CLAUDE-CODE DEVELOPMENT TOOLS ALREADY IDENTIFIED

Use open-source material and the development resources already provided by the user where useful, including:

- Hugging Face access/MCP/plugin;
- GitHub;
- Kaggle;
- MLflow;
- related skills/plugins.

Inspect and use what is genuinely useful rather than adding complexity for its own sake.

---


# 42. MLflow / CURRENT DEVELOPMENT ENVIRONMENT

Current environment information supplied by the user:

- OS: WSL (Linux)
- Claude Code: 2.1.252
- Claude executable: `/home/jiteesh/.local/bin/claude`
- `python` was initially unavailable; `python3` exists.
- A project-local Python `.venv` is being set up.
- MLflow has not yet been connected to Claude Code.
- Desired MLflow purpose: experiment/model tracking and Claude Code access through MCP.
- Keep the MCP tool surface minimal to avoid unnecessary context/token usage.
- Do not add W&B unless there is a concrete reason.

When taking over this setup:

1. First inspect the current environment.
2. Verify what has already been installed/configured.
3. Complete MLflow setup.
4. Start/configure the local MLflow server.
5. Connect MLflow to Claude Code through MCP.
6. Verify the connection with an actual test experiment/run.
7. Do not blindly assume commands or overwrite existing configuration.
8. Explain actions briefly as you go.
9. Stop if an issue requires a user decision.

---


# 43. RESEARCH EXECUTION RULES

Research before committing to low-level system decisions where the prompt explicitly asks you to research.

Research should determine:

- what data is actually needed;
- what data must truly be present;
- what can be derived;
- what can safely be cached;
- what needs live updates;
- what update intervals are operationally relevant;
- what bandwidth is required;
- what communication technologies are practical;
- what can run onboard;
- what belongs on shore/land infrastructure;
- what already exists and should be reused;
- what must be built from scratch.

The user explicitly acknowledges gaps in the system design and delegates the remaining technical decisions to the implementation/research process after the desired product behavior and architecture are understood. Use that delegation responsibly; do not erase the user’s stated intent.

---


# 48A. RESEARCH-DRIVEN SYSTEM HARDENING — ADD THIS WITHOUT REMOVING OR WEAKENING EXISTING REQUIREMENTS

This section is an additional research and reasoning layer. It does NOT replace, delete, or weaken any requirement elsewhere in this document. Everything already specified remains active.

The purpose of this section is to prevent implementation from drifting into an attractive but scientifically or operationally inaccurate Antarctic navigation product.


## 48A.3 MODEL THE VESSEL AS A FIRST-CLASS ENTITY

Do not model the own ship as only a moving latitude/longitude point.

Research and model the vessel's operational envelope, including where authoritative information exists:

- IMO Polar Ship Category A/B/C;
- Polar Ship Certificate;
- applicable Polar Class / classification notation and distinction from IMO Polar Ship Category;
- applicable ice class and classification-society rules;
- Polar Water Operational Manual (PWOM);
- Polar Service Temperature and relevant low-temperature operating limitations;
- ship-specific ice operating limitations;
- ice-strengthened structure / hull capability where authoritative information is available;
- propulsion power and propulsion limitations;
- steering and maneuverability;
- stopping and turning characteristics;
- ability to make progress in different ice regimes;
- draft;
- displacement/loading condition;
- trim;
- stability and freeboard where operationally relevant;
- minimum safe under-keel clearance;
- machinery limitations in low temperatures;
- sea suction / intake and related cold-weather considerations where relevant;
- fuel, stores, endurance and reserve policy;
- bridge equipment and redundancy;
- crew competence, polar training and watchkeeping constraints;
- emergency equipment / lifesaving capability;
- operational condition of the machinery and propulsion system.

Do not invent vessel thresholds. Where a limit is ship-specific, obtain it from authoritative ship/class/PWOM/certification information or explicitly represent it as an unverified assumption.

The route engine must evaluate:

ENVIRONMENT × VESSEL CAPABILITY × MISSION × FORECAST × UNCERTAINTY

rather than evaluating the environment in isolation.


## 48A.4 POLARIS MUST BE RESEARCHED, NOT BLINDLY ASSUMED

Research the Polar Operational Limit Assessment Risk Indexing System (POLARIS), including:

- Risk Index Value (RIV);
- Risk Index Outcome (RIO);
- relationship to vessel ice class / polar capability;
- input ice conditions;
- resulting operational interpretation;
- limitations;
- provenance of thresholds and methodology;
- applicability to Antarctic operating conditions;
- whether the specific modeled vessel and voyage are appropriate for its use.

POLARIS may be represented in the GUI as an ice-operational risk assessment layer or panel where justified.

Do NOT treat a POLARIS value as a universal or autonomous safety decision.

Do NOT make POLARIS the entire route optimizer.

Do NOT assume an Arctic-derived method is automatically valid for Antarctic conditions.

Where Antarctic applicability is uncertain, surface this explicitly and investigate region-specific validation.

Research whether other recognized ice-navigation risk/operational assessment methods are relevant, including AIRSS and any vessel-, flag-, class-, or operator-specific procedures. Do not implement any of them merely because their name appears here; determine their actual applicability first.


## 48A.7 FORECAST HORIZONS MUST BE EXPLICIT

Do not use a generic concept of "future."

Research and document appropriate horizons separately for:

- nowcast / current state;
- short-term forecast;
- medium-term forecast;
- longer-range planning.

For sea ice, iceberg trajectories and weather, determine empirically or from authoritative literature:

- useful prediction horizon;
- expected uncertainty growth;
- update frequency;
- observation latency;
- model degradation with forecast time.

The UI should communicate forecast horizon and confidence rather than making near-term and long-range forecasts look equally certain.


## 48A.10 "BETTER THAN WHAT?" — BASELINES ARE MANDATORY

Every major AI/ML claim must have a baseline.

Research appropriate baselines for:

### Sea-ice forecasting
Consider persistence, climatology, simple statistical methods, physics/model products, or other established baselines as appropriate.

### Iceberg trajectory prediction
Consider persistence/drift-based and other defensible baselines before claiming a learned model is superior.

### Route planning
Compare the proposed approach against defensible alternatives such as:

- shortest-path / geometry-only routing;
- ice-unaware routing;
- simple forecast-aware routing;
- established operational routing methods where data are available;
- persistence-based environmental routing.

Do not claim the AI is better merely because it produces a prediction.


## 48A.11 SCIENTIFIC VALIDATION IS PART OF THE PRODUCT

For every core predictive component, establish:

- input data;
- target/ground truth;
- train/validation/test split;
- temporal holdout strategy;
- spatial holdout where relevant;
- baseline;
- evaluation metric;
- uncertainty reporting;
- failure analysis;
- reproducibility;
- data/version lineage.

Avoid leakage from future observations into training or evaluation.

For route recommendations, define measurable outcome metrics such as appropriate combinations of:

- hazard exposure reduction;
- safety-margin preservation;
- ETA impact;
- fuel/energy impact;
- constraint violations avoided;
- false-negative hazard detection;
- false-positive rerouting burden.


## 48A.12 FALSE POSITIVE VS FALSE NEGATIVE MUST BE RESEARCHED

For important alerts and route-health logic, distinguish:

### False negative
The system fails to identify a meaningful hazard or deterioration.

### False positive
The system triggers a warning or route change that was not operationally necessary.

Research the operational consequences of both.

Do not optimize ordinary classification accuracy alone where operational consequences are asymmetric.

Alert thresholds should therefore be justified and documented.


## 48A.17 ANTARCTIC ENVIRONMENTAL AND REGULATORY CONSTRAINTS MUST BE RESEARCHED

Before implementing no-go or restricted-area logic, research and verify authoritative Antarctic requirements and datasets concerning:

- Antarctic Treaty System;
- Protocol on Environmental Protection to the Antarctic Treaty;
- Antarctic Specially Protected Areas (ASPA);
- Antarctic Specially Managed Areas (ASMA);
- relevant Management Plans and permit requirements;
- Historic Sites and Monuments where relevant;
- marine protected areas and CCAMLR-related measures where relevant;
- environmental impact assessment requirements;
- marine pollution and waste requirements relevant to the voyage;
- wildlife/ecological sensitivity where it can affect routing or mission planning.

Do not treat every protected area as an identical "no-sail" polygon. Determine whether the legal/management regime imposes a prohibition, permit requirement, operational condition, or other restriction.

Research current datasets and management plans before integrating them into routing.


## 48A.18 RESEARCH ANTARCTIC-SPECIFIC NAVIGATION CONDITIONS

Do not assume Arctic and Antarctic navigation are identical.

Research Antarctic-specific implications of:

- seasonal sea-ice behavior;
- first-year vs multi-year ice prevalence;
- pressure/compression;
- leads/openings;
- ridging;
- fast ice;
- marginal ice zone;
- iceberg concentration;
- iceberg uncertainty;
- darkness;
- fog;
- swell;
- high winds;
- freezing spray;
- low temperatures;
- remoteness;
- weak hydrographic coverage;
- communication limitations;
- SAR limitations;
- limited ports/refuge options.

Use Antarctic-specific evidence where available.


## 48A.19 BATHYMETRY / CHART QUALITY / UKC MUST BE TREATED AS UNCERTAIN

Research:

- ENC quality;
- survey confidence;
- source quality / CATZOC where applicable;
- chart compilation scale;
- bathymetric uncertainty;
- under-keel clearance;
- vessel squat where relevant;
- tide/water-level effects where relevant;
- S-102;
- S-104;
- S-129 Under Keel Clearance Management;
- other relevant chart-quality/UKC mechanisms.

A depth value should not be interpreted as equally reliable everywhere.

Do not infer safe passage solely from a single displayed depth number.


## 48A.20 RESCUE CONSEQUENCE MUST INFLUENCE ROUTE DECISION SUPPORT

Research the effect of:

- remoteness;
- SAR response time;
- availability of nearby vessels/icebreakers;
- refuge/shelter options;
- communications;
- weather windows;
- propulsion failure;
- machinery failure;
- abandonment;
- medical emergency.

A route with similar environmental hazard exposure may have materially different operational risk if contingency options are radically different.

Do not invent SAR availability. Use authoritative or explicitly simulated inputs.


## 48A.21 ICEBREAKER / ESCORT SUPPORT MUST BE A DISTINCT CAPABILITY

Where icebreakers are displayed or considered:

- distinguish available, nearby, reachable, and merely known vessels;
- distinguish actual icebreaker capability from ordinary vessel presence;
- investigate whether an escort/assistance relationship actually exists;
- model communication/availability assumptions;
- do not assume the nearest vessel can provide assistance.


## 48A.22 HUMAN FACTORS MUST BE BUILT INTO ALERTING

The bridge team operates under workload constraints.

Research and account for:

- alert fatigue;
- alarm flooding;
- automation bias;
- confirmation bias;
- cognitive overload;
- handover continuity;
- explainability;
- challengeability;
- visibility of uncertainty;
- preservation of established bridge concepts.

The system should make important changes easier to notice without forcing the user to inspect every layer continuously.


## 48A.23 ROUTE DECISION PROVENANCE SHOULD BE RECONSTRUCTABLE

For every material route recommendation, preserve:

BEFORE STATE
→ CHANGE
→ EVIDENCE
→ ASSUMPTIONS
→ CONSTRAINT
→ ALTERNATIVES
→ RECOMMENDATION
→ HUMAN APPROVAL
→ RESULT / LATER OBSERVATION

The system should be able to answer after the fact:

"Why did we change the route at this time?"

This should connect directly to the existing decision object and decision log.


## 48A.24 DATA AND MODEL TIME MUST BE SYNCHRONIZED

Research and implement explicit time handling for:

- observation timestamp;
- publication time;
- ingestion time;
- forecast initialization time;
- forecast valid time;
- route decision time;
- ship position time;
- model inference time;
- data expiration time.

Do not compare data as though they were simultaneous when they are not.


## 48A.25 CLIMATE NON-STATIONARITY MUST NOT BE HAND-WAVED

The existing requirement to recognize global warming/climate change should be preserved.

However:

- do not use "global warming" as a generic explanation for every unusual event;
- distinguish long-term climatological change from short-term weather/ice variability;
- research whether historical distributions remain representative;
- investigate dataset shift / non-stationarity in ML;
- consider recalibration/retraining triggers where appropriate.


## 48A.26 "WHAT DOES THIS MODEL KNOW, AND WHAT DOES IT NOT KNOW?"

Every predictive model should have a documented boundary:

- training geography;
- training seasons;
- environmental regimes;
- input assumptions;
- missing-input behavior;
- known failure modes;
- extrapolation behavior;
- uncertainty behavior.

If the model is asked to predict outside a validated domain, surface that rather than presenting a normal-looking prediction.


## 48A.27 PROFESSIONAL NAVIGATION STANDARDS MUST BE DISTINGUISHED FROM OPTIONAL ANALYTICS

Continue aligning with:

- ENC / ECDIS;
- IHO S-100 ecosystem;
- AIS;
- radar / ARPA;
- GNSS;
- gyro;
- echo sounder;
- weather/ocean products;
- GMDSS.

But clearly distinguish:

1. authoritative navigation information;
2. decision-support analytics;
3. model-derived predictions;
4. simulated/demo information.

Never make a model-derived visualization visually indistinguishable from authoritative navigational information.


## 48A.28 RESEARCH THE ACTUAL VESSEL / VOYAGE PROFILE BEFORE FINAL THRESHOLDS

Before selecting operational thresholds for a demo or future deployment, determine the intended vessel profile.

If the exact vessel is known, research:

- vessel name;
- flag;
- class society;
- IMO number where relevant;
- Polar Ship Certificate;
- Polar Ship Category;
- Polar Class / ice class;
- PWOM;
- operational ice limitations;
- propulsion;
- draft/load condition;
- historical Antarctic operating profile;
- voyage pattern;
- relevant charter/operator constraints.

If the exact vessel is not known, use a clearly labeled representative vessel profile and do not present it as the real operating vessel.


## 48A.30 SKEPTICAL-JUDGE TEST

For every major claim, the implementation/research documentation should be able to answer:

- Better than what?
- Using which data?
- What is the ground truth?
- What is the prediction horizon?
- What is the error?
- What happens when the model is wrong?
- What vessel assumptions are being made?
- Which constraints are hard?
- What happens when connectivity fails?
- What is real versus simulated?
- Why should a captain trust the recommendation?
- How can the captain challenge it?
- What evidence shows this works for Antarctica rather than merely working on generic maritime data?


## 48A.31 REQUIRED RESEARCH OUTPUT FROM CLAUDE BEFORE DEEP IMPLEMENTATION

Before committing to the final architecture/model choices, produce and retain a research matrix covering:

| Topic | What must be determined |
|---|---|
| PS-26059 | exact functional scope and judging-relevant core |
| Vessel capability | Category A/B/C, Polar Class/ice class, certificate, PWOM, temperature/operational limits |
| POLARIS | RIV/RIO, inputs, applicability, limitations, Antarctic relevance |
| Other ice-risk methods | AIRSS and other recognized methods; applicability |
| Sea ice | data variables, forecasts, uncertainty, resolution, latency |
| Icebergs | tracking sources, trajectory methods, uncertainty |
| Weather/ocean | route-time forecast fields and uncertainty |
| Bathymetry | ENC, S-102, CATZOC/QoBD, UKC, S-129 |
| Navigation | ECDIS/AIS/radar/GNSS/gyro/echo sounder/GMDSS integration |
| Antarctic restrictions | ATS/ASPA/ASMA/CCAMLR/environmental requirements |
| SAR | rescue/remoteness/icebreaker/contingency implications |
| Communications | bandwidth, latency, loss, synchronization |
| Human factors | alerts, workload, challengeability |
| ML validation | baselines, temporal holdout, metrics, uncertainty |
| Routing | constrained multi-objective formulation and robust routing |
| Historical data | incidents, route patterns, seasonal context |
| Competitive systems | existing capabilities, gaps, differentiation |
| Open source | reuse opportunities, licenses, maturity |

For each research topic, record:
- authoritative sources;
- conflicting sources if any;
- confidence;
- implementation implication;
- whether it is MVP, future scope, or research-only.


## 48A.32 FINAL REASONING PRINCIPLE

Keep this hierarchy throughout implementation:

REAL WORLD
→ OBSERVATIONS
→ DATA PROVENANCE
→ FORECASTS
→ UNCERTAINTY
→ VESSEL CAPABILITY
→ CONSTRAINTS / RISK
→ FUTURE ROUTE EXPOSURE
→ ALTERNATIVE CORRIDORS
→ ETA / FUEL / OPERATIONAL TRADEOFF
→ EXPLAINABLE DECISION
→ MASTER APPROVAL
→ EXECUTION
→ NEW OBSERVATION
→ VALIDATION / LEARNING LOOP

The system is not successful because it generates a clever line on a map.

It is successful when it can credibly explain:

**what the environment is doing, what it is expected to do when the vessel gets there, what this particular vessel can safely tolerate, how certain the system is, what routes remain feasible, what the trade-offs are, why the recommendation changed, and what evidence the Master can use to challenge or approve the decision.**

---
