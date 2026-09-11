"""One DeepSeek V4.1 Flash battery reaches the board, and it is the natural rerun.

The gateway served different weights under one model id on different days, so
this model has three batteries on disk: the 2026-09-10 one, a reliability-prompt
variant of it, and the 2026-09-11 natural rerun that supersedes both. Only the
last is a member of suite v1.5.

These assertions exist because the failure they guard against is silent. Nothing
errors if a retired battery is carried into a later suite, or if two batteries
for one model both qualify and the board shows the model twice, or if a treated
arm leaks into the official tree - the numbers simply stop meaning what the page
says they mean. Each check below is one of those ways to be quietly wrong.
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

import pytest

from mondaybench.config import repo_root
from mondaybench.evaluator import evaluations_root, models_with_evaluations

SUITE = "1.5"
CANONICAL = "deepseek-v4.1-flash-rerun-v1"
RETIRED = ("deepseek-v4.1-flash", "deepseek-v4.1-flash-reliability-v1")
EXPERIMENTAL = ("deepseek-v4.1-flash-rerun-guardrail-v1", "deepseek-v4.1-flash-probe",
                "deepseek-v4.1-flash-max", "deepseek-v4.1-flash-high")
EVALUATORS = {
    "monday-001": "evaluator-opus5-v0.1",
    "monday-002": "evaluator-opus5-v0.2",
    "monday-003": "evaluator-opus5-v0.3",
    "monday-004": "evaluator-opus5-v0.4",
    "monday-005": "evaluator-opus5-v0.5",
}
FROZEN_MEANS = {
    "monday-001": 95.00, "monday-002": 93.00, "monday-003": 96.33,
    "monday-004": 90.00, "monday-005": 98.33,
}
FROZEN_RUNS = {
    "monday-001": [91.0, 97.0, 97.0],
    "monday-002": [89.5, 100.0, 89.5],
    "monday-003": [95.5, 95.5, 98.0],
    "monday-004": [89.5, 90.0, 90.5],
    "monday-005": [98.5, 97.5, 99.0],
}


def board(scenario_id: str) -> dict:
    path = repo_root() / "leaderboard" / f"v{SUITE}" / scenario_id / "leaderboard.json"
    return json.loads(path.read_text(encoding="utf-8"))


def overall() -> dict:
    path = repo_root() / "leaderboard" / "overall" / "overall-v3.4.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("scenario_id", sorted(EVALUATORS))
def test_one_deepseek_v41_row_per_scenario_board(scenario_id: str) -> None:
    rows = [m for m in board(scenario_id)["models"] if "DeepSeek V4.1" in m["display_name"]]
    assert len(rows) == 1, [m["display_name"] for m in rows]
    assert rows[0]["model_slug"] == CANONICAL


@pytest.mark.parametrize("scenario_id", sorted(EVALUATORS))
def test_retired_and_experimental_batteries_are_not_in_the_suite(scenario_id: str) -> None:
    slugs = set(models_with_evaluations(EVALUATORS[scenario_id], scenario_id,
                                        None, SUITE))
    assert not slugs & set(RETIRED), slugs & set(RETIRED)
    assert not slugs & set(EXPERIMENTAL), slugs & set(EXPERIMENTAL)


@pytest.mark.parametrize("scenario_id", sorted(EVALUATORS))
def test_exactly_three_official_runs(scenario_id: str) -> None:
    base = evaluations_root(None, SUITE) / EVALUATORS[scenario_id] / scenario_id / CANONICAL
    assert sorted(p.name for p in base.glob("run-*.json")) == [
        "run-001.json", "run-002.json", "run-003.json"]


@pytest.mark.parametrize("scenario_id", sorted(EVALUATORS))
def test_run_scores_are_the_frozen_ones(scenario_id: str) -> None:
    base = evaluations_root(None, SUITE) / EVALUATORS[scenario_id] / scenario_id / CANONICAL
    got = [json.loads((base / f"run-{n:03d}.json").read_text(encoding="utf-8"))["final_score"]
           for n in (1, 2, 3)]
    assert got == FROZEN_RUNS[scenario_id]


@pytest.mark.parametrize("scenario_id", sorted(EVALUATORS))
def test_scenario_mean_is_the_frozen_one(scenario_id: str) -> None:
    row = next(m for m in board(scenario_id)["models"] if m["model_slug"] == CANONICAL)
    assert row["score"]["mean"] == pytest.approx(FROZEN_MEANS[scenario_id], abs=0.005)


def test_monday_score_rebuilds_from_the_boards() -> None:
    means = [next(m for m in board(s)["models"] if m["model_slug"] == CANONICAL)["score"]["mean"]
             for s in EVALUATORS]
    assert round(statistics.fmean(means), 2) == 94.53


def test_overall_carries_one_deepseek_v41_row_at_the_frozen_score() -> None:
    rows = [m for m in overall()["models"] if "DeepSeek V4.1" in m["display_name"]]
    assert len(rows) == 1, [m["display_name"] for m in rows]
    assert rows[0]["monday_score"] == pytest.approx(94.53, abs=0.005)
    assert rows[0]["display_name"] == "DeepSeek V4.1 Flash"


def test_no_verdict_cross_contamination() -> None:
    """Every official verdict names a run of the battery it is filed under."""
    for scenario_id in EVALUATORS:
        path = repo_root() / "verdicts" / scenario_id / f"{CANONICAL}.verdicts.jsonl"
        ids = {json.loads(line)["run_id"]
               for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}
        assert ids == {f"{scenario_id}__{CANONICAL}__{n:03d}" for n in (1, 2, 3)}


def test_experiment_directories_stay_out_of_the_official_trees() -> None:
    """An experiment keeps its own runs, verdicts and evaluations under itself."""
    root = repo_root() / "experiments" / "deepseek-v4.1-flash-rerun-guardrail-v1"
    assert (root / "runs").is_dir()
    for scenario_id, evaluator_id in EVALUATORS.items():
        official = evaluations_root(None, SUITE) / evaluator_id / scenario_id
        assert not (official / "deepseek-v4.1-flash-rerun-guardrail-v1").exists()


def test_retired_evidence_is_preserved() -> None:
    """Retiring a battery removes it from the suite, never from the record."""
    for slug in RETIRED:
        runs = list((repo_root() / "runs").glob(f"monday-*/{slug}/run-*.json"))
        assert len(runs) == 15, (slug, len(runs))
    stale = evaluations_root(None, "1.4") / "evaluator-opus5-v0.1" / "monday-001"
    assert (stale / "deepseek-v4.1-flash").exists()
