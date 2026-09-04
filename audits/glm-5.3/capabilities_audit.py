"""Capability breakdown for GLM 5.3, computed with the canonical implementation.

Uses mondaybench/capabilities.py - the same functions `mondaybench capabilities`
calls - so the semantics are the repo's, not this file's: points awarded over
points available, counting only criteria whose PRIMARY mapping is that
capability, penalties excluded.

AUDIT ONLY, and deliberately not the published artifact. `mondaybench
capabilities` profiles models from OFFICIAL SCENARIO LEADERBOARDS, and GLM 5.3
is on none of them, so no official profile exists or should. This reads the
model's own stored evaluations instead and is written here, not into
analysis/capability-profiles-*.json.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from mondaybench.capabilities import (  # noqa: E402
    load_taxonomy, rubric_points, profiles_payload, official_criterion_results,
)
from mondaybench.config import load_evaluator  # noqa: E402
from mondaybench.scenarios import load_scenario  # noqa: E402

EVALUATORS = {
    "monday-001": "evaluator-opus5-v0.1",
    "monday-002": "evaluator-opus5-v0.2",
    "monday-003": "evaluator-opus5-v0.3",
    "monday-004": "evaluator-opus5-v0.4",
    "monday-005": "evaluator-opus5-v0.5",
}


for taxonomy_version in ("0.1", "0.2"):
    taxonomy = load_taxonomy(taxonomy_version)
    results, rubrics = {}, {}
    for sid in taxonomy.scenarios:
        ev = EVALUATORS[sid]
        cfg = load_evaluator(ev)
        rubrics[sid] = load_scenario(sid, rubric_file=cfg.rubric_file).rubric
        # The canonical reader, then filtered to this model. Averaging per
        # criterion across runs and the noise pseudo-criterion both come
        # from it rather than being reimplemented here.
        every = official_criterion_results(ev, sid)
        results[sid] = {"glm5.3": every["glm5.3"]}
    payload = profiles_payload(taxonomy, results, rubric_points(rubrics), {"glm5.3": "GLM 5.3"})
    payload["AUDIT_ONLY"] = (
        "Computed from GLM 5.3's own stored evaluations with mondaybench/capabilities.py. "
        "NOT an official capability profile: `mondaybench capabilities` profiles only models "
        "on official scenario leaderboards, and GLM 5.3 is on none."
    )
    target = Path(__file__).with_name(f"capabilities-summary-v{taxonomy_version}.json")
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    row = payload["models"][0]
    print(f"taxonomy {taxonomy_version}")
    for cid, v in row["capabilities"].items():
        sparse = next((c["sparse"] for c in payload["capabilities"] if c["id"] == cid), False)
        extra = " ".join(f"{k}={v[k]}" for k in sorted(v) if k != "percent")
        print(f"  {cid:<34} {v['percent']:>6.1f}%  {extra}" + ("  [sparse]" if sparse else ""))
    print()
