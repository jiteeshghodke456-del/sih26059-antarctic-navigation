"""Property tests for the world model.

These do not check that the numbers are pretty. They check the things that
would make a domain expert stop listening: wrong hemisphere, wrong magnitudes,
waves inside pack ice, an ice edge that does not respond to wind, and any
non-determinism, which would break both the demo and every other test.
"""

import numpy as np
import pytest

from isih.sim.fields import Atmosphere, Ocean, coriolis
from isih.sim.ice import IceField
from isih.sim.bergs import BergField, USNIC_MIN_AXIS_M, MAX_PROJECTION_H
from isih.sim.geo_mask import on_land
from isih.sim.world import World, BOX


@pytest.fixture(scope="module")
def w():
    return World(seed=20261207)


# --- determinism ----------------------------------------------------------

def test_two_worlds_agree_exactly():
    a = World(seed=5).sample(-58.0, 44.0, 3.25)
    b = World(seed=5).sample(-58.0, 44.0, 3.25)
    for k in a:
        assert float(np.asarray(a[k])) == float(np.asarray(b[k])), k


def test_different_seeds_differ():
    a = World(seed=5).sample(-58.0, 44.0, 3.25)
    b = World(seed=6).sample(-58.0, 44.0, 3.25)
    assert float(a["sic"]) != float(b["sic"]) or float(a["mslp"]) != float(b["mslp"])


def test_time_is_directly_evaluable_not_stepped(w):
    """Asking for t=9 must not require having asked for t=8. This is what lets
    the API serve any time and what keeps the tests independent."""
    direct = float(w.sample(-62.0, 50.0, 9.0)["sic"])
    _ = w.sample(-62.0, 50.0, 0.0)
    again = float(w.sample(-62.0, 50.0, 9.0)["sic"])
    assert direct == again


# --- hemisphere and signs -------------------------------------------------

def test_coriolis_is_negative_in_the_south():
    assert coriolis(-55.0) < 0
    assert coriolis(10.0) > 0


def test_flow_is_clockwise_around_a_southern_low():
    """The first thing a mariner checks. Sample a ring around the pressure
    minimum and confirm the circulation sense is clockwise, i.e. the tangential
    component is consistently negative in the right-handed sense."""
    atm = Atmosphere(3)
    lons = np.linspace(20, 70, 90)
    lats = np.linspace(-68, -45, 60)
    LO, LA = np.meshgrid(lons, lats)
    p = atm.pressure(LO, LA, 0.0)
    j, i = np.unravel_index(np.argmin(p), p.shape)
    clat, clon = LA[j, i], LO[j, i]

    ang = np.linspace(0, 2 * np.pi, 24, endpoint=False)
    r = 2.0
    rl = clat + r * np.sin(ang)
    rn = clon + r * np.cos(ang) / max(np.cos(np.radians(clat)), 0.2)
    u, v = atm.wind(rn, rl, 0.0)
    # Unit vector pointing anticlockwise at each ring point.
    tx, ty = -np.sin(ang), np.cos(ang)
    circulation = np.mean(u * tx + v * ty)
    assert circulation < 0, "Southern Hemisphere flow must be clockwise around a low"


# --- magnitudes -----------------------------------------------------------

def test_the_fifties_are_the_windiest_band():
    """The Furious Fifties are furious. If the model does not reproduce the
    latitude of the strongest winds it is not a Southern Ocean."""
    atm = Atmosphere(11)
    means = {}
    for name, (lo, hi) in {"forties": (-50, -40), "fifties": (-60, -50),
                           "subtropics": (-38, -28)}.items():
        lat = np.linspace(lo, hi, 8)
        acc = []
        for t in range(0, 40, 4):
            for L in np.linspace(12, 84, 8):
                u, v = atm.wind(np.full_like(lat, L), lat, float(t))
                acc.append(np.hypot(u, v))
        means[name] = float(np.mean(acc))
    assert means["fifties"] > means["forties"] > means["subtropics"]


def test_wind_and_pressure_are_in_operational_range(w):
    _, _, s = w.grid(4.0, nx=60, ny=50)
    assert 940.0 < float(s["mslp"].min()) and float(s["mslp"].max()) < 1045.0
    assert float(np.percentile(s["wind_kn"], 50)) < 45.0
    assert float(s["wind_kn"].max()) < 80.0


def test_waves_never_exceed_the_observed_record(w):
    _, _, s = w.grid(4.0, nx=60, ny=50)
    assert float(s["hs"].max()) <= 19.0


def test_waves_are_damped_inside_the_pack(w):
    """Swell does not propagate far into pack ice. A wave field that ignores
    the ice is the most obvious error possible on an ice chart."""
    _, _, s = w.grid(4.0, nx=80, ny=70)
    heavy = s["sic"] > 0.75
    if heavy.sum() > 20:
        assert float(np.nanmax(s["hs"][heavy])) < 1.5


def test_sst_is_at_freezing_under_ice(w):
    _, _, s = w.grid(4.0, nx=60, ny=50)
    icy = s["sic"] > 0.6
    if icy.sum() > 10:
        assert float(np.nanmax(s["sst"][icy])) < 0.5
    assert float(s["sst"].min()) >= -1.95


# --- ice ------------------------------------------------------------------

def test_concentration_is_bounded_and_ice_is_in_the_south(w):
    _, lats, s = w.grid(4.0, nx=70, ny=60)
    assert 0.0 <= float(s["sic"].min()) and float(s["sic"].max()) <= 1.0
    north = s["sic"][lats > -50.0, :]
    assert float(north.max()) < 0.02, "no sea ice north of 50S in summer"


def test_ice_edge_tracks_recent_wind_and_has_memory():
    """The edge must move because the wind moved it - and it must lag.

    Two earlier versions of this test were wrong, and both are worth recording
    because they are the two commonest ways to mis-test a stochastic model.

    The first correlated edge position against the INSTANTANEOUS meridional
    wind and failed at r = -0.09. That looked like a broken model; it was a
    broken test. Ice has inertia, so the edge reflects the wind of the last day
    or two, not the gust at this instant.

    The second correlated against the two-day mean but on a single seed, and
    failed at r = 0.27 when the seeding changed. One realisation is one sample:
    across eight seeds this model gives r from 0.27 to 0.82, median 0.77, and
    positive every time. Testing one draw tests the draw, not the mechanism.

    So this asserts the mechanism: positive on every seed, and a strong median.
    It also asserts the absence of an instantaneous response, which is what
    proves the edge has memory rather than being a function of the wind field
    evaluated at t.
    """
    seeds = (3, 7, 11, 21, 42, 101, 777, 2026)
    lon = np.linspace(15, 85, 40)
    ts = np.arange(0.0, 25.0, 1.0)
    r_lagged, r_inst = [], []

    for sd in seeds:
        atm = Atmosphere(sd)
        ice = IceField(sd, atm)
        edges = np.array([ice.edge_lat(lon, t) for t in ts])
        # Remove the seasonal retreat (a function of t alone) and the fixed
        # bathymetric undulation (a function of lon alone); what is left is wind.
        resid = (edges - edges.mean(axis=0, keepdims=True)
                 - edges.mean(axis=1, keepdims=True) + edges.mean())

        lagged = []
        for t in ts:
            acc = np.zeros_like(lon)
            for lag in (0.0, 0.5, 1.0, 1.5, 2.0):
                _, v = atm.wind(lon, ice.edge_lat(lon, max(0.0, t - lag)),
                                max(0.0, t - lag))
                acc = acc + v
            lagged.append(acc / 5.0)
        lagged = np.array(lagged)
        inst = np.array([atm.wind(lon, ice.edge_lat(lon, t), t)[1] for t in ts])

        r_lagged.append(np.corrcoef(resid.ravel(), lagged.ravel())[0, 1])
        r_inst.append(np.corrcoef(resid.ravel(), inst.ravel())[0, 1])

    r_lagged = np.array(r_lagged)
    r_inst = np.array(r_inst)
    assert (r_lagged > 0).all(), f"edge is not wind-driven on every seed: {r_lagged}"
    assert np.median(r_lagged) > 0.5, f"weak wind response (median r={np.median(r_lagged):.2f})"
    assert np.median(np.abs(r_inst)) < np.median(r_lagged) / 2.0, (
        "edge responds as strongly to instantaneous wind as to recent wind, "
        "so it has no memory")


def test_the_edge_retreats_across_the_summer():
    atm = Atmosphere(9)
    ice = IceField(9, atm)
    lon = np.linspace(12, 86, 60)
    early = float(np.mean(ice.edge_lat(lon, 2.0)))
    late = float(np.mean(ice.edge_lat(lon, 60.0)))
    assert late < early, "ice edge should retreat south through the summer"


# --- icebergs -------------------------------------------------------------

def test_most_bergs_are_below_the_catalogue_threshold(w):
    """USNIC tracks from about 18.5 km. If the model produced only giants it
    would quietly imply the catalogue sees everything, which is the exact
    falsehood the iceberg rule exists to prevent."""
    bergs = w.bergs.at(3.0)
    tracked = [b for b in bergs if b["tracked"]]
    assert 0 < len(tracked) < len(bergs)
    for b in bergs:
        assert b["tracked"] == (b["length_m"] >= USNIC_MIN_AXIS_M)


def test_large_bergs_are_current_driven(w):
    """WDE17's own conclusion. If our biggest berg came out wind-driven, either
    the forcing or the coupling would be wrong."""
    bergs = sorted(w.bergs.at(3.0), key=lambda b: -b["area_km2"])
    assert bergs[0]["wind_share"] < 0.15
    assert bergs[0]["regime"] == "current-driven"


def test_berg_drift_speed_is_physical(w):
    for b in w.bergs.at(5.0):
        assert 0.0 <= b["drift_kn"] < 3.0


def test_projection_stops_at_72_hours_and_widens(w):
    f = w.bergs.forecast(0, 4.0)
    assert max(x["hours"] for x in f) <= MAX_PROJECTION_H
    radii = [x["radius_km"] for x in f]
    assert radii == sorted(radii) and radii[0] > 0


# --- domain ---------------------------------------------------------------

def test_grid_covers_the_corridor(w):
    lons, lats, _ = w.grid(1.0, nx=40, ny=30)
    assert lons[0] == BOX["lon_min"] and lons[-1] == BOX["lon_max"]
    assert lats[0] == BOX["lat_min"] and lats[-1] == BOX["lat_max"]


def test_grid_is_fast_enough_to_serve(w):
    import time
    t0 = time.time()
    w.grid(7.0)
    assert time.time() - t0 < 0.5


# --- land: the tests that should have existed ------------------------------

def test_no_iceberg_is_ever_on_land():
    """Seven of twenty-six bergs were sitting on Antarctica, and the fix before
    this one clamped them into the domain's bounding BOX - which is a different
    question and moved some of them further ashore. Nothing caught it because
    nothing asked. This asks, across seeds and across the whole horizon."""
    for seed in (20261207, 7, 99):
        w = World(seed)
        for t in (0.0, 1.0, 5.0, 12.0, 20.0, 30.0):
            ashore = [b["id"] for b in w.bergs.at(t)
                      if bool(on_land(b["lon"], b["lat"])[0])]
            assert not ashore, f"seed {seed} t={t}: {ashore} on land"


def test_grounded_bergs_stop_and_stay_stopped():
    """A grounded berg is a real thing - it is why a bay stays blocked - but it
    must not creep, and it must not un-ground."""
    w = World(20261207)
    early = {b["id"]: b for b in w.bergs.at(6.0) if b["grounded"]}
    late = {b["id"]: b for b in w.bergs.at(24.0)}
    assert early, "expect some bergs aground near the coast"
    for bid, b in early.items():
        assert late[bid]["grounded"], f"{bid} un-grounded"
        assert abs(late[bid]["lat"] - b["lat"]) < 1e-6
        assert abs(late[bid]["lon"] - b["lon"]) < 1e-6


def test_the_route_never_crosses_land():
    """The lattice had no land mask: 302 of its 5,250 nodes are ashore and the
    published Bharati track had a leg on the continent. Ice made the interior
    expensive, which hid it - expensive is not impossible."""
    from isih.sim.router import Router, VesselModel
    from isih.sim.world import BHARATI, CAPE_TOWN
    w = World(20261207)
    r = Router(w, VesselModel())
    assert r.land.sum() > 0, "a land mask that masks nothing is not a mask"
    for depart in (0.0, 6.0):
        res = r.solve(CAPE_TOWN, BHARATI, depart, "time")
        if res is None:
            continue
        ashore = [(l["lat"], l["lon"]) for l in res["legs"]
                  if bool(on_land(l["lon"], l["lat"])[0])]
        assert not ashore, f"depart {depart}: legs on land {ashore[:3]}"


def test_land_mask_knows_the_continents():
    assert bool(on_land(20.0, -71.5)[0]), "Antarctica"
    assert bool(on_land(25.0, -30.0)[0]), "southern Africa"
    assert not bool(on_land(45.0, -50.0)[0]), "open Southern Ocean"
    assert not bool(on_land(60.0, -60.0)[0]), "open ocean"


def test_berg_drift_is_the_berg_not_the_current():
    """`drift_kn` used to be hypot(current), because `at()` never called the
    velocity closure at all. For a wind-sensitive berg that under-reports the
    berg's own motion, and there was no direction of any kind to draw."""
    w = World(20261207)
    bergs = w.bergs.at(6.0)
    moving = [b for b in bergs if not b["grounded"]]
    assert moving, "expect bergs under way"
    for b in moving:
        assert b["drift_dir_deg"] is not None
        assert 0.0 <= b["drift_dir_deg"] < 360.0
        assert 0.0 <= b["drift_kn"] < 3.0
        assert b["d24"] is not None and b["d24"]["nm"] >= 0.0


def test_grounded_bergs_carry_no_drift_vector():
    """A drift arrow on a grounded berg would be a lie about the one thing the
    arrow claims."""
    w = World(20261207)
    aground = [b for b in w.bergs.at(24.0) if b["grounded"]]
    assert aground, "expect some bergs aground by day 24"
    for b in aground:
        assert b["d24"] is None
        assert b["drift_dir_deg"] is None
        assert b["drift_kn"] == 0.0
        assert b["grounded_since_day"] is not None


# --- POLARIS: a band, never a number ---------------------------------------

def test_polaris_reproduces_the_published_worked_example():
    """The research file computes one regime by hand from Table 1.3: 9/10
    medium first-year plus 1/10 thick first-year. If this module does not
    reproduce those four numbers exactly, the table was typed wrong."""
    from isih import polaris
    partials = {"Med FY": 9, "Thick FY": 1}
    assert polaris.rio_exact(partials, "PC4") == 19
    assert polaris.rio_exact(partials, "PC5") == 9
    assert polaris.rio_exact(partials, "PC6") == -1
    assert polaris.rio_exact(partials, "PC7") == -11
    assert polaris.tier(19, "PC4") == polaris.NORMAL
    assert polaris.tier(-1, "PC6") == polaris.ELEVATED
    assert polaris.tier(-11, "PC7") == polaris.SPECIAL


def test_table_1_1_columns_differ_and_bounds_are_half_open():
    """Polar Classes have a middle band; Finnish-Swedish equivalents do not, so
    for them every negative RIO is already special consideration. Collapsing the
    two columns is the commonest way to misread this table."""
    from isih import polaris
    assert polaris.tier(0, "PC6") == polaris.NORMAL
    assert polaris.tier(-10, "PC6") == polaris.ELEVATED
    assert polaris.tier(-11, "PC6") == polaris.SPECIAL
    assert polaris.tier(-1, "IA") == polaris.SPECIAL       # no elevated band
    assert polaris.tier(0, "IA") == polaris.NORMAL


def test_polaris_is_reported_as_a_band_that_can_flip():
    """The finding is not a value, it is whether the candidate rows agree. The
    open crossing must be stable; heavy ice must flip."""
    from isih import polaris
    assert polaris.band(0.06, "Med FY")["state"] == "stable-normal"
    heavy = polaris.band(0.90, "Med FY")
    assert heavy["state"] == "flips"
    assert heavy["rio_hi"] - heavy["rio_lo"] > 20, "the spread IS the finding"


def test_ice_free_column_is_three_for_every_class():
    from isih import polaris
    for cls in polaris.CLASSES:
        assert polaris.RIV[cls]["Ice-free"] == 3
