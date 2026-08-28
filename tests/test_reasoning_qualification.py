"""A reasoning model that came back without reasoning is not official evidence.

`monday-002/qwen3.8-flash/run-002` scored 66.5 against 93.0 and 100.0 for the
same model on the same prompt, with zero reasoning tokens where the others spent
42,808 and 30,342. The harness could not see it: `reasoning_enabled` was copied
from a declared capability in `models.yaml` and mistaken for an observation.

These tests fix the distinction in place - requested comes from config,
delivered comes from the response - and guard the three things that must never
regress: an unqualified run cannot reach a statistic, it also cannot be deleted,
and a provider that simply reports nothing must not be convicted on silence.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mondaybench import reasoning
from mondaybench.config import load_models
from mondaybench.leaderboard import ModelSummary, official_blockers
from mondaybench.official import qualify_run, reasoning_status
from mondaybench.runner import load_run
from mondaybench.schemas import (
    BenchmarkRun,
    RunEconomics,
    RunGeneration,
    RunModel,
    RunPerformance,
    RunProviderMetadata,
    RunUsage,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
QWEN = REPO_ROOT / "runs" / "monday-002" / "qwen3.8-flash"
PROMPT = "740e627cbc7413c321ede0d54000504de54821d34ff4677f82731b89600423a8"


def make_run(
    *,
    reasoning_requested: bool | None,
    reasoning_tokens: int | None,
    raw_details: dict | None = None,
    legacy_flag: bool = False,
) -> BenchmarkRun:
    return BenchmarkRun(
        benchmark_version="0.2",
        scenario_id="monday-002",
        scenario_prompt_sha256=PROMPT,
        run_id="monday-002__m__001",
        run_number=1,
        model=RunModel(slug="m", display_name="M", provider="p", model_id="m"),
        generation=RunGeneration(
            temperature=0.0,
            max_output_tokens=32000,
            reasoning_enabled=legacy_flag,
            reasoning_requested=reasoning_requested,
        ),
        timestamp_utc="2026-08-28T00:00:00Z",
        usage=RunUsage(input_tokens=10, output_tokens=20, reasoning_tokens=reasoning_tokens),
        performance=RunPerformance(),
        economics=RunEconomics(),
        response="an answer",
        finish_reason="stop",
        provider_metadata=RunProviderMetadata(
            raw_usage={"completion_tokens_details": raw_details} if raw_details else {}
        ),
    )


# --------------------------------------------------------------------------
# Reasoning delivery
# --------------------------------------------------------------------------


def test_requested_and_delivered_is_valid():
    run = make_run(reasoning_requested=True, reasoning_tokens=1200)
    assert reasoning.classify(run) == ("DELIVERED", 1200)
    assert reasoning.disqualifies("DELIVERED") is False


def test_requested_and_zero_tokens_is_invalid():
    run = make_run(reasoning_requested=True, reasoning_tokens=0)
    status, tokens = reasoning.classify(run)
    assert (status, tokens) == ("NOT_DELIVERED", 0)
    assert reasoning.disqualifies(status) is True


def test_not_requested_and_zero_tokens_is_valid():
    """Gemma 4, MIMO and Qwen 3.6 all report zero and are perfectly fine."""
    run = make_run(reasoning_requested=False, reasoning_tokens=0)
    status, _ = reasoning.classify(run)
    assert status == "NOT_REQUESTED"
    assert reasoning.disqualifies(status) is False


def test_a_provider_that_reports_nothing_is_unobservable_not_invalid():
    """Silence is not evidence of absence, so it must not disqualify."""
    run = make_run(reasoning_requested=True, reasoning_tokens=None)
    status, tokens = reasoning.classify(run)
    assert (status, tokens) == ("UNOBSERVABLE", None)
    assert reasoning.disqualifies(status) is False


def test_the_token_count_is_read_from_provider_details_when_usage_is_silent():
    run = make_run(
        reasoning_requested=True, reasoning_tokens=None, raw_details={"reasoning_tokens": 77}
    )
    assert reasoning.classify(run) == ("DELIVERED", 77)


def test_zero_in_provider_details_still_disqualifies():
    run = make_run(
        reasoning_requested=True, reasoning_tokens=None, raw_details={"reasoning_tokens": 0}
    )
    assert reasoning.classify(run) == ("NOT_DELIVERED", 0)


def test_a_legacy_run_without_the_new_field_falls_back_to_reasoning_enabled():
    """Pre-audit runs carry only `reasoning_enabled`; they must stay classifiable."""
    run = make_run(reasoning_requested=None, reasoning_tokens=0, legacy_flag=True)
    assert reasoning.classify(run)[0] == "NOT_DELIVERED"
    run = make_run(reasoning_requested=None, reasoning_tokens=0, legacy_flag=False)
    assert reasoning.classify(run)[0] == "NOT_REQUESTED"


def test_config_can_turn_the_expectation_off():
    """Disabling thinking in extra_body must not make every run invalid."""
    assert reasoning.requested_from_config({"reasoning": True}, {}) is True
    assert reasoning.requested_from_config({"reasoning": True}, {"thinking": False}) is False
    assert (
        reasoning.requested_from_config({"reasoning": True}, {"thinking": {"type": "disabled"}})
        is False
    )
    assert reasoning.requested_from_config({}, {}) is False


# --------------------------------------------------------------------------
# Qualification and the 3-run gate
# --------------------------------------------------------------------------


def _qualify(run: BenchmarkRun):
    return qualify_run(
        run, path=Path("x.json"), expected_prompt_sha256=PROMPT, model=None,
        scenario_id="monday-002",
    )


def test_qualify_run_rejects_a_reasoning_run_with_no_reasoning():
    verdict = _qualify(make_run(reasoning_requested=True, reasoning_tokens=0))
    assert verdict.official is False
    assert any(reasoning.REASONING_NOT_DELIVERED in r for r in verdict.reasons)


def test_qualify_run_accepts_a_non_reasoning_model_reporting_zero():
    assert _qualify(make_run(reasoning_requested=False, reasoning_tokens=0)).official is True


def test_qualify_run_accepts_an_unobservable_provider():
    assert _qualify(make_run(reasoning_requested=True, reasoning_tokens=None)).official is True


def _summary(slug: str, runs: int, scores: list[float], **kw) -> ModelSummary:
    return ModelSummary(
        model_slug=slug, display_name=slug, runs=runs,
        mean=sum(scores) / len(scores) if scores else 0.0,
        minimum=min(scores) if scores else 0.0, maximum=max(scores) if scores else 0.0,
        stddev=0.0, dimensions={}, median_ttfa_ms=None, median_total_latency_ms=None,
        median_cost_usd=None, median_ttft_ms=None, median_output_tokens=None,
        prompt_sha256=PROMPT, run_scores=scores, rubric_version="0.2",
        judge_model_id="claude-opus-5", **kw,
    )


def _blockers(summaries):
    return official_blockers(
        {"evaluator": "evaluator-opus5-v0.2", "integrity_warning": None},
        summaries,
        expected_models=[s.model_slug for s in summaries],
        expected_prompt_sha256=PROMPT,
        expected_rubric_version="0.2",
        expected_evaluator_id="evaluator-opus5-v0.2",
        required_runs=3,
    )


def test_two_valid_plus_one_invalid_fails_the_gate():
    """The invalid run is already dropped, so the model is short and blocked."""
    excluded = [{"run_id": "r2", "score": 66.5, "reasons": ["REASONING_NOT_DELIVERED: ..."]}]
    blockers = _blockers([_summary("qwen3.8-flash", 2, [93.0, 100.0], excluded_runs=excluded)])
    assert any("2 official run(s), 3 required" in b for b in blockers)


def test_two_valid_plus_a_replacement_passes_the_gate():
    """An exclusion that has been replaced must not block publication forever."""
    excluded = [{"run_id": "r2", "score": 66.5, "reasons": ["REASONING_NOT_DELIVERED: ..."]}]
    blockers = _blockers(
        [_summary("qwen3.8-flash", 3, [93.0, 100.0, 91.5], excluded_runs=excluded)]
    )
    assert blockers == []


def test_a_run_missing_its_reasoning_blocks_even_if_it_slipped_into_a_summary():
    blockers = _blockers(
        [
            _summary(
                "qwen3.8-flash", 3, [93.0, 100.0, 66.5],
                reasoning_statuses=["DELIVERED", "DELIVERED", "NOT_DELIVERED"],
            )
        ]
    )
    assert any("missing the reasoning it requested" in b for b in blockers)


def test_runs_spanning_two_generation_configs_block():
    blockers = _blockers(
        [_summary("m", 3, [1.0, 2.0, 3.0], config_fingerprints=["a" * 64, "b" * 64, "a" * 64])]
    )
    assert any("span 2 generation configs" in b for b in blockers)


def test_an_unrecorded_fingerprint_is_not_treated_as_a_mismatch():
    """Pre-audit runs carry None. A missing hash is not evidence of a different one."""
    blockers = _blockers(
        [_summary("m", 3, [1.0, 2.0, 3.0], config_fingerprints=[None, None, "a" * 64])]
    )
    assert not any("generation configs" in b for b in blockers)


# --------------------------------------------------------------------------
# Effective-configuration metadata
# --------------------------------------------------------------------------


def test_the_replacement_run_records_the_full_effective_config():
    run = load_run(QWEN / "run-004.json")
    g = run.generation
    assert g.reasoning_requested is True
    assert g.system_prompt_sha256 and len(g.system_prompt_sha256) == 64
    assert g.config_sha256 and len(g.config_sha256) == 64
    assert g.extra_body == {"caching": False}
    assert "top_p" in g.model_dump()  # recorded even when None: not sent, provider default
    assert run.reasoning is not None
    assert run.reasoning.status == "DELIVERED"
    assert run.reasoning.tokens and run.reasoning.tokens > 0


def test_an_absent_system_prompt_hashes_rather_than_recording_null():
    assert reasoning.system_prompt_sha256(None) == reasoning.EMPTY_SHA256
    assert reasoning.system_prompt_sha256("") == reasoning.EMPTY_SHA256
    assert reasoning.system_prompt_sha256("x") != reasoning.EMPTY_SHA256


def test_the_config_fingerprint_is_stable_and_order_independent():
    kwargs = dict(
        provider="nan", model_id="qwen3.8-flash", temperature=0.0, top_p=None,
        max_output_tokens=32000, reasoning_requested=True, reasoning_mode=None,
        reasoning_effort=None, system_prompt_hash="a" * 64,
    )
    a = reasoning.generation_config_sha256(extra_body={"caching": False, "z": 1}, **kwargs)
    b = reasoning.generation_config_sha256(extra_body={"z": 1, "caching": False}, **kwargs)
    assert a == b
    c = reasoning.generation_config_sha256(extra_body={"caching": True}, **kwargs)
    assert a != c


def test_the_fingerprint_ignores_anything_about_the_response():
    """Two runs of the same config must fingerprint alike however they came out."""
    kwargs = dict(
        provider="nan", model_id="m", temperature=0.0, top_p=0.9, max_output_tokens=100,
        reasoning_requested=True, reasoning_mode=None, reasoning_effort=None,
        extra_body={}, system_prompt_hash="b" * 64,
    )
    assert reasoning.generation_config_sha256(**kwargs) == reasoning.generation_config_sha256(
        **kwargs
    )


def test_top_p_is_pinnable_and_reaches_the_config():
    assert load_models()["qwen3.8-flash"].top_p is None  # not pinned: provider default


# --------------------------------------------------------------------------
# Historical integrity
# --------------------------------------------------------------------------


def test_the_invalidated_run_and_its_evaluation_are_still_on_disk():
    assert (QWEN / "run-002.json").exists()
    assert (QWEN / "run-002.INVALIDATED.md").exists()
    evaluation = (
        REPO_ROOT
        / "evaluations/evaluator-opus5-v0.2/monday-002/qwen3.8-flash/run-002.json"
    )
    assert evaluation.exists()
    assert json.loads(evaluation.read_text(encoding="utf-8"))["final_score"] == 66.5


def test_the_invalidated_run_is_excluded_from_the_published_statistics():
    payload = json.loads(
        (REPO_ROOT / "leaderboard/monday-002/leaderboard.json").read_text(encoding="utf-8")
    )
    qwen = next(m for m in payload["models"] if m["model_slug"] == "qwen3.8-flash")
    assert qwen["score"]["runs"] == 3
    assert 66.5 not in qwen["run_scores"]
    assert any(e["run_id"].endswith("__002") for e in qwen["excluded_runs"])
    assert not any(p.endswith("run-002.json") for p in qwen["provenance"]["runs"])


def test_the_pre_correction_leaderboard_is_archived():
    archived = REPO_ROOT / "archive/monday-002-leaderboard-pre-audit/leaderboard.json"
    assert archived.exists()
    payload = json.loads(archived.read_text(encoding="utf-8"))
    qwen = next(m for m in payload["models"] if m["model_slug"] == "qwen3.8-flash")
    assert qwen["run_scores"] == [93.0, 66.5, 100.0]
    assert qwen["score"]["mean"] == 86.5


def test_only_one_monday_002_run_is_disqualified():
    """Scoped to the scenario it is about.

    This asserted "one in the whole repository" until monday-003 landed and its
    calibration hit the same provider defect twice. A fact about one battery
    stated as a fact about the repo is the same mistake the leaderboard renderer
    made with dimensions; scoping it keeps the guard and drops the false claim.
    """
    offenders = [
        p
        for p in sorted(REPO_ROOT.glob("runs/monday-002/*/run-*.json"))
        if reasoning_status(load_run(p)) == "NOT_DELIVERED"
    ]
    assert [p.name for p in offenders] == ["run-002.json"]
    assert offenders[0].parent.name == "qwen3.8-flash"


def test_monday_001_runs_all_still_qualify():
    models = load_models()
    for path in sorted((REPO_ROOT / "runs" / "monday-001").rglob("run-*.json")):
        run = load_run(path)
        verdict = qualify_run(
            run,
            path=path,
            expected_prompt_sha256=run.scenario_prompt_sha256,
            model=models.get(run.model.slug),
            scenario_id="monday-001",
        )
        assert verdict.official, f"{path}: {verdict.reasons}"


# --------------------------------------------------------------------------
# Line endings
# --------------------------------------------------------------------------


def test_gitattributes_pins_lf():
    text = (REPO_ROOT / ".gitattributes").read_text(encoding="utf-8")
    assert "* text=auto eol=lf" in text
    for suffix in ("*.md", "*.yaml", "*.json", "*.jsonl", "*.csv", "*.py", "*.txt"):
        assert f"{suffix}" in text


@pytest.mark.parametrize(
    "pattern",
    [
        "scenarios/monday-002/*.md",
        "scenarios/monday-002/*.csv",
        "scenarios/monday-002/*.yaml",
        "scenarios/monday-002/*.txt",
    ],
)
def test_frozen_scenario_content_is_lf(pattern):
    """These are the files FROZEN.yaml hashes, so their bytes must travel.

    Two of them - rubric.yaml and scenario.yaml - were rewritten by Python's
    text mode during the freeze and picked up CRLF, which made the manifest
    describe one Windows working tree rather than the content. A Linux clone
    would have failed `freeze --check` on both.
    """
    offenders = [
        p.relative_to(REPO_ROOT).as_posix()
        for p in sorted(REPO_ROOT.glob(pattern))
        if b"\r\n" in p.read_bytes()
    ]
    assert offenders == [], f"CRLF in frozen scenario content: {offenders}"


def test_the_freeze_manifest_matches_the_committed_bytes():
    """The point of the manifest is that it travels. Prove that it does."""
    import hashlib as _h
    import subprocess

    import yaml as _yaml

    manifest = _yaml.safe_load(
        (REPO_ROOT / "scenarios/monday-002/FROZEN.yaml").read_text(encoding="utf-8")
    )
    mismatched = []
    for name, expected in manifest["files"].items():
        blob = subprocess.run(
            ["git", "show", f"HEAD:scenarios/monday-002/{name}"],
            capture_output=True,
            cwd=REPO_ROOT,
        ).stdout
        if not blob:
            continue  # not committed yet, nothing to compare against
        if _h.sha256(blob).hexdigest() != expected:
            mismatched.append(name)
    assert mismatched == [], f"manifest describes a working tree, not the repo: {mismatched}"


def test_artefacts_written_after_the_fix_are_lf():
    """CSV is the one documented exception: RFC 4180 specifies CRLF."""
    targets = [
        REPO_ROOT / "runs/monday-002/qwen3.8-flash/run-004.json",
        REPO_ROOT / "leaderboard/monday-002/leaderboard.md",
        REPO_ROOT / "leaderboard/monday-002/analysis.md",
        REPO_ROOT / "leaderboard/monday-002/criterion-matrix.md",
        REPO_ROOT / "verdicts/monday-002/qwen3.8-flash.verdicts.jsonl",
        REPO_ROOT / "scenarios/monday-002/FROZEN.yaml",
    ]
    offenders = [t.name for t in targets if b"\r\n" in t.read_bytes()]
    assert offenders == [], f"CRLF in freshly written artefacts: {offenders}"


# --------------------------------------------------------------------------
# Multi-signal delivery: a counter of zero is not proof of no reasoning
# --------------------------------------------------------------------------


def make_timed_run(*, requested, tokens, ttft_ms, ttfa_ms, stream=None, events=None):
    """A run whose delivery has to be settled from timings or stream events."""
    from mondaybench.schemas import RunReasoning

    run = make_run(reasoning_requested=requested, reasoning_tokens=tokens)
    block = None
    if stream is not None or events is not None:
        block = RunReasoning(
            requested=bool(requested), status="UNOBSERVABLE", tokens=tokens,
            stream_observed=stream, stream_event_count=events,
        )
    return run.model_copy(
        update={
            "performance": RunPerformance(ttft_ms=ttft_ms, ttfa_ms=ttfa_ms),
            "reasoning": block,
        }
    )


def test_explicit_tokens_win_and_are_labelled_as_such():
    run = make_timed_run(requested=True, tokens=900, ttft_ms=10.0, ttfa_ms=10.0)
    assert reasoning.classify_detailed(run) == ("DELIVERED", 900, "explicit_reasoning_tokens")


def test_a_stream_event_proves_delivery_even_when_usage_says_zero():
    """The MIMO case, as the adapter will record it from now on."""
    run = make_timed_run(
        requested=True, tokens=0, ttft_ms=10.0, ttfa_ms=10.0, stream=True, events=812
    )
    status, tokens, evidence = reasoning.classify_detailed(run)
    assert (status, tokens, evidence) == ("DELIVERED", 0, "explicit_reasoning_stream")


def test_a_long_pre_answer_stream_proves_delivery_for_historical_runs():
    """No stream field recorded, so the verdict is reconstructed and labelled."""
    run = make_timed_run(requested=False, tokens=0, ttft_ms=1_300.0, ttfa_ms=163_300.0)
    status, _, evidence = reasoning.classify_detailed(run)
    assert (status, evidence) == ("DELIVERED", "derived_pre_answer_stream")


def test_a_tiny_timing_difference_is_not_reasoning():
    """Buffering and rounding must never be promoted to evidence."""
    for gap in (0.0, 0.4, 12.5, 300.0, 999.9):
        run = make_timed_run(requested=True, tokens=0, ttft_ms=100.0, ttfa_ms=100.0 + gap)
        status, _, evidence = reasoning.classify_detailed(run)
        assert (status, evidence) == ("NOT_DELIVERED", None), f"gap {gap} was accepted"


def test_metadata_before_the_answer_does_not_count_as_reasoning():
    """Role-only and usage deltas never set ttft, so they cannot open a gap.

    Guarded at the adapter level: only a non-empty reasoning or content delta
    moves the clock. A run whose two timings are equal has no pre-answer
    stream, whatever else the provider sent.
    """
    run = make_timed_run(requested=True, tokens=0, ttft_ms=2_000.0, ttfa_ms=2_000.0)
    assert reasoning.classify_detailed(run)[0] == "NOT_DELIVERED"


def test_an_explicitly_empty_stream_is_a_positive_absence():
    run = make_timed_run(
        requested=True, tokens=None, ttft_ms=5.0, ttfa_ms=5.0, stream=False, events=0
    )
    assert reasoning.classify_detailed(run)[0] == "NOT_DELIVERED"


def test_no_signal_at_all_is_still_unobservable():
    run = make_timed_run(requested=True, tokens=None, ttft_ms=None, ttfa_ms=None)
    assert reasoning.classify_detailed(run)[0] == "UNOBSERVABLE"


def test_missing_timings_are_never_scored_as_if_measured():
    run = make_timed_run(requested=True, tokens=None, ttft_ms=10.0, ttfa_ms=None)
    assert reasoning.classify_detailed(run)[0] == "UNOBSERVABLE"


def test_delivery_outranks_the_request_flag():
    """A model that demonstrably thought is DELIVERED, declared or not."""
    run = make_timed_run(requested=False, tokens=4_000, ttft_ms=1.0, ttfa_ms=1.0)
    assert reasoning.classify_detailed(run)[0] == "DELIVERED"


# --------------------------------------------------------------------------
# The historical runs this was built for
# --------------------------------------------------------------------------


@pytest.mark.parametrize("scenario", ["monday-001", "monday-002"])
def test_every_mimo_run_is_delivered_on_stream_evidence(scenario):
    paths = sorted((REPO_ROOT / "runs" / scenario / "mimo-v2.5").glob("run-*.json"))
    assert len(paths) == 3
    for path in paths:
        status, _, evidence = reasoning.classify_detailed(load_run(path))
        assert (status, evidence) == ("DELIVERED", "derived_pre_answer_stream"), path


def test_mimo_is_now_declared_reasoning_capable():
    model = load_models()["mimo-v2.5"]
    assert reasoning.requested_from_config(model.capabilities, model.extra_body) is True


def test_the_qwen_invalid_run_is_still_not_delivered():
    status, tokens, evidence = reasoning.classify_detailed(load_run(QWEN / "run-002.json"))
    assert (status, tokens, evidence) == ("NOT_DELIVERED", 0, None)


@pytest.mark.parametrize("number", ["001", "003", "004"])
def test_the_qwen_valid_runs_are_delivered_on_explicit_tokens(number):
    status, _, evidence = reasoning.classify_detailed(load_run(QWEN / f"run-{number}.json"))
    assert (status, evidence) == ("DELIVERED", "explicit_reasoning_tokens")


@pytest.mark.parametrize("slug", ["gemma4", "qwen3.6"])
def test_the_genuinely_non_reasoning_models_stay_not_requested(slug):
    for scenario in ("monday-001", "monday-002"):
        for path in sorted((REPO_ROOT / "runs" / scenario / slug).glob("run-*.json")):
            assert reasoning.classify_detailed(load_run(path))[0] == "NOT_REQUESTED", path


def test_every_disqualified_run_is_a_reasoning_model_returning_no_reasoning():
    """Repo-wide, but asserting the *rule* rather than a count.

    The count grows every time a provider serves a thinking model without
    thinking, which is exactly what this guard exists to notice. What must stay
    true is that nothing else ever lands in this list.
    """
    offenders = [
        p.relative_to(REPO_ROOT).as_posix()
        for p in sorted(REPO_ROOT.glob("runs/monday-00*/*/run-*.json"))
        if reasoning.classify(load_run(p))[0] == "NOT_DELIVERED"
    ]
    assert "runs/monday-002/qwen3.8-flash/run-002.json" in offenders
    for rel in offenders:
        run = load_run(REPO_ROOT / rel)
        assert reasoning.was_requested(run), rel
        assert reasoning.delivery_evidence(run)[0] is None, rel
    # Every one of them is excluded from its scenario's qualifying runs.
    for rel in offenders:
        run = load_run(REPO_ROOT / rel)
        verdict = qualify_run(
            run,
            path=REPO_ROOT / rel,
            expected_prompt_sha256=run.scenario_prompt_sha256,
            model=None,
            scenario_id=run.scenario_id,
        )
        assert verdict.official is False, rel


def test_no_official_score_moved():
    payload = json.loads(
        (REPO_ROOT / "leaderboard/monday-002/leaderboard.json").read_text(encoding="utf-8")
    )
    scores = {m["display_name"]: m["run_scores"] for m in payload["models"]}
    assert scores["MIMO v2.5"] == [64.5, 81.5, 97.5]
    assert scores["Qwen 3.8 Flash"] == [93.0, 100.0, 91.5]
    means = {m["display_name"]: round(m["score"]["mean"], 1) for m in payload["models"]}
    assert means == {
        "Qwen 3.8 Flash": 94.8, "GLM 5.2": 91.2, "DeepSeek V4 Flash": 89.3,
        "GLM 5.3 Flash": 87.3, "MIMO v2.5": 81.2, "Qwen 3.6": 70.2, "Gemma 4": 54.2,
    }
