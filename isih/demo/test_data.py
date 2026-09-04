"""The demo must show the published numbers, unchanged, from the real files.

No fixtures, no synthetic data: every test reads isih/figures/*.json and the
NOAA/NSIDC daily files exactly as the app does. If a number here drifts from
docs/ISIH_RESULTS.md, the demo is lying and this suite goes red.
"""

import numpy as np
import pytest

from isih.demo import data


# --- destination window: the 74 % finding ---------------------------------

def test_window_matches_published_numbers():
    s = data.window()["summary"]
    assert s["Bharati"]["days_observed"] == 31
    assert s["Bharati"]["days_closed"] == 23
    assert s["Bharati"]["pct_days_closed"] == 74.2
    assert s["Bharati approach (100 km N)"]["days_closed"] == 0


def test_thirty_one_dates_all_december_2019():
    d = data.dates()
    assert len(d) == 31
    assert d[0] == "2019-12-01" and d[-1] == "2019-12-31"


def test_spillover_signature_on_day_one():
    # ISIH_RESULTS.md §2: 1 Dec 2019, Bharati reads 0.0 raw and 30.7 quality-checked.
    row = data.day_status("2019-12-01")["Bharati"]
    assert row["sic_qa_off"] == 0.0
    assert row["sic_qa_on"] == 30.7


# --- route: exactly what PolarRoute wrote ---------------------------------

def test_route_geometry_and_traveltime():
    r = data.route()
    assert len(r["coords"]) == 41
    lon0, lat0 = r["coords"][0]
    lon1, lat1 = r["coords"][-1]
    assert abs(lat0 - -33.9) < 0.6 and abs(lon0 - 18.4) < 0.6     # Cape Town
    assert abs(lat1 - -69.4) < 0.6 and abs(lon1 - 76.2) < 0.6     # Bharati
    assert abs(r["total_traveltime_days"] - 8.58) < 0.01


def test_route_ice_numbers_match_the_figure():
    # route_map.png legend: route "max 79% ice", straight line "reaches 92% ice".
    # Same raster, same sampling method — the app must show the slide's numbers.
    r = data.route()
    assert round(r["max_sic_pct_along_route"]) == 79
    assert round(r["straight_max_sic_pct"]) == 92
    assert r["route_samples_over_limit"] == 0          # never above the ship's 80 %
    assert r["straight_samples_over_limit"] > 0        # the straight line is blocked


def test_raster_on_screen_is_the_raster_in_the_figure():
    # sic_points.csv is what route_map.png was drawn from; day 1 QA-on must be
    # the same 4,029 cells, or the map and the figure would disagree.
    n_csv = sum(1 for _ in open(data.FIG / "sic_points.csv")) - 1
    assert data.day_field("2019-12-01", qa=True)["n_known"] == n_csv == 4029


def test_cells_parse():
    c = data.cells()
    assert len(c) == 236
    assert all(len(cell["ring"]) >= 4 for cell in c)
    vals = [cell["sic"] for cell in c if cell["sic"] is not None]
    assert vals and min(vals) >= 0.0 and max(vals) <= 100.0


# --- daily raster: real satellite files, QA on and off --------------------

def test_every_window_day_has_a_file_on_disk():
    # A slider that dies on day 17 in front of a judge is the one failure
    # this demo must never have.
    assert data.preflight() == []


def test_day_field_is_inside_corridor_and_in_range():
    f = data.day_field("2019-12-01", qa=True)
    lat, lon, sic = np.array(f["lat"]), np.array(f["lon"]), np.array(f["sic"])
    assert f["n_known"] > 1000
    assert lat.min() >= data.BOUNDS["lat_min"] and lat.max() <= data.BOUNDS["lat_max"]
    assert lon.min() >= data.BOUNDS["lon_min"] and lon.max() <= data.BOUNDS["lon_max"]
    assert sic.min() >= 0 and sic.max() <= 100


def test_qa_off_shows_suppressed_cells_as_zero():
    on = data.day_field("2019-12-01", qa=True)
    off = data.day_field("2019-12-01", qa=False)
    # QA on withholds the suspect cells; QA off hands them back as values...
    assert on["n_unknown"] > 0
    assert off["n_known"] >= on["n_known"]
    # ...and those values are exact zeros — the land-spillover signature.
    assert off["n_exact_zero"] > on["n_exact_zero"]


@pytest.mark.parametrize("d", ["2019-12-10", "2019-12-31"])
def test_other_days_load(d):
    f = data.day_field(d, qa=True)
    assert f["date"] == d and f["n_known"] > 1000
