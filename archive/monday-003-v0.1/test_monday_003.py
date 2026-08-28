"""Guards for monday-003 "Blockers".

The scenario's whole design rests on one rule: every fact is stated somewhere
in the six candidate sources, and no conclusion is. A source that says "Marcus
is the bottleneck" or "this is the critical path" would turn a reasoning test
into a reading test, and nothing else in the harness would notice. That is what
`test_no_candidate_source_states_a_conclusion` is for.

The rest checks the things a hand-built scenario gets wrong quietly: a rubric
that no longer totals 100, a canonical schedule that violates its own
durations, a dependency graph naming work items that do not exist, and the
newest-state facts the whole answer key depends on.
"""

from __future__ import annotations

import csv
import io
import re
from pathlib import Path

import pytest
import yaml

from mondaybench.config import load_evaluator
from mondaybench.prompt_builder import build_prompt
from mondaybench.scenarios import load_scenario

REPO_ROOT = Path(__file__).resolve().parent.parent
D = REPO_ROOT / "scenarios" / "monday-003"

SOURCE_ORDER = [
    "slack.md",
    "emails.md",
    "meetings.md",
    "tasks.md",
    "work-items.csv",
    "availability.csv",
]


@pytest.fixture(scope="module")
def scenario():
    return load_scenario("monday-003")


@pytest.fixture(scope="module")
def rubric_yaml():
    return yaml.safe_load((D / "rubric.yaml").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def gt():
    return yaml.safe_load((D / "ground-truth.yaml").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def work_items():
    text = (D / "work-items.csv").read_text(encoding="utf-8")
    return {r["work_item"]: r for r in csv.DictReader(io.StringIO(text))}


@pytest.fixture(scope="module")
def availability():
    text = (D / "availability.csv").read_text(encoding="utf-8")
    return list(csv.DictReader(io.StringIO(text)))


def minutes(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


# --------------------------------------------------------------------------
# Scenario shape and prompt determinism
# --------------------------------------------------------------------------


def test_source_order_is_the_declared_six(scenario):
    assert scenario.sources == SOURCE_ORDER


def test_scenario_is_a_calibration_draft(scenario):
    assert scenario.status == "calibration"
    assert scenario.is_calibration is True
    assert scenario.scenario_version == "0.1"
    assert scenario.rubric.version == "0.1"


def test_the_prompt_is_deterministic(scenario):
    a, b = build_prompt(scenario), build_prompt(scenario)
    assert a.text == b.text
    assert a.sha256 == b.sha256 and len(a.sha256) == 64


def test_every_source_reaches_the_prompt(scenario):
    text = build_prompt(scenario).text
    for name in SOURCE_ORDER:
        first_line = (D / name).read_text(encoding="utf-8").strip().splitlines()[0]
        assert first_line in text, f"{name} is missing from the assembled prompt"


def test_the_prompt_hash_covers_the_assembly_not_the_template(scenario):
    import hashlib

    built = build_prompt(scenario)
    template = (D / "prompt.md").read_bytes()
    assert hashlib.sha256(template).hexdigest() != built.sha256


def test_the_answer_key_never_reaches_the_candidate(scenario):
    """ground-truth.yaml is not a source, and none of its content leaks in."""
    assert "ground-truth.yaml" not in scenario.sources
    text = build_prompt(scenario).text
    for marker in ("critical_path:", "earliest_feasible_plan", "settled_facts", "bottleneck"):
        assert marker not in text


# --------------------------------------------------------------------------
# The design rule: facts yes, conclusions no
# --------------------------------------------------------------------------

# Each entry is a conclusion the model is meant to derive. If a candidate source
# ever starts saying one of these outright, the criterion that scores it stops
# measuring reasoning.
FORBIDDEN_IN_SOURCES = {
    "names the bottleneck": r"bottleneck",
    "names the critical path": r"critical\s+path",
    "names the cycle": r"\bcircular\b|\bcycle\b",
    "delivers a priority verdict": r"not a priority|deprioriti[sz]",
    "states the earliest delivery": r"earliest (realistic |feasible )?(completion|delivery)",
    "sequences Marcus for the model": r"drop it behind|behind sso",
    "declares something non-blocking": r"non-?blocking|is not a blocker|does not block",
    "explains how to break the cycle": r"break(s|ing)? the (cycle|loop|dependency)",
}


@pytest.mark.parametrize("label,pattern", sorted(FORBIDDEN_IN_SOURCES.items()))
def test_no_candidate_source_states_a_conclusion(label, pattern):
    """The prompt may ask for these. The evidence must not answer them."""
    offenders = []
    for name in SOURCE_ORDER:
        text = (D / name).read_text(encoding="utf-8")
        for m in re.finditer(pattern, text, re.I):
            line = text[: m.start()].count("\n") + 1
            offenders.append(f"{name}:{line}")
    assert offenders == [], f"source {label}: {offenders}"


# --------------------------------------------------------------------------
# Rubric
# --------------------------------------------------------------------------


def test_rubric_totals_exactly_one_hundred(rubric_yaml, scenario):
    assert sum(d["max_points"] for d in rubric_yaml["dimensions"].values()) == 100
    assert rubric_yaml["total_points"] == 100
    assert scenario.rubric.total_base_points == 100


@pytest.mark.parametrize(
    "dimension",
    [
        "critical_path_and_dependencies",
        "resource_allocation",
        "planning_and_parallelization",
        "replanning",
        "state_reconstruction",
        "delivery_and_uncertainty",
    ],
)
def test_each_dimension_sums_to_its_own_maximum(rubric_yaml, dimension):
    d = rubric_yaml["dimensions"][dimension]
    assert sum(c["points"] for c in d["criteria"]) == d["max_points"]


def test_the_rubric_scores_twenty_criteria(scenario):
    assert len(scenario.rubric.criteria) == 20


def test_partial_is_always_half(rubric_yaml):
    for d in rubric_yaml["dimensions"].values():
        for c in d["criteria"]:
            assert c["partial_points"] == c["points"] / 2, c["id"]


def test_the_penalty_cap_is_twenty_five(scenario, rubric_yaml):
    assert rubric_yaml["global_penalties"]["max_penalty"] == 25
    assert scenario.rubric.maximum_global_penalty == 25


def test_penalty_names_map_onto_the_shared_types(scenario):
    """A rubric may rename a penalty; the stored type stays shared."""
    assert set(scenario.rubric.penalties) == {
        "MATERIAL_HALLUCINATION",
        "PROHIBITED_ACTION",
        "MAJOR_PLANNING_ERROR",
        "MAJOR_CONTRADICTION",
    }


# --------------------------------------------------------------------------
# Dependency graph and canonical schedule
# --------------------------------------------------------------------------


def test_every_dependency_names_something_real(gt, work_items):
    derived = {"packaging_approval", "billing_migration_and_backfill", "screenshots"}
    known = set(work_items) | derived
    for task, spec in gt["dependencies"].items():
        assert task in known, task
        for requirement in spec["requires"]:
            assert requirement in known, f"{task} requires unknown {requirement}"


def test_the_critical_path_is_a_real_chain(gt):
    path, deps = gt["critical_path"], gt["dependencies"]
    for earlier, later in zip(path, path[1:]):
        assert earlier in deps[later]["requires"], f"{later} does not require {earlier}"


def test_the_critical_path_is_the_longest_dependent_chain(gt, work_items):
    hours = sum(float(work_items[t]["duration_hours"]) for t in gt["critical_path"])
    assert hours == 10  # 3 + 4 + 2 + 1


def test_the_canonical_schedule_respects_the_stated_durations(gt, work_items):
    for day in ("monday", "tuesday"):
        for step in gt["earliest_feasible_plan"][day]:
            spent = (minutes(step["end"]) - minutes(step["start"])) / 60
            assert spent == float(work_items[step["task"]]["duration_hours"]), step["task"]


def test_the_canonical_schedule_uses_the_declared_owners(gt, work_items):
    for day in ("monday", "tuesday"):
        for step in gt["earliest_feasible_plan"][day]:
            assert step["owner"] == work_items[step["task"]]["owner"], step["task"]


def test_the_canonical_schedule_runs_in_dependency_order(gt):
    plan = gt["earliest_feasible_plan"]
    order = [s["task"] for day in ("monday", "tuesday") for s in plan[day]]
    assert order == gt["critical_path"]


def test_no_step_starts_before_the_one_it_depends_on_ends(gt):
    plan = gt["earliest_feasible_plan"]
    steps = [(0, s) for s in plan["monday"]] + [(1, s) for s in plan["tuesday"]]
    for (d1, a), (d2, b) in zip(steps, steps[1:]):
        assert (d2, minutes(b["start"])) >= (d1, minutes(a["end"])), f"{b['task']} overlaps {a['task']}"


def test_the_canonical_schedule_fits_inside_availability(gt, availability):
    dates = {"monday": "2026-09-21", "tuesday": "2026-09-22"}
    for day, date in dates.items():
        for step in gt["earliest_feasible_plan"][day]:
            rows = [a for a in availability if a["person"] == step["owner"] and a["date"] == date]
            assert rows, f"{step['owner']} has no availability row for {date}"
            assert any(
                minutes(r["available_from"]) <= minutes(step["start"])
                and minutes(step["end"]) <= minutes(r["available_until"])
                for r in rows
            ), f"{step['task']} falls outside {step['owner']}'s availability"


def test_the_earliest_delivery_matches_the_schedule(gt):
    last = gt["earliest_feasible_plan"]["tuesday"][-1]
    assert last["end"] == "12:30"
    assert gt["earliest_delivery"]["canonical"].startswith("2026-09-22T12:30")
    lo, hi = gt["earliest_delivery"]["accept_between"]
    assert lo < gt["earliest_delivery"]["canonical"] < hi


def test_the_delivery_beats_the_committed_deadline(gt, work_items):
    """Tuesday 12:30 against a Wednesday 17:00 commitment: over a day of slack."""
    assert work_items["sso_production_rollout"]["deadline"].startswith("2026-09-23T17:00")
    assert gt["earliest_delivery"]["canonical"] < work_items["sso_production_rollout"]["deadline"]


# --------------------------------------------------------------------------
# The newest-state facts the answer key rests on
# --------------------------------------------------------------------------


def test_security_approval_is_the_newest_state():
    slack = (D / "slack.md").read_text(encoding="utf-8")
    assert "Security review for Enterprise SSO is complete. Approved." in slack
    assert "unless the implementation scope materially changes" in slack
    # ...and the task list still says otherwise, which is the point.
    assert "unblock Security review" in (D / "tasks.md").read_text(encoding="utf-8")


def test_instrumentation_is_not_a_launch_blocker():
    slack = (D / "slack.md").read_text(encoding="utf-8")
    assert "Existing analytics are enough for launch monitoring" in slack
    assert "before launch" in (D / "tasks.md").read_text(encoding="utf-8")


def test_the_contoso_export_is_not_broken():
    slack = (D / "slack.md").read_text(encoding="utf-8")
    emails = (D / "emails.md").read_text(encoding="utf-8")
    assert "Export succeeds" in slack
    assert "imports correctly into our system" in emails
    assert "This isn't blocking production" in emails
    assert "investigate broken Contoso exports" in (D / "tasks.md").read_text(encoding="utf-8")


def test_mock_screenshots_are_accepted_for_approval():
    assert "Mock screenshots are fine for internal approval" in (D / "slack.md").read_text(
        encoding="utf-8"
    )
    assert "internal approval accepts design mockups" in (D / "meetings.md").read_text(
        encoding="utf-8"
    )


def test_daniel_does_not_yet_hold_the_migration_permissions():
    emails = (D / "emails.md").read_text(encoding="utf-8")
    assert "he doesn't currently have the production migration permissions" in emails
    assert "around 30 minutes" in emails


def test_the_board_revenue_section_waits_for_the_migration():
    slack = (D / "slack.md").read_text(encoding="utf-8")
    assert "freeze the revenue charts until the billing migration/backfill is complete" in slack
    assert "board_pack_revenue" in (D / "work-items.csv").read_text(encoding="utf-8")
    assert "board_pack_non_revenue" in (D / "work-items.csv").read_text(encoding="utf-8")


def test_marcus_owns_work_on_and_off_the_critical_path(work_items, gt):
    """The bottleneck has to be derivable from the table, and only from it."""
    marcus = [k for k, v in work_items.items() if v["owner"] == "Marcus"]
    on_path = [t for t in marcus if t in gt["critical_path"]]
    off_path = [t for t in marcus if t not in gt["critical_path"]]
    assert len(on_path) == 2 and off_path == ["onboarding_instrumentation"]


# --------------------------------------------------------------------------
# Evaluator and gates
# --------------------------------------------------------------------------


def test_the_calibration_evaluator_is_bound_to_this_scenario():
    cfg = load_evaluator("evaluator-opus5-v0.3-calibration")
    assert cfg.scenario == "monday-003"
    assert cfg.scenario_version == "0.1"
    assert cfg.rubric_version == "0.1"
    assert cfg.model_id == "claude-opus-5"
    assert cfg.temperature == 0
    assert cfg.require_evidence is True


def test_publication_is_refused_while_it_is_a_calibration_draft():
    from mondaybench.cli_official import cmd_publish

    with pytest.raises(BaseException):  # typer.Exit
        cmd_publish("monday-003", "evaluator-opus5-v0.3-calibration", None, 3)


def test_monday_001_and_002_are_untouched():
    """#003 is additive. Their frozen manifests must still verify."""
    import hashlib

    for scenario_id in ("monday-001", "monday-002"):
        manifest = yaml.safe_load(
            (REPO_ROOT / "scenarios" / scenario_id / "FROZEN.yaml").read_text(encoding="utf-8")
        )
        for name, expected in manifest["files"].items():
            actual = hashlib.sha256(
                (REPO_ROOT / "scenarios" / scenario_id / name).read_bytes()
            ).hexdigest()
            assert actual == expected, f"{scenario_id}/{name} changed"
