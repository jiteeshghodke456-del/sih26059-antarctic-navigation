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
