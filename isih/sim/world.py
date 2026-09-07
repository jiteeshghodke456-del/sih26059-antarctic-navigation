"""The assembled world: one clock, one seed, every field consistent.

Evaluation order is a dependency graph, not a list. Pressure comes first
because wind is its gradient; ice needs wind because the edge is wind-driven;
SST needs ice because water under ice is at the freezing point; waves need both
wind and ice because ice damps swell; visibility needs air and sea temperature
because fog is what happens when warm air crosses cold water.

    pressure -> wind -> ice edge -> SIC -> SST -> waves -> visibility
                  \\-> waves          \\-> berg drift (with current)

Nothing here is scripted. If the route degrades on day six it is because the
wind on days four and five pushed the edge north across it.
"""

from __future__ import annotations

import numpy as np

from .bergs import BergField
from .fields import Atmosphere, Ocean
from .ice import IceField

# The corridor. Cape Town -> Bharati, with the domain wide enough to hold the
# whole passage and the ice edge either side of it.
BOX = {"lon_min": 8.0, "lon_max": 88.0, "lat_min": -74.0, "lat_max": -30.0}

CAPE_TOWN = (-33.9249, 18.4241)
BHARATI = (-69.4044, 76.1900)
MAITRI = (-70.7659, 11.7311)
PROGRESS = (-69.3781, 76.3892)      # Russian station, 5-10 km from Bharati


class World:
    """Deterministic from (seed, t). t is days since the voyage epoch."""

    def __init__(self, seed: int = 20261207):
        self.seed = seed
        self.atm = Atmosphere(seed)
        self.ocean = Ocean(seed)
        self.ice = IceField(seed, self.atm)
        self.bergs = BergField(seed, self.atm, self.ocean)
        self.traffic = TrafficField(seed)
        self.warnings = WarningField(seed)

    # ---- point sampling, used by panels and by the route evaluator ----------
    def sample(self, lat, lon, t):
        lat = np.asarray(lat, dtype=float)
        lon = np.asarray(lon, dtype=float)
        sic = self.ice.concentration(lon, lat, t)
        u, v = self.atm.wind(lon, lat, t)
        cu, cv = self.ocean.current(lon, lat, t)
        sst = self.ocean.sst(lon, lat, t, sic)
        hs, tp, wdir = self.atm.waves(lon, lat, t, sic)
        vis = self.atm.visibility(lon, lat, t, sic, sst)
        return {
            "sic": sic,
            "wind_u": u, "wind_v": v,
            "wind_kn": np.hypot(u, v) * 1.94384,
            "wind_dir": (np.degrees(np.arctan2(-u, -v)) + 360.0) % 360.0,
            "cur_u": cu, "cur_v": cv,
            "cur_kn": np.hypot(cu, cv) * 1.94384,
            "sst": sst,
            "air": self.atm.air_temp(lon, lat, t, sic),
            "hs": hs, "tp": tp, "wave_dir": wdir,
            "vis_nm": vis,
            "mslp": self.atm.pressure(lon, lat, t),
        }

    def grid(self, t, nx=110, ny=90):
        """A field grid for the chart. Kept modest because the chart draws it
        as cells; finer than this is invisible at corridor scale."""
        lons = np.linspace(BOX["lon_min"], BOX["lon_max"], nx)
        lats = np.linspace(BOX["lat_min"], BOX["lat_max"], ny)
        LO, LA = np.meshgrid(lons, lats)
        s = self.sample(LA, LO, t)
        return lons, lats, s


class TrafficField:
    """AIS targets. Simulated - no receiver is connected - but the tracks are
    real great-circle legs between real places at plausible speeds, so bearing
    and CPA arithmetic against them is honest arithmetic."""

    SHIPS = (
        ("SA AGULHAS II", "ZSSA", (-33.92, 18.42), (-70.30, -2.83), 12.5, "Research"),
        ("ALDEBARAN",     "PJHA", (-42.10, 42.00), (-58.20, 72.00), 10.8, "Fishing"),
        ("KAPITAN KHLEBNIKOV", "UBKH", (-62.40, 58.10), (-66.90, 89.50), 11.2, "Passenger"),
        ("FV ANTARCTIC PROVIDER", "LAPR", (-55.60, 30.20), (-61.80, 15.40), 9.4, "Fishing"),
    )

    def __init__(self, seed: int):
        self.rng_offset = (seed % 97) / 97.0

    def at(self, t):
        out = []
        for i, (name, call, a, b, sog, kind) in enumerate(self.SHIPS):
            # Each ship is at a different point of its own passage.
            frac = (self.rng_offset + 0.11 * i + 0.035 * t) % 1.0
            lat = a[0] + (b[0] - a[0]) * frac
            lon = a[1] + (b[1] - a[1]) * frac
            dlat, dlon = b[0] - a[0], b[1] - a[1]
            cog = (np.degrees(np.arctan2(dlon * np.cos(np.radians(lat)), dlat)) + 360) % 360
            out.append({
                "name": name, "callsign": call, "type": kind,
                "lat": round(float(lat), 4), "lon": round(float(lon), 4),
                "cog": round(float(cog), 1), "sog": sog,
            })
        return out


class WarningField:
    """NAVAREA VII-style navigational warnings. Simulated: there is no live
    feed. Each carries the fields a real warning carries, so the UI is built
    against the right shape."""

    def __init__(self, seed: int):
        self.seed = seed

    def at(self, t):
        items = [
            {"id": "NAVAREA VII 214/26", "kind": "ICE",
             "text": "Numerous growlers and bergy bits reported within 40 NM of "
                     "the pack edge between 060E and 075E.",
             "lat": -64.6, "lon": 67.5, "radius_nm": 40, "from_day": 0, "to_day": 14},
            {"id": "NAVAREA VII 219/26", "kind": "SAR",
             "text": "SAR exercise, Prydz Bay approaches. Wide berth requested.",
             "lat": -67.8, "lon": 74.9, "radius_nm": 25, "from_day": 3, "to_day": 9},
            {"id": "NAVAREA VII 221/26", "kind": "DERELICT",
             "text": "Unlit derelict container reported adrift.",
             "lat": -47.2, "lon": 38.4, "radius_nm": 15, "from_day": 1, "to_day": 20},
        ]
        return [w for w in items if w["from_day"] <= t <= w["to_day"]]
