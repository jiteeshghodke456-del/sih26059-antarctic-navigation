#!/usr/bin/env bash
set -euo pipefail

# CMEMS daily forecast harvest — SIH26059
#
# Pulls today's corridor sea-ice forecast cycle (concentration, thickness,
# drift velocity) from GLOBAL_ANALYSISFORECAST_PHY_001_024 and archives it
# by cycle date. This archive is the Stage B training/acceptance-test data
# for the bias-correction model (docs/ML_ARCHITECTURE.md §1.3) and CANNOT
# be back-filled — every day this doesn't run is permanently missing.
#
# Dataset id and variable names confirmed live against the CMEMS catalog
# via `copernicusmarine.describe()` on 2026-08-31 (not guessed from docs).
#
# Requires: `copernicusmarine login` already run once on this machine
# (see docs/TEAM_GUIDE.md) so credentials are cached locally.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARCHIVE_DIR="${ARCHIVE_DIR:-$ROOT_DIR/data/cmems_forecast_archive}"
LOG_FILE="${LOG_FILE:-$ROOT_DIR/data/cmems_harvest.log}"

DATASET_ID="cmems_mod_glo_phy_anfc_0.083deg_P1D-m"
VARIABLES=(siconc sithick usi vsi)

# First-pass corridor box: Cape Town approach through Maitri/Bharati
# latitudes. Deliberately generous — refine once the team locks the exact
# AOI. Config-driven AOI is a stated architecture requirement
# (docs/ARCHITECTURE.md §2.2) — override via env vars, never hard-code
# a narrower box directly into this file.
MIN_LON="${MIN_LON:-0}"
MAX_LON="${MAX_LON:-80}"
MIN_LAT="${MIN_LAT:--78}"
MAX_LAT="${MAX_LAT:--55}"

mkdir -p "$ARCHIVE_DIR"
CYCLE_DATE="$(date -u +%Y-%m-%d)"
OUT_FILE="cmems_siconc_${CYCLE_DATE}.nc"

if [ -f "$ARCHIVE_DIR/$OUT_FILE" ]; then
  echo "$(date -u -Iseconds) already have ${OUT_FILE}, skipping" >> "$LOG_FILE"
  exit 0
fi

echo "$(date -u -Iseconds) harvesting cycle ${CYCLE_DATE}" >> "$LOG_FILE"

VAR_ARGS=()
for v in "${VARIABLES[@]}"; do
  VAR_ARGS+=(--variable "$v")
done

copernicusmarine subset \
  --dataset-id "$DATASET_ID" \
  "${VAR_ARGS[@]}" \
  --start-datetime "${CYCLE_DATE}T00:00:00" \
  --end-datetime "$(date -u -d "${CYCLE_DATE} +10 days" +%Y-%m-%dT00:00:00)" \
  --minimum-longitude "$MIN_LON" --maximum-longitude "$MAX_LON" \
  --minimum-latitude "$MIN_LAT" --maximum-latitude "$MAX_LAT" \
  --output-directory "$ARCHIVE_DIR" \
  --output-filename "$OUT_FILE" \
  --force-download \
  >> "$LOG_FILE" 2>&1

echo "$(date -u -Iseconds) saved ${OUT_FILE}" >> "$LOG_FILE"
