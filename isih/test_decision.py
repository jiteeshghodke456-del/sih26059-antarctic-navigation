"""Tests for the decision object, gates, and route health.

These assert semantics, not plumbing. The rule most worth protecting is that
an UNKNOWN gate never reads as a pass — if someone later "simplifies" that
away, a route with no chart data and no weather data would report VALID, and
the system would be confidently wrong in exactly the direction §48A.12 says
is expensive.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ISIH = Path(__file__).resolve().parent
if str(ISIH) not in sys.path:
    sys.path.insert(0, str(ISIH))

from decision import (  # noqa: E402
    GATES,
    Alternative,
    Approval,
    Decision,
    Evidence,
    GateResult,
    GateState,
    Health,
    gate_digest,
    health_from_gates,
)


def gate(name: str, state: GateState, reason: str = "r", **kw) -> GateResult:
    return GateResult(gate=name, state=state, reason=reason, **kw)


def all_passing() -> list[GateResult]:
    return [gate(g, GateState.PASS) for g in GATES]


def test_all_gates_pass_is_the_only_route_to_valid():
    health, binding = health_from_gates(all_passing())
    assert health is Health.VALID
    assert binding == []


def test_unknown_gate_caps_health_at_degraded():
    """The load-bearing rule: we cannot certify a route we cannot see."""
    gates = all_passing()
    gates[1] = gate("chart", GateState.UNKNOWN, "no bathymetry loaded into the mesh")
    health, binding = health_from_gates(gates)
    assert health is Health.DEGRADED
    assert [g.gate for g in binding] == ["chart"]


def test_unknown_is_not_pass():
    """Stated separately because it is the assumption most likely to rot."""
    assert health_from_gates([gate("weather", GateState.UNKNOWN)])[0] is not Health.VALID


def test_failing_now_is_invalid_but_failing_later_is_critical():
    """The distinction that lets a ship keep steaming while the plan is doomed."""
    now = health_from_gates([*all_passing()[:-1], gate("ice", GateState.FAIL)])[0]
    later = health_from_gates(
        [*all_passing()[:-1], gate("ice", GateState.FAIL, fails_in_hours=36.0)]
    )[0]
    assert now is Health.INVALID
    assert later is Health.CRITICAL


def test_worst_gate_wins():
    gates = [
        gate("ice", GateState.FAIL),
        gate("weather", GateState.MARGINAL),
        gate("chart", GateState.UNKNOWN),
    ]
    assert health_from_gates(gates)[0] is Health.INVALID


def test_binding_gates_lead_with_the_sharpest_reason():
    """§32 asks for the top three reasons; failures must come first."""
    gates = [
        gate("chart", GateState.UNKNOWN, "no survey"),
        gate("ice", GateState.FAIL, "80% ice at leg 22"),
        gate("weather", GateState.MARGINAL, "swell rising"),
    ]
    # All three are DEGRADED-or-worse, but INVALID wins, so only the failure binds.
    health, binding = health_from_gates(gates)
    assert health is Health.INVALID
    assert binding[0].gate == "ice"


def test_no_gates_evaluated_is_not_a_healthy_route():
    assert health_from_gates([])[0] is Health.DEGRADED


def test_unknown_gate_name_is_rejected():
    """Typos must not silently create a tenth gate nobody evaluates."""
    with pytest.raises(ValueError):
        GateResult(gate="vibes", state=GateState.PASS, reason="")


def test_digest_ignores_ordering_but_not_content():
    """'The assumption changed' must be distinguishable from 'data arrived'."""
    a = [gate("ice", GateState.PASS, "12% ice"), gate("chart", GateState.UNKNOWN, "none")]
    b = list(reversed(a))
    assert gate_digest(a) == gate_digest(b)

    changed = [gate("ice", GateState.MARGINAL, "12% ice"), a[1]]
    assert gate_digest(changed) != gate_digest(a)


def test_same_evidence_twice_produces_no_transition():
    """Re-running the evaluation unchanged must not degrade the route."""
    gates = all_passing()
    assert gate_digest(gates) == gate_digest(list(gates))


def _decision(**kw) -> Decision:
    base = dict(
        decision_id="D-001",
        time="2019-12-01T00:00:00+00:00",
        vessel_state={"name": "MV Vasiliy Golovnin", "imo": "8723426"},
        route_version=1,
        environmental_state={"sic_source": "NSIDC CDR G02202 v6"},
    )
    base.update(kw)
    return Decision(**base)


def test_recommendation_answers_all_eight_questions():
    """§11 lists eight questions a recommendation MUST answer."""
    d = _decision(
        gates=[
            gate(
                "ice",
                GateState.FAIL,
                "station cell at 92% ice, above the working limit",
                evidence=[
                    Evidence(
                        source="NSIDC CDR G02202 v6",
                        detail="sic 0.92 at Bharati cell",
                        provenance="isih/figures/destination_window.json",
                        age_hours=18.0,
                    )
                ],
            )
        ],
        alternatives=[Alternative(label="B: approach 100 km N", summary="", eta_delta_days=0.4)],
        trigger_conditions=["station cell drops below the working ice limit"],
        recommendation="Hold at the approach rather than close the station cell.",
    )
    answers = d.recommendation_answers()
    assert len(answers) == 8
    assert all(v for v in answers.values()), answers
    assert "ice gate" in answers["Which constraint is now binding?"]
    assert "18.0 h" in answers["How fresh is that evidence?"]


def test_decision_serialises_with_health_and_reasons():
    d = _decision(gates=[gate("chart", GateState.UNKNOWN, "no bathymetry in the mesh")])
    doc = d.as_dict()
    assert doc["health"] == "DEGRADED"
    assert doc["binding_gates"] == ["chart"]
    assert doc["top_reasons"] == ["no bathymetry in the mesh"]
    assert doc["approval"]["approved"] is False


def test_a_decision_is_unapproved_until_a_human_approves_it():
    """Global rule 12: human approval is mandatory for route decisions."""
    assert _decision().approval.approved is False
    approved = _decision(approval=Approval(approved=True, by="Master", at="2019-12-01T06:00:00Z"))
    assert approved.approval.approved is True
    assert approved.approval.by == "Master"


def test_every_gate_has_a_question():
    """A gate with no stated question cannot be explained to a master."""
    for g in GATES:
        assert GateResult(gate=g, state=GateState.PASS, reason="").assumption
