"""Assemble the blind judging pack for the rerun battery. No judging happens here.

The battery holds one model, so hiding the model's identity would be theatre.
What can be hidden, and is, is which run is which: the three responses in a
scenario are shuffled behind opaque candidate ids and the mapping is written to
a separate file that stays shut until every label is frozen. That is what stops
a second or third response from being read as "the same model again, probably
about the same" instead of on its own.

The scrub check matters more than usual here. These runs were generated today
against a deployment whose reasoning volume differs sharply from the published
battery's, and a response that names its own model or date would let the judge
place it in that story.
"""
from __future__ import annotations
import hashlib, json, random, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from mondaybench.prompt_builder import build_prompt   # noqa: E402
from mondaybench.scenarios import load_scenario       # noqa: E402

SLUG = "deepseek-v4.1-flash-rerun-v1"
LABELS = ["CandidateA", "CandidateB", "CandidateC"]
LEAKS = ["deepseek", "v4.1", "v4-flash", "helmcode", "2026-09-11", "2026-09-10"]

def sha(b: bytes) -> str: return hashlib.sha256(b).hexdigest()

def main() -> int:
    rng = random.Random(20260911)
    pack_dir = OUT / "blind-judge-pack"; pack_dir.mkdir(parents=True, exist_ok=True)
    provenance, scrub = [], []
    for n in range(1, 6):
        sid = f"monday-00{n}"
        scenario = load_scenario(sid)
        prompt = build_prompt(scenario)
        runs = []
        for rp in sorted((ROOT / "runs" / sid / SLUG).glob("run-*.json")):
            r = json.loads(rp.read_text(encoding="utf-8"))
            runs.append((r["run_id"], r["response"]))
        assert len(runs) == 3, f"{sid}: {len(runs)} runs"
        order = list(range(3)); rng.shuffle(order)
        candidates = []
        for label, idx in zip(LABELS, order):
            run_id, text = runs[idx]
            hits = [t for t in LEAKS if t.lower() in text.lower()]
            scrub.append({"scenario_id": sid, "candidate_id": f"MB-{sid[-3:]}-{label}",
                          "identifying_strings_found": hits})
            candidates.append({"candidate_id": f"MB-{sid[-3:]}-{label}",
                               "display_label": label, "response": text,
                               "response_sha256": sha(text.encode("utf-8"))})
            provenance.append({"candidate_id": f"MB-{sid[-3:]}-{label}",
                               "scenario_id": sid, "run_id": run_id})
        pack = {"benchmark_suite": "MondayBench v1.4",
                "pack_type": "BLIND_INDEPENDENT_EVALUATION_PACK",
                "blind": True,
                "scenario": {"scenario_id": sid, "prompt_text": prompt.text,
                             "scenario_prompt_sha256": prompt.sha256},
                "candidates": candidates,
                "expected_output": {
                    "criteria_ids": [c.id for c in scenario.rubric.criteria],
                    "criteria_count": len(scenario.rubric.criteria),
                    "false_action_ids": [f.id for f in (scenario.rubric.noise.false_actions
                                                        if scenario.rubric.noise else [])],
                    "penalty_ids": list(scenario.rubric.penalties)}}
        (pack_dir / f"pack-{sid}.json").write_bytes(
            (json.dumps(pack, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        print(f"{sid}: 3 candidates, {len(scenario.rubric.criteria)} criteria, "
              f"{len(scenario.rubric.noise.false_actions) if scenario.rubric.noise else 0} false actions")
    (pack_dir / "scrub-log.json").write_bytes(
        (json.dumps(scrub, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    (OUT / "private-provenance-map.json").write_bytes(
        (json.dumps({"sealed_until": "all labels frozen", "candidates": provenance},
                    ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    leaked = [s for s in scrub if s["identifying_strings_found"]]
    print(f"\nscrub: {len(leaked)} candidatos con cadenas identificativas")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
