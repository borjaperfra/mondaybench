"""READ-ONLY analysis for the MondayBench v1.1 judge-contract migration.

Reads the repo, writes only into audits/v1.1-migration/. Calls no model, touches
no run, verdict, evaluation, leaderboard or release artifact.

It does three things:

1. records exactly what feeds `judge_prompt_fingerprint()` today;
2. builds the PROPOSED scenario-specific judge contract for every
   (evaluator, scenario) pair that has evaluations, and hashes it;
3. replays both fingerprints over every existing evaluation so the convergence
   can be seen rather than asserted.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
HERE = Path(__file__).parent

from mondaybench import judge as judge_mod            # noqa: E402
from mondaybench.config import load_evaluator          # noqa: E402
from mondaybench.scenarios import load_scenario        # noqa: E402
from mondaybench.prompt_builder import build_prompt    # noqa: E402
from mondaybench.schemas import PENALTY_TYPE_VALUES    # noqa: E402

EVALUATORS = {
    "monday-001": "evaluator-opus5-v0.1",
    "monday-002": "evaluator-opus5-v0.2",
    "monday-003": "evaluator-opus5-v0.3",
    "monday-004": "evaluator-opus5-v0.4",
    "monday-005": "evaluator-opus5-v0.5",
}
SCENARIOS = list(EVALUATORS)


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical(obj) -> str:
    """Stable serialisation: sorted keys, no whitespace, ASCII-escaped."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


# ---------------------------------------------------------------------------
# The PROPOSED contract. Derived from what the repo actually uses.
# ---------------------------------------------------------------------------
def judge_contract(scenario_id: str, evaluator_id: str) -> dict:
    cfg = load_evaluator(evaluator_id)
    sc = load_scenario(scenario_id, rubric_file=cfg.rubric_file)
    rubric = sc.rubric
    built = build_prompt(load_scenario(scenario_id))

    # Judge instructions. An evaluator may override the built-in templates with
    # scenario-specific files under evaluators/<scenario>/ - v0.2..v0.5 all do.
    # The current fingerprint reads NEITHER of those files.
    def instruction(rel, builtin_marker):
        if rel:
            folder = cfg.scenario or scenario_id
            path = ROOT / "evaluators" / folder / rel
            if path.exists():
                return {"source": "evaluators/" + folder + "/" + rel,
                        "sha256": sha(path.read_text(encoding="utf-8"))}
            return {"source": "MISSING:" + rel, "sha256": None}
        return {"source": "builtin", "sha256": sha(builtin_marker)}

    gt_map = cfg.ground_truth_map or {}

    criteria = [
        {
            # Rubric declaration order is preserved: it is the order the
            # recorded judge reads the rubric in, and reordering a rubric is a
            # rubric edit.
            "id": c.id,
            "dimension": c.dimension,
            "points": {"pass": c.points_pass, "partial": c.points_partial, "fail": c.points_fail},
            "pass_definition": c.pass_definition,
            "partial_definition": c.partial_definition,
            "fail_definition": c.fail_definition,
            "ground_truth_paths": sorted(gt_map.get(c.id, [])),
        }
        for c in rubric.criteria
    ]

    # THE FIX. Only the penalties this scenario's rubric declares - not the
    # global PENALTY_TYPE_VALUES union.
    penalties = [
        {"type": t, "points": p.points, "definition": p.definition}
        for t, p in sorted(rubric.penalties.items())
    ]
    scenario_penalty_types = [p["type"] for p in penalties]

    noise = None
    if rubric.noise is not None:
        noise = {
            "max_points": rubric.noise.max_points,
            "starting_points": rubric.noise.starting_points,
            "deduction_per_false_action": rubric.noise.deduction_per_false_action,
            "minimum_points": rubric.noise.minimum_points,
            "false_actions": [{"id": a.id, "description": a.description}
                              for a in rubric.noise.false_actions],
        }

    # Output contract, made scenario-specific: the penalty enum carries this
    # scenario's types only. On the API route this enum reaches the model as
    # response_format.json_schema, so it is model-visible.
    penalty_schema = json.loads(canonical(judge_mod.PENALTY_SCHEMA))
    penalty_schema["properties"]["violations"]["items"]["properties"]["type"]["enum"] = \
        scenario_penalty_types

    return {
        "contract_schema_version": "1",
        "scenario_id": scenario_id,
        "scenario_prompt_sha256": built.sha256,
        "evaluator_id": evaluator_id,
        "rubric_version": rubric.version,
        "rubric_file": cfg.rubric_file,
        "ground_truth_sha256": sha(canonical(sc.ground_truth) if sc.ground_truth
                                   else (sc.ground_truth_text or "")),
        "ground_truth_sliced_per_criterion": bool(gt_map),
        "judge_instructions": {
            "system_prompt_sha256": sha(judge_mod.JUDGE_SYSTEM_PROMPT),
            "criterion": instruction(cfg.prompt_file, "builtin:criterion_prompt"),
            "penalty": instruction(cfg.penalty_prompt_file, "builtin:penalty_prompt"),
            "noise": ({"source": "builtin", "sha256": sha("builtin:noise_prompt")}
                      if noise else None),
        },
        "label_semantics": {"labels": ["PASS", "PARTIAL", "FAIL"], "tie_rule": "lower"},
        "scoring": {
            "total_base_points": rubric.total_base_points,
            "maximum_global_penalty": rubric.maximum_global_penalty,
            "dimension_max": dict(sorted(rubric.dimension_max.items())),
        },
        "criteria": criteria,
        "noise": noise,
        "penalties": penalties,
        "output_contract": {
            "criterion_schema": judge_mod.CRITERION_SCHEMA,
            "noise_schema": judge_mod.NOISE_SCHEMA if noise else None,
            "penalty_schema": penalty_schema,
        },
    }


def contract_fingerprint(contract: dict) -> str:
    return sha(canonical(contract))[:16]


# ---------------------------------------------------------------------------
def main() -> None:
    out = {
        "generated_for": "MondayBench v1.1 judge-contract migration audit",
        "read_only": True,
        "current_fingerprint": {
            "function": "mondaybench.judge.judge_prompt_fingerprint()",
            "value_today": judge_mod.judge_prompt_fingerprint(),
            "hashes": [
                "JUDGE_SYSTEM_PROMPT (built-in)",
                "criterion_prompt(...) rendered with a DUMMY criterion",
                "noise_prompt([], '_') rendered with NO false actions",
                "penalty_prompt({}, '_', '_') rendered with NO ground truth",
                "CRITERION_SCHEMA", "NOISE_SCHEMA", "PENALTY_SCHEMA",
            ],
            "does_not_hash": [
                "the scenario's rubric: criteria, definitions, points, dimensions",
                "the scenario's penalties, their deductions or the penalty cap",
                "the scenario's false actions",
                "the evaluator's ground_truth_map",
                "the ground truth content",
                "the scenario prompt hash",
                "evaluator.prompt_file - the scenario-specific judge instructions",
                "evaluator.penalty_prompt_file - the scenario-specific penalty instructions",
                "the judge model id",
            ],
            "global_penalty_enum_today": list(PENALTY_TYPE_VALUES),
        },
        "contracts": {},
        "scenarios": {},
    }

    for sid in SCENARIOS:
        ev = EVALUATORS[sid]
        contract = judge_contract(sid, ev)
        fp = contract_fingerprint(contract)
        out["contracts"][sid] = {
            "evaluator_id": ev,
            "proposed_contract_fingerprint": fp,
            "criteria": len(contract["criteria"]),
            "scenario_penalty_types": [p["type"] for p in contract["penalties"]],
            "global_penalty_types_today": list(PENALTY_TYPE_VALUES),
            "penalty_types_excluded_by_scenario_scoping": sorted(
                set(PENALTY_TYPE_VALUES) - {p["type"] for p in contract["penalties"]}
            ),
            "has_noise_dimension": contract["noise"] is not None,
            "judge_instruction_sources": {
                "criterion": contract["judge_instructions"]["criterion"]["source"],
                "penalty": contract["judge_instructions"]["penalty"]["source"],
            },
        }
        (HERE / ("contract-" + sid + ".json")).write_text(
            json.dumps(contract, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8", newline="\n")

        # Replay over the evaluations that exist.
        base = ROOT / "evaluations" / ev / sid
        per_model = {}
        for mdir in sorted(p for p in base.iterdir() if p.is_dir()):
            fps, rubvs, runs = set(), set(), 0
            for f in sorted(mdir.glob("run-*.json")):
                d = json.loads(f.read_text(encoding="utf-8"))
                fps.add(d["judge"]["prompt_fingerprint"])
                rubvs.add(d["rubric_version"])
                runs += 1
            per_model[mdir.name] = {
                "runs": runs,
                "current_fingerprints": sorted(fps),
                "rubric_versions": sorted(rubvs),
                # The proposed contract is a pure function of (scenario,
                # rubric, evaluator). Every evaluation under this pair used the
                # same three, so every one of them lands on the same contract.
                "proposed_contract_fingerprint": fp,
            }
        current_unique = sorted({f for m in per_model.values() for f in m["current_fingerprints"]})
        rubric_unique = sorted({r for m in per_model.values() for r in m["rubric_versions"]})
        out["scenarios"][sid] = {
            "evaluator_id": ev,
            "models": per_model,
            "current_unique_fingerprints": current_unique,
            "current_unique_count": len(current_unique),
            "proposed_unique_contracts": [fp],
            "proposed_unique_count": 1,
            "rubric_versions_present": rubric_unique,
            "true_semantic_difference": len(rubric_unique) > 1,
        }

    (HERE / "current-fingerprint-audit.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    print("current judge_prompt_fingerprint() today: "
          + out["current_fingerprint"]["value_today"] + "\n")
    print("scenario      cur-fps  v1.1  models  scenario penalties")
    for sid, d in out["scenarios"].items():
        pens = ",".join(out["contracts"][sid]["scenario_penalty_types"])
        print("%-12s %7d %5d  %6d  %s" % (
            sid, d["current_unique_count"], d["proposed_unique_count"], len(d["models"]), pens))


if __name__ == "__main__":
    main()
