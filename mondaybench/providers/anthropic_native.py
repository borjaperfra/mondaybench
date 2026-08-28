"""Anthropic Messages API provider, used for the evaluator-v0.1 judge.

This is a second provider class because the Anthropic API genuinely differs
from the OpenAI-compatible shape, not for taste:

* `temperature` is rejected with a 400 on Opus 5 / Sonnet 5 and the 4.6+ family,
  so a config asking for `temperature: 0` cannot be honoured. The parameter is
  dropped and reported in `unsupported_parameters` rather than silently ignored.
* Thinking is adaptive; depth is controlled by `output_config.effort`.
* Structured output uses `output_config.format`, which removes most of the
  JSON-parsing failure modes an OpenAI-compatible judge has.

Never route Claude through an OpenAI-compatible shim - use this class.
"""

from __future__ import annotations

import time
from typing import Any

from .base import GenerationResult, ModelProvider, ProviderError

# Models that reject `temperature` outright (400). Kept as prefixes because
# these families have no dated suffixes in their current IDs.
NO_TEMPERATURE_MODELS = (
    "claude-fable-5",
    "claude-mythos-5",
    "claude-opus-5",
    "claude-opus-4-8",
    "claude-opus-4-7",
    "claude-sonnet-5",
)


def rejects_temperature(model_id: str) -> bool:
    return any(model_id.startswith(prefix) for prefix in NO_TEMPERATURE_MODELS)


class AnthropicProvider(ModelProvider):
    name = "anthropic"

    def __init__(self, *, api_key: str | None = None, timeout: float = 300.0):
        try:
            import anthropic
        except ImportError as exc:  # pragma: no cover - dependency is declared
            raise ProviderError(
                "the `anthropic` package is required for the Anthropic judge "
                "(pip install anthropic)"
            ) from exc
        self._anthropic = anthropic
        # A bare client also resolves an `ant auth login` profile, so an unset
        # ANTHROPIC_API_KEY is not necessarily an error.
        self._client = (
            anthropic.Anthropic(api_key=api_key, timeout=timeout)
            if api_key
            else anthropic.Anthropic(timeout=timeout)
        )

    def generate(
        self,
        *,
        model_id: str,
        system_prompt: str | None,
        user_prompt: str,
        generation_config: dict[str, Any],
    ) -> GenerationResult:
        unsupported: list[str] = []

        kwargs: dict[str, Any] = {
            "model": model_id,
            "max_tokens": generation_config.get("max_output_tokens") or 4000,
            "messages": [{"role": "user", "content": user_prompt}],
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        if generation_config.get("temperature") is not None:
            if rejects_temperature(model_id):
                unsupported.append("temperature")
            else:
                kwargs["temperature"] = generation_config["temperature"]

        output_config: dict[str, Any] = {}
        if generation_config.get("effort"):
            output_config["effort"] = generation_config["effort"]
        if generation_config.get("response_json_schema"):
            output_config["format"] = {
                "type": "json_schema",
                "schema": generation_config["response_json_schema"],
            }
        if output_config:
            kwargs["output_config"] = output_config

        started = time.perf_counter()
        try:
            message = self._client.messages.create(**kwargs)
        except self._anthropic.APIStatusError as exc:
            raise ProviderError(
                f"HTTP {exc.status_code} from Anthropic: {str(exc)[:400]}",
                transient=exc.status_code in {408, 409, 429} or exc.status_code >= 500,
                status=exc.status_code,
            ) from exc
        except self._anthropic.APIConnectionError as exc:
            raise ProviderError(f"connection error: {exc}", transient=True) from exc
        elapsed_ms = round((time.perf_counter() - started) * 1000, 1)

        text = "".join(
            block.text for block in message.content if getattr(block, "type", None) == "text"
        )
        if not text.strip():
            raise ProviderError(
                f"Anthropic returned no text content (stop_reason={message.stop_reason})"
            )

        usage = message.usage
        raw_usage = usage.model_dump() if hasattr(usage, "model_dump") else dict(usage or {})

        return GenerationResult(
            text=text,
            input_tokens=getattr(usage, "input_tokens", None),
            output_tokens=getattr(usage, "output_tokens", None),
            reasoning_tokens=None,  # billed inside output_tokens; not reported separately
            ttft_ms=None,  # non-streaming call
            total_latency_ms=elapsed_ms,
            generation_ms=None,
            provider_request_id=getattr(message, "id", None),
            finish_reason=message.stop_reason,
            raw_usage=raw_usage,
            unsupported_parameters=unsupported,
            system_prompt_sent=bool(system_prompt),
        )
