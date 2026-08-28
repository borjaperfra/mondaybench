"""Guards for monday-003 "Blockers", scenario 0.3 - frozen and official.

The scenario's whole design rests on one rule: every fact is stated somewhere
in the six candidate sources, and no conclusion is. A source that says "Marcus
is the bottleneck" or "this is the critical path" would turn a reasoning test
into a reading test, and nothing else in the harness would notice. That is what
`test_no_candidate_source_states_a_conclusion` is for, and v0.2 widens it: the
new answers are an allocation and a separation, so the words that would give
those away are forbidden too.

There are two dated commitments sharing one root dependency, so the graph tests
check both chains and the point where they meet. And there is a contested
engineer, so the resource graph is checked against the canonical plan: the plan
hands his substitutable work to the substitute, at the substitute's stated cost,
not at his.

Since the freeze, three more things are load-bearing. The scenario is immutable,
so `FROZEN.yaml` is verified byte for byte and every frozen file is checked for
CRLF - monday-002 once shipped a manifest that only verified on the machine that
wrote it. The rubric reweighting is justified against the archived v0.2 labels
rather than asserted. And every published mean is recomputed from the
evaluations on disk, so a hand-edited ranking cannot survive and no refused run
can reach a statistic.

The rest checks the things a hand-built scenario gets wrong quietly: a rubric
that no longer totals 100, a canonical schedule that violates its own durations
or somebody's calendar, a dependency graph naming work items that do not exist,
and the newest-state facts the whole answer key depends on.
"""

from __future__ import annotations

import csv
import json
import hashlib
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
ARCHIVE_V01 = REPO_ROOT / "archive" / "monday-003-v0.1"
ARCHIVE_V02 = REPO_ROOT / "archive" / "monday-003-v0.2"
ARCHIVE_V03C = REPO_ROOT / "archive" / "monday-003-v0.3-calibration"

EVALUATOR = "evaluator-opus5-v0.3"

# The candidate prompt has not changed since v0.2. v0.3 is a rubric revision.
PROMPT_SHA256 = "aaf788f309d955d2b427c86fe7d95d2bbf88575fde7306adcfd74b0ec4a4103f"

SOURCE_ORDER = [
    "slack.md",
    "emails.md",
    "meetings.md",
    "tasks.md",
    "work-items.csv",
    "availability.csv",
]

DAYS = ("monday", "tuesday")
DAY_DATES = {"monday": "2026-09-21", "tuesday": "2026-09-22"}

# Steps the canonical plan needs that are not tracked work items: the two
# knowledge transfers. Their durations come from the sources, not the table.
AUXILIARY_STEPS = {
    "contoso_permission_walkthrough": 0.5,
    "migration_permissions_transfer": 0.5,
}


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


def plan_steps(gt):
    """The canonical plan flattened into (day_index, step) pairs."""
    return [
        (i, step)
        for i, day in enumerate(DAYS)
        for step in gt["canonical_plan"][day]
    ]


def effective_duration(gt, work_items, task: str, owner: str) -> float:
    """Hours the plan may spend on a task, given who it handed the task to."""
    if task in AUXILIARY_STEPS:
        return AUXILIARY_STEPS[task]
    spec = gt["resources"].get(task, {})
    if owner not in spec.get("preferred", []):
        for sub in spec.get("substitutes", []):
            if sub["owner"] == owner:
                return float(sub["duration_hours"])
        raise AssertionError(f"{owner} is neither preferred nor a substitute for {task}")
    return float(work_items[task]["duration_hours"])


# --------------------------------------------------------------------------
# Scenario shape and prompt determinism
# --------------------------------------------------------------------------


def test_source_order_is_the_declared_six(scenario):
    assert scenario.sources == SOURCE_ORDER


def test_scenario_is_frozen_and_official_at_v0_3(scenario):
    assert scenario.status == "official"
    assert scenario.is_calibration is False
    assert scenario.scenario_version == "0.3"
    assert scenario.rubric.version == "0.3"
    assert scenario.benchmark_version == "0.3"
    assert scenario.official_runs == 3


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
    built = build_prompt(scenario)
    template = (D / "prompt.md").read_bytes()
    assert hashlib.sha256(template).hexdigest() != built.sha256


def test_the_prompt_is_not_the_v0_1_prompt(scenario):
    """Different sources, different assembly. Replaying v0.1 answers is refused."""
    v01 = "efd837502f4174663c8904fb3e01089de3017ffaff9f154ff611d4bc5286f84e"
    assert build_prompt(scenario).sha256 != v01


def test_the_prompt_is_byte_identical_to_v0_2(scenario):
    """v0.3 is a rubric revision. If this fails, a candidate-visible source moved
    and the v0.2 responses stop being valid samples of this prompt."""
    assert build_prompt(scenario).sha256 == PROMPT_SHA256
    recorded = (ARCHIVE_V02 / "RENDERED_PROMPT_SHA256.txt").read_text(encoding="utf-8").split()[0]
    assert recorded == PROMPT_SHA256
    for name in SOURCE_ORDER + ["prompt.md"]:
        live = (D / name).read_bytes()
        archived = (ARCHIVE_V02 / "scenario" / name).read_bytes()
        assert live == archived, f"{name} changed between v0.2 and v0.3"


def test_the_answer_key_never_reaches_the_candidate(scenario):
    """ground-truth.yaml is not a source, and none of its content leaks in."""
    assert "ground-truth.yaml" not in scenario.sources
    text = build_prompt(scenario).text
    for marker in (
        "dependencies:",
        "canonical_plan",
        "settled_facts",
        "resource_contention",
        "allocation_comparison",
        "bottleneck",
    ):
        assert marker not in text


# --------------------------------------------------------------------------
# The design rule: facts yes, conclusions no
# --------------------------------------------------------------------------

# Each entry is a conclusion the model is meant to derive. If a candidate source
# ever starts saying one of these outright, the criterion that scores it stops
# measuring reasoning. The second block is new in v0.2, where the answers are an
# allocation and a separation rather than a chain.
FORBIDDEN_IN_SOURCES = {
    "names the bottleneck": r"bottleneck",
    "names the critical path": r"critical\s+path",
    "names the cycle": r"\bcircular\b|\bcycle\b|chicken[- ]and[- ]egg",
    "delivers a priority verdict": r"not a priority|deprioriti[sz]",
    "states the earliest delivery": r"earliest (realistic |feasible )?(completion|delivery)",
    "sequences the engineer for the model": r"drop it behind|behind sso",
    "declares something non-blocking": r"non-?blocking|is not a blocker|does not block",
    "explains how to break the cycle": r"break(s|ing)? the (cycle|loop|dependency)",
    # v0.2: the answers are now an allocation and a separation.
    "names the resource contention": r"contention|compet(es|ing) for|stretched across",
    "hands over the allocation": r"\bsubstitut|reserve (marcus|him)|protect (marcus|him)|free up marcus",
    "grades an option for the model": r"suboptimal|the better (option|use|plan)|best use of",
    "separates the two Contoso items": r"red herring|the real (blocker|issue|problem)|actually the blocker",
    "labels a source as stale": r"\bstale\b|out of date|no longer accurate",
}


@pytest.mark.parametrize("label,pattern", sorted(FORBIDDEN_IN_SOURCES.items()))
def test_no_candidate_source_states_a_conclusion(label, pattern):
    """The prompt may ask for these. The evidence must not answer them."""
    offenders = []
    for name in SOURCE_ORDER:
        text = (D / name).read_text(encoding="utf-8")
        for m in re.finditer(pattern, text, re.I):
            line = text[: m.start()].count("\n") + 1
            offenders.append(f"{name}:{line} {m.group(0)!r}")
    assert offenders == [], f"source {label}: {offenders}"


def test_work_items_business_context_states_no_relationships(work_items):
    """v0.1 leaked the whole chain through this column. It stays commercial."""
    relational = re.compile(
        r"required before|prerequisite|depends on|blocks|input for|before the",
        re.I,
    )
    offenders = [
        (k, v["business_context"])
        for k, v in work_items.items()
        if relational.search(v["business_context"])
    ]
    assert offenders == []


def test_meetings_do_not_restate_the_sso_chain():
    """v0.1 summarised the Slack thread into four ordered bullets. Never again."""
    text = (D / "meetings.md").read_text(encoding="utf-8").lower()
    chain_words = ("compatibility patch", "regression", "rollout")
    assert sum(w in text for w in chain_words) <= 1, "meetings.md is reassembling the chain"


def test_the_prompt_does_not_name_the_answer_types():
    """v0.1 asked section 4 for 'circular, stale, or removable dependencies'.

    Naming the classes told the model that all three existed. The scene-setting
    line above the list may still say the information is partly out of date -
    that is the situation, not the answer - so only the numbered requirements
    are checked.
    """
    lines = (D / "prompt.md").read_text(encoding="utf-8").lower().splitlines()
    requirements = [ln for ln in lines if re.match(r"^\d+\.", ln.strip())]
    assert len(requirements) == 6
    for line in requirements:
        for word in ("circular", "stale", "removable", "bottleneck", "contention"):
            assert word not in line, f"prompt requirement names {word!r}: {line}"


# --------------------------------------------------------------------------
# Rubric
# --------------------------------------------------------------------------


def test_rubric_totals_exactly_one_hundred(rubric_yaml, scenario):
    assert sum(d["max_points"] for d in rubric_yaml["dimensions"].values()) == 100
    assert rubric_yaml["total_points"] == 100
    assert scenario.rubric.total_base_points == 100


@pytest.mark.parametrize(
    "dimension,max_points",
    [
        ("critical_path_and_dependencies", 21),
        ("resource_allocation", 25),
        ("planning_and_parallelization", 18),
        ("decision_quality", 14),
        ("state_reconstruction", 10),
        ("accuracy_and_uncertainty", 12),
    ],
)
def test_each_dimension_sums_to_its_own_maximum(rubric_yaml, dimension, max_points):
    d = rubric_yaml["dimensions"][dimension]
    assert d["max_points"] == max_points
    assert sum(c["points"] for c in d["criteria"]) == max_points


def test_the_rubric_scores_twentyone_criteria(scenario):
    assert len(scenario.rubric.criteria) == 21


def test_weight_moved_off_reading_and_onto_choosing(rubric_yaml):
    """v0.1 put 30 points on reconstructing one chain and 20 on allocation."""
    dims = rubric_yaml["dimensions"]
    assert (
        dims["resource_allocation"]["max_points"]
        > dims["critical_path_and_dependencies"]["max_points"]
    )
    assert (
        dims["resource_allocation"]["max_points"] + dims["decision_quality"]["max_points"]
        == 39
    )


def test_the_contested_allocation_is_the_heaviest_single_criterion(scenario):
    heaviest = max(scenario.rubric.criteria, key=lambda c: c.points_pass)
    assert heaviest.id == "scarce_resource_allocation"
    assert heaviest.points_pass == 10


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


def test_no_criterion_id_survives_from_v0_1(scenario):
    """v0.1 verdicts must not silently replay against v0.2 runs."""
    v01 = yaml.safe_load(
        (ARCHIVE_V01 / "scenario" / "rubric.yaml").read_text(encoding="utf-8")
    )
    old = {c["id"] for d in v01["dimensions"].values() for c in d["criteria"]}
    new = {c.id for c in scenario.rubric.criteria}
    assert old & new == set()


# --------------------------------------------------------------------------
# Dependency graph
# --------------------------------------------------------------------------


def test_every_dependency_names_something_real(gt, work_items):
    derived = {"packaging_approval"}
    known = set(work_items) | derived
    for task, spec in gt["dependencies"].items():
        assert task in known, task
        for requirement in spec["requires"]:
            assert requirement in known, f"{task} requires unknown {requirement}"


@pytest.mark.parametrize("chain", ["sso", "contoso_compliance", "pricing", "board"])
def test_each_declared_chain_is_a_real_chain(gt, chain):
    steps, deps = gt["chains"][chain]["steps"], gt["dependencies"]
    for earlier, later in zip(steps, steps[1:]):
        assert earlier in deps[later]["requires"], f"{later} does not require {earlier}"


def test_the_two_dated_chains_share_exactly_one_root(gt):
    """The competition only works if both paths queue behind the same task."""
    sso = gt["chains"]["sso"]["steps"]
    contoso = gt["chains"]["contoso_compliance"]["steps"]
    assert set(sso) & set(contoso) == {"billing_schema_migration"}
    assert sso[0] == contoso[0] == "billing_schema_migration"


def test_the_competing_chain_is_shorter_and_due_sooner(gt, work_items):
    """Otherwise there is nothing to weigh: one path simply dominates."""
    sso, contoso = gt["chains"]["sso"], gt["chains"]["contoso_compliance"]
    assert contoso["depth"] < sso["depth"]
    assert contoso["work_hours"] < sso["work_hours"]
    assert (
        work_items["contoso_compliance_export"]["external_deadline"]
        < work_items["sso_production_rollout"]["external_deadline"]
    )


def test_the_sso_chain_is_ten_hours(gt, work_items):
    hours = sum(float(work_items[t]["duration_hours"]) for t in gt["chains"]["sso"]["steps"])
    assert hours == 10  # 3 + 4 + 2 + 1
    assert gt["chains"]["sso"]["work_hours"] == 10


def test_the_formatter_is_on_no_chain(gt):
    """The noisy item must be reachable from nothing, or the split is fake."""
    assert "contoso_export_formatter" in gt["independent_or_nonblocking"]
    assert "contoso_export_formatter" not in gt["dependencies"]
    for chain in gt["chains"].values():
        assert "contoso_export_formatter" not in chain["steps"]


def test_only_customer_deliverables_carry_external_deadlines(work_items):
    """v0.1 gave patch, QA and rollout the same synthetic Wednesday 17:00."""
    dated = {k for k, v in work_items.items() if v["external_deadline"]}
    assert dated == {
        "billing_schema_migration",
        "sso_production_rollout",
        "contoso_compliance_export",
        "onboarding_launch",
        "pricing_page",
        "board_pack_non_revenue",
        "board_pack_revenue",
    }
    for step in ("api_compatibility_patch", "sso_regression", "contoso_permission_patch"):
        assert work_items[step]["external_deadline"] == "", step


def test_no_two_steps_of_one_chain_share_a_deadline(gt, work_items):
    for name, chain in gt["chains"].items():
        dates = [
            work_items[t]["external_deadline"]
            for t in chain["steps"]
            if t in work_items and work_items[t]["external_deadline"]
        ]
        assert len(dates) == len(set(dates)), f"{name} has duplicate step deadlines"


# --------------------------------------------------------------------------
# Resource graph
# --------------------------------------------------------------------------


def test_every_resource_entry_names_a_real_work_item(gt, work_items):
    for task in gt["resources"]:
        assert task in work_items, task


def test_the_resource_owners_match_the_table(gt, work_items):
    for task, spec in gt["resources"].items():
        assert work_items[task]["owner"] in spec["preferred"], task


def test_the_contested_engineer_holds_three_items_and_one_substitute(gt, work_items):
    c = gt["resource_contention"]
    owned = {k for k, v in work_items.items() if v["owner"] == c["person"]}
    assert set(c["claimed_by"]) <= owned

    substitutable = [
        t for t in c["claimed_by"] if gt["resources"].get(t, {}).get("substitutes")
    ]
    assert substitutable == [c["substitutable_item"]]
    subs = gt["resources"][c["substitutable_item"]]["substitutes"]
    assert [s["owner"] for s in subs] == [c["substitute"]]


def test_the_sso_work_has_no_substitute(gt):
    for task in ("api_compatibility_patch", "sso_production_rollout"):
        assert gt["resources"][task]["substitutes"] == [], task


def test_substituting_is_a_real_trade(gt, work_items):
    """Slower and it costs the engineer half an hour, but it buys back his day."""
    sub = gt["resources"]["contoso_permission_patch"]["substitutes"][0]
    own = float(work_items["contoso_permission_patch"]["duration_hours"])
    assert sub["duration_hours"] > own
    assert sub["handoff_minutes"] > 0
    assert sub["handoff_from"] == gt["resource_contention"]["person"]


def test_the_substitution_facts_are_stated_in_the_sources():
    """Derivable, but only because every input is on the page."""
    slack = (D / "slack.md").read_text(encoding="utf-8")
    assert "three and a half hours for me" in slack
    assert "half an hour with Marcus" in slack
    assert "Two hours if I do it" in slack
    assert "Nobody else has been inside it since the spike" in slack


# --------------------------------------------------------------------------
# Canonical plan, checked against durations, dependencies and calendars
# --------------------------------------------------------------------------


def test_the_canonical_schedule_respects_the_effective_durations(gt, work_items):
    for _, step in plan_steps(gt):
        spent = (minutes(step["end"]) - minutes(step["start"])) / 60
        expected = effective_duration(gt, work_items, step["task"], step["owner"])
        assert spent == expected, f"{step['task']} takes {spent}h, expected {expected}h"


def test_the_canonical_schedule_hands_the_contested_item_to_the_substitute(gt):
    step = next(s for _, s in plan_steps(gt) if s["task"] == "contoso_permission_patch")
    assert step["owner"] == gt["resource_contention"]["substitute"]


def test_nobody_is_in_two_places_at_once(gt):
    by_owner: dict[str, list] = {}
    for day, step in plan_steps(gt):
        by_owner.setdefault(step["owner"], []).append(
            (day, minutes(step["start"]), minutes(step["end"]), step["task"])
        )
    for owner, slots in by_owner.items():
        slots.sort()
        for (d1, s1, e1, t1), (d2, s2, e2, t2) in zip(slots, slots[1:]):
            if d1 == d2:
                assert e1 <= s2, f"{owner}: {t1} overlaps {t2}"


def test_no_planned_step_starts_before_its_dependencies_end(gt):
    ends: dict[str, tuple[int, int]] = {}
    for day, step in plan_steps(gt):
        ends[step["task"]] = (day, minutes(step["end"]))
    for day, step in plan_steps(gt):
        for requirement in gt["dependencies"].get(step["task"], {}).get("requires", []):
            assert requirement in ends, f"{step['task']} needs unscheduled {requirement}"
            assert (day, minutes(step["start"])) >= ends[requirement], (
                f"{step['task']} starts before {requirement} ends"
            )


def test_the_canonical_schedule_fits_inside_availability(gt, availability):
    for day, step in plan_steps(gt):
        date = DAY_DATES[DAYS[day]]
        rows = [
            a
            for a in availability
            if a["person"] == step["owner"]
            and a["date"] == date
            and a["status"] == "available"
        ]
        assert rows, f"{step['owner']} is not available on {date}"
        assert any(
            minutes(r["available_from"]) <= minutes(step["start"])
            and minutes(step["end"]) <= minutes(r["available_until"])
            for r in rows
        ), f"{step['task']} falls outside {step['owner']} availability on {date}"


def test_both_dated_commitments_are_met_by_the_canonical_plan(gt, work_items):
    finish = {}
    for day, step in plan_steps(gt):
        finish[step["task"]] = f"{DAY_DATES[DAYS[day]]}T{step['end']}:00+02:00"
    for task in ("sso_production_rollout", "contoso_compliance_export"):
        assert finish[task] < work_items[task]["external_deadline"], task


# --------------------------------------------------------------------------
# Delivery bounds
# --------------------------------------------------------------------------


def test_the_delivery_bound_is_a_bound_not_a_window(gt):
    """v0.1 scored a 12:00-13:30 clock range and had to pass a model that beat it."""
    sso = gt["earliest_delivery"]["sso"]
    assert "accept_between" not in sso
    assert sso["lower_bound"] == sso["canonical"]


def test_the_bound_matches_the_last_step_of_the_plan(gt):
    rollout = next(
        s for s in gt["canonical_plan"]["tuesday"] if s["task"] == "sso_production_rollout"
    )
    assert gt["earliest_delivery"]["sso"]["canonical"].startswith(
        f"2026-09-22T{rollout['end']}"
    )


def test_the_bound_is_pinned_by_a_calendar_not_by_arithmetic(gt, availability):
    """Compressing the earlier steps must not move it. That is what makes it robust."""
    rollout_owner = next(
        s["owner"]
        for s in gt["canonical_plan"]["tuesday"]
        if s["task"] == "sso_production_rollout"
    )
    row = next(
        a for a in availability if a["person"] == rollout_owner and a["date"] == "2026-09-22"
    )
    floor = minutes(row["available_from"]) + 60  # one hour of rollout
    assert gt["earliest_delivery"]["sso"]["lower_bound"].endswith(
        f"{floor // 60:02d}:{floor % 60:02d}:00+02:00"
    )


def test_the_delivery_beats_the_committed_deadline(gt, work_items):
    assert work_items["sso_production_rollout"]["external_deadline"].startswith(
        "2026-09-23T17:00"
    )
    assert (
        gt["earliest_delivery"]["sso"]["canonical"]
        < work_items["sso_production_rollout"]["external_deadline"]
    )


def test_keeping_the_engineer_on_both_paths_is_recorded_as_feasible(gt):
    """The judge must not treat a slower allocation as a dependency violation."""
    verdict = gt["allocation_comparison"]["marcus_does_both"]["verdict"]
    assert "feasible" in verdict and "worse" in verdict


# --------------------------------------------------------------------------
# Availability
# --------------------------------------------------------------------------


def test_availability_covers_everyone_monday_to_friday(availability, work_items):
    people = {v["owner"] for v in work_items.values()} | {"Daniel"}
    dates = {f"2026-09-{d}" for d in range(21, 26)}
    have = {(a["person"], a["date"]) for a in availability}
    missing = {(p, d) for p in people for d in dates} - have
    assert missing == set(), f"availability gaps: {sorted(missing)}"


def test_out_of_office_is_explicit_not_an_absent_row(availability):
    """v0.1 left silence to do the work, and the answer key had to apologise."""
    for row in availability:
        assert row["status"] in {"available", "out"}, row
        if row["status"] == "out":
            assert row["available_from"] == "" and row["available_until"] == ""
        else:
            assert minutes(row["available_from"]) < minutes(row["available_until"])


def test_exactly_two_people_are_constrained(availability):
    """Everyone else has a normal week, so a constraint means something."""
    constrained = {
        a["person"]
        for a in availability
        if a["status"] == "out" or a["notes"] != "Normal working day"
    }
    assert constrained == {"Elena", "Marcus"}


# --------------------------------------------------------------------------
# The newest-state facts the answer key rests on
# --------------------------------------------------------------------------


def test_security_approval_arrives_only_by_email():
    """No Slack 'so no more Security gate?' / 'Correct.' this time."""
    emails = (D / "emails.md").read_text(encoding="utf-8")
    slack = (D / "slack.md").read_text(encoding="utf-8")
    assert "Approved for the current implementation scope" in emails
    assert "only if the authentication flow itself changes" in emails
    assert "Security" not in slack
    # ...and the task list and the meeting notes still say otherwise.
    assert "unblock Security review" in (D / "tasks.md").read_text(encoding="utf-8")
    assert "still listed as outstanding" in (D / "meetings.md").read_text(encoding="utf-8")


def test_the_two_contoso_items_are_in_different_threads_on_different_days():
    """The separation is the criterion. It must not be handed over in one thread."""
    slack = (D / "slack.md").read_text(encoding="utf-8")
    fmt = slack.index("## Friday 17:24")
    perm = slack.index("## Monday 08:06")
    assert fmt < perm
    formatting_thread = slack[fmt:perm]
    assert "delegated admin" not in formatting_thread.lower()
    permission_thread = slack[perm : slack.index("## Monday 08:19")]
    assert "DD/MM" not in permission_thread
    assert "date format" not in permission_thread


def test_the_contractual_deadline_is_stated_only_by_the_customer():
    emails = (D / "emails.md").read_text(encoding="utf-8")
    assert "16:00 CET on Tuesday 22 September" in emails
    assert "section 8.3" in emails
    assert "16:00" not in (D / "slack.md").read_text(encoding="utf-8")


def test_the_format_complaint_is_cosmetic_and_says_so_as_a_fact():
    slack = (D / "slack.md").read_text(encoding="utf-8")
    emails = (D / "emails.md").read_text(encoding="utf-8")
    assert "The export completes and the file is valid" in slack
    assert "imports correctly into our system" in emails
    assert "investigate broken Contoso exports" in (D / "tasks.md").read_text(encoding="utf-8")


def test_instrumentation_is_not_required_for_the_launch():
    slack = (D / "slack.md").read_text(encoding="utf-8")
    assert "Existing analytics are enough for launch monitoring" in slack
    assert "before launch" in (D / "tasks.md").read_text(encoding="utf-8")


def test_the_pricing_deadlock_is_stated_in_halves_and_never_named():
    slack = (D / "slack.md").read_text(encoding="utf-8")
    emails = (D / "emails.md").read_text(encoding="utf-8")
    assert "cannot go public until packaging approval clears" in slack
    assert "as soon as the page is built and I can take the screenshots off it" in slack
    assert "Mockups are acceptable" in emails
    # the resolution lives in a checklist, not in anyone's advice
    assert "mockup" not in slack.lower()


def test_daniel_does_not_yet_hold_the_migration_permissions():
    emails = (D / "emails.md").read_text(encoding="utf-8")
    assert "doesn't currently have the production migration permissions" in emails
    assert "around 30 minutes" in emails


def test_the_board_revenue_section_waits_for_the_backfill():
    slack = (D / "slack.md").read_text(encoding="utf-8")
    assert "until the billing migration and its backfill are complete" in slack
    assert "ninety minutes" in slack
    assert "billing_backfill" in (D / "work-items.csv").read_text(encoding="utf-8")


def test_the_default_assignment_of_the_contested_item_is_visible(gt, work_items):
    """The model has to override something, so the something has to be there."""
    assert work_items["contoso_permission_patch"]["owner"] == "Marcus"
    assert gt["resources"]["contoso_permission_patch"]["default_assignment"] == "Marcus"
    assert "assigned to Marcus" in (D / "slack.md").read_text(encoding="utf-8")


def test_the_task_list_carries_four_urgent_entries_the_evidence_overrides(gt):
    urgent = [
        line
        for line in (D / "tasks.md").read_text(encoding="utf-8").splitlines()
        if line.startswith("- \U0001f534")
    ]
    assert len(urgent) == 4
    assert len(gt["stale_items"]) >= 4


# --------------------------------------------------------------------------
# Evaluator and gates
# --------------------------------------------------------------------------


def test_the_official_evaluator_is_bound_to_this_scenario():
    cfg = load_evaluator(EVALUATOR)
    assert cfg.scenario == "monday-003"
    assert cfg.scenario_version == "0.3"
    assert cfg.rubric_version == "0.3"
    assert cfg.model_id == "claude-opus-5"
    assert cfg.temperature == 0
    assert cfg.require_evidence is True


def test_the_v0_1_evaluator_is_gone_from_the_live_tree():
    """It is bound to a scenario version that no longer exists on disk."""
    assert not (REPO_ROOT / "evaluators" / "evaluator-opus5-v0.3-calibration.yaml").exists()
    assert (ARCHIVE_V01 / "evaluator-opus5-v0.3-calibration.yaml").exists()


def test_the_scenario_is_frozen_and_the_manifest_verifies():
    """A published scenario is immutable. This is what makes that checkable."""
    import yaml as _yaml

    manifest = _yaml.safe_load((D / "FROZEN.yaml").read_text(encoding="utf-8"))
    assert manifest["frozen"] is True
    assert manifest["prompt_sha256"] == PROMPT_SHA256
    assert manifest["rubric_version"] == "0.3"
    assert set(manifest["files"]) == set(SOURCE_ORDER) | {
        "prompt.md",
        "rubric.yaml",
        "scenario.yaml",
        "ground-truth.yaml",
    }
    for name, expected in manifest["files"].items():
        actual = hashlib.sha256((D / name).read_bytes()).hexdigest()
        assert actual == expected, name


def test_every_frozen_file_uses_lf_so_the_manifest_travels():
    """monday-002 shipped a manifest that only verified on the machine that wrote it."""
    for name in sorted(
        set(SOURCE_ORDER) | {"prompt.md", "rubric.yaml", "scenario.yaml", "ground-truth.yaml"}
    ):
        # 13 is CR. Written as an ordinal so no escape survives a round trip.
        assert 13 not in (D / name).read_bytes(), name


# --------------------------------------------------------------------------
# Integrity
# --------------------------------------------------------------------------


def test_the_archived_v0_1_scenario_records_its_own_prompt_hash():
    recorded = (ARCHIVE_V01 / "RENDERED_PROMPT_SHA256.txt").read_text(encoding="utf-8").split()[0]
    assert recorded == "efd837502f4174663c8904fb3e01089de3017ffaff9f154ff611d4bc5286f84e"


def test_monday_001_and_002_are_untouched():
    """#003 is additive. Their frozen manifests must still verify."""
    for scenario_id in ("monday-001", "monday-002"):
        manifest = yaml.safe_load(
            (REPO_ROOT / "scenarios" / scenario_id / "FROZEN.yaml").read_text(encoding="utf-8")
        )
        for name, expected in manifest["files"].items():
            actual = hashlib.sha256(
                (REPO_ROOT / "scenarios" / scenario_id / name).read_bytes()
            ).hexdigest()
            assert actual == expected, f"{scenario_id}/{name} changed"


# --------------------------------------------------------------------------
# The v0.3 rubric revision, justified against v0.2 data
# --------------------------------------------------------------------------


@pytest.fixture(scope="module")
def v02_labels():
    """The v0.2 criterion labels, straight out of the archive."""
    base = ARCHIVE_V02 / "evaluations-evaluator-opus5-v0.3-calibration-2"
    out = {}
    for model_dir in sorted(base.iterdir()):
        for path in sorted(model_dir.glob("run-*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            out[model_dir.name] = {cid: v["result"] for cid, v in data["criteria"].items()}
    return out


@pytest.fixture(scope="module")
def v02_rubric():
    return yaml.safe_load((ARCHIVE_V02 / "scenario" / "rubric.yaml").read_text(encoding="utf-8"))


def _points(rubric_yaml):
    return {
        c["id"]: c["points"]
        for d in rubric_yaml["dimensions"].values()
        for c in d["criteria"]
    }


def test_every_weight_that_went_down_had_zero_variance_in_v0_2(
    rubric_yaml, v02_rubric, v02_labels
):
    """The reweighting must not be able to reorder the field.

    A criterion every model scored identically contributes the same number to
    every total, so cutting its weight subtracts a constant. That is the whole
    justification for where v0.3 found its points, and it is checkable.
    """
    new, old = _points(rubric_yaml), _points(v02_rubric)
    reduced = [cid for cid in old if cid in new and new[cid] < old[cid]]
    assert reduced, "v0.3 is supposed to have freed weight"
    for cid in reduced:
        results = {labels[cid] for labels in v02_labels.values()}
        assert len(results) == 1, f"{cid} discriminated in v0.2 and must not lose weight"
        assert results == {"PASS"}, cid


def test_the_freed_points_pay_for_the_new_and_reinforced_criteria(rubric_yaml, v02_rubric):
    new, old = _points(rubric_yaml), _points(v02_rubric)
    freed = sum(old[cid] - new[cid] for cid in old if cid in new and new[cid] < old[cid])
    added = sum(new[cid] - old.get(cid, 0) for cid in new if new[cid] > old.get(cid, 0))
    assert freed == added == 7
    assert sum(new.values()) == sum(old.values()) == 100


def test_sso_chain_kept_but_repriced(rubric_yaml, v02_rubric, v02_labels):
    new, old = _points(rubric_yaml), _points(v02_rubric)
    assert old["sso_chain"] == 8 and new["sso_chain"] == 4
    assert {labels["sso_chain"] for labels in v02_labels.values()} == {"PASS"}


def test_factual_plan_accuracy_exists_and_is_a_three_band_criterion(rubric_yaml, scenario):
    criterion = next(c for c in scenario.rubric.criteria if c.id == "factual_plan_accuracy")
    assert criterion.points_pass == 5
    assert criterion.points_partial == 2.5
    assert criterion.points_fail == 0
    raw = next(
        c
        for d in rubric_yaml["dimensions"].values()
        for c in d["criteria"]
        if c["id"] == "factual_plan_accuracy"
    )
    # PARTIAL is reserved for the immaterial slip, FAIL for the rest.
    assert "does not materially alter" in raw["partial"]
    assert "materially distorts" in raw["fail"]


def test_the_rewritten_contoso_criterion_asks_for_no_particular_words(rubric_yaml):
    raw = next(
        c
        for d in rubric_yaml["dimensions"].values()
        for c in d["criteria"]
        if c["id"] == "contoso_state_separated"
    )
    assert "no particular phrasing is required" in raw["pass"]
    assert "through the plan" in raw["pass"]
    assert "fail" in raw, "the rewritten criterion declares its own FAIL band"


def test_earliest_delivery_still_allows_a_faster_valid_plan(rubric_yaml, gt):
    raw = next(
        c
        for d in rubric_yaml["dimensions"].values()
        for c in d["criteria"]
        if c["id"] == "earliest_feasible_delivery"
    )
    assert "demonstrably earlier is equally correct" in raw["pass"]
    assert "accept_between" not in gt["earliest_delivery"]["sso"]


# --------------------------------------------------------------------------
# Factual anchors
# --------------------------------------------------------------------------


def test_every_anchor_deadline_matches_the_work_item_table(gt, work_items):
    for item, text in gt["factual_anchors"]["external_deadlines"].items():
        stated = work_items[item]["external_deadline"]
        assert stated, item
        date, clock = stated[:10], stated[11:16]
        assert date in text and clock in text, f"{item}: anchor {text!r} vs table {stated}"


def test_every_anchor_duration_matches_the_work_item_table(gt, work_items):
    for item, hours in gt["factual_anchors"]["durations_hours"].items():
        if item not in work_items:
            assert hours == 0.5, item  # the two knowledge transfers
            continue
        assert float(work_items[item]["duration_hours"]) == hours, item


def test_every_anchor_owner_matches_the_work_item_table(gt, work_items):
    for item, text in gt["factual_anchors"]["owners"].items():
        assert work_items[item]["owner"] in text, item


def test_the_thursday_anchor_is_recorded_because_a_model_got_it_wrong(gt, work_items):
    """The v0.2 slip this criterion exists for."""
    anchor = gt["factual_anchors"]["external_deadlines"]["billing_schema_migration"]
    assert "THURSDAY" in anchor
    assert work_items["billing_schema_migration"]["external_deadline"].startswith("2026-09-24")


def test_the_anchors_declare_their_scope_boundary():
    """Without it the criterion charges dependency and state errors twice."""
    text = (D / "ground-truth.yaml").read_text(encoding="utf-8")
    assert "wrong RELATIONSHIP" in text and "wrong STATE" in text
    assert "Rounding the present moment is not a substitution" in text


def test_the_marcus_availability_anchor_matches_the_calendar(gt, availability):
    anchor = gt["factual_anchors"]["availability"]["marcus"]
    tuesday = next(
        a for a in availability if a["person"] == "Marcus" and a["date"] == "2026-09-22"
    )
    assert tuesday["available_from"] == "13:00"
    assert "13:00-17:30" in anchor and "09:00-13:00" in anchor


# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# The official battery
# --------------------------------------------------------------------------
#
# Complete and published: seven models, three qualifying runs each.
#
# qwen3.8-flash needed seven attempts to get three. Runs 003 to 006 came back
# with zero reasoning tokens and a changed input-token count for a byte-
# identical prompt at an identical configuration fingerprint, and the guard
# refused all four; run 007 was served on the reasoning path again and
# qualified. The refused attempts are kept, never evaluated, and never reach a
# statistic - which is what the tests below check, alongside recomputing every
# published mean from the evaluations on disk.

MODELS = [
    "deepseek-v4-flash",
    "gemma4",
    "glm5.2",
    "glm5.3-flash",
    "mimo-v2.5",
    "qwen3.6",
    "qwen3.8-flash",
]

OFFICIAL_RUNS = 3
INCOMPLETE = "qwen3.8-flash"


@pytest.fixture(scope="module")
def evaluations():
    base = REPO_ROOT / "evaluations" / EVALUATOR / "monday-003"
    out = {}
    for slug in MODELS:
        paths = sorted((base / slug).glob("run-*.json"))
        assert paths, f"no evaluation for {slug}"
        out[slug] = {p.name: json.loads(p.read_text(encoding="utf-8")) for p in paths}
    return out


@pytest.fixture(scope="module")
def qualified_runs():
    """Every stored run, with the qualification verdict the harness gives it."""
    from mondaybench.config import load_models
    from mondaybench.official import qualify_run
    from mondaybench.runner import load_run

    models = load_models()
    out = {}
    for slug in MODELS:
        rows = []
        for path in sorted((REPO_ROOT / "runs" / "monday-003" / slug).glob("run-*.json")):
            run = load_run(path)
            verdict = qualify_run(
                run,
                path=path,
                expected_prompt_sha256=PROMPT_SHA256,
                model=models[slug],
                scenario_id="monday-003",
            )
            rows.append((path.name, run, verdict))
        out[slug] = rows
    return out


def test_every_model_has_its_three_official_runs(qualified_runs):
    for slug, rows in qualified_runs.items():
        official = [name for name, _, v in rows if v.official]
        assert len(official) == OFFICIAL_RUNS, f"{slug}: {official}"


def test_the_rejected_attempts_are_all_one_model_and_one_defect(qualified_runs):
    """Four refusals, all qwen3.8-flash, all the same provider defect.

    Kept because a serving defect that gets deleted cannot be counted later, and
    because the model's serving qualification rate is a fact about the battery.
    """
    from mondaybench.official import reasoning_status

    rejected = {
        slug: [name for name, _, v in rows if not v.official]
        for slug, rows in qualified_runs.items()
    }
    assert {s: n for s, n in rejected.items() if n} == {
        INCOMPLETE: ["run-003.json", "run-004.json", "run-005.json", "run-006.json"]
    }
    for name, run, verdict in qualified_runs[INCOMPLETE]:
        if not verdict.official:
            assert reasoning_status(run) == "NOT_DELIVERED", name
            assert run.usage.reasoning_tokens == 0, name

    note = REPO_ROOT / "runs" / "monday-003" / INCOMPLETE / "REJECTED-ATTEMPTS.md"
    assert note.is_file(), "a rejected attempt must be documented, not just kept"
    assert "REASONING_NOT_DELIVERED" in note.read_text(encoding="utf-8")


def test_the_rejected_attempts_were_served_differently(qualified_runs):
    """The evidence that this is a serving path and not a shorter answer.

    The prompt is frozen and the generation config fingerprint is identical
    across all seven attempts. An input-token count that moves anyway means the
    request was tokenised by something else.
    """
    rows = qualified_runs[INCOMPLETE]
    good = {run.usage.input_tokens for _, run, v in rows if v.official}
    bad = {run.usage.input_tokens for _, run, v in rows if not v.official}
    assert len(good) == 1 and len(bad) == 1
    assert good != bad, "the rejected runs tokenised the same as the good ones"

    fingerprints = {run.generation.config_sha256 for _, run, _ in rows}
    assert len(fingerprints) == 1, "we did not send a different configuration"
    for _, run, _ in rows:
        assert run.scenario_prompt_sha256 == PROMPT_SHA256


def test_no_rejected_attempt_was_ever_evaluated(evaluations, qualified_runs):
    """A refused run must not reach a score by any route."""
    for slug, rows in qualified_runs.items():
        rejected = {name for name, _, v in rows if not v.official}
        assert rejected & set(evaluations[slug]) == set(), slug


def test_no_two_runs_of_a_model_are_the_same_response(qualified_runs):
    """A cache hit would deflate run_range to zero and look like stability."""
    for slug, rows in qualified_runs.items():
        texts = [run.response for _, run, v in rows if v.official]
        assert len(set(texts)) == len(texts), slug


def test_every_run_was_generated_against_the_frozen_prompt(qualified_runs):
    for slug, rows in qualified_runs.items():
        for name, run, _ in rows:
            assert run.scenario_prompt_sha256 == PROMPT_SHA256, f"{slug}/{name}"


def test_every_model_used_one_generation_config_throughout(qualified_runs):
    for slug, rows in qualified_runs.items():
        fingerprints = {run.generation.config_sha256 for _, run, _ in rows}
        assert len(fingerprints) == 1, f"{slug}: {fingerprints}"


def test_every_scored_run_delivered_reasoning_if_it_was_asked_for(qualified_runs):
    from mondaybench.official import reasoning_status

    for slug, rows in qualified_runs.items():
        for name, run, verdict in rows:
            if verdict.official:
                assert reasoning_status(run) != "NOT_DELIVERED", f"{slug}/{name}"


def test_rejected_attempts_are_preserved_not_deleted():
    """A serving defect that is deleted cannot be counted later."""
    for slug in MODELS:
        failed = REPO_ROOT / "runs" / "monday-003" / slug / "failed-attempts.jsonl"
        if failed.exists():
            assert failed.read_text(encoding="utf-8").strip(), slug


def test_every_qualifying_run_has_exactly_one_evaluation(evaluations, qualified_runs):
    for slug, rows in qualified_runs.items():
        official = {name for name, _, v in rows if v.official}
        assert set(evaluations[slug]) == official, slug


def test_every_evaluation_is_against_the_frozen_prompt_and_rubric(scenario, evaluations):
    assert build_prompt(scenario).sha256 == PROMPT_SHA256
    for slug, runs in evaluations.items():
        for name, e in runs.items():
            assert e["scenario_prompt_sha256"] == PROMPT_SHA256, f"{slug}/{name}"
            assert e["rubric_version"] == "0.3", f"{slug}/{name}"
            assert e["evaluator_id"] == EVALUATOR, f"{slug}/{name}"
            assert e["benchmark_version"] == "0.3", f"{slug}/{name}"


def test_every_evaluation_labels_every_criterion(scenario, evaluations):
    ids = {c.id for c in scenario.rubric.criteria}
    for slug, runs in evaluations.items():
        for name, e in runs.items():
            assert set(e["criteria"]) == ids, f"{slug}/{name}"


def test_one_judge_fingerprint_across_the_whole_battery(evaluations):
    """A ranking that blends judge prompt versions across models is not a ranking."""
    prints = {
        e["judge"]["prompt_fingerprint"] for runs in evaluations.values() for e in runs.values()
    }
    assert len(prints) == 1, prints


def test_the_verdict_files_cover_every_scored_run(scenario, evaluations):
    ids = {c.id for c in scenario.rubric.criteria}
    for slug in MODELS:
        path = REPO_ROOT / "verdicts" / "monday-003" / f"{slug}.verdicts.jsonl"
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        by_run: dict[str, set] = {}
        for row in rows:
            if "criterion_id" in row:
                by_run.setdefault(row["run_id"], set()).add(row["criterion_id"])
        expected = {
            f"monday-003__{slug}__{name.removeprefix('run-').removesuffix('.json')}"
            for name in evaluations[slug]
        }
        assert set(by_run) == expected, slug
        for run_id, labelled in by_run.items():
            assert labelled == ids, run_id
        assert sum(1 for r in rows if r.get("kind") == "penalties") == len(expected), slug


def test_the_official_verdicts_share_no_criterion_with_the_v0_1_verdicts():
    def criteria(directory):
        out = set()
        for path in directory.glob("*.verdicts.jsonl"):
            for line in path.read_text(encoding="utf-8").splitlines():
                row = json.loads(line)
                if "criterion_id" in row:
                    out.add(row["criterion_id"])
        return out

    new = criteria(REPO_ROOT / "verdicts" / "monday-003")
    old = criteria(ARCHIVE_V01 / "verdicts")
    assert new and old
    assert new & old == set()


def test_the_battery_discriminates(evaluations):
    import statistics

    means = {
        slug: statistics.fmean(e["final_score"] for e in runs.values())
        for slug, runs in evaluations.items()
    }
    assert max(means.values()) - min(means.values()) >= 25, sorted(means.items())


def test_penalties_use_only_the_shared_types(evaluations):
    allowed = {
        "MATERIAL_HALLUCINATION",
        "PROHIBITED_ACTION",
        "MAJOR_PLANNING_ERROR",
        "MAJOR_CONTRADICTION",
    }
    for slug, runs in evaluations.items():
        for name, e in runs.items():
            types = {i["type"] for i in e["penalties"].get("items", [])}
            assert types <= allowed, f"{slug}/{name}"


# --------------------------------------------------------------------------
# The published leaderboard
# --------------------------------------------------------------------------


@pytest.fixture(scope="module")
def published():
    path = REPO_ROOT / "leaderboard" / "monday-003" / "leaderboard.json"
    assert path.is_file(), "monday-003 has not been published"
    return json.loads(path.read_text(encoding="utf-8"))


def test_the_published_leaderboard_declares_itself_official(published):
    assert published["official"] is True
    assert published["scenario"] == "monday-003"
    assert published["evaluator"] == EVALUATOR
    assert published["frozen_prompt_sha256"] == PROMPT_SHA256
    assert published["rubric_version"] == "0.3"
    assert published["benchmark_version"] == "0.3"
    assert published["integrity_warning"] is None
    assert len(published["models"]) == len(MODELS)


def test_every_published_model_has_three_runs_and_no_exclusions(published):
    for entry in published["models"]:
        assert entry["score"]["runs"] == OFFICIAL_RUNS, entry["model_slug"]
        assert entry["excluded_runs"] == [], entry["model_slug"]
        assert len(entry["run_scores"]) == OFFICIAL_RUNS, entry["model_slug"]


def test_the_published_score_is_the_plain_mean_of_the_stored_runs(published, evaluations):
    """No dropping the worst run, no best-of-N. Recomputed from disk."""
    import statistics

    for entry in published["models"]:
        stored = sorted(e["final_score"] for e in evaluations[entry["model_slug"]].values())
        assert sorted(entry["run_scores"]) == stored, entry["model_slug"]
        assert entry["score"]["mean"] == pytest.approx(
            round(statistics.fmean(stored), 2)
        ), entry["model_slug"]
        assert entry["score"]["min"] == min(stored)
        assert entry["score"]["max"] == max(stored)
        assert entry["score"]["range"] == pytest.approx(round(max(stored) - min(stored), 2))


def test_no_rejected_run_reached_the_published_statistics(published, qualified_runs):
    rejected_scores_possible = {
        f"monday-003__{slug}__{name.removeprefix('run-').removesuffix('.json')}"
        for slug, rows in qualified_runs.items()
        for name, _, v in rows
        if not v.official
    }
    assert rejected_scores_possible, "this test is pointless if nothing was rejected"
    for entry in published["models"]:
        assert len(entry["run_scores"]) == OFFICIAL_RUNS


def test_the_published_ranking_is_ordered_by_score(published):
    means = [e["score"]["mean"] for e in published["models"]]
    assert means == sorted(means, reverse=True)
    assert [e["rank"] for e in published["models"]] == list(range(1, len(means) + 1))


def test_the_other_published_leaderboards_are_untouched():
    """monday-001 owns leaderboard/ itself; monday-002 owns its subdirectory."""
    shared = json.loads(
        (REPO_ROOT / "leaderboard" / "leaderboard.json").read_text(encoding="utf-8")
    )
    assert shared["scenario"] == "monday-001" and shared["official"] is True
    second = json.loads(
        (REPO_ROOT / "leaderboard" / "monday-002" / "leaderboard.json").read_text(encoding="utf-8")
    )
    assert second["scenario"] == "monday-002" and second["official"] is True


def test_the_calibration_report_states_one_recommendation():
    report = (REPO_ROOT / "analysis" / "monday-003-calibration-v0.3.md").read_text(
        encoding="utf-8"
    )
    freeze = "RECOMMENDATION: FREEZE MONDAY-003 v0.3" in report
    revise = "RECOMMENDATION: REVISE BEFORE FREEZE" in report
    assert freeze != revise, "the report must land on exactly one recommendation"


# --------------------------------------------------------------------------
# Integrity: three calibration generations, none of them mutated
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "archive,evaluator,runs_expected",
    [
        (ARCHIVE_V01, "evaluator-opus5-v0.3-calibration", 9),
        (ARCHIVE_V02, "evaluator-opus5-v0.3-calibration-2", 7),
        (ARCHIVE_V03C, "evaluator-opus5-v0.3-calibration-3", 14),
    ],
)
def test_each_archived_calibration_is_preserved_whole(archive, evaluator, runs_expected):
    for name in (
        "README.md",
        "RENDERED_PROMPT_SHA256.txt",
        "calibration-report.md",
        f"{evaluator}.yaml",
        "scenario/rubric.yaml",
        "scenario/scenario.yaml",
        "verdicts/_generate.py",
    ):
        assert (archive / name).is_file(), f"{archive.name}/{name}"
    assert len(sorted((archive / "runs-monday-003").glob("*/run-*.json"))) == runs_expected
    assert (
        len(sorted((archive / f"evaluations-{evaluator}").glob("*/run-*.json")))
        == runs_expected
        if archive is ARCHIVE_V03C
        else 7
    )
    assert len(sorted((archive / "verdicts").glob("*.verdicts.jsonl"))) == 7


def test_the_archived_rubrics_are_the_versions_they_claim():
    for archive, version in (
        (ARCHIVE_V01, "0.1"),
        (ARCHIVE_V02, "0.2"),
        (ARCHIVE_V03C, "0.3"),
    ):
        rubric = yaml.safe_load(
            (archive / "scenario" / "rubric.yaml").read_text(encoding="utf-8")
        )
        assert rubric["rubric_version"] == version, archive.name
        stored = yaml.safe_load(
            (archive / "scenario" / "scenario.yaml").read_text(encoding="utf-8")
        )
        assert stored["scenario_version"] == version, archive.name
        # every archived scenario is a draft; only the live one is official
        assert stored["status"] == "calibration", archive.name


def test_only_the_official_evaluator_lives_in_the_live_tree():
    live = sorted(p.name for p in (REPO_ROOT / "evaluators").glob("evaluator-opus5-v0.3*.yaml"))
    assert live == [f"{EVALUATOR}.yaml"]
    declared = yaml.safe_load(
        (REPO_ROOT / "evaluators" / f"{EVALUATOR}.yaml").read_text(encoding="utf-8")
    )
    assert declared["status"] == "official"
    assert "calibration" not in EVALUATOR
    assert (ARCHIVE_V01 / "evaluator-opus5-v0.3-calibration.yaml").is_file()
    assert (ARCHIVE_V02 / "evaluator-opus5-v0.3-calibration-2.yaml").is_file()
    assert (ARCHIVE_V03C / "evaluator-opus5-v0.3-calibration-3.yaml").is_file()


def test_only_the_current_evaluator_has_live_evaluations_for_this_scenario():
    """A superseded evaluator directory is a stale ranking waiting to be built."""
    live = sorted(
        d.name
        for d in (REPO_ROOT / "evaluations").iterdir()
        if d.is_dir() and (d / "monday-003").exists()
    )
    assert live == [EVALUATOR]


def test_all_three_calibration_reports_are_on_disk():
    for name in (
        "monday-003-calibration-v0.1.md",
        "monday-003-calibration-v0.2.md",
        "monday-003-calibration-v0.3.md",
    ):
        assert (REPO_ROOT / "analysis" / name).is_file(), name
