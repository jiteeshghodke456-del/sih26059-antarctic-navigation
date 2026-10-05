# STAGE 02 — AI/ML + SYSTEM ARCHITECTURE (GATED)
## ENTRY GATE
Before changing architecture, inspect the repository and ask whether this stage has already been completed. Verify the Stage 01 research handoff and existing implementation. Do not rebuild completed work; audit and fill gaps only.

MISSION
Only after Stage 01 research is complete, design the changes required to the existing project architecture.

DO NOT blindly implement the research recommendations.
For every proposed change:
- cite the research evidence;
- show the current implementation;
- identify the gap;
- propose the smallest necessary change;
- preserve working behavior;
- identify migration risk;
- define tests.

AIML ARCHITECTURE
Design a defensible architecture for:
- sea-ice forecasting;
- iceberg trajectory prediction;
- weather/ocean integration;
- multimodal/EO model use where justified;
- route exposure/risk calculation;
- vessel-aware constraint evaluation;
- uncertainty propagation;
- model evaluation and baselines;
- MLflow tracking.

For each ML model, define:
DATA → PREPROCESSING → MODEL → OUTPUT → UNCERTAINTY → VALIDATION → CONSUMER.

Do not select models by popularity. Use the Stage 01 model decision matrix.

Do not assume a foundation model is better than a simple baseline.

VESSEL/RISK ARCHITECTURE
Model vessel parameters as domain data and distinguish:
- vessel capability;
- physical hazard;
- route exposure;
- decision uncertainty.

POLARIS must be integrated only according to the Stage 01 applicability research. It is not automatically the route optimizer or an Antarctic safety oracle.

ROUTING ARCHITECTURE
Treat routing as spatiotemporal and vessel-aware, with hard constraints separated from objectives/preferences.

Do not invent arbitrary weights without methodological justification.

OUTPUTS
Produce:
1. architecture delta;
2. AIML architecture;
3. data/model flow;
4. domain-model changes;
5. API/interface changes;
6. migration plan;
7. test plan;
8. rationale linked to research;
9. draw.io-ready architecture.

STOP after the architecture/change plan and tests are defined. Do not perform unrelated UI work.

# 33. ARCHITECTURE-FIRST DEVELOPMENT ORDER

Before coding, the project MUST define:

1. Domain entities.
2. Ingestion interfaces.
3. Time/coordinate conventions.
4. Data provenance model.
5. Route representation.
6. Hazard representation.
7. Uncertainty model.
8. Decision lifecycle.
9. Offline synchronization.
10. UI state model.

The immediate architectural deliverables requested are:

- a clear system architecture suitable for draw.io;
- the Markdown content needed for the presentation/PPT mentioned in this prompt;
- data-source architecture and rationale;
- then the prototype.

The architecture should make explicit the ship/edge side, shore/land side, ingestion, storage, model/forecast processing, route engine, decision engine, synchronization layer, UI, alerting, communications, and future integrations.

Do not redesign the domain later merely because the prototype was built quickly.

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


# 46. IMMEDIATE EXECUTION ORDER FOR CLAUDE CODE

Take over the project in this order:

1. **Inspect the repository and existing environment before changing anything.**
2. **Understand the entire product/operational requirements in this document and the source appendix.**
3. **Research the current technical and data landscape, including Indian and foreign sources, open-source navigation/map options, competitor systems, Antarctic policies, and relevant standards.**
4. **Create the domain model and system architecture first.**
5. **Create a clear draw.io-compatible architecture representation and the Markdown/presentation material requested.**
6. **Define ship-side vs shore-side execution and data responsibilities.**
7. **Define ingestion, provenance, freshness, synchronization, bandwidth, and offline behavior.**
8. **Define route, hazard, decision, uncertainty, mission, and versioning models.**
9. **Refine the professional-sailor UI around the existing bridge mental model.**
10. **Build the smallest real-data MVP.**
11. **Integrate genuine data sources where available.**
12. **Use historical replay or explicit simulation only where necessary for unavailable prototype/future capabilities.**
13. **Demonstrate route degradation → explanation → alternatives → what-if → Master approval → versioned route → continued monitoring.**
14. **Implement/prepare ML experimentation and tracking through MLflow using the supplied environment requirements.**
15. **Document what is real, simulated, historical replay, unavailable, or future.**
16. **Do not overwrite existing configuration or make irreversible architectural changes without evidence.**

---


# 47. NON-NEGOTIABLE SAFETY / TRUTH RULES

1. The Master remains in control.
2. The software does not autonomously execute navigational decisions.
3. Hard safety constraints override optimization.
4. Uncertainty is visible.
5. Source age is visible.
6. Data disagreement is visible.
7. Absence of an iceberg record does not equal absence of an iceberg.
8. Public AIS is not the ship’s primary navigation record.
9. Published itineraries are not automatically the actual bridge track.
10. Simulated data are never presented as live.
11. Route versions and decision history are preserved.
12. The system must degrade safely during communications loss.
13. The application must not silently invent authoritative navigational information.


---


## 48A.1 THINK FROM THE DECISION BACKWARDS

For every feature, model, data source, map layer, alert, or UI element, first determine:

1. What operational decision does this information change?
2. What evidence changes that decision?
3. What happens if the information is late, wrong, incomplete, or conflicting?
4. What vessel-specific condition changes the interpretation?
5. What uncertainty must be visible?
6. What is the operational consequence of a false negative?
7. What is the operational consequence of a false positive?

Do not add functionality merely because it is technically impressive.

The product should answer the captain's actual decision questions rather than merely display environmental variables.


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


## 48A.5 SEPARATE DIFFERENT KINDS OF RISK

The system should distinguish at least:

### Physical hazard
What exists in the environment?

Examples:
- sea ice;
- pressure ice;
- ridging;
- ice edge;
- fast ice;
- pack ice;
- marginal ice zone;
- iceberg;
- growler / bergy-bit where detectable;
- storm;
- waves/swell;
- fog;
- darkness;
- poor visibility;
- shoal / shallow water;
- traffic.

### Vessel capability
Can this particular ship tolerate, maneuver through, avoid, or safely operate around it?

### Route exposure
How much and for how long will the selected route encounter the hazard?

### Decision uncertainty
How uncertain are the observations, forecasts, vessel assumptions, or model outputs?

Never collapse these four concepts into a single unexplained risk number.


## 48A.6 THINK IN 4D: LATITUDE × LONGITUDE × TIME × VESSEL STATE

The environment is dynamic.

Do not evaluate only:

CURRENT SHIP POSITION × CURRENT ENVIRONMENT

Instead evaluate:

FUTURE SHIP POSITION(t)
against
FORECAST ENVIRONMENT(t)

across a defined horizon.

For each important hazard, investigate:

- forecast/observation time;
- route arrival time at the affected location;
- predicted hazard state at that time;
- uncertainty envelope;
- expected exposure duration;
- vessel capability at that time;
- consequence of the hazard reaching the route.

The route should therefore be treated as a spatiotemporal corridor rather than a static polyline.


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


## 48A.8 ROUTE OPTIMIZATION MUST BE CONSTRAINED MULTI-OBJECTIVE OPTIMIZATION

Do not define the problem simply as shortest path.

Consider, as appropriate:

- hard safety constraints;
- vessel operating envelope;
- ice exposure;
- iceberg exposure;
- weather/sea-state exposure;
- bathymetric/UKC margin;
- navigational constraints;
- uncertainty;
- ETA;
- fuel/energy;
- mission constraints;
- communication availability;
- contingency availability.

First classify each variable as:

- HARD CONSTRAINT;
- SAFETY/OPERATIONAL CONSTRAINT;
- SOFT OBJECTIVE;
- PREFERENCE.

Do not invent arbitrary weights such as "safety 40%, fuel 20%" without evidence.

When multiple alternatives are feasible, show the trade-off instead of pretending there is one mathematically perfect route.


## 48A.9 ROBUST ROUTING AND UNCERTAINTY PROPAGATION

The recommended route should not depend solely on the mean prediction.

Research and, where feasible, model:

- position uncertainty;
- iceberg trajectory uncertainty;
- sea-ice forecast uncertainty;
- weather uncertainty;
- bathymetric uncertainty;
- vessel-state uncertainty;
- sensor uncertainty;
- source disagreement;
- communication latency.

Prefer robust or uncertainty-aware route assessment when appropriate.

For an iceberg, consider comparing the future route not only against the predicted center point but against an appropriate uncertainty envelope.

For sea ice, investigate how forecast uncertainty changes expected route exposure.

A route can be preferred because it remains acceptable across a plausible range of future conditions, not simply because the mean forecast looks favorable.


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


## 48A.13 ROUTE HEALTH MUST BE A STATE, NOT A DECORATIVE COLOR

Retain the existing Valid / Degraded / Invalid concept and extend it so the state is evidence-based.

For example:

VALID
→ DEGRADED
→ CRITICAL
→ INVALID

where appropriate.

Every status change should identify:

- what changed;
- when;
- where;
- which assumption was invalidated;
- which constraint became binding;
- evidence;
- age;
- uncertainty;
- route consequence;
- alternatives;
- next review/trigger condition.

A route should become unhealthy because a meaningful operational assumption changed, not merely because new data arrived.


## 48A.14 BUILD A MINIMUM TRUSTWORTHY SYSTEM

Research and explicitly define the smallest subset that must remain useful if all non-essential services fail.

At minimum investigate a fail-safe local mode containing, as appropriate:

- own-ship position;
- last trusted approved route;
- essential local chart/navigation representation;
- last trusted environmental information;
- vessel limits;
- basic hard safety constraints;
- local hazard state;
- decision/history context;
- clear stale-data status.

Define functionality levels such as:

- FULL CONNECTIVITY;
- DEGRADED CONNECTIVITY;
- LOW-BANDWIDTH;
- STALE-DATA;
- LOCAL-ONLY;
- SENSOR/LOCAL-INPUT ONLY.

For each mode, document:

- available data;
- unavailable data;
- confidence degradation;
- disabled features;
- retained safety functions;
- synchronization behavior.


## 48A.15 DESIGN A DATA FRESHNESS / TRUST CONTRACT

Every layer should have a freshness policy.

For each source determine:

- expected update interval;
- typical latency;
- maximum acceptable age for the intended use;
- what happens after that age;
- whether the data become informational only;
- whether the route recommendation must be invalidated/reviewed.

Do not imply that "latest available" means "live."

The system must distinguish at minimum:

LIVE DATA
HISTORICAL REPLAY
SIMULATED INPUT
STALE DATA
UNAVAILABLE


## 48A.16 SENSOR AND SOURCE CONFLICT MUST BE FIRST-CLASS

When sources disagree:

- do not silently average incompatible observations;
- retain provenance;
- identify which sources disagree;
- estimate the possible reason;
- surface confidence degradation;
- determine whether a safety decision should be blocked or escalated.

Examples include:

- GNSS vs other position sources;
- satellite ice analysis vs onboard observation;
- forecast vs observed weather;
- public AIS vs onboard navigation record;
- different sea-ice products;
- different iceberg datasets.


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


## 48A.29 PREDICTION SHOULD LEAD TO AN OPERATIONAL CONSEQUENCE

Every predictive output should map to an operational interpretation.

Examples:

SEA-ICE FORECAST
→ expected concentration/stage/exposure ahead
→ route consequence
→ alternative corridor

ICEBERG TRAJECTORY
→ predicted separation/intersection probability
→ hazard level
→ maneuver/route-review trigger

WEATHER FORECAST
→ expected route-condition deterioration
→ ETA / operational consequence
→ route-health change

VESSEL STATE
→ reduced capability
→ binding constraint
→ route reassessment

A prediction that has no operational consequence should not be prioritized over a prediction that can change the decision.


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


# DECISION-FIRST THINKING

For every major feature, model:

1. What decision is the captain trying to make?
2. What information affects that decision?
3. What prediction or calculation is required?
4. What uncertainty exists?
5. What constraint could invalidate the result?
6. What alternative actions exist?
7. How will the captain understand why the recommendation changed?
8. How will the result be validated?

The application must reason from:
ENVIRONMENT + FORECAST + VESSEL + MISSION + UNCERTAINTY
→ RISK / ROUTE EXPOSURE
→ CANDIDATE ROUTES
→ ETA / FUEL / SAFETY TRADEOFF
→ EXPLAINABLE DECISION
→ HUMAN APPROVAL.


# VESSEL-AWARE REASONING

Never treat the ship as merely a point moving over a map.

A route recommendation must be evaluated against the specific vessel profile and its operational envelope.

Research and account for, where applicable:

- Polar Ship Category;
- Polar Class / applicable ice class;
- Polar Ship Certificate;
- PWOM;
- Polar Service Temperature / applicable low-temperature limitations;
- vessel-specific operational ice limits;
- ice-handling / maneuvering capability;
- propulsion characteristics and limitations;
- stopping / turning / maneuvering behaviour;
- draft;
- displacement / loading condition;
- trim;
- stability;
- under-keel clearance requirements;
- fuel / endurance;
- machinery condition;
- steering condition;
- crew competence / polar training;
- mission-specific operational limits.

Do not invent vessel-specific values.

Where actual vessel data are unavailable, explicitly identify the value as an assumption, placeholder, historical value, or simulation and explain what authoritative information would be required in a real deployment.

The same environmental conditions must be capable of producing different route assessments for different vessel capabilities.


# FOUR DISTINCT RISK CONCEPTS

Do not collapse all risk into one generic number.

Keep these concepts distinguishable:

1. PHYSICAL HAZARD
   What environmental or navigational hazard exists?

2. VESSEL CAPABILITY
   Can this particular vessel safely operate under those conditions?

3. ROUTE EXPOSURE
   How much of that hazard is encountered along the candidate route over time?

4. DECISION UNCERTAINTY
   How uncertain are the observations, forecasts, predictions, assumptions, and resulting recommendation?

The GUI and decision engine should preserve these distinctions.


# THINK IN 4D, NOT JUST ON A MAP

Do not evaluate routes only against the present environment.

Treat the problem as:

latitude + longitude + time + vessel state.

For every relevant route segment, consider the environmental state expected when the vessel is actually there.

Where appropriate:

own-ship trajectory
→ future ship position over time

environmental forecast
→ future sea-ice / weather / ocean state over time

iceberg model
→ future iceberg trajectory / uncertainty envelope

Then evaluate:

future ship position × future hazard state × vessel capability × uncertainty.

A route that is safe now but likely to become unsafe before the vessel reaches that location must be recognized as a deteriorating route.


# FORECAST HORIZON DISCIPLINE

Do not use the word “forecast” without defining the relevant horizon.

Research and explicitly distinguish the useful prediction horizons for:

- sea ice;
- iceberg trajectories;
- weather;
- ocean conditions.

Determine where each prediction remains operationally useful and where uncertainty becomes too large.

Expose forecast horizon and forecast age in the decision system.


# ROUTE OPTIMIZATION DISCIPLINE

Do not define the problem as “find the shortest route.”

Treat route planning as constrained, multi-objective decision support involving, where justified:

- safety;
- vessel capability;
- sea-ice exposure;
- iceberg exposure;
- weather / sea-state exposure;
- bathymetric / UKC constraints;
- ETA;
- fuel / energy;
- uncertainty;
- mission requirements;
- operational feasibility.

Before assigning numerical weights, determine through research which factors are:

- hard safety constraints;
- operational constraints;
- optimization objectives;
- preferences.

Hard safety and vessel-capability constraints MUST override efficiency optimization.

Do not invent arbitrary percentages such as “safety = 40%, fuel = 20%, ETA = 40%” without a defensible methodological basis.


# POLARIS / POLAR RISK METHODS

Research POLARIS and determine how it should be used.

Investigate:

- vessel capability / ice class inputs;
- Risk Index Values (RIV);
- Risk Index Outcome (RIO);
- how POLARIS interacts with ice conditions;
- operational interpretation;
- limitations;
- applicability to Antarctic rather than Arctic conditions;
- Antarctic validation evidence;
- whether POLARIS should be a hard constraint, advisory risk indicator, comparative research layer, or another role.

Do NOT blindly treat POLARIS as an authoritative Antarctic safety oracle.

If incorporated into the GUI, display its inputs, result, applicability, source, timestamp, and operational interpretation rather than presenting an unexplained generic “risk score”.

Research other relevant polar risk-assessment approaches such as AIRSS and comparable operational methodologies where applicable.

Determine what each method contributes that the rest of the system does not.


# BASELINE-FIRST SCIENTIFIC VALIDATION

Every important predictive component must answer:

“Better than what?”

Before claiming an AI model is useful, establish appropriate baselines.

Examples to investigate where applicable:

- persistence;
- climatology;
- simple physics-based prediction;
- conventional trajectory models;
- existing operational products;
- simpler machine-learning models.

The system must not select a sophisticated model merely because it is more complex.

For every core predictive component, define:

- training data;
- validation data;
- test data;
- temporal separation;
- spatial considerations;
- baseline;
- evaluation metrics;
- uncertainty representation;
- failure modes;
- domain of validity.

Avoid temporal leakage.

Use historical holdout periods where appropriate.


# PREDICTION MUST BE COMPARED WITH OBSERVATION

For sea-ice forecasting:

prediction at time T
→ compare against observed later ice state.

For iceberg trajectories:

predicted trajectory at time T
→ compare against later observed iceberg position.

For routing:

recommended route at time T
→ evaluate against the later environmental state and appropriate baseline routes.

The project must be capable of demonstrating not just that predictions exist, but whether they were useful and how accurate they were.


# UNCERTAINTY-AWARE ROUTING

Do not provide false precision.

When predictions have uncertainty, represent it.

For icebergs, where scientifically justified, consider trajectory uncertainty envelopes rather than displaying a single deterministic point.

For sea ice, weather, and other environmental forecasts, retain uncertainty/quality information.

A route should be evaluated not only against the predicted best estimate but against a plausible range of future conditions where appropriate.

The system should be able to distinguish:

“predicted safe”

from

“robustly safe under plausible forecast error”.

Research appropriate methods for robust / risk-aware routing.


# FALSE POSITIVE / FALSE NEGATIVE THINKING

For safety-relevant detection and alerting, explicitly consider:

- false negatives: hazard exists but is not detected;
- false positives: warning occurs when hazard is not operationally significant.

Do not optimize generic model accuracy alone.

Research which error types are operationally more costly for each component and design alerts and thresholds accordingly.


# ROUTE HEALTH MUST BE DYNAMIC

Do not reduce route health to a decorative green/red indicator.

A route should be able to move through states such as:

VALID
→ DEGRADED
→ CRITICAL
→ INVALID

Each state must have evidence.

Route health must explain:

- what changed;
- which assumption changed;
- which constraint is binding;
- what evidence caused the change;
- how fresh the evidence is;
- what the consequence is;
- what alternatives exist;
- what trigger would change the decision again.


# MINIMUM TRUSTWORTHY SYSTEM

Design the system so that, if higher-level services fail, the minimum trusted operational subset remains available.

Research and explicitly define what must continue working if:

- internet is lost;
- shore communication is lost;
- cloud services are unavailable;
- satellite data are stale;
- some sensors fail;
- sources disagree;
- model inference fails.

Define the minimum trustworthy onboard state, for example as appropriate:

- own-ship state;
- last trusted route;
- local chart / essential map data;
- vessel limits;
- last trusted environmental information;
- basic safety/constraint logic.

Do not assume the entire system is always online.


# DEGRADATION STATES

Do not model connectivity simply as online/offline.

Research an explicit degradation model such as:

FULL CONNECTIVITY
→ DEGRADED CONNECTIVITY
→ LOW BANDWIDTH
→ STALE ENVIRONMENTAL DATA
→ LOCAL-ONLY
→ SENSOR-ONLY / MINIMUM TRUSTED MODE

For each state determine:

- available data;
- unavailable data;
- update frequency;
- uncertainty implications;
- available features;
- disabled features;
- required warnings;
- required human verification.


# STALE-DATA CONTRACT

Every important dynamic dataset should have an explicit understanding of:

- observation time;
- forecast initialization time;
- received time;
- expected next update;
- current age;
- freshness state;
- quality;
- consequences of becoming stale.

The system must know when a dataset has become too old for a particular decision.

Do not assume that “data exists” means “data is current enough to use”.


# SENSOR / SOURCE DISAGREEMENT

Never automatically average incompatible observations.

When sources disagree:

1. identify the disagreement;
2. preserve source provenance;
3. assess source quality;
4. determine whether one source should be preferred;
5. surface the conflict when it materially affects the decision;
6. increase uncertainty where appropriate.


# HUMAN-CHALLENGEABLE AI

The captain/OOW must be able to challenge the system.

Every recommendation should make it possible to inspect:

- evidence;
- assumptions;
- constraints;
- vessel factors;
- forecast horizon;
- data age;
- uncertainty;
- alternatives;
- route consequences;
- trigger conditions.

The AI must not rely on “trust me” outputs.


# DECISION PROVENANCE

For every major route decision preserve:

BEFORE STATE
→ WHAT CHANGED
→ EVIDENCE
→ INTERPRETATION
→ ALTERNATIVES
→ RECOMMENDATION
→ HUMAN APPROVAL
→ ROUTE VERSION
→ LATER OUTCOME.

This should be reconstructable after the voyage or during a later review.


# FINAL QUESTION BEFORE CODING

Before implementing any major component, explicitly ask internally:

“What is the PS-26059 contribution of this component?”

If the answer is weak, classify it as supporting infrastructure, secondary functionality, or future scope and do not allow it to consume disproportionate implementation time.

The goal is not to build the largest Antarctic software system.

The goal is to build the most scientifically defensible, operationally credible, vessel-aware, uncertainty-aware, demonstrably useful PS-26059 solution possible, while keeping the larger product vision architecturally alive.