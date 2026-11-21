"""Download NOAA/NSIDC near-real-time CDR G10016 v4 daily SIC (Southern Hemisphere).

Truth data for the real-forecast hindcast (HANDOFF_TONIGHT slice 2).
The NRT archive keeps only ~3 months, so days roll off permanently —
run this promptly and never delete what it saved.

Usage: python scripts/download_nsidc_nrt.py [--start 2026-08-24] [--end today] [--out data/nsidc_nrt]

Files land as sic_pss25_YYYYMMDD_am2_icdr_v04r00.nc (~300 KB each).
The folder is gitignored; MANIFEST.sha256 records what was fetched.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import urllib.request
from datetime import date, timedelta
from pathlib import Path

BASE = "https://noaadata.apps.nsidc.org/NOAA/G10016_V4/south/daily"


def fetch_day(d: date, out_dir: Path) -> tuple[str, bool, str]:
    # shortcut: filename hardcodes the am2 (AMSR2) sensor tag, correct since
    # 2025-01-01; extend with the F17 tag if ever reaching further back.
    name = f"sic_pss25_{d:%Y%m%d}_am2_icdr_v04r00.nc"
    dest = out_dir / name
    if dest.exists() and dest.stat().st_size > 0:
        return name, True, "already have"
    url = f"{BASE}/{d.year}/{name}"
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            data = r.read()
    except Exception as e:  # noqa: BLE001 - record and move on, day may not be published yet
        return name, False, str(e)
    dest.write_bytes(data)
    return name, True, f"{len(data)} bytes"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2026-08-24")
    ap.add_argument("--end", default=str(date.today()))
    ap.add_argument("--out", type=Path, default=Path("data/nsidc_nrt"))
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    d = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)
    failed = []
    while d <= end:
        name, ok, msg = fetch_day(d, args.out)
        print(("ok  " if ok else "FAIL"), name, msg)
        if not ok:
            failed.append(name)
        d += timedelta(days=1)

    manifest = args.out / "MANIFEST.sha256"
    lines = []
    for f in sorted(args.out.glob("*.nc")):
        h = hashlib.sha256(f.read_bytes()).hexdigest()
        lines.append(f"{h}  {f.name}")
    manifest.write_text("\n".join(lines) + "\n")
    print(f"{len(lines)} files in manifest; {len(failed)} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
