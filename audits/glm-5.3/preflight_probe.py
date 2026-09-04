"""Preflight for glm5.3 on Helmcode. Non-scored, non-frozen prompt.

Runs through the harness's own adapter path (OpenAICompatibleProvider) and, in
parallel, captures the raw SSE frames so the *served* model id, tool_calls and
cost fields can be observed - the adapter does not record those.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from mondaybench.config import resolve_env  # noqa: E402
from mondaybench.providers.openai_compatible import OpenAICompatibleProvider  # noqa: E402
from mondaybench.providers.base import ProviderError  # noqa: E402
import httpx  # noqa: E402

BASE = resolve_env("HELMCODE_BASE_URL", required=True).rstrip("/")
KEY = resolve_env("HELMCODE_API_KEY", required=True)
MODEL = "glm5.3"

# Deliberately NOT a frozen scenario prompt.
SYS = "You are a helpful assistant."
USER = "Reply with exactly one line: PREFLIGHT OK, then the sum of 17 and 23."

out: dict = {"model_requested": MODEL, "base_url_env": "HELMCODE_BASE_URL", "probes": {}}


def raw_stream(payload: dict) -> dict:
    """Raw SSE capture: served model id, tool_calls, finish_reason, usage."""
    seen_models, tool_calls, finish, usage, rid = set(), 0, None, {}, None
    n_frames = 0
    reasoning_chars = 0
    content_chars = 0
    t0 = time.perf_counter()
    with httpx.Client(timeout=300.0) as c:
        with c.stream("POST", f"{BASE}/chat/completions",
                      headers={"Authorization": f"Bearer {KEY}",
                               "Content-Type": "application/json"},
                      json=payload) as r:
            if r.status_code >= 400:
                r.read()
                return {"http_status": r.status_code, "body": r.text[:800]}
            headers = dict(r.headers)
            for line in r.iter_lines():
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if not data or data == "[DONE]":
                    continue
                try:
                    ev = json.loads(data)
                except json.JSONDecodeError:
                    continue
                n_frames += 1
                if ev.get("model"):
                    seen_models.add(ev["model"])
                if ev.get("id") and rid is None:
                    rid = ev["id"]
                if ev.get("usage"):
                    usage = ev["usage"]
                for ch in ev.get("choices") or []:
                    d = ch.get("delta") or {}
                    if d.get("tool_calls"):
                        tool_calls += len(d["tool_calls"])
                    th = d.get("reasoning_content") or d.get("reasoning")
                    if isinstance(th, str):
                        reasoning_chars += len(th)
                    if d.get("content"):
                        content_chars += len(d["content"])
                    if ch.get("finish_reason"):
                        finish = ch["finish_reason"]
    return {
        "http_status": 200,
        "served_model_ids": sorted(seen_models),
        "provider_request_id": rid,
        "finish_reason": finish,
        "usage": usage,
        "tool_call_deltas": tool_calls,
        "sse_frames": n_frames,
        "reasoning_chars": reasoning_chars,
        "content_chars": content_chars,
        "elapsed_ms": round((time.perf_counter() - t0) * 1000, 1),
        "response_headers": {k: v for k, v in headers.items()
                             if k.lower().startswith(("x-", "openai-", "cf-ray"))},
    }


# --- Probe 1: benchmark config, streaming, via raw wire (identity + usage) ---
payload = {
    "model": MODEL,
    "messages": [{"role": "system", "content": SYS}, {"role": "user", "content": USER}],
    "stream": True,
    "max_tokens": 32000,
    "temperature": 0,
    "stream_options": {"include_usage": True},
    "caching": False,
}
out["probes"]["wire_streaming_benchmark_config"] = {"request": payload, "result": raw_stream(payload)}

# --- Probe 2: same call through the harness adapter -------------------------
prov = OpenAICompatibleProvider(base_url=BASE, api_key=KEY)
try:
    res = prov.generate(model_id=MODEL, system_prompt=SYS, user_prompt=USER,
                        generation_config={"temperature": 0, "max_output_tokens": 32000,
                                           "extra_body": {"caching": False}})
    out["probes"]["harness_adapter"] = {
        "ok": True, "text": res.text[:400], "input_tokens": res.input_tokens,
        "output_tokens": res.output_tokens, "reasoning_tokens": res.reasoning_tokens,
        "ttft_ms": res.ttft_ms, "ttfa_ms": res.ttfa_ms,
        "total_latency_ms": res.total_latency_ms, "finish_reason": res.finish_reason,
        "provider_request_id": res.provider_request_id, "raw_usage": res.raw_usage,
        "unsupported_parameters": res.unsupported_parameters,
        "reasoning_stream_observed": res.reasoning_stream_observed,
        "reasoning_stream_event_count": res.reasoning_stream_event_count,
    }
except ProviderError as exc:
    out["probes"]["harness_adapter"] = {"ok": False, "kind": exc.kind,
                                        "status": exc.status, "error": str(exc)[:800]}

# --- Probe 3: top_p acceptance (small budget, parameter acceptance only) ----
p3 = dict(payload, top_p=1.0, max_tokens=64,
          messages=[{"role": "user", "content": "Say OK."}])
out["probes"]["top_p_accepted"] = {"request_extra": {"top_p": 1.0}, "result": raw_stream(p3)}

Path(__file__).with_name("preflight-probes.json").write_text(
    json.dumps(out, indent=2), encoding="utf-8")
print(json.dumps(out["probes"]["wire_streaming_benchmark_config"]["result"], indent=2)[:2500])
