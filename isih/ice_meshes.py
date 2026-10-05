"""Daily vessel-performance meshes built from ice a satellite really measured.

The route figure builds one mesh for one day. Any experiment about *forecasting*
needs many days, so this module turns "give me the navigable world on 4 Dec
2019" into a cached call.

A vessel mesh is the environmental mesh (ice, thickness, density) after
PolarRoute's vessel performance model has been applied, so every cell carries:

    speed          list of 8 headings, km/hr, already derated for ice
    inaccessible   True if this vessel may not enter (ice limit, land, depth)
    SIC            sea-ice concentration in percent

Building one costs a few seconds, so results are cached to disk as JSON. The
cache key is the date plus the vessel, because changing the ship changes which
cells are passable.

Vessel is MV Vasiliy Golovnin, the ship India actually charters (43rd ISEA).
See docs/NAVIGATION_RESEARCH.md for the sourcing of these dimensions and for
what remains unverified (ice class in particular).
"""

from __future__ import annotations

import hashlib
import json
from datetime import date as Date
from datetime import timedelta
from pathlib import Path

from make_route_figure import build_mesh, nsidc_to_dataframe

NSIDC_DIR = Path(__file__).parent / "data" / "nsidc_sic"
CACHE_DIR = Path(__file__).parent / "data" / "vessel_meshes"

# MV Vasiliy Golovnin (IMO 8723426), Project 10620 "Vitus Bering" type, built
# Kherson 1988. FESCO hull chartered by NCPOR under a 5-year contract.
#
# beam 22.4 m and service speed 16.4 kn are verified against four independent
# registries. An earlier prototype config used beam 18.6 and 14.0 km/hr; both
# were wrong, and 14.0 km/hr (7.6 kn) was roughly half the real service speed.
#
# Three parameters remain uncalibrated and must be said out loud:
#   force_limit   - carried over from BAS's RRS Sir David Attenborough config.
#                   No published force limit exists for this hull.
#   max_ice_conc  - a working threshold, NOT derived from the ice class.
#                   Production replaces it with an IMO POLARIS RIO calculation,
#                   which is indexed by ice *type*, not concentration.
#   max_wave      - PolarRoute treats this as a hard cutoff only; its
#                   wave-added-resistance function is dead code, so sea state
#                   applies no speed or fuel penalty anywhere. Transit times
#                   from this config are therefore a LOWER BOUND.
#
# Ice class: RS old-system notation KM(*) ULA (verified, fleetphoto.ru registry
# entry for this hull). ULA is the highest non-icebreaker tier of the pre-1999
# Russian scale. Its modern Arc/PC equivalent is NOT sourced -- at least one
# Russian source explicitly denies ULA == Arc5 -- so we do not assert one.
GOLOVNIN = {
    "vessel_type": "SDA",
    "max_speed": 30.4,          # 16.4 kn service speed, verified
    "unit": "km/hr",
    "beam": 22.4,               # verified, 4 registries
    "hull_type": "slender",
    "force_limit": 96634.5,     # UNCALIBRATED: SDA value, not Golovnin's
    "max_ice_conc": 80,         # working stand-in, not from ice class
    "min_depth": 20,
    "max_wave": 3.0,
}

# The vessel as the prototype originally had it, kept so the effect of fixing
# the specification can be measured rather than asserted.
GOLOVNIN_UNCALIBRATED = {**GOLOVNIN, "max_speed": 14.0, "beam": 18.6}


def nsidc_file_for(day: Date) -> Path:
    """Path to the NSIDC daily CDR file for `day`."""
    path = NSIDC_DIR / f"sic_pss25_{day:%Y%m%d}_F17_v06r00.nc"
    if not path.exists():
        raise FileNotFoundError(
            f"No NSIDC observation for {day:%Y-%m-%d} ({path.name}). "
            f"The local archive covers 2018-01-01 to 2020-12-31."
        )
    return path


def vessel_mesh_for(day: Date, vessel: dict | None = None,
                    cache_dir: Path | None = None,
                    apply_qa: bool = True) -> dict:
    """Vessel-performance mesh for one day of observed ice, cached on disk.

    Every cell gains `speed` (km/hr per heading) and `inaccessible`, which is
    what a replay needs in order to ask "how fast could the ship actually move
    here, on this date".
    """
    from polar_route.vessel_performance.vessel_performance_modeller import (
        VesselPerformanceModeller,
    )

    vessel = vessel or GOLOVNIN
    cache_dir = cache_dir or CACHE_DIR
    cache_dir.mkdir(parents=True, exist_ok=True)

    # The whole vessel config goes into the key. Caching on date alone -- or on
    # the ice limit alone -- would silently serve a mesh built for a different
    # ship, because speed, beam and force limit all change the derated speeds.
    fingerprint = hashlib.sha1(
        json.dumps({**vessel, "qa": apply_qa}, sort_keys=True).encode()
    ).hexdigest()[:10]
    cache = cache_dir / f"vmesh_{day:%Y%m%d}_{fingerprint}.json"
    if cache.exists():
        return json.loads(cache.read_text())

    nc_path = nsidc_file_for(day)
    iso = f"{day:%Y-%m-%d}"

    points = nsidc_to_dataframe(nc_path, apply_qa=apply_qa)
    csv_path = cache_dir / f"points_{day:%Y%m%d}.csv"
    points.to_csv(csv_path, index=False)

    mesh_json = build_mesh(csv_path, iso)

    vpm = VesselPerformanceModeller(mesh_json, vessel)
    vpm.model_accessibility()
    vpm.model_performance()
    vessel_mesh = vpm.to_json()

    cache.write_text(json.dumps(vessel_mesh))
    csv_path.unlink(missing_ok=True)   # the mesh embeds what we need
    return vessel_mesh


class CellLookup:
    """Point-in-cell lookup over one vessel mesh.

    meshiphi cells are axis-aligned lat/long rectangles described by a centre
    (cx, cy) and half-widths (dcx, dcy), so containment is two comparisons. The
    mesh is adaptive, so cells vary in size and a linear scan is honest and
    fast enough at a few hundred cells.
    """

    def __init__(self, vessel_mesh: dict) -> None:
        self.cells = vessel_mesh["cellboxes"]

    def at(self, lat: float, lon: float) -> dict | None:
        for cell in self.cells:
            if (abs(lon - cell["cx"]) <= cell["dcx"]
                    and abs(lat - cell["cy"]) <= cell["dcy"]):
                return cell
        return None

    def speed_at(self, lat: float, lon: float) -> float | None:
        """Speed in km/hr, or None where the ship may not go.

        `speed` is stored per compass heading. With currents zeroed and no wind
        loaded every heading is identical, so heading 0 is representative -- if
        wind is ever wired in, this must become heading-aware.
        """
        cell = self.at(lat, lon)
        if cell is None or cell.get("inaccessible"):
            return None
        speed = cell.get("speed")
        if speed is None:
            return None
        return float(speed[0]) if isinstance(speed, list) else float(speed)

    def sic_at(self, lat: float, lon: float) -> float | None:
        cell = self.at(lat, lon)
        return None if cell is None else cell.get("SIC")


def daterange(start: Date, days: int):
    """Yield `days` consecutive dates beginning at `start`."""
    for offset in range(days):
        yield start + timedelta(days=offset)
