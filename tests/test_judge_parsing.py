"""The judge is a model, so its output format is untrusted input.

These tests cover what judges actually do wrong: fence the JSON, wrap it in
prose, invent an enum value, or omit a field.
"""

from __future__ import annotations

import pytest

from mondaybench.config import EvaluatorConfig
from mondaybench.judge import Judge, JudgeError, extract_json
from mondaybench.providers.base import GenerationResult, ModelProvider


class ScriptedProvider(ModelProvider):
    """Returns canned texts in order, so judge parsing can be tested offline."""

    def __init__(self, texts: list[str]):
        self.texts = list(texts)
        self.prompts: list[str] = []

    def generate(self, *, model_id, system_prompt, user_prompt, generation_config):
        self.prompts.append(user_prompt)
        if not self.texts:
            raise AssertionError("ScriptedProvider ran out of canned responses")
        return GenerationResult(
            text=self.texts.pop(0),
            input_tokens=100,
            output_tokens=20,
            total_latency_ms=1.0,
        )


def make_judge(texts: list[str]) -> Judge:
    config = EvaluatorConfig(
        id="evaluator-test",
        provider="test",
        api_style="anthropic",
        model_id="test-judge",
        model_env=None,
        base_url_env=None,
        api_key_env=None,
        temperature=0,
        effort="low",
        max_output_tokens=1000,
        require_evidence=True,
        ground_truth_map={},
    )
    return Judge(config, provider=ScriptedProvider(texts))


# --------------------------------------------------------------------------
# extract_json
# --------------------------------------------------------------------------


def test_clean_json():
    assert extract_json('{"result": "PASS"}') == {"result": "PASS"}


def test_markdown_fenced_json():
    text = '```json\n{"result": "PARTIAL", "evidence": "x"}\n```'
    assert extract_json(text)["result"] == "PARTIAL"


def test_bare_fenced_json():
    assert extract_json('```\n{"result": "FAIL"}\n```')["result"] == "FAIL"


def test_json_wrapped_in_prose():
    text = 'Sure! Here is my assessment:\n\n{"result": "PASS", "reason": "ok"}\n\nHope that helps.'
    assert extract_json(text)["result"] == "PASS"


def test_json_with_trailing_commentary_after_fence():
    text = '```json\n{"result": "PASS"}\n```\n\nLet me know if you need more detail.'
    assert extract_json(text)["result"] == "PASS"


def test_no_json_at_all_raises():
    with pytest.raises(JudgeError, match="no JSON object"):
        extract_json("I am not able to evaluate this.")


def test_single_object_is_recovered_from_a_wrapping_array():
    # Judges occasionally wrap the verdict in a list. One object is recoverable.
    assert extract_json('[{"result": "PASS"}]')["result"] == "PASS"


def test_ambiguous_multi_object_array_raises_rather_than_picking_one():
    with pytest.raises(JudgeError, match="no JSON object"):
        extract_json('[{"result": "PASS"}, {"result": "FAIL"}]')


# --------------------------------------------------------------------------
# criterion verdicts
# --------------------------------------------------------------------------


def test_criterion_verdict_from_fenced_json(rubric):
    criterion = rubric.criteria_by_id["contoso_action"]
    judge = make_judge(['```json\n{"result":"PASS","evidence":"quote","reason":"why"}\n```'])
    verdict = judge.judge_criterion(criterion, {}, "some response")
    assert verdict.result == "PASS"
    assert verdict.evidence == "quote"
    assert judge.stats.calls == 1
    assert judge.stats.repairs == 0


def test_lowercase_label_is_normalized(rubric):
    criterion = rubric.criteria_by_id["contoso_action"]
    judge = make_judge(['{"result":"partial","evidence":"q","reason":"r"}'])
    assert judge.judge_criterion(criterion, {}, "r").result == "PARTIAL"


def test_invalid_enum_raises(rubric):
    criterion = rubric.criteria_by_id["contoso_action"]
    judge = make_judge(['{"result":"EXCELLENT","evidence":"q","reason":"r"}'])
    with pytest.raises(JudgeError, match="invalid label"):
        judge.judge_criterion(criterion, {}, "r")


def test_missing_optional_fields_are_none(rubric):
    criterion = rubric.criteria_by_id["contoso_action"]
    judge = make_judge(['{"result":"FAIL"}'])
    verdict = judge.judge_criterion(criterion, {}, "r")
    assert verdict.result == "FAIL"
    assert verdict.evidence is None
    assert verdict.reason is None


def test_one_repair_attempt_then_success(rubric):
    criterion = rubric.criteria_by_id["contoso_action"]
    judge = make_judge(["I cannot produce JSON.", '{"result":"PASS","evidence":"q","reason":"r"}'])
    verdict = judge.judge_criterion(criterion, {}, "r")
    assert verdict.result == "PASS"
    assert judge.stats.repairs == 1
    assert judge.stats.calls == 2
    # the second prompt must carry the repair instruction
    assert "not valid JSON" in judge.provider.prompts[1]


def test_two_failures_raise_rather_than_inventing_a_result(rubric):
    criterion = rubric.criteria_by_id["contoso_action"]
    judge = make_judge(["nope", "still nope"])
    with pytest.raises(JudgeError, match="unusable after one repair"):
        judge.judge_criterion(criterion, {}, "r")


# --------------------------------------------------------------------------
# noise judge
# --------------------------------------------------------------------------


def test_noise_verdict_orders_items_by_rubric(rubric):
    actions = rubric.noise.false_actions
    payload = {
        "items": [
            {"id": a.id, "triggered": a.id == "lunch", "evidence": "e" if a.id == "lunch" else ""}
            for a in reversed(actions)
        ]
    }
    import json

    judge = make_judge([json.dumps(payload)])
    verdict = judge.judge_noise(actions, "response")
    assert [item.id for item in verdict.items] == [a.id for a in actions]
    assert verdict.items[[a.id for a in actions].index("lunch")].triggered is True


def test_noise_judge_omitting_a_category_raises(rubric):
    actions = rubric.noise.false_actions
    judge = make_judge(['{"items":[{"id":"lunch","triggered":false,"evidence":""}]}'])
    with pytest.raises(JudgeError, match="omitted categories"):
        judge.judge_noise(actions, "response")


def test_noise_judge_without_items_raises(rubric):
    judge = make_judge(['{"result":"PASS"}'])
    with pytest.raises(JudgeError, match="no items list"):
        judge.judge_noise(rubric.noise.false_actions, "response")


# --------------------------------------------------------------------------
# penalty judge
# --------------------------------------------------------------------------


def test_empty_violations_is_valid():
    judge = make_judge(['{"violations":[]}'])
    assert judge.judge_penalties({}, "response").violations == []


def test_missing_violations_field_means_none():
    judge = make_judge(["{}"])
    assert judge.judge_penalties({}, "response").violations == []


def test_penalty_violation_is_parsed():
    judge = make_judge(
        '{"violations":[{"type":"PROHIBITED_ACTION","evidence":"sends pricing","reason":"r"}]}'.split(
            "\n"
        )
    )
    violations = judge.judge_penalties({}, "response").violations
    assert len(violations) == 1
    assert violations[0].type == "PROHIBITED_ACTION"


def test_invalid_penalty_type_raises():
    judge = make_judge(['{"violations":[{"type":"BAD_VIBES","evidence":"e","reason":"r"}]}'])
    with pytest.raises(JudgeError, match="invalid type"):
        judge.judge_penalties({}, "response")


# --------------------------------------------------------------------------
# Regression: the penalty judge must see the evidence, not just the answer key
# --------------------------------------------------------------------------


def test_penalty_prompt_includes_the_source_material():
    """Calibration caught four false MATERIAL_HALLUCINATIONs in one run.

    Cause: the judge was shown only `ground-truth.yaml`, which summarises the
    correct conclusions. Details the model correctly quoted from Slack and email
    were absent from that summary, so they read as invented - capping penalties
    at -20 for a response that fabricated nothing.
    """
    from mondaybench.judge import penalty_prompt

    sources = "--- emails.md ---\n- New ARR closed: EUR 31k"
    prompt = penalty_prompt({"current_state": {"acme_incident": "resolved"}}, sources, "resp")

    # Collapse wrapping so the assertions are about content, not line breaks.
    flat = " ".join(prompt.split())
    assert "New ARR closed: EUR 31k" in flat
    assert "authority on what is supported" in flat
    # And the ground truth must be explicitly demoted from "list of permitted facts".
    assert "not an exhaustive list of permitted facts" in flat
    # The judge must be told to go looking before flagging.
    assert "quoting or paraphrasing a detail found there is never a hallucination" in flat


def test_penalty_prompt_still_carries_the_ground_truth():
    from mondaybench.judge import penalty_prompt

    prompt = penalty_prompt({"current_state": {"acme_incident": "resolved"}}, "sources", "resp")
    assert "acme_incident" in prompt
    assert "MATERIAL_HALLUCINATION" in prompt
    assert "PROHIBITED_ACTION" in prompt
    assert "MAJOR_CONTRADICTION" in prompt
