"""Download NOAA/NSIDC CDR sea-ice concentration — the ISIH prototype's truth field.

This is what the model is corrected *toward*: what the satellite actually
observed. No authentication required (verified 2026-08-31).

Grid: 25 km south polar stereographic, 332 x 316 — the dimensions
ML_ARCHITECTURE.md §1.3 previously only assumed.

Usage:
    python isih/download_nsidc.py --start-year 2018 --end-year 2020
"""

import argparse
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from pathlib import Path

BASE_URL = "https://noaadata.apps.nsidc.org/NOAA/G02202_V6/south/daily"
# Passive-microwave platform changes over the record; the filename carries it.
# F17 covers the recent era. Older years use different sensors, so the
# downloader discovers the real filename per-year from the directory listing
# rather than assuming one.
DEFAULT_OUT = Path(__file__).parent / "data" / "nsidc_sic"


def list_year_files(year: int, timeout: int = 60) -> dict[str, str]:
    """Return {YYYYMMDD: filename} for a year, read from the real listing."""
    url = f"{BASE_URL}/{year}/"
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    files: dict[str, str] = {}
    for chunk in html.split('href="')[1:]:
        name = chunk.split('"')[0]
        if not name.endswith(".nc"):
            continue
        # sic_pss25_YYYYMMDD_<platform>_v06r00.nc
        parts = name.split("_")
        for part in parts:
            if len(part) == 8 and part.isdigit():
                files[part] = name
                break
    return files


def download_one(year: int, filename: str, out_dir: Path, retries: int = 3) -> tuple[str, bool, str]:
    dest = out_dir / filename
    if dest.exists() and dest.stat().st_size > 1000:
        return filename, True, "cached"

    url = f"{BASE_URL}/{year}/{filename}"
    for attempt in range(retries):
        try:
            tmp = dest.with_suffix(".part")
            with urllib.request.urlopen(url, timeout=120) as resp, open(tmp, "wb") as fh:
                fh.write(resp.read())
            if tmp.stat().st_size < 1000:
                tmp.unlink(missing_ok=True)
                raise ValueError(f"suspiciously small file ({tmp.stat().st_size}B)")
            tmp.rename(dest)
            return filename, True, "downloaded"
        except (urllib.error.URLError, OSError, ValueError) as exc:
            if attempt == retries - 1:
                return filename, False, str(exc)
            time.sleep(2 ** attempt)
    return filename, False, "exhausted retries"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--start-year", type=int, default=2018)
    ap.add_argument("--end-year", type=int, default=2020)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--workers", type=int, default=6,
                    help="parallel downloads; keep modest, this is a public server")
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)

    targets: list[tuple[int, str]] = []
    for year in range(args.start_year, args.end_year + 1):
        try:
            year_files = list_year_files(year)
        except Exception as exc:
            print(f"[{year}] FAILED to list: {exc}", flush=True)
            continue
        print(f"[{year}] {len(year_files)} files available", flush=True)
        targets.extend((year, name) for name in sorted(year_files.values()))

    if not targets:
        print("No files found — aborting rather than reporting success.", file=sys.stderr)
        return 1

    print(f"\nDownloading {len(targets)} files to {args.out}", flush=True)
    ok = failed = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(download_one, y, n, args.out): n for y, n in targets}
        for i, fut in enumerate(as_completed(futures), 1):
            name, success, note = fut.result()
            if success:
                ok += 1
            else:
                failed += 1
                print(f"  FAIL {name}: {note}", flush=True)
            if i % 100 == 0 or i == len(targets):
                print(f"  {i}/{len(targets)}  ok={ok} failed={failed}", flush=True)

    total_mb = sum(f.stat().st_size for f in args.out.glob("*.nc")) / 1e6
    print(f"\nDone. {ok} ok, {failed} failed. {total_mb:.0f} MB in {args.out}")
    return 1 if failed and ok == 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
