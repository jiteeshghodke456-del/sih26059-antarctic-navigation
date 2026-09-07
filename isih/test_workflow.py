"""Tests for the §4 passage workflow.

The ordering *is* the requirement. A UI that shows all ten panels but lets a
captain approve a route before a mission exists has not implemented §4, so
most of these assert that a step is refused rather than that it works.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ISIH = Path(__file__).resolve().parent
if str(ISIH) not in sys.path:
    sys.path.insert(0, str(ISIH))

from workflow import (  # noqa: E402
    ORDER,
    Mission,
    RoutePlan,
    Stage,
    Workflow,
    WorkflowError,
)


def walked_to_review() -> Workflow:
    w = Workflow()
    w.sign_in("Master A. Sharma")
    w.new_voyage()
    w.start_voyage("43rd ISEA resupply", "Bharati", "2019-12-01")
    w.define_mission(Mission(destination_policy="STATION_REQUIRED", cargo_tonnes=900))
    w.set_route(RoutePlan(source="solved", engine="PolarRoute 1.1.11", n_waypoints=41,
                          total_days=8.58))
    w.confirm_waypoints()
    return w


# ---------------- the guards ----------------

def test_a_fresh_workflow_starts_at_sign_in():
    assert Workflow().stage is Stage.SIGN_IN


def test_cannot_start_a_voyage_before_signing_in():
    with pytest.raises(WorkflowError):
        Workflow().start_voyage("x", "Bharati", "2019-12-01")


def test_a_watchkeeper_needs_a_name():
    with pytest.raises(WorkflowError):
        Workflow().sign_in("   ")


def test_cannot_define_a_mission_before_a_voyage():
    w = Workflow()
    w.sign_in("OOW")
    w.new_voyage()
    with pytest.raises(WorkflowError):
        w.define_mission(Mission())


def test_signing_in_twice_is_refused():
    """Unguarded, this jumped to the command centre from any stage and lost
    the plan. Handing over the watch is the explicit path."""
    w = walked_to_review()
    with pytest.raises(WorkflowError):
        w.sign_in("Someone Else")


def test_handing_over_the_watch_keeps_the_voyage():
    w = walked_to_review()
    w.hand_over("Chief Officer R. Nair")
    assert w.watchkeeper == "Chief Officer R. Nair"
    assert w.voyage is not None and w.stage is Stage.REVIEW
    assert any("handed over" in h.detail for h in w.history)


def test_cannot_set_a_route_before_a_mission():
    """Without a mission there is no definition of an acceptable route."""
    w = Workflow()
    w.sign_in("OOW")
    w.new_voyage()
    w.start_voyage("v", "Bharati", "2019-12-01")
    with pytest.raises(WorkflowError):
        w.set_route(RoutePlan())


def test_cannot_approve_before_the_route_is_reviewed():
    w = Workflow()
    w.sign_in("OOW")
    w.new_voyage()
    w.start_voyage("v", "Bharati", "2019-12-01")
    w.define_mission(Mission())
    with pytest.raises(WorkflowError):
        w.approve("DEGRADED")


def test_cannot_approve_with_unconfirmed_waypoints():
    w = walked_to_review()
    w.waypoints_confirmed = False
    with pytest.raises(WorkflowError):
        w.approve("DEGRADED")


def test_cannot_open_the_workspace_before_sailing():
    w = walked_to_review()
    with pytest.raises(WorkflowError):
        w.open_workspace("ice moved")


def test_an_unknown_destination_policy_is_rejected():
    with pytest.raises(WorkflowError):
        Mission(destination_policy="probably fine")


def test_an_unknown_route_source_is_rejected():
    with pytest.raises(WorkflowError):
        RoutePlan(source="vibes")


# ---------------- the happy path ----------------

def test_the_full_forward_path():
    w = walked_to_review()
    assert w.stage is Stage.REVIEW
    w.approve("DEGRADED")
    assert w.stage is Stage.APPROVED
    w.begin_navigation()
    assert w.stage is Stage.ACTIVE


def test_the_step_counter_has_no_gap():
    """VOYAGE used to be in ORDER while nothing ever set it, so the counter
    jumped from 2 to 4 and the progress bar lied."""
    w = Workflow()
    seen = [w.as_dict()["step_number"]]
    w.sign_in("OOW");                                   seen.append(w.as_dict()["step_number"])
    w.new_voyage();                                     seen.append(w.as_dict()["step_number"])
    w.start_voyage("v", "Bharati", "2019-12-01");       seen.append(w.as_dict()["step_number"])
    w.define_mission(Mission());                        seen.append(w.as_dict()["step_number"])
    w.set_route(RoutePlan(source="solved"));            seen.append(w.as_dict()["step_number"])
    w.confirm_waypoints();                              seen.append(w.as_dict()["step_number"])
    w.approve("DEGRADED");                              seen.append(w.as_dict()["step_number"])
    w.begin_navigation();                               seen.append(w.as_dict()["step_number"])
    assert seen == list(range(1, 10)), seen


def test_the_workspace_anchors_to_active_not_to_nothing():
    """WORKSPACE is absent from ORDER, so `idx` fell through to None and
    every stage reported done:true while the workspace was open."""
    w = walked_to_review()
    w.approve("DEGRADED")
    w.begin_navigation()
    w.open_workspace("station cell closed")
    v = w.as_dict()
    assert v["in_workspace"] is True
    assert v["step_number"] == ORDER.index(Stage.ACTIVE) + 1
    done = [o["stage"] for o in v["order"] if o["done"]]
    assert "active" not in done, "ACTIVE is current, not done"
    assert len(done) == len(ORDER) - 1


def test_every_stage_has_a_title_and_a_question():
    from workflow import STAGE_ASKS, STAGE_TITLE
    for s in Stage:
        assert STAGE_TITLE[s] and STAGE_ASKS[s]


def test_the_view_reports_progress_through_the_ordered_path():
    w = walked_to_review()
    v = w.as_dict()
    assert v["stage"] == "review"
    assert v["step_count"] == len(ORDER)
    assert v["step_number"] == ORDER.index(Stage.REVIEW) + 1
    done = [o["stage"] for o in v["order"] if o["done"]]
    assert "sign_in" in done and "mission" in done
    assert "approved" not in done


# ---------------- mission definition is load-bearing ----------------

def test_mission_policy_changes_what_success_means():
    """The field that decides whether the logistics gate can pass.

    Bharati's own cell was closed 23 of 31 days while the approach was open on
    all 31, so these two policies genuinely disagree on most days of the
    window. This is a mission decision with a measurable consequence.
    """
    strict = Mission(destination_policy="STATION_REQUIRED")
    relaxed = Mission(destination_policy="APPROACH_OK")
    assert strict.accepts_approach is False
    assert relaxed.accepts_approach is True
    assert strict.as_dict()["meaning"] != relaxed.as_dict()["meaning"]


# ---------------- the monitoring loop ----------------

def test_the_workspace_offers_exactly_the_three_choices_of_section_4():
    for action, expected in (
        ("keep", Stage.ACTIVE),
        ("alternative", Stage.WAYPOINTS),
        ("edit", Stage.WAYPOINTS),
    ):
        w = walked_to_review()
        w.approve("DEGRADED")
        w.begin_navigation()
        w.open_workspace("station cell closed")
        if action == "keep":
            w.keep_plan("the approach remains open and the mission accepts it")
        elif action == "alternative":
            w.take_alternative("B", "conservative corridor")
        else:
            w.edit_plan("tighten the ice limit")
        assert w.stage is expected


def test_keeping_the_plan_is_recorded_as_a_decision():
    """Deciding that nothing needs to change is a decision, and the system
    that forgets to log it loses the reason later."""
    w = walked_to_review()
    w.approve("DEGRADED")
    w.begin_navigation()
    w.open_workspace("ice moved")
    w.keep_plan("approach still open")
    kept = [h for h in w.history if "kept the existing plan" in h.detail]
    assert kept and kept[0].by == "Master A. Sharma"


def test_editing_forces_the_waypoints_to_be_confirmed_again():
    w = walked_to_review()
    w.approve("DEGRADED")
    w.begin_navigation()
    w.open_workspace("ice moved")
    w.edit_plan("change departure day")
    assert w.waypoints_confirmed is False
    with pytest.raises(WorkflowError):
        w.approve("DEGRADED")


@pytest.mark.parametrize("choice", ["edit", "alternative"])
def test_the_loop_actually_closes(choice):
    """The defect this test exists for: edit and take-alternative both used to
    land at REVIEW with confirmation cleared, but confirm_waypoints requires
    WAYPOINTS and approve refuses unconfirmed waypoints — so the captain
    reached a dead end and §4's cycle could never come round."""
    w = walked_to_review()
    w.approve("DEGRADED")
    w.begin_navigation()
    w.open_workspace("station cell closed")

    if choice == "edit":
        w.edit_plan("depart two days later")
    else:
        w.take_alternative("B", "conservative corridor")

    assert w.stage is Stage.WAYPOINTS
    w.confirm_waypoints()
    assert w.stage is Stage.REVIEW
    w.approve("DEGRADED")
    w.begin_navigation()
    assert w.stage is Stage.ACTIVE


def test_a_corridor_cannot_be_approved_without_showing_its_waypoints():
    """Taking corridor B used to reach REVIEW with the OLD confirmation still
    true, so its 51 legs could be approved having never been displayed."""
    w = walked_to_review()
    w.approve("DEGRADED")
    w.begin_navigation()
    w.open_workspace("ice moved")
    w.take_alternative("B", "conservative corridor")
    assert w.waypoints_confirmed is False


def test_history_attributes_every_step_to_the_watchkeeper():
    w = walked_to_review()
    w.approve("DEGRADED")
    # sign_in itself is recorded before a watchkeeper existed on the previous
    # line, so check everything from the voyage onward.
    for step in w.history[1:]:
        assert step.by == "Master A. Sharma", step
