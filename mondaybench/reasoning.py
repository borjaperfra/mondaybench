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


def classify(run: Any) -> tuple[ReasoningStatus, int | None]:
    """Return the reasoning status of a run and the token count behind it."""
    tokens = _reported_reasoning_tokens(run)
    if not was_requested(run):
        return "NOT_REQUESTED", tokens
    if tokens is None:
        return "UNOBSERVABLE", None
    return ("DELIVERED" if tokens > 0 else "NOT_DELIVERED"), tokens


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
