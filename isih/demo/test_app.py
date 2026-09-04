"""The API must serve the same real numbers the loaders produce, and refuse bad input plainly.

Runs the real startup path (preflight + warm-up) through the test client, so a
missing daily file fails here, not in front of an examiner.
"""

import pytest
from fastapi.testclient import TestClient

from isih.demo.app import app


@pytest.fixture(scope="module")
def client():
    # `with` runs the lifespan: preflight over all 31 files, then warm-up.
    with TestClient(app) as c:
        yield c


def test_index_is_the_page(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Bharati" in r.text and "/static/app.js" in r.text


def test_static_assets_served(client):
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/style.css").status_code == 200


def test_summary_carries_the_published_window(client):
    s = client.get("/api/summary").json()
    assert s["vessel"] == "MV Vasiliy Golovnin"
    assert s["ice_limit_pct"] == 80
    assert len(s["dates"]) == 31
    assert s["summary"]["Bharati"]["days_closed"] == 23
    assert s["summary"]["Bharati approach (100 km N)"]["days_closed"] == 0
    assert s["results"]["do_not_claim"]          # the caveats ship with the numbers


def test_route_endpoint(client):
    r = client.get("/api/route").json()
    assert len(r["coords"]) == 41
    assert abs(r["total_traveltime_days"] - 8.58) < 0.01
    assert r["max_sic_pct_along_route"] < 80


def test_cells_endpoint(client):
    c = client.get("/api/cells").json()
    assert len(c["cells"]) == 236


def test_day_on_and_off_differ_in_the_documented_way(client):
    on = client.get("/api/day/2019-12-01?qa=on").json()
    off = client.get("/api/day/2019-12-01?qa=off").json()
    assert on["qa"] is True and off["qa"] is False
    assert on["n_unknown"] > 0 and off["n_unknown"] == 0
    assert off["n_exact_zero"] > on["n_exact_zero"]
    assert len(on["lat"]) == len(on["lon"]) == len(on["sic"]) == on["n_known"]


def test_day_outside_window_is_a_clean_404(client):
    r = client.get("/api/day/2019-11-30")
    assert r.status_code == 404
    assert "outside the demo window" in r.json()["detail"]


def test_bad_qa_value_is_a_clean_400(client):
    assert client.get("/api/day/2019-12-01?qa=maybe").status_code == 400
