# Backlog

One line per item: `[severity][area] what's wrong — pointer to full evidence`.

## HARD BLOCKERS — do these before the build starts, not during it

- [BLOCKER][data] **Start the daily CMEMS forecast harvest cron on day 1 of Phase 0.** The Stage B archive (real forecast cycles, ~5–15 MB/day corridor subset) cannot be back-filled; every day it does not run is permanently missing from the ADR-027 acceptance test, which is the strongest claim in the pitch — see docs/ML_ARCHITECTURE.md §1.3, docs/ARCHITECTURE.md §4 Phase 0.
- [BLOCKER][data] **Round-trip one real file from each of NSIDC gridded SIC (Earthdata `.netrc`), ERA5 (`cdsapi`), and CMEMS (`copernicusmarine.subset()`) in Phase 1, and measure CDS queue latency for a multi-decade request.** Zero bytes of training data have ever been downloaded; DATASET.md's "verified live" for these means HTTP 200 on a landing page. CDS queue latency for multi-decade requests is hours-to-days and appears nowhere in the schedule — see docs/WEAKNESS_ANALYSIS.md §9, docs/ARCHITECTURE.md §4 Phase 1.
- [BLOCKER][ml] **ADR-018 base-field gate.** By end of Phase 1 there must be (i) a real CMEMS file containing `siconc` at leads 1–10 over the corridor and (ii) a real GLORYS12 SIC file. If either fails, reinstate ADR-004's from-scratch U-Net as primary — the fallback is fully specified, but the decision must be made in Phase 1, not Phase 2 — see docs/ML_ARCHITECTURE.md §1.4.

## Open — ML / evaluation

- [critical][ml] RISKIEST ASSUMPTION — conformal coverage assumes exchangeability between calibration residuals and operations, and the post-2016 Antarctic regime is exactly the distribution shift that can break it. Must run the §1.6.5 gate (MIZ coverage at lead 5 in [85 %, 96 %], mean width <25 SIC-%, beats the disagreement proxy) on held-out 2022–24 **and** on real harvested forecast cycles before any demo — see docs/ML_ARCHITECTURE.md §6, §1.6.5.
- [major][ml] Stage A→B transfer is unproven: a GLORYS12 reanalysis background is not a true forecast background. The Stage B fine-tune + acceptance test is the check; failing it triggers the ADR-027 demotion — see docs/ML_ARCHITECTURE.md §1.3.
- [major][ml] Exact NSIDC south polar-stereographic grid dimensions at 25 km (~332×316) asserted from memory, not verified — confirm at first ingestion before sizing the network and the data volume estimate — see docs/ML_ARCHITECTURE.md §1.3.
- [minor][ml] Wagner exclusion radii (p90 leave-one-berg-out error at 24/48/72 h) are unmeasured; the 72 h cap and the 5 %-corridor-area auto-downgrade are committed, but the actual radii and the resulting area fraction must be measured in Phase 3 — see docs/ML_ARCHITECTURE.md §2.5.
- [minor][ml] GBM sanity bound `c_sanity` (p99 of training |residual correction|, est. ~10–25 km) is an estimate until the model is fitted; the frozen per-feature ranges and the two unit tests are specified — see docs/ML_ARCHITECTURE.md §2.3.

## Open — build / measurement

- [major][build] `thickness` and `density` LUT dataloaders MUST be wired into the mesh config or PolarRoute's ice-resistance speed adjustment silently no-ops and the ice physics is inert — verified in `SDA.model_speed()` source — see docs/ML_ARCHITECTURE.md §3.6.
- [major][build] Corridor mesh size (est. 0.5–1 MB gzip) and the **daily incremental delta** (completely unmeasured, and it is the load-bearing bandwidth number) must be measured in **Phase 1**, not Phase 4. Pre-committed response if they miss budget: coarsen the open-ocean mesh, then lengthen the full-refresh cadence — never move the budget — see docs/ARCHITECTURE.md §1.2.
- [minor][build] On-vessel re-correction payload (fresh corridor SIC observation, est. 5–15 KB gzipped) is unmeasured; if it does not fit the sub-50 KB budget, drop on-vessel re-inference and say pack-only — see docs/ML_ARCHITECTURE.md §7.2, docs/ARCHITECTURE.md §2.4b.
- [minor][build] Sync-budget CI test (50 KB daily delta / 1 MB full corridor refresh) specified in ADR-017 but not yet written — it is what converts "bandwidth-honest" from adjective to constraint.
- [minor][scope] Corridor AOI, vessel parameters and season must be a **config file**, not constants, so ADR-001's scoping survives "and for the Ross Sea, or a different ship?" — stated as a requirement in docs/ARCHITECTURE.md §2.2, not yet enforced by anything.
- [major][scope] GBM iceberg residual correction, NCPOR NPDC validation data, and Sentinel-1 SAR ice-edge extraction remain STRETCH goals — cut first if the schedule slips. **Exception:** if Phase 2 slips, the GBM is promoted to baseline so a trained model still ships — see docs/ARCHITECTURE.md §4.

## Open — data sourcing

- [major][data] No verified operational wave **forecast** source. ERA5 waves are reanalysis; GFS *wind* is verified but GFS-Wave was never checked. Either verify GFS-Wave or drop waves from the operational hazard claim — see docs/WEAKNESS_ANALYSIS.md §10.4, docs/DATASET.md §5.
- [minor][data] MV Vasiliy Golovnin's real published dimensions (beam, length, draft, ice class) not yet sourced; needed for the Golovnin `AbstractShip` subclass **and** for the ADR-026 depth margin (3 × draft) — see docs/ML_ARCHITECTURE.md §3.5.
- [minor][data] OSI SAF (EUMETSAT) actual data-centre/FTP download endpoint not test-fetched, only product landing pages — needs a free EUMETSAT account to verify the real download mechanism — see docs/DATASET.md §1.2.
- [minor][data] OSI SAF ice-drift product **OSI-405-d (62.5 km)** is a free observational drift field that could validate Wagner or feed the fusion layer; identified in COMPETITIVE_ANALYSIS.md §2 and never used since. Cheap win, currently ignored — see docs/WEAKNESS_ANALYSIS.md §10.6.
- [minor][data] NCPOR National Polar Data Center (`npdc.ncpor.res.in/.../searchRawData.jsp`) is a Struts-based in-page search form, not a REST API — needs interactive exploration before relying on it even as a validation source — see docs/DATASET.md §7.
- [minor][data] Sentinel-1 EW-mode revisit cadence over the Antarctic sea-ice zone is not verified for any specific corridor — check ESA's live observation-scenario maps before any algorithm assumes a SAR refresh interval — see docs/DATASET.md §2.1.
- [minor][data] Sofar Ocean Spotter buoy access/licensing not checked; DTU Space Antarctic sea-ice-thickness product catalogue not confirmed — see docs/COMPETITIVE_ANALYSIS.md §2.

## Open — demo honesty (recite these, do not claim otherwise)

- [minor][pitch] Pack **signing** has no key-management story — it is theater until there is one. Say "signed and versioned" only alongside how keys are held.
- [minor][pitch] Resumable Iridium delta sync will only ever be tested over throttled localhost. Say **"tested under emulated link constraints,"** never "tested over Iridium."

## Resolved by the revision-2 architecture pass (2026-08-31)

- [resolved][scope] **NCPOR-overlap check** — RESOLVED, greenfield confirmed. Manually checked `npdc.ncpor.res.in`, `ncpor.res.in` "Research Vessel Movements" (`/pages/view/248-research-vessel-moment`), and `data.ncpor.res.in`. Findings: (1) "Research Vessel Movements" is static archival text — PDF cruise schedules and historical reports for **ORV Sagar Kanya** (a different, general oceanographic vessel — not the Antarctic-charter MV Vasiliy Golovnin) — no live tracking, no forecasting, no route optimization. (2) `data.ncpor.res.in` offers only station observations (MAITRI/BHARATI AWS/DCWIS feeds, Black Carbon data) and generic dataset-catalog/plotting tools (Ferret, R) — no sea-ice forecast, no iceberg tracking, no routing tool anywhere. D5 stands as a genuine strength, not a risk.
- [resolved][ml] CMEMS positioning — RESOLVED: pivoted to bias-correcting CMEMS (ADR-018) **and** made raw packed CMEMS a build-blocking baseline (ADR-027).
- [resolved][ml] Impossible training spec ("AMSR2 1979–2018") — RESOLVED: NSIDC 25 km SSM/I–SSMIS CDR as the single observation product, 1993–2018/2019–21/2022–24, GLORYS12 background; AMSR2 reassigned to the fusion layer (ADR-019). Compute plan named with arithmetic (ADR-023).
- [resolved][ml] Scalar variance-inflation factor — RESOLVED: stratified split-conformal with a pre-committed pass/fail gate and a written demotion branch (ADR-020).
- [resolved][routing] Day-8-to-14 routing hole — RESOLVED: forecast-grade / CMEMS-direct / climatology-grade tiering with daily re-optimisation (ADR-022, ARCHITECTURE.md §2.4a).
- [resolved][ml] Corridor-blockading berg radii — RESOLVED: 72 h projection cap + 5 %-area auto-downgrade (ADR-025).
- [resolved][build] No QC layer / missing-source contradiction — RESOLVED: QC pass, single target grid, per-channel imputation, obs-only pack type (ADR-024).
- [resolved][ux] "Refuse to route" availability failure — RESOLVED: climatology-mode floor defined (ADR-022, ARCHITECTURE.md §2.5).
- [resolved][ml] GBM→Wagner trigger undefined — RESOLVED: frozen per-feature ranges + p99 correction cap, unit-tested (ADR-025).
- [resolved][build] Model weights absent from the sync story — RESOLVED: USB at port only, never over Iridium (ADR-023, ARCHITECTURE.md §2.4b).
- [resolved][pitch] "Pareto set" overclaim and D4's cherry-picked headline — RESOLVED: 12-run dominance-filtered sweep (ADR-021); D4 leads with the measured worst case.
- [resolved][data] GEBCO predicted-bathymetry disclosure — RESOLVED: TID grid ingested, provenance-conditional depth margin (ADR-026).
- [resolved][routing] PolarRoute iceberg-hazard handling — RESOLVED by source inspection: no native iceberg model, but `excluded_zones` is a native extension point, so no fork needed.
