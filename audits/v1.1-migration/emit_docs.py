"""READ-ONLY: emit the remaining planning artifacts from the analyses already run."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from analyse import EVALUATORS, SCENARIOS, judge_contract, contract_fingerprint  # noqa: E402

audit = json.loads((HERE / "current-fingerprint-audit.json").read_text(encoding="utf-8"))
inv = json.loads((HERE / "rejudge-inventory.json").read_text(encoding="utf-8"))

# ---------------------------------------------------------------------------
# proposed-judge-contract.json - the specification, not one instance
# ---------------------------------------------------------------------------
spec = {
    "name": "MondayBench judge contract v1",
    "purpose": ("Answer 'did these two evaluations use the same scoring semantics APPLICABLE TO "
                "THIS SCENARIO?' - not 'did the repository hold identical global schemas at the "
                "moment each was written?'"),
    "fingerprint": {
        "function": "judge_contract_fingerprint(scenario, evaluator) -> str",
        "algorithm": "sha256(canonical_json(contract))[:16]",
        "canonical_json": ("json.dumps(obj, sort_keys=True, separators=(',',':'), "
                           "ensure_ascii=True) - key order, whitespace and unicode escaping are "
                           "all normalised, so serialisation cannot move the hash"),
        "stored_on": "Evaluation.judge.contract_fingerprint (new field)",
        "legacy_field": ("Evaluation.judge.prompt_fingerprint is KEPT and never rewritten, so "
                         "every v1.0 evaluation stays byte-identical and independently readable."),
    },
    "shape": {
        "contract_schema_version": "str - bumped when this object's shape changes",
        "scenario_id": "str",
        "scenario_prompt_sha256": "str - what the candidate was actually asked",
        "evaluator_id": "str",
        "rubric_version": "str",
        "rubric_file": "str",
        "ground_truth_sha256": "str - over the canonicalised answer key, or the prose text",
        "ground_truth_sliced_per_criterion": "bool - whether a ground_truth_map is in force",
        "judge_instructions": {
            "system_prompt_sha256": "str",
            "criterion": {"source": "evaluators/<scenario>/judge-prompt.md | builtin",
                          "sha256": "str"},
            "penalty": {"source": "evaluators/<scenario>/penalty-judge-prompt.md | builtin",
                        "sha256": "str"},
            "noise": "same shape, or null when the rubric has no noise dimension",
        },
        "label_semantics": {"labels": ["PASS", "PARTIAL", "FAIL"], "tie_rule": "lower"},
        "scoring": {"total_base_points": "float", "maximum_global_penalty": "float",
                    "dimension_max": "dict, key-sorted"},
        "criteria": ("array IN RUBRIC DECLARATION ORDER. Each entry: id, dimension, "
                     "points{pass,partial,fail}, the three definitions, and the sorted "
                     "ground_truth_paths that criterion's judge call may see."),
        "noise": "null, or {max_points, starting_points, deduction_per_false_action, "
                 "minimum_points, false_actions:[{id,description}]}",
        "penalties": ("array of {type, points, definition}, sorted by type, containing ONLY the "
                      "penalties this scenario's rubric declares"),
        "output_contract": {"criterion_schema": "object",
                            "noise_schema": "object or null",
                            "penalty_schema": "object whose type.enum is the scenario's penalties"},
    },
    "ordering_rules": {
        "criteria": ("declaration order preserved. It is the order the recorded judge reads the "
                     "rubric in, and reordering a rubric is a rubric edit that should move the "
                     "hash. This is what makes TEST F meaningful."),
        "penalties": "sorted by type - a dict has no meaningful order",
        "dimension_max": "key-sorted",
        "ground_truth_paths": "sorted",
        "everything_else": "key-sorted by canonical_json",
    },
    "deliberately_excluded": [
        "PENALTY_TYPE_VALUES - the global union. THE root cause; replaced by the scenario's own "
        "penalty list rather than merely dropped.",
        "timestamps, local paths, YAML comments, file mtimes",
        "any criterion, penalty or false action belonging to another scenario",
        "run-level data: responses, scores, model identity",
    ],
    "deliberately_included_that_is_not_today": [
        "the rubric itself - criteria, definitions, points, dimensions, the penalty cap",
        "the scenario's false actions",
        "evaluator.prompt_file and evaluator.penalty_prompt_file, the scenario-specific judge "
        "instructions that v0.2..v0.5 all declare and that the current fingerprint never reads",
        "the ground truth content and the per-criterion ground_truth_map",
        "the scenario prompt hash",
    ],
    "instances": {},
}
for sid in SCENARIOS:
    c = judge_contract(sid, EVALUATORS[sid])
    spec["instances"][sid] = {
        "evaluator_id": EVALUATORS[sid],
        "contract_fingerprint": contract_fingerprint(c),
        "criteria": len(c["criteria"]),
        "penalties": [p["type"] for p in c["penalties"]],
        "noise_dimension": c["noise"] is not None,
        "full_contract_file": "contract-" + sid + ".json",
    }
(HERE / "proposed-judge-contract.json").write_text(
    json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

# ---------------------------------------------------------------------------
# historical-dry-run.json
# ---------------------------------------------------------------------------
rows = []
for sid in SCENARIOS:
    d = audit["scenarios"][sid]
    models = sorted(d["models"])
    rows.append({
        "scenario": sid,
        "evaluator_id": d["evaluator_id"],
        "current_unique_fingerprints": d["current_unique_count"],
        "current_fingerprint_values": d["current_unique_fingerprints"],
        "v1_1_unique_contracts": d["proposed_unique_count"],
        "v1_1_contract_value": d["proposed_unique_contracts"][0],
        "models": len(models),
        "model_slugs": models,
        "rubric_versions_present": d["rubric_versions_present"],
        "true_semantic_differences": bool(d["true_semantic_difference"]),
        "converging_evaluations": sum(m["runs"] for m in d["models"].values()),
        "note": ("Every evaluation under this pair used one scenario, one rubric file and one "
                 "evaluator, so all of them land on one contract. The split visible today is "
                 "global repository state, not semantics."),
    })
dry = {
    "read_only": True,
    "no_files_mutated": True,
    "question": ("If the v1.1 contract fingerprint had existed all along, how many distinct judge "
                 "contracts would each scenario have?"),
    "rows": rows,
    "totals": {
        "evaluations_examined": sum(r["converging_evaluations"] for r in rows),
        "current_distinct_fingerprints_overall": len(
            {f for r in rows for f in r["current_fingerprint_values"]}),
        "v1_1_distinct_contracts_overall": len({r["v1_1_contract_value"] for r in rows}),
        "scenarios_with_a_true_semantic_difference": sum(
            1 for r in rows if r["true_semantic_differences"]),
    },
    "interpretation": ("Four of the five scenarios currently carry two fingerprints and would "
                       "carry one. The fifth already carries one. No scenario has a genuine "
                       "semantic split: every evaluation in a scenario was judged against a "
                       "single rubric version under a single evaluator."),
}
(HERE / "historical-dry-run.json").write_text(
    json.dumps(dry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

# ---------------------------------------------------------------------------
# estimated-rejudge-cost.json
# ---------------------------------------------------------------------------
cost = {
    "read_only": True,
    "no_model_was_called": True,
    "scope": {
        "official_models": inv["official_models"],
        "official_judged_responses": inv["total_official_responses"],
        "regeneration_required": inv["regeneration_required"],
        "blockers": inv["blockers"],
    },
    "option_rescore_only": inv["route_rescore_only"],
    "option_full_rejudge_recorded_route": inv["route_recorded_judge"],
    "option_full_rejudge_api_route": inv["route_api_judge"],
    "optional_provisional_rejudge": {
        "models": inv["provisional_models_out_of_scope"]["models"],
        "in_official_scope": False,
        "why": inv["provisional_models_out_of_scope"]["why"],
        "cost_if_ever_done": ("Two more models across five scenarios is 2/8 of the official "
                              "re-judge, so roughly 713 further criterion verdicts on the same "
                              "assumptions. It buys evaluation comparability for generations that "
                              "remain non-comparable, which is why it is listed and not "
                              "recommended."),
    },
    "per_scenario_judge_work": inv["per_scenario_judge_work"],
    "honesty_note": ("There is no historical judge token data to calibrate against: JudgeRecord "
                     "stores no token counts and every published evaluation used route=recorded, "
                     "so the API figures are a sizing exercise built from measured prompt "
                     "material and a stated chars-per-token assumption, not a quote."),
}
(HERE / "estimated-rejudge-cost.json").write_text(
    json.dumps(cost, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

print("wrote proposed-judge-contract.json, historical-dry-run.json, estimated-rejudge-cost.json")
for r in rows:
    print("  %-12s %d -> %d contracts, %d models, %d evaluations" % (
        r["scenario"], r["current_unique_fingerprints"], r["v1_1_unique_contracts"],
        r["models"], r["converging_evaluations"]))
