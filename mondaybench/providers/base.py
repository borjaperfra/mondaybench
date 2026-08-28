"""The provider interface. Deliberately one method wide."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class ProviderError(Exception):
    """A model call failed in a way that must not produce a benchmark run.

    `kind` classifies the failure so the caller does not have to read the
    message. Two of them look alike and are not:

    * `truncated_by_budget` — `finish_reason=length` with no answer. The model
      hit its ceiling mid-thought; raising `max_output_tokens` is the fix.
    * `empty_final_answer` — the provider closed the stream cleanly
      (`finish_reason=stop`) having emitted reasoning and no answer. Nothing was
      truncated, so a bigger budget changes nothing, and suggesting one sends
      the reader after a setting that is not the problem.
    """

    def __init__(
        self,
        message: str,
        *,
        transient: bool = False,
        status: int | None = None,
        kind: str = "error",
    ):
        super().__init__(message)
        self.transient = transient
        self.status = status
        self.kind = kind


@dataclass
class GenerationResult:
    text: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    reasoning_tokens: int | None = None
    # TTFT is the first token of ANY kind the API emits, reasoning included -
    # that is what the API-level metric means. For a thinking model the first
    # *visible* token can arrive minutes later, so that is reported separately
    # as time-to-first-answer rather than conflated with TTFT.
    ttft_ms: float | None = None
    ttfa_ms: float | None = None
    total_latency_ms: float = 0.0
    generation_ms: float | None = None
    provider_request_id: str | None = None
    finish_reason: str | None = None
    raw_usage: dict[str, Any] = field(default_factory=dict)
    # Parameters the config asked for that this API rejects or does not accept.
    unsupported_parameters: list[str] = field(default_factory=list)
    system_prompt_sent: bool = True

    def tokens_per_second(self) -> float | None:
        """Output throughput over the window in which the tokens were produced.

        `output_tokens` includes reasoning tokens, so the window must start at
        the first token of any kind. Measuring from the first *visible* token
        instead produced absurd figures during calibration - 1,291 tok/s for a
        model that spent two minutes thinking - because the reasoning tokens
        were counted but the time spent producing them was not.
        """
        if not self.output_tokens:
            return None
        window_ms = self.generation_ms if self.generation_ms else self.total_latency_ms
        if not window_ms or window_ms <= 0:
            return None
        return round(self.output_tokens / (window_ms / 1000.0), 1)


class ModelProvider:
    """Generate one completion. Implementations must not retry silently."""

    name = "base"

    def generate(
        self,
        *,
        model_id: str,
        system_prompt: str | None,
        user_prompt: str,
        generation_config: dict[str, Any],
    ) -> GenerationResult:
        raise NotImplementedError
