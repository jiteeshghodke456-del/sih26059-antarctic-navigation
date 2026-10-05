# STAGE 04 — FUTURE SCOPE + DEPLOYMENT + STARTUP (GATED)
## ENTRY GATE
Before implementing/documenting extras, inspect the repository and ask whether this stage has already been completed. Verify existing future-scope, deployment, PPT, startup, and MLflow work first. Do not destabilize the PS-26059 core.

MISSION
After the core product, research, architecture, and UI are stable, implement or document the remaining future and supporting capabilities requested by the source prompt.

FUTURE FEATURES
- Scientific mission stoppage.
- Ecology/restricted/hazardous area awareness.
- Historical incidents/common route behavior/climate context.
- Shore/station/emergency coordination.
- Icebreaker/emergency responder support layer.
- Baymax Mode.
- Local LLM master-assistant experience.
- Pendrive deployment concept.
- High/low bandwidth behavior.
- Startup/market/commercial strategy.
- Draw.io architecture and PPT Markdown/document.

RULE
Future capabilities may be simulated for the demo, but must be labeled appropriately and must not be represented as real operational/medical/emergency capabilities when they are not actually implemented.

Do not allow future scope to destabilize the PS-26059 core.

PPT MATERIAL
Use simple human-like sentences. Provide the requested USPs, implementation roadmap, future scope, deployment plan, killer feature, innovation, feasibility, research justification, startup path, money-making plan, competitive comparison, strengths and weaknesses.

MLflow
Preserve the requested local WSL/Claude/MLflow setup requirements and verify real experiment tracking.

STOP after future/demo/supporting deliverables are complete and documented.

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


## 48A.25 CLIMATE NON-STATIONARITY MUST NOT BE HAND-WAVED

The existing requirement to recognize global warming/climate change should be preserved.

However:

- do not use "global warming" as a generic explanation for every unusual event;
- distinguish long-term climatological change from short-term weather/ice variability;
- research whether historical distributions remain representative;
- investigate dataset shift / non-stationarity in ML;
- consider recalibration/retraining triggers where appropriate.


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
