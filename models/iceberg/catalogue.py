"""Real Antarctic iceberg positions from the US National Ice Center.

USNIC names, tracks and publishes every Antarctic iceberg that is "20 sqNM or
greater, or 10 NM on its longest axis" -- so roughly 18.5 km on the long axis
and up. The feed is free, needs no account, and updates weekly.

    https://usicecenter.gov/Products/AntarcIcebergs
    CSV: https://usicecenter.gov/File/DownloadCurrent?pId=134

Two properties of this catalogue shape everything downstream.

**It is giant bergs only, by construction.** The size floor puts every tracked
berg in the regime where WDE17's wind term collapses and v_iceberg ~ v_current
(see drift.relative_wind_forcing and models/iceberg/test_drift.py). So the
accuracy of a trajectory forecast for this catalogue is inherited almost
entirely from the ocean-current field, not from the drift physics. Growlers and
bergy bits -- the classic hull-holing hazard -- are three and a half orders of
magnitude below this floor and appear in no satellite product anywhere. This
module cannot and must not be presented as growler warning.

**The live CSV is a current snapshot, not a time series.** It holds this
week's positions only. Trajectories come from the USNIC product archive, which
keeps every weekly issue back to 2014-11-07: see fetch_usnic_archive. Nothing
needs harvesting on a schedule; a missed week can always be fetched later.

No synthetic bergs are ever generated. If the feed is unreachable the loader
raises; it does not invent positions.
"""

from __future__ import annotations

import io
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd

USNIC_CSV_URL = "https://usicecenter.gov/File/DownloadCurrent?pId=134"
USNIC_PRODUCT_PAGE = "https://usicecenter.gov/Products/AntarcIcebergs"
USNIC_SITE = "https://usicecenter.gov"
USNIC_ARCHIVE_SEARCH = USNIC_SITE + "/Products/DisplaySearchResults"

# One archive hit: the download link and the publisher's own file name, which
# carries the issue date. Anything not matching this exact shape is ignored, so
# a file name out of the HTML can never point outside the archive folder.
_ARCHIVE_LINK = re.compile(
    r'href="(/File/DownloadArchive\?prd=\d+)"[^>]*>(AntarcticIcebergs_\d{8}\.csv)<')

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "icebergs"

NAUTICAL_MILE_M = 1852.0

# USNIC's published tracking floor, in nautical miles.
TRACKING_FLOOR_LONG_AXIS_NM = 10.0
TRACKING_FLOOR_AREA_SQNM = 20.0


def fetch_usnic(cache_dir: Path | None = None, timeout: int = 60,
                refresh: bool = False) -> Path:
    """Download today's USNIC Antarctic iceberg CSV. Returns the file path.

    Cached per calendar day, because the feed is weekly and re-downloading adds
    nothing. Raises on failure rather than degrading to stale or invented data.
    """
    cache_dir = cache_dir or DATA_DIR
    cache_dir.mkdir(parents=True, exist_ok=True)
    out = cache_dir / f"usnic_antarctic_{date.today():%Y%m%d}.csv"

    if out.exists() and not refresh:
        return out

    request = Request(USNIC_CSV_URL, headers={"User-Agent": "SIH26059/1.0"})
    with urlopen(request, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError(
                f"USNIC returned HTTP {response.status} for {USNIC_CSV_URL}")
        payload = response.read()

    if not payload.strip():
        raise RuntimeError("USNIC returned an empty body")
    out.write_bytes(payload)
    return out


def _archive_links(html: str) -> list[tuple[str, str]]:
    """(file name, download URL) for every CSV issue in an archive result page."""
    return [(name, USNIC_SITE + href) for href, name in _ARCHIVE_LINK.findall(html)]


def fetch_usnic_archive(start: date, end: date, archive_dir: Path | None = None,
                        timeout: int = 60) -> list[Path]:
    """Download every weekly issue published between two dates. Returns new files.

    Files keep USNIC's own names (AntarcticIcebergs_YYYYMMDD.csv, the issue
    date) under data/icebergs/archive/. Issues already on disk are skipped.
    Each download must parse with load_usnic before it is kept.
    """
    archive_dir = archive_dir or DATA_DIR / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": "iceberg-archive-fetch/1.0"}

    form = urlencode({"searchText": "IcebergProducts",
                      "searchProduct": "Antarctic Icebergs CSV",
                      "startDate": f"{start:%m/%d/%Y}",
                      "endDate": f"{end:%m/%d/%Y}"}).encode()
    with urlopen(Request(USNIC_ARCHIVE_SEARCH, data=form, headers=headers),
                 timeout=timeout) as response:
        links = _archive_links(response.read().decode("utf-8", "replace"))
    if not links:
        raise RuntimeError(f"USNIC archive listed no CSV issues for {start} to {end}")

    saved = []
    for name, url in sorted(links):
        out = archive_dir / name
        if out.exists():
            continue
        with urlopen(Request(url, headers=headers), timeout=timeout) as response:
            out.write_bytes(response.read())
        try:
            load_usnic(out)
        except Exception:
            out.unlink()
            raise
        saved.append(out)
    return saved


def load_usnic(path: Path | str | None = None) -> pd.DataFrame:
    """Parse a USNIC CSV into SI units, ready for the drift model.

    Returned columns:
        name          iceberg designation, e.g. "A23A"
        lat, lon      degrees, latitude negative in the south
        length_m      longest axis, metres
        width_m       shortest axis, metres
        area_km2      as published
        observed      date of the position fix
        harmonic_m    S = LW/(L+W), the length scale WDE17 actually uses

    The file is served with a UTF-8 BOM, so the first column name parses as
    "\\ufeffIceberg" unless read as utf-8-sig -- which silently produces a
    KeyError on 'Iceberg' much later.
    """
    if path is None:
        path = fetch_usnic()
    raw = Path(path).read_bytes().decode("utf-8-sig")
    frame = pd.read_csv(io.StringIO(raw))

    frame.columns = [c.strip() for c in frame.columns]
    required = {"Iceberg", "Length (NM)", "Width (NM)", "Latitude",
                "Longitude", "Area (sqKM)", "Last Update"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"USNIC schema changed; missing columns: {missing}")

    out = pd.DataFrame({
        "name": frame["Iceberg"].astype(str).str.strip(),
        "lat": pd.to_numeric(frame["Latitude"], errors="coerce"),
        "lon": pd.to_numeric(frame["Longitude"], errors="coerce"),
        "length_m": pd.to_numeric(frame["Length (NM)"],
                                  errors="coerce") * NAUTICAL_MILE_M,
        "width_m": pd.to_numeric(frame["Width (NM)"],
                                 errors="coerce") * NAUTICAL_MILE_M,
        "area_km2": pd.to_numeric(frame["Area (sqKM)"], errors="coerce"),
        "observed": pd.to_datetime(frame["Last Update"], format="%m/%d/%Y",
                                   errors="coerce"),
    })

    # A zero or missing dimension would divide by zero in the harmonic mean and
    # produce an infinite Lambda, i.e. a fictitious wind-dominated berg.
    out = out.dropna(subset=["lat", "lon", "length_m", "width_m"])
    out = out[(out.length_m > 0) & (out.width_m > 0)]

    # USNIC publishes longest x shortest, but do not assume the ordering holds.
    long_axis = np.maximum(out.length_m, out.width_m)
    short_axis = np.minimum(out.length_m, out.width_m)
    out["length_m"], out["width_m"] = long_axis, short_axis

    out["harmonic_m"] = out.length_m * out.width_m / (out.length_m + out.width_m)

    if not out.lat.between(-90, 0).all():
        raise ValueError("USNIC Antarctic feed contains non-southern latitudes")

    return out.sort_values("area_km2", ascending=False).reset_index(drop=True)


def summarise(frame: pd.DataFrame) -> dict:
    """Headline numbers for a catalogue snapshot, for logging and the deck."""
    return {
        "icebergs": int(len(frame)),
        "observed": (None if frame.observed.isna().all()
                     else str(frame.observed.max().date())),
        "largest": frame.loc[frame.area_km2.idxmax(), "name"],
        "largest_area_km2": float(frame.area_km2.max()),
        "smallest_area_km2": float(frame.area_km2.min()),
        "median_long_axis_km": float(frame.length_m.median() / 1000.0),
        "shortest_long_axis_km": float(frame.length_m.min() / 1000.0),
        "lat_range": [float(frame.lat.min()), float(frame.lat.max())],
        "lon_range": [float(frame.lon.min()), float(frame.lon.max())],
    }


if __name__ == "__main__":
    # python models/iceberg/catalogue.py 2026-08-20 2026-11-19
    import sys

    for path in fetch_usnic_archive(date.fromisoformat(sys.argv[1]),
                                    date.fromisoformat(sys.argv[2])):
        print("saved", path)
