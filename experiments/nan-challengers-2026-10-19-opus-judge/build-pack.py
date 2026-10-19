"""Build the blind judge pack for the two NaN challengers of 2026-10-19.

One pack per model, because the two batteries finished hours apart. For each
scenario, takes the model's three OFFICIAL runs (as `plan_model` qualifies them
- prompt hash, ceiling, provider, reasoning delivery, no cached duplicates),
shuffles them under a fixed seed and gives them anonymous candidate ids. The
judges see only `pack/<key>/blind-judge-pack.json`; the join back to runs
lives in `pack/<key>/provenance-map.json`, which they are forbidden to open.
`<key>` is the first 8 hex of sha256(slug), so the path does not name the model.

Usage:  python experiments/nan-challengers-2026-10-19-opus-judge/build-pack.py <slug>
"""
from __future__ import annotations

import hashlib
import json
import random
import string
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from mondaybench.config import apply_endpoint_overrides, endpoint_overrides_for, load_models  # noqa: E402
from mondaybench.official import plan_model                  # noqa: E402
from mondaybench.prompt_builder import build_prompt          # noqa: E402
from mondaybench.scenarios import load_scenario              # noqa: E402

SCEN = ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"]
SEED = 20261019


def pack_key(slug: str) -> str:
    return hashlib.sha256(slug.encode("utf-8")).hexdigest()[:8]


def main(slug: str) -> int:
    out = HERE / "pack" / pack_key(slug)
    out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    pack = {"pack_type": "blind-judge-pack", "blind_seed": SEED,
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "scenarios": []}
    prov = {"blind_seed": SEED, "created_at": pack["created_at"], "scenarios": {}}
    problems = []
    for sid in SCEN:
        loaded = load_scenario(sid)
        prompt = build_prompt(loaded)
        models = apply_endpoint_overrides(load_models(), endpoint_overrides_for(sid))
        plan = plan_model(scenario_id=sid, model_slug=slug, model=models.get(slug),
                          expected_prompt_sha256=prompt.sha256,
                          expected_max_output_tokens=loaded.safety_ceiling_tokens)
        if len(plan.official) < 3:
            problems.append(f"{sid} {slug}: {len(plan.official)} official runs")
        runs = [v.run for v in plan.official[:3]]
        rng.shuffle(runs)
        cands, pmap = [], []
        for letter, run in zip(string.ascii_uppercase, runs):
            cid = f"MB-{sid[-3:]}-Candidate{letter}"
            sha = hashlib.sha256(run.response.encode("utf-8")).hexdigest()
            cands.append({"candidate_id": cid, "display_label": f"Candidate {letter}",
                          "response": run.response, "response_sha256": sha})
            pmap.append({"candidate_id": cid, "true_run_id": run.run_id,
                         "model_slug": run.model.slug, "response_sha256": sha})
        pack["scenarios"].append({"scenario_id": sid, "candidates": cands})
        prov["scenarios"][sid] = pmap
    if problems:
        print("STOP:", *problems, sep="\n  ")
        return 1
    for name, obj in (("blind-judge-pack.json", pack), ("provenance-map.json", prov)):
        (out / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n",
                                          encoding="utf-8", newline="\n")
    print("pack written to", out.relative_to(ROOT), ":", {s["scenario_id"]: len(s["candidates"]) for s in pack["scenarios"]})
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
