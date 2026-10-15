"""Suite v1.10 adds three closed models to the board and moves nothing else.

Claude Opus 5, Claude Fable 5.1 and Gemini 3.8 Flash (High) were published as
provisional rows at 97.07, 94.90 and 86.00. Overall v3.5 makes them official
board rows, from the same responses and the same labels. These checks pin the
two halves of that claim: the three numbers are the published ones, recomputed
here from the stored evaluations rather than read off the board, and every one
of the ten incumbents in Overall v3.4 is carried into v3.5 unchanged.
"""
from __future__ import annotations

import json
import statistics

import pytest

from mondaybench.config import load_models, repo_root
from mondaybench.evaluator import find_evaluations, load_evaluation

SUITE = "1.10"
EVALUATORS = {
    "monday-001": "evaluator-opus5-v0.1",
    "monday-002": "evaluator-opus5-v0.2",
    "monday-003": "evaluator-opus5-v0.3",
    "monday-004": "evaluator-opus5-v0.4",
    "monday-005": "evaluator-opus5-v0.5",
}
NEW = {
    "claude-opus-5": 97.07,
    "claude-fable-5-1": 94.90,
    "gemini-3-8-flash-high": 86.00,
}


def overall(version: str) -> dict:
    path = repo_root() / "leaderboard" / "overall" / f"overall-v{version}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def rows(version: str) -> dict[str, dict]:
    return {row["model_slug"]: row for row in overall(version)["models"]}


@pytest.mark.parametrize("slug", sorted(NEW))
def test_the_monday_score_recomputes_from_the_stored_evaluations(slug: str) -> None:
    means = []
    for scenario_id, evaluator_id in EVALUATORS.items():
        paths = find_evaluations(evaluator_id, scenario_id, slug, None, SUITE)
        assert len(paths) == 3, (slug, scenario_id, len(paths))
        means.append(statistics.mean(load_evaluation(p).final_score for p in paths))
    assert round(statistics.mean(means), 2) == NEW[slug]


@pytest.mark.parametrize("slug", sorted(NEW))
def test_the_board_publishes_the_published_score(slug: str) -> None:
    assert rows("3.5")[slug]["monday_score"] == NEW[slug]


def test_v3_5_is_the_v3_4_board_plus_exactly_the_three() -> None:
    before, after = rows("3.4"), rows("3.5")
    assert len(before) == 10 and len(after) == 13
    assert set(after) - set(before) == set(NEW)
    assert overall("3.5")["suite_version"] == SUITE
    assert overall("3.5")["incomplete_models"] == []


def test_no_incumbent_moved() -> None:
    before, after = rows("3.4"), rows("3.5")
    for slug, row in before.items():
        assert after[slug]["monday_score"] == row["monday_score"], slug
        assert after[slug]["scenario_scores"] == row["scenario_scores"], slug
        assert after[slug]["run_stability"] == row["run_stability"], slug


@pytest.mark.parametrize("slug", sorted(NEW))
def test_what_the_route_did_not_expose_stays_null(slug: str) -> None:
    """The Astra rule: never a number where the route exposed none."""
    model = load_models()[slug]
    assert model.temperature is None and model.max_output_tokens is None
    assert model.base_url_env is None, "these routes cannot be driven by `mondaybench run`"
    for scenario_id in EVALUATORS:
        for path in sorted((repo_root() / "runs" / scenario_id / slug).glob("run-*.json")):
            run = json.loads(path.read_text(encoding="utf-8"))
            generation = run["generation"]
            assert generation["temperature"] is None, path
            assert generation["top_p"] is None, path
            assert generation["max_output_tokens"] is None, path
            assert run["provider_metadata"]["request_id"] is None, path
            assert run["performance"] == {
                "ttft_ms": None, "ttfa_ms": None,
                "total_latency_ms": None, "tokens_per_second": None,
            }, path
