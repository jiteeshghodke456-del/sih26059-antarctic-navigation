# STAGE 00 — EXECUTION CONTROL / GATED CLAUDE CODE EXECUTION

Use these files sequentially. Do NOT give Claude Code all stages as one implementation request.

## EXECUTION ORDER

00_EXECUTION_CONTROL.md
→ 01_RESEARCH_FOUNDATION.md
→ 02_AIML_AND_SYSTEM_ARCHITECTURE.md
→ 03_FRONTEND_UI_AND_WORKFLOW.md
→ 04_FUTURE_SCOPE_DEPLOYMENT_AND_STARTUP.md
→ 05_PRE_DEMO_VALIDATION_AND_RELEASE_AUDIT.md
→ 06_RECREATE_ISIH_DEMO_FINAL.md

MASTER_SOURCE_UNTOUCHED.md is preserved as the lossless source record and is not an execution stage.

## GATE RULE — EVERY STAGE EXCEPT THE FINAL DEMO

At the START of each stage, Claude MUST:

1. Inspect the repository, current branch/Git state, tests, configuration, existing outputs, and relevant previous-stage handoffs.
2. Determine whether the current stage has already been completed before doing any implementation or research that duplicates it.
3. Ask the user explicitly:

   "Has this stage already been completed? I found: [evidence]. Choose:
   A) COMPLETED — verify/audit it and only fill genuine gaps.
   B) PARTIALLY COMPLETED — verify what exists and finish only the gaps.
   C) NOT COMPLETED — execute this stage."

4. Do not assume that a file, cache key, UI screen, config value, or documented claim proves completion. Verify behavior/evidence.
5. If the user says COMPLETED, do not rebuild the stage. Audit it against the stage requirements, record what passes/fails, and repair only genuine gaps.
6. If PARTIALLY COMPLETED, preserve working portions and work only on missing/incorrect pieces.
7. Never silently skip a stage because later-stage work appears to exist.
8. At the END of the stage, STOP and report:
   - verified work;
   - incomplete/unknown items;
   - changes made;
   - tests/evidence;
   - exact handoff into the next stage.

## FINAL DEMO EXCEPTION

For 06_RECREATE_ISIH_DEMO_FINAL.md:

- DO NOT ask whether the stage is already complete.
- ALWAYS recreate/rebuild the SIH demo from the verified repository state and all completed prior-stage outputs.
- Preserve useful working infrastructure where practical, but the demo flow itself must be reconstructed and tested deliberately.
- This is the final executable stage.

## GLOBAL RULES

1. The untouched master remains the source of truth.
2. No requirement, constraint, research objective, feature, safety rule, workflow step, data requirement, source, implementation expectation, or future-scope idea may be silently dropped.
3. Do not fabricate unavailable facts or operational data.
4. Distinguish VERIFIED / INFERRED / ASSUMED / HISTORICAL REPLAY / SIMULATED / FUTURE.
5. Preserve existing working behavior unless evidence justifies a targeted change.
6. Do not overwrite configuration, delete working code, replace architecture, or refactor broadly without evidence.
7. PS-26059 remains the center of gravity.
8. "Real data only" applies wherever real data are genuinely available. Historical replay or simulation must be explicitly labelled.
9. Do not call simulated capability live.
10. Do not mistake visual polish for scientific validity.
11. Every major AI/ML claim must have a defensible baseline and measurable validation.
12. Human approval remains mandatory for operational route decisions.
13. Hard safety constraints override optimization.
14. Uncertainty, data age, source disagreement, and provenance must remain visible.
15. The system must fail safely under stale data, communication loss, missing observations, and conflicting sources.
16. Do not continue automatically into the next stage after a STOP.

## FRONTEND DESIGN SKILL

For 03_FRONTEND_UI_AND_WORKFLOW.md, use the available frontend-design skill/workflow before redesigning or implementing UI. Treat it as a design-system and usability aid, not permission to turn the product into a futuristic dashboard.

The UI must remain professional bridge decision-support software: clean, information-dense, accurate, operationally legible, and sailor-oriented.

