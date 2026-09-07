# Quality gate — the definition of done

These requirements existed in the master prompt and were **lost when it was
compressed into the six-stage bundle** (`docs/MASTER_AUDIT.md` §A.4). They are
reinstated here as a checklist rather than prose, because a requirement that
lives only in a document is exactly what got dropped last time.

Three things live here:

1. the **core technical milestone** — what "done" means for PS-26059;
2. the **implementation quality gate** — ten questions asked before any feature;
3. the **scope discipline** — the rule that stops the project sprawling.

---

## 0. The operating rule (master §49 — lost, reinstated)

> When there is any doubt whether a detail matters, **assume that it matters.**
>
> When simplifying or consolidating requirements, preserve the underlying
> information, constraints, intent, examples, and prohibitions.
>
> Do not delete information merely because it is repetitive, unusual,
> aspirational, or difficult to implement. Determine whether it adds a separate
> constraint or expectation first.
>
> Where two statements appear to conflict, **surface the conflict and research
> it** rather than silently dropping one.
>
> Where the source contains a factual claim that requires current verification,
> verify it before using it as an implementation fact.

This is the rule whose absence allowed the other seven losses. It is listed
first deliberately.

---

## 1. Core technical milestone (master line 5112 — lost, reinstated)

> Before spending substantial implementation effort on peripheral features,
> produce a working end-to-end demonstration of this pipeline.
> **This is the primary technical milestone.**
> **Do not consider the project technically mature merely because the GUI is
> polished.**

| # | Stage | Status |
|---|---|---|
| 1 | Real / authoritative data | **done** — NSIDC CDR, 1,096 daily files (Measured) |
| 2 | Data provenance | **done** — every layer carries source and date |
| 3 | Sea-ice / iceberg / weather processing | **partial** — ice done; icebergs and weather are the open items |
| 4 | Forecast or trajectory output | **partial** — SIC correction trained; iceberg trajectory not produced |
| 5 | Vessel-aware constraints | **done** — vessel-modelled mesh, but see the identical-two-ship finding |
| 6 | Risk / exposure assessment | **partial** — ice exposure only; four risk kinds not separated in the UI |
| 7 | 2–3 candidate routes | **done** — corridors A/B/C (Measured) |
| 8 | Safety / ETA / fuel-energy comparison | **partial** — fuel and time are collinear, so the comparison is degenerate |
| 9 | Uncertainty | **partial** — gate coverage and a data-derived MARGINAL band; no ensemble |
| 10 | Explainable recommendation | **done** — gates name their reasons and their blockers |
| 11 | Human approval | **done** — attributed, versioned |
| 12 | Route version | **done** — `supersedes` chain |
| 13 | Monitoring / reassessment | **done** — divergence detection distinguishes "assumption changed" from "new data arrived" |

**Verdict: the pipeline runs end to end, with stages 3, 4, 6, 8 and 9 partial.**
The GUI being good is not evidence about any of these rows.

---

## 2. Implementation quality gate (master line 5134 — lost, reinstated)

Ask these **before** moving to the next major feature. Order matters.

1. Does the current feature work with real data where real data are available?
2. Is its source / provenance known?
3. Is its freshness visible?
4. Is its uncertainty known?
5. Is there an appropriate baseline?
6. Is it validated?
7. Does it improve an actual decision?
8. Does it fail safely?
9. Can the captain understand it?
10. Does it remain compatible with the existing architecture?

> **If the answer is no, fix the underlying capability before adding decorative
> complexity.**

### Applying it to what exists today

| Feature | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Sea-ice raster | ✅ | ✅ | ⚠️ | ⚠️ | n/a | ✅ | ✅ | ✅ | ✅ | ✅ | pass |
| Route solve | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | pass, no uncertainty |
| Decision gates | ✅ | ✅ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **strongest component** |
| SIC correction model | ✅ | ✅ | n/a | ⚠️ | ✅ | ⚠️ | ✅ | ✅ | ⚠️ | ✅ | leakage ablation outstanding |
| Iceberg drift | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | n/a | ❌ | ✅ | **gate fails — fix before shipping the claim** |
| Alternatives A/B/C | ✅ | ✅ | ✅ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | pass |
| Fuel comparison | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ⚠️ | ✅ | **degenerate — collinear with time** |

The iceberg row is the clearest instance of the rule this gate exists to enforce:
the physics is excellent and the *capability* is absent, so no amount of UI work
on it would count as progress.

---

## 3. Scope discipline (master line 4590 — lost, reinstated)

> The PS-26059 CORE is:
> 1. Antarctic sea-ice forecasting;
> 2. Antarctic iceberg trajectory prediction;
> 3. identification of safer and fuel/energy-efficient navigation routes.
>
> **Do NOT allow the project to become an "Antarctic operating system" before the
> PS-26059 core is technically demonstrated.**

Required implementation priority:

```
PS-26059 CORE
  → sea-ice forecasting
  → iceberg trajectory prediction
  → vessel-aware route assessment
  → safe/fuel-efficient candidate corridors
  → uncertainty-aware decision support
  → professional map/decision workspace
  → measurable validation
```

Only after that pipeline works should effort move to emergency coordination, LLM
assistance, Baymax Mode, station coordination, or startup-platform features.

**The litmus test every feature must answer:**

> "What real operational decision does this feature improve?"

> Do not add complexity merely because it looks impressive in a demonstration.

### Standing consequence for this repository

Of the three core capabilities, **sea-ice forecasting** is demonstrated and
**route identification** is demonstrated; **iceberg trajectory prediction is
not**. It is one third of the problem statement's own title. Any future work that
adds a Tier-3 feature ahead of it is a violation of this section, and the
submitted deck already claims it — which makes it the single highest-priority
item in the project.
