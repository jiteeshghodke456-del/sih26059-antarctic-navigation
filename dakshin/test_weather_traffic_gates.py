"""Slices 6 and 8: weather and traffic gates over real-data inputs."""
from decision import GateState
from gates import traffic_gate, weather_gate


def test_weather_unknown_without_data():
    g = weather_gate()
    assert g.state is GateState.UNKNOWN


def test_weather_states_and_visibility_always_unassessed():
    g = weather_gate(worst_hs_m=1.8, worst_wind_ms=8.0)
    assert g.state is GateState.PASS
    assert "visibility" in g.unassessed
    assert "assumption" in g.reason

    assert weather_gate(worst_hs_m=2.7).state is GateState.MARGINAL
    assert weather_gate(worst_hs_m=3.2).state is GateState.FAIL
    assert weather_gate(worst_wind_ms=14.5).state is GateState.MARGINAL
    assert weather_gate(worst_wind_ms=18.0).state is GateState.FAIL
    # a wave FAIL is not downgraded by calm wind
    assert weather_gate(worst_hs_m=3.2, worst_wind_ms=5.0).state is GateState.FAIL


def test_weather_reports_missing_component():
    g = weather_gate(worst_hs_m=1.0)
    assert "wind" in g.unassessed


def test_traffic_unknown_without_feed():
    assert traffic_gate().state is GateState.UNKNOWN


def test_traffic_bands():
    assert traffic_gate(True, None, 0).state is GateState.PASS
    assert traffic_gate(True, 8.0, 1).state is GateState.PASS
    assert traffic_gate(True, 3.5, 2).state is GateState.MARGINAL
    assert traffic_gate(True, 1.2, 1).state is GateState.FAIL
    assert "assumption" in traffic_gate(True, 1.2, 1).reason
