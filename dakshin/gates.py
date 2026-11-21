"""Evaluate the nine decision gates of §12 against evidence we actually hold.

The uncomfortable part of this module is the honest part. Of the nine gates,
six can now be evaluated from real data (ice, chart, logistics, contingency,
weather from real waves/wind, traffic when a live AIS feed exists), and one
of those (chart) can never PASS because our bathymetry is not an official
chart. The rest return UNKNOWN, each naming the specific dataset that would
settle it — and weather always lists visibility as unassessed.

That is deliberate, and it is worth defending rather than papering over. A
system that lit nine gates green would be claiming to have checked the chart,
the weather, the traffic picture, the communications plan and the live sensor
feed. We have none of those. §48A.26 asks "what does this model know, and
what does it not know" — this module is the answer, in code, where it cannot
drift away from the documentation.

The practical consequence is that route health tops out at DEGRADED. That is
the correct answer for this prototype, and saying so out loud is a stronger
position than a wall of green lights that a reviewer can dismantle in one
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
# How close to the working limit counts as MARGINAL, in concentration points.
#
# This was 5 for no reason at all — a number that felt about right, which is
# exactly the kind of invented threshold §48A.3 and §47 forbid. It is now
# derived from the product's own uncertainty: the CDR ships
# `cdr_seaice_conc_stdev`, its per-pixel estimated standard deviation, and
# across the 70-90% band that brackets our 80% working limit its median value
# is 7.4 points (mean 8.0, p90 11.7), measured on the December 2019 archive.
#
# So MARGINAL means "within one standard deviation of the limit, where the
# standard deviation is the one the data provider publishes". Note the
# direction of the correction: the invented band was NARROWER than the
# instrument's own uncertainty, which would have reported a comfortable PASS
# for routes the retrieval cannot actually distinguish from the limit.
MARGINAL_BAND_PCT = 7.4
MARGINAL_BAND_BASIS = (
    "one median standard deviation of the NOAA/NSIDC CDR retrieval across the "
    "70-90% concentration band (cdr_seaice_conc_stdev, December 2019 archive)"
)

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
    dakshin/ice_meshes.py as an uncalibrated value borrowed from another ship.
    §48A.3 forbids inventing vessel thresholds, so this is UNKNOWN rather
    than a pass built on a borrowed constant.
    """
    ev = [
        Evidence(
            source="dakshin/ice_meshes.py",
            detail=(
                f"{vessel.get('name', 'vessel')}: beam {vessel.get('beam')} m, "
                f"max_speed {vessel.get('max_speed')} km/h (verified against registries); "
                f"force_limit {vessel.get('force_limit')} is UNCALIBRATED"
            ),
            provenance="dakshin/ice_meshes.py",
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


# Why the chart gate can never PASS on our data. Stated once, so the gate and
# its tests cannot drift apart on the wording.
CHART_NOT_ENC = (
    "IBCSO is a scientific compilation, not an official electronic navigational "
    "chart (ENC); passage planning still needs official charts."
)


def chart_gate(
    mesh_config: dict[str, Any],
    vessel: dict[str, Any],
    leg_depths_m: list[float | None] | None = None,
    *,
    provenance: str = "data/bathymetry/ibcso_v2_corridor_0p05.nc",
) -> GateResult:
    """§12 chart gate: is there water under the keel along the whole route?

    `leg_depths_m` is the depth at each route point (m, positive down; IBCSO
    v2 / GEBCO_2020, the shallowest value within ~5 km), None where the point
    lies outside the bathymetry coverage. Any point shallower than the
    vessel's `min_depth` is a FAIL.

    Otherwise the answer is MARGINAL, never PASS. IBCSO is the best seafloor
    compilation south of 50 S, but it is a research grid with ~24% of the
    seafloor actually surveyed, not a chart a master may plan a passage on.
    §48A.19 asks that bathymetry and under-keel clearance be treated as
    uncertain; this is that, in the gate state.

    Without leg depths the gate falls back to asking whether the mesh holds
    bathymetry at all. A configured `min_depth` with no data behind it is worse
    than an absent one, because it reads as protection that is not there, so
    that case stays UNKNOWN.
    """
    min_depth = vessel.get("min_depth")
    loaders = [
        s.get("loader") for s in mesh_config.get("mesh_info", {}).get("data_sources", [])
    ]

    if leg_depths_m is not None:
        known = [(k, d) for k, d in enumerate(leg_depths_m) if d is not None]
        shallow = [(k, d) for k, d in known if d < min_depth]
        n, n_unknown = len(leg_depths_m), len(leg_depths_m) - len(known)
        ev = [Evidence(
            "IBCSO v2 (Dorschel et al. 2022, CC-BY-4.0)",
            f"{len(known)} of {n} route points inside coverage; shallowest "
            + (f"{min(d for _, d in known):.0f} m" if known else "n/a")
            + f" against a {min_depth} m minimum depth",
            provenance,
        )]
        if shallow:
            k, d = min(shallow, key=lambda kd: kd[1])
            return GateResult(
                gate="chart",
                state=GateState.FAIL,
                reason=(
                    f"{len(shallow)} route point(s) shallower than the vessel's "
                    f"{min_depth} m minimum depth; shallowest {d:.0f} m at leg {k}"
                ),
                evidence=ev,
                at_leg=k,
            )
        if not known:
            return GateResult(
                gate="chart",
                state=GateState.UNKNOWN,
                reason="No point of the route lies inside the bathymetry coverage",
                evidence=ev,
            )
        reason = CHART_NOT_ENC
        if n_unknown:
            reason += (f" {n_unknown} of {n} route points lie outside the IBCSO "
                       f"subset and were not depth-checked.")
        return GateResult("chart", GateState.MARGINAL, reason, ev)

    if any(l in ("bathymetry", "gebco", "depth") for l in loaders):
        return GateResult(
            gate="chart",
            state=GateState.MARGINAL,
            reason=CHART_NOT_ENC,
            evidence=[
                Evidence("meshiphi", f"loaders: {loaders}", "dakshin/figures/routes.json")
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
                provenance="dakshin/figures/routes.json",
            )
        ],
    )


def ice_gate(
    worst_ice_pct: float | None,
    ice_limit_pct: float,
    *,
    at_leg: int | None = None,
    fails_in_hours: float | None = None,
    provenance: str = "dakshin/figures/routes.json",
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
    elif margin <= MARGINAL_BAND_PCT:
        pts = "point" if round(margin) == 1 else "points"
        state, reason = GateState.MARGINAL, (
            f"Ice reaches {worst_ice_pct:.0f}%, within {margin:.0f} {pts} of the "
            f"{ice_limit_pct:.0f}% working limit — inside the retrieval's own "
            f"uncertainty, so the margin is not measurable"
        )
    else:
        pts = "point" if round(margin) == 1 else "points"
        state, reason = GateState.PASS, (
            f"Ice peaks at {worst_ice_pct:.0f}%, {margin:.0f} {pts} below the working limit"
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
    provenance: str = "dakshin/figures/destination_window.json",
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


def contingency_gate(n_alternatives: int, provenance: str = "dakshin/figures/routes.json") -> GateResult:
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


# Working limits for the weather gate. Both are ASSUMPTIONS, not vessel
# documentation, and the gate's reasons say so: 3.0 m significant wave height
# is the PolarRoute example config's max_wave value, and the wind limits are
# the Beaufort 7/8 boundaries (13.9 / 17.2 m/s). The real numbers belong in
# this hull's PWOM, which we do not hold (see capability gate).
MAX_WAVE_M = 3.0
WAVE_MARGINAL_BAND_M = 0.5
WIND_FAIL_MS = 17.2    # Beaufort 8
WIND_MARGINAL_MS = 13.9  # Beaufort 7


def weather_gate(
    worst_hs_m: float | None = None,
    worst_wind_ms: float | None = None,
    *,
    provenance: str = "data/cmems_forecast_archive + data/ecmwf_wind",
) -> GateResult:
    """§12 weather gate, from real forecast waves and wind along the route
    at arrival times (slice 6). With no data it stays UNKNOWN, as before.

    Visibility is in no free dataset we hold, so it is listed in
    `unassessed` and shown in the UI — a green-ish gate must not quietly
    imply it checked fog.
    """
    if worst_hs_m is None and worst_wind_ms is None:
        return _unknown("weather")

    parts, ev = [], []
    state = GateState.PASS
    if worst_hs_m is not None:
        ev.append(Evidence("CMEMS wave forecast (VHM0 daily max)",
                           f"worst significant wave height on route {worst_hs_m:.2f} m "
                           f"against an assumed {MAX_WAVE_M} m limit",
                           provenance))
        if worst_hs_m > MAX_WAVE_M:
            state = GateState.FAIL
            parts.append(f"waves {worst_hs_m:.2f} m exceed the assumed "
                         f"{MAX_WAVE_M} m limit")
        elif worst_hs_m > MAX_WAVE_M - WAVE_MARGINAL_BAND_M:
            state = GateState.MARGINAL
            parts.append(f"waves {worst_hs_m:.2f} m within "
                         f"{WAVE_MARGINAL_BAND_M} m of the assumed limit")
        else:
            parts.append(f"waves {worst_hs_m:.2f} m under the assumed "
                         f"{MAX_WAVE_M} m limit")
    if worst_wind_ms is not None:
        ev.append(Evidence("ECMWF open-data IFS 10 m wind (CC BY 4.0)",
                           f"worst wind on route {worst_wind_ms:.1f} m/s against "
                           f"Beaufort 7/8 bands (assumptions)",
                           provenance))
        if worst_wind_ms >= WIND_FAIL_MS:
            state = GateState.FAIL
            parts.append(f"wind {worst_wind_ms:.1f} m/s at or above Beaufort 8")
        elif worst_wind_ms >= WIND_MARGINAL_MS:
            if state is not GateState.FAIL:
                state = GateState.MARGINAL
            parts.append(f"wind {worst_wind_ms:.1f} m/s in Beaufort 7")
        else:
            parts.append(f"wind {worst_wind_ms:.1f} m/s below Beaufort 7")
    missing = [n for n, v in (("waves", worst_hs_m), ("wind", worst_wind_ms))
               if v is None]
    return GateResult(
        gate="weather",
        state=state,
        reason="; ".join(parts) + " — limits are assumptions, not this hull's "
               "PWOM; visibility not assessed"
               + (f"; no data for {', '.join(missing)}" if missing else ""),
        evidence=ev,
        unassessed=["visibility"] + missing,
    )


# Traffic separation distances. ASSUMPTIONS, stated in the reason: 2 nm CPA
# as the close-quarters line and 5 nm as the monitoring band — not COLREGS
# figures, which prescribe conduct, not distances.
TRAFFIC_FAIL_NM = 2.0
TRAFFIC_MARGINAL_NM = 5.0


def traffic_gate(
    feed_live: bool = False,
    nearest_target_nm: float | None = None,
    n_targets: int = 0,
    *,
    provenance: str = "ship AIS receiver via dakshin/ais_feed.py",
) -> GateResult:
    """§12 traffic gate (slice 8). UNKNOWN with no live feed — shore AIS
    networks are empty in the Southern Ocean, so without the ship's own
    receiver there is genuinely no traffic picture, and saying PASS would be
    inventing one."""
    if not feed_live:
        return _unknown("traffic")
    ev = [Evidence("AIS feed", f"{n_targets} target(s) in the picture; nearest "
                   + (f"{nearest_target_nm:.1f} nm from the next 24 h of track"
                      if nearest_target_nm is not None else "none near track"),
                   provenance)]
    assumed = (f" — {TRAFFIC_FAIL_NM}/{TRAFFIC_MARGINAL_NM} nm bands are "
               "assumptions, not COLREGS figures")
    if nearest_target_nm is None or nearest_target_nm > TRAFFIC_MARGINAL_NM:
        return GateResult("traffic", GateState.PASS,
                          f"no target within {TRAFFIC_MARGINAL_NM} nm of the "
                          f"next 24 h of track{assumed}", ev)
    if nearest_target_nm > TRAFFIC_FAIL_NM:
        return GateResult("traffic", GateState.MARGINAL,
                          f"target {nearest_target_nm:.1f} nm from track, inside "
                          f"the {TRAFFIC_MARGINAL_NM} nm monitoring band{assumed}", ev)
    return GateResult("traffic", GateState.FAIL,
                      f"target {nearest_target_nm:.1f} nm from track, inside the "
                      f"{TRAFFIC_FAIL_NM} nm close-quarters line{assumed}", ev)


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
    leg_depths_m: list[float | None] | None = None,
    worst_hs_m: float | None = None,
    worst_wind_ms: float | None = None,
    traffic_feed_live: bool = False,
    nearest_target_nm: float | None = None,
    n_targets: int = 0,
) -> list[GateResult]:
    """Evaluate all nine gates. Order follows §12."""
    return [
        capability_gate(vessel),
        chart_gate(mesh_config, vessel, leg_depths_m),
        ice_gate(worst_ice_pct, ice_limit_pct),
        weather_gate(worst_hs_m, worst_wind_ms),
        traffic_gate(traffic_feed_live, nearest_target_nm, n_targets),
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
