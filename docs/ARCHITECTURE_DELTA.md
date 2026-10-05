# Architecture delta

Stage 02's rule: *"DO NOT blindly implement the research recommendations. For
every proposed change: cite the research evidence; show the current
implementation; identify the gap; propose the smallest necessary change;
preserve working behavior; identify migration risk; define tests."*

This document is the delta, not a re-description of the system.
`docs/ARCHITECTURE.md` remains the standing description.

---

## 1. Architecture delta

### 1.1 The change that mattered — a decision layer

| | |
|---|---|
| **Evidence** | §11 builds the product on a first-class Decision object; §12 defines nine gates; §48A.1 says think from the decision backwards; §48A.13 requires route health be an evidence-based state |
| **Current implementation** | Six read-only `GET` endpoints. Grep for *decision object*, *route version*, *approval*, *decision log* returned **zero hits**. There was no `POST` of any kind |
| **Gap** | The product had no decision in it. It rendered environmental data and a precomputed route |
| **Smallest change** | Two pure modules (`isih/decision.py`, `isih/gates.py`), one service that binds them to files already on disk (`isih/demo/decision_service.py`), and four endpoints |
| **Preserved** | Every existing endpoint and every existing figure. The ice raster, projection and route drawing were kept verbatim |
| **Migration risk** | Low. The decision layer reads existing artifacts and writes nothing to disk |
| **Tests** | `isih/test_decision.py` (14), `isih/test_gates.py` (15), `isih/test_behavioural.py` (14) |

**The design choice worth defending: health is derived, never scored.** §11 says
a black-box `route score = 0.82` is less useful than an evidence-based
explanation. So there is no score. Health is the worst state among nine named
gates and the gate that produced it travels with it, which makes the
explanation a structural property rather than a string somebody remembered to
write.

**And UNKNOWN never reads as a pass.** A gate we cannot evaluate caps health at
DEGRADED. §48A.12 makes a false negative — telling a master the route is fine
when it is not — the expensive error in this domain, so missing evidence is a
reason to be less confident, never a reason to be silent.

### 1.2 What the delta deliberately does *not* change

- **PolarRoute stays.** It works, it is MIT-licensed BAS software, and §33's
  reuse-before-build order is satisfied. The finding that fuel and traveltime
  are collinear is a configuration fact, not a reason to replace the router.
- **The U-Net stays.** See §2.1.
- **No foundation model is adopted.** `docs/research/MODEL_REUSE_MATRIX.md`
  adjudicated nine and rejected seven; two are benchmark-only.

---

## 2. AI/ML architecture

### 2.1 Sea-ice concentration correction — the incumbent, retained

| Stage | Detail |
|---|---|
| **DATA** | NOAA/NSIDC CDR G02202 v6, 25 km, 1,096 daily files 2018–2020. CMEMS GLORYS12 as the background field |
| **PREPROCESSING** | 12 channels: the background valid at target time, the last 7 days of observations, and derived channels. Three-way temporal split |
| **MODEL** | U-Net, 1,929,601 parameters, one model per horizon, same seed across horizons. Trained on a free Kaggle T4 |
| **OUTPUT** | Corrected SIC at 1, 3, 5, 7-day leads |
| **UNCERTAINTY** | **None quantified.** One seed, no ensemble, no calibration. This is a stated gap, not an oversight |
| **VALIDATION** | Held-out melt season, scored once. RMSE 0.0465 / 0.0720 / 0.0938 / 0.0968 against persistence 0.0570 / 0.0958 / 0.1204 / 0.1395 |
| **CONSUMER** | Nothing yet. **The trained weights are not in the repository and the demo does not run the model** — it serves the routing result and the satellite record |

**Why no foundation model replaces this.** The argument is information-theoretic,
not budgetary. The entire 1979-present daily SIC record is on the order of
17,000 frames of ~10⁵ pixels — far too small for the scale premise that
motivates foundation models, and a ~2 M-parameter CNN saturates it. *"We could
not afford one"* is a losing answer; *"the target is too small to need one"* is
not.

### 2.2 The forcing layer — designed, not built

`docs/ISIH_RESULTS.md` named ERA5 wind and temperature as the top unimplemented
improvement. The adjudication found that the obvious implementation would make
things **worse**: in ERA5 and MERRA-2 sea ice is a *prescribed* lower boundary
taken from satellite SIC, so 2 m temperature at the target date is close to a
deterministic function of the observed ice at that date. Adding it at `t+lead`
would add a second, larger leak on top of the GLORYS12 one we already disclose.

The corrected design:

- winds valid at `t`, not `t+lead` — causal and free;
- better, the **wind-advected first guess** (semi-Lagrangian advection of
  SIC(`t`) by the free-drift rule), which is simultaneously a stronger baseline
  and a better channel than raw wind;
- forcing as a **pluggable service benchmarked foundation-model vs NWP vs
  persisted analysis**, not "we integrated Aurora". The first expert question is
  *"why not ECMWF open data?"*, and it needs an answer from evidence.

The same service feeds three consumers: the SIC model, the Wagner iceberg drift
model (which currently declares a sensitivity sweep because it had no winds),
and route weather exposure.

### 2.3 Iceberg drift — implemented, never validated

Wagner–Dell–Eisenman is implemented and tested against the paper's own
coefficient table, and a regime check ran on the real USNIC catalogue under a
**declared sweep of assumed winds and currents**, because we do not have wind
and current at those positions and did not invent them. **No trajectory error
has ever been measured.** It is one third of the problem statement and it is
roadmap, not capability.

---

## 3. Data and model flow

```
NSIDC CDR G02202 v6 (25 km)  ─┐
CMEMS GLORYS12 background    ─┼─→ features (12 ch) ─→ U-Net ─→ corrected SIC
                              │                                    │
                              │                          (not yet consumed)
                              ▼
                    meshiphi mesh (5° cells)
                              │
                    VesselPerformanceModeller  ←── vessel config
                              │                    (beam, speed, ice limit)
                              ▼
                    PolarRoute Dijkstra + smoothing
                              │
                              ▼
             routes.json · alternatives.json · vessel_comparison.json
                              │
ATS protected areas ─────────►│
destination window   ─────────►│
                              ▼
                     NINE DECISION GATES        ← the new layer
                              │
                    route health (derived)
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
      master's approval  ────────────►  decision log
       (versioned)                    (supersedes chain)
```

**The resolution seam, stated because it is invisible otherwise:** the router
optimises on 5° cellbox means; the "heaviest ice on the route" figure we
publish is sampled from 25 km pixels along the line. They are not the same
quantity, and tightening the mesh constraint can raise the pixel figure — 74%
to 91% when the limit went from 60% to 55%.

---

## 4. Domain-model changes

| Type | Purpose | §|
|---|---|---|
| `GateState` | PASS / MARGINAL / FAIL / **UNKNOWN** | §12 |
| `Health` | VALID / DEGRADED / CRITICAL / INVALID | §48A.13 |
| `Evidence` | source, detail, **provenance as a real path**, valid time, age | §15 |
| `GateResult` | one gate, its state, reason, evidence, and where it bites | §12 |
| `Alternative` | a corridor with a measurable delta, or one that does not exist | §32 |
| `Approval` | approved, by whom, when — `by` is required, never defaulted | rule 12 |
| `Decision` | every field §11 enumerates, plus `supersedes` | §11 |

`gate_digest()` is what distinguishes *an assumption changed* from *new data
arrived*: identical evidence yields an identical digest and therefore no
transition at all.

---

## 5. API and interface changes

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/decision?day=` | GET | Evaluate for a day; report divergence from the standing approval |
| `/api/decision/approve` | **POST** | Master approves. Appends a version; **400** if unattributed |
| `/api/decisions` | GET | The decision log |
| `/api/alternatives` | GET | A/B/C corridors and the findings from computing them |
| `/api/vessel-comparison` | GET | Same ice, two ships |

All six pre-existing endpoints are unchanged.

---

## 6. Migration plan

Landed in five commits, each independently revertible: domain model → gate
evaluators → alternatives generator → service and endpoints → UI. No schema, no
persistence, no external service. The decision log is in-memory on purpose —
persisting approvals would mean a demo inherits the previous demo's decisions.

**Risks accepted:** the log does not survive a restart (correct for a demo); the
alternatives are precomputed rather than solved live (a route solve takes tens
of seconds and PolarRoute is not in the demo venv, deliberately, so the running
app has no geospatial dependency that can fail live).

---

## 7. Test plan

| Layer | File | Asserts |
|---|---|---|
| Domain | `isih/test_decision.py` | UNKNOWN never passes; FAIL-now vs FAIL-later; digest stability |
| Gates | `isih/test_gates.py` | Each gate's real state; every UNKNOWN names its blocker |
| Behaviour | `isih/test_behavioural.py` | The twelve mandatory tests |
| Service | `isih/demo/test_app.py` | Endpoints, page structure, no external resources |

**77 tests pass.** The invariants most worth protecting: a gate with no data can
never read as a pass; a never-scored destination is UNKNOWN and not *closed*;
the page never loads an external resource.

---

## 8. Rationale linked to research

| Change | Research |
|---|---|
| No foundation model adopted | `research/MODEL_REUSE_MATRIX.md` |
| Ice limit labelled an assumption everywhere | `research/VESSEL_SPECIFICATIONS.md` — no framework indexes concentration |
| No POLARIS RIO published | `research/POLARIS_APPLICABILITY.md` |
| Horizons stated explicitly | `research/FORECAST_HORIZONS.md` |
| Protected areas by legal regime, not as no-go | `isih/protected_areas.py` — ASMA entry needs no permit |
| Forcing at `t`, not `t+lead` | `research/MODEL_REUSE_MATRIX.md` §2.1 |

---

## 9. draw.io

`docs/DECISION_FLOW.drawio` is regenerated by
`scripts/gen_decision_flow_drawio.py` and now carries the gate layer, the
health state machine and the approval chain. `docs/v1.drawio` and
`docs/v1_tiers.drawio` remain the system and tier diagrams. All three
regenerate in place from the repository rather than being hand-edited.
