# ANTARCTIC NAVIGATION DECISION-SUPPORT SYSTEM — CLAUDE CODE MASTER PROMPT
## SEMANTIC-LOSSLESS RESTRUCTURED VERSION

### 0. HOW TO USE THIS DOCUMENT

You are taking over the design, research, architecture, prototype, and future implementation planning for a professional-grade Antarctic maritime navigation decision-support system for the Indian Antarctic Programme, with specific relevance to the NCPOR Cape Town → Maitri / Bharati logistics pattern.

This document has been reorganized for Claude Code. The wording has been normalized where useful, but **no distinct requirement, constraint, feature, research objective, future-scope item, safety principle, workflow step, data requirement, source, example, implementation expectation, commercial objective, or user-provided idea may be lost**.

Treat requirements using the following priority semantics:

- **MUST / HARD CONSTRAINT** — mandatory unless authoritative evidence proves it impossible or unsafe; surface the conflict rather than silently changing it.
- **SHOULD** — strong design expectation.
- **RESEARCH REQUIRED** — investigate with authoritative sources before making an implementation decision.
- **FUTURE SCOPE** — not required to be operational now, but must be architecturally represented and simulated/smartly demonstrated where requested.
- **DEMO / PROTOTYPE** — what should be demonstrable now/tomorrow.
- **DO NOT** — explicit prohibition.

When a user requirement is ambiguous, do not discard it. Preserve the ambiguity, research the available evidence, and make the smallest defensible assumption while documenting it.

Do not fabricate unavailable operational data. When something is simulated, label it as simulation.

---

# 1. PRODUCT VISION

Build an Antarctic sea-ice, iceberg-trajectory, weather/ocean, navigation, and route-decision-support system that behaves like a professional bridge decision-support layer rather than a generic GIS dashboard or consumer mapping product.

The central value proposition is not “find the shortest route.” The system should help a captain see the future state of the voyage, understand large amounts of environmental and operational information, detect when assumptions behind the approved route become invalid, compare safer alternatives, and make a better human decision.

The core principle is:

> There is no perfect path. There is only a safer path relative to the available evidence, vessel capability, operational constraints, uncertainty, and consequences of delay.

There is no route with zero sea-ice concentration. The goal is not to pretend that sea ice can be eliminated; it is to identify comparatively safer corridors with quantified/visible uncertainty and route consequences.

The system must preserve the captain’s existing mental model and habits while adding powerful predictive, analytical, and decision-support capabilities.

---

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

# 25. FUTURE “BAYMAX MODE”

Add a future feature called **Baymax Mode**.

It is a small AI assistant intended to connect to the captain’s watch and continuously monitor health-related signals such as:

- stress;
- O2 level;
- sleep;
- and other available data.

It can suggest:

- stress-reduction actions;
- music;
- words of comfort.

Baymax Mode is a future/dummy system.

Everything marked “(in future)” should be **surreally simulated** for the prototype where requested so the future feature can look integrated and smooth, as though the actual system were present, but it must not be represented as real operational/medical capability when it is not.

---

# 26. FUTURE LOCAL LLM

Future scope includes a locally run LLM for more natural communication, with a “master assistant relationship.”

This future capability may be a dummy in the prototype, but it should be architected and presented smoothly enough to demonstrate the intended interaction model.

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

# 39. COMMERCIAL / STARTUP / MARKET POSITIONING

The project should eventually be capable of becoming a startup.

The deliverables requested for the presentation/material include:

- 2 extremely strong USPs;
- 3 basic USPs;
- creative but human-like simple sentences that judges can understand;
- practical and completely sensible implementation roadmap;
- futuristic scopes;
- completely well-thought deployment plan;
- 1 killer feature that makes the system better than teams selecting the same PS;
- innovation and feasibility;
- a justified research slide demonstrating hard work and depth of research into the problem statement;
- supply-chain management or related relevance where applicable;
- explanation of how it becomes a startup later;
- clear money-making plan;
- market-entry approach / how to introduce the product;
- explanation of how features survive in the industry;
- competitor weaknesses and how this system succeeds;
- weaknesses and strengths of the application.

The strategy must be grounded in features that genuinely work in the market and solve daily user problems, not “sparkly” complexity that becomes useless after deployment.

Judges care about whether the features are good, useful, demonstrable, and market-relevant rather than merely complex.

Problems should be solved from the root from the user’s perspective.

---

# 40. PPT / DOCUMENT OUTPUTS REQUESTED

Produce a document containing, at minimum:

1. 2 extremely strong USPs.
2. 3 basic USPs.
3. Human-like/simple explanation suitable for a PPT.
4. Practical implementation roadmap.
5. Futuristic scopes.
6. Deployment plan.
7. 1 killer feature.
8. Innovation.
9. Feasibility.
10. Justified research slide/content.
11. Startup path.
12. Market-entry strategy.
13. Money-making plan.
14. Competitive comparison.
15. Strengths.
16. Weaknesses.
17. How features survive real industry use.

Also provide a clear system architecture suitable for draw.io.

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

# 45. FINAL SYSTEM ACCEPTANCE CHECKLIST

The system should answer all of these clearly:

### Position
Where is the vessel?

→ Current position, heading, speed, navigation source.

### Approved route
What route is approved?

→ Versioned route with waypoints, legs, and corridor.

### Future environment
What is happening ahead?

→ Ice, iceberg, weather, depth, and traffic over the route horizon.

### Continuation
Can the vessel safely continue?

→ Constraint checks plus explainable route health.

### Change
What changed?

→ Difference since the previous decision.

### Uncertainty
What is uncertain?

→ Data quality, age, uncertainty, disagreement, gaps.

### Contingency
What if this corridor closes?

→ Precomputed alternatives and trigger conditions.

### Authority
Who approved the change?

→ Decision log with time and authority.

### Offline operation
Can it operate offline?

→ Yes, using cached essential data and explicit stale-data status.

### Challengeability
Can a professional challenge the AI?

→ Yes; every recommendation exposes evidence, assumptions, alternatives, and triggers.

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

# 48A. RESEARCH-DRIVEN SYSTEM HARDENING — ADD THIS WITHOUT REMOVING OR WEAKENING EXISTING REQUIREMENTS

This section is an additional research and reasoning layer. It does NOT replace, delete, or weaken any requirement elsewhere in this document. Everything already specified remains active.

The purpose of this section is to prevent implementation from drifting into an attractive but scientifically or operationally inaccurate Antarctic navigation product.

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

# 48. SOURCE PRESERVATION / AUDIT APPENDIX

The following section preserves the user’s original source text verbatim. It is intentionally retained so that no information is lost during restructuring and so every normalized requirement above can be traced back to the supplied material.

---

## BEGIN ORIGINAL SOURCE — VERBATIM

  i want a nice simple gui for the app can we use open cpn man and can we integreate different layers like navigation layer sea ice forecasting layer icreberg path
  prediction layer and other stuff dashboard should be cleverly designed and the sea ice map layers below it too 
it will be like icy sea software more or less not exactly just a inspiration also use use Polarstern MapViewer + R/V Laura Bassi + actual Nuyina voyage-track visualization as your three primary UX references also  https://opencpn.org/ open cpn is an      open source navigation platform for navigation in sea can we use this applications gui and map
  rendering and route showing methods for our antartic application as insipration and can we add the other layer on top like sea ice conc ice berg route suggestion and other stuff
  related to ps to it we need the ui to use the professional grade software which they currently use like so maps ned to be very accurate with all kinds of data it
  could look cleaner but shouldnt hinder the sailors learning curve and make him forget concepts he currently uses the app sould use clean minimalmaps modern enough but
  shouldnt hinder sailor past habits and ice charts shoudnt use vibe coded ultra futuristic vibe the ui needs to have accurate data sailor needs and simple ui and accurate maps inspired from the above 2 applications
you can refer /userpsychology skill if needed for this  
focus on simplicity and not making too many changes in the ui that captains use in applications for looking at statc sea data ice charts and other stuff
and all kinds of data present in the software
 also research indian websites [ prompt frok chat gpt Do not prioritize Indian infrastructure for ideological, nationalistic, or “local-for-local” reasons.

Treat every Indian government/research source as a candidate that must be evaluated objectively against the best foreign alternative for the same capability.

For each data source, model, compute platform, communication service, API, map layer, weather product, ocean product, satellite product, or infrastructure component, compare:

* scientific accuracy
* spatial resolution
* temporal resolution
* update interval / latency
* Antarctic and Southern Ocean coverage
* historical depth
* reliability and availability
* API/data accessibility
* licensing and usage restrictions
* cost
* processing requirements
* interoperability
* operational maturity

Use the Indian government/research source when it is demonstrably competitive or superior on the dimensions relevant to that component.

Use a foreign source when it is materially better, more current, more accurate, more complete, more reliable, unavailable from India, or necessary for validation.

Where scientifically useful, use Indian and foreign sources together:

* Indian source for primary ingestion + foreign source for validation
* foreign source for primary ingestion + Indian source for independent cross-check
* multi-source ensemble/fusion when this improves prediction quality

Never assume an Indian service covers Antarctica merely because the organization operates internationally. Verify actual spatial coverage, update frequency, resolution and current availability before integrating it.

Do not hard-code the architecture around nationality of the provider. Build provider-agnostic adapters so the application can switch between Indian and foreign sources based on measured data quality and availability.

The objective is:
BEST AVAILABLE SYSTEM = MAXIMUM USE OF CAPABLE EXISTING INDIAN INFRASTRUCTURE + FOREIGN SOURCES WHERE THEY ARE TECHNICALLY BETTER OR NECESSARY.

The final system should contain a documented justification for every major source choice, including why an Indian source was selected over a foreign alternative or why a foreign source was retained.
] (we will also use foreign countries provided data but using Indian data sources gives us a upper hand we can combine all such open source data please use all the kinds of data you need for accuracy and prediction and suggestion) https://data.ncpor.res.in/ such as this one and many other for data we can use related to our voyage
  decision both of our stations and refine ui of the application /fontend-design-skills /skill-finder /brainstorming /plan look into tech stack more and system
  asrchitecture first make a clear system architecture for draw io and the md for the ppt mentioned below in prompt then start with prototype 
please develop whatever we can today keeping everything real no dummy data.the workflow is like this -> 
connect pendrive to laptop the application starts automatically APPLICATION START
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
┌───────────────────────────────────────┐
│ UPDATED INFORMATION                   │
│                                       │
│ Ship state                             │
│ Navigation                            │
│ Ice                                    │
│ Icebergs                               │
│ Weather                                │
│ Ocean                                  │
│ Forecast                               │
│ Mission                                │
│ Route health                           │
│ Data freshness                         │
└──────────────────────┬────────────────┘
                       ↓
                ROUTE REASSESSMENT
                       ↓
              ┌────────┼────────┐
              ↓        ↓        ↓
          KEEP PLAN  EDIT     ALTERNATIVE
                       │        │
                       └────┬───┘
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
  live 3d 2d map , on the route our ship is following should also check for weather updates further down the route as a blizzard can hit the ship or southern winds can
  start freezing the ice iceberg featyre should show predeicted movement roadmap like icysea software using vector arrows simple clean minimal informative and
  professional built for sailors old map habits  as there arent many failures currently the ships still reach antartica safely but see if ny past incidents happened on
  the route to maitri and bharati station from cape town and learn from them the models should also learn from mistakes this is a future scope it can do while suggesting though this is a future
  scope but add it to the protype we will be showing tomorrow , it also shouldnt hinder ecology and shouldnt enter hazardous forbidden zones so please research about that
  antartica voyage policies and dangerous parts where you shouldnt sail in a ship from through the software should support missions stoppage so if they want to run a
  uikc scientific research at a place in the sea along the sailing route or decided route it should be very smart and understand where and how long has the ship stopped
  and should the captain kee moving or not monitoring further weather ice concentration and winds and ice pressure and iceberg moving in and out of route they can
  simly be avoided by going around them but the point is we have to know about them before we see them and the application is a way the captain can see the future ,
  take better decisions, help him understand large amounts of data by processing it for him and showing it to him on the gui everything he needs which he already used
to use before but just with powerful features that we aim to provide added to it, like an assistant , check for other competitors which which existed before us
why they failed in what way are they better than us exactly and what gaps can we cover from them our software should also know common occrunces on the route to 
the two stations the commonly used route each time of the year and should be smart enough to know that globalwarming exists and can cause unpredictable
occurences to happen theres no thing such as perfect path only safe path theres no route with 0 percent sea ice concentration only with less sea ice concentration never under
estimate berg infested water and smallest of the ice in future should be able to extract data from already existing sensors on board of ship and use it 
application shuld notify nearest ice breaker and destination station about current situation of the ship like an sos signal it should actively ommunicate
with shore and maitri and Bharati station for data updates gui should also have a support layer so when that is turned on you can see available icebreakers 
or other emergency responders , and their route for better and safer voyage planning future will have a locally run llm for even better natural communication like 
a master assistant relationship the future stuff can be a dummy but smartly applied so it looks as if its actually real have a dummy login screen at the start of 
the applications workflow sudden storms can overthrow voyage plans hence applications hould be ready to begin assisting sailor with further data and current 
situation , as data isn't live we have to brainstorm how do we overcome stale data issue my guess is using current ship data and continuously keep fetching available
latest data from shore but your research will surely find even better suggestions and ideas i dont have much knowledge about system designs that are these low in level
so ill rely on you try to use open sourced stuff ive given you hugging face access mcp and plugin and gh and Kaggle and this one  :- We are setting up an ML/AI development environment for my SIH 2026 Antarctic project.
and make what doesn't exist yourself as due to isolation we also can add a mental health feature in the software we will call this one Baymax Mode this will be a
small ai assistant which will connect to the captains watch and monitor his health status like stress o2 level sleep and al other dat continuously monitor it
and suggest stress , music and words of comfort this will be a dummy system too as it is in the future everything marked (in future) shuld be surreally simulated
such that judges cant identify difference between real and dummy feature it as to be that smooth as if its actually really there start simple sure and we iwll
keep making slight changes in ui and experience of protoype though im 100 percent reliant on you for making me a draw io file of the now updated architecture 
and data sources i will also need a file stating 2 extremely strong usp of our application and 3 basic usp this sould be creative and this document that staes these informations
which will be added to ppt should be in human like simple sentences simple enough tounderstand , int he same document add these too :- a practical and
complately making sence implementation roadmap , futuristic scopes , a completely well thought of deployment plan , 1 kille rfeature what makes us
better than other people who picked the same ps, innovation and feasilbility of the application , a justified research slide
so judges understand the hardwork and how in depth did we dive into the problem statement, supply chain management or related , how it becomes a 
startup later , how will you introduce yourself in the market with a clear money making plan , how our features survive in the industry 
, how our competitors fail and we succeed , all weaknesses and storng poitns of our application , and judges dont care bout complexity
they see how good are the features ad if they actually work in the market and are not just appear sparkly but are utterly useless in the real application when deployed
and the user starts to use it daily ,  our problems should be solved and thought from root from users perpective  i also had the idea of using a pendrive to load all our
software into whoch when plugged in asks for login and when login completes it will load the actual software i will create ai generated images later for the animaion ina pp
dont worry bout that for now focus o making the base software ready perfectly good for demonsttrion the pendrive when plugged in will connect using internet to 
land fetch the data process and show it to captain along wth other features now we need to clearly identify what runs aboard and what gets taken from the land
vi internet knowing all the kinds of data youre gonna need to require for the application is a must and what data needs ot be trly present and what doesn't is another must
after the internet connectivity research part we should see if bandwidths can increase to bring in more data as necessary or take more decisions these decsions will addd to a a trong usp 
hence needs to be thought of carefully suppose if we get 2 sources high bandwidth and low bandwidth  then we should make infrastructure ready for low bandwidth accurately enouhg but should substantially increase power
if it switches to high bandwidth mode eg more data more updates quickly downloading stuff before the connection is lost my prompt has many gaps where i have left the further desicisons to you after 
sharing what i really want ot see in my applicarion and architecture i will trust you fully for researching and setting clear goals for yourself adfter completely understanding what i need in my application my architecture and results 
im still quite unsure how will we ale to deal with delays in coms connection lost , communication lost , incorrect data and incorrect suggestion , how to manage stale data and data not being updated
freshly as there are no do overs in the sea we have to thinkthis through our applicatoin should never fail so badly that the crew could face harsh decisom and have to wait for rescue stranded

 
[from chtpgt End-to-End Mental Model for Antarctic Voyage Planning, Ice Navigation and Route Decision Support


A practitioner-oriented research brief for designing an Antarctic navigation decision-support system for Indian Antarctic logistics, with specific attention to the Maitri–Bharati operating pattern.

Prepared from IMO, IHO, WMO, NCPOR/MoES, COMNAP, USNIC, BAS and related operational sources.

─────────────────────────────────────────────────────────────────────────────────────────────────────────

Executive conclusion

The most important thing to understand is that an Antarctic captain does not normally ask a computer, "What is the shortest route to Maitri?" The real task is closer to: "Given my ship's certified polar capability, current and forecast sea ice, iceberg exposure, bathymetry, weather, sea state, visibility, traffic, communications, station logistics, daylight, fuel/endurance and the consequences of delay, what corridor is safe enough, where are the decision gates, and when must I change the plan?"

The route on the electronic chart is therefore not the decision itself. It is the executable representation of a decision. The professional workflow is appraisal -> route design -> safety validation -> execution -> continuous monitoring -> re-appraisal -> controlled amendment. IMO formalizes voyage planning around appraisal, planning, execution and monitoring.

For the Indian Antarctic programme, the problem is unusually concrete: NCPOR's current operating pattern uses Cape Town as the maritime staging point and the chartered vessel to serve Bharati and Maitri. In the 2025-26 season NCPOR's planning advisory gave a tentative sequence Cape Town -> India Bay (Maitri) -> Larsemann Hills (Bharati) -> India Bay -> Cape Town, with the actual 2025 expedition departing Cape Town on 25 December 2025 aboard MV Vasiliy Golovnin. The exact track is operational data; the official published documents establish the voyage pattern and timings, not every waypoint used by the bridge.

How to use this document

Read Sections 1-8 to build sailor empathy and understand the physical bridge workflow. Read Sections 9-14 to translate that workflow into software requirements. The final section contains a Claude-ready system prompt that encodes the professional mental model without pretending that an AI can replace the Master or Officer of the Watch.

1. What a voyage actually looks like on the map

1.1 The basic picture

A professional electronic navigation display usually contains several distinct concepts at the same time:

Map object

What the sailor sees

What it means operationally

Official ENC / nautical chart

Coastline, depth contours, obstructions, aids to navigation, chart limits and symbols

The authoritative geographic/navigation base for route planning.

Planned route

A sequence of waypoints joined into route legs

The intended track the bridge team has approved.

Own-ship symbol

Current ship position plus heading/course/speed vectors

Where the vessel is now and where its motion is taking it.

Historical track / breadcrumb

A trail behind the ship

What the ship actually did, useful for monitoring and reconstruction.

AIS contacts

Other vessels with identity/course/speed where available

Traffic awareness and collision-risk assessment; not a replacement for visual/radar watchkeeping.

Radar picture

Echoes around the ship

Independent detection of targets and, where detectable, ice/objects.

Ice layer

Sea-ice concentration/type/extent and often iceberg information

The key environmental constraint in polar operations.

Weather/ocean layers

Wind, pressure, waves, visibility, currents, forecast fields

Affects safety, ETA, fuel, motion, visibility and the likelihood of route deterioration.

Safety corridors / limits

No-go areas, safety contour, XTD/XTL, depth or operational boundaries

The mathematical expression of minimum acceptable separation from hazards.

The captain therefore does not look at a single magical "Antarctic map." He or she reconciles multiple data sources in one bridge workflow. Modern integrated bridges can display radar, chart, navigation and environmental information together, but the human still owns the judgement.

1.2 What a route looks like conceptually

Cape Town

    |

    |  long ocean leg

    |  planned route = WP001 -> WP002 -> WP003 -> ...

    |

    |                 actual ship track

    |                 (can diverge from plan)

    v

  MIZ / iceberg-risk region

    |

    |------ planned corridor ------X

    |                                  |                               \ amended corridor

    |                                    v                                 v

India Bay / Maitri maritime approach ----> offload / station interface


Route record typically contains, for each leg:

WP_from -> WP_to

distance

initial / final course

planned speed

ETA

cross-track limits

turning / wheel-over information

notes / constraints

The route is usually not entered as one freehand line. It is constructed from waypoints and legs, with safety parameters and checks. IMO training guidance explicitly covers waypoint selection, planning notes, turning radius/wheel-over, dangerous depths, cross-track deviations, safe speed, route checking, alarms/warnings and alternative routes.

1.3 Planned route versus current position

This distinction matters enormously for your software. The planned route is a hypothesis about where the vessel should go. The live vessel track is the observation of where it is actually going. Ice, weather, traffic and operational events can cause the actual track to diverge. A good DSS must make that divergence visible rather than silently replacing the plan.

2. Who is actually making the decision on the ship?

Role

Primary responsibility in this problem

Master / Captain

Final command responsibility. Approves voyage plan, major route amendments, operational limits and go/no-go decisions.

Chief Mate / First Officer

Passage planning, bridge management, cargo/operations coordination and navigational management depending on watch system.

Officer of the Watch (OOW)

Maintains the navigational watch, monitors position/traffic/weather, executes the approved passage plan and escalates deviations.

Ice Navigator / qualified polar navigator

Specialist interpretation of ice conditions, ice types, route feasibility and ice-related operational limitations. IMO guidance stresses continuous ice monitoring when underway in ice.

Helmsman / steering system

Maintains commanded heading or follows steering commands/autopilot as permitted.

Lookout

Independent visual detection of hazards, traffic and ice. Critical because sensor data are not complete.

Engine room / Chief Engineer

Ensures propulsion, steering, power generation and other machinery remain within operating condition; propulsion capability is a navigational constraint.

Shore / expedition logistics

Station requirements, cargo priorities, timing, helicopter/offload operations, weather windows, contingency plans.

Ice / weather service analysts

Provide environmental intelligence; they influence but do not replace shipboard judgement.

Scientists / expedition staff

Provide mission objectives and operational requirements but do not normally own ship navigation decisions.

For software design, this means the system is a decision-support layer for a multi-person bridge team, not a single-user route app. The Master should be able to understand why the recommendation changed, what evidence supports it, and what assumptions are driving it.

3. What the sailor must know before leaving port

3.1 The ship itself

Polar Ship Certificate category / applicable ice capability and operational limits.

Propulsion type, steering characteristics, stopping/turning behaviour and maneuverability under expected conditions.

Draft, displacement, stability and minimum safe under-keel clearance.

Fuel, fresh water, stores and endurance limits.

Known machinery limitations under low temperatures and ice exposure.

Bridge equipment available, its redundancy and known sensor limitations.

PWOM (Polar Water Operational Manual) procedures and operational decision limits.

Crew competence, watchkeeping arrangements and polar training requirements.

3.2 The geography

Official nautical charts / ENCs at appropriate scales.

Coastal approaches, bathymetry, shoals, islands, channels, anchorages and known hazards.

Chart quality and survey uncertainty, especially where hydrographic coverage is weak.

Station approach geometry and the actual maritime offload / mooring arrangement.

Fallback locations and emergency options, not just the intended destination.

3.3 The environment

Current sea-ice distribution and concentration.

Ice type / stage of development and likely strength.

Fast ice versus drifting pack ice / marginal ice zone.

Iceberg positions and uncertainty.

Wind, wave, swell, pressure, visibility, precipitation and freezing spray.

Surface currents and expected drift of sea ice / icebergs.

Daylight and visual conditions.

Forecast confidence and time-to-degradation.

3.4 The operation

Cargo sequence and whether specific weather/sea-state windows are required.

Helicopter or aviation interfaces, if relevant.

Personnel transfer constraints.

Scientific objectives and whether the ship must deviate from the normal logistics track.

Station communications and coordination plan.

Waste return / backhaul obligations and departure deadline.

Winter onset / seasonal closure risk.

4. The navigation stack: what is actually on the bridge

System

Input

Output / use

Failure implication

GNSS / position source

Satellite navigation

Ship position

Loss/degradation requires alternative position fixing and cross-checks.

Gyrocompass

Heading sensors

True/reference heading

Heading error can corrupt steering and ECDIS orientation.

ECDIS

ENC + position + heading + speed + route

Chart display, route plan, alarms, monitoring

Can mislead if chart data, safety settings or sensor inputs are wrong.

Radar / ARPA

Radio echoes

Target detection, bearing/range, tracking

Blind spots/clutter/ice/weather limitations; still essential as an independent sensor.

AIS

VHF/ship transponders

Traffic identity, position, course, speed, status

Coverage/availability depends on other vessel and radio conditions; not every hazard transmits AIS.

Echo sounder

Acoustic depth

Under-keel awareness / depth trend

Late/limited warning in some geometries; must not replace chart/bathymetry planning.

Speed log

Water/ground reference depending system

Speed and distance

Important for ETA and navigation calculations.

Weather receiver / satcom feed

Meteorological information

Forecasts/warnings

Communication latency / model uncertainty.

Ice information service

Satellite analysis, charts, observations

Sea-ice/iceberg intelligence

May be delayed, coarse or uncertain; must be ground-truthed.

GMDSS

Safety communications

Distress, safety and maritime safety information

Loss of comms reduces situational awareness and contingency options.

Ship's internal systems

Engine, steering, alarms, cargo, stability

Operational state

A route that is geographically safe may still be operationally impossible.

IMO notes that ECDIS can incorporate real-time information and that its use became an accepted/required chart carriage pathway under SOLAS. IHO's S-101 is the current operational ENC product specification from 1 January 2026; S-102 bathymetry, S-104 water level, S-111 surface currents and S-124 navigational warnings form part of the wider S-100 digital navigation ecosystem.

5. How route entry really works

5.1 From destination to route

Define the voyage: departure port/position, destination and intermediate operational stops.

Collect the complete appraisal: charts, publications, weather, ice, warnings, ship limitations, traffic and operational constraints.

Select the chart areas / ENC cells and appropriate scales.

Create candidate waypoints and route legs around land, shoals, safety contours and operational constraints.

Set planned speed or speed profile and calculate ETA.

Set cross-track limits / corridor width and turn parameters.

Run the ECDIS route safety check and manually inspect the route at appropriate scales.

Review alternatives and contingency routes.

Document the plan and obtain the required Master / company approval.

During execution, continuously compare the actual ship state against the plan.

5.2 Typical route data model

Field

Example / meaning

Route ID

ISEA-45-BHR-MTR-OUTBOUND

Waypoint ID

WP_014

Latitude / longitude

Coordinate pair

Leg distance

Nautical miles

Course

True course or system reference

Speed

Planned speed for leg

ETA

Estimated time at waypoint

XTD / XTL

Cross-track corridor limits

Turn information

Radius / wheel-over / turn anticipation as applicable

Safety depth / contour

Vessel-specific protection setting

Operational constraint

e.g. avoid >X concentration of ice, avoid known berg cluster

Source timestamp

When the supporting ice/weather data were valid

Confidence

How reliable the input is

Decision note

Why this waypoint/corridor was chosen

Alternate route

Precomputed fallback corridor

Approval / revision

Who changed/approved the route and when

5.3 Important distinction: route planning is not navigation

Route planning chooses a permissible corridor and sequence of waypoints. Navigation is the continuous act of determining where the ship is, where it is heading, what is around it, whether the plan remains valid, and what immediate control action is required. Your SIH system is primarily a decision-support and route-replanning system sitting beside this navigation loop.

6. What changes when the ship approaches Antarctica

The problem changes qualitatively. Open-ocean route planning is dominated by bathymetry, weather, traffic and efficiency. Polar navigation adds a moving, partially observed hazard field whose properties have physical meaning: concentration, ice type, thickness/strength, floe size, drift, melt and deformation.

6.1 Sea-ice information is not just 'ice/no ice'

Operational ice products can describe total concentration, partial concentrations of multiple ice types, stage of development/age and floe size. The WMO Egg Code is the conventional compact representation used in ice observations/charts.

Ice attribute

Why the bridge cares

Total concentration

How much of the sea surface is occupied by ice.

Stage of development

Age/thickness/strength proxy; older and thicker ice can present very different resistance.

Partial concentration

Which fractions of the total field belong to the different ice types.

Floe size

Affects maneuverability, impact/pressure interactions and route continuity.

Fast ice

Fixed to coast/grounded; often behaves as a barrier rather than a drifting field.

Pack ice / MIZ

Dynamic field with openings, compression and changing routes.

Iceberg presence

Large/relatively isolated hazards, often not encoded by the same field as sea ice.

Trend / change

A field that is worsening may be more dangerous than a field with slightly higher but stable concentration.

A software system should therefore never collapse the ice state to a binary safe/unsafe label without exposing the underlying variables.

6.2 Iceberg data

USNIC tracks large Antarctic icebergs using satellite-derived observations and publishes positions in machine-readable formats including CSV and GIS shapefile. BAS also emphasizes that up-to-date sea-ice and iceberg information is required for safe and efficient routing and that local observations can add important 'ground truth' to satellite and automated products.

For your DSS, treat iceberg position as a moving object with uncertainty: last observation time, estimated position, observed size, source and confidence. The system should distinguish 'tracked object' from 'all possible ice in the water'.

7. What a captain is actually deciding

Think of the captain's problem as a sequence of decision gates rather than one optimization problem.

Decision gate

Question

Evidence

Capability gate

Can this ship legally and physically operate here under its polar certificate/PWOM limits?

Ship certification, ice capability, draft, machinery, crew competence

Chart gate

Is the route geographically understood well enough?

ENC, bathymetry, survey confidence, publications

Ice gate

Will the expected ice exceed the ship's operating limit or create unacceptable maneuvering risk?

Ice concentration/type, forecast, drift, visual/radar observations

Weather gate

Will wind/waves/visibility make the proposed corridor unsafe or make the operation impossible?

Forecasts, observations, sea state

Traffic gate

Is there conflict with other vessels or operations?

AIS, radar, communications

Logistics gate

Will the chosen track still meet cargo/people/operation timing?

ETA, station window, helicopter/cargo plan

Communications gate

Can the ship obtain timely warnings and coordinate contingencies?

GMDSS, satcom, station/shore contact

Contingency gate

If the route closes in front of us, where do we go?

Alternate corridors, safe havens, endurance

Execution gate

Are the current observations still consistent with the assumptions used to approve the route?

Live sensors + latest ice/weather

This is the heart of the problem statement. A strong DSS should surface these gates explicitly and show the captain what is driving the recommendation. A black-box 'route score = 0.82' is less useful than 'Route B is preferred because it reduces forecast ice pressure, keeps UKC margin above the vessel threshold, and retains an alternate corridor if the MIZ advances.'

8. Why Antarctic navigation is unusually difficult

Problem

Operational consequence

Software implication

Sparse / imperfect hydrographic coverage

Charted depths may be less certain than in heavily surveyed ports.

Display survey/source quality and depth confidence.

Rapidly changing sea ice

A route can become impractical after it was approved.

Time-stamp every environmental layer; support re-routing.

Iceberg drift

Large hazards move independently of sea-ice polygons.

Track discrete objects and propagate uncertainty.

Satellite revisit / latency

Remote sensing is not continuous.

Show observation age and gaps.

Weather changes

Visibility and sea state can change faster than a route cycle.

Forecast trajectory, not just current conditions.

Weak communications

Large files and continuous cloud services may be unavailable.

Edge-first, cache-first, low-bandwidth design.

Sensor disagreement

GNSS, radar, chart and visual observations may differ.

Sensor provenance, confidence, conflict alerts.

Human workload

Bridge team has many simultaneous tasks.

Prioritize actionable changes, avoid alert flooding.

Remote SAR / repair constraints

A small error can have a large consequence.

Penalty for isolation and lack of safe fallback.

Mission pressure

Cargo/science objectives create pressure to continue.

Keep safety constraints higher priority than ETA optimization.

9. The India-specific Maitri/Bharati context

9.1 The geography

NCPOR identifies Maitri at approximately 70°45'52"S, 11°44'03"E in the Schirmacher Oasis and describes it as an inland station about 100 km from the shore. Bharati is at approximately 69°24.41'S, 76°11.72'E in the Larsemann Hills near the coast. NCPOR describes the two as roughly 3,000 km apart.

9.2 The maritime pattern

NCPOR planning documents repeatedly describe the general maritime voyage pattern as Cape Town -> Bharati -> Maitri -> Cape Town, with the exact sequence changing according to expedition objectives and operational requirements. More recent planning material for the 2025-26 season used a tentative sequence Cape Town -> India Bay -> Larsemann Hills -> India Bay -> Cape Town.

This matters for your system because the destination is not simply a GPS point. A vessel approaches a maritime operating area, performs offload/transfer activity, may wait for operational weather, then departs for another remote operating area. The DSS should represent the voyage as a sequence of operational phases.

Phase

Maitri/Bharati interpretation

1. Port preparation

Cape Town loading, fuel, cargo sequencing, personnel and ship readiness.

2. Southern Ocean transit

Long ocean leg with weather routing and increasing polar awareness.

3. Pre-ice / iceberg watch

Enhanced ice information, iceberg updates, visual/radar vigilance.

4. Polar approach

More conservative speed/corridor, route validity checks, ice observations.

5. Station operating area

Approach, mooring/anchoring/offload/transfer as operational plan allows.

6. Station turnaround

Cargo, personnel, waste, mission-specific work, weather window management.

7. Inter-station leg

New route appraisal; previous route is not simply copied because environmental state changes.

8. Return leg

Re-appraisal, departure timing, seasonal risk and ice closure considerations.

9. Exit / Southern Ocean

Gradual reversion toward conventional open-ocean voyage management.

9.3 45th ISEA: a concrete modern reference

NCPOR reported that the 45th Indian Scientific Expedition to Antarctica departed Cape Town on 25 December 2025 aboard MV Vasiliy Golovnin and completed its planned summer component. NCPOR's 2025 planning advisory had earlier shown an approximate 111-day charter with tentative dates: Cape Town departure in late December, India Bay in early January, Larsemann Hills in early February, return to India Bay in March, and Cape Town in early April. Treat those dates as a planning baseline rather than a guaranteed actual track or schedule.

10. What the professional sailor does with changing information

A useful mental model is a feedback controller:

                PLAN

                  |

                  v

        route + constraints + ETA

                  |

                  v

               EXECUTE

                  |

                  v

        observe ship + environment

        /        |          \

     GNSS      radar       visual

        \        |          /

         +--- AIS / ice / weather

                  |

                  v

          COMPARE TO ASSUMPTIONS

                  |

        +---------+---------+

        |                   |

     still valid         invalid

        |                   |

        v                   v

    continue          re-appraise route

                          |

                          v

                    amend + approve

                          |

                          +----> EXECUTE

The most valuable software event is therefore not only 'new data arrived.' It is 'new data invalidates a route assumption.'

Incoming change

Possible response

Ice concentration increases ahead

Reduce speed, widen/shift corridor, hold, or choose alternate corridor.

Ice edge moves toward planned track

Trigger route-validity warning and present alternatives.

New large iceberg appears

Calculate separation against current and future track; flag route if required.

Visibility deteriorates

Increase conservatism; rely more heavily on radar/navigation procedures.

Wind/sea state worsens

Re-evaluate speed, ETA, vessel motion and ability to conduct transfer.

Bathymetry concern discovered

Reduce route confidence and re-plan around safer depth margin.

Propulsion performance degrades

Recalculate achievable speed and ice-handling capability; reassess route.

Station operation slips

Optimize revised arrival/departure window; do not sacrifice navigational safety.

Communication outage

Fall back to cached data and onboard procedures; reduce dependence on shore services.

Sensor disagreement

Surface the conflict; do not automatically average incompatible observations.

11. What data should your DSS ingest?

11.1 Minimum viable layer stack

Layer

Required fields

Base chart

ENC cell, geometry, feature class, depth/contour, publication/update status.

Own vessel

Latitude, longitude, COG, SOG, heading, speed, draft, current route, timestamp.

Route

Waypoints, legs, XTD/XTL, speed, ETA, safety parameters, alternate routes.

Sea ice

Concentration, ice type/stage, floe characteristics where available, timestamp, source.

Icebergs

ID, lat/lon, size, update time, source, uncertainty.

Weather

Wind, pressure, visibility, precipitation, temperature, wave height/direction, forecast time.

Ocean

Surface currents, sea temperature where relevant, forecast validity.

Traffic

AIS target ID, location, course, speed, status, last update.

Warnings

Navigational warnings, urgency, geographic polygon/point, start/end time.

Ship limits

Ice class/capability, max operational ice, minimum depth/UKC, speed rules, machinery state.

Mission

Destination, cargo/transfer priority, operational window, deadlines, station status.

Confidence

Source, timestamp, age, quality/confidence and uncertainty.

11.2 Data provenance is a first-class feature

Every environmental object shown to the bridge should answer: What is this? When was it observed? Who produced it? What sensor/model produced it? How accurate is it? When should I expect the next update?

A 12-hour-old ice analysis and a 15-minute-old radar observation should never be visually or numerically indistinguishable.

12. What your AI should and should not do

12.1 High-value AI functions

Fuse heterogeneous observations into a consistent situational picture.

Detect route-assumption violations.

Forecast movement/trend of ice and other hazards.

Generate candidate route corridors instead of a single opaque answer.

Score alternatives by safety margin, ETA impact, fuel/energy impact and operational feasibility.

Explain recommendations with evidence and timestamped sources.

Predict when a route is likely to become invalid before the hazard reaches the ship.

Summarize the change since the last bridge decision.

Provide contingency routes and explicit trigger conditions for switching.

Work offline/edge-first and degrade gracefully when communications fail.

12.2 What the AI must not pretend to do

Do not claim to be the Master.

Do not silently overwrite the approved passage plan.

Do not treat satellite ice data as ground truth.

Do not infer that absence of an iceberg record means no iceberg exists.

Do not hide uncertainty behind a single safety score.

Do not ignore the ship's certified operating limits.

Do not prioritize ETA over safety constraints.

Do not make a route recommendation without showing the evidence window and data age.

13. The UX you should actually build

Do not design a generic GIS dashboard. Design a bridge decision-support interface.

Screen region

Content

Primary map

Official chart + planned route + actual track + ice + iceberg + danger areas.

Own-ship card

Position, COG/SOG, heading, next waypoint, ETA, XTE, current operational state.

Route health

Valid / degraded / invalid with the top 3 reasons.

Ice panel

Concentration/type/trend + source timestamp + uncertainty.

Weather panel

Current + forecast in route corridor, not generic station weather.

Hazard timeline

Events likely to affect route over the next 6/12/24/48 h.

Alternative routes

A/B/C corridors with safety margin, ETA delta, hazard exposure and rationale.

Decision log

What changed, who approved, when, and why.

Data freshness

Per-layer age and health status.

Offline state

What data are cached and what is unavailable.

13.1 The screen should answer five questions immediately

1. Where am I?

2. Where was I supposed to be?

3. What is in front of me?

4. Is the approved route still valid?

5. What are my safest alternatives if it is not?

14. Build the system around decision objects, not just map layers

A common software mistake is to build 'the map' first and add intelligence later. A stronger architecture models the operational decision.

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


Example:

Decision D-204

  state_time: 2026-01-08T06:00Z

  route: ISEA45-MTR-07

  status: DEGRADED

  primary_reason: increasing pack-ice concentration

  secondary_reason: worsening visibility forecast

  alternative: CORRIDOR-B

  ETA_delta: +5h

  confidence: medium

  evidence:

      ice_chart: USNIC_...

      local_observation: bridge_watch_...

      forecast: model_...

  trigger:

      "switch if concentration > threshold OR observed lead closes"

  approval:

      Master pending

This structure makes the system explainable, auditable and easier to integrate with live navigation feeds.

15. Source and evidence map

Source

URL

Use in this guide

IMO Polar Code

https://www.imo.org/en/ourwork/safety/pages/polar-code.aspx

Polar Ship Certificate, PWOM, polar operational requirements.

IMO Shipping in Polar Waters

https://www.imo.org/en/mediacentre/hottopics/pages/polar-default.aspx

Polar hazards, training, categories and decision-support concepts.

IMO Voyage Planning A.893(21)

https://wwwcdn.imo.org/localresources/en/KnowledgeCentre/IndexofIMOResolutions/AssemblyDocuments/A.893%2821%29.pdf

Appraisal, berth-to-berth planning, execution and monitoring.

IMO ECDIS

https://www.imo.org/en/OurWork/Safety/Pages/ElectronicCharts.aspx

ECDIS purpose and chart carriage context.

IHO ENC / S-100

https://iho.int/en/enc-ecdis

S-101, S-102, S-104, S-111, S-124 operational product ecosystem.

WMO Sea-Ice Guidance

https://community.wmo.int/site/knowledge-hub/programmes-and-initiatives/marine-services/sea-ice-guidance

Sea-ice nomenclature and charting standards.

WMO Manual 558

https://etrp.wmo.int/pluginfile.php/20417/mod_label/intro/WMO-558-vI-2024_en.pdf

Sea-ice codes, stages and nomenclature.

US National Ice Center Antarctic Ice Charts

https://usicecenter.gov/Products/AntarcCharts

Daily/weekly Antarctic sea-ice products.

USNIC Antarctic Icebergs

https://usicecenter.gov/Products/Antarcicebergs

Tracked iceberg positions and machine-readable products.

BAS Mapping / Polar View

https://www.bas.ac.uk/polar-capabilities/mapping/

Operational polar mapping and sea-ice information.

BAS Sea Ice Observations for Ship Navigation

https://www.bas.ac.uk/wp-content/uploads/2024/10/NZArC_Scoping_Report_2024.pdf

Need for current ice/iceberg information and value of local observations.

NCPOR Research Stations

https://pdc.ncpor.res.in/npdc/research-stations.action

Maitri/Bharati locations and operational context.

NCPOR 2025 Planning Advisory

https://ncpor.res.in/files/AL-01%20Planning%20Advisory%20-%20Antarctic%20Expedition-2025_1.pdf

2025-26 tentative voyage sequence/timing.

NCPOR 45th ISEA update

https://ncpor.res.in/news/view/1012

45th ISEA actual departure and completion report.

PIB / MoES 43rd ISEA voyage

https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=1993769&lang=2&reg=48

Example of Indian chartered vessel, crew and Antarctic entry.

COMNAP Antarctic facilities / vessels

https://www.comnap.aq/antarctic-facilities-information

National Antarctic programme facilities and vessel ecosystem.

16. A sailor-empathy walkthrough: one hypothetical bridge watch

1. At watch handover, the OOW reads the current passage plan, next waypoints, ship position, weather/ice notes, standing orders and any recent changes.

2. The OOW checks whether the ship remains within the planned cross-track corridor and whether the next leg remains safe under current information.

3. The ice layer is examined for observation age, concentration/type and trend. Radar and visual lookout are treated as independent evidence.

4. The OOW checks for new iceberg or traffic information and compares it with the own-ship future path, not just the present position.

5. The weather forecast is checked over the actual route corridor and next decision horizon.

6. If all assumptions remain valid, the ship continues with normal monitoring.

7. If a key assumption is invalidated, the OOW escalates according to the vessel's procedures and the Master decides whether the route should be amended.

8. A candidate alternative is evaluated using current evidence and vessel constraints.

9. The revised decision is recorded. The original plan remains visible as history so that the bridge team can see what changed.

That last point is important for your UI: the system should preserve the chain of decisions. A captain needs to reconstruct not only where the ship went, but why the route was changed at a particular time.


Antarctic Sailor / Master Mental Model • Research brief • 2026

17. Claude-ready master prompt

Copy the following prompt into Claude Code / another coding agent before asking it to design or implement your Antarctic navigation decision-support system.

You are helping build a professional-grade Antarctic maritime navigation decision-support system for the Indian Antarctic Programme, with specific relevance to the NCPOR Cape Town -> Maitri / Bharati logistics pattern.


You must think like a bridge team supporting a Master, not like a generic GIS developer.


CORE MENTAL MODEL


The system is NOT a generic map application and NOT an autonomous captain.


The core operational loop is:


1. APPRAISE the voyage

2. PLAN the passage

3. VALIDATE the route against chart, bathymetry, vessel limits and hazards

4. EXECUTE the approved route

5. MONITOR the ship and environment continuously

6. DETECT when assumptions become invalid

7. RE-APPRAISE

8. GENERATE candidate alternatives

9. PRESENT an explainable recommendation

10. REQUIRE appropriate human approval for route changes


The planned route and actual ship track are separate objects.


The route is a sequence of waypoints and legs, not a single freehand polyline.


The actual bridge mental model is:

planned route + own ship state + radar/AIS + official ENC + bathymetry + sea ice + iceberg information + weather/ocean + navigational warnings + vessel capability + mission constraints + uncertainty.


WHAT A PROFESSIONAL BRIDGE TEAM CARES ABOUT


Represent at minimum:

- own ship position

- COG/SOG

- heading

- next waypoint

- ETA

- cross-track error / corridor

- planned route

- actual historical track

- depth / safety contour / under-keel margin

- traffic targets

- sea-ice concentration

- ice type / stage of development

- floe characteristics when available

- fast ice

- iceberg objects

- iceberg position age

- wind

- waves

- visibility

- surface current

- navigational warnings

- forecast time horizon

- source timestamp

- confidence / uncertainty

- ship polar category / ice capability

- draft and endurance constraints where available

- station operational constraints

- alternate routes

- decision history


DO NOT REDUCE ICE TO A BOOLEAN "SAFE / UNSAFE" FLAG.


Sea ice has operational meaning through:

- total concentration

- partial concentration

- stage of development / age / thickness proxy

- floe size

- drift and trend

- compression / opening where supported

- fast ice versus drifting pack

- observation age

- source and uncertainty


Use WMO-style sea-ice concepts and terminology.


ICEBERG MODEL


Treat icebergs as moving discrete hazard objects with:

- ID

- latitude

- longitude

- observed size

- last update

- source

- uncertainty

- movement estimate when available


Do not infer "no iceberg" from "no tracked iceberg record".


SOURCES AND DATA PROVENANCE


Every important environmental object must expose:

- source

- timestamp

- observation/forecast time

- latency/age

- confidence or uncertainty

- processing method if known


A 12-hour-old satellite ice analysis must be visually distinguishable from a 15-minute local observation.


Architecture must support multiple sources and disagreement between sources.


NAVIGATION DATA STANDARDS


Understand the professional digital navigation stack:

- ENC / ECDIS

- IHO S-101 electronic navigational charts

- S-102 bathymetric surfaces

- S-104 water level information

- S-111 surface currents

- S-124 navigational warnings

- AIS

- radar / ARPA

- GNSS

- gyro

- echo sounder

- weather / ocean products

- GMDSS safety communications


The software should be architected so a real ECDIS or bridge integration can be connected later without redesigning the domain model.


ROUTE MODEL


Represent route data as:

Route

 -> Waypoints

 -> Legs

 -> constraints

 -> speed profile

 -> ETA

 -> XTD/XTL

 -> turn/wheel-over metadata where relevant

 -> safety parameters

 -> notes

 -> alternative routes

 -> approval/revision history


Do not silently replace an approved route.


When a new route is proposed, preserve the old route and show the reason for the change.


DECISION MODEL


Create a first-class Decision object containing:

- decision_id

- time

- vessel state

- route version

- environmental state

- hazards considered

- assumptions

- constraints

- alternatives

- recommendation

- confidence

- trigger conditions

- evidence

- human approval state

- revision history


A route recommendation must answer:

1. What changed?

2. Why does it matter?

3. Which constraint is now binding?

4. What alternatives exist?

5. What is the ETA/safety tradeoff?

6. What evidence supports the recommendation?

7. How fresh is that evidence?

8. What condition would make us change the decision again?


ANTARCTIC OPERATING CONTEXT


Use the Indian Antarctic Programme as a concrete design reference.


Important context:

- NCPOR is India's nodal organisation for the Antarctic Programme.

- Maitri is in Schirmacher Oasis at approximately 70°45'52"S, 11°44'03"E and is inland from the coast.

- Bharati is in the Larsemann Hills near Prydz Bay at approximately 69°24.41"S, 76°11.72"E.

- The maritime operating pattern has commonly involved Cape Town staging and chartered-vessel service to Bharati and Maitri.

- NCPOR's 2025-26 planning material used a tentative Cape Town -> India Bay -> Larsemann Hills -> India Bay -> Cape Town sequence.

- The 45th ISEA departed Cape Town on 25 Dec 2025 aboard MV Vasiliy Golovnin.


Do NOT fabricate exact bridge waypoints, mooring points, chart depths, ice limits, or current-voyage tracks unless they are provided by authoritative data.


Do NOT assume that a published itinerary equals the actual bridge track.


PUBLIC AIS IS NOT THE SAME AS THE SHIP'S PRIMARY NAVIGATION RECORD.


USER INTERFACE


Design the main experience like a bridge decision-support display, not a consumer map.


The primary view should show:

- official chart / base map

- planned route

- actual track

- own ship

- ice field

- iceberg objects

- traffic

- hazard zones

- optional forecast trajectory

- route corridor

- alternative corridors


Peripheral panels:

- own-ship state

- route health

- ice state

- weather

- hazard timeline

- alternatives

- data freshness

- decision log

- offline state


The system should immediately answer:

- Where am I?

- Where was I supposed to be?

- What is ahead?

- Is the route still valid?

- What are the safest alternatives?


ALERTING PHILOSOPHY


Do not create alert spam.


Prioritize:

P1 = immediate safety relevance

P2 = route degradation / approaching decision point

P3 = informational change


Every alert should include:

- what changed

- location

- time

- severity

- source

- confidence

- route consequence

- suggested action

- expiry / next review time


AI / ML


High-value functions:

- multimodal data fusion

- route-assumption violation detection

- ice trend prediction

- iceberg trajectory estimation

- route corridor generation

- candidate route ranking

- ETA impact estimation

- uncertainty propagation

- anomaly detection

- explainable change summaries

- contingency trigger generation


Avoid:

- autonomous route execution

- black-box safety score

- hiding uncertainty

- using AI confidence as legal/operational authority

- pretending to replace Master/OOW judgement


OFFLINE / LOW-BANDWIDTH


Antarctic operations may have intermittent or constrained communications.


The system must be edge-first:

- local cache

- local map tiles

- local data store

- queued synchronization

- delta updates

- compressed environmental layers

- source timestamps

- stale-data indicators

- graceful degradation


If communications disappear, the core map/route/safety functionality should continue using cached data and onboard feeds.


ENGINEERING EXPECTATIONS


Before coding:

1. Define domain entities.

2. Define ingestion interfaces.

3. Define time/coordinate conventions.

4. Define data provenance model.

5. Define route representation.

6. Define hazard representation.

7. Define uncertainty model.

8. Define decision lifecycle.

9. Define offline synchronization.

10. Define UI state model.


Then build a SMALL MVP.


MVP PRIORITY:

- map

- own ship

- route input

- waypoints

- planned vs actual track

- one sea-ice layer

- iceberg layer

- weather snapshot

- route health

- explainable alternative route

- timestamp/source display

- decision log


Do not build every feature at once.


DEMONSTRATION LOGIC


The demo should be understandable to a non-sailor but credible to a maritime reviewer.


A good demo flow:

1. Show planned Cape Town -> station route.

2. Show own ship moving on the route.

3. Update sea-ice/iceberg/weather inputs.

4. Introduce a realistic route degradation event.

5. Show exactly which assumption failed.

6. Generate 2-3 alternate corridors.

7. Compare safety margin + ETA + operational impact.

8. Ask for Master approval.

9. Save the decision in the log.

10. Continue monitoring.


NEVER FAKE LIVE DATA WITHOUT LABELING IT AS SIMULATION.


If real data are unavailable in an MVP, explicitly label the data source as:

SIMULATED INPUT / HISTORICAL REPLAY / LIVE DATA


Do not call simulated data "live".


SAFETY / GOVERNANCE


This software is decision support.


The Master remains the final operational authority.


Any route or safety recommendation must be explainable, timestamped and auditable.


When uncertain, surface uncertainty rather than inventing certainty.


When data conflict, surface the conflict rather than averaging it away.


When a recommendation violates vessel capability or a hard safety constraint, reject it.


The most important feature is not making a clever route. It is making the route decision traceable, current, conservative where necessary, and easy for the bridge team to challenge.


Your implementation, data model, UI and explanations must consistently reflect the mental model of a professional polar bridge team.

18. Final design checklist

Question

Your system should answer it

Where is the vessel?

Current position, heading, speed and navigation source.

What route is approved?

Versioned route with waypoints, legs and corridor.

What is happening ahead?

Ice, iceberg, weather, depth and traffic over the route horizon.

Can the vessel safely continue?

Constraint checks plus explainable route health.

What changed?

Diff since previous decision.

What is uncertain?

Data quality, age and uncertainty visible.

What if this corridor closes?

Precomputed alternates and trigger conditions.

Who approved the change?

Decision log with time and authority.

Can it operate offline?

Yes, with cached essential data and stale-data indication.

Can a professional challenge the AI?

Yes; every recommendation has evidence, assumptions and alternatives.
Copy the following prompt into Claude Code / another coding agent before asking it to design or implement your Antarctic navigation decision-support system.
You are helping build a professional-grade Antarctic maritime navigation decision-support system for the Indian Antarctic Programme, with specific relevance to the NCPOR Cape Town -> Maitri / Bharati logistics pattern.
You must think like a bridge team supporting a Master, not like a generic GIS developer.
CORE MENTAL MODEL
The system is NOT a generic map application and NOT an autonomous captain.
The core operational loop is:
1. APPRAISE the voyage
2. PLAN the passage
3. VALIDATE the route against chart, bathymetry, vessel limits and hazards
4. EXECUTE the approved route
5. MONITOR the ship and environment continuously
6. DETECT when assumptions become invalid
7. RE-APPRAISE
8. GENERATE candidate alternatives
9. PRESENT an explainable recommendation
10. REQUIRE appropriate human approval for route changes
The planned route and actual ship track are separate objects.
The route is a sequence of waypoints and legs, not a single freehand polyline.
The actual bridge mental model is:
planned route + own ship state + radar/AIS + official ENC + bathymetry + sea ice + iceberg information + weather/ocean + navigational warnings + vessel capability + mission constraints + uncertainty.
WHAT A PROFESSIONAL BRIDGE TEAM CARES ABOUT
Represent at minimum:
- own ship position
- COG/SOG
- heading
- next waypoint
- ETA
- cross-track error / corridor
- planned route
- actual historical track
- depth / safety contour / under-keel margin
- traffic targets
- sea-ice concentration
- ice type / stage of development
- floe characteristics when available
- fast ice
- iceberg objects
- iceberg position age
- wind
- waves
- visibility
- surface current
- navigational warnings
- forecast time horizon
- source timestamp
- confidence / uncertainty
- ship polar category / ice capability
- draft and endurance constraints where available
- station operational constraints
- alternate routes
- decision history
DO NOT REDUCE ICE TO A BOOLEAN "SAFE / UNSAFE" FLAG.
Sea ice has operational meaning through:
- total concentration
- partial concentration
- stage of development / age / thickness proxy
- floe size
- drift and trend
- compression / opening where supported
- fast ice versus drifting pack
- observation age
- source and uncertainty
Use WMO-style sea-ice concepts and terminology.
ICEBERG MODEL
Treat icebergs as moving discrete hazard objects with:
- ID
- latitude
- longitude
- observed size
- last update
- source
- uncertainty
- movement estimate when available
Do not infer "no iceberg" from "no tracked iceberg record".
SOURCES AND DATA PROVENANCE
Every important environmental object must expose:
- source
- timestamp
- observation/forecast time
- latency/age
- confidence or uncertainty
- processing method if known
A 12-hour-old satellite ice analysis must be visually distinguishable from a 15-minute local observation.
Architecture must support multiple sources and disagreement between sources.
NAVIGATION DATA STANDARDS
Understand the professional digital navigation stack:
- ENC / ECDIS
- IHO S-101 electronic navigational charts
- S-102 bathymetric surfaces
- S-104 water level information
- S-111 surface currents
- S-124 navigational warnings
- AIS
- radar / ARPA
- GNSS
- gyro
- echo sounder
- weather / ocean products
- GMDSS safety communications
The software should be architected so a real ECDIS or bridge integration can be connected later without redesigning the domain model.
ROUTE MODEL
Represent route data as:
Route
 -> Waypoints
 -> Legs
 -> constraints
 -> speed profile
 -> ETA
 -> XTD/XTL
 -> turn/wheel-over metadata where relevant
 -> safety parameters
 -> notes
 -> alternative routes
 -> approval/revision history
Do not silently replace an approved route.
When a new route is proposed, preserve the old route and show the reason for the change.
DECISION MODEL
Create a first-class Decision object containing:
- decision_id
- time
- vessel state
- route version
- environmental state
- hazards considered
- assumptions
- constraints
- alternatives
- recommendation
- confidence
- trigger conditions
- evidence
- human approval state
- revision history
A route recommendation must answer:
1. What changed?
2. Why does it matter?
3. Which constraint is now binding?
4. What alternatives exist?
5. What is the ETA/safety tradeoff?
6. What evidence supports the recommendation?
7. How fresh is that evidence?
8. What condition would make us change the decision again?
ANTARCTIC OPERATING CONTEXT
Use the Indian Antarctic Programme as a concrete design reference.
Important context:
- NCPOR is India's nodal organisation for the Antarctic Programme.
- Maitri is in Schirmacher Oasis at approximately 70°45'52"S, 11°44'03"E and is inland from the coast.
- Bharati is in the Larsemann Hills near Prydz Bay at approximately 69°24.41"S, 76°11.72"E.
- The maritime operating pattern has commonly involved Cape Town staging and chartered-vessel service to Bharati and Maitri.
- NCPOR's 2025-26 planning material used a tentative Cape Town -> India Bay -> Larsemann Hills -> India Bay -> Cape Town sequence.
- The 45th ISEA departed Cape Town on 25 Dec 2025 aboard MV Vasiliy Golovnin.
Do NOT fabricate exact bridge waypoints, mooring points, chart depths, ice limits, or current-voyage tracks unless they are provided by authoritative data.
Do NOT assume that a published itinerary equals the actual bridge track.
PUBLIC AIS IS NOT THE SAME AS THE SHIP'S PRIMARY NAVIGATION RECORD.
USER INTERFACE
Design the main experience like a bridge decision-support display, not a consumer map.
The primary view should show:
- official chart / base map
- planned route
- actual track
- own ship
- ice field
- iceberg objects
- traffic
- hazard zones
- optional forecast trajectory
- route corridor
- alternative corridors
Peripheral panels:
- own-ship state
- route health
- ice state
- weather
- hazard timeline
- alternatives
- data freshness
- decision log
- offline state
The system should immediately answer:
- Where am I?
- Where was I supposed to be?
- What is ahead?
- Is the route still valid?
- What are the safest alternatives?
ALERTING PHILOSOPHY
Do not create alert spam.
Prioritize:
P1 = immediate safety relevance
P2 = route degradation / approaching decision point
P3 = informational change
Every alert should include:
- what changed
- location
- time
- severity
- source
- confidence
- route consequence
- suggested action
- expiry / next review time
AI / ML
High-value functions:
- multimodal data fusion
- route-assumption violation detection
- ice trend prediction
- iceberg trajectory estimation
- route corridor generation
- candidate route ranking
- ETA impact estimation
- uncertainty propagation
- anomaly detection
- explainable change summaries
- contingency trigger generation
Avoid:
- autonomous route execution
- black-box safety score
- hiding uncertainty
- using AI confidence as legal/operational authority
- pretending to replace Master/OOW judgement
OFFLINE / LOW-BANDWIDTH
Antarctic operations may have intermittent or constrained communications.
The system must be edge-first:
- local cache
- local map tiles
- local data store
- queued synchronization
- delta updates
- compressed environmental layers
- source timestamps
- stale-data indicators
- graceful degradation
If communications disappear, the core map/route/safety functionality should continue using cached data and onboard feeds.
ENGINEERING EXPECTATIONS
Before coding:
1. Define domain entities.
2. Define ingestion interfaces.
3. Define time/coordinate conventions.
4. Define data provenance model.
5. Define route representation.
6. Define hazard representation.
7. Define uncertainty model.
8. Define decision lifecycle.
9. Define offline synchronization.
10. Define UI state model.
Then build a SMALL MVP.
MVP PRIORITY:
- map
- own ship
- route input
- waypoints
- planned vs actual track
- one sea-ice layer
- iceberg layer
- weather snapshot
- route health
- explainable alternative route
- timestamp/source display
- decision log
Do not build every feature at once.
DEMONSTRATION LOGIC
The demo should be understandable to a non-sailor but credible to a maritime reviewer.
A good demo flow:
1. Show planned Cape Town -> station route.
2. Show own ship moving on the route.
3. Update sea-ice/iceberg/weather inputs.
4. Introduce a realistic route degradation event.
5. Show exactly which assumption failed.
6. Generate 2-3 alternate corridors.
7. Compare safety margin + ETA + operational impact.
8. Ask for Master approval.
9. Save the decision in the log.
10. Continue monitoring.
NEVER FAKE LIVE DATA WITHOUT LABELING IT AS SIMULATION.
If real data are unavailable in an MVP, explicitly label the data source as:
SIMULATED INPUT / HISTORICAL REPLAY / LIVE DATA
Do not call simulated data "live".
SAFETY / GOVERNANCE
This software is decision support.
The Master remains the final operational authority.
Any route or safety recommendation must be explainable, timestamped and auditable.
When uncertain, surface uncertainty rather than inventing certainty.
When data conflict, surface the conflict rather than averaging it away.
When a recommendation violates vessel capability or a hard safety constraint, reject it.
The most important feature is not making a clever route. It is making the route decision traceable, current, conservative where necessary, and easy for the bridge team to challenge.
Your implementation, data model, UI and explanations must consistently reflect the mental model of a professional polar bridge team.]

 
[ prompt from chatgpt to refer for mlflow Current environment:

* OS: WSL (Linux)
* Claude Code: 2.1.252
* Claude executable: `/home/jiteesh/.local/bin/claude`
* `python` was initially unavailable; `python3` exists.
* I am setting up a project-local Python `.venv`.
* MLflow has not yet been connected to Claude Code.
* I want MLflow for experiment/model tracking and Claude Code access through MCP.
* Keep the MCP tool surface minimal to avoid unnecessary context/token usage.
* Do not add W&B unless there is a concrete reason.

Take over from this point. First inspect the current environment and verify what has already been installed/configured. Then complete the MLflow setup, start/configure the local MLflow server, connect MLflow to Claude Code through MCP, and verify the connection with an actual test experiment/run.

Do not blindly assume commands or overwrite existing configuration. Explain what you are doing briefly as you go in very short and stop if you encounter an issue that requires my decision.]



## END ORIGINAL SOURCE — VERBATIM

---

# 49. SEMANTIC-LOSSLESS OPERATING INSTRUCTION

Claude Code must treat Sections 1–48 as the normalized execution layer and the original-source appendix as the final preservation/audit layer.

When there is any doubt whether a detail matters, assume that it matters.

When simplifying or consolidating requirements, preserve the underlying information, constraints, intent, examples, and prohibitions.

Do not delete information merely because it is repetitive, unusual, aspirational, or difficult to implement. Determine whether it adds a separate constraint or expectation first.

Where two statements appear to conflict, surface the conflict and research it rather than silently dropping one.

Where the source contains a factual claim that requires current verification, verify it before using it as an implementation fact; do not silently rewrite the original claim in the audit appendix.
# FINAL IMPLEMENTATION DISCIPLINE — DO NOT LOSE THE CORE

The project must remain centered on the actual PS-26059 problem.

The PS-26059 CORE is:
1. Antarctic sea-ice forecasting;
2. Antarctic iceberg trajectory prediction;
3. identification of safer and fuel/energy-efficient navigation routes.

These three capabilities are the primary technical objective and must receive implementation priority over secondary, future, presentation, or convenience features.

Do NOT allow the project to become an “Antarctic operating system” before the PS-26059 core is technically demonstrated.

The implementation priority MUST remain:

PS-26059 CORE
→ sea-ice forecasting
→ iceberg trajectory prediction
→ vessel-aware route assessment
→ safe/fuel-efficient candidate corridors
→ uncertainty-aware decision support
→ professional map/decision workspace
→ measurable validation

Only after the above pipeline is functioning should substantial effort be moved into secondary/future capabilities such as emergency coordination, LLM assistance, Baymax Mode, advanced station coordination, or broader startup-platform functionality.

A feature must justify its existence by answering:
“What real operational decision does this feature improve?”

Do not add complexity merely because it looks impressive in a demonstration.

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

# ANTARCTIC REGULATORY / ENVIRONMENTAL RESEARCH

Before implementing hard geographic restrictions, research authoritative Antarctic requirements including, where applicable:

- Antarctic Treaty System requirements;
- Environmental Protocol;
- Antarctic Specially Protected Areas (ASPAs);
- Antarctic Specially Managed Areas (ASMAs);
- management plans;
- vessel/environmental restrictions;
- pollution-prevention requirements;
- applicable MARPOL requirements;
- navigational warnings;
- protected ecological areas;
- station-specific operating constraints.

Do not invent no-go polygons.

If an area is restricted or environmentally sensitive, identify the authoritative source and legal/operational basis.

# NAVIGATION DATA QUALITY

Research and account for chart/data quality, not merely chart presence.

Investigate, where applicable:

- chart coverage;
- survey quality;
- CATZOC / quality-of-data concepts;
- under-keel clearance;
- S-129 / UKC-related information;
- bathymetric uncertainty;
- chart update status;
- source authority.

A geographically safe route can still be operationally unsuitable if the underlying bathymetric knowledge is insufficient.

# HUMAN FACTORS

Research bridge human factors relevant to the design:

- cognitive workload;
- alert fatigue;
- automation bias;
- trust calibration;
- fatigue;
- watch handover;
- discoverability;
- established navigation habits;
- information prioritization.

The UI must reduce cognitive load without hiding important information.

# COMPETITIVE / OPERATIONAL BENCHMARK

Do not merely ask:

“What software already exists?”

Ask:

- What decision does it support?
- What data does it use?
- At what latency?
- What forecast horizon?
- What vessel assumptions?
- What risk methodology?
- What routing methodology?
- What uncertainty does it expose?
- What does the user actually see?
- What is genuinely better?
- What remains unsolved?
- What can this system demonstrate that they cannot?

Do not create a strawman competitor.

# SKEPTICAL-JUDGE TEST

For every major claim, Claude must be able to answer:

- Better than what?
- Based on what data?
- At what resolution?
- At what update frequency?
- Validated how?
- Under what vessel assumptions?
- With what uncertainty?
- What happens if the prediction is wrong?
- What happens if communication is lost?
- What happens if two sources disagree?
- Why is this method applicable to Antarctica?
- What exactly is real in the prototype?

Do not claim capabilities that the prototype cannot substantiate.

# CORE TECHNICAL MILESTONE BEFORE EXPANSION

Before spending substantial implementation effort on peripheral features, produce a working end-to-end demonstration of:

REAL / AUTHORITATIVE DATA
→ DATA PROVENANCE
→ SEA-ICE / ICEBERG / WEATHER PROCESSING
→ FORECAST OR TRAJECTORY OUTPUT
→ VESSEL-AWARE CONSTRAINTS
→ RISK / EXPOSURE ASSESSMENT
→ 2–3 CANDIDATE ROUTES
→ SAFETY / ETA / FUEL-ENERGY COMPARISON
→ UNCERTAINTY
→ EXPLAINABLE RECOMMENDATION
→ HUMAN APPROVAL
→ ROUTE VERSION
→ MONITORING / REASSESSMENT.

This is the primary technical milestone.

Do not consider the project technically mature merely because the GUI is polished.

# IMPLEMENTATION QUALITY GATE

Before moving to the next major feature, verify:

1. Does the current feature work with real data where real data are available?
2. Is its source/provenance known?
3. Is its freshness visible?
4. Is its uncertainty known?
5. Is there an appropriate baseline?
6. Is it validated?
7. Does it improve an actual decision?
8. Does it fail safely?
9. Can the captain understand it?
10. Does it remain compatible with the existing architecture?

If the answer is no, fix the underlying capability before adding decorative complexity.

# SCOPE PRIORITY

Use this order of importance:

TIER 1 — PS-26059 CORE
- sea-ice forecasting;
- iceberg trajectory prediction;
- safe/fuel-efficient route decision support;
- real-data ingestion;
- uncertainty;
- validation;
- map/decision workspace.

TIER 2 — OPERATIONAL DSS ENHANCEMENTS
- vessel capability;
- Polar Code / PWOM research;
- POLARIS / other polar risk methodologies;
- weather-over-route analysis;
- bathymetric confidence;
- route health;
- alternatives;
- provenance;
- offline operation;
- sensor integration;
- decision history.

TIER 3 — FUTURE PRODUCT
- emergency communication;
- icebreaker coordination;
- scientific mission support;
- local LLM;
- Baymax Mode;
- broader station/expedition logistics;
- startup platform expansion.

Do not allow Tier 3 to displace Tier 1.

# FINAL QUESTION BEFORE CODING

Before implementing any major component, explicitly ask internally:

“What is the PS-26059 contribution of this component?”

If the answer is weak, classify it as supporting infrastructure, secondary functionality, or future scope and do not allow it to consume disproportionate implementation time.

The goal is not to build the largest Antarctic software system.

The goal is to build the most scientifically defensible, operationally credible, vessel-aware, uncertainty-aware, demonstrably useful PS-26059 solution possible, while keeping the larger product vision architecturally alive.