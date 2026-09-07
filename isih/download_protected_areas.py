"""Download the Antarctic Treaty Secretariat's protected-areas shapefile.

This is the authoritative source for Antarctic Specially Protected Areas
(ASPA) and Antarctic Specially Managed Areas (ASMA). It is published by the
Treaty Secretariat itself, which is the body that holds the Measures that
designate them — so it is the register, not a redistribution of one.

No authentication required (verified 2026-09-07: HTTP 200, 1,972,818 bytes).

Why this source and not CCAMLR's GeoServer: CCAMLR carries `gis:aspa` and
`gis:asma` layers, but they are a *partial marine subset* — 12 ASPA + 2 ASMA
features against the Secretariat's 77 + 6. Using CCAMLR would silently drop
ASPA 174 Stornes, which is 1.9 km from Bharati. The Secretariat shapefile is
authoritative; CCAMLR's is a convenience extract for a different purpose.

CRS is EPSG:3031 (WGS 84 Antarctic Polar Stereographic, standard parallel
-71), stated in the .prj — not assumed.

Usage:
    python isih/download_protected_areas.py
"""

from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

# The Secretariat versions this file by year. 2024 is the current edition as
# of 2026-09-07; when a newer one appears the old URL keeps working, so
# bumping this is a deliberate act, not an automatic one — a protected-area
# boundary changing under a cached route is exactly the kind of silent shift
# docs/backlog.md's provenance rules exist to prevent.
URL = "https://documents.ats.aq/gis/apa_shape_2024.zip"
EDITION = "2024"

DEFAULT_OUT = Path(__file__).parent / "data" / "protected_areas"

# Sanity floor. The real archive is ~1.9 MB; anything much smaller is an
# error page or a truncated transfer, and a truncated shapefile fails in
# confusing ways much later.
MIN_BYTES = 1_000_000


def download(out_dir: Path = DEFAULT_OUT, timeout: int = 120) -> Path:
    """Fetch and unpack the shapefile. Returns the path to the .shp."""
    out_dir.mkdir(parents=True, exist_ok=True)
    archive = out_dir / f"apa_shape_{EDITION}.zip"

    if not archive.exists():
        print(f"fetching {URL}")
        try:
            with urllib.request.urlopen(URL, timeout=timeout) as resp:
                payload = resp.read()
        except urllib.error.URLError as exc:
            raise SystemExit(f"could not reach the Treaty Secretariat: {exc}")

        if len(payload) < MIN_BYTES:
            raise SystemExit(
                f"{URL} returned only {len(payload)} bytes — expected "
                f">{MIN_BYTES}. Treating as a failed download rather than "
                f"unpacking a truncated shapefile."
            )
        archive.write_bytes(payload)
        print(f"saved {archive} ({len(payload):,} bytes)")
    else:
        print(f"already have {archive}")

    with zipfile.ZipFile(archive) as zf:
        zf.extractall(out_dir)

    shp = next(out_dir.glob("*.shp"), None)
    if shp is None:
        raise SystemExit(f"no .shp found in {archive}")

    # A shapefile is a file *set*; .shp alone is unusable. Fail here rather
    # than at first read.
    for ext in (".dbf", ".shx", ".prj"):
        if not shp.with_suffix(ext).exists():
            raise SystemExit(f"incomplete shapefile: {shp.with_suffix(ext)} missing")

    print(f"ready: {shp}")
    return shp


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args(argv)
    download(args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
