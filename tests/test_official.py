"""What qualifies as official evidence, and what must block publication.

These are the checks that stand between a working repository and a public claim,
so they are tested harder than anything else: a run that slips into an official
battery unnoticed is worse than one that is missing.
"""

from __future__ import annotations

import json

import pytest

from mondaybench.config import ModelConfig, Pricing
from mondaybench.freeze import build_manifest, check_drift, load_manifest, write_manifest
from mondaybench.leaderboard import check_scoring_arithmetic, official_blockers
from mondaybench.official import OFFICIAL_RUNS, plan_model, qualify_run
from mondaybench.runner import write_run
from mondaybench.schemas import (
    BenchmarkRun,
    DimensionScore,
    Evaluation,
    JudgeRecord,
    Penalties,
    PenaltyItem,
    RunEconomics,
    RunGeneration,
    RunModel,
    RunPerformance,
    RunProviderMetadata,
    RunUsage,
)

GOOD_HASH = "e" * 64
OTHER_HASH = "f" * 64

MODEL = ModelConfig(
    slug="glm5.2",
    display_name="GLM 5.2",
    provider="helmcode",
    api_style="openai_compatible",
    model_id="glm5.2",
    base_url_env="HELMCODE_BASE_URL",
    api_key_env="HELMCODE_API_KEY",
    temperature=0,
    max_output_tokens=16000,
    reasoning_enabled=True,
    pricing=Pricing(),
)


def make_run(
    *,
    run_number: int = 1,
    prompt_hash: str = GOOD_HASH,
    finish_reason: str = "stop",
    response: str = "a briefing",
    temperature: float | None = 0,
    max_output_tokens: int = 16000,
    model_id: str = "glm5.2",
    provider: str = "helmcode",
    unsupported: list[str] | None = None,
    scenario_id: str = "monday-001",
) -> BenchmarkRun:
    return BenchmarkRun(
        benchmark_version="0.1",
        scenario_id=scenario_id,
        scenario_prompt_sha256=prompt_hash,
        run_id=f"{scenario_id}__glm5.2__{run_number:03d}",
        run_number=run_number,
        model=RunModel(
            slug="glm5.2", display_name="GLM 5.2", provider=provider, model_id=model_id
        ),
        generation=RunGeneration(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            reasoning_enabled=True,
            unsupported_parameters=unsupported or [],
        ),
        timestamp_utc="2026-08-27T00:00:00Z",
        usage=RunUsage(input_tokens=2900, output_tokens=1200),
        performance=RunPerformance(ttft_ms=1000.0, ttfa_ms=5000.0, total_latency_ms=18000.0),
        economics=RunEconomics(),
        response=response,
        finish_reason=finish_reason,
        provider_metadata=RunProviderMetadata(),
    )


def check(run: BenchmarkRun, **kwargs):
    from pathlib import Path

    return qualify_run(
        run,
        path=Path("run-001.json"),
        expected_prompt_sha256=kwargs.get("prompt", GOOD_HASH),
        model=kwargs.get("model", MODEL),
        scenario_id=kwargs.get("scenario_id", "monday-001"),
    )


# --------------------------------------------------------------------------
# run qualification
# --------------------------------------------------------------------------


def test_a_clean_run_is_official():
    verdict = check(make_run())
    assert verdict.official
    assert verdict.reasons == []


def test_a_different_prompt_hash_disqualifies():
    verdict = check(make_run(prompt_hash=OTHER_HASH))
    assert not verdict.official
    assert any("prompt hash" in r for r in verdict.reasons)


def test_a_truncated_run_disqualifies():
    verdict = check(make_run(finish_reason="length"))
    assert not verdict.official
    assert any("truncated" in r for r in verdict.reasons)


def test_an_empty_response_disqualifies():
    verdict = check(make_run(response="   "))
    assert not verdict.official
    assert any("empty" in r for r in verdict.reasons)


def test_a_dropped_parameter_disqualifies():
    verdict = check(make_run(unsupported=["temperature"]))
    assert not verdict.official
    assert any("rejected configured parameters" in r for r in verdict.reasons)


@pytest.mark.parametrize(
    "kwargs,fragment",
    [
        ({"temperature": 0.7}, "temperature"),
        ({"max_output_tokens": 4000}, "max_output_tokens"),
        ({"model_id": "glm5.3-flash"}, "model_id"),
        ({"provider": "nan"}, "provider"),
    ],
)
def test_config_drift_disqualifies(kwargs, fragment):
    verdict = check(make_run(**kwargs))
    assert not verdict.official
    assert any(fragment in r for r in verdict.reasons)


def test_wrong_scenario_disqualifies():
    verdict = check(make_run(scenario_id="monday-002"), scenario_id="monday-001")
    assert not verdict.official
    assert any("scenario" in r for r in verdict.reasons)


def test_several_faults_are_all_reported():
    verdict = check(make_run(prompt_hash=OTHER_HASH, finish_reason="length", temperature=0.5))
    assert len(verdict.reasons) >= 3


# --------------------------------------------------------------------------
# planning
# --------------------------------------------------------------------------


def test_plan_counts_official_and_asks_for_the_shortfall(tmp_path):
    write_run(make_run(run_number=1), root=tmp_path)
    plan = plan_model(
        scenario_id="monday-001",
        model_slug="glm5.2",
        model=MODEL,
        expected_prompt_sha256=GOOD_HASH,
        root=tmp_path,
    )
    assert plan.have == 1
    assert plan.missing == 2
    assert plan.next_run_numbers() == [2, 3]
    assert not plan.complete


def test_plan_never_reuses_a_run_number_even_for_a_rejected_run(tmp_path):
    # run-001 is unofficial, but its file exists, so 001 must not be reissued.
    write_run(make_run(run_number=1, prompt_hash=OTHER_HASH), root=tmp_path)
    plan = plan_model(
        scenario_id="monday-001",
        model_slug="glm5.2",
        model=MODEL,
        expected_prompt_sha256=GOOD_HASH,
        root=tmp_path,
    )
    assert plan.have == 0
    assert plan.missing == 3
    assert plan.next_run_numbers() == [2, 3, 4]
    assert 1 not in plan.next_run_numbers()


def test_a_complete_plan_asks_for_nothing(tmp_path):
    # Distinct responses: three identical ones are one sample and two cache hits.
    for number in (1, 2, 3):
        write_run(make_run(run_number=number, response=f"briefing {number}"), root=tmp_path)
    plan = plan_model(
        scenario_id="monday-001",
        model_slug="glm5.2",
        model=MODEL,
        expected_prompt_sha256=GOOD_HASH,
        root=tmp_path,
    )
    assert plan.complete
    assert plan.missing == 0
    assert plan.next_run_numbers() == []
    assert plan.target == OFFICIAL_RUNS


# --------------------------------------------------------------------------
# freeze
# --------------------------------------------------------------------------


def test_freeze_detects_a_changed_file(tmp_path):
    (tmp_path / "slack.md").write_text("original", encoding="utf-8")
    manifest = build_manifest(
        scenario_id="monday-001",
        benchmark_version="0.1",
        prompt_sha256=GOOD_HASH,
        rubric_file="rubric-0.2.yaml",
        rubric_version="0.2",
        directory=tmp_path,
        names=["slack.md"],
    )
    write_manifest(manifest, tmp_path)
    assert check_drift(manifest, tmp_path).clean

    (tmp_path / "slack.md").write_text("tampered", encoding="utf-8")
    drift = check_drift(manifest, tmp_path)
    assert not drift.clean
    assert drift.changed[0][0] == "slack.md"


def test_freeze_detects_a_missing_file(tmp_path):
    (tmp_path / "slack.md").write_text("original", encoding="utf-8")
    manifest = build_manifest(
        scenario_id="monday-001",
        benchmark_version="0.1",
        prompt_sha256=GOOD_HASH,
        rubric_file="rubric-0.2.yaml",
        rubric_version="0.2",
        directory=tmp_path,
        names=["slack.md"],
    )
    (tmp_path / "slack.md").unlink()
    drift = check_drift(manifest, tmp_path)
    assert drift.missing == ["slack.md"]
    assert not drift.clean


def test_manifest_round_trips(tmp_path):
    (tmp_path / "slack.md").write_text("original", encoding="utf-8")
    manifest = build_manifest(
        scenario_id="monday-001",
        benchmark_version="0.1",
        prompt_sha256=GOOD_HASH,
        rubric_file="rubric-0.2.yaml",
        rubric_version="0.2",
        directory=tmp_path,
        names=["slack.md"],
    )
    write_manifest(manifest, tmp_path)
    reloaded = load_manifest(tmp_path)
    assert reloaded is not None
    assert reloaded.prompt_sha256 == GOOD_HASH
    assert reloaded.rubric_version == "0.2"
    assert reloaded.files == manifest.files


def test_the_real_scenario_is_frozen_and_intact():
    from mondaybench.config import repo_root
    from mondaybench.prompt_builder import build_prompt
    from mondaybench.scenarios import load_scenario

    directory = repo_root() / "scenarios" / "monday-001"
    manifest = load_manifest(directory)
    assert manifest is not None, "monday-001 must be frozen for v0.1"
    assert check_drift(manifest, directory).clean
    scenario = load_scenario("monday-001", rubric_file=manifest.rubric_file)
    assert build_prompt(scenario).sha256 == manifest.prompt_sha256
    assert scenario.rubric.version == manifest.rubric_version


# --------------------------------------------------------------------------
# publication gates
# --------------------------------------------------------------------------


class FakeSummary:
    def __init__(self, slug, runs=3, scores=None, prompt=GOOD_HASH, rubric="0.2", judge="claude-opus-5"):
        self.model_slug = slug
        self.runs = runs
        self.run_scores = scores if scores is not None else [90.0] * runs
        self.prompt_sha256 = prompt
        self.rubric_version = rubric
        self.judge_model_id = judge
        self.warnings: list[str] = []
        # Added with the reasoning-delivery gates. Empty means "nothing
        # recorded", which the gates treat as no evidence rather than a
        # mismatch - the same way a pre-audit run is treated.
        self.excluded_runs: list[dict] = []
        self.config_fingerprints: list[str | None] = []
        self.reasoning_statuses: list[str] = []


def blockers(summaries, payload=None, **kwargs):
    payload = payload or {"evaluator": "evaluator-opus5-v0.1", "integrity_warning": None}
    return official_blockers(
        payload,
        summaries,  # type: ignore[arg-type]
        expected_models=kwargs.get("models", ["a", "b"]),
        expected_prompt_sha256=GOOD_HASH,
        expected_rubric_version="0.2",
        expected_evaluator_id="evaluator-opus5-v0.1",
        required_runs=3,
    )


def test_a_complete_battery_has_no_blockers():
    assert blockers([FakeSummary("a"), FakeSummary("b")]) == []


def test_too_few_runs_blocks():
    found = blockers([FakeSummary("a", runs=2, scores=[90.0, 91.0]), FakeSummary("b")])
    assert any("2 official run(s), 3 required" in b for b in found)


def test_a_missing_model_blocks():
    found = blockers([FakeSummary("a")])
    assert any("b: no evaluations found" in b for b in found)


def test_an_unexpected_model_blocks():
    found = blockers([FakeSummary("a"), FakeSummary("b"), FakeSummary("c")])
    assert any("outside the official battery" in b for b in found)


def test_a_missing_evaluation_blocks():
    found = blockers([FakeSummary("a", runs=3, scores=[90.0, 91.0]), FakeSummary("b")])
    assert any("an evaluation is missing" in b for b in found)


def test_mixed_prompt_hashes_block():
    found = blockers([FakeSummary("a"), FakeSummary("b", prompt=OTHER_HASH)])
    assert any("multiple prompt hashes" in b for b in found)


def test_the_wrong_prompt_hash_blocks():
    found = blockers([FakeSummary("a", prompt=OTHER_HASH), FakeSummary("b", prompt=OTHER_HASH)])
    assert any("published scenario is" in b for b in found)


def test_mixed_rubric_versions_block():
    found = blockers([FakeSummary("a"), FakeSummary("b", rubric="0.1")])
    assert any("multiple rubric versions" in b for b in found)


def test_the_wrong_rubric_blocks():
    found = blockers([FakeSummary("a", rubric="0.1"), FakeSummary("b", rubric="0.1")])
    assert any("official evaluator pins 0.2" in b for b in found)


def test_mixed_judges_block():
    found = blockers([FakeSummary("a"), FakeSummary("b", judge="claude-sonnet-5")])
    assert any("multiple judge models" in b for b in found)


def test_an_integrity_warning_blocks():
    payload = {"evaluator": "evaluator-opus5-v0.1", "integrity_warning": "MIXED JUDGE VERSIONS"}
    found = blockers([FakeSummary("a"), FakeSummary("b")], payload=payload)
    assert any("integrity warning" in b for b in found)


def test_the_wrong_evaluator_blocks():
    payload = {"evaluator": "evaluator-manual-v0.2", "integrity_warning": None}
    found = blockers([FakeSummary("a"), FakeSummary("b")], payload=payload)
    assert any("expected 'evaluator-opus5-v0.1'" in b for b in found)


def test_a_per_model_warning_blocks():
    summary = FakeSummary("a")
    summary.warnings = ["run-002 hit max_output_tokens"]
    found = blockers([summary, FakeSummary("b")])
    assert any("max_output_tokens" in b for b in found)


# --------------------------------------------------------------------------
# scoring arithmetic
# --------------------------------------------------------------------------


def _evaluation(**overrides) -> Evaluation:
    base = dict(
        evaluator_id="evaluator-opus5-v0.1",
        benchmark_version="0.1",
        rubric_version="0.2",
        scenario_id="monday-001",
        run_id="monday-001__glm5.2__001",
        model_slug="glm5.2",
        scenario_prompt_sha256=GOOD_HASH,
        timestamp_utc="2026-08-27T00:00:00Z",
        judge=JudgeRecord(provider="anthropic", model_id="claude-opus-5", temperature=0),
        dimensions={"action_detection": DimensionScore(score=90.0, max_score=100.0)},
        criteria={},
        false_actions={},
        penalties=Penalties(),
        base_score=90.0,
        final_score=90.0,
    )
    base.update(overrides)
    return Evaluation(**base)  # type: ignore[arg-type]


def _write_eval(evaluation: Evaluation, tmp_path):
    from mondaybench.evaluator import write_evaluation

    write_evaluation(evaluation, 1, root=tmp_path)


def test_consistent_arithmetic_passes(tmp_path):
    _write_eval(_evaluation(), tmp_path)
    assert check_scoring_arithmetic("evaluator-opus5-v0.1", "monday-001", tmp_path) == []


def test_dimensions_not_summing_to_base_is_caught(tmp_path):
    _write_eval(_evaluation(base_score=95.0, final_score=95.0), tmp_path)
    problems = check_scoring_arithmetic("evaluator-opus5-v0.1", "monday-001", tmp_path)
    assert any("dimensions sum to" in p for p in problems)


def test_penalties_not_applied_is_caught(tmp_path):
    penalties = Penalties(
        items=[PenaltyItem(type="PROHIBITED_ACTION", points=-10.0)], raw_total=-10.0, total=-10.0
    )
    # final should be 80, not 90
    _write_eval(_evaluation(penalties=penalties), tmp_path)
    problems = check_scoring_arithmetic("evaluator-opus5-v0.1", "monday-001", tmp_path)
    assert any("!= final" in p for p in problems)


def test_the_published_evaluations_add_up():
    """The real files, not a fixture: no published score may fail this."""
    from mondaybench.config import repo_root

    root = repo_root()
    for evaluator in ("evaluator-manual-v0.2", "evaluator-opus5-v0.1"):
        if not (root / "evaluations" / evaluator).exists():
            continue
        assert check_scoring_arithmetic(evaluator, "monday-001") == []


def test_arithmetic_check_reads_the_verdict_files_as_json():
    """The verdicts are the audit trail, so they must stay machine-readable."""
    from mondaybench.config import repo_root

    directory = repo_root() / "verdicts"
    if not directory.exists():
        pytest.skip("no recorded verdicts in this checkout")
    for path in directory.glob("*.verdicts.jsonl"):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if line.strip() and not line.lstrip().startswith("#"):
                json.loads(line)  # raises on malformed audit trail


# --------------------------------------------------------------------------
# Cache-hit detection
# --------------------------------------------------------------------------
#
# Both endpoints cache a response for an identical prompt. Measured during the
# official battery: a repeat request returned in 715ms with a byte-identical
# response against 32,327ms for the real generation. Three "official runs" would
# have been two generations and a stored copy, with run_range and sigma deflated
# to zero. `caching: false` in models.yaml suppresses it; this check is the
# independent backstop for when a flag stops being honoured.


def test_a_duplicated_response_is_rejected_as_a_cache_hit(tmp_path):
    write_run(make_run(run_number=1, response="identical briefing"), root=tmp_path)
    write_run(make_run(run_number=2, response="identical briefing"), root=tmp_path)
    plan = plan_model(
        scenario_id="monday-001",
        model_slug="glm5.2",
        model=MODEL,
        expected_prompt_sha256=GOOD_HASH,
        root=tmp_path,
    )
    assert plan.have == 1, "only the first of two identical responses may count"
    assert len(plan.rejected) == 1
    assert any("cached duplicate" in r for r in plan.rejected[0].reasons)


def test_the_earliest_run_keeps_its_place(tmp_path):
    write_run(make_run(run_number=1, response="same"), root=tmp_path)
    write_run(make_run(run_number=2, response="same"), root=tmp_path)
    write_run(make_run(run_number=3, response="different"), root=tmp_path)
    plan = plan_model(
        scenario_id="monday-001",
        model_slug="glm5.2",
        model=MODEL,
        expected_prompt_sha256=GOOD_HASH,
        root=tmp_path,
    )
    assert [v.run_number for v in plan.official] == [1, 3]
    assert [v.run_number for v in plan.rejected] == [2]


def test_three_distinct_responses_are_all_official(tmp_path):
    for number, text in enumerate(("first", "second", "third"), start=1):
        write_run(make_run(run_number=number, response=text), root=tmp_path)
    plan = plan_model(
        scenario_id="monday-001",
        model_slug="glm5.2",
        model=MODEL,
        expected_prompt_sha256=GOOD_HASH,
        root=tmp_path,
    )
    assert plan.complete
    assert plan.have == 3
    assert plan.rejected == []


def test_caching_is_disabled_for_every_configured_model():
    """A missing flag here silently turns run 3 into a copy of run 2.

    Scoped to the models this harness can actually generate. An entry with
    neither an endpoint nor a key cannot reach the provider adapter at all, so
    there is no request for the flag to ride on, and declaring `caching: false`
    for one would assert a transport property that was never observable. Those
    entries carry a stricter obligation instead: they must also declare no
    output ceiling, so nothing in the config can be read as a generation
    parameter that was actually sent.
    """
    from mondaybench.config import load_models

    for slug, cfg in load_models().items():
        if cfg.base_url_env is None and cfg.api_key_env is None:
            assert cfg.max_output_tokens is None, (
                f"{slug} has no API route but declares a generation ceiling"
            )
            continue
        assert cfg.extra_body.get("caching") is False, f"{slug} may serve cached responses"


def test_the_cache_flag_never_reaches_the_prompt():
    """`caching` is a transport directive; the prompt hash must not move."""
    from mondaybench.freeze import load_manifest
    from mondaybench.config import repo_root
    from mondaybench.prompt_builder import build_prompt
    from mondaybench.scenarios import load_scenario

    manifest = load_manifest(repo_root() / "scenarios" / "monday-001")
    assert manifest is not None
    scenario = load_scenario("monday-001", rubric_file=manifest.rubric_file)
    assert build_prompt(scenario).sha256 == manifest.prompt_sha256


def test_the_flag_is_sent_in_the_request_body():
    from mondaybench.providers.openai_compatible import OpenAICompatibleProvider

    provider = OpenAICompatibleProvider(base_url="https://api.example.com/v1", api_key="sk-test")
    payload, _ = provider._payload(
        model_id="glm5.2",
        system_prompt="You are a helpful assistant.",
        user_prompt="hello",
        generation_config={"max_output_tokens": 16000, "extra_body": {"caching": False}},
        stream=True,
    )
    assert payload["caching"] is False
    # And it must not have disturbed the messages.
    assert payload["messages"][1]["content"] == "hello"
