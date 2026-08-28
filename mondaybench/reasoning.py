"""Did the provider actually deliver the reasoning the run was supposed to use?

`monday-002/qwen3.8-flash/run-002` scored 66.5 against 93.0 and 100.0 for the
same model on the same prompt. The audit found why: it came back with **zero
reasoning tokens** where the other two spent 42,808 and 30,342, in 19.6 seconds
against 380 and 285, with a different input token count for byte-identical
input. The provider served a non-thinking path, and the harness could not tell,
because `generation.reasoning_enabled` was copied out of `models.yaml` - a
*declared capability*, not an observation.

This module draws that distinction. `reasoning_requested` comes from the
configuration; `reasoning_delivered` comes only from the response.

## Why "requested" is derived from the model config

For the OpenAI-compatible providers used here, thinking is not a parameter we
send: these models think by default and there is no flag to set. So the
effective configuration's *intent* is exactly what `capabilities.reasoning`
declares, and that is what `reasoning_requested` records. It is a statement
about the regime a run is supposed to belong to, never evidence that the regime
was honoured. If a provider is added later that takes an explicit reasoning
parameter, put it in `extra_body` and extend `requested_from_config`.

## The four states, and why UNOBSERVABLE exists

Zero reasoning tokens means nothing unless the provider actually reports them.
Inventing a verdict from a missing field would be exactly the error this module
exists to prevent, so an unreported signal is `UNOBSERVABLE` and never
`NOT_DELIVERED`. A run in that state is not silently dropped either: it is
surfaced so a human decides.

## Why one counter is not enough

**`usage.reasoning_tokens == 0` does not universally mean "no reasoning".**
MIMO v2.5 streams a thinking phase - 139 to 162 seconds of it on monday-002 -
and then reports zero reasoning tokens. Trusting the counter alone would have
recorded six official runs as non-reasoning while the model was demonstrably
thinking, and would have left the model outside the very guard this module
provides.

So delivery is established by whichever of three signals is available, in
descending order of directness:

1. `explicit_reasoning_tokens` - the provider counted them.
2. `explicit_reasoning_stream` - the adapter saw `reasoning_content` /
   `reasoning` deltas and recorded how many. Structural only; no content is
   ever stored.
3. `derived_pre_answer_stream` - reconstructed from a run's own timings, for
   runs written before the adapter counted stream events.

Signal 3 is *not* "the response was slow". In this codebase `ttft_ms` is set by
the first non-empty `reasoning_content`/`reasoning` delta **or** the first
non-empty `content` delta, and by nothing else - role-only deltas, `usage`
events and `id` events never touch it. `ttfa_ms` is set only by the first
`content` delta. A gap between the two is therefore structural evidence that
reasoning deltas arrived first, not an inference from latency. A conservative
threshold still applies, because the value is a reconstruction rather than
something the adapter asserted at the time, and because a future adapter could
define these fields differently.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Literal

ReasoningStatus = Literal["DELIVERED", "NOT_DELIVERED", "NOT_REQUESTED", "UNOBSERVABLE"]

#: The qualification reason recorded when a reasoning run comes back without it.
REASONING_NOT_DELIVERED = "REASONING_NOT_DELIVERED"


def requested_from_config(capabilities: dict[str, Any], extra_body: dict[str, Any]) -> bool:
    """Whether this model's runs are supposed to be in the reasoning regime.

    `capabilities.reasoning` is the declaration. `extra_body` wins where a
    provider does take an explicit switch, so turning thinking off in config
    also turns off the expectation - otherwise every run would be invalid.
    """
    for key in ("reasoning", "thinking", "enable_thinking"):
        if key in extra_body:
            value = extra_body[key]
            if isinstance(value, bool):
                return value
            if isinstance(value, dict):
                # e.g. {"thinking": {"type": "disabled"}}
                return str(value.get("type", "")).lower() not in {"disabled", "off", "none"}
    return bool(capabilities.get("reasoning", False))


def _reported_reasoning_tokens(run: Any) -> int | None:
    """Reasoning tokens as the *provider* reported them, or None if it did not.

    Checked in three places because providers disagree about where it lives.
    None here means "no signal", which is materially different from zero.
    """
    usage = getattr(run, "usage", None)
    if usage is not None and getattr(usage, "reasoning_tokens", None) is not None:
        return int(usage.reasoning_tokens)

    metadata = getattr(run, "provider_metadata", None)
    raw = dict(getattr(metadata, "raw_usage", {}) or {}) if metadata is not None else {}
    details = raw.get("completion_tokens_details") or {}
    if isinstance(details, dict) and details.get("reasoning_tokens") is not None:
        return int(details["reasoning_tokens"])
    if raw.get("reasoning_tokens") is not None:
        return int(raw["reasoning_tokens"])
    return None


def was_requested(run: Any) -> bool:
    """Read the request side off a run, old or new.

    Runs written before this module carry only `reasoning_enabled`, which held
    the same declared capability. Reading it keeps every historical run
    classifiable without rewriting a single byte of it.
    """
    generation = getattr(run, "generation", None)
    if generation is None:
        return False
    explicit = getattr(generation, "reasoning_requested", None)
    if explicit is not None:
        return bool(explicit)
    return bool(getattr(generation, "reasoning_enabled", False))


#: Smallest TTFT->TTFA gap accepted as evidence of a pre-answer reasoning
#: stream. Across all 43 official runs the gap is bimodal: exactly 0.0 ms when
#: the first delta was the answer, and 16,500 ms or more when it was not. The
#: threshold sits in an empty band more than four orders of magnitude wide, so
#: it is not a tuned parameter - it is there to absorb rounding and to refuse
#: anything that could plausibly be buffering rather than generation.
PRE_ANSWER_STREAM_MIN_MS = 1000.0


def _stream_events(run: Any) -> tuple[bool | None, int | None]:
    """Whether the adapter saw reasoning deltas, and how many. None = unrecorded."""
    block = getattr(run, "reasoning", None)
    if block is None:
        return None, None
    return getattr(block, "stream_observed", None), getattr(block, "stream_event_count", None)


def _pre_answer_gap_ms(run: Any) -> float | None:
    """Milliseconds of non-content stream before the first answer token.

    None when either timing is missing, so a run that cannot be measured is
    never scored as if it had been.
    """
    performance = getattr(run, "performance", None)
    if performance is None:
        return None
    ttft, ttfa = getattr(performance, "ttft_ms", None), getattr(performance, "ttfa_ms", None)
    if ttft is None or ttfa is None:
        return None
    return ttfa - ttft


def delivery_evidence(run: Any) -> tuple[str | None, int | None]:
    """Which signal, if any, shows this run generated a reasoning phase.

    Ordered most direct first. Returns (evidence_kind, reported_tokens); the
    kind is None when nothing establishes delivery, which is *not* the same as
    establishing that no reasoning happened.
    """
    tokens = _reported_reasoning_tokens(run)
    if tokens is not None and tokens > 0:
        return "explicit_reasoning_tokens", tokens

    observed, count = _stream_events(run)
    if observed:
        return "explicit_reasoning_stream", tokens

    gap = _pre_answer_gap_ms(run)
    if gap is not None and gap >= PRE_ANSWER_STREAM_MIN_MS:
        return "derived_pre_answer_stream", tokens

    return None, tokens


def classify(run: Any) -> tuple[ReasoningStatus, int | None]:
    """Return the reasoning status of a run and the token count behind it."""
    return classify_detailed(run)[:2]


def classify_detailed(run: Any) -> tuple[ReasoningStatus, int | None, str | None]:
    """Status, reported token count, and the evidence the status rests on.

    Delivery is an observation, so it is settled before the request side is
    consulted: a model that demonstrably thought is DELIVERED whether or not
    the configuration expected it. That is how MIMO v2.5 - which streams a
    thinking phase and then reports zero tokens - is classified correctly
    without rewriting the six historical runs that recorded it.
    """
    evidence, tokens = delivery_evidence(run)
    if evidence is not None:
        return "DELIVERED", tokens, evidence

    if not was_requested(run):
        return "NOT_REQUESTED", tokens, None

    # Requested, and nothing shows it happened. Only a provider that positively
    # reported zero counts as an observed absence; silence stays UNOBSERVABLE.
    observed, _ = _stream_events(run)
    if tokens == 0 or observed is False:
        return "NOT_DELIVERED", tokens, None
    return "UNOBSERVABLE", tokens, None


def disqualifies(status: ReasoningStatus) -> bool:
    """Only a positively observed absence disqualifies a run.

    `UNOBSERVABLE` deliberately does not: refusing a run because a provider is
    quiet about its telemetry would invent evidence.
    """
    return status == "NOT_DELIVERED"


# --------------------------------------------------------------------------
# Effective-configuration fingerprint
# --------------------------------------------------------------------------

EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()


def system_prompt_sha256(system_prompt: str | None) -> str:
    """Hash of the exact system prompt text.

    A run with no system prompt hashes the empty string rather than storing
    null, so the field is always comparable and never ambiguous. `None` as a
    stored value would be indistinguishable from "we forgot to record it".
    """
    return hashlib.sha256((system_prompt or "").encode("utf-8")).hexdigest()


def generation_config_sha256(
    *,
    provider: str,
    model_id: str,
    temperature: float | None,
    top_p: float | None,
    max_output_tokens: int,
    reasoning_requested: bool,
    reasoning_mode: str | None,
    reasoning_effort: str | None,
    extra_body: dict[str, Any] | None,
    system_prompt_hash: str,
) -> str:
    """Fingerprint of everything that materially shapes a generation.

    Two runs sharing this hash were asked for under the same effective
    configuration; that is the whole claim. Nothing about the *response* enters
    it - no timestamps, no request ids, no token counts - so it stays a property
    of the request and can be compared across a battery.
    """
    canonical = {
        "provider": provider,
        "model_id": model_id,
        "temperature": temperature,
        "top_p": top_p,
        "max_output_tokens": max_output_tokens,
        "reasoning_requested": reasoning_requested,
        "reasoning_mode": reasoning_mode,
        "reasoning_effort": reasoning_effort,
        "extra_body": extra_body or {},
        "system_prompt_sha256": system_prompt_hash,
    }
    blob = json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()
