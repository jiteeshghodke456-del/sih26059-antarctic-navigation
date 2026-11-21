# STAGE 03 — FRONTEND UI + WORKFLOW (GATED)
## ENTRY GATE
Before changing the UI, inspect the repository and ask whether this stage has already been completed. Verify the current UI/workflow against the requirements and prior architecture. Use the available frontend-design skill/workflow before redesigning UI. Preserve operational simplicity and sailor mental models.

MISSION
Refine/build the UI and workflow using the verified requirements and architecture. Do not change scientific/business logic unless necessary to expose already-verified outputs.

UI PRINCIPLES
- Professional bridge decision-support display.
- Simple/minimal/accurate.
- Preserve sailor habits and concepts.
- No ultra-futuristic “vibe-coded” UI.
- Data density must be understandable without hiding information.
- 2D and 3D only where useful.
- Layers must coexist without obscuring navigation.
- The captain should immediately understand: where am I, where should I be, what is ahead, is the route valid, what are the safest alternatives?

GUI RISK PRESENTATION
Where Stage 01 research validates POLARIS usage, show it as a contextual risk-assessment component with inputs/result/applicability/source/time and not an unexplained risk number.
Keep physical hazard, vessel capability, route exposure, and uncertainty distinguishable.

UI STATE
Route health is a state such as VALID → DEGRADED → CRITICAL → INVALID, with evidence and reason.

Every alert must preserve the existing P1/P2/P3 philosophy and show the required context.

Do not add decorative widgets that do not support an operational decision.

STOP after the UI/workflow is implemented and tested against the existing demo workflow.

# 2. PRIMARY UX / UI DIRECTION

## 2.1 UX references

Use these as primary UX references:

1. Polarstern MapViewer
2. R/V Laura Bassi
3. Actual Nuyina voyage-track visualization

Also use IcySea as inspiration for iceberg movement visualization, while not cloning it.

Investigate OpenCPN: https://opencpn.org/

OpenCPN is an open-source navigation platform for navigation at sea. Determine whether its GUI, map rendering approach, route display methods, or related open-source implementation patterns can be used as inspiration or reused where legally/technically appropriate for this Antarctic application.

The desired interface is approximately “like IcySea” in broad spirit, but **not exactly IcySea**. The references are inspiration, not a mandate to copy them.

## 2.2 UI philosophy

The UI MUST:

- be simple;
- be professional-grade;
- use very accurate maps and the kinds of data sailors actually need;
- be modern enough to feel clean without becoming futuristic for the sake of appearance;
- preserve sailor learning curves and established bridge habits;
- avoid a “vibe-coded ultra-futuristic” aesthetic;
- avoid unnecessary changes to the interfaces captains already use for static sea data, ice charts, and related information;
- keep maps clean, minimal, informative, and highly accurate;
- make the large quantity of data understandable through processing, prioritization, visualization, and explanation;
- put the sea-ice map and other environmental layers below/around the dashboard appropriately;
- support 2D and live/interactive 3D visualization where useful;
- allow navigation, sea-ice forecasting, iceberg path prediction, and other relevant layers to coexist without obscuring the professional navigation picture.

You may refer to `/userpsychology` skill when useful.

The primary design constraint is **simplicity without loss of operational information**.

---


# 4. END-TO-END USER WORKFLOW

The application workflow MUST support:

CONNECT PENDRIVE TO LAPTOP
↓
APPLICATION START
↓
CAPTAIN AUTHENTICATION
↓
COMMAND CENTER
↓
SELECT / CREATE VOYAGE
↓
MISSION DEFINITION
↓
ROUTE CREATION / IMPORT
↓
WAYPOINT + ETA DEFINITION
↓
ROUTE REVIEW
↓
FORECAST-BASED ROUTE ASSESSMENT
↓
ROUTE HEALTH
↓
CAPTAIN APPROVES ROUTE
↓
ACTIVE NAVIGATION
↓
LIVE / RECENT / FORECAST DATA
↓
CONTINUOUS SITUATIONAL AWARENESS
↓
HAZARD / ENVIRONMENT CHANGES
↓
ROUTE IMPACT DETECTION
↓
HEADS-UP
↓
CAPTAIN OPENS DECISION WORKSPACE
↓
UPDATED INFORMATION
- Ship state
- Navigation
- Ice
- Icebergs
- Weather
- Ocean
- Forecast
- Mission
- Route health
- Data freshness
↓
ROUTE REASSESSMENT
↓
KEEP PLAN / EDIT / ALTERNATIVE
↓
WHAT-IF EDITING
↓
LIVE IMPACT PREVIEW
↓
CAPTAIN APPROVES
↓
NEW ROUTE VERSION
↓
NAVIGATION
↓
MONITOR AGAIN
↺

Do not silently replace an approved plan.

When a new route is proposed, preserve the old route, preserve its history, show why the route changed, and require the appropriate human approval.

---


# 5. MAP AND LAYER STACK

The main map should support, as applicable:

- official chart / base map;
- planned route;
- actual historical track / breadcrumb;
- own-ship symbol with current motion information;
- route corridor / cross-track limits;
- depth / safety contour / under-keel margin;
- sea-ice concentration;
- sea-ice type / stage of development;
- fast ice;
- iceberg objects;
- predicted iceberg trajectories / roadmap;
- weather;
- ocean / currents;
- traffic / AIS;
- radar-related information where integration is available;
- navigational warnings;
- hazard zones / no-go areas;
- optional forecast trajectories;
- alternative route corridors;
- support/emergency layer showing available icebreakers and emergency responders and their routes when such data are available.

The iceberg feature should show predicted movement using simple, clean, minimal, informative vector arrows similar in conceptual usability to IcySea.

The system should check conditions **further down the route**, not just at the current ship position. A blizzard can hit the ship later; southern winds can contribute to changing/freezing ice conditions; icebergs and sea ice can move into or away from the future route.

The application is intended to let the captain “see the future” as much as scientifically justified by forecast/trajectory data, not just inspect present conditions.

---


# 32. UI CONTENT STRUCTURE

Primary map:

- official chart + planned route + actual track + ice + iceberg + danger areas.

Own-ship card:

- position;
- COG/SOG;
- heading;
- next waypoint;
- ETA;
- XTE;
- current operational state.

Route health:

- Valid / Degraded / Invalid;
- top three reasons.

Ice panel:

- concentration;
- type;
- trend;
- source timestamp;
- uncertainty.

Weather panel:

- current conditions in route corridor;
- forecast conditions in route corridor;
- not generic station weather.

Hazard timeline:

- events likely to affect the route over the next 6/12/24/48 hours.

Alternative routes:

- A/B/C corridors;
- safety margin;
- ETA delta;
- hazard exposure;
- rationale.

Decision log:

- what changed;
- who approved;
- when;
- why.

Data freshness:

- per-layer age;
- health status.

Offline state:

- cached data;
- unavailable data.

The screen should immediately answer:

1. Where am I?
2. Where was I supposed to be?
3. What is in front of me?
4. Is the approved route still valid?
5. What are my safest alternatives if it is not?

---


# 38. SAILOR-EMPATHY WATCH MODEL

A representative bridge watch should work approximately as follows:

1. At watch handover, the OOW reads the current passage plan, next waypoints, ship position, weather/ice notes, standing orders, and recent changes.
2. The OOW checks whether the ship remains within the planned cross-track corridor and whether the next leg remains safe.
3. The ice layer is examined for observation age, concentration/type, and trend. Radar and visual lookout are independent evidence.
4. The OOW checks for new iceberg or traffic information and compares it with the future own-ship path.
5. The weather forecast is checked over the route corridor and decision horizon.
6. If assumptions remain valid, continue normal monitoring.
7. If a key assumption is invalidated, escalate according to vessel procedures and let the Master decide whether to amend the route.
8. Evaluate candidate alternatives using current evidence and vessel constraints.
9. Record the revised decision; keep the original plan visible as history.

Preserve the chain of decisions so a captain can reconstruct not only where the ship went but why the route changed at a particular time.

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


## 48A.2 PS-26059 CORE MUST REMAIN THE CENTER OF GRAVITY

The implementation must preserve a clear hierarchy:

### PS-26059 CORE — FIRST PRIORITY

- Antarctic sea-ice forecasting / concentration forecasting;
- iceberg trajectory prediction;
- identification/generation of safe and fuel-efficient navigation routes;
- integration of satellite, oceanographic and meteorological information;
- visualization of forecast and route consequences;
- scientific validation of predictions and routing decisions.

### OPERATIONAL DECISION-SUPPORT ENHANCEMENTS — SECOND PRIORITY

- vessel capability / polar operating envelope;
- POLARIS or other researched ice-risk methods where applicable;
- weather-over-route assessment;
- route health;
- uncertainty;
- data provenance/freshness;
- route-assumption violation detection;
- alternative corridors;
- decision explanation;
- offline/low-bandwidth resilience;
- historical replay and incident context.

### FUTURE PRODUCT CAPABILITIES — THIRD PRIORITY

- emergency coordination;
- station communication;
- scientific mission support;
- local LLM;
- Baymax Mode;
- advanced onboard sensor integrations;
- broader expedition/fleet-management functionality;
- commercial/startup platform extensions.

Do not allow Tier 2 or Tier 3 functionality to consume the engineering effort required to prove the Tier 1 PS-26059 capability.


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
