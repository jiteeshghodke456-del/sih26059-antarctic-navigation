# STAGE 06 — RECREATE THE ISIH / SIH DEMO — FINAL EXECUTION STAGE
## ENTRY RULE
This is the only stage that does NOT ask whether it has already been completed. ALWAYS recreate the SIH demo from the verified repository state and all completed prior-stage handoffs.

MISSION
Build the current ISIH demonstration from the verified repository state and Stage 01 research. Preserve everything already working unless evidence requires a targeted fix.

CORE PRIORITY
The demonstrable center of the product is:
REAL DATA → SEA-ICE / ICEBERG / WEATHER PROCESSING → FORECAST/PREDICTION → VESSEL-AWARE CONSTRAINTS → RISK/EXPOSURE → 2–3 ROUTES → SAFETY/ETA/FUEL-ENERGY TRADEOFF → EXPLAINATION → HUMAN APPROVAL → ROUTE VERSION → MONITORING.

BUILD RULES
- Inspect first.
- Reuse current architecture and code where it works.
- Do not rebuild working components for aesthetic reasons.
- Do not add fake live data.
- Use real data wherever the capability exists.
- Use HISTORICAL REPLAY or SIMULATED INPUT only where necessary and label it.
- Keep PS-26059 core ahead of secondary/future features.
- Future-scope features requested for the demo may be simulated, but must be technically coherent and explicitly separated from real data.

DEMO MUST SHOW
1. Planned Cape Town → station route.
2. Own ship moving on route.
3. Sea-ice / iceberg / weather update.
4. A realistic route degradation event.
5. Exactly which assumption failed.
6. 2–3 alternative corridors.
7. Safety margin + ETA + operational impact.
8. Master approval.
9. Decision log.
10. Continued monitoring/reassessment.

Vessel-aware behavior must be TESTED, not inferred from cache keys or configuration. Use controlled tests with the same environment and different vessel capability to prove that the route/risk result can actually change.

The map/UI must retain established sailor concepts and not become a generic futuristic GIS interface.

STOP after the current demo works and the requested future-scope placeholders are integrated at the appropriate level. Do not begin post-research architecture replacement in this stage.

# 1. PRODUCT VISION

Build an Antarctic sea-ice, iceberg-trajectory, weather/ocean, navigation, and route-decision-support system that behaves like a professional bridge decision-support layer rather than a generic GIS dashboard or consumer mapping product.

The central value proposition is not “find the shortest route.” The system should help a captain see the future state of the voyage, understand large amounts of environmental and operational information, detect when assumptions behind the approved route become invalid, compare safer alternatives, and make a better human decision.

The core principle is:

> There is no perfect path. There is only a safer path relative to the available evidence, vessel capability, operational constraints, uncertainty, and consequences of delay.

There is no route with zero sea-ice concentration. The goal is not to pretend that sea ice can be eliminated; it is to identify comparatively safer corridors with quantified/visible uncertainty and route consequences.

The system must preserve the captain’s existing mental model and habits while adding powerful predictive, analytical, and decision-support capabilities.

---


# 3. CORE BRIDGE MENTAL MODEL

Do not think like a generic GIS developer. Think like a bridge team supporting the Master.

The system is:

- NOT a generic map application;
- NOT an autonomous captain;
- a decision-support layer for a multi-person bridge team.

The professional operational loop is:

1. APPRAISE the voyage
2. PLAN the passage
3. VALIDATE the route against chart, bathymetry, vessel limits, and hazards
4. EXECUTE the approved route
5. MONITOR the ship and environment continuously
6. DETECT when assumptions become invalid
7. RE-APPRAISE
8. GENERATE candidate alternatives
9. PRESENT an explainable recommendation
10. REQUIRE appropriate human approval for route changes

The route on an electronic chart is not the decision itself. It is the executable representation of a decision.

The planned route and actual ship track are separate objects.

The route is a sequence of waypoints and legs, not one freehand polyline.

The bridge mental model is:

> planned route + own ship state + radar/AIS + official ENC + bathymetry + sea ice + iceberg information + weather/ocean + navigational warnings + vessel capability + mission constraints + uncertainty.

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


# 6. PROFESSIONAL BRIDGE INFORMATION MODEL

Represent at minimum:

- own ship position;
- COG/SOG;
- heading;
- next waypoint;
- ETA;
- cross-track error / corridor;
- planned route;
- actual historical track;
- depth / safety contour / under-keel margin;
- traffic targets;
- sea-ice concentration;
- ice type / stage of development;
- floe characteristics when available;
- fast ice;
- iceberg objects;
- iceberg position age;
- wind;
- waves;
- visibility;
- surface current;
- navigational warnings;
- forecast time horizon;
- source timestamp;
- confidence / uncertainty;
- ship polar category / ice capability;
- draft and endurance constraints where available;
- station operational constraints;
- alternate routes;
- decision history.

The ship is not just a point on a map. The system must understand the ship’s certified/operational capability, propulsion state, draft, endurance, bridge systems, machinery limits, and mission constraints.

---


# 7. SEA-ICE MODEL — NEVER REDUCE TO BOOLEAN SAFE/UNSAFE

DO NOT REDUCE ICE TO A BOOLEAN “SAFE / UNSAFE” FLAG.

Sea ice must retain operational meaning through:

- total concentration;
- partial concentration;
- stage of development / age / thickness proxy;
- floe size;
- drift and trend;
- compression / opening where supported;
- fast ice versus drifting pack;
- observation age;
- source and uncertainty.

Use WMO-style sea-ice concepts and terminology.

A worsening field can be more dangerous than a slightly higher but stable field. Surface the underlying variables rather than hiding them behind a single label.

---


# 8. ICEBERG MODEL

Treat icebergs as moving discrete hazard objects with:

- ID;
- latitude;
- longitude;
- observed size;
- last update;
- source;
- uncertainty;
- movement estimate when available.

Do NOT infer “no iceberg” from “no tracked iceberg record.”

Distinguish between:

- a tracked iceberg object;
- the absence of a tracked object;
- the broader possibility of unobserved ice/objects.

Where scientifically supported, propagate trajectory uncertainty and compare the predicted future position against the future own-ship route, not just the ship’s current position.

---


# 9. WEATHER / OCEAN / FORECAST LOGIC

Forecast information should be evaluated along the actual route corridor and future decision horizon, not as generic station weather.

Relevant information includes:

- wind;
- pressure;
- visibility;
- precipitation;
- temperature;
- freezing spray where available;
- wave height and direction;
- swell;
- surface current;
- sea temperature where relevant;
- forecast time;
- forecast confidence;
- likely route deterioration;
- time-to-degradation.

The system should identify hazards ahead of the vessel and estimate whether current conditions or forecast trajectories are likely to invalidate route assumptions before the hazard physically reaches the ship.

---


# 10. ROUTE PLANNING MODEL

Route planning chooses a permissible corridor and sequence of waypoints. Navigation is the continuous act of determining where the ship is, where it is heading, what is around it, whether the plan remains valid, and what immediate control action is required.

This SIH system is primarily a decision-support and route-replanning system sitting beside the navigation loop.

A route record should support:

- Route ID;
- Waypoint ID;
- latitude / longitude;
- leg distance;
- initial / final course;
- planned speed;
- ETA;
- XTD / XTL;
- turning / wheel-over information;
- safety depth / contour;
- operational constraints;
- source timestamp;
- confidence;
- decision note;
- alternate route / fallback corridor;
- approval / revision information.

The route should be constructed from waypoints and legs with safety parameters and checks.

Route planning process:

1. Define voyage: departure, destination, and intermediate operational stops.
2. Perform complete appraisal: charts, publications, weather, ice, warnings, ship limitations, traffic, operational constraints.
3. Select appropriate chart areas / ENC cells and scales.
4. Create candidate waypoints and route legs around land, shoals, safety contours, and operational constraints.
5. Set planned speed / speed profile and calculate ETA.
6. Set cross-track limits / corridor width and turn parameters.
7. Run route safety checks and inspect the route at appropriate scales.
8. Review alternatives and contingency routes.
9. Document the plan and obtain Master/company approval.
10. During execution, compare actual ship state against the plan continuously.

---


# 11. DECISION OBJECT MODEL

Build the system around decision objects, not only map layers.

A first-class Decision object should contain:

- decision_id;
- time;
- vessel state;
- route version;
- environmental state;
- hazards considered;
- assumptions;
- constraints;
- alternatives;
- recommendation;
- confidence;
- trigger conditions;
- evidence;
- human approval state;
- revision history.

Conceptually:

Decision
├── vessel_state
├── intended_route
├── environmental_state
├── hazard_objects
├── operational_constraints
├── forecast_horizon
├── alternatives
├── assumptions
├── uncertainty
├── recommendation
├── trigger_conditions
└── approval_record

A recommendation MUST answer:

1. What changed?
2. Why does it matter?
3. Which constraint is now binding?
4. What alternatives exist?
5. What is the ETA/safety tradeoff?
6. What evidence supports the recommendation?
7. How fresh is that evidence?
8. What condition would make us change the decision again?

A black-box score such as “route score = 0.82” is less useful than an evidence-based explanation such as a preferred corridor because it reduces forecast ice pressure, preserves under-keel margin, and retains an alternate corridor if the MIZ advances.

---


# 12. DECISION GATES

Treat the captain’s problem as a sequence of decision gates:

### Capability gate
Can this ship legally and physically operate here under its Polar Ship Certificate / PWOM limits?

Evidence: ship certification, ice capability, draft, machinery, crew competence.

### Chart gate
Is the route geographically understood well enough?

Evidence: ENC, bathymetry, survey confidence, publications.

### Ice gate
Will expected ice exceed the ship’s operating limit or create unacceptable maneuvering risk?

Evidence: ice concentration/type, forecast, drift, visual/radar observations.

### Weather gate
Will wind/waves/visibility make the proposed corridor unsafe or the operation impossible?

Evidence: forecasts, observations, sea state.

### Traffic gate
Is there conflict with other vessels or operations?

Evidence: AIS, radar, communications.

### Logistics gate
Will the chosen track still meet cargo/people/operation timing?

Evidence: ETA, station window, helicopter/cargo plan.

### Communications gate
Can the ship obtain timely warnings and coordinate contingencies?

Evidence: GMDSS, satcom, station/shore contact.

### Contingency gate
If the route closes ahead, where do we go?

Evidence: alternate corridors, safe havens, endurance.

### Execution gate
Are current observations still consistent with the assumptions used to approve the route?

Evidence: live sensors + latest ice/weather.

---


# 13. ALERTING PHILOSOPHY

Do not create alert spam.

Priority:

- P1 = immediate safety relevance
- P2 = route degradation / approaching decision point
- P3 = informational change

Every alert should include:

- what changed;
- location;
- time;
- severity;
- source;
- confidence;
- route consequence;
- suggested action;
- expiry / next review time.

Examples of route-affecting events and responses:

- Ice concentration increases ahead → reduce speed, widen/shift corridor, hold, or choose alternate corridor.
- Ice edge moves toward planned track → trigger route-validity warning and present alternatives.
- New large iceberg appears → calculate separation against current and future track; flag route if required.
- Visibility deteriorates → increase conservatism and rely more heavily on radar/navigation procedures.
- Wind/sea state worsens → reassess speed, ETA, vessel motion, and transfer feasibility.
- Bathymetry concern discovered → reduce route confidence and re-plan around safer depth margin.
- Propulsion performance degrades → recalculate achievable speed and ice-handling capability; reassess route.
- Station operation slips → optimize revised arrival/departure window without sacrificing navigational safety.
- Communication outage → fall back to cached data and onboard procedures; reduce dependence on shore services.
- Sensor disagreement → surface the conflict; do not automatically average incompatible observations.

---


# 14. SENSOR / BRIDGE INTEGRATION

The architecture must be ready to ingest existing onboard sensors and bridge systems.

Relevant stack:

- GNSS / position source;
- gyrocompass;
- ECDIS / ENC;
- radar / ARPA;
- AIS;
- echo sounder;
- speed log;
- weather receiver / satcom feed;
- ice information service;
- GMDSS;
- ship internal systems including engine, steering, alarms, cargo, and stability.

Important failure implications:

- GNSS degradation requires alternative position fixing and cross-checks.
- Heading error can corrupt steering and ECDIS orientation.
- ECDIS can mislead if chart data, safety settings, or sensor inputs are wrong.
- Radar has blind spots/clutter/ice/weather limitations but remains important independent evidence.
- AIS depends on other vessels/radio conditions and does not represent every hazard.
- Echo sounder can provide depth trend but must not replace chart/bathymetry planning.
- Weather/satcom feeds have communication latency and model uncertainty.
- Ice services may be delayed, coarse, or uncertain and must be ground-truthed.
- Loss of GMDSS/communications reduces situational awareness and contingency options.
- A geographically safe route can still be operationally impossible because of ship internal state.

Architecture should allow a real ECDIS or bridge integration to be connected later without redesigning the domain model.

---


# 15. DATA PROVENANCE AND TRUST

Every important environmental object MUST expose:

- source;
- timestamp;
- observation/forecast time;
- latency / age;
- confidence or uncertainty;
- processing method if known.

Every environmental object shown to the bridge should answer:

- What is this?
- When was it observed?
- Who produced it?
- What sensor/model produced it?
- How accurate is it?
- When should the next update be expected?

A 12-hour-old satellite ice analysis and a 15-minute local observation MUST NOT be visually or numerically indistinguishable.

Architecture MUST support multiple sources and disagreement between sources.

When sources conflict, surface the conflict rather than averaging incompatible observations away.

---


# 16. MINIMUM DATA / LAYER STACK

### Base chart
ENC cell, geometry, feature class, depth/contour, publication/update status.

### Own vessel
Latitude, longitude, COG, SOG, heading, speed, draft, current route, timestamp.

### Route
Waypoints, legs, XTD/XTL, speed, ETA, safety parameters, alternate routes.

### Sea ice
Concentration, ice type/stage, floe characteristics where available, timestamp, source.

### Icebergs
ID, latitude/longitude, size, update time, source, uncertainty.

### Weather
Wind, pressure, visibility, precipitation, temperature, wave height/direction, forecast time.

### Ocean
Surface currents, sea temperature where relevant, forecast validity.

### Traffic
AIS target ID, location, course, speed, status, last update.

### Warnings
Navigational warnings, urgency, geographic polygon/point, start/end time.

### Ship limits
Ice class/capability, maximum operational ice, minimum depth/UKC, speed rules, machinery state.

### Mission
Destination, cargo/transfer priority, operational window, deadlines, station status.

### Confidence
Source, timestamp, age, quality/confidence, uncertainty.

---


# 18. VOYAGE PHASE MODEL

Represent the voyage as operational phases, not merely a GPS destination:

1. Port preparation — Cape Town loading, fuel, cargo sequencing, personnel, ship readiness.
2. Southern Ocean transit — long ocean leg with weather routing and increasing polar awareness.
3. Pre-ice / iceberg watch — enhanced ice information, iceberg updates, visual/radar vigilance.
4. Polar approach — more conservative speed/corridor, route validity checks, ice observations.
5. Station operating area — approach, mooring/anchoring/offload/transfer as operational plan allows.
6. Station turnaround — cargo, personnel, waste, mission-specific work, weather-window management.
7. Inter-station leg — new route appraisal; do not simply copy the previous route because environmental state changes.
8. Return leg — re-appraisal, departure timing, seasonal risk, ice-closure considerations.
9. Exit / Southern Ocean — gradual reversion toward conventional open-ocean voyage management.

---


# 19. MISSION STOPPAGE / SCIENTIFIC RESEARCH SUPPORT

The application should support mission stoppage.

If the crew wants to run scientific research at a place in the sea along the sailing route or a decided route, the system should understand:

- where the ship stopped;
- how long it stopped;
- whether the captain should remain stopped or continue;
- weather conditions during the stop;
- ice concentration;
- winds;
- ice pressure where available;
- iceberg movement into/out of the route;
- operational impact and future route condition.

The system should intelligently monitor whether a stoppage remains sensible under changing conditions.

---


# 22. AI / ML CAPABILITIES

High-value functions include:

- multimodal data fusion;
- route-assumption violation detection;
- ice trend prediction;
- iceberg trajectory estimation;
- route corridor generation;
- candidate route ranking;
- ETA impact estimation;
- uncertainty propagation;
- anomaly detection;
- explainable change summaries;
- contingency trigger generation;
- prediction of when a route is likely to become invalid before the hazard reaches the ship;
- summarization of changes since the previous bridge decision;
- candidate route generation rather than one opaque answer.

The AI should score alternatives using relevant considerations such as:

- safety margin;
- ETA impact;
- fuel/energy impact;
- operational feasibility.

The AI must explain recommendations using evidence, sources, timestamps, uncertainty, assumptions, and constraints.

The AI must not:

- claim to be the Master;
- autonomously execute route changes;
- silently overwrite the approved passage plan;
- treat satellite ice data as ground truth;
- infer absence of iceberg from absence of a tracked record;
- hide uncertainty behind a single safety score;
- ignore certified vessel limits;
- prioritize ETA over safety;
- make recommendations without showing evidence-window and data-age context;
- use AI confidence as legal/operational authority;
- pretend to replace Master/OOW judgement.

---


# 23. OFFLINE / LOW-BANDWIDTH / COMMUNICATION FAILURE

Antarctic operations may have intermittent or constrained communications.

The system MUST be edge-first and support:

- local cache;
- local map tiles;
- local data store;
- queued synchronization;
- delta updates;
- compressed environmental layers;
- source timestamps;
- stale-data indicators;
- graceful degradation.

If communications disappear, core map/route/safety functionality should continue using cached data and onboard feeds.

The system should continuously obtain available latest data from shore/land where communication exists, while not becoming dependent on the connection being continuously available.

The stale-data problem must be explicitly designed for. Consider the user’s hypothesis—combine current ship data with continuously fetched latest shore data—but research better mechanisms too.

The system should support different bandwidth modes. For example:

- low-bandwidth mode: maintain critical accuracy and essential functionality with limited data;
- higher-bandwidth mode: quickly acquire more data, more updates, larger layers, and more decision-support information before a connection is lost.

The architecture should prepare for high-bandwidth and low-bandwidth data sources, with the low-bandwidth mode accurate enough to remain operationally useful while taking advantage of higher bandwidth when available.

Communication loss, latency, stale data, incorrect data, and incorrect suggestions must be treated as first-class engineering/safety problems because there are no “do overs” at sea.

The application should never fail so badly that the crew is forced into a harsh decision and then has to wait for rescue because the software failed to degrade safely.

---


# 24. SHORE / STATION / EMERGENCY COMMUNICATION

The application should actively communicate with shore and Maitri/Bharati for data updates.

For emergencies, the application should be able to notify the nearest icebreaker and destination station about the ship’s current situation, conceptually similar to an SOS workflow, subject to real communications/integration capability and proper authorization.

The support layer should be able to display:

- available icebreakers;
- emergency responders;
- their positions/routes;
- relevant route implications for safer planning.

Treat actual emergency communication integrations as a future/real-integration capability unless the prototype genuinely has the required authorized communications pathway.

---


# 27. “REAL DATA ONLY” PROTOTYPE RULE

Develop everything that can be developed today while keeping it real.

No dummy data for capabilities that can genuinely use real data.

For any feature whose real data/integration is unavailable and must be simulated:

- make the simulation technically coherent;
- distinguish it explicitly from live data;
- use labels such as:
  - SIMULATED INPUT
  - HISTORICAL REPLAY
  - LIVE DATA
- never call simulated data “live”.

For future features specifically requested to be simulated, make the simulation smooth and integrated rather than visually obvious or brittle.

---


# 28. PENDRIVE DEPLOYMENT CONCEPT

The current deployment concept is:

1. A pendrive contains the software/environment.
2. The pendrive is connected to a laptop.
3. The application starts automatically or initiates the application workflow.
4. A login screen is presented.
5. After authentication, the actual command-center/navigation software loads.
6. The onboard laptop communicates over the available internet/communication link to land/shore services where available.
7. Land/shore data are fetched, processed, cached, and shown to the captain alongside onboard data.

The system architecture must clearly identify:

- what runs aboard the ship;
- what is taken from land via internet;
- what must remain locally available;
- what should be cached;
- what can be synchronized later;
- what must continue working when communications disappear.

AI-generated animation assets for the app may be added later; do not prioritize those now.

Focus first on the base software being strong enough for demonstration.

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


# 34. SMALL MVP PRIORITY

Build a SMALL MVP first.

MVP priority:

- map;
- own ship;
- route input;
- waypoints;
- planned vs actual track;
- one sea-ice layer;
- iceberg layer;
- weather snapshot;
- route health;
- explainable alternative route;
- timestamp/source display;
- decision log.

Do not build every feature at once.

However, future-scope features should be represented architecturally and simulated where explicitly requested for the demonstration.

---


# 35. DEMONSTRATION LOGIC

The demonstration must be understandable to a non-sailor but credible to a maritime reviewer.

Recommended flow:

1. Show planned Cape Town → station route.
2. Show own ship moving on the route.
3. Update sea-ice / iceberg / weather inputs.
4. Introduce a realistic route-degradation event.
5. Show exactly which assumption failed.
6. Generate 2–3 alternate corridors.
7. Compare safety margin + ETA + operational impact.
8. Ask for Master approval.
9. Save the decision in the log.
10. Continue monitoring.

The prototype to be shown tomorrow should include the future-scope intelligence where the original prompt explicitly asks for it, but any simulated component must be marked as such.

---


# 36. SAFETY / GOVERNANCE

This is decision support.

The Master remains the final operational authority.

Any route or safety recommendation must be:

- explainable;
- timestamped;
- auditable;
- grounded in evidence;
- explicit about uncertainty.

When uncertain, surface uncertainty rather than inventing certainty.

When data conflict, surface the conflict rather than averaging it away.

When a recommendation violates vessel capability or a hard safety constraint, reject it.

The most important feature is not making a clever route. It is making the route decision traceable, current, conservative where necessary, and easy for the bridge team to challenge.

The implementation, data model, UI, and explanations must consistently reflect the mental model of a professional polar bridge team.

---


# 37. REAL-WORLD FAILURE MODES TO DESIGN AROUND

Explicitly design for:

- communication delay;
- connection loss;
- stale data;
- data not updating freshly;
- incorrect data;
- conflicting sensors;
- incorrect recommendations;
- incomplete iceberg records;
- satellite revisit gaps;
- sparse/imperfect hydrographic coverage;
- rapidly changing ice;
- weather deterioration;
- human workload / alert overload;
- remote SAR / repair limitations;
- operational pressure from cargo/science goals;
- ship machinery/propulsion degradation;
- mission stoppage creating changing risk;
- lack of fallback options.

The application is intended for an environment in which a software failure should not itself strand the crew or force a dangerous decision.

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


# 44. DECISION QUALITY OVER VISUAL COMPLEXITY

A feature is valuable only when it improves the real operational decision.

Prioritize:

- evidence quality;
- data freshness;
- uncertainty handling;
- route validity;
- explainability;
- safe alternatives;
- human approval;
- low-bandwidth resilience;
- realistic ship integration;
- minimal cognitive load.

Do not build futuristic visuals that obscure the navigation concepts sailors already understand.

---


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
