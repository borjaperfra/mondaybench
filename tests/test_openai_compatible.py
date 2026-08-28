"""Payload construction for OpenAI-compatible endpoints.

The temperature case is not hypothetical: Helmcode's LiteLLM gateway forwards
`temperature` verbatim to Anthropic, which answers 400. Without the guard below,
one config line kills an entire evaluation run.
"""

from __future__ import annotations

from mondaybench.providers.openai_compatible import OpenAICompatibleProvider


def make_provider(base_url="https://api.example.com/v1"):
    return OpenAICompatibleProvider(base_url=base_url, api_key="sk-test")


def build(model_id, config, stream=False):
    return make_provider()._payload(
        model_id=model_id,
        system_prompt="You are a helpful assistant.",
        user_prompt="hello",
        generation_config=config,
        stream=stream,
    )


# --------------------------------------------------------------------------
# endpoint resolution
# --------------------------------------------------------------------------


def test_v1_suffix_is_not_duplicated():
    assert (
        make_provider("https://api.example.com/v1")._endpoint()
        == "https://api.example.com/v1/chat/completions"
    )


def test_v1_is_appended_when_missing():
    assert (
        make_provider("https://api.example.com")._endpoint()
        == "https://api.example.com/v1/chat/completions"
    )


def test_full_path_is_left_alone():
    url = "https://api.example.com/v1/chat/completions"
    assert make_provider(url)._endpoint() == url


def test_trailing_slash_is_handled():
    assert (
        make_provider("https://api.example.com/v1/")._endpoint()
        == "https://api.example.com/v1/chat/completions"
    )


# --------------------------------------------------------------------------
# temperature
# --------------------------------------------------------------------------


def test_open_model_keeps_temperature():
    payload, unsupported = build("glm5.2", {"temperature": 0, "max_output_tokens": 4000})
    assert payload["temperature"] == 0
    assert unsupported == []


def test_claude_through_a_gateway_drops_temperature():
    # Same request shape, but the gateway fronts a model that rejects it.
    payload, unsupported = build("claude-opus-5", {"temperature": 0, "max_output_tokens": 4000})
    assert "temperature" not in payload
    assert unsupported == ["temperature"]


def test_other_rejecting_models_are_covered():
    for model_id in ("claude-sonnet-5", "claude-opus-4-8", "claude-fable-5"):
        payload, unsupported = build(model_id, {"temperature": 0, "max_output_tokens": 100})
        assert "temperature" not in payload, model_id
        assert unsupported == ["temperature"], model_id


def test_claude_haiku_45_still_accepts_temperature():
    # Haiku 4.5 predates the removal, so dropping it would be wrong.
    payload, unsupported = build("claude-haiku-4-5", {"temperature": 0, "max_output_tokens": 100})
    assert payload["temperature"] == 0
    assert unsupported == []


def test_unset_temperature_is_simply_absent():
    payload, unsupported = build("glm5.2", {"temperature": None, "max_output_tokens": 4000})
    assert "temperature" not in payload
    assert unsupported == []


# --------------------------------------------------------------------------
# other payload fields
# --------------------------------------------------------------------------


def test_system_prompt_comes_first():
    payload, _ = build("glm5.2", {"max_output_tokens": 100})
    assert payload["messages"][0]["role"] == "system"
    assert payload["messages"][1]["role"] == "user"


def test_max_tokens_is_mapped():
    payload, _ = build("glm5.2", {"max_output_tokens": 4000})
    assert payload["max_tokens"] == 4000


def test_json_schema_becomes_response_format():
    schema = {"type": "object", "properties": {"result": {"type": "string"}}}
    payload, _ = build("glm5.2", {"max_output_tokens": 100, "response_json_schema": schema})
    assert payload["response_format"]["type"] == "json_schema"
    assert payload["response_format"]["json_schema"]["strict"] is True
    assert payload["response_format"]["json_schema"]["schema"] == schema


def test_streaming_requests_usage():
    payload, _ = build("glm5.2", {"max_output_tokens": 100}, stream=True)
    assert payload["stream"] is True
    assert payload["stream_options"] == {"include_usage": True}


def test_extra_body_is_merged():
    payload, _ = build("glm5.2", {"max_output_tokens": 100, "extra_body": {"top_k": 5}})
    assert payload["top_k"] == 5


# --------------------------------------------------------------------------
# Reasoning streams
# --------------------------------------------------------------------------
#
# NaN's glm5.3-flash streams its thinking in `reasoning_content` deltas and its
# answer in `content` deltas. On the first calibration sweep it spent all 4,000
# output tokens reasoning and emitted no `content` at all, and the provider
# reported only "stream produced no content" - true but useless. These tests
# pin the distinction between a budget exhausted by thinking and a dead stream.

import json

import httpx
import pytest

from mondaybench.providers.base import ProviderError


def _sse(events: list[dict]) -> bytes:
    body = "".join(f"data: {json.dumps(e)}\n\n" for e in events)
    return (body + "data: [DONE]\n\n").encode("utf-8")


def _delta(**fields) -> dict:
    return {"choices": [{"index": 0, "delta": fields}]}


class _StreamCtx:
    """`client.stream(...)` is used as a context manager, so the stub must be one."""

    def __init__(self, response):
        self._response = response

    def __enter__(self):
        return self._response

    def __exit__(self, *a):
        return False


def _stub_client(raw: bytes, monkeypatch):
    class StubClient:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def stream(self, method, url, headers=None, json=None):
            request = httpx.Request(method, url)
            return _StreamCtx(httpx.Response(200, content=raw, request=request))

    monkeypatch.setattr(httpx, "Client", StubClient)


def _provider_with(events: list[dict], monkeypatch):
    """Point a provider at a stubbed SSE stream."""
    _stub_client(_sse(events), monkeypatch)
    return make_provider()


def test_reasoning_deltas_are_excluded_from_the_answer(monkeypatch):
    events = [
        _delta(role="assistant"),
        _delta(reasoning_content="The user wants a briefing. Let me think..."),
        _delta(content="Contoso first."),
        {"choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]},
    ]
    provider = _provider_with(events, monkeypatch)
    result = provider.generate(
        model_id="glm5.3-flash",
        system_prompt=None,
        user_prompt="x",
        generation_config={"max_output_tokens": 16000, "stream": True},
    )
    # The thinking must never reach the scored response.
    assert result.text == "Contoso first."
    assert "Let me think" not in result.text
    assert result.finish_reason == "stop"


def test_the_alternate_reasoning_field_is_also_recognised(monkeypatch):
    events = [
        _delta(reasoning="thinking hard"),
        _delta(content="answer"),
    ]
    provider = _provider_with(events, monkeypatch)
    result = provider.generate(
        model_id="glm5.3-flash",
        system_prompt=None,
        user_prompt="x",
        generation_config={"max_output_tokens": 16000, "stream": True},
    )
    assert result.text == "answer"


def test_reasoning_but_no_answer_reports_budget_exhaustion(monkeypatch):
    events = [
        _delta(reasoning_content="a very long chain of thought" * 20),
        {"choices": [{"index": 0, "delta": {}, "finish_reason": "length"}]},
    ]
    provider = _provider_with(events, monkeypatch)
    with pytest.raises(ProviderError) as excinfo:
        provider.generate(
            model_id="glm5.3-flash",
            system_prompt=None,
            user_prompt="x",
            generation_config={"max_output_tokens": 4000, "stream": True},
        )
    message = str(excinfo.value)
    # The error must name the cause and the fix, not just the symptom.
    assert "reasoning but no" in message
    assert "max_output_tokens" in message
    assert "finish_reason=length" in message


def test_a_genuinely_empty_stream_is_still_a_plain_failure(monkeypatch):
    events = [_delta(role="assistant"), {"choices": [{"index": 0, "delta": {}}]}]
    provider = _provider_with(events, monkeypatch)
    with pytest.raises(ProviderError, match="stream produced no content"):
        provider.generate(
            model_id="glm5.3-flash",
            system_prompt=None,
            user_prompt="x",
            generation_config={"max_output_tokens": 16000, "stream": True},
        )


def test_malformed_sse_frame_does_not_abort_a_valid_generation(monkeypatch):
    raw = (
        b"data: {oops not json\n\n"
        b'data: {"choices":[{"delta":{"content":"ok"}}]}\n\n'
        b"data: [DONE]\n\n"
    )
    _stub_client(raw, monkeypatch)
    provider = make_provider()
    result = provider.generate(
        model_id="glm5.2",
        system_prompt=None,
        user_prompt="x",
        generation_config={"max_output_tokens": 100, "stream": True},
    )
    assert result.text == "ok"


def test_ttft_counts_the_first_reasoning_token_not_the_first_answer(monkeypatch):
    """Calibration reported 1,291 tok/s for a model that thought for two minutes.

    Cause: TTFT was marked on the first *visible* token, so the whole reasoning
    phase fell outside the throughput window while its tokens were still counted.
    TTFT must be the first token of any kind; time-to-first-answer is separate.
    """
    events = [
        _delta(reasoning_content="thinking"),
        _delta(reasoning_content=" more"),
        _delta(content="the answer"),
    ]
    provider = _provider_with(events, monkeypatch)
    result = provider.generate(
        model_id="glm5.3-flash",
        system_prompt=None,
        user_prompt="x",
        generation_config={"max_output_tokens": 16000, "stream": True},
    )
    assert result.ttft_ms is not None and result.ttfa_ms is not None
    # The answer cannot arrive before the first token.
    assert result.ttft_ms <= result.ttfa_ms


def test_non_thinking_model_has_equal_ttft_and_ttfa(monkeypatch):
    provider = _provider_with([_delta(content="hello")], monkeypatch)
    result = provider.generate(
        model_id="gemma4",
        system_prompt=None,
        user_prompt="x",
        generation_config={"max_output_tokens": 100, "stream": True},
    )
    assert result.ttft_ms == result.ttfa_ms


def test_throughput_is_not_inflated_by_a_late_answer():
    """A direct check on the arithmetic, independent of timing jitter."""
    from mondaybench.providers.base import GenerationResult

    # 8,320 output tokens (7,250 of them reasoning) produced over 173 seconds.
    honest = GenerationResult(text="a", output_tokens=8320, total_latency_ms=173000.0)
    assert honest.tokens_per_second() == pytest.approx(48.1, abs=0.1)

    # The old bug: window measured from the first visible token only (13.3s).
    inflated = GenerationResult(
        text="a", output_tokens=8320, total_latency_ms=173000.0, generation_ms=13300.0
    )
    assert inflated.tokens_per_second() > 600  # what calibration wrongly reported
