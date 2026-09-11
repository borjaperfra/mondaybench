"""Is reasoning actually delivered at `reasoning_effort: max`, on both routes?

    python tools/probe_max_reasoning_active.py

Borja's own testing against api.helmcode.com established that low, medium, high
and max all return 200 carrying `message.reasoning_content`, and that any value
the gateway does not recognise returns 200 with reasoning silently OFF. That was
measured on the blocking route.

The harness does not use the blocking route. `mondaybench run` generates with
`stream=True`, and on that route reasoning arrives as `reasoning_content` deltas
rather than as a field on a finished message. A level that carries reasoning
when read one way and not the other would be invisible to the blocking check and
fatal to a battery, so both routes are probed here with the same request.

For each level this records, per route:

  * whether the provider reported reasoning tokens, and how many
  * whether the adapter observed reasoning stream events (streaming only)
  * `prompt_tokens`, because the two high levels are known to send more of them
    than the bare prompt - 139 and 152 against 60 on Borja's induction prompt -
    which means something is injected into the request at those levels
  * the request id's shape, which separated the reasoning path from the
    silent non-reasoning one in the earlier effort probe

`bogus_xyz` is included as the control. Without it a row of 200s proves nothing:
it is the value that must come back WITHOUT reasoning, and if it does not, the
gateway is not reading the field at all and no other row can be trusted.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mondaybench.config import load_models  # noqa: E402
from mondaybench.providers import OpenAICompatibleProvider  # noqa: E402

MODEL_SLUG = "deepseek-v4.1-flash"

# Short, but enough that a thinking model has something to think about.
PROMPT = (
    "A bag holds 3 red, 4 blue and 5 green marbles. Two are drawn without "
    "replacement. What is the probability both are the same colour? Give the "
    "reduced fraction only."
)

LEVELS = [
    ("omitted", None),
    ("max", "max"),
    ("high", "high"),
    ("bogus_xyz (control)", "bogus_xyz"),
]


def request_id_shape(rid: str | None) -> str:
    if not rid:
        return "absent"
    if re.match(r"^chatcmpl-\d{6,}-[A-Za-z0-9]+$", rid):
        return "digits-alnum"
    if re.match(r"^chatcmpl-[0-9a-f]{8,}$", rid):
        return "hex"
    return "other"


def reasoning_tokens_from(usage: dict) -> int | None:
    details = usage.get("completion_tokens_details")
    if isinstance(details, dict) and details.get("reasoning_tokens") is not None:
        return int(details["reasoning_tokens"])
    if usage.get("reasoning_tokens") is not None:
        return int(usage["reasoning_tokens"])
    return None


def blocking(model, effort):
    """The route Borja measured: read reasoning off the finished message."""
    body = {
        "model": model.model_id,
        "messages": [{"role": "user", "content": PROMPT}],
        "max_tokens": model.max_output_tokens,
        "temperature": model.temperature,
        "stream": False,
        **dict(model.extra_body),
    }
    if effort is not None:
        body["reasoning_effort"] = effort
    with httpx.Client(timeout=600.0) as client:
        r = client.post(
            f"{model.base_url().rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {model.api_key()}",
                     "Content-Type": "application/json"},
            json=body,
        )
    if r.status_code >= 400:
        return {"http": r.status_code, "error": r.text[:200]}
    payload = r.json()
    usage = payload.get("usage") or {}
    message = ((payload.get("choices") or [{}])[0].get("message") or {})
    content = message.get("reasoning_content") or message.get("reasoning") or ""
    return {
        "http": r.status_code,
        "reasoning_tokens": reasoning_tokens_from(usage),
        "reasoning_content_chars": len(content),
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "request_id_shape": request_id_shape(payload.get("id")),
        "answer": (message.get("content") or "").strip()[:40],
    }


def streaming(model, effort):
    """The route the harness actually generates on."""
    extra = dict(model.extra_body)
    if effort is not None:
        extra["reasoning_effort"] = effort
    provider = OpenAICompatibleProvider(base_url=model.base_url(),
                                        api_key=model.api_key(), stream=True,
                                        timeout=600.0)
    result = provider.generate(
        model_id=model.model_id,
        system_prompt=None,
        user_prompt=PROMPT,
        generation_config={"max_output_tokens": model.max_output_tokens,
                           "temperature": model.temperature, "extra_body": extra},
    )
    usage = dict(result.raw_usage or {})
    return {
        "http": 200,
        "reasoning_tokens": reasoning_tokens_from(usage),
        "stream_observed": result.reasoning_stream_observed,
        "stream_events": result.reasoning_stream_event_count,
        "prompt_tokens": result.input_tokens,
        "completion_tokens": result.output_tokens,
        "request_id_shape": request_id_shape(result.provider_request_id),
        "answer": (result.text or "").strip()[:40],
    }


def main() -> int:
    model = load_models()[MODEL_SLUG]
    print(f"{model.slug} -> {model.provider} {model.model_id} "
          f"temperature={model.temperature} ceiling={model.max_output_tokens}\n")

    rows = []
    for label, effort in LEVELS:
        for route, fn in (("blocking", blocking), ("streaming", streaming)):
            try:
                out = fn(model, effort)
            except Exception as exc:  # noqa: BLE001 - a failure is a result here
                out = {"http": None, "error": f"{type(exc).__name__}: {exc}"[:200]}
            out.update({"level": label, "route": route})
            rows.append(out)
            rt = out.get("reasoning_tokens")
            delivered = "YES" if (rt or 0) > 0 or out.get("stream_events") else "no"
            print(f"{label:<22} {route:<10} http={out.get('http')}  "
                  f"reasoning={delivered:<4} tokens={str(rt):<7} "
                  f"events={str(out.get('stream_events','-')):<7} "
                  f"ptok={str(out.get('prompt_tokens')):<5} "
                  f"id={out.get('request_id_shape','-'):<12} "
                  f"{str(out.get('answer') or out.get('error'))[:38]!r}")

    out_path = Path(__file__).resolve().parents[1] / "analysis" / "max-reasoning-probe.json"
    out_path.write_text(json.dumps({"prompt": PROMPT, "model": MODEL_SLUG,
                                    "rows": rows}, indent=2), encoding="utf-8")
    print(f"\nraw -> {out_path.relative_to(Path.cwd()).as_posix()}")

    def got(level, route):
        r = next(x for x in rows if x["level"] == level and x["route"] == route)
        return (r.get("reasoning_tokens") or 0) > 0 or bool(r.get("stream_events"))

    print("\nVERDICT")
    for route in ("blocking", "streaming"):
        ok = got("max", route)
        ctl = got("bogus_xyz (control)", route)
        print(f"  {route:<10} max delivers reasoning: {ok}   "
              f"control delivers reasoning: {ctl}  "
              f"-> {'usable' if ok and not ctl else 'NOT ESTABLISHED'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
