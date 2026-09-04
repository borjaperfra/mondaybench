"""Release-level gates for suite v1.1 (tests R, S, T of the migration plan).

These assert that two releases coexist without either disturbing the other, and
that the thing v1.1 exists to make possible - an eighth model on a frozen suite
- actually happens.
"""

from __future__ import annotations

import json

import pytest

from mondaybench.config import repo_root
from mondaybench.evaluator import (
    evaluations_root,
    find_evaluations,
    load_evaluation,
    models_with_evaluations,
)
from mondaybench.leaderboard import leaderboard_dir
from mondaybench.suite import load_suite_manifest, verify_suite

SCENARIOS = ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"]
EVALUATORS = {
    "monday-001": "evaluator-opus5-v0.1",
    "monday-002": "evaluator-opus5-v0.2",
    "monday-003": "evaluator-opus5-v0.3",
    "monday-004": "evaluator-opus5-v0.4",
    "monday-005": "evaluator-opus5-v0.5",
}
OFFICIAL = {
    "glm5.3-flash", "glm5.2", "mimo-v2.5", "deepseek-v4-flash",
    "qwen3.8-flash", "qwen3.6", "gemma4", "glm5.3",
}
# Reachable only through a route that is not the official provider route.
PROVISIONAL = {"claude-opus-5", "claude-fable-5-1"}


# ---------------------------------------------------------------------------
# R - both releases verify against the same tree
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("version", ["1.0", "1.1"])
def test_R_a_release_verifies_under_its_own_policy(version):
    manifest = load_suite_manifest(version)
    assert manifest is not None, f"no manifest for suite v{version}"
    drift = verify_suite(version)
    failing = {name: report.summary() for name, report in drift.items() if not report.ok}
    assert not failing, f"v{version} does not verify: {failing}"


def test_R_the_two_releases_are_distinct_claims():
    v10 = load_suite_manifest("1.0")
    v11 = load_suite_manifest("1.1")
    assert v10["suite_digest"] != v11["suite_digest"]
    # ...over the same five questions, which is what makes them comparable at all
    assert [s["prompt_sha256"] for s in v10["scenarios"]] == [
        s["prompt_sha256"] for s in v11["scenarios"]
    ]


# ---------------------------------------------------------------------------
# S - v1.1 never writes into v1.0's locations
# ---------------------------------------------------------------------------


def test_S_versioned_paths_are_disjoint_from_the_legacy_ones():
    for scenario_id in SCENARIOS:
        legacy = leaderboard_dir(scenario_id)
        versioned = leaderboard_dir(scenario_id, suite_version="1.1")
        assert legacy != versioned
        assert "v1.1" in versioned.parts
        assert "v1.1" not in legacy.parts
    assert evaluations_root() != evaluations_root(None, "1.1")
    assert evaluations_root(None, "1.0") == evaluations_root()


def test_S_the_v1_0_boards_carry_no_v1_1_model():
    """The proof that publishing v1.1 did not touch what v1.0 published."""
    for scenario_id in SCENARIOS:
        path = leaderboard_dir(scenario_id) / "leaderboard.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        slugs = {row["model_slug"] for row in payload["models"]}
        assert "glm5.3" not in slugs, f"{scenario_id}: v1.0 board was modified"
        assert len(slugs) == 7


def test_S_v1_0_evaluations_were_not_restamped():
    for scenario_id, evaluator_id in EVALUATORS.items():
        for slug in models_with_evaluations(evaluator_id, scenario_id):
            for path in find_evaluations(evaluator_id, scenario_id, slug):
                evaluation = load_evaluation(path)
                assert evaluation.suite_version is None, path
                assert evaluation.judge.contract_fingerprint is None, path


# ---------------------------------------------------------------------------
# T - an eighth model gets in
# ---------------------------------------------------------------------------


def test_T_an_eighth_official_model_is_on_every_v1_1_board():
    for scenario_id in SCENARIOS:
        payload = json.loads(
            (leaderboard_dir(scenario_id, suite_version="1.1") / "leaderboard.json")
            .read_text(encoding="utf-8")
        )
        assert payload["official"] is True
        assert payload.get("integrity_warning") is None, payload.get("integrity_warning")
        slugs = {row["model_slug"] for row in payload["models"]}
        assert slugs == OFFICIAL, f"{scenario_id}: {slugs ^ OFFICIAL}"


def test_T_the_gate_that_blocked_the_eighth_model_is_gone():
    """No v1.1 board may carry a MIXED JUDGE VERSIONS warning."""
    for scenario_id in SCENARIOS:
        payload = json.loads(
            (leaderboard_dir(scenario_id, suite_version="1.1") / "leaderboard.json")
            .read_text(encoding="utf-8")
        )
        assert "MIXED JUDGE VERSIONS" not in json.dumps(payload)


# ---------------------------------------------------------------------------
# Score invariance - the hard migration gate
# ---------------------------------------------------------------------------


def _scores(evaluator_id, scenario_id, slug, suite_version=None):
    return [
        load_evaluation(p).final_score
        for p in find_evaluations(evaluator_id, scenario_id, slug, None, suite_version)
    ]


@pytest.mark.parametrize("slug", sorted(OFFICIAL - {"glm5.3"}))
def test_every_incumbent_run_score_is_identical_in_v1_1(slug):
    for scenario_id, evaluator_id in EVALUATORS.items():
        assert _scores(evaluator_id, scenario_id, slug) == _scores(
            evaluator_id, scenario_id, slug, "1.1"
        ), f"{slug}/{scenario_id}"


@pytest.mark.parametrize("slug", sorted(OFFICIAL - {"glm5.3"}))
def test_every_incumbent_judgment_is_identical_in_v1_1(slug):
    for scenario_id, evaluator_id in EVALUATORS.items():
        old = {p.name: load_evaluation(p) for p in find_evaluations(evaluator_id, scenario_id, slug)}
        new = {
            p.name: load_evaluation(p)
            for p in find_evaluations(evaluator_id, scenario_id, slug, None, "1.1")
        }
        assert set(old) == set(new)
        for name, before in old.items():
            after = new[name]
            assert {c: r.result for c, r in before.criteria.items()} == {
                c: r.result for c, r in after.criteria.items()
            }, f"{slug}/{scenario_id}/{name}: a criterion label moved"
            assert {a: r.triggered for a, r in before.false_actions.items()} == {
                a: r.triggered for a, r in after.false_actions.items()
            }, f"{slug}/{scenario_id}/{name}: a false-action judgment moved"
            assert before.penalties.total == after.penalties.total
            assert before.base_score == after.base_score
            assert before.final_score == after.final_score


def test_the_overall_boards_agree_on_every_incumbent():
    v2 = json.loads(
        (repo_root() / "leaderboard" / "overall" / "overall-v2.json").read_text(encoding="utf-8")
    )
    v3 = json.loads(
        (repo_root() / "leaderboard" / "overall" / "overall-v3.json").read_text(encoding="utf-8")
    )
    old = {m["model_slug"]: m["monday_score"] for m in v2["models"]}
    new = {m["model_slug"]: m["monday_score"] for m in v3["models"]}
    for slug, score in old.items():
        assert new[slug] == score, f"{slug}: {score} -> {new[slug]}"
    assert set(new) - set(old) == {"glm5.3"}


# ---------------------------------------------------------------------------
# Scope
# ---------------------------------------------------------------------------


def test_provisional_models_stay_out_of_the_official_v1_1_boards():
    """Evaluation comparability must not override generation-route eligibility."""
    for scenario_id in SCENARIOS:
        payload = json.loads(
            (leaderboard_dir(scenario_id, suite_version="1.1") / "leaderboard.json")
            .read_text(encoding="utf-8")
        )
        slugs = {row["model_slug"] for row in payload["models"]}
        assert not (slugs & PROVISIONAL), f"{scenario_id} carries a provisional model"


def test_the_migration_reused_every_generation():
    """No candidate output was regenerated: each v1.1 evaluation points at an
    existing run file, and each names the v1.0 evaluation it re-stamps."""
    from mondaybench.runner import run_path

    for scenario_id, evaluator_id in EVALUATORS.items():
        for slug in models_with_evaluations(evaluator_id, scenario_id, None, "1.1"):
            for path in find_evaluations(evaluator_id, scenario_id, slug, None, "1.1"):
                evaluation = load_evaluation(path)
                assert evaluation.suite_version == "1.1"
                assert evaluation.migrated_from, path
                assert (repo_root() / evaluation.migrated_from).is_file()
                number = int(path.stem.split("-")[1])
                assert run_path(scenario_id, slug, number).is_file()
                # A re-stamp is recorded, never re-judged.
                assert evaluation.judge.route == "recorded"
                # And session identity is never invented for a migrated record.
                assert evaluation.judge.judge_session_id is None
