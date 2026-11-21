#!/usr/bin/env bash
set -euo pipefail

# CMEMS daily forecast harvest — Dakshin
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
# (see docs/archive-hackathon/TEAM_GUIDE.md) so credentials are cached locally.

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
DATE_FROM_CLOCK=0
if [ -z "$CYCLE_DATE" ]; then
  DATE_FROM_CLOCK=1
  # CMEMS guarantees the day's forecast only by 12:00 UTC, and GitHub often
  # starts a scheduled run hours late. A run that starts after midnight UTC
  # but before 12:00 still sees YESTERDAY's forecast on the server, so that is
  # the cycle it must be filed under. Four cycles (2026-09-20, 10-11, 11-10,
  # 11-17) were archived as stale copies of the previous day before this rule
  # and the length check below existed. See data/cmems_forecast_archive/KNOWN_STALE.md.
  if [ "$(date -u +%H)" -lt 12 ]; then
    CYCLE_DATE="$(date -u -d 'yesterday' +%Y-%m-%d)"
  else
    CYCLE_DATE="$(date -u +%Y-%m-%d)"
  fi
fi
OUT_FILE="cmems_siconc_${CYCLE_DATE}.nc"

# A real cycle has this many daily steps: the cycle date plus nine forecast days.
EXPECTED_DAYS="${EXPECTED_DAYS:-10}"

# Tell the workflow which cycle this run was about and how it ended, so the
# verify step checks the right file instead of guessing from the clock.
report() {
  [ -n "${GITHUB_OUTPUT:-}" ] || return 0
  { echo "cycle=${CYCLE_DATE}"; echo "status=$1"; } >> "$GITHUB_OUTPUT"
}

# Everything this script says goes to the log file AND to stdout. Writing only
# to the log made a silent no-op look identical to a good run in the Actions
# console, which is most of why a merely-late job read as a broken one.
say() { echo "$(date -u -Iseconds) $*" | tee -a "$LOG_FILE"; }

# Surface ocean currents for the same cycle, box and 10-day window, from the
# same product's currents dataset. Dataset id and variable names (uo, vo in
# m s-1) confirmed live via `copernicusmarine.describe()` on 2026-11-21.
# Depth 0..1 m selects only the top model level (0.494 m).
CUR_DATASET_ID="cmems_mod_glo_phy-cur_anfc_0.083deg_P1D-m"
CUR_OUT_FILE="cmems_cur_${CYCLE_DATE}.nc"

# Runs after the ice cycle and must never fail the script: the workflow only
# commits when this script exits 0, and the runner is thrown away afterwards,
# so a currents error turning red would also lose the ice cycle saved above.
# Errors are therefore logged and returned, not raised (`set -e` does not
# apply inside a function called from an `if`, hence the explicit checks).
harvest_currents() {
  if [ -f "$ARCHIVE_DIR/$CUR_OUT_FILE" ]; then
    say "already have ${CUR_OUT_FILE}, skipping"
    return 0
  fi
  copernicusmarine subset \
    --dataset-id "$CUR_DATASET_ID" \
    --variable uo --variable vo \
    --minimum-depth 0 --maximum-depth 1 \
    --start-datetime "${CYCLE_DATE}T00:00:00" \
    --end-datetime "$(date -u -d "${CYCLE_DATE} +10 days" +%Y-%m-%dT00:00:00)" \
    --minimum-longitude "$MIN_LON" --maximum-longitude "$MAX_LON" \
    --minimum-latitude "$MIN_LAT" --maximum-latitude "$MAX_LAT" \
    --output-directory "$ARCHIVE_DIR" \
    --output-filename "$CUR_OUT_FILE" \
    2>&1 | tee -a "$LOG_FILE" || return 1
  [ -f "$ARCHIVE_DIR/$CUR_OUT_FILE" ] || return 1

  # Same stale-cycle rule as the ice file below.
  local n_days
  n_days="$(python3 -c 'import sys, netCDF4; print(len(netCDF4.Dataset(sys.argv[1]).dimensions["time"]))' \
            "$ARCHIVE_DIR/$CUR_OUT_FILE" 2>/dev/null || echo unknown)"
  if [ "$DATE_FROM_CLOCK" = 1 ] && [ "$n_days" != unknown ] && [ "$n_days" -ne "$EXPECTED_DAYS" ]; then
    rm -f "$ARCHIVE_DIR/$CUR_OUT_FILE"
    say "REJECTED ${CUR_OUT_FILE}: ${n_days} daily steps, expected ${EXPECTED_DAYS}. Nothing saved."
    return 0
  fi
  say "saved ${CUR_OUT_FILE} (${n_days} daily steps)"

  # uo/vo are not in compress_netcdf.py's int16 table, so they get its
  # lossless float32 deflate. Never fails the harvest, as for the ice file.
  if python3 "$ROOT_DIR/scripts/compress_netcdf.py" \
       "$ARCHIVE_DIR/$CUR_OUT_FILE" >> "$LOG_FILE" 2>&1; then
    echo "$(date -u -Iseconds) compressed ${CUR_OUT_FILE}" >> "$LOG_FILE"
  else
    echo "$(date -u -Iseconds) WARNING compression failed for ${CUR_OUT_FILE}, " \
         "keeping the uncompressed file" >> "$LOG_FILE"
  fi
}

run_currents() {
  harvest_currents || say "WARNING currents harvest failed for ${CYCLE_DATE}; the ice cycle is unaffected"
}

# Waves for the weather gate (slice 6): 3-hourly VHM0/VMDR from the wave
# forecast product, reduced to daily max before saving (reduce_wav_daily.py),
# same box and window. Same never-fail contract as the currents.
WAV_DATASET_ID="cmems_mod_glo_wav_anfc_0.083deg_PT3H-i"
WAV_OUT_FILE="cmems_wav_${CYCLE_DATE}.nc"

harvest_waves() {
  if [ -f "$ARCHIVE_DIR/$WAV_OUT_FILE" ]; then
    say "already have ${WAV_OUT_FILE}, skipping"
    return 0
  fi
  copernicusmarine subset \
    --dataset-id "$WAV_DATASET_ID" \
    --variable VHM0 --variable VMDR \
    --start-datetime "${CYCLE_DATE}T00:00:00" \
    --end-datetime "$(date -u -d "${CYCLE_DATE} +9 days" +%Y-%m-%dT21:00:00)" \
    --minimum-longitude "$MIN_LON" --maximum-longitude "$MAX_LON" \
    --minimum-latitude "$MIN_LAT" --maximum-latitude "$MAX_LAT" \
    --output-directory "$ARCHIVE_DIR" \
    --output-filename "$WAV_OUT_FILE" \
    2>&1 | tee -a "$LOG_FILE" || return 1
  [ -f "$ARCHIVE_DIR/$WAV_OUT_FILE" ] || return 1

  python3 "$ROOT_DIR/scripts/reduce_wav_daily.py" \
    "$ARCHIVE_DIR/$WAV_OUT_FILE" >> "$LOG_FILE" 2>&1 || {
      rm -f "$ARCHIVE_DIR/$WAV_OUT_FILE"
      say "REJECTED ${WAV_OUT_FILE}: daily reduction failed. Nothing saved."
      return 1
    }

  # Same stale-cycle rule as the ice file (10 daily steps after reduction).
  local n_days
  n_days="$(python3 -c 'import sys, netCDF4; print(len(netCDF4.Dataset(sys.argv[1]).dimensions["time"]))' \
            "$ARCHIVE_DIR/$WAV_OUT_FILE" 2>/dev/null || echo unknown)"
  if [ "$DATE_FROM_CLOCK" = 1 ] && [ "$n_days" != unknown ] && [ "$n_days" -ne "$EXPECTED_DAYS" ]; then
    rm -f "$ARCHIVE_DIR/$WAV_OUT_FILE"
    say "REJECTED ${WAV_OUT_FILE}: ${n_days} daily steps, expected ${EXPECTED_DAYS}. Nothing saved."
    return 0
  fi
  say "saved ${WAV_OUT_FILE} (${n_days} daily steps)"

  if python3 "$ROOT_DIR/scripts/compress_netcdf.py" \
       "$ARCHIVE_DIR/$WAV_OUT_FILE" >> "$LOG_FILE" 2>&1; then
    echo "$(date -u -Iseconds) compressed ${WAV_OUT_FILE}" >> "$LOG_FILE"
  else
    echo "$(date -u -Iseconds) WARNING compression failed for ${WAV_OUT_FILE}, " \
         "keeping the uncompressed file" >> "$LOG_FILE"
  fi
}

run_waves() {
  harvest_waves || say "WARNING waves harvest failed for ${CYCLE_DATE}; the ice cycle is unaffected"
}

if [ -f "$ARCHIVE_DIR/$OUT_FILE" ]; then
  say "already have ${OUT_FILE}, skipping"
  report already_have
  # The ice cycle may predate the currents/waves harvest, or a fetch may
  # have failed on the run that saved it, so still try those files.
  run_currents
  run_waves
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

# Check the file really is this cycle before keeping it. The request asks for
# cycle date .. cycle date + 10 days. If the server still holds yesterday's
# forecast the answer is one day short; if tomorrow's has already replaced it,
# one day long. Either way the data is a different forecast under this cycle's
# name, which is worse than a missing day, so drop it and let a later run retry.
# A date typed in by hand (workflow_dispatch) is a deliberate back-fill and is
# not checked.
N_DAYS="$(python3 -c 'import sys, netCDF4; print(len(netCDF4.Dataset(sys.argv[1]).dimensions["time"]))' \
          "$ARCHIVE_DIR/$OUT_FILE" 2>/dev/null || echo unknown)"
if [ "$DATE_FROM_CLOCK" = 1 ] && [ "$N_DAYS" != unknown ] && [ "$N_DAYS" -ne "$EXPECTED_DAYS" ]; then
  rm -f "$ARCHIVE_DIR/$OUT_FILE"
  say "REJECTED ${OUT_FILE}: ${N_DAYS} daily steps, expected ${EXPECTED_DAYS}." \
      "The server is not holding the ${CYCLE_DATE} forecast right now. Nothing saved; a later run will retry."
  report not_published
  exit 0
fi
[ "$N_DAYS" != unknown ] || say "WARNING could not count the time steps in ${OUT_FILE}; keeping it unchecked"

say "saved ${OUT_FILE} (${N_DAYS} daily steps)"
report saved

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

# Not reached when the ice cycle was REJECTED above: the currents and waves
# come from the same daily bulletin, so they would be stale too and a later
# run fetches all three.
run_currents
run_waves
