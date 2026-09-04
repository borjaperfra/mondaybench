"""Exactly what the model is sent on the official route. Built, not sent."""
import json, sys, hashlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from mondaybench.config import load_models
from mondaybench.scenarios import load_scenario
from mondaybench.prompt_builder import build_prompt
from mondaybench.providers.openai_compatible import OpenAICompatibleProvider
from mondaybench.runner import effective_ceiling

m = load_models()["glm5.3"]
prov = OpenAICompatibleProvider(base_url="https://api.helmcode.com/v1", api_key="REDACTED")
out = {}
for sid in ["monday-001","monday-002","monday-003","monday-004","monday-005"]:
    loaded = load_scenario(sid); built = build_prompt(loaded)
    payload, unsupported = prov._payload(
        model_id=m.model_id, system_prompt=built.system_prompt, user_prompt=built.text,
        generation_config={"temperature": m.temperature,
                           "max_output_tokens": effective_ceiling(loaded, m),
                           "extra_body": m.extra_body},
        stream=True)
    msgs = payload["messages"]
    out[sid] = {
        "top_level_keys": sorted(payload.keys()),
        "message_roles": [x["role"] for x in msgs],
        "message_count": len(msgs),
        "system_content": msgs[0]["content"],
        "user_sha256": hashlib.sha256(msgs[1]["content"].encode()).hexdigest(),
        "user_matches_frozen_prompt": hashlib.sha256(msgs[1]["content"].encode()).hexdigest() == built.sha256,
        "user_head": msgs[1]["content"][:200],
        "user_tail": msgs[1]["content"][-200:],
        "tools_key_present": "tools" in payload,
        "unsupported_parameters": unsupported,
        "max_tokens": payload.get("max_tokens"),
        "temperature": payload.get("temperature"),
        "top_p_present": "top_p" in payload,
        "extra_keys_beyond_standard": sorted(set(payload) - {"model","messages","stream","max_tokens","temperature","stream_options"}),
    }
Path(__file__).with_name("wire-capture.json").write_text(json.dumps(out, indent=2)+"\n", encoding="utf-8")
for sid, d in out.items():
    print(sid, "roles", d["message_roles"], "| frozen-match", d["user_matches_frozen_prompt"],
          "| tools", d["tools_key_present"], "| extra", d["extra_keys_beyond_standard"], "| max_tokens", d["max_tokens"])
print("system prompt:", repr(out["monday-001"]["system_content"]))
