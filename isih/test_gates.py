"""Tests for the nine decision gates.

Several of these assert that a gate is UNKNOWN. That looks like testing for
absence, but it is the point: each one pins a specific honesty claim we make
on stage, and if someone later wires a placeholder into the weather gate to
make the panel look complete, the test fails and says so.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ISIH = Path(__file__).resolve().parent
if str(ISIH) not in sys.path:
    sys.path.insert(0, str(ISIH))

from decision import GateState, Health, health_from_gates  # noqa: E402
import gates as G  # noqa: E402

VESSEL = {
    "name": "MV Vasiliy Golovnin",
    "beam": 22.4,
    "max_speed": 30.4,
    "force_limit": 96634.5,
    "min_depth": 20,
    "max_ice_conc": 80,
}

# The real mesh's data sources, as recorded in isih/figures/routes.json.
MESH_NO_BATHY = {
    "mesh_info": {
        "data_sources": [
            {"loader": "scalar_csv"},
            {"loader": "thickness"},
            {"loader": "density"},
        ]
    }
}


def test_capability_is_unknown_without_a_polar_ship_certificate():
    g = G.capability_gate(VESSEL)
    assert g.state is GateState.UNKNOWN
    assert "Polar Ship Certificate" in g.reason  # names its blocker
    # The uncalibrated force limit must be visible in the evidence, not buried.
    assert "UNCALIBRATED" in g.evidence[0].detail


def test_chart_gate_catches_the_inert_minimum_depth_constraint():
    """min_depth is configured but the mesh has no bathymetry to apply it to."""
    g = G.chart_gate(MESH_NO_BATHY, VESSEL)
    assert g.state is GateState.UNKNOWN
    assert "20 m minimum-depth constraint has no data to act on" in g.reason


def test_chart_gate_passes_once_bathymetry_is_loaded():
    mesh = {"mesh_info": {"data_sources": [{"loader": "bathymetry"}]}}
    assert G.chart_gate(mesh, VESSEL).state is GateState.PASS


def test_ice_gate_boundaries():
    assert G.ice_gate(50.0, 80.0).state is GateState.PASS
    assert G.ice_gate(77.0, 80.0).state is GateState.MARGINAL
    assert G.ice_gate(92.0, 80.0).state is GateState.FAIL
    assert G.ice_gate(None, 80.0).state is GateState.UNKNOWN


def test_the_marginal_band_is_the_retrievals_own_uncertainty():
    """The band was 5 points for no reason. It is now one median standard
    deviation of the CDR's own published per-pixel uncertainty across the
    70-90% band — 7.4 points, measured. A threshold in a safety-adjacent
    system has to come from somewhere."""
    assert G.MARGINAL_BAND_PCT == 7.4
    assert "standard deviation" in G.MARGINAL_BAND_BASIS
    assert "cdr_seaice_conc_stdev" in G.MARGINAL_BAND_BASIS

    # Either side of the band, on a 80% limit.
    assert G.ice_gate(73.0, 80.0).state is GateState.MARGINAL   # 7.0 points
    assert G.ice_gate(72.0, 80.0).state is GateState.PASS       # 8.0 points

    # And the reason says WHY it is marginal, not merely that it is.
    assert "not measurable" in G.ice_gate(73.0, 80.0).reason


def test_ice_gate_keeps_the_assumed_limit_caveat_attached():
    """Ice class is about thickness; a concentration limit is our assumption."""
    g = G.ice_gate(92.0, 80.0)
    assert "assumption, not a certificated one" in g.reason


def test_ice_failure_ahead_of_the_ship_is_critical_not_invalid():
    g = G.ice_gate(92.0, 80.0, at_leg=22, fails_in_hours=30.0)
    assert health_from_gates([g])[0] is Health.CRITICAL


def test_never_scored_destination_is_unknown_not_closed():
    """The exact bug that once shipped as 'Maitri closed 31 of 31 days'."""
    g = G.logistics_gate(None, "Maitri (Leningradskaya coast)")
    assert g.state is GateState.UNKNOWN
    assert "never scored" in g.reason
    assert g.state is not GateState.FAIL


def test_logistics_pass_and_fail():
    assert G.logistics_gate(True, "Bharati").state is GateState.PASS
    assert G.logistics_gate(False, "Bharati", days_closed=23, days_total=31).state is GateState.FAIL


def test_contingency_needs_more_than_one_route():
    assert G.contingency_gate(0).state is GateState.FAIL
    assert G.contingency_gate(1).state is GateState.MARGINAL
    assert G.contingency_gate(3).state is GateState.PASS


def test_weather_gate_refuses_to_call_ice_drift_weather():
    """We hold CMEMS sithick/usi/vsi. Those are ice fields, not weather."""
    g = G.weather_gate()
    assert g.state is GateState.UNKNOWN
    assert "wind" in g.reason and "visibility" in g.reason


def test_execution_gate_is_unknown_in_replay():
    assert G.execution_gate(live_sensors=False).state is GateState.UNKNOWN
    assert G.execution_gate(live_sensors=True).state is GateState.PASS


def test_every_unknown_gate_names_what_would_settle_it():
    """UNKNOWN must be a costed roadmap item, not a shrug."""
    gs = G.evaluate_all(
        vessel=VESSEL,
        mesh_config=MESH_NO_BATHY,
        worst_ice_pct=79.0,
        ice_limit_pct=80.0,
        destination_open=False,
        destination="Bharati",
        n_alternatives=0,
    )
    for g in gs:
        if g.state is GateState.UNKNOWN:
            assert g.gate in G.BLOCKED_ON, f"{g.gate} is UNKNOWN with no stated blocker"
            assert G.BLOCKED_ON[g.gate] in g.reason or "never scored" in g.reason


def test_evaluate_all_returns_all_nine_gates_in_order():
    gs = G.evaluate_all(
        vessel=VESSEL,
        mesh_config=MESH_NO_BATHY,
        worst_ice_pct=79.0,
        ice_limit_pct=80.0,
        destination_open=True,
        destination="Bharati",
        n_alternatives=2,
    )
    from decision import GATES

    assert [g.gate for g in gs] == list(GATES)


def test_todays_honest_answer_is_that_the_route_cannot_be_certified():
    """The headline claim: this prototype cannot call any route VALID.

    Six of nine gates have no data behind them. If this test ever fails
    because health became VALID, someone has either wired in the missing
    datasets (good — update this test) or faked a gate (bad).
    """
    gs = G.evaluate_all(
        vessel=VESSEL,
        mesh_config=MESH_NO_BATHY,
        worst_ice_pct=79.0,
        ice_limit_pct=80.0,
        destination_open=True,
        destination="Bharati",
        n_alternatives=2,
    )
    health, binding = health_from_gates(gs)
    assert health is not Health.VALID
    cov = G.coverage_summary(gs)
    assert cov["gates_total"] == 9
    assert cov["gates_unknown"] == 6, cov
    assert cov["gates_evaluated"] == 3
    # And every unknown gate says what it needs.
    assert all(u["needs"] for u in cov["unknown"])


def test_gate_states_match_the_real_repo_mesh():
    """Guard against the mesh silently gaining or losing a data source."""
    routes = ISIH / "figures" / "routes.json"
    if not routes.exists():
        return
    cfg = json.loads(routes.read_text())
    loaders = [s.get("loader") for s in cfg["config"]["mesh_info"]["data_sources"]]
    assert "scalar_csv" in loaders
    assert not any(l in ("bathymetry", "gebco", "depth") for l in loaders), (
        "mesh gained bathymetry — the chart gate can now be evaluated, update it"
    )
