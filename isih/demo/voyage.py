"""Voyage state: the active plan, own ship, alerts and the hazard timeline.

This is the layer the bridge console talks to. It owns one World, one Router and
one active plan, and it answers the five questions UI section 32 says the screen
must answer without a caption:

    where am I, where was I supposed to be, what is in front of me,
    is the approved route still valid, and what are my alternatives.

Alerting (section 13) lives here rather than in the UI because an alert must be
a consequence of evidence, not a rendering decision. Every alert carries the
nine mandated fields and none is raised without a named route consequence.
"""

from __future__ import annotations

import math
import threading
from dataclasses import dataclass, field

import numpy as np

from isih.sim.router import Router, VesselModel
from isih.sim.world import BHARATI, CAPE_TOWN, MAITRI, PROGRESS, World

HOLD_POINT = (-64.5, 76.19)          # pack-edge hold, ~550 km north of Bharati
EPOCH_LABEL = "2026-12-07T00:00:00Z"


def _hav_nm(lat1, lon1, lat2, lon2):
    R = 3440.065
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(min(1.0, math.sqrt(a)))


def _bearing(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return (math.degrees(math.atan2(y, x)) + 360.0) % 360.0


@dataclass
class Plan:
    version: int
    objective: str
    ice_limit: float
    destination: str
    depart_day: float
    route: dict
    approved_by: str | None = None
    note: str = ""
    supersedes: int | None = None


class VoyageService:
    def __init__(self, seed: int = 20261207):
        self.world = World(seed)
        self.vessel = VesselModel()
        self.router = Router(self.world, self.vessel)
        self.lock = threading.Lock()
        self.plans: list[Plan] = []
        self.acked: set[str] = set()
        self._route_cache: dict = {}

    # ---- routing -----------------------------------------------------------
    def solve(self, destination="BHARATI", objective="time", ice_limit=0.80,
              depart_day=0.0):
        goal = {"BHARATI": BHARATI, "MAITRI": MAITRI,
                "HOLD": HOLD_POINT}.get(destination, BHARATI)
        key = (destination, objective, round(ice_limit, 3), round(depart_day, 2))
        if key not in self._route_cache:
            self.router._cache.clear()
            self._route_cache[key] = self.router.solve(
                CAPE_TOWN, goal, depart_day, objective, ice_limit)
        return self._route_cache[key]

    def alternatives(self, depart_day=0.0):
        """Three corridors that differ in what they are willing to accept."""
        out = []
        specs = (
            ("A", "Planned", "time", 0.80, "BHARATI"),
            ("B", "Fuel-conserving", "fuel", 0.80, "BHARATI"),
            ("C", "Ice-cautious", "time", 0.55, "BHARATI"),
            ("D", "Hold at pack edge", "time", 0.80, "HOLD"),
        )
        base = self.solve("BHARATI", "time", 0.80, depart_day)
        for key, label, obj, lim, dest in specs:
            r = self.solve(dest, obj, lim, depart_day)
            if r is None:
                out.append({"key": key, "label": label, "objective": obj,
                            "ice_limit": lim, "destination": dest,
                            "solved": False,
                            "why": f"no route exists at a {int(lim*100)}% ice limit"})
                continue
            out.append({
                "key": key, "label": label, "objective": obj, "ice_limit": lim,
                "destination": dest, "solved": True,
                "days": r["days"], "fuel_t": r["fuel_t"],
                "distance_km": r["distance_km"], "n_legs": r["n_legs"],
                "worst_sic": r["worst_sic"], "worst_hs": r["worst_hs"],
                "d_days": None if base is None else round(r["days"] - base["days"], 2),
                "d_fuel": None if base is None else round(r["fuel_t"] - base["fuel_t"], 1),
            })
        return out

    # ---- own ship ----------------------------------------------------------
    def own_ship(self, t):
        plan = self.active_plan()
        if plan is None or not plan.route:
            return None
        legs = plan.route["legs"]
        since = (t - plan.depart_day) * 24.0
        if since <= 0:
            l = legs[0]
            return {"lat": l["lat"], "lon": l["lon"], "cog": 0.0, "sog": 0.0,
                    "underway": False, "leg": 0, "progress": 0.0}
        for k in range(len(legs) - 1):
            if legs[k]["hours"] <= since <= legs[k + 1]["hours"]:
                a, b = legs[k], legs[k + 1]
                span = max(b["hours"] - a["hours"], 1e-6)
                f = (since - a["hours"]) / span
                lat = a["lat"] + f * (b["lat"] - a["lat"])
                lon = a["lon"] + f * (b["lon"] - a["lon"])
                nm = _hav_nm(a["lat"], a["lon"], b["lat"], b["lon"])
                return {"lat": round(lat, 4), "lon": round(lon, 4),
                        "cog": round(_bearing(a["lat"], a["lon"], b["lat"], b["lon"]), 1),
                        "sog": round(nm / span, 1), "underway": True, "leg": k,
                        "progress": round(since / legs[-1]["hours"], 3)}
        l = legs[-1]
        return {"lat": l["lat"], "lon": l["lon"], "cog": 0.0, "sog": 0.0,
                "underway": False, "leg": len(legs) - 1, "progress": 1.0,
                "arrived": True}

    def active_plan(self):
        for p in reversed(self.plans):
            if p.approved_by:
                return p
        return self.plans[-1] if self.plans else None

    # ---- hazards -----------------------------------------------------------
    def berg_separation(self, t, horizon_h=72):
        """Closest approach between every tracked berg's projected track and the
        ship's FUTURE track - section 8 asks for the future position against the
        future route, not against where the ship happens to be now."""
        plan = self.active_plan()
        if plan is None:
            return []
        legs = plan.route["legs"]
        since = (t - plan.depart_day) * 24.0
        ahead = [l for l in legs if since <= l["hours"] <= since + horizon_h]
        if len(ahead) < 2:
            ahead = legs[-2:]
        out = []
        bergs = self.world.bergs.at(t)
        for idx, b in enumerate(bergs):
            fc = self.world.bergs.forecast(idx, t)
            best = None
            for step in fc:
                bh = step["hours"]
                pos = min(ahead, key=lambda l: abs((l["hours"] - since) - bh))
                d = _hav_nm(step["lat"], step["lon"], pos["lat"], pos["lon"])
                margin = d - step["radius_km"] / 1.852
                if best is None or margin < best["margin_nm"]:
                    best = {"hours": bh, "sep_nm": round(d, 1),
                            "margin_nm": round(margin, 1),
                            "radius_nm": round(step["radius_km"] / 1.852, 1)}
            if best:
                out.append({**b, "cpa": best})
        out.sort(key=lambda x: x["cpa"]["margin_nm"])
        return out

    def timeline(self, t):
        """What is likely to affect the route over the next 6/12/24/48 hours."""
        plan = self.active_plan()
        rows = []
        for h in (6, 12, 24, 48):
            tt = t + h / 24.0
            if plan is None:
                rows.append({"hours": h, "state": "none", "items": []})
                continue
            legs = plan.route["legs"]
            since = (t - plan.depart_day) * 24.0
            ahead = [l for l in legs if since <= l["hours"] <= since + h]
            if not ahead:
                rows.append({"hours": h, "state": "none", "items": []})
                continue
            lats = np.array([l["lat"] for l in ahead])
            lons = np.array([l["lon"] for l in ahead])
            s = self.world.sample(lats, lons, tt)
            items, state = [], "none"
            if float(s["sic"].max()) > 0.60:
                items.append(f"ice to {int(round(float(s['sic'].max())*100))}% on track")
                state = "warn" if float(s["sic"].max()) < 0.80 else "bad"
            if float(s["hs"].max()) > 5.0:
                items.append(f"sea {float(s['hs'].max()):.1f} m")
                state = "bad" if float(s["hs"].max()) > 8.0 else max(state, "warn", key=len)
            if float(s["vis_nm"].min()) < 2.0:
                items.append(f"visibility {float(s['vis_nm'].min()):.1f} nm")
                state = "warn" if state == "none" else state
            if float(s["wind_kn"].max()) > 40.0:
                items.append(f"wind {int(float(s['wind_kn'].max()))} kn")
                state = "warn" if state == "none" else state
            rows.append({"hours": h, "state": state, "items": items})
        return rows

    # ---- alerting (section 13) --------------------------------------------
    def alerts(self, t):
        """P1 immediate safety, P2 route degradation, P3 informational.

        Every alert carries the nine mandated fields. Nothing is raised without
        a route consequence, which is the anti-spam rule: an event that does not
        change the plan is not an alert, it is a reading on a panel.
        """
        out = []
        plan = self.active_plan()
        ship = self.own_ship(t)

        def add(pri, kind, what, where, lat, lon, source, conf, consequence,
                action, expiry_h):
            aid = f"{kind}:{round(lat,1)}:{round(lon,1)}:{int(t)}"
            out.append({
                "id": aid, "priority": pri, "kind": kind, "what": what,
                "where": where, "lat": lat, "lon": lon,
                "time_day": round(t, 2), "source": source, "confidence": conf,
                "consequence": consequence, "action": action,
                "expires_in_h": expiry_h, "acked": aid in self.acked,
            })

        # P1 - iceberg closing on the future track
        for b in self.berg_separation(t)[:4]:
            m = b["cpa"]["margin_nm"]
            if m < 12.0:
                add("P1" if m < 5.0 else "P2", "ICEBERG",
                    f"{b['id']} within {b['cpa']['sep_nm']} nm of track",
                    f"{b['source']} berg, {b['area_km2']} km2",
                    b["lat"], b["lon"], "drift model (WDE17) on tracked position",
                    "uncertainty grows 13 km/day; projection capped at 72 h",
                    f"closest approach in {b['cpa']['hours']} h, margin {m} nm",
                    "alter to open the CPA or reduce to allow a wider berth",
                    b["cpa"]["hours"])

        if plan is not None and ship is not None:
            s = self.world.sample(ship["lat"], ship["lon"], t)
            hs = float(s["hs"]); vis = float(s["vis_nm"]); sic = float(s["sic"])
            wind = float(s["wind_kn"])
            if hs > 7.0:
                add("P1" if hs > 10.0 else "P2", "SEA STATE",
                    f"significant wave height {hs:.1f} m",
                    "at own ship", ship["lat"], ship["lon"],
                    "wave field from wind", "fetch-limited growth",
                    "speed reduction and added fuel; transfer operations not feasible",
                    "consider a southerly diversion or reduce to ease motion", 12)
            if vis < 1.0:
                add("P1", "VISIBILITY", f"visibility {vis:.1f} nm",
                    "at own ship", ship["lat"], ship["lon"],
                    "fog from air-sea temperature difference", "modelled",
                    "growler lookout degraded; radar is the only detection left",
                    "reduce speed, post extra lookout, use the ice searchlight", 6)
            if sic > 0.55:
                add("P2", "ICE", f"concentration {int(sic*100)}% at own ship",
                    "at own ship", ship["lat"], ship["lon"],
                    "modelled concentration field", "assumed 80% working limit",
                    "speed derated; margin to the working limit is narrowing",
                    "review the corridor before the margin closes", 24)
            if wind > 45.0:
                add("P2", "WIND", f"wind {int(wind)} kn",
                    "at own ship", ship["lat"], ship["lon"],
                    "geostrophic wind from pressure field", "modelled",
                    "ice edge will be displaced downwind; route assumptions may move",
                    "re-check the approach before committing", 18)

        # P2 - the destination is closed on the day we would arrive
        if plan is not None and plan.route:
            eta_day = plan.depart_day + plan.route["days"]
            arr = self.solve(plan.destination, plan.objective, plan.ice_limit, eta_day)
            if arr is None:
                add("P2", "DESTINATION", "destination not reachable on the ETA",
                    plan.destination, BHARATI[0], BHARATI[1],
                    "route search on the field valid at arrival",
                    "assumed ice limit, not a certificated figure",
                    "the plan arrives on a day with no solution",
                    "hold at the pack edge or re-time the approach", 48)

        for w in self.world.warnings.at(t):
            add("P3", "WARNING", w["id"], w["text"], w["lat"], w["lon"],
                "NAVAREA VII", "simulated - no live feed",
                "advisory; no change to the plan unless the track passes within the radius",
                "note in the passage plan", 72)

        order = {"P1": 0, "P2": 1, "P3": 2}
        out.sort(key=lambda a: (order[a["priority"]], a["what"]))
        return out
