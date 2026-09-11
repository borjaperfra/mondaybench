"""Does the endpoint take a reasoning-effort control, and does it do anything?

    python tools/probe_reasoning_effort.py --model deepseek-v4.1-flash

`models.yaml` sets no reasoning control on any model: these deployments think by
default and nothing in the repo says the gateway understands a knob for it. So
this asks, before any slug is created for a "maximum effort" variant.

Two questions, and the second is the one that matters:

1. Is the parameter ACCEPTED (200, not 400)?
2. Does it CHANGE ANYTHING?

A gateway that silently drops an unknown body field answers 200 to everything,
which looks like success and is worthless. So the sweep includes a deliberately
invalid value (`reasoning_effort: "banana"`). If that is accepted too, the
parameter is being ignored and no 200 in this table means a thing. Effect is
then read off `reasoning_tokens` at low vs high, on one fixed prompt at
temperature 0 with `caching: false` so no answer comes from a cache.

It writes nothing under `runs/`. It is a probe, not a generation.
"""

from __future__ import annotations

import argparse
import json
import re
import time

import httpx

from mondaybench.config import load_models

# Short answer, non-trivial thinking: the interesting number is reasoning
# tokens, so the answer must not dominate the completion.
PROMPT = (
    "Three tasks: A takes 2h, B takes 3h, C takes 1h. B cannot start until A is "
    "done. C needs the same single machine as B, so they cannot overlap. One "
    "worker, 8h day, starts at 09:00. Give only the finish time of the last task."
)

# name -> extra fields merged into the request body
VARIANTS: list[tuple[str, dict]] = [
    ("baseline", {}),
    ("effort=low", {"reasoning_effort": "low"}),
    ("effort=medium", {"reasoning_effort": "medium"}),
    ("effort=high", {"reasoning_effort": "high"}),
    ("effort=max", {"reasoning_effort": "max"}),
    ("effort=maximum", {"reasoning_effort": "maximum"}),
    # THE CONTROL. Not a typo, not a guess at a real level. If the gateway
    # accepts this, it accepts anything and is reading none of it.
    ("effort=banana (control)", {"reasoning_effort": "banana"}),
    # OpenRouter-style nesting, in case the gateway speaks that dialect.
    ("reasoning.effort=high", {"reasoning": {"effort": "high"}}),
]


def endpoint_for(model) -> str:
    base_url = model.base_url().rstrip("/")
    if base_url.endswith("/chat/completions"):
        return base_url
    if base_url.endswith("/v1"):
        return f"{base_url}/chat/completions"
    return f"{base_url}/v1/chat/completions"


def probe(model, name: str, extra: dict) -> dict:
    payload = {
        "model": model.model_id,
        "messages": [{"role": "user", "content": PROMPT}],
        "max_tokens": model.max_output_tokens,
        "stream": False,
    }
    if model.temperature is not None:
        payload["temperature"] = model.temperature
    for key, value in (model.extra_body or {}).items():
        payload[key] = value
    payload.update(extra)

    started = time.perf_counter()
    try:
        with httpx.Client(timeout=600.0) as client:
            response = client.post(
                endpoint_for(model),
                headers={
                    "Authorization": f"Bearer {model.api_key()}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
    except httpx.HTTPError as exc:
        return {"variant": name, "sent": extra, "status": None, "accepted": False,
                "error": f"network: {exc}"}
    elapsed_ms = round((time.perf_counter() - started) * 1000)

    if response.status_code >= 400:
        return {
            "variant": name,
            "sent": extra,
            "status": response.status_code,
            "accepted": False,
            "latency_ms": elapsed_ms,
            "error": response.text[:400].replace("\n", " "),
        }

    try:
        body = response.json()
    except ValueError:
        return {"variant": name, "sent": extra, "status": response.status_code,
                "accepted": False, "latency_ms": elapsed_ms, "error": "non-JSON body"}

    usage = body.get("usage") or {}
    details = usage.get("completion_tokens_details") or {}
    reasoning_tokens = details.get("reasoning_tokens")
    if reasoning_tokens is None:
        reasoning_tokens = usage.get("reasoning_tokens")
    choice = (body.get("choices") or [{}])[0]
    message = choice.get("message") or {}
    return {
        "variant": name,
        "sent": extra,
        "status": response.status_code,
        "accepted": True,
        "latency_ms": elapsed_ms,
        "finish_reason": choice.get("finish_reason"),
        "completion_tokens": usage.get("completion_tokens"),
        "reasoning_tokens": reasoning_tokens,
        "request_id": body.get("id"),
        "answer": (message.get("content") or "").strip()[:120],
        "error": None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="deepseek-v4.1-flash")
    parser.add_argument("--out", help="write the raw results as JSON here")
    parser.add_argument(
        "--repeat", type=int, default=1,
        help="samples per variant. One sample cannot tell an effort level from "
             "this model's own run-to-run variance, so use 3+ to compare levels.",
    )
    parser.add_argument(
        "--only", help="comma-separated substrings; probe just the matching variants",
    )
    args = parser.parse_args()

    model = load_models()[args.model]
    print(f"{args.model}  provider={model.provider}  model_id={model.model_id}  "
          f"max_tokens={model.max_output_tokens}  temperature={model.temperature}\n")
    print(f"{'variant':<26} {'stat':>5} {'reas':>7} {'compl':>7} {'ms':>7} {'id':>4}  note")

    variants = VARIANTS
    if args.only:
        wanted = [w.strip() for w in args.only.split(",") if w.strip()]
        variants = [v for v in VARIANTS if any(w in v[0] for w in wanted)]

    results = []
    for name, extra in variants:
        for sample in range(args.repeat):
            r = probe(model, name, extra)
            r["sample"] = sample + 1
            results.append(r)
            note = r.get("error") or r.get("answer") or ""
            # The request id FORMAT is evidence: a timestamped id and a bare hex
            # id came from different serving paths in the first sweep.
            rid = (r.get("request_id") or "")
            shape = "ts" if re.match(r"^chatcmpl-\d{6,}-", rid) else ("hex" if rid else "-")
            label = f"{name} #{sample + 1}" if args.repeat > 1 else name
            print(
                f"{label:<26} {str(r['status']):>5} "
                f"{str(r.get('reasoning_tokens')):>7} {str(r.get('completion_tokens')):>7} "
                f"{str(r.get('latency_ms')):>7} {shape:>4}  {note[:60]}"
            )

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump({"model": args.model, "prompt": PROMPT, "results": results}, fh, indent=2)
        print(f"\nraw -> {args.out}")


if __name__ == "__main__":
    main()
