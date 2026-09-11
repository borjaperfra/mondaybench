"""Phase 1 of the reasoning-effort experiment: baseline vs reasoning_effort=high.

    python run_probe.py --preflight     writes preflight.json + probe-config.json
    python run_probe.py --execute       runs the 60 samples in the frozen order
    python run_probe.py --sentinel      runs the 5 invalid-value sentinel calls

NOT a MondayBench run. It touches no scenario, no battery, no leaderboard and no
evaluation. Everything it writes lives under this directory.

## What is controlled

Every field that reaches the wire is taken from `models.yaml`'s
`deepseek-v4.1-flash` entry through the harness's own `ModelConfig` and its own
`OpenAICompatibleProvider`, so the request is assembled by the same code that
assembles a benchmark run. The single experimental variable is the
`reasoning_effort` field in the request body: absent for `baseline`, `"high"`
for `high`.

## Two deliberate departures from a benchmark run, both constant across variants

1. **No system prompt.** The earlier probe sent none, and this experiment
   continues the comparison it started. A benchmark run sends the harness
   default ("You are a helpful assistant."). Held identical across variants, so
   it cannot explain a baseline/high difference.
2. **Streaming on.** The earlier probe was blocking, which is why it could not
   observe reasoning stream events at all. Streaming is what makes
   `reasoning_stream_observed` measurable, and preserving that signal is the
   point. Held identical across variants. It does mean the token counts here are
   not directly comparable with the earlier blocking probe's numbers.

## Retries

Infrastructure only, and every attempt is recorded. The harness's own transient
set (408/409/425/429/500/502/503/504 plus network errors) is honoured, extended
with the Cloudflare edge codes 520-527 because the earlier probe saw a 524 and
those are unambiguously edge failures rather than model behaviour. A response
that merely scores badly is never retried. If a slot exhausts its attempts it is
recorded as FAILED and excluded from the statistics, never silently replaced.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mondaybench.config import load_models  # noqa: E402
from mondaybench.providers import OpenAICompatibleProvider, ProviderError  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scorer  # noqa: E402

HERE = Path(__file__).resolve().parent
MODEL_SLUG = "deepseek-v4.1-flash"

N_PER_VARIANT = 30
VARIANTS = {"baseline": None, "high": "high"}   # variant -> reasoning_effort value
SENTINEL_VALUE = "banana"
N_SENTINEL = 5

ORDER_SEED = 20260911          # frozen assignment order
BOOTSTRAP_SEED = 424242        # recorded here, used by analyze.py
SCORER_SPEC = "strict-distinct-times + last-time robustness check, v1"

MAX_ATTEMPTS = 3
BACKOFF_SECONDS = (2.0, 6.0)
# The harness's transient set, plus the Cloudflare edge range.
INFRA_STATUSES = {408, 409, 425, 429, 500, 502, 503, 504, *range(520, 528)}


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def frozen_prompt() -> str:
    return (HERE / "frozen-prompt.txt").read_bytes().decode("utf-8")


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def request_id_shape(rid: str | None) -> str:
    """Observable shape of the id the provider returned. Description, not cause."""
    if not rid:
        return "absent"
    if re.match(r"^chatcmpl-\d{6,}-[A-Za-z0-9]+$", rid):
        return "chatcmpl-digits-alnum"
    if re.match(r"^chatcmpl-[0-9a-f]{8,}$", rid):
        return "chatcmpl-hex"
    return "other"


# --------------------------------------------------------------------------
# preflight
# --------------------------------------------------------------------------

def build_preflight(model) -> dict:
    prompt = frozen_prompt()
    shared = {
        "model_slug": model.slug,
        "provider": model.provider,
        "api_style": model.api_style,
        "model_id": model.model_id,
        "base_url_env": model.base_url_env,
        "api_key_env": model.api_key_env,
        "endpoint": OpenAICompatibleProvider(
            base_url=model.base_url(), api_key="x"
        )._endpoint(),
        "temperature": model.temperature,
        "top_p_sent": model.top_p is not None,
        "top_p": model.top_p,
        "max_output_tokens": model.max_output_tokens,
        "extra_body": dict(model.extra_body),
        "capabilities": dict(model.capabilities),
        "reasoning_enabled": model.reasoning_enabled,
        "system_prompt": None,
        "system_prompt_sha256": sha(""),
        "tools_sent": False,
        "streaming": True,
        "stream_options_include_usage": True,
        "retry_max_attempts": MAX_ATTEMPTS,
        "retry_backoff_seconds": list(BACKOFF_SECONDS),
        "retry_infra_statuses": sorted(INFRA_STATUSES),
        "prompt_sha256": sha(prompt),
        "prompt_bytes": len(prompt.encode("utf-8")),
        "conversation_carry_over": False,
        "best_of_n": False,
        "quality_retries": False,
    }
    controlled = {}
    for key, value in shared.items():
        controlled[key] = {"baseline": value, "high": value, "same": True}
    controlled["reasoning_effort"] = {
        "baseline": "<field absent from request body>",
        "high": "high",
        "same": False,
    }
    differences = [k for k, v in controlled.items() if not v["same"]]
    return {
        "generated_utc": now(),
        "purpose": "Is reasoning_effort observably effective on this route, or is "
                   "its effect indistinguishable from this model's natural variance?",
        "is_mondaybench_run": False,
        "touches": {
            "runs/": False, "evaluations/": False, "leaderboards/": False,
            "releases/": False, "verdicts/": False,
            "existing deepseek batteries": False, "reliability experiment": False,
        },
        "controlled": controlled,
        "differences": differences,
        "declared_deviations_from_a_benchmark_run": [
            {"what": "system prompt", "value": "absent for every variant",
             "why": "continues the earlier probe, which sent none",
             "constant_across_variants": True},
            {"what": "streaming", "value": "on for every variant",
             "why": "the only way to observe reasoning stream events; the earlier "
                    "probe was blocking and could not see them",
             "constant_across_variants": True,
             "consequence": "token counts are not directly comparable with the "
                            "earlier blocking probe"},
        ],
        "verdict": "CLEAN" if differences == ["reasoning_effort"] else "STOP",
    }


def build_order() -> list[dict]:
    slots = ["baseline"] * N_PER_VARIANT + ["high"] * N_PER_VARIANT
    random.Random(ORDER_SEED).shuffle(slots)
    return [{"sample_id": f"s{i + 1:03d}", "variant": v} for i, v in enumerate(slots)]


def cmd_preflight(model) -> int:
    preflight = build_preflight(model)
    (HERE / "preflight.json").write_text(json.dumps(preflight, indent=2), encoding="utf-8")

    print("PREFLIGHT\n")
    width = max(len(k) for k in preflight["controlled"])
    for key, entry in preflight["controlled"].items():
        tag = "SAME     " if entry["same"] else "DIFFERENT"
        shown = entry["baseline"] if entry["same"] else f"{entry['baseline']}  ->  {entry['high']}"
        print(f"  {tag}  {key:<{width}}  {shown}")
    print(f"\n  differences: {preflight['differences']}")
    print(f"  verdict: {preflight['verdict']}")
    if preflight["verdict"] != "CLEAN":
        print("\nSTOP: something other than reasoning_effort differs.")
        return 1

    config_path = HERE / "probe-config.json"
    if config_path.exists():
        print(f"\n{config_path.name} already exists; the frozen order is NOT regenerated.")
        return 0
    order = build_order()
    config = {
        "frozen_utc": now(),
        "experiment": HERE.name,
        "phase": 1,
        "question": preflight["purpose"],
        "model_slug": MODEL_SLUG,
        "prompt_file": "frozen-prompt.txt",
        "prompt_sha256": sha(frozen_prompt()),
        "correct_answer": "15:00",
        "scorer": SCORER_SPEC,
        "scorer_file": "scorer.py",
        "n_per_variant": N_PER_VARIANT,
        "variants": {k: (v if v is not None else "<absent>") for k, v in VARIANTS.items()},
        "order_seed": ORDER_SEED,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "bootstrap_resamples": 10000,
        "interleaved": True,
        "sentinel": {"value": SENTINEL_VALUE, "n": N_SENTINEL,
                     "in_statistics": False, "runs_after_the_60": True},
        "request_config": {k: v["baseline"] for k, v in preflight["controlled"].items()
                           if k != "reasoning_effort"},
        "order": order,
    }
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    counts = {v: sum(1 for s in order if s["variant"] == v) for v in VARIANTS}
    print(f"\n  frozen order -> {config_path.name}  ({counts}, seed {ORDER_SEED})")
    print("  first 12 slots: " + " ".join(s["variant"][0].upper() for s in order[:12]))
    return 0


# --------------------------------------------------------------------------
# execution
# --------------------------------------------------------------------------

def one_call(provider, model, effort, sample_id: str, variant: str) -> dict:
    """One independent sample. Retries infrastructure failures only."""
    prompt = frozen_prompt()
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
        "variant": variant,
        "reasoning_effort_sent": effort if effort is not None else None,
        "reasoning_effort_field_present": effort is not None,
        "model_id": model.model_id,
        "provider": model.provider,
        "prompt_sha256": sha(prompt),
        "attempts": [],
    }

    for attempt in range(MAX_ATTEMPTS):
        started_utc = now()
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
                "attempt": attempt + 1, "started_utc": started_utc, "outcome": "error",
                "error": str(exc)[:400], "status": exc.status, "kind": exc.kind,
                "transient_per_harness": bool(exc.transient),
                "classified_infrastructure": infra,
            })
            if not infra or attempt == MAX_ATTEMPTS - 1:
                record["status"] = "FAILED"
                record["failure_reason"] = str(exc)[:400]
                record["http_status"] = exc.status
                record["retries"] = len(record["attempts"]) - 1
                return record
            time.sleep(BACKOFF_SECONDS[min(attempt, len(BACKOFF_SECONDS) - 1)])
            continue

        record["attempts"].append({"attempt": attempt + 1, "started_utc": started_utc,
                                   "outcome": "ok"})
        usage = dict(result.raw_usage or {})
        details = usage.get("completion_tokens_details") or {}
        # Absent and zero are different facts and are recorded as different values.
        reported = None
        candidates = [usage.get("reasoning_tokens")]
        if isinstance(details, dict):
            candidates.append(details.get("reasoning_tokens"))
        for source in candidates:
            if source is not None:
                reported = int(source)
                break
        scored = scorer.score(result.text)
        record.update({
            "status": "OK",
            "timestamp_utc": started_utc,
            "completed_utc": now(),
            "http_status": 200,
            "request_id": result.provider_request_id,
            "request_id_shape": request_id_shape(result.provider_request_id),
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
            "response_text": result.text,
            "response_sha256": sha(result.text),
            "raw_usage": usage,
            "score_strict": scored["strict"],
            "score_last_time": scored["last_time"],
            "times_found_minutes": scored["times_found_minutes"],
            "retries": len(record["attempts"]) - 1,
        })
        return record

    record["status"] = "FAILED"  # pragma: no cover
    return record


def cmd_execute(model, sentinel: bool) -> int:
    config = json.loads((HERE / "probe-config.json").read_text(encoding="utf-8"))
    if config["prompt_sha256"] != sha(frozen_prompt()):
        print("STOP: frozen-prompt.txt no longer matches the hash in probe-config.json")
        return 1

    provider = OpenAICompatibleProvider(
        base_url=model.base_url(), api_key=model.api_key(), stream=True, timeout=300.0
    )

    if sentinel:
        out_path = HERE / "raw" / "sentinel-banana.jsonl"
        slots = [{"sample_id": f"sent{i + 1:02d}", "variant": "sentinel-banana"}
                 for i in range(N_SENTINEL)]
    else:
        out_path = HERE / "raw" / "samples.jsonl"
        slots = config["order"]

    done = set()
    if out_path.exists():
        for line in out_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                done.add(json.loads(line)["sample_id"])
        print(f"resuming: {len(done)} already recorded in {out_path.name}")

    print(f"{'sample':<8} {'variant':<16} {'stat':>5} {'reas':>7} {'out':>6} "
          f"{'ev':>5} {'ttfa':>8} {'total':>8} {'id shape':>22}  score  answer")
    for slot in slots:
        if slot["sample_id"] in done:
            continue
        effort = SENTINEL_VALUE if sentinel else VARIANTS[slot["variant"]]
        record = one_call(provider, model, effort, slot["sample_id"], slot["variant"])
        with out_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        if record["status"] == "OK":
            rt = record["reasoning_tokens_reported"]
            print(f"{record['sample_id']:<8} {record['variant']:<16} "
                  f"{record['http_status']:>5} {('null' if rt is None else rt):>7} "
                  f"{str(record['output_tokens']):>6} "
                  f"{str(record['reasoning_stream_event_count']):>5} "
                  f"{str(record['ttfa_ms']):>8} {str(record['total_latency_ms']):>8} "
                  f"{record['request_id_shape']:>22}  {record['score_strict'][:4]}   "
                  f"{record['response_text'].strip()[:40]!r}", flush=True)
        else:
            print(f"{record['sample_id']:<8} {record['variant']:<16} "
                  f"{str(record['http_status']):>5} {'FAILED':>7} "
                  f"  retries={record.get('retries')}  "
                  f"{record.get('failure_reason', '')[:70]}", flush=True)
    print(f"\nwrote -> {out_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--sentinel", action="store_true")
    args = parser.parse_args()

    model = load_models()[MODEL_SLUG]
    if args.preflight:
        return cmd_preflight(model)
    if args.execute or args.sentinel:
        preflight = json.loads((HERE / "preflight.json").read_text(encoding="utf-8"))
        if preflight["verdict"] != "CLEAN":
            print("STOP: preflight verdict is not CLEAN")
            return 1
        return cmd_execute(model, sentinel=args.sentinel)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
