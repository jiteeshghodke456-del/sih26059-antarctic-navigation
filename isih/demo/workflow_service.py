"""Bind the §4 passage workflow to the real route artifacts.

`isih/workflow.py` holds the ordering rules and knows nothing about files.
This module is the join: it fills each step from what the pipeline actually
produced, and exposes one `act()` so the ordering lives in exactly one place.

The waypoint list is the clearest example of something we already had and
never showed. PolarRoute returns 41 waypoints with a cumulative transit time
at each, which is precisely §4's "waypoint + ETA definition" — it simply had
no screen. Nothing here is generated for the sake of the workflow.
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

ISIH = Path(__file__).resolve().parents[1]
if str(ISIH) not in sys.path:
    sys.path.insert(0, str(ISIH))

from workflow import (                              # noqa: E402
    Mission,
    RoutePlan,
    Stage,
    Workflow,
    WorkflowError,
)

from . import data                                  # noqa: E402

WF = Workflow()


class UnknownAction(KeyError):
    pass


def accepts_approach() -> bool:
    """Does the current mission accept discharge at the approach?

    Defaults to False when no mission has been defined, because the stricter
    reading is the safe one: assuming a relaxed mission would make the
    logistics gate pass on days the station is genuinely closed.
    """
    return bool(WF.mission and WF.mission.accepts_approach)


def waypoints() -> dict[str, Any]:
    """Legs with cumulative ETA, for §4's waypoint step.

    Times are stamped from the voyage's departure day when one has been set,
    so the column reads as dates a master can check rather than as elapsed
    decimals.
    """
    r = data.route()
    coords = r["coords"]
    cum = r.get("traveltime_cumulative") or []
    depart = None
    if WF.voyage and WF.voyage.depart_day:
        depart = datetime.strptime(WF.voyage.depart_day, "%Y-%m-%d")

    rows = []
    for i, (lon, lat) in enumerate(coords):
        days = cum[i] if i < len(cum) else None
        eta = None
        if depart is not None and days is not None:
            eta = (depart + timedelta(days=float(days))).strftime("%d %b %H:%M")
        rows.append({
            "n": i,
            "lat": lat,
            "lon": lon,
            "elapsed_days": round(days, 3) if days is not None else None,
            "eta": eta,
            "is_first": i == 0,
            "is_last": i == len(coords) - 1,
        })
    return {
        "waypoints": rows,
        "count": len(rows),
        "total_days": r["total_traveltime_days"],
        "engine": r["engine"],
        "note": ("Cumulative transit times come from PolarRoute's own per-leg "
                 "solution. Steaming time only — no waiting, no weather, no "
                 "station operations."),
    }


def preview(day: str) -> dict[str, Any]:
    """What each corridor would mean if the ship departed on `day`.

    Read-only and side-effect free: it touches neither the workflow nor the
    decision log, so opening the what-if cannot advance the passage. A test
    asserts /api/workflow is byte-identical either side of a call.

    Every number is read from artifacts already on disk. The only computation
    is the ice gate, evaluated with each corridor's own worst-ice figure
    against its own limit — the same function the console already trusts. The
    arrival reading is the honest addition: a corridor that gets there 0.08
    days later can arrive on a day the station is shut.
    """
    import gates as G
    from decision import GateState

    doc = _load_alternatives()
    if doc is None:
        raise WorkflowError("alternatives not computed — run isih/alternatives.py")

    dates = data.dates()
    w = data.window()
    approach = accepts_approach()
    target = APPROACH_NAME if approach else "Bharati"

    def open_on(iso: str) -> bool | None:
        for row in w.get("daily", []):
            if row.get("date") == iso and target in row:
                v = row[target].get("sic_qa_on")
                return None if v is None else bool(row[target].get("passable"))
        return None

    def label(state: bool | None) -> str:
        if state is None:
            return "not scored"
        return "open" if state else "closed"

    rows = []
    for c in doc.get("corridors", []):
        arrival = None
        if c.get("solved") and c.get("traveltime_days") is not None:
            i = dates.index(day) + int(c["traveltime_days"])
            arrival = dates[i] if i < len(dates) else None

        gate = (G.ice_gate(c.get("worst_ice_pct"), float(c["ice_limit_pct"]))
                if c.get("solved") else None)

        rows.append({
            "label": c["label"],
            "name": c["name"],
            "solved": bool(c.get("solved")),
            "legs": c.get("legs"),
            "traveltime_days": c.get("traveltime_days"),
            "eta_delta_days": c.get("eta_delta_days"),
            "worst_ice_pct": c.get("worst_ice_pct"),
            "ice_limit_pct": c["ice_limit_pct"],
            "ice_gate": gate.state.value if gate else None,
            "ice_reason": gate.reason if gate else c.get("why"),
            "arrival_day": arrival,
            "destination_on_departure": label(open_on(day)),
            "destination_on_arrival": (
                label(open_on(arrival)) if arrival else
                ("outside the replay window" if c.get("solved") else "—")
            ),
        })

    return {
        "day": day,
        "target": target,
        "mission_accepts_approach": approach,
        "corridors": rows,
        "provenance": "isih/figures/alternatives.json",
        "scope": ("Corridors were solved on 1 Dec 2019 ice and held fixed. "
                  "Changing the departure day changes the ETAs and the "
                  "destination reading, not the geometry."),
        "router": doc.get("router", ""),
    }


def _load_alternatives():
    from . import decision_service
    return decision_service.alternatives_doc()


APPROACH_NAME = "Bharati approach (100 km N)"


def state() -> dict[str, Any]:
    """Workflow state, plus what the current step needs to offer."""
    doc = WF.as_dict()
    doc["mode"] = "monitoring" if WF.stage in (Stage.ACTIVE, Stage.WORKSPACE) else "planning"
    doc["accepts_approach"] = accepts_approach()

    if WF.stage is Stage.VOYAGE or WF.stage is Stage.COMMAND_CENTER:
        doc["choices"] = {
            "destinations": ["Bharati", "Bharati approach (100 km N)"],
            "days": data.dates(),
        }
    if WF.stage is Stage.MISSION:
        doc["choices"] = {
            "policies": [
                {"value": "STATION_REQUIRED",
                 "label": "The ship must reach Bharati's own cell",
                 "consequence": "The station cell was closed 23 of 31 days in this window."},
                {"value": "APPROACH_OK",
                 "label": "Discharge at the approach 100 km north is acceptable",
                 "consequence": "The approach was open on all 31 days."},
            ]
        }
    if WF.stage is Stage.ROUTE:
        r = data.route()
        doc["choices"] = {
            "sources": [
                {"value": "solved", "label": f"Solve with {r['engine']}",
                 "detail": f"{r['n_legs']} legs, {r['total_traveltime_days']:.2f} days"},
                {"value": "imported", "label": "Import a passage plan",
                 "detail": "Not available in this build — an imported plan carries "
                           "assumptions we cannot inspect."},
            ]
        }
    return doc


def act(action: str, body: dict[str, Any]) -> dict[str, Any]:
    """Perform one workflow step. Raises WorkflowError if out of order."""
    if action == "sign-in":
        WF.sign_in(body.get("name", ""))

    elif action == "command-center":
        WF.open_command_center()

    elif action == "new-voyage":
        WF.new_voyage()

    elif action == "hand-over":
        WF.hand_over(body.get("name", ""))

    elif action == "voyage":
        dest = body.get("destination", "Bharati")
        day = body.get("depart_day") or data.dates()[0]
        if day not in data.dates():
            raise WorkflowError(f"{day} is outside the replay window")
        WF.start_voyage(
            name=body.get("name") or f"Cape Town to {dest}",
            destination=dest,
            depart_day=day,
        )

    elif action == "mission":
        WF.define_mission(Mission(
            destination_policy=body.get("destination_policy", "STATION_REQUIRED"),
            cargo_tonnes=body.get("cargo_tonnes"),
            latest_arrival=body.get("latest_arrival"),
            notes=body.get("notes", ""),
        ))

    elif action == "route":
        src = body.get("source", "solved")
        if src == "imported":
            raise WorkflowError(
                "Importing a passage plan is not available in this build. An "
                "imported route carries the exporting system's assumptions, and "
                "we would be unable to state them — see docs/RELEASE_AUDIT.md."
            )
        r = data.route()
        WF.set_route(RoutePlan(source="solved", engine=r["engine"],
                               n_waypoints=len(r["coords"]),
                               total_days=r["total_traveltime_days"]))

    elif action == "waypoints":
        WF.confirm_waypoints()

    elif action == "approve":
        from . import decision_service
        day = (WF.voyage.depart_day if WF.voyage else None)
        dec = decision_service.LOG.current(day, accepts_approach())
        WF.approve(dec["health"])
        decision_service.LOG.approve(
            by=WF.watchkeeper or "unattributed",
            note=body.get("why", ""),
            day=day,
            accepts_approach=accepts_approach(),
        )

    elif action == "navigate":
        WF.begin_navigation()

    elif action == "workspace":
        WF.open_workspace(body.get("reason", "an assumption changed"))

    elif action == "keep":
        # §4's third choice, and the one most systems forget. Keeping the plan
        # must re-approve it, or the console goes on reporting "the evidence
        # has moved" forever and the master has no way to say "I have seen
        # that, and it does not change the plan". Deciding to change nothing
        # is a decision, so it gets a version and an attribution like any
        # other.
        from . import decision_service
        why = body.get("why") or "no stated reason"
        WF.keep_plan(why)
        decision_service.LOG.approve(
            by=WF.watchkeeper or "unattributed",
            note=f"kept the existing plan — {why}",
            day=body.get("day") or (WF.voyage.depart_day if WF.voyage else None),
            accepts_approach=accepts_approach(),
        )

    elif action == "alternative":
        WF.take_alternative(body.get("label", "B"),
                            body.get("why") or "no stated reason")

    elif action == "edit":
        WF.edit_plan(body.get("what") or "unspecified change")

    elif action == "reset":
        WF.reset()
        from . import decision_service
        decision_service.LOG.reset()

    else:
        raise UnknownAction(f"unknown workflow action {action!r}")

    return state()
