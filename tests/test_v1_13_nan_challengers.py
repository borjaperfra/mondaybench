"""Suite v1.13 adds two NaN challengers to the board and moves nothing else.

DeepSeek V4.1 Flash (1017) and MiMo v2.6 Flash were generated on NaN on
2026-10-19 with a per-run seed and judged blind by Claude Opus 5.5
(experiments/nan-challengers-2026-10-19-opus-judge/). These checks pin the two
numbers, recomputed from the stored evaluations rather than read off the board,
that every incumbent of Overall v3.5 is carried into v3.6 unchanged, and that
every official run of both batteries was a seeded, distinct generation.
"""
from __future__ import annotations

import json
import statistics

import pytest

from mondaybench.config import load_models, repo_root
from mondaybench.evaluator import find_evaluations, load_evaluation
from mondaybench.runner import load_run, run_path

SUITE = "1.13"
EVALUATORS = {
    "monday-001": "evaluator-opus5-v0.1",
    "monday-002": "evaluator-opus5-v0.2",
    "monday-003": "evaluator-opus5-v0.3",
    "monday-004": "evaluator-opus5-v0.4",
    "monday-005": "evaluator-opus5-v0.5",
}
NEW = {
    "deepseek-v4.1-flash-1017": 91.23,
    "mimo-v2.6-flash": 87.87,
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
    assert rows("3.6")[slug]["monday_score"] == NEW[slug]


def test_v3_6_is_the_v3_5_board_plus_exactly_the_two() -> None:
    before, after = rows("3.5"), rows("3.6")
    assert len(before) == 13 and len(after) == 15
    assert set(after) - set(before) == set(NEW)
    assert overall("3.6")["suite_version"] == SUITE
    assert overall("3.6")["incomplete_models"] == []


def test_no_incumbent_moved() -> None:
    before, after = rows("3.5"), rows("3.6")
    for slug, row in before.items():
        assert after[slug]["monday_score"] == row["monday_score"], slug
        assert after[slug]["scenario_scores"] == row["scenario_scores"], slug
        assert after[slug]["run_stability"] == row["run_stability"], slug


@pytest.mark.parametrize("slug", sorted(NEW))
def test_every_official_run_is_a_seeded_distinct_generation(slug: str) -> None:
    """NaN ignored `caching: false` on 2026-10-19; the seed is what made each
    run a fresh sample, so a run without one would be a cache-hit risk."""
    assert load_models()[slug].seed_per_run
    for scenario_id, evaluator_id in EVALUATORS.items():
        responses = set()
        for path in find_evaluations(evaluator_id, scenario_id, slug, None, SUITE):
            number = int(path.stem.split("-")[1])
            run = load_run(run_path(scenario_id, slug, number))
            assert run.generation.extra_body.get("seed") == number, (scenario_id, number)
            responses.add(run.response)
        assert len(responses) == 3, (slug, scenario_id)
