"""The twelve mandatory behavioural tests of Stage 05.

The governing instruction is "attack the completed project rather than
trusting its documentation". So these do not test that a function returns a
value; they test that the *system behaves* the way we say it does on stage.

Several of them assert a limitation rather than a capability. Test 5 asserts
that we never report zero icebergs, because we have not looked. Test 2
asserts that our freshness reporting is incomplete and names what is missing.
That is deliberate: a test that pins an honest gap is what stops the gap from
being quietly papered over later, and it fails loudly if someone starts
claiming more than we can support.

Each test names its number and the sentence it is discharging.

Run:  .venv-demo/bin/python -m pytest isih/test_behavioural.py -v
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ISIH = Path(__file__).resolve().parent
if str(ISIH) not in sys.path:
    sys.path.insert(0, str(ISIH))

FIG = ISIH / "figures"
DOCS = ISIH.parent / "docs"

fastapi = pytest.importorskip("fastapi", reason="the demo service is needed")
from fastapi.testclient import TestClient  # noqa: E402

from isih.demo.app import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def _load(name: str) -> dict:
    p = FIG / name
    if not p.exists():
        pytest.skip(f"{name} not generated — run isih/alternatives.py")
    return json.loads(p.read_text())


# ---------------------------------------------------------------- 1

def test_01_same_environment_different_vessel():
    """"Same environment, different vessel -> verify route/risk behaviour
    actually differs where it should."

    Result is PARTIAL and the artifact must say so. Both ships follow an
    identical track on this day's ice; what differs is ETA and fuel. Claiming
    "different ships get different routes" on this evidence would be false,
    so the comparison carries an explicit do-not-claim line.
    """
    v = _load("vessel_comparison.json")
    assert len(v["runs"]) == 2

    # The cost of the plan must genuinely depend on the ship.
    assert abs(v["eta_delta_days"]) > 0.5, v["eta_delta_days"]
    assert abs(v["fuel_delta_pct"]) > 1.0, v["fuel_delta_pct"]

    # And the honest verdict must be recorded, not the flattering one.
    assert v["track_identical"] is True
    assert v["verdict"].startswith("PARTIAL")
    assert "do_not_claim" in v and "different ships get different routes" in v["do_not_claim"]

    # Both ships must carry the SAME assumed ice limit, or the experiment
    # manufactures its own result.
    limits = {r["config"]["max_ice_conc"] for r in v["runs"].values()}
    assert len(limits) == 1, f"the two vessels were given different ice limits: {limits}"


# ---------------------------------------------------------------- 2

def test_02_data_freshness_is_reported_and_its_gaps_are_named(client):
    """"Real data freshness -> verify age/source/received time behaviour."

    PARTIAL, deliberately pinned. Every environmental value states its source
    and its valid date. What we do NOT have is a received time or a computed
    age, because this is replay from an archive rather than a live feed —
    there is no arrival timestamp to report. This test asserts what exists and
    fails if someone starts inventing an age.
    """
    dec = client.get("/api/decision").json()
    env = dec["environmental_state"]
    assert env["ice_source"], "no source recorded for the ice field"
    assert env["ice_date"], "no valid time recorded for the ice field"
    assert env["router"], "no provenance for the route"

    # Replay must not fabricate a live-feed age.
    assert dec["data_mode"] == "HISTORICAL REPLAY"
    for gate in dec["gates"]:
        for ev in gate["evidence"]:
            if ev.get("age_hours") is not None:
                pytest.fail(
                    "an age was reported for archived data; there is no "
                    "arrival time in replay to compute one from"
                )


# ---------------------------------------------------------------- 3

def test_03_source_disagreement_is_surfaced(client):
    """"Sensor/source disagreement -> verify conflict is surfaced."

    We have a real one, and it is not synthetic: the CDR's own QA flag
    disagrees with its own concentration field. At Bharati the raw product
    reads open water where the quality-checked read is suppressed. Both
    readings are served, so the conflict is visible rather than resolved
    silently in our favour.
    """
    day = client.get("/api/summary").json()["dates"][0]
    raw = client.get(f"/api/day/{day}?qa=off").json()
    qa = client.get(f"/api/day/{day}?qa=on").json()

    assert raw["qa"] is False and qa["qa"] is True
    # The QA pass must actually change the picture, or there is no conflict
    # being surfaced and this test is decorative.
    assert qa["n_unknown"] > 0, "QA marked nothing unknown — no disagreement to show"
    assert raw["n_exact_zero"] > qa.get("n_exact_zero", 0), (
        "the raw product should report more exact-zero cells than the "
        "quality-checked one; if not, the suppression is not being surfaced"
    )


# ---------------------------------------------------------------- 4

def test_04_missing_optional_layer_degrades_rather_than_fails(client):
    """"Stale communications -> verify graceful degradation."

    Two properties. The page fetches nothing external, so loss of the outside
    world changes nothing. And an absent optional layer degrades to an
    explicitly-unavailable state instead of taking the service down.
    """
    html = client.get("/").text
    external = [
        ln for ln in html.splitlines()
        if ("http://" in ln or "https://" in ln or "//fonts." in ln) and "xmlns" not in ln
    ]
    assert not external, f"page would need the network: {external[:2]}"

    pa = client.get("/api/protected")
    assert pa.status_code == 200
    assert "available" in pa.json(), "the layer must declare availability either way"

    # A capability we do not have must answer 503 with an instruction, never
    # a plausible empty result that reads as "nothing there".
    missing = client.get("/api/vessel-comparison")
    assert missing.status_code in (200, 503)
    if missing.status_code == 503:
        assert "run isih/alternatives.py" in missing.json()["detail"]


# ---------------------------------------------------------------- 5

def test_05_absence_of_iceberg_data_is_never_reported_as_no_icebergs(client):
    """"Missing iceberg record -> verify system does not infer 'no iceberg'."

    The catalogue exists in the repo but is not wired into the route, and the
    decision must say exactly that rather than reporting a clear sea. This is
    the same class of error as the destination that was once reported closed
    31 of 31 days when it had never been scored at all.
    """
    dec = client.get("/api/decision").json()
    bergs = [h for h in dec["hazards_considered"] if "iceberg" in h["kind"].lower()]
    assert bergs, "icebergs are not mentioned at all, which is worse than saying unknown"

    berg = bergs[0]
    state = berg["state"].lower()
    for forbidden in ("none", "clear", "no icebergs", "zero"):
        assert forbidden not in state, (
            f"the iceberg hazard reports {berg['state']!r}, which asserts an "
            f"absence we have not established"
        )
    assert "not" in state or "unknown" in state


# ---------------------------------------------------------------- 6

def test_06_route_health_changes_because_of_evidence_not_noise(client):
    """"Route degradation -> verify route health changes because of actual
    evidence."

    Both halves matter. Health must move when the observation genuinely
    changes the answer, and must NOT move when it does not. §48A.13 is
    explicit that a route should degrade because an assumption changed, not
    merely because new data arrived.
    """
    dates = client.get("/api/summary").json()["dates"]
    healths = {}
    for d in dates:
        healths[d] = client.get(f"/api/decision?day={d}").json()["health"]

    assert len(set(healths.values())) > 1, (
        f"route health never changes across the whole window: {set(healths.values())}"
    )
    assert "INVALID" in healths.values(), "no day in the window ever invalidates the route"

    # Re-evaluating identical evidence must be stable.
    first = client.get(f"/api/decision?day={dates[0]}").json()
    again = client.get(f"/api/decision?day={dates[0]}").json()
    assert first["gate_digest"] == again["gate_digest"]
    assert again["diverges_from_approval"] is False or again["approved_version"] is not None


def test_06b_divergence_from_an_approved_plan_names_the_gate_that_flipped(client):
    """The operational half of test 6: after approval, the system must tell
    the master which assumption broke, not merely that something did."""
    dates = client.get("/api/summary").json()["dates"]
    healths = {d: client.get(f"/api/decision?day={d}").json()["health"] for d in dates}
    good = next(d for d, h in healths.items() if h != "INVALID")
    bad = next(d for d, h in healths.items() if h == "INVALID")

    client.post("/api/decision/approve", json={"by": "Master (test)", "day": good})
    diverged = client.get(f"/api/decision?day={bad}").json()

    assert diverged["diverges_from_approval"] is True
    assert "logistics" in diverged["divergence"], diverged["divergence"]
    assert "to FAIL" in diverged["divergence"]

    same = client.get(f"/api/decision?day={good}").json()
    assert same["diverges_from_approval"] is False, (
        "re-reading the approved day reports divergence — the system is "
        "confusing 'new data arrived' with 'an assumption changed'"
    )


# ---------------------------------------------------------------- 7

def test_07_alternatives_differ_measurably():
    """"Alternative routes -> verify alternatives differ in measurable
    exposure/ETA/fuel/operational terms."

    An alternative that does not differ measurably is the same plan drawn
    twice. One of ours differs by not existing at all, which is the
    contingency gate's real answer at that ice limit.
    """
    doc = _load("alternatives.json")
    cs = doc["corridors"]
    assert len(cs) >= 3

    solved = [c for c in cs if c.get("solved")]
    assert len(solved) >= 2, "fewer than two corridors solved"

    a, b = solved[0], solved[1]
    assert a["legs"] != b["legs"] or abs(a["traveltime_days"] - b["traveltime_days"]) > 1e-6, (
        "two 'alternatives' are the same route"
    )
    # Exposure must be reported per corridor, not just duration.
    assert a.get("worst_ice_pct") is not None and b.get("worst_ice_pct") is not None

    unsolved = [c for c in cs if not c.get("solved")]
    assert unsolved, "no corridor demonstrates the limit at which no route exists"
    assert "no route exists" in unsolved[0]["why"]


def test_07b_the_objective_collinearity_finding_is_recorded():
    """Solving for fuel returns the same path as solving for time. That is a
    limitation of this configuration and must be stated, not hidden behind
    the phrase 'multi-objective'."""
    doc = _load("alternatives.json")
    ids = {f["id"] for f in doc["findings"]}
    assert "objectives-collinear" in ids
    finding = next(f for f in doc["findings"] if f["id"] == "objectives-collinear")
    assert "identical" in finding["finding"]


# ---------------------------------------------------------------- 8 & 9

def test_08_prediction_is_scored_against_observation():
    """"Prediction -> compare against later observation or appropriate
    historical replay."

    The model is scored on a held-out melt season with ground truth, and the
    upper-bound nature of that protocol is disclosed in the same document as
    the numbers — which is the only place a caveat is any use.
    """
    results = (DOCS / "ISIH_RESULTS.md").read_text()
    assert "Persistence" in results
    assert "upper bound on forecast skill" in results, (
        "the leakage caveat is missing from the document carrying the numbers"
    )


def test_09_baselines_are_defensible_and_carry_their_period():
    """"Baseline -> compare against defensible simpler method."

    Persistence is the baseline. The trap this test guards is real and has
    already bitten once: persistence scored over a different period beats our
    own model, so every persistence figure must state the period it came
    from or the two get quoted side by side on stage.
    """
    results = (DOCS / "ISIH_RESULTS.md").read_text()
    assert "0.0570" in results and "0.1395" in results, "persistence numbers missing"

    viva = (DOCS / "VIVA_PREP.md").read_text()
    if "0.0893" in viva:
        # The qualifier can legitimately wrap onto the following line, so
        # check a small context window rather than the single line the
        # number happens to land on.
        lines = viva.splitlines()
        for i, line in enumerate(lines):
            if "0.0893" not in line:
                continue
            context = " ".join(lines[max(0, i - 1):i + 3]).lower()
            assert any(w in context for w in ("full-year", "all seasons", "period", "melt")), (
                f"a persistence figure is quoted with no period nearby: {line.strip()[:110]}"
            )


# ---------------------------------------------------------------- 10

def test_10_replay_is_labelled_everywhere_it_is_shown(client):
    """"Simulated feature -> verify it is labelled."

    Nothing here is simulated, but replay is just as capable of being
    mistaken for live, and a judge watching ice move across a map will assume
    it is live unless told otherwise.
    """
    dm = client.get("/api/summary").json()["data_mode"]
    assert dm["mode"] == "HISTORICAL REPLAY"
    assert "not a live feed" in dm["means"].lower()

    html = client.get("/").text
    assert 'id="mode-badge"' in html and 'id="mode-text"' in html

    dec = client.get("/api/decision").json()
    assert dec["data_mode"] == "HISTORICAL REPLAY"
    assert "no live GPS" in dec["vessel_state"]["position_source"]


# ---------------------------------------------------------------- 11

def test_11_no_capability_is_claimed_without_data_behind_it(client):
    """"Existing tests -> all pass after changes."

    Discharged by the suite as a whole. What this adds is the invariant most
    worth protecting: a gate with no data must never read as a pass, so the
    system cannot certify a route it cannot see.
    """
    dec = client.get("/api/decision").json()
    unknown = [g for g in dec["gates"] if g["state"] == "UNKNOWN"]
    assert unknown, "every gate suddenly has data — verify that, do not assume it"
    assert dec["health"] != "VALID", (
        "the route reads VALID while gates are unevaluated; either the missing "
        "datasets were wired in (update this test) or a gate is being faked"
    )
    for g in unknown:
        assert "needs" in g["reason"].lower() or "never scored" in g["reason"].lower(), (
            f"gate {g['gate']} is UNKNOWN without saying what would settle it"
        )


# ---------------------------------------------------------------- 12

def test_12_demo_serves_every_endpoint_it_needs_without_manual_repair(client):
    """"Demo -> runs from the expected starting environment without
    undocumented manual repair."

    The app refuses to start at all if a satellite file is missing, so
    reaching this test already proves the preflight passed. What remains is
    that every endpoint the page calls actually answers.
    """
    for path in ("/", "/api/summary", "/api/route", "/api/cells",
                 "/api/protected", "/api/decision", "/api/decisions"):
        r = client.get(path)
        assert r.status_code == 200, f"{path} returned {r.status_code}"

    day = client.get("/api/summary").json()["dates"][0]
    assert client.get(f"/api/day/{day}?qa=on").status_code == 200
    assert client.get(f"/api/day/{day}?qa=off").status_code == 200

    # A date outside the window must 404 rather than silently serve something.
    assert client.get("/api/day/1999-01-01").status_code == 404
