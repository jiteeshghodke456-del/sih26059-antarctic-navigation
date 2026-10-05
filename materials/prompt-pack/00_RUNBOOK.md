# RUNBOOK — ORDERED, GATED CLAUDE CODE EXECUTION

Run exactly one stage at a time.

## 00 — Execution control
Give Claude Code `00_EXECUTION_CONTROL.md` first. It establishes the gate behavior and final-demo exception.

## 01 — Research foundation
Run `01_RESEARCH_FOUNDATION.md`.
Claude must first ask whether this stage was already completed, then verify/audit or perform the research.
STOP.

## 02 — AI/ML + system architecture
Run `02_AIML_AND_SYSTEM_ARCHITECTURE.md`.
Claude must first check whether Stage 02 work already exists, then use Stage 01 evidence before proposing architectural changes.
STOP.

## 03 — Frontend UI + workflow
Run `03_FRONTEND_UI_AND_WORKFLOW.md`.
Claude must first check whether this stage already exists. Use the available frontend-design skill/workflow. Do not redesign scientific/business logic merely for appearance.
STOP.

## 04 — Future scope + deployment + startup
Run `04_FUTURE_SCOPE_DEPLOYMENT_AND_STARTUP.md`.
Claude must first check whether this stage already exists. Keep future capabilities isolated from the PS-26059 core.
STOP.

## 05 — Pre-demo validation + release audit
Run `05_PRE_DEMO_VALIDATION_AND_RELEASE_AUDIT.md`.
Claude must first check whether validation/audit work already exists. Attack the system skeptically and fix only justified blockers/gaps. This is the final quality gate BEFORE the demo reconstruction.
STOP.

## 06 — Recreate the SIH demo FINAL
Run `06_RECREATE_ISIH_DEMO_FINAL.md`.
This is the exception: Claude must NOT ask whether it was already completed. It must recreate the SIH demo from the verified current repository and all prior-stage outputs, using real data where available and explicit replay/simulation where unavoidable.

At the end, run the demo end-to-end and report the exact verified behavior.

## IMPORTANT

Never combine multiple stages into one Claude request.
Never let a later-stage artifact silently substitute for an earlier-stage decision.
Use `MASTER_SOURCE_UNTOUCHED.md` for lossless reference when a requirement appears missing or ambiguous.
