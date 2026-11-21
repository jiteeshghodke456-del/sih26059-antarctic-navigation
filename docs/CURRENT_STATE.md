# Current state — night build 2026-11-21/22

If this session was cleared, read this file plus `docs/backlog.md` and
continue from "Next actions". Full task spec: the HANDOFF_TONIGHT text the
owner pasted (slices 1–11 + F1–F4); its hard rules still apply (real data
only; score once, report what comes out; push only to jiteeshghodke456-del).

## Done tonight (all committed and pushed to origin/main)

| Slice | What landed | Evidence |
|---|---|---|
| 1 (code) | `dakshin/model_io.py` checksum-verified loader + tests (skip until checkpoints) | `dakshin/test_model_io.py` |
| 2 (baselines) | NRT truth downloader (89 days), `build_channels_operational`, hindcast scorer. Raw CMEMS beats persistence at all leads | `dakshin/figures/realforecast_hindcast.json` |
| 4 | Currents in daily harvest + 82-day analysis backfill; CI run green | `data/cmems_cur_analysis/`, workflow run 44931056680 |
| 5 | RK2 berg forecast + USNIC validation: **persistence wins, giants are grounded**, measured 4.35 km/day error rate | `dakshin/figures/berg_hindcast.json` |
| 6 | Waves in harvest (daily max), ECMWF wind harvest (daily, CC BY 4.0), `RealWorld`, weather gate from real data (FAILs at 4.77 m waves on 2026-11-21), real route run: **Bharati approach closed by spring ice, closest 50.6 km** | `dakshin/figures/real_route.json` |
| 7 | IBCSO v2 subset (CC-BY-4.0), min-depth block in both routers, chart gate never PASS without ENC | `data/bathymetry/`, agent commit ce236c7 |
| 8 | Hardened NMEA AIS decoder (pyais) + traffic gate bands | `dakshin/ais_feed.py` |
| F1 | Resolution study: RMSE blind to resolution (double penalty), IIEE shows 1° losing the edge, 1/12°≈1/4° | `docs/RESOLUTION_STUDY.md` |
| F3 | Coarse currents beat eddy-resolving on grounded bergs → grounding detection is the binding constraint | `dakshin/figures/berg_resolution.json` |

Test suite: 186 passed, 7 skipped (baseline at session start: 159; the 7
skips are model_io + pre-existing, they un-skip when checkpoints land).

## In flight

- **Kaggle re-run** of the training notebook: kernel
  `jiteeshghodke/notebookd39fdf7959` version 6, QUEUED for the free T4 pool.
  History: the original 2026-08-31 checkpoints were never in Kaggle's output
  store, and the saved notebook's training-loop cell was typed *markdown*, so
  batch runs did nothing. v6 fixes the cell type; CMEMS credentials come from
  the private dataset `jiteeshghodke/cmems-creds` (CLI batch runs cannot read
  Kaggle Secrets). A background watcher polls every 5 min.
- **When COMPLETE:** run `KAGGLE_API_TOKEN=<token> bash scripts/pull_checkpoints.sh`,
  then write the "Real-forecast hindcast (2026)" section into the results doc
  with the numbers as they come out (including any lead where the U-Net
  loses), update `docs/RESOLUTION_STUDY.md`'s pending U-Net rows, commit the
  checkpoints, create Release `model-v0.1`.
- **If it ERRORs again:** `kaggle kernels logs jiteeshghodke/notebookd39fdf7959`,
  fix only what the log names, push v7 unchanged otherwise.

## Owner's end-of-build asks (do after the model work, in this order)

1. **De-hackathon rename**: strip every SIH/ISIH mention — package dir,
   doc filenames (ISIH_*.md), README, text references. Keep the Kaggle
   checkpoint artifact names (`isih_prototype_lead*.pt`) for checksum
   integrity; note the mapping. GitHub repo rename = owner's call, flag only.
2. **Study doc** written by Haiku and Sonnet subagents: exhaustive — project
   evolution stage by stage, research findings, innovations, architecture,
   file-by-file map, data flow, how to run every data operation, physics
   (WDE17 drift, double penalty, IIEE, POLARIS), papers used. The owner will
   feed it to another AI to study from, so density beats polish.
3. **README.md rewrite** for a physical-oceanography professor (NEMO/ANHA
   background): what this is, the honest results, data sources + licences,
   how to reproduce every number.

## Secrets (never commit)

Kaggle token + CMEMS login are cached in `~/.kaggle` / `~/.copernicusmarine`
in the sandbox; aisstream.io key at `~/.sih-secrets/aisstream.key`
(unused so far — shore AIS is empty in the Southern Ocean anyway).
