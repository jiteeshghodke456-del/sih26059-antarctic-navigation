# STAGE 05 — PRE-DEMO VALIDATION / RELEASE AUDIT (GATED)
## ENTRY GATE
Before running the audit, inspect the repository and ask whether this stage has already been completed. Verify existing tests, validation reports, data lineage, model evaluation, and demo readiness first. This stage is intentionally BEFORE the final SIH demo reconstruction.

MISSION
Attack the completed project rather than trusting its documentation.

Read:
- all prior stage handoffs;
- current repository;
- tests;
- data lineage;
- model evaluation;
- UI;
- demo flow.

RUN A SKEPTICAL-JUDGE ATTACK

For every important claim ask:
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
- Why is the method applicable to Antarctica?
- What exactly is real in the prototype?

MANDATORY BEHAVIORAL TESTS
1. Same environment, different vessel → verify route/risk behavior actually differs where it should.
2. Real data freshness → verify age/source/received time behavior.
3. Sensor/source disagreement → verify conflict is surfaced.
4. Stale communications → verify graceful degradation.
5. Missing iceberg record → verify system does not infer “no iceberg”.
6. Route degradation → verify route health changes because of actual evidence.
7. Alternative routes → verify alternatives differ in measurable exposure/ETA/fuel/operational terms.
8. Prediction → compare against later observation or appropriate historical replay.
9. Baseline → compare against defensible simpler method.
10. Simulated feature → verify it is labeled.
11. Existing tests → all pass after changes.
12. Demo → runs from the expected starting environment without undocumented manual repair.

OUTPUT
Create:
- VERIFIED CLAIMS;
- PARTIAL CLAIMS;
- FAILED CLAIMS;
- UNKNOWN CLAIMS;
- P0 blockers;
- P1 important improvements;
- P2 deferred items;
- judge questions and answers;
- final demo runbook;
- evidence links/commands;
- release readiness decision.

Do not beautify over a failed core capability.

STOP after the release audit.

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
