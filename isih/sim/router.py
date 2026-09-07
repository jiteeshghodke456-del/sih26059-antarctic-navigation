"""Constrained multi-objective route search over the world model.

Why this exists rather than a second call to PolarRoute: PolarRoute is the
better engine and is used for the published corridors, but it lives in a
separate Python environment, it has no time dimension, and it cannot be run
from inside a request. The audit's sharpest structural finding was that the
prediction layer never reached the route - the router met day-zero ice on day
nine. A search that runs against the live world model at request time is what
closes that, and it is only tractable because the domain is small.

Two things here are deliberately different from the published corridors.

1.  TIME IS A DIMENSION. The cost of entering a cell is evaluated with the ice
    and weather valid at the time the ship would actually arrive there, not at
    departure. That is the whole point: a forecast is useless to a router that
    cannot ask "what will it be like when I get there".

2.  FUEL AND TIME ARE NOT COLLINEAR. In the published configuration they were -
    with zero currents and wave resistance dead, fuel was a monotone function of
    time and solving for either returned the same path. Here speed is reduced by
    ice AND by sea state, while fuel burn rises with the cube of speed and with
    added resistance in waves. A time-optimal track drives through the weather;
    a fuel-optimal one goes around it. That gives a genuine trade-off surface
    rather than twelve copies of one line.

The vessel model is a deliberately simple derating curve, not a hull
performance model, and the ice limit remains an assumption - no ice class
anywhere indexes ice concentration. Both are stated in the output.
"""

from __future__ import annotations

import heapq
import math

import numpy as np

R_EARTH_KM = 6371.0


class VesselModel:
    """Speed and fuel as functions of ice and sea state."""

    def __init__(self, max_speed_kn=16.4, ice_limit=0.80, min_speed_kn=2.0,
                 name="MV Vasiliy Golovnin"):
        self.name = name
        self.max_speed_kn = max_speed_kn
        self.ice_limit = ice_limit
        self.min_speed_kn = min_speed_kn

    def speed_kn(self, sic, hs):
        """Speed made good. Ice derates by an exponent slightly above linear,
        which reflects that resistance climbs faster than concentration does;
        heavy seas force a voluntary speed reduction, which is a real bridge
        decision and not a hull limit."""
        sic = np.asarray(sic, dtype=float)
        hs = np.asarray(hs, dtype=float)
        frac = np.clip(sic / max(self.ice_limit, 1e-6), 0.0, 1.0)
        v_ice = self.max_speed_kn * (1.0 - 0.92 * frac ** 1.35)
        # Voluntary speed reduction: negligible below 4 m, severe above 9 m.
        sea_factor = 1.0 - 0.45 * np.clip((hs - 4.0) / 5.0, 0.0, 1.0)
        v = np.maximum(v_ice * sea_factor, self.min_speed_kn)
        return np.where(sic > self.ice_limit, 0.0, v)

    def fuel_t_per_km(self, speed_kn, sic, hs):
        """Tonnes per kilometre.

        Expressed per DISTANCE, not per hour, and that choice is the whole
        reason fuel and time stop being the same objective.

        Per hour, a cubic-in-speed burn makes slow cells cheap, so a fuel search
        happily crawls through a storm - which is what the first version of this
        did. Converting to per-distance divides out one power of speed and
        leaves three independent resistances:

            calm water   proportional to v^2    (penalises going fast)
            ice          proportional to C^1.5  (penalises ice at any speed)
            added wave   proportional to Hs^2   (penalises weather at any speed)

        A time-optimal track maximises speed and accepts the weather. A
        fuel-optimal one gives up speed to go round the ice and the sea state.
        Coefficients are scaled so a calm 16.4 kn passage burns about 24 t/day,
        which is the right order for a vessel of this size. RELATIVE ONLY - the
        absolute figure needs this hull's own performance curve, which is not
        public."""
        v = np.asarray(speed_kn, dtype=float)
        sic = np.asarray(sic, dtype=float)
        hs = np.asarray(hs, dtype=float)
        calm = 0.000120 * v ** 2
        ice = 0.0200 * np.clip(sic, 0.0, 1.0) ** 1.5
        wave = 0.00035 * np.clip(hs, 0.0, 18.0) ** 2
        return calm + ice + wave

def _haversine_km(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R_EARTH_KM * math.asin(min(1.0, math.sqrt(a)))


class Router:
    """Dijkstra on a lat/lon lattice, with cost evaluated at arrival time."""

    # 8-connected, so the track can run diagonally instead of in stair steps.
    NEIGHBOURS = ((-1, 0), (1, 0), (0, -1), (0, 1),
                  (-1, -1), (-1, 1), (1, -1), (1, 1))

    def __init__(self, world, vessel: VesselModel, dlat=0.55, dlon=0.9,
                 lat_min=-70.6, lat_max=-33.0, lon_min=13.0, lon_max=79.5):
        self.world = world
        self.vessel = vessel
        self.lats = np.arange(lat_min, lat_max + dlat, dlat)
        self.lons = np.arange(lon_min, lon_max + dlon, dlon)
        self.ny, self.nx = len(self.lats), len(self.lons)
        self._cache = {}

    def _conditions(self, t_slot):
        """Fields on the router lattice at a quantised time. Quantising to
        6-hour slots keeps the number of world evaluations small while still
        letting the ship meet different weather at different points."""
        if t_slot not in self._cache:
            LO, LA = np.meshgrid(self.lons, self.lats)
            s = self.world.sample(LA, LO, t_slot * 0.25)
            self._cache[t_slot] = (s["sic"], s["hs"])
        return self._cache[t_slot]

    def _nearest(self, lat, lon):
        j = int(np.clip(np.argmin(np.abs(self.lats - lat)), 0, self.ny - 1))
        i = int(np.clip(np.argmin(np.abs(self.lons - lon)), 0, self.nx - 1))
        return j, i

    def solve(self, start, goal, depart_t=0.0, objective="time", ice_limit=None):
        """start/goal are (lat, lon). Returns a dict, or None if no route."""
        vessel = self.vessel
        if ice_limit is not None:
            vessel = VesselModel(vessel.max_speed_kn, ice_limit,
                                 vessel.min_speed_kn, vessel.name)

        sj, si = self._nearest(*start)
        gj, gi = self._nearest(*goal)

        INF = float("inf")
        best = np.full((self.ny, self.nx), INF)
        elapsed = np.full((self.ny, self.nx), INF)   # hours since departure
        fuel = np.full((self.ny, self.nx), INF)
        prev = {}
        best[sj, si] = 0.0
        elapsed[sj, si] = 0.0
        fuel[sj, si] = 0.0
        pq = [(0.0, sj, si)]
        seen = np.zeros((self.ny, self.nx), dtype=bool)

        while pq:
            cost, j, i = heapq.heappop(pq)
            if seen[j, i]:
                continue
            seen[j, i] = True
            if (j, i) == (gj, gi):
                break
            t_here = elapsed[j, i]
            slot = int((depart_t * 24.0 + t_here) // 6.0)
            sic, hs = self._conditions(slot)

            for dj, di in self.NEIGHBOURS:
                nj, ni = j + dj, i + di
                if not (0 <= nj < self.ny and 0 <= ni < self.nx) or seen[nj, ni]:
                    continue
                s_n = float(sic[nj, ni])
                if s_n > vessel.ice_limit:
                    continue                      # hard constraint, never priced
                h_n = float(hs[nj, ni])
                v = float(vessel.speed_kn(s_n, h_n))
                if v <= 0.0:
                    continue
                d_km = _haversine_km(self.lats[j], self.lons[i],
                                     self.lats[nj], self.lons[ni])
                hours = d_km / (v * 1.852)
                burn = float(vessel.fuel_t_per_km(v, s_n, h_n)) * d_km
                step = hours if objective == "time" else burn
                nc = cost + step
                if nc < best[nj, ni]:
                    best[nj, ni] = nc
                    elapsed[nj, ni] = t_here + hours
                    fuel[nj, ni] = fuel[j, i] + burn
                    prev[(nj, ni)] = (j, i)
                    heapq.heappush(pq, (nc, nj, ni))

        if not seen[gj, gi]:
            return None

        path = []
        node = (gj, gi)
        while node != (sj, si):
            path.append(node)
            node = prev[node]
        path.append((sj, si))
        path.reverse()

        legs = []
        for k, (j, i) in enumerate(path):
            t_h = float(elapsed[j, i])
            slot = int((depart_t * 24.0 + t_h) // 6.0)
            sic, hs = self._conditions(slot)
            legs.append({
                "lat": round(float(self.lats[j]), 4),
                "lon": round(float(self.lons[i]), 4),
                "hours": round(t_h, 2),
                "sic": round(float(sic[j, i]), 3),
                "hs": round(float(hs[j, i]), 2),
            })
        total_km = sum(_haversine_km(legs[k]["lat"], legs[k]["lon"],
                                     legs[k + 1]["lat"], legs[k + 1]["lon"])
                       for k in range(len(legs) - 1))
        return {
            "objective": objective,
            "ice_limit": vessel.ice_limit,
            "legs": legs,
            "n_legs": len(legs) - 1,
            "hours": round(float(elapsed[gj, gi]), 2),
            "days": round(float(elapsed[gj, gi]) / 24.0, 3),
            "fuel_t": round(float(fuel[gj, gi]), 1),
            "distance_km": round(total_km, 1),
            "worst_sic": round(max(l["sic"] for l in legs), 3),
            "worst_hs": round(max(l["hs"] for l in legs), 2),
            "vessel": vessel.name,
            "ice_limit_is_assumed": True,
        }

    def critical_ice_limit(self, start, goal, depart_t=0.0,
                           limits=(0.85, 0.8, 0.75, 0.7, 0.65, 0.6,
                                   0.55, 0.5, 0.45, 0.4, 0.35, 0.3)):
        """The assumed limit at which the destination stops being reachable.

        The audit's recommendation, implemented: since the 80% limit is our own
        assumption and not a certificated figure, the honest daily output is not
        'open' but the limit at which the answer flips. It costs one solve per
        step and it does not rest on a number we invented."""
        last_ok = None
        for lim in limits:
            if self.solve(start, goal, depart_t, "time", ice_limit=lim) is not None:
                last_ok = lim
            else:
                return {"reachable_at_or_above": last_ok, "fails_at": lim}
        return {"reachable_at_or_above": last_ok, "fails_at": None}
