"""Full pipeline against fake providers: no network, no credentials.

Proves the seam the whole benchmark rests on - a raw run written once, then
evaluated by a judge that only ever emits labels, then aggregated.
"""

from __future__ import annotations

import json

import pytest

from mondaybench import runner as runner_mod
from mondaybench.config import EvaluatorConfig, ModelConfig, Pricing
from mondaybench.evaluator import evaluate_run
from mondaybench.judge import Judge
from mondaybench.leaderboard import build_leaderboard, write_leaderboard
from mondaybench.prompt_builder import build_prompt
from mondaybench.providers.base import GenerationResult, ModelProvider, ProviderError
from mondaybench.runner import RunExistsError, execute_run, find_runs

GOOD_RESPONSE = """
## 1. What happened while I was away

- Acme reported a spike in API errors on Thursday. Marcus traced it to a
  connection pool config in release 2.18.0, rolled it back, and Acme confirmed
  recovery. The incident is closed.
- Analytics v2 slipped from Monday to Wednesday after QA found an export
  regression. Sam owns release coordination.
- Julia took full ownership of the Analytics v2 launch email. Nothing is needed
  from me there.
- Contoso's commercial terms are agreed, but their legal team raised a
  data-retention question.
- Enterprise churn moved from 3.1% to 4.4%.
- Proposed Enterprise pricing is still a draft and internal only.
- Friday's partner sync happened; October integration is still the target.

## 2. What requires my attention today, in priority order

1. **Contoso data retention - before 11:00.** Sarah needs written confirmation
   that admin-deleted data is also purged from disaster-recovery backups within
   the DPA retention period. Noah suggests Marcus knows the infrastructure
   behaviour. If this is not confirmed by 11:00, the renewal signature slips to
   Contoso's next approval window (EUR 72k ARR).
2. **Umbrella metrics.** Umbrella shows 163 API errors, 1821ms p95 latency and
   usage down 41% over 7 days, on only 94,217 requests. Nothing in Slack, email
   or the meeting notes explains this. I do not know the cause and should not
   guess - it needs investigating today.
3. **Enterprise churn breakdown.** Daniel wants a clearer view before Tuesday's
   board meeting. Pied Piper and Hooli may contribute but the provided material
   does not establish that they fully explain the move from 3.1% to 4.4%.
4. **Analytics v2 readiness (low).** Release is Wednesday, so a readiness check
   can wait until the critical items above are handled.

## 3. Important but no action needed from me

- Acme is resolved; Marcus is writing the incident notes.
- Julia owns the launch email and will have a draft before Tuesday.
- The icon question was settled - existing outlined icon for this release.
- Proposed Enterprise pricing must not be shared externally until approved and
  announced. Mark at Initech asked for the new tiers; I cannot send them.

## 4. Unclear or needs more information

- **Umbrella's root cause is unknown.** The metrics are anomalous; the cause is
  not established by anything provided.
- **Friday conversion.** Julia thought conversion dropped, but the provided
  metrics contain no conversion data at all, so this cannot be verified from the
  data I have.
- **Churn causality.** The two known cancellations do not establish the full
  cause of the increase.
- Globex asked to move the Q3 planning session to Thursday - no urgency,
  confirm early this week.
""".strip()


class FakeModelProvider(ModelProvider):
    def __init__(self, text: str = GOOD_RESPONSE, fail_times: int = 0, transient: bool = True):
        self.text = text
        self.fail_times = fail_times
        self.transient = transient
        self.calls = 0

    def generate(self, *, model_id, system_prompt, user_prompt, generation_config):
        self.calls += 1
        if self.fail_times > 0:
            self.fail_times -= 1
            raise ProviderError("simulated failure", transient=self.transient)
        return GenerationResult(
            text=self.text,
            input_tokens=2900,
            output_tokens=700,
            ttft_ms=310.0,
            total_latency_ms=4200.0,
            generation_ms=3890.0,
            provider_request_id="req_fake",
            finish_reason="stop",
            raw_usage={"prompt_tokens": 2900, "completion_tokens": 700},
        )


class FakeJudgeProvider(ModelProvider):
    """A judge that PASSes everything, triggers nothing, penalizes nothing."""

    def __init__(self, label: str = "PASS"):
        self.label = label
        self.criterion_calls = 0

    def generate(self, *, model_id, system_prompt, user_prompt, generation_config):
        if "false or unnecessary actions" in user_prompt:
            ids = [
                line.split(":")[0].removeprefix("- ").strip()
                for line in user_prompt.splitlines()
                if line.startswith("- ") and ":" in line
            ]
            payload = {"items": [{"id": i, "triggered": False, "evidence": ""} for i in ids]}
        elif "serious factual failures" in user_prompt:
            payload = {"violations": []}
        else:
            self.criterion_calls += 1
            payload = {"result": self.label, "evidence": "quoted", "reason": "matches definition"}
        return GenerationResult(
            text=json.dumps(payload), input_tokens=800, output_tokens=40, total_latency_ms=900.0
        )


TEST_MODEL = ModelConfig(
    slug="fixture-model",
    display_name="Fixture Model",
    provider="fake",
    api_style="openai_compatible",
    model_id="fixture-model",
    base_url_env=None,
    api_key_env=None,
    temperature=0,
    max_output_tokens=4000,
    reasoning_enabled=False,
    pricing=Pricing(input_per_million_usd=0.2, output_per_million_usd=0.8),
)


def _evaluator(scenario_map: dict[str, list[str]]) -> EvaluatorConfig:
    return EvaluatorConfig(
        id="evaluator-v0.1",
        provider="fake",
        api_style="anthropic",
        model_id="fake-judge",
        model_env=None,
        base_url_env=None,
        api_key_env=None,
        temperature=0,
        effort="medium",
        max_output_tokens=4000,
        require_evidence=True,
        ground_truth_map=scenario_map,
    )


@pytest.fixture
def patched_provider(monkeypatch):
    provider = FakeModelProvider()
    monkeypatch.setattr(runner_mod, "build_model_provider", lambda model: provider)
    return provider


def test_run_writes_immutable_evidence(scenario, tmp_path, patched_provider):
    run = execute_run(scenario=scenario, model=TEST_MODEL, run_number=1, root=tmp_path)
    assert run.run_id == "monday-001__fixture-model__001"
    assert run.scenario_prompt_sha256 == build_prompt(scenario).sha256
    assert run.performance.tokens_per_second == pytest.approx(179.9, abs=0.2)
    assert run.economics.total_cost_usd == pytest.approx(0.00114, abs=1e-6)

    paths = find_runs("monday-001", "fixture-model", tmp_path)
    assert len(paths) == 1

    with pytest.raises(RunExistsError):
        execute_run(scenario=scenario, model=TEST_MODEL, run_number=1, root=tmp_path)

    execute_run(
        scenario=scenario, model=TEST_MODEL, run_number=1, root=tmp_path, overwrite=True
    )


def test_transient_failure_is_retried(scenario, tmp_path, monkeypatch):
    provider = FakeModelProvider(fail_times=2, transient=True)
    monkeypatch.setattr(runner_mod, "build_model_provider", lambda model: provider)
    monkeypatch.setattr(runner_mod, "BACKOFF_SECONDS", (0.0, 0.0))
    run = execute_run(scenario=scenario, model=TEST_MODEL, run_number=1, root=tmp_path)
    assert provider.calls == 3
    assert run.response


def test_non_transient_failure_writes_no_run(scenario, tmp_path, monkeypatch):
    provider = FakeModelProvider(fail_times=1, transient=False)
    monkeypatch.setattr(runner_mod, "build_model_provider", lambda model: provider)
    with pytest.raises(ProviderError):
        execute_run(scenario=scenario, model=TEST_MODEL, run_number=1, root=tmp_path)
    assert find_runs("monday-001", "fixture-model", tmp_path) == []


def test_evaluation_scores_and_audits(legacy_scenario, evaluator_config, tmp_path, patched_provider):
    run = execute_run(scenario=legacy_scenario, model=TEST_MODEL, run_number=1, root=tmp_path)
    evaluator = _evaluator(evaluator_config.ground_truth_map)
    judge = Judge(evaluator, provider=FakeJudgeProvider("PASS"))

    evaluation = evaluate_run(
        scenario=legacy_scenario, evaluator=evaluator, run=run, judge=judge, root=tmp_path
    )
    assert evaluation.final_score == 100
    assert judge.provider.criterion_calls == len(legacy_scenario.rubric.criteria)
    # A judge that PASSes everything cannot disagree with the matchers.
    assert evaluation.disagreements == []
    # The good response really does contain the evidence the matchers look for.
    matched = {c.id for c in evaluation.deterministic_checks if c.matched}
    assert {"contoso_11_00", "churn_3_1_to_4_4", "umbrella_metrics_present"} <= matched


def test_matcher_flags_a_suspicious_fail(legacy_scenario, evaluator_config, tmp_path, patched_provider):
    run = execute_run(scenario=legacy_scenario, model=TEST_MODEL, run_number=1, root=tmp_path)
    evaluator = _evaluator(evaluator_config.ground_truth_map)
    judge = Judge(evaluator, provider=FakeJudgeProvider("FAIL"))

    evaluation = evaluate_run(
        scenario=legacy_scenario, evaluator=evaluator, run=run, judge=judge, root=tmp_path
    )
    flagged = {d.criterion_id for d in evaluation.disagreements}
    # The response plainly states 3.1% -> 4.4%, so a FAIL on churn_numbers is
    # exactly the kind of judge mistake this channel exists to surface.
    assert "churn_numbers" in flagged
    assert "release_wednesday" in flagged
    assert evaluation.final_score == 10  # noise points only


def test_leaderboard_aggregates_three_runs(
    legacy_scenario, evaluator_config, tmp_path, patched_provider
):
    evaluator = _evaluator(evaluator_config.ground_truth_map)
    labels = ["PASS", "PARTIAL", "PASS"]
    for number, label in enumerate(labels, start=1):
        run = execute_run(scenario=legacy_scenario, model=TEST_MODEL, run_number=number, root=tmp_path)
        judge = Judge(evaluator, provider=FakeJudgeProvider(label))
        evaluate_run(
            scenario=legacy_scenario, evaluator=evaluator, run=run, judge=judge, root=tmp_path
        )

    payload, summaries = build_leaderboard(
        scenario_id="monday-001",
        evaluator_id="evaluator-v0.1",
        benchmark_version="0.1",
        root=tmp_path,
    )
    assert len(summaries) == 1
    summary = summaries[0]
    assert summary.runs == 3
    # mean of the three, not best-of-N
    assert summary.maximum == 100
    assert summary.minimum < 100
    assert summary.minimum < summary.mean < summary.maximum
    assert summary.stddev > 0
    assert summary.median_ttft_ms == 310.0
    assert summary.median_cost_usd is not None

    json_path, csv_path, md_path = write_leaderboard(payload, summaries, root=tmp_path)
    assert json.loads(json_path.read_text(encoding="utf-8"))["models"][0]["rank"] == 1
    assert "monday_score" in csv_path.read_text(encoding="utf-8").splitlines()[0]
    # The public markdown must name the model and its score.
    md = md_path.read_text(encoding="utf-8")
    assert "Monday Score" in md and "Fixture Model" in md


def test_mixed_prompt_hashes_are_flagged(legacy_scenario, evaluator_config, tmp_path, patched_provider):
    evaluator = _evaluator(evaluator_config.ground_truth_map)
    for number in (1, 2):
        run = execute_run(scenario=legacy_scenario, model=TEST_MODEL, run_number=number, root=tmp_path)
        judge = Judge(evaluator, provider=FakeJudgeProvider("PASS"))
        evaluate_run(
            scenario=legacy_scenario, evaluator=evaluator, run=run, judge=judge, root=tmp_path
        )

    # Simulate a run generated against a different legacy_scenario version.
    path = find_runs("monday-001", "fixture-model", tmp_path)[1]
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["scenario_prompt_sha256"] = "0" * 64
    path.write_text(json.dumps(payload), encoding="utf-8")
    eval_path = tmp_path / "evaluations/evaluator-v0.1/monday-001/fixture-model/run-002.json"
    eval_payload = json.loads(eval_path.read_text(encoding="utf-8"))
    eval_payload["scenario_prompt_sha256"] = "0" * 64
    eval_path.write_text(json.dumps(eval_payload), encoding="utf-8")

    _, summaries = build_leaderboard(
        scenario_id="monday-001",
        evaluator_id="evaluator-v0.1",
        benchmark_version="0.1",
        root=tmp_path,
    )
    assert any("more than one prompt hash" in w for w in summaries[0].warnings)
