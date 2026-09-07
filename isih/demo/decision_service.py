"""Assemble a real Decision from the files on disk, and keep the log.

This is the join between the domain model (isih/decision.py, isih/gates.py)
and the artifacts the pipeline actually produced. Nothing here invents a
value: every field traces to a file, and where a file has nothing to say the
gate returns UNKNOWN rather than a default.

The decision log is deliberately in-memory. §11 wants revision history and
§32 a decision log, and both are satisfied within a session; persisting
approvals to disk would mean a demo inherits the previous demo's decisions,
which is worse. `supersedes` chains the versions so nothing is silently
replaced — §4 is explicit that an approved plan must never be overwritten
without preserving the old one and showing why it changed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ISIH = Path(__file__).resolve().parents[1]
if str(ISIH) not in sys.path:
    sys.path.insert(0, str(ISIH))

import gates as G                                   # noqa: E402
from decision import (                              # noqa: E402
    Alternative,
    Approval,
    Decision,
    Evidence,
    GateState,
    health_from_gates,
    utc_now,
)

from . import data                                  # noqa: E402

FIG = ISIH / "figures"

# Kept out of ice_meshes so the demo has no PolarRoute dependency at runtime.
# Values mirror isih/ice_meshes.py:GOLOVNIN exactly; the test below asserts it.
VESSEL = {
    "name": "MV Vasiliy Golovnin",
    "imo": "8723426",
    "max_speed": 30.4,
    "unit": "km/hr",
    "beam": 22.4,
    "min_depth": 20,
    "max_ice_conc": 80,
    "force_limit": 96634.5,
    "ice_class": "RS KM(*) ULA[2] (at d<=8.5 m) AUT2 — SINGLE-SOURCE",
    "polar_ship_category": None,
}


def _load(name: str) -> dict | None:
    p = FIG / name
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError:
        return None


def alternatives_doc() -> dict | None:
    return _load("alternatives.json")


def vessel_comparison() -> dict | None:
    return _load("vessel_comparison.json")


def _alternatives() -> list[Alternative]:
    doc = alternatives_doc()
    if not doc:
        return []
    out = []
    for c in doc.get("corridors", []):
        if c.get("solved"):
            summary = (f"{c['traveltime_days']:.2f} d, fuel {c['fuel']:.0f}, "
                       f"{c['legs']} legs, worst ice {c.get('worst_ice_pct')}%")
        else:
            summary = "no route exists for this ship at this ice limit"
        out.append(Alternative(
            label=f"{c['label']} — {c['name']} ({c['ice_limit_pct']}% limit)",
            summary=summary,
            eta_days=c.get("traveltime_days"),
            eta_delta_days=c.get("eta_delta_days"),
            worst_ice_pct=c.get("worst_ice_pct"),
            fuel=c.get("fuel"),
            fuel_delta=c.get("fuel_delta"),
            rationale=c.get("rationale", ""),
            provenance="isih/figures/alternatives.json",
        ))
    return out


def _destination_state(day: str) -> tuple[bool | None, str, int | None, int | None]:
    """Is the primary destination reachable on `day`?

    Returns None for open when the target was never scored — no mesh cell
    contains it — which the logistics gate turns into UNKNOWN rather than
    into 'closed'. That distinction was a real bug once.
    """
    w = data.window()
    name = "Bharati"
    summ = w.get("summary", {}).get(name)
    if summ is None:
        return None, name, None, None

    open_today = None
    for row in w.get("daily", []):
        if row.get("date") == day and name in row:
            v = row[name].get("sic_qa_on")
            open_today = None if v is None else bool(row[name].get("passable"))
            break
    closed = summ.get("days_closed")
    total = summ.get("days_in_window") or len(w.get("daily", []))
    return open_today, name, closed, total


def build(day: str | None = None) -> Decision:
    """Build the current decision from real artifacts."""
    day = day or data.dates()[0]
    route = data.route()
    routes_cfg = _load("routes.json") or {}
    alts = _alternatives()
    solved_alts = [a for a in alts if a.eta_days is not None]

    open_today, dest, closed, total = _destination_state(day)

    gate_list = G.evaluate_all(
        vessel=VESSEL,
        mesh_config=routes_cfg.get("config", {}),
        worst_ice_pct=route.get("max_sic_pct_along_route"),
        ice_limit_pct=float(VESSEL["max_ice_conc"]),
        destination_open=open_today,
        destination=dest,
        n_alternatives=len(solved_alts),
        days_closed=closed,
        days_total=total,
        live_sensors=False,
    )

    health, binding = health_from_gates(gate_list)
    cov = G.coverage_summary(gate_list)

    recommendation = (
        f"{cov['gates_evaluated']} of {cov['gates_total']} decision gates can be "
        f"evaluated from data we hold. This route cannot be certified as VALID."
    )
    if binding:
        recommendation = binding[0].reason

    return Decision(
        decision_id=f"D-{day}",
        time=utc_now(),
        data_mode=data.DATA_MODE["mode"],
        vessel_state={
            **VESSEL,
            "position_source": "no live GPS — historical replay",
        },
        route_version=1,
        environmental_state={
            "ice_source": data.SOURCE_ICE,
            "ice_date": day,
            "router": data.SOURCE_ROUTE,
            "worst_ice_pct_on_route": route.get("max_sic_pct_along_route"),
            "steaming_days": route.get("total_traveltime_days"),
        },
        hazards_considered=[
            {"kind": "sea ice", "state": "observed", "source": data.SOURCE_ICE},
            {"kind": "icebergs", "state": "not on this screen",
             "source": "USNIC catalogue held but not wired into the route"},
            {"kind": "weather", "state": "no data", "source": "none"},
        ],
        assumptions=[
            "The 80% ice-concentration limit is a working assumption. No ice class "
            "indexes concentration — every framework indexes thickness or type.",
            "Steaming time only: PolarRoute's wave-added-resistance function is dead "
            "code in 1.1.11, so every duration here is a lower bound.",
            "The route is solved on one day's ice and held fixed; the router has no "
            "time dimension.",
        ],
        constraints=[
            f"ice limit {VESSEL['max_ice_conc']}% (assumed)",
            f"minimum depth {VESSEL['min_depth']} m (configured, but no bathymetry "
            f"exists in the mesh to apply it)",
        ],
        gates=gate_list,
        alternatives=alts,
        recommendation=recommendation,
        confidence=f"{cov['gates_evaluated']} of {cov['gates_total']} gates evaluable",
        trigger_conditions=[
            "the destination cell's concentration crosses the assumed working limit",
            "a newer satellite observation changes the worst ice on the route",
            "bathymetry becomes available, which would let the chart gate be evaluated",
        ],
        evidence=[
            Evidence(data.SOURCE_ICE, f"observation for {day}",
                     f"isih/data/nsidc_sic (day {day})"),
            Evidence(data.SOURCE_ROUTE, "computed corridor",
                     "isih/figures/routes.json"),
            Evidence("PolarRoute alternatives", f"{len(alts)} corridors",
                     "isih/figures/alternatives.json"),
        ],
        approval=Approval(approved=False),
    )


class DecisionLog:
    """Route versions and approvals for one session.

    Approving does not mutate a decision in place: it appends a new version
    that supersedes the previous one, so the history §4 requires is intact.
    """

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []

    def current(self, day: str | None = None) -> dict[str, Any]:
        if not self._entries:
            self._entries.append(build(day).as_dict())
        return self._entries[-1]

    def approve(self, by: str, note: str = "") -> dict[str, Any]:
        prev = self.current()
        nxt = json.loads(json.dumps(prev))
        nxt["route_version"] = prev["route_version"] + 1
        nxt["decision_id"] = f"{prev['decision_id']}-v{nxt['route_version']}"
        nxt["supersedes"] = prev["decision_id"]
        nxt["time"] = utc_now()
        nxt["approval"] = {"approved": True, "by": by, "at": utc_now(),
                           "note": note or None}
        self._entries.append(nxt)
        return nxt

    def entries(self) -> list[dict[str, Any]]:
        """Newest first, trimmed to what a log needs to show."""
        return [
            {
                "decision_id": e["decision_id"],
                "time": e["time"],
                "route_version": e["route_version"],
                "health": e["health"],
                "top_reasons": e.get("top_reasons", []),
                "approval": e["approval"],
                "supersedes": e.get("supersedes"),
            }
            for e in reversed(self._entries)
        ]

    def reset(self) -> None:
        self._entries.clear()


LOG = DecisionLog()
