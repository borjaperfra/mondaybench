"""Extract the token-budget evidence from every stored run and write the audit.

    python analysis/_token_budget_audit.py

Writes `analysis/token-budget-audit.json` (machine-readable, one record per run)
and prints the tables that `analysis/token-budget-audit.md` is built from.

This reads only. It changes no run, no evaluation, no leaderboard and no
qualification rule.

The question the audit exists to answer is what `max_output_tokens: 32000`
actually means once it has been through our adapter and the provider. Three
things are needed to answer it and all three are on disk:

  * what we sent - `mondaybench/providers/openai_compatible.py` maps
    `max_output_tokens` onto the request field `max_tokens`;
  * what came back - `provider_metadata.raw_usage` is the provider's own usage
    object, stored verbatim;
  * what the answer looked like - the response text, whose length is the check
    on whether `completion_tokens` includes the reasoning phase or excludes it.

Nothing here is inferred from the field name alone.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNS = REPO_ROOT / "runs"
OUT_JSON = REPO_ROOT / "analysis" / "token-budget-audit.json"

# The single place `max_output_tokens` becomes a wire field. Recorded here so
# the audit states what was sent rather than what the config called it.
REQUEST_FIELD = "max_tokens"
ADAPTER = "mondaybench/providers/openai_compatible.py::_payload"


def records() -> list[dict]:
    out: list[dict] = []
    for scenario_dir in sorted(RUNS.iterdir()):
        if not scenario_dir.is_dir():
            continue
        for model_dir in sorted(scenario_dir.iterdir()):
            if not model_dir.is_dir():
                continue
            for path in sorted(model_dir.glob("run-*.json")):
                raw = json.loads(path.read_text(encoding="utf-8"))
                usage = raw.get("usage") or {}
                meta = raw.get("provider_metadata") or {}
                provider_usage = meta.get("raw_usage") or {}
                details = provider_usage.get("completion_tokens_details") or {}
                generation = raw.get("generation") or {}

                configured = generation.get("max_output_tokens")
                completion = provider_usage.get("completion_tokens")
                if completion is None:
                    completion = usage.get("output_tokens")
                reasoning = details.get("reasoning_tokens")
                if reasoning is None:
                    reasoning = provider_usage.get("reasoning_tokens")
                if reasoning is None:
                    reasoning = usage.get("reasoning_tokens")

                answer_chars = len(raw.get("response") or "")
                # Only meaningful if reasoning is a subset of completion, which
                # is what `chars_per_answer_token` is here to test.
                answer_tokens = (
                    completion - reasoning
                    if completion is not None and reasoning is not None
                    else None
                )
                out.append(
                    {
                        "scenario": raw.get("scenario_id"),
                        "model": model_dir.name,
                        "run_id": raw.get("run_id"),
                        "run_file": str(path.relative_to(REPO_ROOT)).replace("\\", "/"),
                        "provider": (raw.get("model") or {}).get("provider"),
                        "provider_model_id": (raw.get("model") or {}).get("model_id"),
                        "api_style": meta.get("api_style") or "openai_compatible",
                        "request_field": REQUEST_FIELD,
                        "configured_max_output_tokens": configured,
                        "reasoning_requested": generation.get("reasoning_requested"),
                        "reasoning_enabled": generation.get("reasoning_enabled"),
                        "reasoning_mode": generation.get("reasoning_mode"),
                        "reasoning_stream_observed": meta.get("reasoning_stream_observed"),
                        "reasoning_stream_event_count": meta.get("reasoning_stream_event_count"),
                        "input_tokens": provider_usage.get("prompt_tokens", usage.get("input_tokens")),
                        "reasoning_tokens": reasoning,
                        "completion_tokens": completion,
                        "total_tokens": provider_usage.get("total_tokens"),
                        "answer_tokens_derived": answer_tokens,
                        "answer_chars": answer_chars,
                        "chars_per_answer_token": (
                            round(answer_chars / answer_tokens, 2)
                            if answer_tokens and answer_tokens > 0
                            else None
                        ),
                        "chars_per_completion_token": (
                            round(answer_chars / completion, 2)
                            if completion
                            else None
                        ),
                        "finish_reason": raw.get("finish_reason"),
                        "completed": raw.get("finish_reason") == "stop",
                        "exceeds_configured": (
                            completion is not None
                            and configured is not None
                            and completion > configured
                        ),
                        "overage_tokens": (
                            completion - configured
                            if completion is not None
                            and configured is not None
                            and completion > configured
                            else 0
                        ),
                        "usage_keys": sorted(provider_usage.keys()),
                        "completion_tokens_details": details,
                    }
                )
    return out


def classify(rows: list[dict]) -> dict[str, dict]:
    """What the configured ceiling appears to bound, per provider and model.

    Decided only from observed behaviour:

      * a run that stopped at exactly the ceiling with reasoning inside it is
        evidence the ceiling bounds reasoning + answer (semantics A);
      * a run whose completion_tokens exceeded the ceiling while its derived
        answer stayed under it is evidence the ceiling does not bound reasoning
        (semantics B or "not enforced");
      * everything else is silent, and is reported as such.
    """
    out: dict[str, dict] = {}
    for row in rows:
        key = f"{row['provider']}/{row['model']}"
        bucket = out.setdefault(
            key,
            {
                "provider": row["provider"],
                "model": row["model"],
                "runs": 0,
                "max_completion_tokens_seen": 0,
                "configured": row["configured_max_output_tokens"],
                "truncated_at_ceiling": 0,
                "exceeded_ceiling": 0,
                "max_overage": 0,
                "reasoning_ever_reported": False,
                "evidence": "SILENT",
            },
        )
        bucket["runs"] += 1
        if row["completion_tokens"]:
            bucket["max_completion_tokens_seen"] = max(
                bucket["max_completion_tokens_seen"], row["completion_tokens"]
            )
        if row["reasoning_tokens"]:
            bucket["reasoning_ever_reported"] = True
        if (
            row["finish_reason"] == "length"
            and row["completion_tokens"] == row["configured_max_output_tokens"]
        ):
            bucket["truncated_at_ceiling"] += 1
        if row["exceeds_configured"]:
            bucket["exceeded_ceiling"] += 1
            bucket["max_overage"] = max(bucket["max_overage"], row["overage_tokens"])

    for bucket in out.values():
        if bucket["exceeded_ceiling"]:
            bucket["evidence"] = "CEILING NOT APPLIED TO COMPLETION"
        elif bucket["truncated_at_ceiling"]:
            bucket["evidence"] = "CEILING BOUNDS COMPLETION (reasoning + answer)"
        elif bucket["max_completion_tokens_seen"] < (bucket["configured"] or 0):
            bucket["evidence"] = "SILENT (never approached the ceiling)"
    return out


def main() -> None:
    rows = records()
    buckets = classify(rows)
    payload = {
        "generated_from": "runs/ (read-only)",
        "request_field_sent": REQUEST_FIELD,
        "adapter": ADAPTER,
        "note": (
            "max_output_tokens is mapped onto the OpenAI Chat Completions field "
            "`max_tokens`, not `max_completion_tokens`. No run in this repository "
            "was generated with `max_completion_tokens`."
        ),
        "runs": rows,
        "by_provider_model": buckets,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT_JSON.relative_to(REPO_ROOT)}  ({len(rows)} runs)\n")

    print("## Runs whose delivered completion exceeded the configured ceiling\n")
    print("| scenario | model | run | configured | completion | reasoning | derived answer | over by | finish |")
    print("|---|---|---|---:|---:|---:|---:|---:|---|")
    for r in rows:
        if not r["exceeds_configured"]:
            continue
        print(
            f"| {r['scenario']} | {r['model']} | {r['run_id'].split('__')[-1]} | "
            f"{r['configured_max_output_tokens']} | {r['completion_tokens']} | "
            f"{r['reasoning_tokens']} | {r['answer_tokens_derived']} | "
            f"+{r['overage_tokens']} | {r['finish_reason']} |"
        )

    print("\n## Runs that stopped at the ceiling\n")
    print("| scenario | model | run | configured | completion | reasoning | derived answer | answer chars | finish |")
    print("|---|---|---|---:|---:|---:|---:|---:|---|")
    for r in rows:
        if r["finish_reason"] != "length":
            continue
        print(
            f"| {r['scenario']} | {r['model']} | {r['run_id'].split('__')[-1]} | "
            f"{r['configured_max_output_tokens']} | {r['completion_tokens']} | "
            f"{r['reasoning_tokens']} | {r['answer_tokens_derived']} | "
            f"{r['answer_chars']} | {r['finish_reason']} |"
        )

    print("\n## Is reasoning inside completion_tokens?\n")
    print("chars per derived answer token should land in the 3-5 range if it is.\n")
    print("| provider/model | runs | reasoning reported | median chars/answer tok | median chars/completion tok |")
    print("|---|---:|---|---:|---:|")
    import statistics

    groups: dict[str, list[dict]] = {}
    for r in rows:
        groups.setdefault(f"{r['provider']}/{r['model']}", []).append(r)
    for key, group in sorted(groups.items()):
        a = [r["chars_per_answer_token"] for r in group if r["chars_per_answer_token"]]
        c = [r["chars_per_completion_token"] for r in group if r["chars_per_completion_token"]]
        reported = "yes" if any(r["reasoning_tokens"] for r in group) else "no (always 0/absent)"
        print(
            f"| {key} | {len(group)} | {reported} | "
            f"{statistics.median(a):.2f} | {statistics.median(c):.2f} |"
            if a and c
            else f"| {key} | {len(group)} | {reported} | - | - |"
        )

    print("\n## What the ceiling appears to bound\n")
    print("| provider/model | runs | configured | max completion seen | stopped at ceiling | exceeded | verdict |")
    print("|---|---:|---:|---:|---:|---:|---|")
    for key, b in sorted(buckets.items()):
        print(
            f"| {key} | {b['runs']} | {b['configured']} | {b['max_completion_tokens_seen']} | "
            f"{b['truncated_at_ceiling']} | {b['exceeded_ceiling']} | {b['evidence']} |"
        )

    print("\n## Hypothetical rule: completion_tokens must not exceed configured\n")
    affected = [r for r in rows if r["exceeds_configured"]]
    by_scenario: dict[str, list[dict]] = {}
    for r in affected:
        by_scenario.setdefault(r["scenario"], []).append(r)
    for scenario, group in sorted(by_scenario.items()):
        models = sorted({r["model"] for r in group})
        print(f"- **{scenario}**: {len(group)} run(s) would be invalidated, models: {', '.join(models)}")
    print(f"\nTotal: {len(affected)} of {len(rows)} runs across the whole repository.")


if __name__ == "__main__":
    main()
