"""A ranking that blends judge prompt versions is not a ranking.

This guard exists because a calibration sweep was interrupted midway through a
penalty-prompt change, leaving five evaluations from the old prompt beside two
from the new one under the same `evaluator_id`. Nothing detected it; the
leaderboard would have ranked seven models judged by two different rulebooks.
"""

from __future__ import annotations

import json

import pytest

from mondaybench.evaluator import write_evaluation
from mondaybench.judge import judge_prompt_fingerprint
from mondaybench.leaderboard import build_leaderboard
from mondaybench.schemas import DimensionScore, Evaluation, JudgeRecord, Penalties

EVALUATOR = "evaluator-test"
SCENARIO = "monday-001"


def _evaluation(model_slug: str, fingerprint: str | None, score: float = 90.0) -> Evaluation:
    return Evaluation(
        evaluator_id=EVALUATOR,
        benchmark_version="0.1",
        scenario_id=SCENARIO,
        run_id=f"{SCENARIO}__{model_slug}__001",
        model_slug=model_slug,
        scenario_prompt_sha256="a" * 64,
        timestamp_utc="2026-08-27T00:00:00Z",
        judge=JudgeRecord(
            provider="test",
            model_id="test-judge",
            temperature=None,
            prompt_fingerprint=fingerprint,
        ),
        dimensions={"action_detection": DimensionScore(score=score, max_score=100.0)},
        criteria={},
        false_actions={},
        penalties=Penalties(),
        base_score=score,
        final_score=score,
    )


def _write(evaluation: Evaluation, tmp_path):
    write_evaluation(evaluation, 1, root=tmp_path)


def _build(tmp_path):
    return build_leaderboard(
        scenario_id=SCENARIO,
        evaluator_id=EVALUATOR,
        benchmark_version="0.1",
        root=tmp_path,
    )


def test_consistent_fingerprints_produce_no_warning(tmp_path):
    fp = judge_prompt_fingerprint()
    _write(_evaluation("model-a", fp, 90.0), tmp_path)
    _write(_evaluation("model-b", fp, 80.0), tmp_path)
    payload, summaries = _build(tmp_path)
    assert payload["integrity_warning"] is None
    assert [s.model_slug for s in summaries] == ["model-a", "model-b"]


def test_mixed_fingerprints_across_models_are_flagged(tmp_path):
    _write(_evaluation("model-a", "aaaaaaaaaaaaaaaa", 90.0), tmp_path)
    _write(_evaluation("model-b", "bbbbbbbbbbbbbbbb", 80.0), tmp_path)
    payload, _ = _build(tmp_path)
    warning = payload["integrity_warning"]
    assert warning is not None
    assert "MIXED JUDGE VERSIONS" in warning
    # The invariant is that the mix is REPORTED, not that a particular remedy is
    # suggested. v1.1 dropped "re-evaluate every run with --overwrite": the
    # migration audit established that following it would rewrite incumbent
    # evidence in an append_only group, which the benchmarking docs forbid
    # twice. See audits/v1.1-migration/.
    assert "not valid" in warning
    assert "aaaaaaaaaaaaaaaa" in warning and "bbbbbbbbbbbbbbbb" in warning


def test_an_unfingerprinted_evaluation_counts_as_a_distinct_version(tmp_path):
    """Exactly the interrupted-sweep case: old files carry no fingerprint."""
    _write(_evaluation("model-a", None, 90.0), tmp_path)
    _write(_evaluation("model-b", judge_prompt_fingerprint(), 80.0), tmp_path)
    payload, _ = _build(tmp_path)
    assert payload["integrity_warning"] is not None
    assert "MIXED JUDGE VERSIONS" in payload["integrity_warning"]


def test_all_unfingerprinted_is_internally_consistent(tmp_path):
    """Pre-fingerprint evaluations are uniformly old, so nothing is mixed.

    The guard cannot retroactively see a mix that predates it. That is a real
    limitation, not a bug: it protects future sweeps, and the current state has
    to be resolved by re-evaluating everything.
    """
    _write(_evaluation("model-a", None, 90.0), tmp_path)
    _write(_evaluation("model-b", None, 80.0), tmp_path)
    payload, _ = _build(tmp_path)
    assert payload["integrity_warning"] is None


def test_the_fingerprint_is_stable_across_calls():
    assert judge_prompt_fingerprint() == judge_prompt_fingerprint()
    assert len(judge_prompt_fingerprint()) == 16


def test_the_fingerprint_tracks_the_penalty_prompt(monkeypatch):
    """Changing judge instructions must change the fingerprint."""
    from mondaybench import judge as judge_mod

    before = judge_mod.judge_prompt_fingerprint()
    original = judge_mod.penalty_prompt
    monkeypatch.setattr(
        judge_mod,
        "penalty_prompt",
        lambda gt, src, resp: original(gt, src, resp) + "\nAn extra instruction.",
    )
    assert judge_mod.judge_prompt_fingerprint() != before


def test_mixed_prompt_hashes_are_still_flagged_per_model(tmp_path):
    fp = judge_prompt_fingerprint()
    first = _evaluation("model-a", fp, 90.0)
    _write(first, tmp_path)
    second = _evaluation("model-a", fp, 80.0)
    second = second.model_copy(update={"scenario_prompt_sha256": "b" * 64})
    write_evaluation(second, 2, root=tmp_path)

    _, summaries = _build(tmp_path)
    assert any("more than one prompt hash" in w for w in summaries[0].warnings)


def test_leaderboard_json_carries_the_warning_field(tmp_path):
    _write(_evaluation("model-a", "aaaaaaaaaaaaaaaa", 90.0), tmp_path)
    _write(_evaluation("model-b", "bbbbbbbbbbbbbbbb", 80.0), tmp_path)
    payload, summaries = _build(tmp_path)
    from mondaybench.leaderboard import write_leaderboard

    json_path, _, _ = write_leaderboard(payload, summaries, root=tmp_path)
    written = json.loads(json_path.read_text(encoding="utf-8"))
    assert "integrity_warning" in written
    assert written["integrity_warning"] is not None
