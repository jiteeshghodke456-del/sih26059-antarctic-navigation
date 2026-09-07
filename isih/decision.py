"""Decision objects, decision gates, and route health.

This is the spine the master prompt asks for in §11 (decision object model),
§12 (decision gates) and §48A.13 (route health must be a state, not a
decorative colour). Until now the product had none of it: the API was six
read-only GETs and nothing in the codebase could answer "is the approved
route still valid, and why not".

The central design choice is that **route health is derived from the gates,
never scored**. §11 says plainly that "route score = 0.82" is less useful
than an evidence-based explanation. So there is no score here. A route's
health is the worst state among nine named gates, and the gate that produced
it is carried along as the binding reason. That makes the explanation a
structural property rather than a string somebody remembered to write.

The second choice is how UNKNOWN behaves, and it is the one worth arguing
about. A gate we cannot evaluate — no bathymetry, no AIS, no wind — does not
pass. It caps health at DEGRADED. A system that reported VALID while blind to
the chart and the weather would be lying by omission, and §48A.12 is explicit
that a false negative (telling the master a route is fine when it is not) is
the expensive error in this domain. Missing evidence is therefore a reason to
be less confident, never a reason to be silent. This is the same rule the
demo already learned the hard way when never-scored destinations were being
reported as "closed 31 of 31 days".

§48A.13 also requires that a route degrade "because a meaningful operational
assumption changed, not merely because new data arrived". That is enforced in
`RouteHealth.changed_because` — a transition carries the gate and the
assumption that flipped, and re-evaluating with identical evidence produces
no transition at all.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Iterable
import hashlib
import json


class GateState(str, Enum):
    """State of one decision gate.

    UNKNOWN is not a synonym for PASS. It means we lack the evidence the
    gate needs, which is itself an operational fact the master must see.
    """

    PASS = "PASS"
    MARGINAL = "MARGINAL"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class Health(str, Enum):
    """Route health. §48A.13's four states, in worsening order."""

    VALID = "VALID"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"
    INVALID = "INVALID"


# Worsening order, used to take a maximum over gates.
_HEALTH_RANK = {Health.VALID: 0, Health.DEGRADED: 1, Health.CRITICAL: 2, Health.INVALID: 3}

# The nine gates of §12, in the order the master prompt lists them. The order
# is not cosmetic: it runs from "may this ship be here at all" to "is what we
# assumed still true right now", which is the sequence a bridge actually works
# through.
GATES = (
    "capability",
    "chart",
    "ice",
    "weather",
    "traffic",
    "logistics",
    "communications",
    "contingency",
    "execution",
)

GATE_QUESTION = {
    "capability": "Can this ship legally and physically operate here?",
    "chart": "Is the route geographically understood well enough?",
    "ice": "Will expected ice exceed the ship's operating limit?",
    "weather": "Will wind, waves or visibility make the corridor unsafe?",
    "traffic": "Is there conflict with other vessels or operations?",
    "logistics": "Will this track still meet the station's operating window?",
    "communications": "Can the ship get timely warnings and coordinate?",
    "contingency": "If the route closes ahead, where do we go?",
    "execution": "Are observations still consistent with what we approved?",
}


@dataclass(frozen=True)
class Evidence:
    """One piece of evidence behind a gate.

    `provenance` is a real path or URL, never a prose description. §15 wants
    every environmental object to state where it came from, and a string like
    "satellite data" is not that.
    """

    source: str
    detail: str
    provenance: str
    valid_time: str | None = None
    age_hours: float | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GateResult:
    gate: str
    state: GateState
    reason: str
    evidence: list[Evidence] = field(default_factory=list)
    # Where on the route the gate bites, if it does. None means "everywhere"
    # or "not location-specific".
    at_leg: int | None = None
    # Hours from decision time at which the gate is expected to fail. Only
    # meaningful when state is FAIL and the failure is ahead of the ship;
    # this is what separates CRITICAL from INVALID.
    fails_in_hours: float | None = None

    def __post_init__(self) -> None:
        if self.gate not in GATES:
            raise ValueError(f"unknown gate {self.gate!r}; expected one of {GATES}")

    @property
    def assumption(self) -> str:
        """The operational assumption this gate encodes."""
        return GATE_QUESTION[self.gate]

    def as_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["state"] = self.state.value
        d["question"] = GATE_QUESTION[self.gate]
        return d


def health_from_gates(gates: Iterable[GateResult]) -> tuple[Health, list[GateResult]]:
    """Derive route health from gate states, and name the binding gates.

    Rules, in the order they are applied:

    - a gate failing **now** makes the route INVALID;
    - a gate that will fail **later on the route** makes it CRITICAL — the
      ship can proceed, but not to the end of the plan as approved;
    - a MARGINAL gate makes it DEGRADED;
    - an UNKNOWN gate also caps at DEGRADED. We cannot certify a route we
      cannot see. See the module docstring.

    Returns the health and every gate that is responsible for it, so the UI
    can show "top three reasons" (§32) without re-deriving anything.
    """
    gates = list(gates)
    if not gates:
        # No gates evaluated at all is not a healthy route; it is an
        # unevaluated one, and saying VALID here would be the exact failure
        # this module exists to prevent.
        return Health.DEGRADED, []

    worst = Health.VALID
    for g in gates:
        if g.state is GateState.FAIL:
            level = Health.CRITICAL if (g.fails_in_hours or 0) > 0 else Health.INVALID
        elif g.state in (GateState.MARGINAL, GateState.UNKNOWN):
            level = Health.DEGRADED
        else:
            level = Health.VALID
        if _HEALTH_RANK[level] > _HEALTH_RANK[worst]:
            worst = level

    if worst is Health.VALID:
        return worst, []

    binding = [g for g in gates if _gate_level(g) is worst]
    # Failures first, then marginal, then unknown — so "top three reasons"
    # leads with the sharpest one.
    order = {GateState.FAIL: 0, GateState.MARGINAL: 1, GateState.UNKNOWN: 2, GateState.PASS: 3}
    binding.sort(key=lambda g: (order[g.state], g.fails_in_hours or 0))
    return worst, binding


def _gate_level(g: GateResult) -> Health:
    if g.state is GateState.FAIL:
        return Health.CRITICAL if (g.fails_in_hours or 0) > 0 else Health.INVALID
    if g.state in (GateState.MARGINAL, GateState.UNKNOWN):
        return Health.DEGRADED
    return Health.VALID


@dataclass
class Approval:
    """§11 approval_record. Human approval is mandatory (global rule 12)."""

    approved: bool
    by: str | None = None
    at: str | None = None
    note: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Alternative:
    """One candidate corridor. §32 wants each to carry a measurable delta.

    An alternative that does not differ measurably is not an alternative; it
    is the same plan drawn twice. Stage 05's behavioural test 7 checks this.
    """

    label: str
    summary: str
    eta_days: float | None = None
    eta_delta_days: float | None = None
    worst_ice_pct: float | None = None
    fuel: float | None = None
    fuel_delta: float | None = None
    rationale: str = ""
    provenance: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Decision:
    """§11's first-class Decision object.

    Every field the master prompt lists is present. Where we genuinely do not
    have something, the field carries an explicit marker rather than a
    plausible default — a decision object that quietly defaults its
    environmental state is worse than one that says it is missing.
    """

    decision_id: str
    time: str
    vessel_state: dict[str, Any]
    route_version: int
    environmental_state: dict[str, Any]
    hazards_considered: list[dict[str, Any]] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    gates: list[GateResult] = field(default_factory=list)
    alternatives: list[Alternative] = field(default_factory=list)
    recommendation: str = ""
    confidence: str = "UNQUANTIFIED"
    trigger_conditions: list[str] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    approval: Approval = field(default_factory=lambda: Approval(approved=False))
    supersedes: str | None = None
    data_mode: str = "HISTORICAL REPLAY"

    @property
    def health(self) -> Health:
        return health_from_gates(self.gates)[0]

    @property
    def binding_gates(self) -> list[GateResult]:
        return health_from_gates(self.gates)[1]

    def recommendation_answers(self) -> dict[str, str]:
        """The eight questions §11 says a recommendation MUST answer.

        Returned as a mapping so the UI cannot quietly omit one; a missing
        answer shows up as the literal string below rather than an absent key.
        """
        binding = self.binding_gates
        top = binding[0] if binding else None
        unanswered = "not established"
        return {
            "What changed?": self.recommendation or unanswered,
            "Why does it matter?": (top.reason if top else "no gate is binding"),
            "Which constraint is now binding?": (
                f"{top.gate} gate — {top.assumption}" if top else "none"
            ),
            "What alternatives exist?": (
                "; ".join(a.label for a in self.alternatives) if self.alternatives else unanswered
            ),
            "What is the ETA/safety tradeoff?": (
                "; ".join(
                    f"{a.label}: {a.eta_delta_days:+.2f} d" for a in self.alternatives
                    if a.eta_delta_days is not None
                ) or unanswered
            ),
            "What evidence supports the recommendation?": (
                "; ".join(e.provenance for e in (top.evidence if top else [])) or unanswered
            ),
            "How fresh is that evidence?": _freshness_phrase(top.evidence if top else []),
            "What condition would change the decision again?": (
                "; ".join(self.trigger_conditions) if self.trigger_conditions else unanswered
            ),
        }

    def as_dict(self) -> dict[str, Any]:
        health, binding = health_from_gates(self.gates)
        return {
            "decision_id": self.decision_id,
            "time": self.time,
            "data_mode": self.data_mode,
            "vessel_state": self.vessel_state,
            "route_version": self.route_version,
            "environmental_state": self.environmental_state,
            "hazards_considered": self.hazards_considered,
            "assumptions": self.assumptions,
            "constraints": self.constraints,
            "gates": [g.as_dict() for g in self.gates],
            "health": health.value,
            "binding_gates": [g.gate for g in binding],
            "top_reasons": [g.reason for g in binding[:3]],
            "alternatives": [a.as_dict() for a in self.alternatives],
            "recommendation": self.recommendation,
            "recommendation_answers": self.recommendation_answers(),
            "confidence": self.confidence,
            "trigger_conditions": self.trigger_conditions,
            "evidence": [e.as_dict() for e in self.evidence],
            "approval": self.approval.as_dict(),
            "supersedes": self.supersedes,
        }


def _freshness_phrase(evidence: list[Evidence]) -> str:
    ages = [e.age_hours for e in evidence if e.age_hours is not None]
    if not ages:
        return "age not recorded"
    return f"oldest supporting evidence {max(ages):.1f} h old"


def gate_digest(gates: Iterable[GateResult]) -> str:
    """Stable digest of gate states and reasons.

    Used to tell "the assumption changed" apart from "new data arrived":
    re-evaluating with the same evidence yields the same digest, so no
    transition is recorded. §48A.13 requires exactly that distinction.
    """
    payload = [
        {"gate": g.gate, "state": g.state.value, "reason": g.reason, "at_leg": g.at_leg}
        for g in sorted(gates, key=lambda x: x.gate)
    ]
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()[:16]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
