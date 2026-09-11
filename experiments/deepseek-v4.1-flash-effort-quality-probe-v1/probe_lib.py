"""Shared call machinery for phase 1b. One place, so nothing drifts.

Calibration and the main experiment both go through `one_call` here, which means
the request they send can only differ in the fields passed to it. The request is
assembled by the harness's own `ModelConfig` and `OpenAICompatibleProvider`, the
same code that assembles a benchmark run.

Config is identical to `deepseek-v4.1-flash-effort-probe-v1`: helmcode,
`deepseek-v4-flash`, temperature 0, no top_p, 32,000 max output tokens,
`caching: false`, no system prompt, streaming on, no tools. Retries fire on
infrastructure failures only and every attempt is recorded.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))

from mondaybench.config import load_models  # noqa: E402
from mondaybench.providers import OpenAICompatibleProvider, ProviderError  # noqa: E402

import scorers  # noqa: E402

MODEL_SLUG = "deepseek-v4.1-flash"
MAX_ATTEMPTS = 3
BACKOFF_SECONDS = (2.0, 6.0)
INFRA_STATUSES = {408, 409, 425, 429, 500, 502, 503, 504, *range(520, 528)}


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def sha(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def request_id_shape(rid: str | None) -> str:
    """Observable shape of the returned id. A description, never a cause."""
    if not rid:
        return "absent"
    if re.match(r"^chatcmpl-\d{6,}-[A-Za-z0-9]+$", rid):
        return "chatcmpl-digits-alnum"
    if re.match(r"^chatcmpl-[0-9a-f]{8,}$", rid):
        return "chatcmpl-hex"
    return "other"


def load_model():
    return load_models()[MODEL_SLUG]


def build_provider(model):
    return OpenAICompatibleProvider(
        base_url=model.base_url(), api_key=model.api_key(), stream=True, timeout=300.0
    )


def answer_keys() -> dict:
    return json.loads((HERE / "microtests" / "answer-keys.json").read_text(encoding="utf-8"))


def microtest_prompt(test_id: str) -> str:
    return (HERE / "microtests" / f"{test_id}.txt").read_bytes().decode("utf-8")


def request_fingerprint(model, effort: str | None, prompt: str) -> dict:
    """Every field that reaches the wire, for the preflight comparison."""
    extra_body = dict(model.extra_body)
    if effort is not None:
        extra_body["reasoning_effort"] = effort
    return {
        "model_slug": model.slug,
        "provider": model.provider,
        "api_style": model.api_style,
        "model_id": model.model_id,
        "endpoint": build_provider_endpoint(model),
        "prompt_bytes": len(prompt.encode("utf-8")),
        "prompt_sha256": sha(prompt),
        "system_prompt": None,
        "system_prompt_sha256": sha(""),
        "temperature": model.temperature,
        "top_p_sent": model.top_p is not None,
        "top_p": model.top_p,
        "max_output_tokens": model.max_output_tokens,
        "capabilities": dict(model.capabilities),
        "caching": extra_body.get("caching"),
        "tools_sent": False,
        "streaming": True,
        "stream_options_include_usage": True,
        "retry_max_attempts": MAX_ATTEMPTS,
        "retry_backoff_seconds": list(BACKOFF_SECONDS),
        "retry_infra_statuses": sorted(INFRA_STATUSES),
        "conversation_carry_over": False,
        "best_of_n": False,
        "quality_retries": False,
        "reasoning_effort": ("<field absent from request body>" if effort is None else effort),
    }


def build_provider_endpoint(model) -> str:
    return OpenAICompatibleProvider(base_url=model.base_url(), api_key="x")._endpoint()


def one_call(provider, model, *, test_id: str, effort: str | None, sample_id: str,
             variant: str, phase: str) -> dict:
    """One independent sample. Infrastructure retries only, all attempts logged."""
    prompt = microtest_prompt(test_id)
    key = answer_keys()[test_id]
    extra_body = dict(model.extra_body)
    if effort is not None:
        extra_body["reasoning_effort"] = effort
    generation_config = {
        "max_output_tokens": model.max_output_tokens,
        "temperature": model.temperature,
        "extra_body": extra_body,
    }
    if model.top_p is not None:
        generation_config["top_p"] = model.top_p

    record: dict = {
        "sample_id": sample_id,
        "phase": phase,
        "microtest_id": test_id,
        "variant": variant,
        "reasoning_effort_sent": effort,
        "reasoning_effort_field_present": effort is not None,
        "model_id": model.model_id,
        "provider": model.provider,
        "prompt_sha256": key["prompt_sha256"],
        "attempts": [],
    }

    for attempt in range(MAX_ATTEMPTS):
        started = now()
        try:
            result = provider.generate(
                model_id=model.model_id,
                system_prompt=None,
                user_prompt=prompt,
                generation_config=generation_config,
            )
        except ProviderError as exc:
            infra = bool(exc.transient) or (exc.status in INFRA_STATUSES)
            record["attempts"].append({
                "attempt": attempt + 1, "started_utc": started, "outcome": "error",
                "error": str(exc)[:400], "status": exc.status, "kind": exc.kind,
                "transient_per_harness": bool(exc.transient),
                "classified_infrastructure": infra,
            })
            if not infra or attempt == MAX_ATTEMPTS - 1:
                record.update({"status": "FAILED", "failure_reason": str(exc)[:400],
                               "http_status": exc.status,
                               "retries": len(record["attempts"]) - 1})
                return record
            time.sleep(BACKOFF_SECONDS[min(attempt, len(BACKOFF_SECONDS) - 1)])
            continue

        record["attempts"].append({"attempt": attempt + 1, "started_utc": started,
                                   "outcome": "ok"})
        usage = dict(result.raw_usage or {})
        details = usage.get("completion_tokens_details") or {}
        # Absent and zero are different facts. They are stored as different values.
        reported = None
        candidates = [usage.get("reasoning_tokens")]
        if isinstance(details, dict):
            candidates.append(details.get("reasoning_tokens"))
        for source in candidates:
            if source is not None:
                reported = int(source)
                break
        scored = scorers.score(result.text, key["answer"], key["answer_type"])
        record.update({
            "status": "OK",
            "timestamp_utc": started,
            "completed_utc": now(),
            "http_status": 200,
            "request_id": result.provider_request_id,
            "request_id_shape": request_id_shape(result.provider_request_id),
            "prompt_tokens": result.input_tokens,
            "input_tokens": result.input_tokens,
            "output_tokens": result.output_tokens,
            "reasoning_tokens_reported": reported,
            "reasoning_tokens_field_present": reported is not None,
            "reasoning_stream_observed": result.reasoning_stream_observed,
            "reasoning_stream_event_count": result.reasoning_stream_event_count,
            "ttft_ms": result.ttft_ms,
            "ttfa_ms": result.ttfa_ms,
            "total_latency_ms": result.total_latency_ms,
            "generation_ms": result.generation_ms,
            "finish_reason": result.finish_reason,
            "unsupported_parameters": result.unsupported_parameters,
            "raw_answer": result.text,
            "response_sha256": sha(result.text),
            "raw_usage": usage,
            "verdict": scored["verdict"],
            "parsed_answer": scored["parsed_answer"],
            "expected_answer": scored["expected_answer"],
            "answer_lines_found": scored["answer_lines_found"],
            "retries": len(record["attempts"]) - 1,
        })
        return record

    record["status"] = "FAILED"  # pragma: no cover
    return record


def append(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def print_row(record: dict) -> None:
    if record["status"] != "OK":
        print(f"{record['sample_id']:<10} {record['microtest_id']:<22} "
              f"{record['variant']:<9} FAILED retries={record.get('retries')} "
              f"{record.get('failure_reason', '')[:60]}", flush=True)
        return
    rt = record["reasoning_tokens_reported"]
    print(f"{record['sample_id']:<10} {record['microtest_id']:<22} "
          f"{record['variant']:<9} {record['verdict'][:4]:<5} "
          f"got={str(record['parsed_answer']):<10} "
          f"reas={('null' if rt is None else rt):>6} "
          f"ptok={str(record['prompt_tokens']):>4} "
          f"out={str(record['output_tokens']):>6} "
          f"ms={record['total_latency_ms']:>9.0f}", flush=True)
