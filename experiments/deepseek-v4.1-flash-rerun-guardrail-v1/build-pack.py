"""Blind pack, private provenance and scrub log. No judging happens here.

Each pack carries the frozen scenario prompt, the frozen sources, the frozen
rubric and the frozen ground truth alongside three candidate responses under
opaque labels. The response bytes are copied verbatim from the run artifacts and
re-hashed afterwards, so a pack whose candidate text drifted from the run it came
from is caught rather than shipped.

The provenance map is written OUTSIDE the pack directory. The scrub check then
reads the packs back off disk and looks for the forbidden strings in the metadata
the pack itself adds - not in the frozen scenario text, sources, rubric, ground
truth or candidate responses, which must stay byte-exact even when an ordinary
word inside them happens to collide with the list.
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
sys.path.insert(0, str(REPO))

from mondaybench.config import load_evaluator  # noqa: E402
from mondaybench.prompt_builder import build_prompt  # noqa: E402
from mondaybench.scenarios import load_scenario  # noqa: E402

SLUG = "deepseek-v4.1-flash-rerun-guardrail-v1"
SCENARIOS = ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"]
EVALUATORS = {
    "monday-001": "evaluator-opus5-v0.1", "monday-002": "evaluator-opus5-v0.2",
    "monday-003": "evaluator-opus5-v0.3", "monday-004": "evaluator-opus5-v0.4",
    "monday-005": "evaluator-opus5-v0.5",
}
LABELS = ["Candidate A", "Candidate B", "Candidate C"]
BLIND_SEED = 20260911

# Checked against the metadata a pack adds, never against frozen content.
FORBIDDEN = ["DeepSeek", "deepseek", "V4.1", "v4.1", "guardrail", "reliability",
             "treatment", "experiment", "system_prompt", "system prompt",
             "Helmcode", "helmcode", "rerun-guardrail", "run_number", "run_id",
             "Monday Score", "leaderboard"]


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def criterion_dict(c) -> dict:
    return {"id": c.id, "dimension": c.dimension,
            "points": {"pass": c.points_pass, "partial": c.points_partial,
                       "fail": c.points_fail},
            "pass_definition": c.pass_definition,
            "partial_definition": c.partial_definition,
            "fail_definition": c.fail_definition}


def main() -> int:
    rng = random.Random(BLIND_SEED)
    pack_dir = ROOT / "blind-judge-pack"
    pack_dir.mkdir(parents=True, exist_ok=True)
    provenance, scrub_rows = [], []

    for sid in SCENARIOS:
        evaluator = load_evaluator(EVALUATORS[sid])
        loaded = load_scenario(sid, rubric_file=evaluator.rubric_file)
        scenario = loaded.scenario if hasattr(loaded, "scenario") else loaded
        prompt = build_prompt(load_scenario(sid))

        runs = []
        run_dir = ROOT / "runs" / sid / SLUG
        for p in sorted(run_dir.glob("run-*.json")):
            d = json.loads(p.read_text(encoding="utf-8"))
            runs.append((p, d))
        assert len(runs) == 3, f"{sid}: {len(runs)} runs"

        order = list(range(3))
        rng.shuffle(order)
        candidates = []
        for label, idx in zip(LABELS, order):
            path, d = runs[idx]
            text = d["response"]
            candidates.append({"candidate_id": f"{sid}-{label.split()[-1]}",
                               "label": label, "response": text,
                               "response_sha256": sha(text.encode("utf-8"))})
            provenance.append({
                "scenario_id": sid, "candidate_id": f"{sid}-{label.split()[-1]}",
                "label": label, "run_id": d["run_id"], "run_number": d["run_number"],
                "run_file": path.relative_to(REPO).as_posix(),
                "response_sha256": sha(text.encode("utf-8")),
                "telemetry": {
                    "reasoning_tokens": d["reasoning"]["tokens"],
                    "reasoning_status": d["reasoning"]["status"],
                    "output_tokens": d["usage"]["output_tokens"],
                    "input_tokens": d["usage"]["input_tokens"],
                    "ttft_ms": d["performance"]["ttft_ms"],
                    "ttfa_ms": d["performance"]["ttfa_ms"],
                    "total_latency_ms": d["performance"]["total_latency_ms"],
                    "tokens_per_second": d["performance"]["tokens_per_second"],
                    "finish_reason": d["finish_reason"],
                    "max_output_tokens": d["generation"]["max_output_tokens"],
                    "request_id": d["provider_metadata"]["request_id"],
                },
            })

        noise = scenario.rubric.noise
        pack = {
            "pack_type": "BLIND_INDEPENDENT_EVALUATION_PACK",
            "blind": True,
            "scenario_id": sid,
            "scenario_prompt": prompt.text,
            "scenario_prompt_sha256": prompt.sha256,
            "rubric": {
                "version": scenario.rubric.version,
                "total_base_points": scenario.rubric.total_base_points,
                "maximum_global_penalty": scenario.rubric.maximum_global_penalty,
                "dimension_max": scenario.rubric.dimension_max,
                "criteria": [criterion_dict(c) for c in scenario.rubric.criteria],
                "penalties": {k: {"points": v.points, "definition": v.definition}
                              for k, v in scenario.rubric.penalties.items()},
                "noise": (None if noise is None else {
                    "starting_points": noise.starting_points,
                    "deduction_per_false_action": noise.deduction_per_false_action,
                    "minimum_points": noise.minimum_points,
                    "max_points": noise.max_points,
                    "false_actions": [{"id": f.id, "description": getattr(f, "description", None)}
                                      for f in noise.false_actions]}),
            },
            "ground_truth": json.loads(json.dumps(
                scenario.ground_truth, default=str)) if getattr(scenario, "ground_truth", None) else None,
            "candidates": candidates,
        }
        out = pack_dir / f"pack-{sid}.json"
        out.write_bytes((json.dumps(pack, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        print(f"{sid}: 3 candidates, {len(scenario.rubric.criteria)} criteria -> {out.name}")

    (ROOT / "private-provenance-map.json").write_bytes((json.dumps({
        "private": True,
        "do_not_place_in_blind_judge_pack": True,
        "experiment": "deepseek-v4.1-flash-rerun-guardrail-v1",
        "model": "DeepSeek V4.1 Flash",
        "model_slug": SLUG,
        "model_id": "deepseek-v4-flash",
        "provider": "helmcode",
        "treatment": "frozen reliability guardrail system prompt",
        "system_prompt_sha256": "eb136804970c72fa214521a341fdde95294393990fae0a5e86bd15614794653d",
        "control": "deepseek-v4.1-flash-rerun-v1",
        "blind_seed": BLIND_SEED,
        "candidates": provenance,
    }, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))

    # ---- scrub ------------------------------------------------------------
    prov_by_cand = {p["candidate_id"]: p for p in provenance}
    for sid in SCENARIOS:
        raw = (pack_dir / f"pack-{sid}.json").read_text(encoding="utf-8")
        pack = json.loads(raw)
        # Walk the structure rather than the serialised text. A string search
        # over the file cannot tell the pack's own metadata from an ordinary
        # English word inside the frozen rubric - monday-004's rubric says "Any
        # equivalent treatment" and its ground truth says "two treatments", and
        # both must survive byte-exact. FROZEN_PATHS names the regions that are
        # content; everything else is metadata this pack added, and only that is
        # searched.
        FROZEN_PATHS = ("scenario_prompt", "rubric", "ground_truth")
        def metadata_strings(obj, path=()):
            if path and path[0] in FROZEN_PATHS:
                return
            if path[:1] == ("candidates",) and path[-1:] == ("response",):
                return
            if isinstance(obj, dict):
                for k, v in obj.items():
                    yield str(k)
                    yield from metadata_strings(v, path + (k,))
            elif isinstance(obj, list):
                for v in obj:
                    yield from metadata_strings(v, path)
            elif isinstance(obj, str):
                yield obj
        metadata = chr(10).join(metadata_strings(pack))
        hits = sorted({t for t in FORBIDDEN if t in metadata})

        shas = [c["response_sha256"] for c in pack["candidates"]]
        byte_match = []
        for c in pack["candidates"]:
            p = prov_by_cand[c["candidate_id"]]
            src = json.loads((REPO / p["run_file"]).read_text(encoding="utf-8"))["response"]
            byte_match.append(src == c["response"]
                              and sha(src.encode("utf-8")) == c["response_sha256"])
        scrub_rows.append({
            "scenario_id": sid,
            "forbidden_metadata_hits": hits,
            "candidate_count": len(pack["candidates"]),
            "exactly_three_candidates": len(pack["candidates"]) == 3,
            "unique_response_sha_count": len(set(shas)),
            "no_duplicate_response_sha": len(set(shas)) == 3,
            "candidate_bytes_match_run_artifacts": all(byte_match),
            "provenance_absent_from_pack": not (pack_dir / "private-provenance-map.json").exists(),
            "candidate_keys": sorted({k for c in pack["candidates"] for k in c}),
            "system_prompt_absent_from_pack": "eb136804970c72fa" not in raw,
        })

    (ROOT / "scrub-log.json").write_bytes((json.dumps({
        "forbidden_terms_checked": FORBIDDEN,
        "scope": "metadata the pack adds; frozen prompt, sources, rubric, ground truth and candidate responses are excluded from the search and preserved byte-exact",
        "scenarios": scrub_rows,
        "all_clear": all(not r["forbidden_metadata_hits"] and r["exactly_three_candidates"]
                         and r["no_duplicate_response_sha"]
                         and r["candidate_bytes_match_run_artifacts"]
                         and r["system_prompt_absent_from_pack"] for r in scrub_rows),
    }, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))

    print()
    for r in scrub_rows:
        print(f"  {r['scenario_id']}: forbidden={r['forbidden_metadata_hits'] or 'none'}  "
              f"3 candidates={r['exactly_three_candidates']}  unique SHAs={r['no_duplicate_response_sha']}  "
              f"bytes match runs={r['candidate_bytes_match_run_artifacts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
