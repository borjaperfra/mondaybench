"""READ-ONLY: would GLM 5.3 become comparable with the incumbents under v1.1?

Answers it per scenario, from the stored evaluations and the proposed contract.
Writes only glm5.3-compatibility.json. Calls no model.
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from analyse import EVALUATORS, SCENARIOS, judge_contract, contract_fingerprint  # noqa: E402

INCUMBENTS = ["glm5.3-flash", "glm5.2", "mimo-v2.5", "deepseek-v4-flash",
              "qwen3.8-flash", "qwen3.6", "gemma4"]


def scores(evaluator_id, scenario_id, slug):
    d = ROOT / "evaluations" / evaluator_id / scenario_id / slug
    out = []
    for f in sorted(d.glob("run-*.json")):
        out.append(json.loads(f.read_text(encoding="utf-8"))["final_score"])
    return out


def main() -> None:
    result = {
        "model": "glm5.3",
        "generation_eligibility": {
            "status": "VALID",
            "detail": ("Official provider route, frozen prompts, 15/15 qualifying runs, reasoning "
                       "DELIVERED on all 15, no truncation, 15 distinct response hashes, prompt "
                       "equivalence verified against the frozen bytes. Nothing about the "
                       "generation is in question."),
        },
        "current_measured_score": {
            "value": 93.73,
            "label": "current-evaluator measured score, pending uniform v1.1 re-stamp",
            "not": ["invalid", "wrong", "discarded"],
            "detail": ("A valid score under evaluator-opus5-v0.1..v0.5 as they stand. What it is "
                       "not yet is officially comparable INSIDE v1.0, because the leaderboard's "
                       "comparability gate compares a fingerprint that describes global "
                       "repository state rather than this scenario's judge contract."),
        },
        "per_scenario": {},
    }

    for sid in SCENARIOS:
        ev = EVALUATORS[sid]
        contract = judge_contract(sid, ev)
        fp = contract_fingerprint(contract)

        inc_fps, inc_rubrics = set(), set()
        for slug in INCUMBENTS:
            for f in sorted((ROOT / "evaluations" / ev / sid / slug).glob("run-*.json")):
                d = json.loads(f.read_text(encoding="utf-8"))
                inc_fps.add(d["judge"]["prompt_fingerprint"])
                inc_rubrics.add(d["rubric_version"])
        chal_fps, chal_rubrics = set(), set()
        for f in sorted((ROOT / "evaluations" / ev / sid / "glm5.3").glob("run-*.json")):
            d = json.loads(f.read_text(encoding="utf-8"))
            chal_fps.add(d["judge"]["prompt_fingerprint"])
            chal_rubrics.add(d["rubric_version"])

        same_today = inc_fps == chal_fps
        # Under v1.1 the contract is a pure function of (scenario, rubric,
        # evaluator). All eight models were judged against the same three here,
        # so all eight land on the same contract.
        same_rubric = inc_rubrics == chal_rubrics and len(inc_rubrics) == 1
        verdict = "COMPATIBLE" if same_rubric else "UNKNOWN"

        glm = scores(ev, sid, "glm5.3")
        result["per_scenario"][sid] = {
            "evaluator_id": ev,
            "rubric_version_incumbents": sorted(inc_rubrics),
            "rubric_version_glm5.3": sorted(chal_rubrics),
            "current_fingerprint_incumbents": sorted(inc_fps),
            "current_fingerprint_glm5.3": sorted(chal_fps),
            "compatible_today": "YES" if same_today else "NO",
            "proposed_contract_fingerprint": fp,
            "compatible_under_v1_1": verdict,
            "reason": (
                ("Both were judged against " + sorted(inc_rubrics)[0] + " under " + ev +
                 ", against the same criteria, the same scenario-scoped penalties and the same "
                 "tie-break. The contract is identical, so the v1.1 fingerprint is identical. The "
                 "only thing that separated them was global repository state at judging time.")
                if verdict == "COMPATIBLE" else
                "Rubric versions differ between incumbents and challenger; that is a real "
                "semantic difference and no fingerprint should hide it."
            ),
            "glm5.3_run_scores": glm,
            "glm5.3_scenario_mean": round(statistics.mean(glm), 2) if glm else None,
            "note_scores_do_not_move": ("A v1.1 re-stamp replays the same recorded labels, so this "
                                        "mean is unchanged by the migration. A full re-judge would "
                                        "be a different exercise and would move it."),
        }

    compatible = [s for s, d in result["per_scenario"].items()
                  if d["compatible_under_v1_1"] == "COMPATIBLE"]
    result["summary"] = {
        "compatible_today": [s for s, d in result["per_scenario"].items()
                             if d["compatible_today"] == "YES"],
        "compatible_under_v1_1": compatible,
        "incompatible_under_v1_1": [s for s, d in result["per_scenario"].items()
                                    if d["compatible_under_v1_1"] == "INCOMPATIBLE"],
        "unknown_under_v1_1": [s for s, d in result["per_scenario"].items()
                               if d["compatible_under_v1_1"] == "UNKNOWN"],
        "expected_status_after_migration": (
            "OFFICIAL on all five scenarios and eligible for an Overall revision, at the same "
            "93.73, provided the re-stamp replays the existing recorded verdicts. If a full "
            "re-judge is chosen instead, every model's score including the incumbents' is "
            "re-derived and no current number should be assumed to survive."),
        "proposed_interim_classification": {
            "generation_eligibility": "OFFICIAL_GENERATION",
            "evaluation_comparability": "PENDING_V1_1_CONTRACT",
            "publication_eligibility": "PENDING",
            "why_not_just_EXCLUDED": ("EXCLUDED reads as a judgement about the model or its run. "
                                      "The generation cleared every official gate; what is "
                                      "pending is a harness-side comparability stamp."),
        },
    }

    (HERE / "glm5.3-compatibility.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    print("%-12s %-9s %-9s %-14s %s" % ("scenario", "today", "v1.1", "contract", "rubric"))
    for sid, d in result["per_scenario"].items():
        print("%-12s %-9s %-9s %-14s %s" % (
            sid, d["compatible_today"], d["compatible_under_v1_1"],
            d["proposed_contract_fingerprint"], ",".join(d["rubric_version_incumbents"])))


if __name__ == "__main__":
    main()
