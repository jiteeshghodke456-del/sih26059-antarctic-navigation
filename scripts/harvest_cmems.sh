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

# CYCLE_DATE may be supplied by the workflow_dispatch input so a missed day
# can be chased manually. Caveat worth knowing before you rely on it: the
# dataset still serves the *analysis* for a past date, but the forecast as it
# was issued on that date is gone. A back-filled cycle is therefore not a
# substitute for a cycle captured on the day.
CYCLE_DATE="${CYCLE_DATE:-}"
[ -n "$CYCLE_DATE" ] || CYCLE_DATE="$(date -u +%Y-%m-%d)"
OUT_FILE="cmems_siconc_${CYCLE_DATE}.nc"

# Everything this script says goes to the log file AND to stdout. Writing only
# to the log made a silent no-op look identical to a good run in the Actions
# console, which is most of why a merely-late job read as a broken one.
say() { echo "$(date -u -Iseconds) $*" | tee -a "$LOG_FILE"; }

if [ -f "$ARCHIVE_DIR/$OUT_FILE" ]; then
  say "already have ${OUT_FILE}, skipping"
  exit 0
fi

say "harvesting cycle ${CYCLE_DATE}"

VAR_ARGS=()
for v in "${VARIABLES[@]}"; do
  VAR_ARGS+=(--variable "$v")
done

# `--force-download` was removed: the CLI deprecated it and warns on every run.
# Overwrite protection is already handled by the "already have" check above.
copernicusmarine subset \
  --dataset-id "$DATASET_ID" \
  "${VAR_ARGS[@]}" \
  --start-datetime "${CYCLE_DATE}T00:00:00" \
  --end-datetime "$(date -u -d "${CYCLE_DATE} +10 days" +%Y-%m-%dT00:00:00)" \
  --minimum-longitude "$MIN_LON" --maximum-longitude "$MAX_LON" \
  --minimum-latitude "$MIN_LAT" --maximum-latitude "$MAX_LAT" \
  --output-directory "$ARCHIVE_DIR" \
  --output-filename "$OUT_FILE" \
  2>&1 | tee -a "$LOG_FILE"

say "saved ${OUT_FILE}"

# Compress before this ever reaches git. `copernicusmarine subset` writes
# NetCDF with no compression at all (verified: zlib=False, complevel=0,
# contiguous), which is 42.6 MB per day of raw float32 committed permanently
# to history -- about 4.3 GB by December. Compression takes that to ~5 MB with
# a quantisation error three orders of magnitude below the precision anything
# downstream uses. See scripts/compress_netcdf.py for the measurements.
#
# This step must never fail the harvest: an uncompressed archive file is far
# better than a missing one, because the cycle cannot be re-fetched later.
if python3 "$ROOT_DIR/scripts/compress_netcdf.py" \
     "$ARCHIVE_DIR/$OUT_FILE" >> "$LOG_FILE" 2>&1; then
  echo "$(date -u -Iseconds) compressed ${OUT_FILE}" >> "$LOG_FILE"
else
  echo "$(date -u -Iseconds) WARNING compression failed for ${OUT_FILE}, " \
       "keeping the uncompressed file" >> "$LOG_FILE"
fi
