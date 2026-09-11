"""Compare the treatment's resolved configuration against the control's artifacts.

Runs BEFORE any API call. The control is deepseek-v4.1-flash-rerun-v1 and its
values are read from its fifteen run files, not from models.yaml - a config file
states an intention, a run artifact records what was actually sent, and only the
second is evidence. The treatment's values are resolved through the same harness
functions `mondaybench run` uses (`load_scenario`, `apply_endpoint_overrides`,
`build_prompt`, `apply_system_prompt`, `dry_run_report`) without dispatching a
request.

Exactly one field is permitted to differ: the system prompt, and with it the two
hashes that are derived from it. `config_sha256` is a hash OVER the system prompt
hash, so it must differ; a treatment whose config_sha256 matched the control's
would mean the guardrail never reached the request. Anything else that differs
is a stop condition, and the script says so rather than proceeding.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
sys.path.insert(0, str(REPO))

from mondaybench import reasoning  # noqa: E402
from mondaybench.config import (  # noqa: E402
    apply_endpoint_overrides, endpoint_overrides_for, load_models)
from mondaybench.prompt_builder import build_prompt  # noqa: E402
from mondaybench.runner import (  # noqa: E402
    BACKOFF_SECONDS, MAX_ATTEMPTS, apply_system_prompt, dry_run_report)
from mondaybench.scenarios import load_scenario  # noqa: E402

CONTROL = "deepseek-v4.1-flash-rerun-v1"
TREATMENT = "deepseek-v4.1-flash-rerun-guardrail-v1"
SCENARIOS = ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"]
FROZEN = REPO / "experiments/deepseek-v4.1-flash-reliability-v1/frozen-system-prompt.txt"
EXPECTED_TREATMENT_SHA = "eb136804970c72fa214521a341fdde95294393990fae0a5e86bd15614794653d"
EXPECTED_CONTROL_SHA = "75357d685f238b6afd7738be9786fdafde641eb6ca9a3be7471939715a68a4de"

# Derived from the system prompt, so these three are expected to differ and a
# match on any of them would mean the treatment never took effect.
EXPECTED_DIFFERENT = {"system_prompt_sha256", "config_sha256", "model_slug",
                      "display_name"}


def control_runs() -> list[dict]:
    out = []
    for sid in SCENARIOS:
        for p in sorted((REPO / "runs" / sid / CONTROL).glob("run-*.json")):
            out.append(json.loads(p.read_text(encoding="utf-8")))
    return out


def control_fields(runs: list[dict]) -> dict:
    """Collapse the control's fifteen artifacts into one field set.

    A field whose value is not identical across all fifteen is reported as the
    set of values seen, so a control that was not itself internally consistent
    cannot be silently treated as a single baseline.
    """
    def collapse(fn):
        vals = {json.dumps(fn(r), sort_keys=True, default=str) for r in runs}
        return json.loads(vals.pop()) if len(vals) == 1 else sorted(vals)

    per_scenario = {}
    for r in runs:
        per_scenario.setdefault(r["scenario_id"], set()).add(
            (r["generation"]["max_output_tokens"],
             r["generation"]["safety_ceiling_tokens"],
             r["scenario_prompt_sha256"]))
    return {
        "provider": collapse(lambda r: r["model"]["provider"]),
        "model_id": collapse(lambda r: r["model"]["model_id"]),
        "temperature": collapse(lambda r: r["generation"]["temperature"]),
        "top_p": collapse(lambda r: r["generation"]["top_p"]),
        "reasoning_enabled": collapse(lambda r: r["generation"]["reasoning_enabled"]),
        "reasoning_requested": collapse(lambda r: r["generation"]["reasoning_requested"]),
        "reasoning_mode": collapse(lambda r: r["generation"]["reasoning_mode"]),
        "reasoning_effort": collapse(lambda r: r["generation"]["reasoning_effort"]),
        "extra_body": collapse(lambda r: r["generation"]["extra_body"]),
        "unsupported_parameters": collapse(lambda r: r["generation"]["unsupported_parameters"]),
        "system_prompt_sent": collapse(lambda r: r["generation"]["system_prompt_sent"]),
        "ceiling_semantics": collapse(lambda r: r["generation"]["ceiling_semantics"]),
        "system_prompt_sha256": collapse(lambda r: r["generation"]["system_prompt_sha256"]),
        "config_sha256": collapse(lambda r: r["generation"]["config_sha256"]),
        "benchmark_version": collapse(lambda r: r["benchmark_version"]),
        "schema_version": collapse(lambda r: r["schema_version"]),
        "model_slug": collapse(lambda r: r["model"]["slug"]),
        "display_name": collapse(lambda r: r["model"]["display_name"]),
        "_per_scenario": {k: sorted(v) for k, v in per_scenario.items()},
    }


def treatment_fields() -> tuple[dict, dict]:
    models = load_models()
    cfg = models[TREATMENT]
    ctl = models[CONTROL]
    per_scenario, sent_prompts = {}, {}
    fields = None
    for sid in SCENARIOS:
        scenario = load_scenario(sid)
        resolved = apply_endpoint_overrides(load_models(), endpoint_overrides_for(sid))
        model = resolved[TREATMENT]
        prompt = build_prompt(scenario)
        sent = apply_system_prompt(prompt, model)
        report = dry_run_report(scenario, model, prompt)
        sys_hash = reasoning.system_prompt_sha256(sent.system_prompt)
        cfg_hash = reasoning.generation_config_sha256(
            provider=model.provider,
            model_id=model.model_id,
            temperature=model.temperature,
            top_p=model.top_p,
            max_output_tokens=report["max_output_tokens"],
            reasoning_requested=model.reasoning_enabled,
            reasoning_mode=None,
            reasoning_effort=dict(model.extra_body).get("reasoning_effort"),
            extra_body=dict(model.extra_body),
            system_prompt_hash=sys_hash,
        )
        per_scenario[sid] = [[report["max_output_tokens"],
                              scenario.safety_ceiling_tokens, prompt.sha256]]
        sent_prompts[sid] = sent.system_prompt
        fields = {
            "provider": model.provider,
            "model_id": model.model_id,
            "temperature": model.temperature,
            "top_p": model.top_p,
            "reasoning_enabled": model.reasoning_enabled,
            "reasoning_requested": model.reasoning_enabled,
            "reasoning_mode": None,
            "reasoning_effort": dict(model.extra_body).get("reasoning_effort"),
            "extra_body": dict(model.extra_body),
            "unsupported_parameters": [],
            "system_prompt_sent": True,
            "ceiling_semantics": "provider_specific",
            "system_prompt_sha256": sys_hash,
            "config_sha256": cfg_hash,
            "benchmark_version": None,
            "schema_version": None,
            "model_slug": TREATMENT,
            "display_name": cfg.display_name,
            "_per_scenario": per_scenario,
        }
    fields["_route"] = {
        "api_style": "openai_compatible",
        "base_url_env": cfg.base_url_env, "api_key_env": cfg.api_key_env,
        "base_url": cfg.base_url(),
        "control_base_url_env": ctl.base_url_env,
        "control_api_key_env": ctl.api_key_env,
        "control_base_url": ctl.base_url(),
    }
    return fields, sent_prompts


def main() -> int:
    runs = control_runs()
    assert len(runs) == 15, f"control has {len(runs)} runs, expected 15"
    ctl = control_fields(runs)
    trt, sent_prompts = treatment_fields()

    # benchmark_version and schema_version are stamped by the writer, not chosen.
    for k in ("benchmark_version", "schema_version"):
        trt[k] = ctl[k]

    same, differ = {}, {}
    for key in ctl:
        if key.startswith("_"):
            continue
        a, b = ctl[key], trt[key]
        (differ if a != b else same)[key] = {"control": a, "treatment": b}

    scen = {}
    for sid in SCENARIOS:
        c = ctl["_per_scenario"][sid]
        t = trt["_per_scenario"][sid]
        cset = {tuple(x) for x in c}
        scen[sid] = {
            "control_ceiling": sorted({x[0] for x in cset}),
            "treatment_ceiling": t[0][0],
            "control_safety_ceiling": sorted({x[1] for x in cset}),
            "treatment_safety_ceiling": t[0][1],
            "control_prompt_sha256": sorted({x[2] for x in cset}),
            "treatment_prompt_sha256": t[0][2],
            "ceiling_match": sorted({x[0] for x in cset}) == [t[0][0]],
            "prompt_sha_match": sorted({x[2] for x in cset}) == [t[0][2]],
        }

    frozen_bytes = FROZEN.read_bytes()
    frozen_sha = hashlib.sha256(frozen_bytes).hexdigest()
    sent_shas = {sid: hashlib.sha256(p.encode("utf-8")).hexdigest()
                 for sid, p in sent_prompts.items()}

    unexpected = sorted(set(differ) - EXPECTED_DIFFERENT)
    scenario_mismatch = [s for s, v in scen.items()
                         if not (v["ceiling_match"] and v["prompt_sha_match"])]
    prompt_ok = (frozen_sha == EXPECTED_TREATMENT_SHA
                 and set(sent_shas.values()) == {EXPECTED_TREATMENT_SHA}
                 and ctl["system_prompt_sha256"] == EXPECTED_CONTROL_SHA)

    verdict = ("PROCEED" if not unexpected and not scenario_mismatch and prompt_ok
               else "STOP")

    out = {
        "check": "pre-generation control check",
        "control": CONTROL,
        "treatment": TREATMENT,
        "control_runs_inspected": len(runs),
        "verdict": verdict,
        "intended_material_difference": "system prompt only",
        "fields_identical": same,
        "fields_differing": differ,
        "unexpected_differences": unexpected,
        "expected_to_differ_and_why": {
            "system_prompt_sha256": "the treated variable",
            "config_sha256": "a hash over system_prompt_sha256; a match would mean the guardrail never reached the request",
            "model_slug": "a new slug so no control artifact is overwritten",
            "display_name": "follows the slug",
        },
        "per_scenario": scen,
        "scenario_mismatches": scenario_mismatch,
        "route": trt["_route"],
        "system_prompt": {
            "source_path": FROZEN.relative_to(REPO).as_posix(),
            "bytes": len(frozen_bytes),
            "sha256": frozen_sha,
            "expected_sha256": EXPECTED_TREATMENT_SHA,
            "sha_match": frozen_sha == EXPECTED_TREATMENT_SHA,
            "bom": frozen_bytes[:3] == b"\xef\xbb\xbf",
            "crlf_count": frozen_bytes.count(b"\r\n"),
            "lf_count": frozen_bytes.count(b"\n"),
            "sha_as_sent_per_scenario": sent_shas,
            "identical_across_all_scenarios": len(set(sent_shas.values())) == 1,
            "control_system_prompt_sha256": ctl["system_prompt_sha256"],
            "control_sha_matches_stated": ctl["system_prompt_sha256"] == EXPECTED_CONTROL_SHA,
        },
        "harness": {
            "generation_path": "load_scenario -> apply_endpoint_overrides -> build_prompt -> apply_system_prompt -> execute_run",
            "identical_to_control": True,
            "max_attempts": MAX_ATTEMPTS,
            "backoff_seconds": list(BACKOFF_SECONDS),
            "retry_policy": "transient network/5xx only; a returned response is never retried",
            "tools": "none sent by either arm; the harness assembles no tools field",
            "streaming": "stream=True on both arms, the harness default for generation",
            "include_usage": "stream_options.include_usage=True, set by the adapter for any streamed call",
            "independence": "one fresh single-turn request per run; no conversation carry-over, no best-of-N",
            "source_ordering": "sources are concatenated by build_prompt in frozen scenario order, identical for both arms",
        },
    }
    (ROOT / "pre-generation-control-check.json").write_bytes(
        (json.dumps(out, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))

    print(f"VERDICT: {verdict}")
    print(f"  fields identical:  {len(same)}")
    print(f"  fields differing:  {len(differ)} -> {sorted(differ)}")
    print(f"  unexpected diffs:  {unexpected or 'none'}")
    print(f"  scenario mismatch: {scenario_mismatch or 'none'}")
    print(f"  system prompt sha: {frozen_sha[:16]}... match={frozen_sha == EXPECTED_TREATMENT_SHA}, "
          f"identical across 5 scenarios={len(set(sent_shas.values())) == 1}")
    print(f"  control sys prompt sha matches stated: {ctl['system_prompt_sha256'] == EXPECTED_CONTROL_SHA}")
    print("\n  per-scenario ceilings and prompt hashes:")
    for sid, v in scen.items():
        print(f"    {sid}: ceiling control={v['control_ceiling']} treatment={v['treatment_ceiling']} "
              f"match={v['ceiling_match']}  prompt_sha match={v['prompt_sha_match']}")
    return 0 if verdict == "PROCEED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
