"""Real-browser test of the bridge console.

Skipped unless playwright is installed AND a server is already running, because
this needs a browser and a live port and must never be the reason `pytest isih`
fails on a fresh clone. Run it deliberately:

    python -m uvicorn isih.demo.app:app --port 8000 &
    python -m pytest isih/demo/test_bridge_ui.py -q

What it asserts is what the unit tests structurally cannot: that the page loads,
that a person can walk the whole section 4 workflow, that the console never
reaches outside itself, and that nothing throws in a browser. Two defects in
this console - a coastline that was never fetched and an ice texture that
painted ice into open water - were invisible to every unit test and obvious the
moment a page was rendered.
"""

from __future__ import annotations

import os
import urllib.error
import urllib.request

import pytest

BASE = os.environ.get("ISIH_BASE", "http://127.0.0.1:8000")
CHROME = os.environ.get(
    "ISIH_CHROME",
    os.path.expanduser("~/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome"),
)


def _server_up() -> bool:
    try:
        with urllib.request.urlopen(BASE + "/api/v2/meta", timeout=2) as r:
            return r.status == 200
    except (urllib.error.URLError, OSError):
        return False


playwright = pytest.importorskip("playwright.sync_api",
                                 reason="playwright not installed")
pytestmark = pytest.mark.skipif(not _server_up(),
                                reason=f"no server at {BASE}")


@pytest.fixture(scope="module")
def page():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        kw = {"executable_path": CHROME} if os.path.exists(CHROME) else {}
        browser = p.chromium.launch(**kw)
        pg = browser.new_page(viewport={"width": 1600, "height": 950})
        pg._isih_errors = []
        pg._isih_requests = []
        pg.on("pageerror", lambda e: pg._isih_errors.append(str(e)))
        pg.on("request", lambda r: pg._isih_requests.append(r.url))
        yield pg
        browser.close()


def _walk_workflow(pg):
    pg.goto(BASE + "/", wait_until="networkidle")
    pg.fill("#signin-name", "Master under test")
    pg.click("#signin-form button[data-primary]")
    pg.wait_for_timeout(2500)
    for _ in range(3):                       # command centre, voyage, mission
        pg.click("#stage footer button[data-primary]")
        pg.wait_for_timeout(900)
    pg.click("#stage footer button[data-primary]")   # solve
    pg.wait_for_timeout(4500)


def test_console_loads_and_gates_on_sign_in(page):
    page.goto(BASE + "/", wait_until="networkidle")
    assert page.title() == "ISIH — bridge console"
    assert page.is_visible("#signin"), "the console must open on sign-in"
    assert page.locator(".toolrail .tool").count() >= 10


def test_the_page_declares_that_its_environment_is_synthetic(page):
    page.goto(BASE + "/", wait_until="networkidle")
    assert "SYNTHETIC ENVIRONMENT" in page.content()


def test_full_workflow_reaches_navigation(page):
    _walk_workflow(page)
    # route -> waypoints
    btns = page.locator("#stage footer button")
    for i in range(btns.count()):
        if btns.nth(i).inner_text().strip() == "Waypoints":
            btns.nth(i).click()
            break
    page.wait_for_timeout(2500)
    assert page.locator("#stage table.tbl tr").count() > 3, "waypoints must be laid"

    page.click("#stage footer button[data-primary]")     # -> review
    page.wait_for_timeout(900)
    gates = page.locator("#stage ul.gates li")
    assert gates.count() == 9, "all nine decision gates must be shown"
    unknown = page.locator('#stage ul.gates li[data-s="UNKNOWN"]').count()
    assert unknown >= 3, "a console that claims to know everything is the bug"

    page.fill("#stage .field input[type=text]", "Master under test")
    page.click("#stage footer button[data-primary]")     # approve
    page.wait_for_timeout(2500)
    page.click("#stage footer button[data-primary]")     # begin navigation
    page.wait_for_timeout(3000)

    assert not page.is_visible("#stage-scrim")
    assert "MONITORING" in page.text_content("#wf-mode")
    assert page.locator("#rail .panel").count() >= 8
    assert page.locator("#statusbar .stat").count() >= 8
    assert page.text_content(".health .state") in (
        "VALID", "DEGRADED", "CRITICAL", "INVALID")


def test_every_visible_panel_declares_provenance(page):
    assert page.locator(".pv").count() > 0, "simulated panels must carry a dot"


def test_time_advances_and_the_world_moves(page):
    before = page.text_content("#statusbar")
    page.eval_on_selector("#t-slider",
                          "e => { e.value = '120'; e.dispatchEvent(new Event('change')); }")
    page.wait_for_timeout(4000)
    assert page.text_content("#statusbar") != before, "the world must change with time"


def test_console_never_reaches_outside_itself(page):
    external = [u for u in page._isih_requests
                if not u.startswith(BASE) and not u.startswith("data:")]
    assert external == [], f"offline claim broken by {external}"


def test_no_javascript_errors_anywhere_in_the_run(page):
    assert page._isih_errors == [], page._isih_errors


def test_health_changes_across_the_voyage(page):
    """Health must be a state, not a fixed light.

    It sat on DEGRADED from Cape Town to Bharati because two gates were
    hardcoded UNKNOWN. The rule - a gate with no data never passes - was right;
    a permanent amber was not evidence of it, it was a stuck light that taught
    the operator nothing. The gates now have inputs, so the voyage reads VALID
    in open water and degrades as the ship works into the ice and out of
    geostationary cover.
    """
    seen = []
    for h in (0, 60, 132, 168):
        page.eval_on_selector(
            "#t-slider", f"e => {{ e.value = '{h}'; e.dispatchEvent(new Event('change')); }}")
        page.wait_for_timeout(2600)
        seen.append(page.text_content(".health .state").strip())
    assert len(set(seen)) >= 2, f"health never changed across the voyage: {seen}"
    assert "VALID" in seen, f"health never reaches VALID: {seen}"


def test_zooming_out_and_panning_cannot_lose_the_chart(page):
    """The bug that would have ended a demo.

    Thirty ordinary wheel-out ticks collapsed the whole domain into a speck on a
    blank canvas, because the zoom floor was a hardcoded scale of 20 with no
    relationship to the data extent. One ordinary drag at that zoom then moved
    the centre from 56 S to 88 N - pole to pole - because the pan converts
    pixels to degrees by dividing by the scale, and nothing bounded the result.
    The cursor then read 391 E, which is not a place. There was no reset, and
    the only recovery was a reload, which discards the entire voyage.
    """
    page.goto(BASE + "/", wait_until="networkidle")
    page.fill("#signin-name", "Zoom test")
    page.click("#signin-form button[data-primary]")
    page.wait_for_timeout(2000)
    page.evaluate("document.getElementById('stage-scrim').hidden = true")

    box = page.locator("#chartwrap").bounding_box()
    cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    page.mouse.move(cx, cy)
    for _ in range(30):
        page.mouse.wheel(0, 260)
    page.wait_for_timeout(500)

    page.mouse.move(cx, cy)
    page.mouse.down()
    page.mouse.move(cx + 300, cy + 150, steps=10)
    page.mouse.up()
    page.wait_for_timeout(500)

    rng = page.text_content("#hud-range")
    assert "N " not in rng and "'N" not in rng, f"centre left the southern hemisphere: {rng}"
    page.mouse.move(cx + 40, cy + 40)
    page.wait_for_timeout(250)
    cursor = page.text_content("#hud-cursor")
    lon_deg = int(cursor.split("°")[1].strip().split()[-1][:3]) if "°" in cursor else 0
    assert lon_deg <= 180, f"impossible longitude on screen: {cursor}"

    # and HOME must actually bring it back
    page.click("#t-home")
    page.wait_for_timeout(700)
    assert "S" in page.text_content("#hud-range")
