"""What does `reasoning_effort: max` produce when nothing stops it?

    python run-unbounded.py monday-005 1

Exploratory. NOT a battery, not comparable with anything published, and it
cannot be: it changes two things at once against every other DeepSeek battery.

  * `max_output_tokens` goes to 393,216, three times the suite's largest
    configured ceiling of 131,072. It is not literally unbounded: the gateway
    rejects a ceiling with HTTP 400 somewhere between 393,216 and 400,000, so
    393,216 is the most headroom this route will take. The rejection is a
    request-validation error, not a model limit - it arrives instantly, before
    any token is generated.
  * The HTTP client timeout goes to 3,600 seconds from the harness default of
    300. This is the constraint that actually killed the earlier attempts: at
    the ~180 tokens/second these runs sustain, 300 seconds is about 54,000
    tokens, and the monday-005 leaks needed more than 131,072. A bigger token
    ceiling alone would have changed nothing.

The timeout is transport, not a generation parameter - the model sees the same
request either way - but it is raised HERE rather than in the harness, because
making 3,600 seconds the default would change what "failed" means for every
model in the suite.

Written under `experiments/` for the same reason: a run whose ceiling and
patience both differ cannot sit in `runs/` beside batteries that share one
configuration.

The question is narrow. Does the reasoning ever terminate on its own, how much
of it is there, and is the answer any better than the one the same model gives
in 20,000 tokens?
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
sys.path.insert(0, str(REPO))

from mondaybench.config import load_models  # noqa: E402
from mondaybench.prompt_builder import build_prompt  # noqa: E402
from mondaybench.providers import OpenAICompatibleProvider, ProviderError  # noqa: E402
from mondaybench.scenarios import load_scenario  # noqa: E402

CEILING = 393_216
TIMEOUT_S = 3600.0
BASE_SLUG = "deepseek-v4.1-flash"


def main() -> int:
    scenario_id = sys.argv[1] if len(sys.argv) > 1 else "monday-005"
    run_number = int(sys.argv[2]) if len(sys.argv) > 2 else 1

    model = load_models()[BASE_SLUG]
    scenario = load_scenario(scenario_id)
    prompt = build_prompt(scenario)

    extra = dict(model.extra_body)
    extra["reasoning_effort"] = "max"

    provider = OpenAICompatibleProvider(
        base_url=model.base_url(), api_key=model.api_key(),
        stream=True, timeout=TIMEOUT_S,
    )

    started = datetime.now(timezone.utc)
    print(f"{scenario_id} run-{run_number}  ceiling={CEILING:,}  timeout={TIMEOUT_S:.0f}s")
    print(f"prompt sha256 {prompt.sha256[:12]}  {len(prompt.text):,} chars  started {started:%H:%M:%S}Z")
    sys.stdout.flush()

    record: dict = {
        "experiment": ROOT.name,
        "not_a_benchmark_artifact": True,
        "scenario_id": scenario_id,
        "run_number": run_number,
        "model_slug": BASE_SLUG,
        "model_id": model.model_id,
        "reasoning_effort": "max",
        "max_output_tokens": CEILING,
        "client_timeout_s": TIMEOUT_S,
        "scenario_prompt_sha256": prompt.sha256,
        "started_utc": started.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    try:
        result = provider.generate(
            model_id=model.model_id,
            system_prompt=prompt.system_prompt,
            user_prompt=prompt.text,
            generation_config={"max_output_tokens": CEILING,
                               "temperature": model.temperature,
                               "extra_body": extra},
        )
    except ProviderError as exc:
        record.update({"outcome": "FAILED", "kind": exc.kind, "error": str(exc)[:600],
                       "completed_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
        print(f"\nFAILED ({exc.kind}): {str(exc)[:200]}")
    else:
        usage = dict(result.raw_usage or {})
        details = usage.get("completion_tokens_details") or {}
        record.update({
            "outcome": "OK",
            "finish_reason": result.finish_reason,
            "input_tokens": result.input_tokens,
            "output_tokens": result.output_tokens,
            "reasoning_tokens": (details.get("reasoning_tokens")
                                 if isinstance(details, dict) else None),
            "reasoning_stream_events": result.reasoning_stream_event_count,
            "ttft_ms": result.ttft_ms,
            "ttfa_ms": result.ttfa_ms,
            "total_latency_ms": result.total_latency_ms,
            "request_id": result.provider_request_id,
            "response": result.text,
            "response_chars": len(result.text),
            "raw_usage": usage,
            "completed_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        })
        print(f"\nOK  finish={result.finish_reason}  "
              f"reasoning={record['reasoning_tokens']}  output={result.output_tokens}  "
              f"{result.total_latency_ms/1000:.0f}s  answer {len(result.text):,} chars")

    out = ROOT / f"{scenario_id}-run-{run_number:03d}.json"
    out.write_bytes(json.dumps(record, indent=2, ensure_ascii=False).encode("utf-8"))
    print(f"wrote {out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
