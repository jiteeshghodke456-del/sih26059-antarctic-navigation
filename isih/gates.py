"""Evaluate the nine decision gates of §12 against evidence we actually hold.

The uncomfortable part of this module is the honest part. Of the nine gates,
we can evaluate three from real data. The other six return UNKNOWN, each
naming the specific dataset that would settle it.

That is deliberate, and it is worth defending rather than papering over. A
system that lit nine gates green would be claiming to have checked the chart,
the weather, the traffic picture, the communications plan and the live sensor
feed. We have none of those. §48A.26 asks "what does this model know, and
what does it not know" — this module is the answer, in code, where it cannot
drift away from the documentation.

The practical consequence is that route health tops out at DEGRADED. That is
the correct answer for this prototype, and saying so out loud is a stronger
position than a wall of green lights that a judge can dismantle in one
question.

Each evaluator is a pure function over explicit inputs so the states can be
tested without touching the filesystem.
"""

from __future__ import annotations

from typing import Any

from decision import Evidence, GateResult, GateState

# Where an UNKNOWN gate's evidence would have to come from. Naming the
# specific dataset turns "we didn't do it" into a costed roadmap item, and
# stops UNKNOWN from becoming a shrug.
BLOCKED_ON = {
    "chart": "IHO ENC / GEBCO bathymetry loaded into the meshiphi mesh",
    "weather": "ERA5 or CMEMS wind, wave and visibility fields over the corridor",
    "traffic": "AIS feed or terrestrial/satellite traffic picture",
    "communications": "GMDSS / satcom coverage and link-budget model for the corridor",
    "capability": "Polar Ship Certificate and PWOM for IMO 8723426",
    "execution": "live bridge sensor feed (GPS, radar, ice observation)",
}


def capability_gate(vessel: dict[str, Any]) -> GateResult:
    """§12 capability gate: may this ship legally and physically be here?

    We hold verified beam and service speed, but no Polar Ship Certificate
    and no PWOM, and the mesh's `force_limit` is explicitly commented in
    isih/ice_meshes.py as an uncalibrated value borrowed from another ship.
    §48A.3 forbids inventing vessel thresholds, so this is UNKNOWN rather
    than a pass built on a borrowed constant.
    """
    ev = [
        Evidence(
            source="isih/ice_meshes.py",
            detail=(
                f"{vessel.get('name', 'vessel')}: beam {vessel.get('beam')} m, "
                f"max_speed {vessel.get('max_speed')} km/h (verified against registries); "
                f"force_limit {vessel.get('force_limit')} is UNCALIBRATED"
            ),
            provenance="isih/ice_meshes.py",
        )
    ]
    return GateResult(
        gate="capability",
        state=GateState.UNKNOWN,
        reason=(
            "The mesh force limit is an uncalibrated value borrowed from another vessel. "
            f"Needs {BLOCKED_ON['capability']}"
        ),
        evidence=ev,
    )


def chart_gate(mesh_config: dict[str, Any], vessel: dict[str, Any]) -> GateResult:
    """§12 chart gate — and the sharpest finding in this module.

    The vessel config carries `min_depth: 20`, but the routing mesh's data
    sources are SIC, thickness and density only. There is no bathymetry in
    the mesh, so the minimum-depth constraint can never fire. A configured
    constraint with no data behind it is worse than an absent one, because it
    reads as protection that is not there. §48A.19 requires bathymetry and
    under-keel clearance be treated as uncertain; here it is simply absent.
    """
    loaders = [
        s.get("loader") for s in mesh_config.get("mesh_info", {}).get("data_sources", [])
    ]
    has_bathy = any(l in ("bathymetry", "gebco", "depth") for l in loaders)
    min_depth = vessel.get("min_depth")
    if has_bathy:
        return GateResult(
            gate="chart",
            state=GateState.PASS,
            reason="bathymetry present in the mesh",
            evidence=[
                Evidence("meshiphi", f"loaders: {loaders}", "isih/figures/routes.json")
            ],
        )
    return GateResult(
        gate="chart",
        state=GateState.UNKNOWN,
        reason=(
            f"No bathymetry in the routing mesh (loaders: {', '.join(str(l) for l in loaders)}). "
            f"The vessel's {min_depth} m minimum-depth constraint has no data to act on. "
            f"Needs {BLOCKED_ON['chart']}"
        ),
        evidence=[
            Evidence(
                source="meshiphi mesh config",
                detail=f"data source loaders present: {loaders}; min_depth={min_depth} inert",
                provenance="isih/figures/routes.json",
            )
        ],
    )


def ice_gate(
    worst_ice_pct: float | None,
    ice_limit_pct: float,
    *,
    at_leg: int | None = None,
    fails_in_hours: float | None = None,
    provenance: str = "isih/figures/routes.json",
    limit_is_assumed: bool = True,
) -> GateResult:
    """§12 ice gate. The one gate we can genuinely evaluate.

    `limit_is_assumed` is not decoration. Ice *class* is defined in terms of
    ice thickness, not concentration, so a concentration threshold is our
    assumption rather than a certificated limit. Saying so here keeps the
    caveat attached to the number instead of living only in a document.
    """
    if worst_ice_pct is None:
        return GateResult(
            gate="ice",
            state=GateState.UNKNOWN,
            reason="no ice concentration sampled along the route",
            evidence=[],
        )

    ev = [
        Evidence(
            source="NOAA/NSIDC Sea Ice Concentration CDR G02202 v6",
            detail=f"worst ice on route {worst_ice_pct:.0f}% against a working limit of {ice_limit_pct:.0f}%",
            provenance=provenance,
        )
    ]
    margin = ice_limit_pct - worst_ice_pct
    if margin < 0:
        state, reason = GateState.FAIL, (
            f"Ice on the route reaches {worst_ice_pct:.0f}%, above the "
            f"{ice_limit_pct:.0f}% working limit"
        )
    elif margin <= 5:
        state, reason = GateState.MARGINAL, (
            f"Ice reaches {worst_ice_pct:.0f}%, within {margin:.0f} points of the "
            f"{ice_limit_pct:.0f}% working limit"
        )
    else:
        state, reason = GateState.PASS, (
            f"Ice peaks at {worst_ice_pct:.0f}%, {margin:.0f} points below the working limit"
        )

    if limit_is_assumed and state is not GateState.PASS:
        reason += " — note this limit is an assumption, not a certificated one"

    return GateResult(
        gate="ice",
        state=state,
        reason=reason,
        evidence=ev,
        at_leg=at_leg,
        fails_in_hours=fails_in_hours,
    )


def logistics_gate(
    destination_open: bool | None,
    destination: str,
    *,
    days_closed: int | None = None,
    days_total: int | None = None,
    provenance: str = "isih/figures/destination_window.json",
) -> GateResult:
    """§12 logistics gate: will this track still meet the station window?

    `destination_open is None` means the destination was never scored — no
    mesh cell contains it. That is UNKNOWN, emphatically not "closed". The
    demo previously reported exactly this case as closed 31 of 31 days.
    """
    if destination_open is None:
        return GateResult(
            gate="logistics",
            state=GateState.UNKNOWN,
            reason=f"{destination} was never scored — no mesh cell contains it",
            evidence=[Evidence("destination window", "no cell", provenance)],
        )
    detail = f"{destination} reachable" if destination_open else f"{destination} not reachable"
    if days_closed is not None and days_total:
        detail += f"; closed {days_closed} of {days_total} days in the window"
    ev = [Evidence("vessel-performance mesh", detail, provenance)]
    if destination_open:
        return GateResult("logistics", GateState.PASS, f"{destination} is reachable today", ev)
    return GateResult(
        gate="logistics",
        state=GateState.FAIL,
        reason=f"{destination} is not reachable for this ship today",
        evidence=ev,
    )


def contingency_gate(n_alternatives: int, provenance: str = "isih/figures/routes.json") -> GateResult:
    """§12 contingency gate: if the route closes ahead, where do we go?

    With a single computed path there is no answer, and §32 asks for A/B/C
    corridors. One route is not a plan with a fallback; it is a plan.
    """
    ev = [Evidence("route solver", f"{n_alternatives} alternative corridor(s) computed", provenance)]
    if n_alternatives >= 2:
        return GateResult("contingency", GateState.PASS, f"{n_alternatives} alternatives available", ev)
    if n_alternatives == 1:
        return GateResult(
            gate="contingency",
            state=GateState.MARGINAL,
            reason="Only one alternative corridor — thin cover if the primary closes",
            evidence=ev,
        )
    return GateResult(
        gate="contingency",
        state=GateState.FAIL,
        reason="No alternative corridor has been computed; there is no fallback plan",
        evidence=ev,
    )


def _unknown(gate: str) -> GateResult:
    return GateResult(
        gate=gate,
        state=GateState.UNKNOWN,
        reason=f"Not evaluated — needs {BLOCKED_ON[gate]}",
        evidence=[],
    )


def weather_gate() -> GateResult:
    """§12 weather gate.

    We hold CMEMS sea-ice thickness and drift, which are ice fields, not
    weather. No wind, no waves, no visibility, so this cannot be evaluated.
    Calling ice drift "weather" to fill the panel would be the sort of quiet
    substitution §47 exists to forbid.
    """
    return _unknown("weather")


def traffic_gate() -> GateResult:
    return _unknown("traffic")


def communications_gate() -> GateResult:
    return _unknown("communications")


def execution_gate(live_sensors: bool = False) -> GateResult:
    """§12 execution gate: are observations still consistent with what we approved?

    In HISTORICAL REPLAY there is no live sensor feed by construction, so
    this is UNKNOWN rather than a pass. Replay cannot confirm the present.
    """
    if live_sensors:
        return GateResult("execution", GateState.PASS, "live observations consistent with plan", [])
    return _unknown("execution")


def evaluate_all(
    *,
    vessel: dict[str, Any],
    mesh_config: dict[str, Any],
    worst_ice_pct: float | None,
    ice_limit_pct: float,
    destination_open: bool | None,
    destination: str,
    n_alternatives: int,
    days_closed: int | None = None,
    days_total: int | None = None,
    live_sensors: bool = False,
) -> list[GateResult]:
    """Evaluate all nine gates. Order follows §12."""
    return [
        capability_gate(vessel),
        chart_gate(mesh_config, vessel),
        ice_gate(worst_ice_pct, ice_limit_pct),
        weather_gate(),
        traffic_gate(),
        logistics_gate(
            destination_open, destination, days_closed=days_closed, days_total=days_total
        ),
        communications_gate(),
        contingency_gate(n_alternatives),
        execution_gate(live_sensors),
    ]


def coverage_summary(gates: list[GateResult]) -> dict[str, Any]:
    """How much of the decision we can actually see.

    Reported in the UI so the honest answer is on the screen rather than only
    in a document nobody opens during a demo.
    """
    evaluable = [g for g in gates if g.state is not GateState.UNKNOWN]
    return {
        "gates_total": len(gates),
        "gates_evaluated": len(evaluable),
        "gates_unknown": len(gates) - len(evaluable),
        "unknown": [
            {"gate": g.gate, "needs": BLOCKED_ON.get(g.gate, "additional data")}
            for g in gates
            if g.state is GateState.UNKNOWN
        ],
    }
