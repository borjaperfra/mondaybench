"""The leaderboard renderer must not know any scenario's dimensions.

monday-002 shipped with its markdown and CSV showing monday-001's six
dimensions - `Action detection`, `Noise resistance` and the rest - because both
renderers held a module-level list of names. Every dimension monday-002 actually
scores was absent, and every one it does not scored a silent `0`.

These tests exist so that a third scenario with a seventh dimension publishes
correctly without anyone editing `leaderboard.py`.
"""

from __future__ import annotations

import csv
import inspect
from pathlib import Path

import pytest
import yaml

from mondaybench import leaderboard as lb
from mondaybench.leaderboard import (
    ModelSummary,
    dimension_columns,
    dimension_label,
    render_markdown,
    rubric_dimension_order,
)

REPO_ROOT = Path(__file__).resolve().parent.parent

# The two published scenarios and the rubric each is scored against.
SCENARIOS = {
    "monday-001": ("evaluator-opus5-v0.1", "rubric-0.2.yaml", Path("leaderboard")),
    "monday-002": ("evaluator-opus5-v0.2", "rubric.yaml", Path("leaderboard/monday-002")),
}


def rubric_dimensions(scenario_id: str) -> dict[str, float]:
    """Dimension name -> max_points, straight out of the rubric YAML."""
    _, rubric_file, _ = SCENARIOS[scenario_id]
    raw = yaml.safe_load(
        (REPO_ROOT / "scenarios" / scenario_id / rubric_file).read_text(encoding="utf-8")
    )
    return {name: float(body["max_points"]) for name, body in raw["dimensions"].items()}


def _summary(dimensions: dict[str, float], maxima: dict[str, float], order=None):
    return ModelSummary(
        model_slug="m",
        display_name="M",
        runs=3,
        mean=50.0,
        minimum=50.0,
        maximum=50.0,
        stddev=0.0,
        dimensions=dimensions,
        dimension_max=maxima,
        median_ttfa_ms=None,
        median_total_latency_ms=None,
        median_cost_usd=None,
        median_ttft_ms=None,
        median_output_tokens=None,
        prompt_sha256="e" * 64,
        dimension_order=list(order or []),
        run_scores=[50.0, 50.0, 50.0],
        rubric_version="0.2",
        judge_model_id="claude-opus-5",
        rank=1,
    )


# --------------------------------------------------------------------------
# No global list of dimension names may exist
# --------------------------------------------------------------------------


def test_the_module_holds_no_hardcoded_dimension_list():
    """The two names that caused the bug must not come back."""
    assert not hasattr(lb, "CSV_DIMENSIONS")
    assert not hasattr(lb, "DIMENSION_LABELS")


def test_no_scenario_dimension_name_is_written_into_the_renderer():
    source = inspect.getsource(lb)
    every_name = set(rubric_dimensions("monday-001")) | set(rubric_dimensions("monday-002"))
    baked_in = sorted(n for n in every_name if n in source)
    assert baked_in == [], f"renderer hardcodes dimension names: {baked_in}"


# --------------------------------------------------------------------------
# Each scenario publishes its own dimensions, with its own maxima
# --------------------------------------------------------------------------


@pytest.mark.parametrize("scenario_id", sorted(SCENARIOS))
def test_published_markdown_shows_exactly_the_rubric_dimensions(scenario_id):
    _, _, out_dir = SCENARIOS[scenario_id]
    text = (REPO_ROOT / out_dir / "leaderboard.md").read_text(encoding="utf-8")
    expected = rubric_dimensions(scenario_id)

    for name, maximum in expected.items():
        row = f"| {dimension_label(name)} |"
        assert row in text, f"{scenario_id}: {name} missing from the published markdown"
        # ...and its max column is the rubric's, not a number from elsewhere.
        line = next(l for l in text.splitlines() if l.startswith(row))
        assert line.rstrip().endswith(f"| {maximum:g} |"), line

    # No other scenario's dimensions may appear.
    for other in SCENARIOS:
        if other == scenario_id:
            continue
        for name in rubric_dimensions(other):
            if name in expected:
                continue
            assert f"| {dimension_label(name)} |" not in text, (
                f"{scenario_id} markdown shows {other}'s {name}"
            )


@pytest.mark.parametrize("scenario_id", sorted(SCENARIOS))
def test_published_csv_columns_are_exactly_the_rubric_dimensions(scenario_id):
    _, _, out_dir = SCENARIOS[scenario_id]
    with (REPO_ROOT / out_dir / "leaderboard.csv").open(encoding="utf-8", newline="") as fh:
        header = next(csv.reader(fh))
    expected = set(rubric_dimensions(scenario_id))
    assert expected <= set(header), f"{scenario_id}: missing {expected - set(header)}"

    foreign = set()
    for other in SCENARIOS:
        if other != scenario_id:
            foreign |= set(rubric_dimensions(other)) - expected
    assert not (foreign & set(header)), f"{scenario_id} CSV carries {foreign & set(header)}"


def test_monday_001_keeps_its_original_six():
    assert rubric_dimension_order("monday-001", "evaluator-opus5-v0.1") == [
        "action_detection",
        "state_reconstruction",
        "prioritization",
        "data_reasoning",
        "uncertainty",
        "noise_resistance",
    ]


def test_monday_002_has_its_own_six():
    assert rubric_dimension_order("monday-002", "evaluator-opus5-v0.2") == [
        "state_reconstruction",
        "temporal_supersession",
        "planning_dependencies",
        "decision_prioritization",
        "cross_source_data_reasoning",
        "uncertainty_epistemic",
    ]


def test_the_two_scenarios_do_not_share_a_dimension_set():
    """If they did, this whole test module would prove nothing."""
    assert set(rubric_dimensions("monday-001")) != set(rubric_dimensions("monday-002"))


@pytest.mark.parametrize("scenario_id", sorted(SCENARIOS))
def test_rubric_dimension_maxima_sum_to_one_hundred(scenario_id):
    assert sum(rubric_dimensions(scenario_id).values()) == 100


# --------------------------------------------------------------------------
# A dimension the scenario does not score must not appear as a zero
# --------------------------------------------------------------------------


def test_an_unscored_dimension_is_absent_rather_than_rendered_as_zero():
    """The old renderer printed `| Noise resistance | 0.0 | 10 |` for #002."""
    summary = _summary(
        {"alpha": 12.0, "beta": 8.0},
        {"alpha": 15.0, "beta": 10.0},
        order=["alpha", "beta"],
    )
    text = render_markdown({"official": True, "benchmark_version": "9.9"}, [summary])
    assert "| Alpha | 12.0 | 15 |" in text
    assert "| Beta | 8.0 | 10 |" in text
    assert "noise" not in text.lower()
    # No phantom dimension row. Checked against the dimension table only: the
    # summary table legitimately carries a 0.0 range.
    table = text.split("| Dimension | Score | Max |")[1].split("| **Monday Score**")[0]
    rows = [l for l in table.splitlines() if l.startswith("| ")]
    assert len(rows) == 2, rows  # alpha and beta, and nothing else
    assert "0.0" not in table


def test_dimension_columns_never_invents_a_name():
    summary = _summary({"alpha": 1.0}, {"alpha": 5.0})
    assert dimension_columns([summary]) == ["alpha"]


def test_maxima_come_from_the_summary_not_from_a_constant():
    """Same dimension name, a different rubric weight: the renderer must follow."""
    summary = _summary({"state_reconstruction": 7.0}, {"state_reconstruction": 42.0},
                       order=["state_reconstruction"])
    text = render_markdown({"official": True, "benchmark_version": "9.9"}, [summary])
    assert "| State reconstruction | 7.0 | 42 |" in text
    assert "| 25 |" not in text  # monday-001's weight for this dimension


def test_rubric_order_is_preserved_and_unknown_extras_are_appended():
    summary = _summary(
        {"b": 1.0, "a": 1.0, "z": 1.0},
        {"b": 20.0, "a": 10.0, "z": 30.0},
        order=["b", "a"],          # z is scored but not in the declared order
    )
    assert dimension_columns([summary]) == ["b", "a", "z"]


def test_a_missing_scenario_yields_no_order_rather_than_raising():
    assert rubric_dimension_order("monday-999", "evaluator-opus5-v0.2") == []


# --------------------------------------------------------------------------
# The status line names the scenario's own version
# --------------------------------------------------------------------------


def test_status_line_uses_the_scenario_version():
    summary = _summary({"alpha": 1.0}, {"alpha": 5.0}, order=["alpha"])
    md2 = render_markdown({"official": True, "benchmark_version": "0.2"}, [summary])
    assert "**Status:** official v0.2 result. Every publication gate passed." in md2
    md1 = render_markdown({"official": True, "benchmark_version": "0.1"}, [summary])
    assert "**Status:** official v0.1 result. Every publication gate passed." in md1


def test_status_line_falls_back_when_no_version_is_declared():
    summary = _summary({"alpha": 1.0}, {"alpha": 5.0}, order=["alpha"])
    text = render_markdown({"official": True}, [summary])
    assert "**Status:** official. Every publication gate passed." in text


@pytest.mark.parametrize(
    "scenario_id,expected",
    [("monday-001", "official v0.1 result"), ("monday-002", "official v0.2 result")],
)
def test_published_status_lines_are_right(scenario_id, expected):
    _, _, out_dir = SCENARIOS[scenario_id]
    text = (REPO_ROOT / out_dir / "leaderboard.md").read_text(encoding="utf-8")
    assert f"**Status:** {expected}. Every publication gate passed." in text
