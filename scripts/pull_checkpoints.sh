#!/usr/bin/env bash
set -euo pipefail
# Slice 1 finish: pull the 4 trained checkpoints from the Kaggle re-run,
# checksum them, and run the full scoring that was waiting on them.
# Requires KAGGLE_API_TOKEN in the environment and the kernel COMPLETE.
#
# Usage: KAGGLE_API_TOKEN=... bash scripts/pull_checkpoints.sh
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CKPT_DIR="$ROOT_DIR/models/sic_correction/checkpoints"
KERNEL="jiteeshghodke/notebookd39fdf7959"
PY="${PY:-/home/agent/.venvs/sih-work/bin/python}"

mkdir -p "$CKPT_DIR"
kaggle kernels output "$KERNEL" -p "$CKPT_DIR"
ls -la "$CKPT_DIR"

cd "$CKPT_DIR"
for lead in 1 3 5 7; do
  [ -f "isih_prototype_lead${lead}.pt" ] || { echo "MISSING lead ${lead}"; exit 1; }
done
sha256sum isih_prototype_lead{1,3,5,7}.pt > SHA256SUMS
cat SHA256SUMS

cd "$ROOT_DIR"
"$PY" -m pytest isih/test_model_io.py -q          # slice 1 check, no longer skipped
"$PY" scripts/realforecast_hindcast.py            # slice 2 with the model
"$PY" scripts/resolution_study.py                 # F1 with the model
echo "DONE — now update the results docs with the numbers as they came out,"
echo "commit the checkpoints (~8 MB each), and attach them to a GitHub"
echo "Release model-v0.1: gh release create model-v0.1 models/sic_correction/checkpoints/*.pt -t 'Prototype checkpoints (re-run 2026-11-21)'"
