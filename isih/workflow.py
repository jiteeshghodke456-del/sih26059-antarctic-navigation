"""The end-to-end passage workflow of §4, as a state machine.

§4 specifies an application flow, not a dashboard: sign in, pick a voyage,
define the mission, create the route, define waypoints and ETAs, review,
assess against forecast, read route health, approve, navigate, monitor, and —
when something changes — open a decision workspace, reassess, edit or take an
alternative, re-approve into a new route version, and go round again.

The prototype previously implemented the second half of that loop and none of
the first. This module is the missing spine. It exists as a state machine
rather than a set of screens because the ordering is the requirement: a route
cannot be approved before it has been reviewed, and it cannot be reviewed
before a mission says what "good" means.

**Mission definition is load-bearing, not ceremony.** The single most useful
finding this project has is that Bharati's own cell was closed 23 of 31 days
while the water 100 km north was open on all 31. So the mission's
`destination_policy` — must the ship reach the station, or is the approach
acceptable? — decides whether the logistics gate passes on a given day, and
therefore decides route health. Changing that one field changes the answer,
on real observations. That is why this screen is worth building rather than
staging.

Authentication here is **identity, not security**. There is no user store and
this is not a login; it records who is on watch, which is what a bridge
actually does at handover and what §11's approval record needs anyway. It is
labelled as such in the UI rather than dressed up as access control.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any

from decision import utc_now


class Stage(str, Enum):
    """Where the captain is in the passage workflow."""

    SIGN_IN = "sign_in"
    COMMAND_CENTER = "command_center"
    VOYAGE = "voyage"
    MISSION = "mission"
    ROUTE = "route"
    WAYPOINTS = "waypoints"
    REVIEW = "review"
    APPROVED = "approved"
    ACTIVE = "active"
    WORKSPACE = "workspace"


# The forward path of §4. `WORKSPACE` is entered from `ACTIVE` on a heads-up
# and leaves via one of three explicit choices, so it is not a simple next().
ORDER = [
    Stage.SIGN_IN,
    Stage.COMMAND_CENTER,
    Stage.VOYAGE,
    Stage.MISSION,
    Stage.ROUTE,
    Stage.WAYPOINTS,
    Stage.REVIEW,
    Stage.APPROVED,
    Stage.ACTIVE,
]

STAGE_TITLE = {
    Stage.SIGN_IN: "Who is on watch",
    Stage.COMMAND_CENTER: "Command centre",
    Stage.VOYAGE: "Select or create a voyage",
    Stage.MISSION: "Mission definition",
    Stage.ROUTE: "Route creation",
    Stage.WAYPOINTS: "Waypoints and ETA",
    Stage.REVIEW: "Route review and assessment",
    Stage.APPROVED: "Approved",
    Stage.ACTIVE: "Active navigation",
    Stage.WORKSPACE: "Decision workspace",
}

STAGE_ASKS = {
    Stage.SIGN_IN: "Every approval has to be attributable to a person.",
    Stage.COMMAND_CENTER: "Open a voyage, or start a new one.",
    Stage.VOYAGE: "Which passage, and when does it depart?",
    Stage.MISSION: "What has to be true for this voyage to have succeeded?",
    Stage.ROUTE: "Where does the route come from — solved, or imported?",
    Stage.WAYPOINTS: "Do the legs and their ETAs look right?",
    Stage.REVIEW: "Given the mission, is this route acceptable?",
    Stage.APPROVED: "The plan of record, and who signed it.",
    Stage.ACTIVE: "Sail it, and keep checking whether it is still true.",
    Stage.WORKSPACE: "Something changed. Keep, edit, or take an alternative?",
}


class WorkflowError(RuntimeError):
    """Raised when a step is attempted out of order or without its inputs."""


@dataclass
class Mission:
    """What has to be true for the voyage to have succeeded.

    `destination_policy` is the field that matters:

      STATION_REQUIRED  the ship must reach Bharati's own cell
      APPROACH_OK       discharging at the approach 100 km north is acceptable

    On December 2019 observations those two policies give different answers on
    23 of the 31 days, so this is a mission decision with a measurable
    operational consequence, not a preference.
    """

    destination_policy: str = "STATION_REQUIRED"
    cargo_tonnes: int | None = None
    latest_arrival: str | None = None
    notes: str = ""

    POLICIES = ("STATION_REQUIRED", "APPROACH_OK")

    def __post_init__(self) -> None:
        if self.destination_policy not in self.POLICIES:
            raise WorkflowError(
                f"destination_policy must be one of {self.POLICIES}, "
                f"got {self.destination_policy!r}"
            )

    @property
    def accepts_approach(self) -> bool:
        return self.destination_policy == "APPROACH_OK"

    def as_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["accepts_approach"] = self.accepts_approach
        d["meaning"] = (
            "Discharge at the approach 100 km north is acceptable."
            if self.accepts_approach
            else "The ship must reach Bharati's own cell."
        )
        return d


@dataclass
class Voyage:
    name: str
    origin: str = "Cape Town"
    destination: str = "Bharati"
    depart_day: str | None = None          # a date inside the replay window
    created_at: str = field(default_factory=utc_now)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RoutePlan:
    """Where the route came from. §4 allows creation or import.

    `source` is recorded because it changes what the numbers mean. A solved
    route carries the router's assumptions; an imported one carries whatever
    the exporting system assumed, which we do not know.
    """

    source: str = "solved"                  # solved | imported
    engine: str = ""
    n_waypoints: int = 0
    total_days: float | None = None

    SOURCES = ("solved", "imported")

    def __post_init__(self) -> None:
        if self.source not in self.SOURCES:
            raise WorkflowError(f"route source must be one of {self.SOURCES}")

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Step:
    """One completed transition, for the audit trail §48A.23 wants."""

    stage: str
    at: str
    by: str | None
    detail: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class Workflow:
    """The passage workflow for one session.

    Every advance is guarded. The guards are the point: §4 is an ordering
    requirement, and a UI that lets a captain approve a route before a mission
    exists has not implemented it, however many panels it shows.
    """

    def __init__(self) -> None:
        self.stage: Stage = Stage.SIGN_IN
        self.watchkeeper: str | None = None
        self.voyage: Voyage | None = None
        self.mission: Mission | None = None
        self.route_plan: RoutePlan | None = None
        self.waypoints_confirmed: bool = False
        self.history: list[Step] = []

    # ---------------- helpers ----------------

    def _record(self, stage: Stage, detail: str) -> None:
        self.history.append(
            Step(stage=stage.value, at=utc_now(), by=self.watchkeeper, detail=detail)
        )

    def _require(self, *stages: Stage) -> None:
        if self.stage not in stages:
            want = ", ".join(s.value for s in stages)
            raise WorkflowError(
                f"cannot do that from {self.stage.value}; this step follows {want}"
            )

    # ---------------- the forward path ----------------

    def sign_in(self, name: str) -> None:
        """Identity, not access control. Recorded so approvals are attributable.

        Guarded to SIGN_IN. Without the guard this could be called at any
        stage and would jump silently to the command centre, losing a plan
        mid-voyage. Handing over the watch is a separate, explicit act.
        """
        self._require(Stage.SIGN_IN)
        if not name.strip():
            raise WorkflowError("a watchkeeper needs a name")
        self.watchkeeper = name.strip()
        self.stage = Stage.COMMAND_CENTER
        self._record(Stage.SIGN_IN, f"{self.watchkeeper} took the watch")

    def hand_over(self, name: str) -> None:
        """Watch handover — the bridge habit the sign-in stage really models.

        The voyage is retained; only the person changes. §38's watch model
        opens with handover, so it belongs in the workflow rather than being
        reachable only by restarting the application.
        """
        if not name.strip():
            raise WorkflowError("a watchkeeper needs a name")
        outgoing = self.watchkeeper or "nobody"
        self.watchkeeper = name.strip()
        self._record(self.stage, f"watch handed over from {outgoing} to {self.watchkeeper}")

    def open_command_center(self) -> None:
        self._require(Stage.COMMAND_CENTER, Stage.ACTIVE, Stage.APPROVED, Stage.VOYAGE)
        self.stage = Stage.COMMAND_CENTER
        self._record(Stage.COMMAND_CENTER, "opened the command centre")

    def new_voyage(self) -> None:
        """COMMAND_CENTER -> VOYAGE. Split out so VOYAGE is a real resting
        stage; previously it was in ORDER but nothing ever set it, so the
        step counter jumped from 2 straight to 4."""
        self._require(Stage.COMMAND_CENTER)
        self.stage = Stage.VOYAGE
        self._record(Stage.VOYAGE, "started a new voyage")

    def start_voyage(self, name: str, destination: str, depart_day: str) -> None:
        self._require(Stage.VOYAGE)
        self.voyage = Voyage(name=name, destination=destination, depart_day=depart_day)
        self.stage = Stage.MISSION
        self._record(Stage.VOYAGE, f"{name}: Cape Town to {destination}, departing {depart_day}")

    def define_mission(self, mission: Mission) -> None:
        self._require(Stage.MISSION)
        if self.voyage is None:
            raise WorkflowError("a mission needs a voyage first")
        self.mission = mission
        self.stage = Stage.ROUTE
        self._record(Stage.MISSION, mission.as_dict()["meaning"])

    def set_route(self, plan: RoutePlan) -> None:
        self._require(Stage.ROUTE)
        if self.mission is None:
            raise WorkflowError("a route needs a mission first — otherwise there is "
                                "no definition of an acceptable one")
        self.route_plan = plan
        self.stage = Stage.WAYPOINTS
        self._record(Stage.ROUTE, f"{plan.source} route, {plan.n_waypoints} waypoints")

    def confirm_waypoints(self) -> None:
        self._require(Stage.WAYPOINTS)
        self.waypoints_confirmed = True
        self.stage = Stage.REVIEW
        self._record(Stage.WAYPOINTS, "waypoints and ETAs confirmed")

    def to_review(self) -> None:
        self._require(Stage.WAYPOINTS, Stage.REVIEW)
        self.stage = Stage.REVIEW

    def approve(self, health: str) -> None:
        """§4 and global rule 12: a human approves, and it is attributable.

        REVIEW only. Approving straight from the workspace would let a master
        adopt a corridor whose waypoints were never shown — §4 routes every
        change back through review for exactly that reason.
        """
        self._require(Stage.REVIEW)
        if not self.waypoints_confirmed:
            raise WorkflowError("waypoints have not been confirmed")
        if self.watchkeeper is None:
            raise WorkflowError("nobody is signed in; an approval must be attributable")
        self.stage = Stage.APPROVED
        self._record(Stage.APPROVED, f"approved with route health {health}")

    def begin_navigation(self) -> None:
        self._require(Stage.APPROVED, Stage.ACTIVE)
        self.stage = Stage.ACTIVE
        self._record(Stage.ACTIVE, "under way")

    # ---------------- the monitoring loop ----------------

    def open_workspace(self, reason: str) -> None:
        """Entered from a heads-up while under way."""
        self._require(Stage.ACTIVE, Stage.WORKSPACE)
        self.stage = Stage.WORKSPACE
        self._record(Stage.WORKSPACE, f"opened after: {reason}")

    def keep_plan(self, why: str) -> None:
        """One of §4's three choices, and the one most systems forget to offer.

        Deciding that a changed environment does not change the plan is a
        decision, and it belongs in the log next to the others.
        """
        self._require(Stage.WORKSPACE)
        self.stage = Stage.ACTIVE
        self._record(Stage.ACTIVE, f"kept the existing plan — {why}")

    def take_alternative(self, label: str, why: str) -> None:
        """Adopt a different corridor — which means new waypoints and new ETAs.

        Lands at WAYPOINTS, not REVIEW. A different corridor has a different
        track (41 legs at the 80% limit, 51 at 55%), so its legs must be put
        in front of the master before it can be approved.
        """
        self._require(Stage.WORKSPACE)
        self.stage = Stage.WAYPOINTS
        self.waypoints_confirmed = False
        self._record(Stage.WAYPOINTS, f"switched to corridor {label} — {why}")

    def edit_plan(self, what: str) -> None:
        """Change a plan input, then re-walk confirmation and review.

        Also lands at WAYPOINTS. The previous version set REVIEW with
        confirmation cleared, which dead-ended the loop: confirm_waypoints
        requires WAYPOINTS and approve refuses unconfirmed waypoints, so
        nothing could close it.
        """
        self._require(Stage.WORKSPACE)
        self.stage = Stage.WAYPOINTS
        self.waypoints_confirmed = False
        self._record(Stage.WAYPOINTS, f"editing the plan: {what}")

    # ---------------- view ----------------

    @property
    def can_advance(self) -> bool:
        return self.stage is not Stage.ACTIVE

    def as_dict(self) -> dict[str, Any]:
        # WORKSPACE is not in ORDER — it is a sub-state of ACTIVE, the way an
        # ECDIS route editor is opened from route monitoring rather than being
        # a third mode. Anchoring it to ACTIVE keeps the progress bar honest;
        # previously `idx` fell through to None and every stage reported done.
        anchor = self.stage if self.stage in ORDER else Stage.ACTIVE
        idx = ORDER.index(anchor)
        return {
            "stage": self.stage.value,
            "title": STAGE_TITLE[self.stage],
            "asks": STAGE_ASKS[self.stage],
            "in_workspace": self.stage is Stage.WORKSPACE,
            "step_number": idx + 1,
            "step_count": len(ORDER),
            "order": [
                {"stage": s.value, "title": STAGE_TITLE[s],
                 "done": ORDER.index(s) < idx}
                for s in ORDER
            ],
            "watchkeeper": self.watchkeeper,
            "voyage": self.voyage.as_dict() if self.voyage else None,
            "mission": self.mission.as_dict() if self.mission else None,
            "route_plan": self.route_plan.as_dict() if self.route_plan else None,
            "waypoints_confirmed": self.waypoints_confirmed,
            "history": [h.as_dict() for h in self.history],
        }

    def reset(self) -> None:
        self.__init__()
