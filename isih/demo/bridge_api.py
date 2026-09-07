"""HTTP surface for the bridge console.

Kept in its own module and mounted as a router so the existing service and its
tests are untouched. Everything here reads the world model and the voyage
service; nothing here holds state of its own.
"""

from __future__ import annotations

import numpy as np
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from isih.sim.world import BHARATI, BOX, CAPE_TOWN, MAITRI, PROGRESS

from .voyage import EPOCH_LABEL, HOLD_POINT, Plan, VoyageService

router = APIRouter(prefix="/api/v2")
VOY = VoyageService()

FIELDS = ("sic", "wind_kn", "hs", "vis_nm", "sst", "cur_kn", "mslp")


class ApproveBody(BaseModel):
    by: str = Field(min_length=1, max_length=120)
    note: str = Field(default="", max_length=500)
    objective: str = "time"
    ice_limit: float = 0.80
    destination: str = "BHARATI"
    depart_day: float = 0.0


@router.get("/meta")
def meta():
    return {
        "epoch": EPOCH_LABEL,
        "box": BOX,
        "places": {
            "CAPE_TOWN": {"lat": CAPE_TOWN[0], "lon": CAPE_TOWN[1], "name": "Cape Town"},
            "BHARATI": {"lat": BHARATI[0], "lon": BHARATI[1], "name": "Bharati"},
            "MAITRI": {"lat": MAITRI[0], "lon": MAITRI[1], "name": "Maitri"},
            "PROGRESS": {"lat": PROGRESS[0], "lon": PROGRESS[1], "name": "Progress (RU)"},
            "HOLD": {"lat": HOLD_POINT[0], "lon": HOLD_POINT[1], "name": "Pack-edge hold"},
        },
        "vessel": {
            "name": VOY.vessel.name, "imo": "8723426",
            "max_speed_kn": VOY.vessel.max_speed_kn,
            "ice_limit": VOY.vessel.ice_limit,
            "ice_limit_is_assumed": True,
        },
        "fields": list(FIELDS),
    }


@router.get("/field")
def field(t: float = 0.0, var: str = "sic", nx: int = 108, ny: int = 88):
    if var not in FIELDS:
        raise HTTPException(400, f"unknown field {var!r}")
    lons, lats, s = VOY.world.grid(t, nx=int(np.clip(nx, 20, 200)),
                                   ny=int(np.clip(ny, 20, 200)))
    a = np.asarray(s[var], dtype=float)
    return {
        "var": var, "t": t,
        "lon_min": float(lons[0]), "lon_max": float(lons[-1]),
        "lat_min": float(lats[0]), "lat_max": float(lats[-1]),
        "nx": len(lons), "ny": len(lats),
        "vmin": round(float(np.nanmin(a)), 3), "vmax": round(float(np.nanmax(a)), 3),
        "values": [round(float(x), 3) for x in a.ravel()],
    }


@router.get("/vectors")
def vectors(t: float = 0.0, var: str = "wind", nx: int = 22, ny: int = 18):
    lons, lats, s = VOY.world.grid(t, nx=nx, ny=ny)
    u = s["wind_u"] if var == "wind" else s["cur_u"]
    v = s["wind_v"] if var == "wind" else s["cur_v"]
    out = []
    for j in range(len(lats)):
        for i in range(len(lons)):
            out.append({"lat": round(float(lats[j]), 3), "lon": round(float(lons[i]), 3),
                        "u": round(float(u[j, i]), 2), "v": round(float(v[j, i]), 2)})
    return {"var": var, "t": t, "items": out}


@router.get("/bergs")
def bergs(t: float = 0.0):
    sep = VOY.berg_separation(t)
    if sep:
        return {"t": t, "items": sep}
    return {"t": t, "items": VOY.world.bergs.at(t)}


@router.get("/berg-track")
def berg_track(t: float = 0.0, index: int = 0):
    n = len(VOY.world.bergs.name)
    if not (0 <= index < n):
        raise HTTPException(404, "no such berg")
    return {"index": index, "id": VOY.world.bergs.name[index],
            "forecast": VOY.world.bergs.forecast(index, t)}


@router.get("/traffic")
def traffic(t: float = 0.0):
    return {"t": t, "items": VOY.world.traffic.at(t)}


@router.get("/warnings")
def warnings(t: float = 0.0):
    return {"t": t, "items": VOY.world.warnings.at(t)}


@router.get("/route")
def route(destination: str = "BHARATI", objective: str = "time",
          ice_limit: float = 0.80, depart_day: float = 0.0):
    r = VOY.solve(destination, objective, float(np.clip(ice_limit, 0.15, 0.95)),
                  depart_day)
    if r is None:
        return {"solved": False,
                "why": f"no route to {destination} at a {int(ice_limit*100)}% ice limit "
                       f"departing day {depart_day:+.0f}"}
    return {"solved": True, **r}


@router.get("/alternatives")
def alternatives(depart_day: float = 0.0):
    return {"depart_day": depart_day, "items": VOY.alternatives(depart_day)}


@router.get("/critical-limit")
def critical_limit(depart_day: float = 0.0, destination: str = "BHARATI"):
    goal = {"BHARATI": BHARATI, "MAITRI": MAITRI, "HOLD": HOLD_POINT}[destination]
    VOY.router._cache.clear()
    return VOY.router.critical_ice_limit(CAPE_TOWN, goal, depart_day)


@router.get("/state")
def state(t: float = 0.0):
    ship = VOY.own_ship(t)
    plan = VOY.active_plan()
    cond = None
    if ship:
        s = VOY.world.sample(ship["lat"], ship["lon"], t)
        cond = {k: round(float(np.asarray(s[k])), 2) for k in
                ("sic", "wind_kn", "wind_dir", "hs", "tp", "vis_nm", "sst",
                 "air", "mslp", "cur_kn")}
    return {
        "t": t,
        "mode": "monitoring" if (plan and plan.approved_by) else "planning",
        "ship": ship,
        "conditions": cond,
        "plan": None if plan is None else {
            "version": plan.version, "objective": plan.objective,
            "ice_limit": plan.ice_limit, "destination": plan.destination,
            "depart_day": plan.depart_day,
            "approved_by": plan.approved_by, "note": plan.note,
            "days": plan.route["days"], "fuel_t": plan.route["fuel_t"],
            "distance_km": plan.route["distance_km"], "n_legs": plan.route["n_legs"],
        },
        "versions": [
            {"version": p.version, "by": p.approved_by, "note": p.note,
             "objective": p.objective, "ice_limit": p.ice_limit,
             "destination": p.destination, "days": p.route["days"],
             "supersedes": p.supersedes}
            for p in VOY.plans
        ],
    }


@router.get("/alerts")
def alerts(t: float = 0.0):
    return {"t": t, "items": VOY.alerts(t)}


@router.post("/ack/{alert_id:path}")
def ack(alert_id: str):
    VOY.acked.add(alert_id)
    return {"acked": alert_id}


@router.get("/timeline")
def timeline(t: float = 0.0):
    return {"t": t, "rows": VOY.timeline(t)}


@router.get("/waypoints")
def waypoints(destination: str = "BHARATI", objective: str = "time",
              ice_limit: float = 0.80, depart_day: float = 0.0, every: int = 6):
    r = VOY.solve(destination, objective, ice_limit, depart_day)
    if r is None:
        raise HTTPException(409, "no route to lay waypoints on")
    legs = r["legs"]
    picked = legs[::max(1, every)]
    if picked[-1] is not legs[-1]:
        picked.append(legs[-1])
    return {"items": [
        {"n": i, "lat": l["lat"], "lon": l["lon"],
         "eta_h": l["hours"], "eta_day": round(depart_day + l["hours"] / 24.0, 2),
         "sic": l["sic"], "hs": l["hs"]}
        for i, l in enumerate(picked)]}


@router.post("/approve")
def approve(body: ApproveBody):
    r = VOY.solve(body.destination, body.objective, body.ice_limit, body.depart_day)
    if r is None:
        raise HTTPException(409, "cannot approve a plan with no route")
    with VOY.lock:
        prev = VOY.active_plan()
        p = Plan(version=len(VOY.plans) + 1, objective=body.objective,
                 ice_limit=body.ice_limit, destination=body.destination,
                 depart_day=body.depart_day, route=r,
                 approved_by=body.by, note=body.note,
                 supersedes=None if prev is None else prev.version)
        VOY.plans.append(p)
    return {"version": p.version, "supersedes": p.supersedes, "by": p.approved_by}


@router.post("/reset")
def reset():
    with VOY.lock:
        VOY.plans.clear()
        VOY.acked.clear()
    return {"reset": True}


@router.get("/sensors")
def sensors(t: float = 0.0):
    """NMEA 0183 sentences derived from the planned track.

    Simulated: no instrument is attached. The geometry is real - position,
    course and speed come from the actual solved route - so the sentences are
    well formed and the checksums are correct, which is what makes this useful
    for building the ingest path rather than merely looking busy.
    """
    ship = VOY.own_ship(t)
    if ship is None:
        return {"t": t, "sentences": [], "note": "no active plan"}
    s = VOY.world.sample(ship["lat"], ship["lon"], t)

    def nmea(body):
        c = 0
        for ch in body:
            c ^= ord(ch)
        return f"${body}*{c:02X}"

    def dm(v, deg_width, pos, neg):
        h = pos if v >= 0 else neg
        v = abs(v)
        d = int(v)
        m = (v - d) * 60
        return f"{d:0{deg_width}d}{m:07.4f}", h

    lat_s, lat_h = dm(ship["lat"], 2, "N", "S")
    lon_s, lon_h = dm(ship["lon"], 3, "E", "W")
    hh = int((t * 24) % 24); mm = int((t * 24 * 60) % 60)
    out = [
        nmea(f"GPGGA,{hh:02d}{mm:02d}00.00,{lat_s},{lat_h},{lon_s},{lon_h},1,09,0.9,0.0,M,0.0,M,,"),
        nmea(f"GPVTG,{ship['cog']:.1f},T,,M,{ship['sog']:.1f},N,{ship['sog']*1.852:.1f},K,A"),
        nmea(f"HEHDT,{ship['cog']:.1f},T"),
        nmea(f"VWMWV,{float(s['wind_dir']):.1f},T,{float(s['wind_kn']):.1f},N,A"),
        nmea(f"SDDBT,{'':s},f,{'':s},M,{'':s},F"),
        nmea(f"VDVHW,{ship['cog']:.1f},T,,M,{ship['sog']:.1f},N,{ship['sog']*1.852:.1f},K"),
    ]
    return {"t": t, "sentences": out,
            "note": "derived from the planned track; no instrument attached"}


@router.get("/offline")
def offline(t: float = 0.0):
    """Pack sizes, measured by actually building and compressing the payloads."""
    import gzip
    import json as _json

    r = VOY.solve("BHARATI", "time", 0.80, 0.0)
    parts = {}

    def m(name, obj):
        raw = _json.dumps(obj, separators=(",", ":")).encode()
        parts[name] = {"raw_b": len(raw), "gz_b": len(gzip.compress(raw, 9))}

    lons, lats, s = VOY.world.grid(t, nx=108, ny=88)
    m("ice field (108x88, uint8)", [int(round(x * 100)) for x in np.asarray(s["sic"]).ravel()])
    m("wind field", [[round(float(a), 1), round(float(b), 1)]
                     for a, b in zip(np.asarray(s["wind_u"]).ravel()[::9],
                                     np.asarray(s["wind_v"]).ravel()[::9])])
    m("route polyline + summary", {"legs": [[l["lat"], l["lon"]] for l in (r or {"legs": []})["legs"]],
                                   "days": (r or {}).get("days"), "fuel_t": (r or {}).get("fuel_t")})
    m("iceberg positions", VOY.world.bergs.at(t))
    m("alerts", VOY.alerts(t))
    total_raw = sum(p["raw_b"] for p in parts.values())
    total_gz = sum(p["gz_b"] for p in parts.values())
    return {
        "t": t, "parts": parts,
        "total_raw_b": total_raw, "total_gz_b": total_gz,
        "iridium_certus_kbps": 704,
        "seconds_at_certus": round(total_gz * 8 / (704 * 1000), 2),
        "measured": True,
        "note": "sizes measured by building and gzipping the real payloads",
    }
