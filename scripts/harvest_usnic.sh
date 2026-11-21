#!/usr/bin/env bash
set -euo pipefail
# Weekly USNIC Antarctic iceberg list -> data/icebergs/archive/ (slice 5).
# Named by the newest "Last Update" in the file, matching the existing archive.
# Idempotent: re-running on the same issue overwrites the identical file.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARCHIVE_DIR="$ROOT_DIR/data/icebergs/archive"
TMP="$(mktemp)"
curl -fsSL "https://usicecenter.gov/File/DownloadCurrent?pId=134" -o "$TMP"
head -1 "$TMP" | grep -q "Iceberg" || { echo "unexpected USNIC payload"; exit 1; }
ISSUE=$(python3 - "$TMP" <<'PY'
import csv, datetime, sys
with open(sys.argv[1], encoding="utf-8-sig") as f:
    dates = [datetime.datetime.strptime(r["Last Update"], "%m/%d/%Y")
             for r in csv.DictReader(f) if r.get("Last Update")]
print(max(dates).strftime("%Y%m%d"))
PY
)
mkdir -p "$ARCHIVE_DIR"
mv "$TMP" "$ARCHIVE_DIR/AntarcticIcebergs_$ISSUE.csv"
echo "archived AntarcticIcebergs_$ISSUE.csv"
