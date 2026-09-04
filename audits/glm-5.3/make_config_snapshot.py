import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from mondaybench.config import load_models
from mondaybench.scenarios import load_scenario
from mondaybench.prompt_builder import build_prompt
from mondaybench import reasoning
from mondaybench.runner import effective_ceiling, CEILING_SEMANTICS

m = load_models()["glm5.3"]
mode, effort = reasoning.requested_mode(m) if hasattr(reasoning, "requested_mode") else (None, None)
snap = {
    "model_slug": "glm5.3",
    "display_name": m.display_name,
    "requested_model": m.model_id,
    "served_model_observed_in_preflight": "glm5.3",
    "provider": m.provider,
    "gateway": "https://api.helmcode.com/v1 (HELMCODE_BASE_URL)",
    "api_style": m.api_style,
    "adapter": "mondaybench.providers.openai_compatible.OpenAICompatibleProvider",
    "temperature": m.temperature,
    "top_p": m.top_p,
    "top_p_note": "not pinned, therefore not sent; provider default applies. Accepted when probed (HTTP 200).",
    "max_output_tokens": m.max_output_tokens,
    "ceiling_semantics": CEILING_SEMANTICS,
    "reasoning_enabled": m.reasoning_enabled,
    "reasoning_mode": "UNOBSERVABLE (no mode parameter exposed by this gateway; model thinks by default)",
    "reasoning_effort": "UNOBSERVABLE (no effort parameter exposed by this gateway)",
    "extra_body": m.extra_body,
    "temperature_exception": None,
    "scenarios": {},
}
for sid in ["monday-001","monday-002","monday-003","monday-004","monday-005"]:
    loaded = load_scenario(sid)
    built = build_prompt(loaded)
    sh = reasoning.system_prompt_sha256(built.system_prompt)
    ceiling = effective_ceiling(loaded, m)
    ch = reasoning.generation_config_sha256(
        provider=m.provider, model_id=m.model_id, temperature=m.temperature,
        top_p=m.top_p, max_output_tokens=ceiling,
        reasoning_requested=m.reasoning_enabled, reasoning_mode=None,
        reasoning_effort=None, extra_body=m.extra_body, system_prompt_hash=sh)
    snap["scenarios"][sid] = {
        "prompt_sha256": built.sha256,
        "system_prompt_sha256": sh,
        "safety_ceiling_tokens": ceiling,
        "config_sha256": ch,
    }
Path(__file__).with_name("config-snapshot.json").write_text(json.dumps(snap, indent=2)+"\n", encoding="utf-8")
print(json.dumps(snap, indent=2))
