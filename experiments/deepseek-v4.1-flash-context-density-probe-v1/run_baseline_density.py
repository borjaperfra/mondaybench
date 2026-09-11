"""Baseline calibration across the three density levels. No treatment.

    python run_baseline_density.py --preflight    freezes the order, writes the preflight
    python run_baseline_density.py --execute      runs the 15 baseline samples

`reasoning_effort` is never sent. There is no flag for it, and the call site
passes `effort=None` literally. Phase 1c ends when the instrument is
characterised; the baseline-versus-high comparison is phase 1d and needs
explicit authorisation.

Configuration is the baseline of the two previous probes, unchanged: helmcode,
`deepseek-v4-flash`, temperature 0, no `top_p`, 32,000 max output tokens,
`caching: false`, no system prompt, no tools, streaming on, infrastructure-only
retries with every attempt recorded.

The 15 slots are 5 per level in a randomised balanced interleaved order, frozen
before the first call. Running the levels in blocks would confound density with
whatever the backend was doing at the time.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))

from mondaybench.config import load_models  # noqa: E402
from mondaybench.providers import OpenAICompatibleProvider, ProviderError  # noqa: E402

import scorer  # noqa: E402

MODEL_SLUG = "deepseek-v4.1-flash"
LEVELS = ("compact", "medium", "dense")
N_PER_LEVEL = 5
ORDER_SEED = 16003112          # frozen assignment order
MAX_ATTEMPTS = 3
BACKOFF_SECONDS = (2.0, 6.0)
INFRA_STATUSES = {408, 409, 425, 429, 500, 502, 503, 504, *range(520, 528)}
RAW = HERE / "raw" / "baseline-density.jsonl"


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def sha(text: str) -> str:
    import hashlib
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def request_id_shape(rid: str | None) -> str:
    import re
    if not rid:
        return "absent"
    if re.match(r"^chatcmpl-\d{6,}-[A-Za-z0-9]+$", rid):
        return "chatcmpl-digits-alnum"
    if re.match(r"^chatcmpl-[0-9a-f]{8,}$", rid):
        return "chatcmpl-hex"
    return "other"


def level_prompt(level: str) -> str:
    return (HERE / "prompts" / f"{level}.txt").read_bytes().decode("utf-8")


def hashes() -> dict:
    return json.loads((HERE / "prompts" / "hashes.json").read_text(encoding="utf-8"))


def answer_key() -> str:
    return json.loads((HERE / "answer-key.json").read_text(encoding="utf-8"))["answer"]


def fingerprint(model, level: str) -> dict:
    prompt = level_prompt(level)
    return {
        "model_slug": model.slug,
        "provider": model.provider,
        "api_style": model.api_style,
        "model_id": model.model_id,
        "endpoint": OpenAICompatibleProvider(base_url=model.base_url(),
                                             api_key="x")._endpoint(),
        "temperature": model.temperature,
        "top_p_sent": model.top_p is not None,
        "top_p": model.top_p,
        "max_output_tokens": model.max_output_tokens,
        "capabilities": dict(model.capabilities),
        "caching": dict(model.extra_body).get("caching"),
        "tools_sent": False,
        "streaming": True,
        "stream_options_include_usage": True,
        "system_prompt": None,
        "system_prompt_sha256": sha(""),
        "retry_max_attempts": MAX_ATTEMPTS,
        "retry_backoff_seconds": list(BACKOFF_SECONDS),
        "retry_infra_statuses": sorted(INFRA_STATUSES),
        "conversation_carry_over": False,
        "best_of_n": False,
        "quality_retries": False,
        "reasoning_effort": "<field absent from request body>",
        "prompt_bytes": len(prompt.encode("utf-8")),
        "prompt_sha256": sha(prompt),
        "answer_key": answer_key(),
    }


def cmd_preflight(model) -> int:
    prints = {level: fingerprint(model, level) for level in LEVELS}
    shared_keys = [k for k in prints["compact"]
                   if k not in ("prompt_bytes", "prompt_sha256")]
    controlled = {
        key: {**{level: prints[level][key] for level in LEVELS},
              "same": len({json.dumps(prints[level][key], sort_keys=True)
                           for level in LEVELS}) == 1}
        for key in shared_keys
    }
    varying = {key: {level: prints[level][key] for level in LEVELS}
               for key in ("prompt_bytes", "prompt_sha256")}
    differences = [k for k, v in controlled.items() if not v["same"]]

    audit = json.loads((HERE / "equivalence-audit.json").read_text(encoding="utf-8"))
    preflight = {
        "generated_utc": now(),
        "phase": "1c",
        "purpose": "characterise a context-density instrument on baseline only",
        "is_mondaybench_run": False,
        "treatment_sent": False,
        "reasoning_effort_sent_anywhere": False,
        "controlled_across_levels": controlled,
        "intended_to_vary": varying,
        "differences_in_controlled_fields": differences,
        "equivalence_audit_verdict": audit["verdict"],
        "answer_identical_across_levels": audit["answer_identical_across_levels"],
        "declared_deviations_from_a_benchmark_run": [
            {"what": "system prompt", "value": "absent for every level",
             "constant_across_levels": True,
             "why": "continues the configuration of the two previous probes"},
            {"what": "streaming", "value": "on for every level",
             "constant_across_levels": True,
             "why": "needed to observe reasoning stream events"},
        ],
        "verdict": ("CLEAN" if not differences and audit["verdict"] == "CLEAN"
                    else "STOP"),
    }
    (HERE / "preflight.json").write_text(json.dumps(preflight, indent=2),
                                         encoding="utf-8")

    print("PREFLIGHT - phase 1c, baseline only\n")
    width = max(len(k) for k in controlled)
    for key, entry in controlled.items():
        tag = "SAME     " if entry["same"] else "DIFFERENT"
        print(f"  {tag}  {key:<{width}}  {entry['compact']}")
    print("\n  INTENDED TO VARY:")
    for key, entry in varying.items():
        shown = {level: (value[:12] if isinstance(value, str) else value)
                 for level, value in entry.items()}
        print(f"    {key:<{width}}  {shown}")
    print(f"\n  differences in controlled fields: {differences}")
    print(f"  equivalence audit: {audit['verdict']}")
    print(f"  verdict: {preflight['verdict']}")
    if preflight["verdict"] != "CLEAN":
        return 1

    config_path = HERE / "experiment-config.json"
    if config_path.exists():
        print(f"\n{config_path.name} exists; the frozen order is NOT regenerated.")
        return 0
    slots = [level for level in LEVELS for _ in range(N_PER_LEVEL)]
    random.Random(ORDER_SEED).shuffle(slots)
    order = [{"sample_id": f"b{i + 1:03d}", "level": level}
             for i, level in enumerate(slots)]
    config = {
        "frozen_utc": now(),
        "phase": "1c",
        "experiment": HERE.name,
        "hypothesis": "the same constraints, dispersed through more context, may "
                      "cost reliability even though they are solved when compact",
        "primary_metric": "task success rate",
        "levels": LEVELS,
        "n_per_level": N_PER_LEVEL,
        "order_seed": ORDER_SEED,
        "interleaved": True,
        "treatment": None,
        "reasoning_effort_sent": False,
        "answer_key": answer_key(),
        "prompt_hashes": hashes(),
        "outcome_classes": list(scorer.OUTCOMES),
        "budget_exhausted_counts_as_failure_for_success_rate": True,
        "budget_exhausted_merged_into_incorrect": False,
        "request_config": {k: v["compact"] for k, v in controlled.items()},
        "order": order,
    }
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    counts = {level: sum(1 for s in order if s["level"] == level) for level in LEVELS}
    print(f"\n  frozen order -> {config_path.name} ({counts}, seed {ORDER_SEED})")
    print("  order: " + " ".join(s["level"][0].upper() for s in order))
    return 0


def one_call(provider, model, level: str, sample_id: str) -> dict:
    prompt = level_prompt(level)
    key = answer_key()
    generation_config = {
        "max_output_tokens": model.max_output_tokens,
        "temperature": model.temperature,
        "extra_body": dict(model.extra_body),     # no reasoning_effort, ever
    }
    if model.top_p is not None:
        generation_config["top_p"] = model.top_p

    record: dict = {
        "sample_id": sample_id,
        "phase": "1c",
        "level": level,
        "variant": "baseline",
        "reasoning_effort_sent": None,
        "reasoning_effort_field_present": False,
        "model_id": model.model_id,
        "provider": model.provider,
        "prompt_sha256": sha(prompt),
        "prompt_bytes": len(prompt.encode("utf-8")),
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
            # Budget exhaustion is a result about the model, not a transport
            # failure: it is recorded as an outcome rather than retried.
            if exc.kind in ("truncated_by_budget", "empty_final_answer"):
                record.update({
                    "status": "NO_ANSWER",
                    "outcome": scorer.outcome("UNPARSEABLE", None, exc.kind),
                    "scored_verdict": None,
                    "provider_error_kind": exc.kind,
                    "failure_reason": str(exc)[:400],
                    "http_status": 200,
                    "finish_reason": "length" if exc.kind == "truncated_by_budget" else "stop",
                    "retries": len(record["attempts"]) - 1,
                })
                return record
            if not infra or attempt == MAX_ATTEMPTS - 1:
                record.update({"status": "FAILED", "outcome": "INFRA_FAILURE",
                               "failure_reason": str(exc)[:400],
                               "http_status": exc.status,
                               "retries": len(record["attempts"]) - 1})
                return record
            time.sleep(BACKOFF_SECONDS[min(attempt, len(BACKOFF_SECONDS) - 1)])
            continue

        record["attempts"].append({"attempt": attempt + 1, "started_utc": started,
                                   "outcome": "ok"})
        usage = dict(result.raw_usage or {})
        details = usage.get("completion_tokens_details") or {}
        reported = None
        candidates = [usage.get("reasoning_tokens")]
        if isinstance(details, dict):
            candidates.append(details.get("reasoning_tokens"))
        for source in candidates:
            if source is not None:
                reported = int(source)
                break
        scored = scorer.score(result.text, key)
        record.update({
            "status": "OK",
            "timestamp_utc": started,
            "completed_utc": now(),
            "http_status": 200,
            "request_id": result.provider_request_id,
            "request_id_shape": request_id_shape(result.provider_request_id),
            "prompt_tokens": result.input_tokens,
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
            "scored_verdict": scored["verdict"],
            "outcome": scorer.outcome(scored["verdict"], result.finish_reason, None),
            "parsed_answer": scored["parsed_answer"],
            "expected_answer": scored["expected_answer"],
            "answer_lines_found": scored["answer_lines_found"],
            "retries": len(record["attempts"]) - 1,
        })
        return record

    record["status"] = "FAILED"  # pragma: no cover
    return record


def cmd_execute(model) -> int:
    preflight = json.loads((HERE / "preflight.json").read_text(encoding="utf-8"))
    if preflight["verdict"] != "CLEAN":
        print("STOP: preflight verdict is not CLEAN")
        return 1
    config = json.loads((HERE / "experiment-config.json").read_text(encoding="utf-8"))
    for level in LEVELS:
        if config["prompt_hashes"][level]["sha256"] != sha(level_prompt(level)):
            print(f"STOP: {level}.txt no longer matches its frozen hash")
            return 1

    provider = OpenAICompatibleProvider(base_url=model.base_url(),
                                        api_key=model.api_key(),
                                        stream=True, timeout=600.0)
    RAW.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if RAW.exists():
        done = {json.loads(line)["sample_id"]
                for line in RAW.read_text(encoding="utf-8").splitlines() if line.strip()}
        print(f"resuming: {len(done)} already recorded")

    print(f"{'sample':<7} {'level':<8} {'outcome':<17} {'got':<7} {'reas':>7} "
          f"{'ptok':>6} {'out':>7} {'ev':>7} {'ms':>9}")
    for slot in config["order"]:
        if slot["sample_id"] in done:
            continue
        record = one_call(provider, model, slot["level"], slot["sample_id"])
        with RAW.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        rt = record.get("reasoning_tokens_reported")
        print(f"{record['sample_id']:<7} {record['level']:<8} "
              f"{str(record.get('outcome')):<17} "
              f"{str(record.get('parsed_answer')):<7} "
              f"{('null' if rt is None else rt):>7} "
              f"{str(record.get('prompt_tokens')):>6} "
              f"{str(record.get('output_tokens')):>7} "
              f"{str(record.get('reasoning_stream_event_count')):>7} "
              f"{str(record.get('total_latency_ms', '')):>9}", flush=True)
    print(f"\nwrote -> {RAW}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    model = load_models()[MODEL_SLUG]
    if args.preflight:
        return cmd_preflight(model)
    if args.execute:
        return cmd_execute(model)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
