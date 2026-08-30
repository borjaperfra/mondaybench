"""Establish, per endpoint, the largest `max_tokens` value the API will accept.

    python tools/probe_output_ceiling.py            probe every configured model
    python tools/probe_output_ceiling.py --model X  probe one

The monday-004 calibration needs a generation ceiling high enough not to bind
any of the seven models. `models.yaml` documents context windows (1M, 500K,
256K) and nothing about maximum output, so the supported ceiling cannot be read
off the repository - and guessing it is exactly what the brief forbids.

So this asks the endpoints. Each probe is a two-message request whose answer is
one word, sent with a large `max_tokens`. It costs a handful of tokens and it
establishes the one thing that matters: whether the API accepts the parameter
value at all, or rejects it with a limit of its own. A 400 naming the real
maximum is the best evidence available; a clean 200 means the value is accepted.

It writes nothing under `runs/`. It is a probe, not a generation.
"""

from __future__ import annotations

import argparse
import json

import httpx

from mondaybench.config import load_models

CANDIDATES = [131072, 96000, 64000, 48000]
PROMPT = "Reply with the single word: ok"


def probe(model, ceiling: int) -> dict:
    """One non-streaming request. Returns what the endpoint said."""
    base_url = model.base_url().rstrip("/")
    if base_url.endswith("/chat/completions"):
        endpoint = base_url
    elif base_url.endswith("/v1"):
        endpoint = f"{base_url}/chat/completions"
    else:
        endpoint = f"{base_url}/v1/chat/completions"

    payload = {
        "model": model.model_id,
        "messages": [{"role": "user", "content": PROMPT}],
        "max_tokens": ceiling,
        "stream": False,
    }
    for key, value in (model.extra_body or {}).items():
        payload[key] = value

    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {model.api_key()}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
    except httpx.HTTPError as exc:
        return {"ceiling": ceiling, "status": None, "accepted": False, "error": f"network: {exc}"}

    if response.status_code >= 400:
        detail = response.text[:400].replace("\n", " ")
        return {
            "ceiling": ceiling,
            "status": response.status_code,
            "accepted": False,
            "error": detail,
        }

    try:
        body = response.json()
    except ValueError:
        return {"ceiling": ceiling, "status": response.status_code, "accepted": False, "error": "non-JSON body"}

    usage = body.get("usage") or {}
    choice = (body.get("choices") or [{}])[0]
    return {
        "ceiling": ceiling,
        "status": response.status_code,
        "accepted": True,
        "finish_reason": choice.get("finish_reason"),
        "completion_tokens": usage.get("completion_tokens"),
        "error": None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model")
    args = parser.parse_args()

    models = load_models()
    slugs = [args.model] if args.model else list(models)
    results: dict[str, dict] = {}

    for slug in slugs:
        model = models[slug]
        highest = None
        attempts = []
        for ceiling in CANDIDATES:
            outcome = probe(model, ceiling)
            attempts.append(outcome)
            print(
                f"{slug:<20} {ceiling:>7}  "
                f"{'OK ' if outcome['accepted'] else 'REJ'}  "
                f"status={outcome['status']}  "
                f"{outcome.get('error') or ''}"
            )
            if outcome["accepted"]:
                highest = ceiling
                break
        results[slug] = {
            "provider": model.provider,
            "model_id": model.model_id,
            "highest_accepted": highest,
            "attempts": attempts,
        }

    print("\n=== highest accepted max_tokens per endpoint ===")
    for slug, r in results.items():
        print(f"  {slug:<20} {r['provider']:<10} {r['highest_accepted']}")
    print("\n" + json.dumps(results, indent=2)[:200] + " ...")


if __name__ == "__main__":
    main()
