"""Record the A-T blocking-test results and the release integrity state.

Runs pytest and reads the tree. Calls no model, writes only into this directory.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).parent
sys.path.insert(0, str(ROOT))

CONTRACT = "tests/test_judge_contract.py"
RELEASE = "tests/test_suite_v1_1.py"

# The audit's blocking set, mapped onto the tests that now enforce it.
BLOCKING = [
    ("A", "adding a monday-006 penalty does not change monday-001",
     f"{CONTRACT}::test_A_a_new_scenario_penalty_does_not_change_monday_001"),
    ("B", "changing a monday-001 penalty deduction changes the fingerprint",
     f"{CONTRACT}::test_B_changing_a_penalty_deduction_changes_the_fingerprint"),
    ("C", "changing monday-001 criterion wording changes the fingerprint",
     f"{CONTRACT}::test_C_changing_criterion_wording_changes_the_fingerprint"),
    ("D", "changing monday-005 does not change monday-001",
     f"{CONTRACT}::test_D_changing_monday_005_leaves_monday_001_alone"),
    ("E", "serialisation order does not change the fingerprint",
     f"{CONTRACT}::test_E_serialisation_order_does_not_change_the_fingerprint"),
    ("F", "reordering rubric criteria does change the fingerprint",
     f"{CONTRACT}::test_F_reordering_criteria_changes_the_fingerprint"),
    ("G", "non-operative metadata does not reach the contract",
     f"{CONTRACT}::test_G_non_operative_metadata_does_not_reach_the_contract"),
    ("H", "changing the label vocabulary changes the fingerprint",
     f"{CONTRACT}::test_H_changing_the_label_vocabulary_changes_the_fingerprint"),
    ("I", "changing the lower-label tie rule changes the fingerprint",
     f"{CONTRACT}::test_I_changing_the_tie_rule_changes_the_fingerprint"),
    ("J", "changing monday-003 factual anchors is confined to monday-003",
     f"{CONTRACT}::test_J_changing_monday_003_factual_anchors_is_confined_to_monday_003"),
    ("K", "future global enum additions do not move historical fingerprints",
     f"{CONTRACT}::test_K_no_historical_scenario_moves_when_the_global_enum_grows"),
    ("L", "a model judged today shares the incumbents' contract",
     f"{CONTRACT}::test_L_a_model_judged_today_shares_the_contract_of_earlier_incumbents"),
    ("M", "changing an external judge-prompt.md changes the fingerprint",
     f"{CONTRACT}::test_MN_changing_an_external_judge_prompt_changes_the_fingerprint[monday-003-criterion]"),
    ("N", "changing an external penalty-judge-prompt.md changes the fingerprint",
     f"{CONTRACT}::test_MN_changing_an_external_judge_prompt_changes_the_fingerprint[monday-004-penalty]"),
    ("O", "the rendered penalty enum equals the scenario's penalties",
     f"{CONTRACT}::test_O_the_rendered_penalty_enum_equals_the_scenarios_penalties"),
    ("P", "a v1.0 evaluation without a contract still loads",
     f"{CONTRACT}::test_P_a_v1_0_evaluation_without_a_contract_still_loads_and_keys_legacy"),
    ("Q", "the comparability gate cannot become a no-op",
     f"{CONTRACT}::test_Q_the_comparability_gate_cannot_become_a_no_op"),
    ("R", "verify-release 1.0 and 1.1 coexist",
     f"{RELEASE}::test_R_a_release_verifies_under_its_own_policy"),
    ("S", "publishing v1.1 writes nothing into v1.0's locations",
     f"{RELEASE}::test_S_the_v1_0_boards_carry_no_v1_1_model"),
    ("T", "an eighth official model enters every board",
     f"{RELEASE}::test_T_an_eighth_official_model_is_on_every_v1_1_board"),
]


def run(node_id: str) -> str:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--no-header", node_id],
        cwd=ROOT, capture_output=True, text=True,
    )
    return "PASS" if result.returncode == 0 else "FAIL"


def main() -> None:
    rows = []
    for letter, description, node in BLOCKING:
        rows.append({"test": letter, "description": description,
                     "node_id": node, "result": run(node)})
        print(f"  {rows[-1]['result']:<5} {letter}  {description}")

    full = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--no-header"],
        cwd=ROOT, capture_output=True, text=True,
    )
    tail = [line for line in full.stdout.strip().splitlines() if line.strip()][-1]

    (HERE / "contract-tests.json").write_text(json.dumps({
        "model_calls_during_testing": 0,
        "blocking_set": rows,
        "blocking_all_pass": all(r["result"] == "PASS" for r in rows),
        "full_suite": {"summary": tail, "exit_code": full.returncode},
        "count_based_assertions_rewritten": [
            {"test": "tests/test_capabilities.py::test_every_model_gets_a_profile",
             "was": "len(profiles) == 7",
             "now": "the profiled set equals the models with official results, no duplicates"},
            {"test": "tests/test_sample_provenance.py::test_D_...",
             "was": "len(live) == 21",
             "now": "the battery is whatever earned an evaluation, three per model, "
                    "with zero overlap against the calibration archive"},
            {"test": "tests/test_sample_provenance.py::test_E_...",
             "was": "len(ids) == len(set(ids)) == 21",
             "now": "every official sample is mutually distinct, whatever the count"},
            {"test": "tests/test_suite_release.py::test_the_manifest_digests_match_the_working_tree",
             "was": "byte-identity for every non-mutable group, which contradicted the "
                    "append_only policy it claimed to verify",
             "now": "byte-identity for immutable groups; a new test asserts the append_only "
                    "invariant - existing files unchanged, additions allowed"},
            {"test": "tests/test_cli_endpoints.py (x2)",
             "was": "a hardcoded served-model list of the seven original slugs",
             "now": "the stub's served list is derived from models.yaml"},
            {"test": "tests/test_challenge.py (x3) and tests/test_monday_005.py",
             "was": "the latest Overall release is v2; exactly three overall-v*.json files",
             "now": "the next revision extends whatever the latest base release is; the "
                    "earlier Overalls are asserted as a subset"},
            {"test": "tests/test_leaderboard_integrity.py::test_mixed_fingerprints_...",
             "was": "the warning text must suggest 're-evaluate every run'",
             "now": "the mix must be reported and both fingerprints named; the old remedy "
                    "would rewrite incumbent evidence and is no longer suggested"},
        ],
        "tests_deliberately_unchanged": {
            "tests/test_overall_v2.py": "asserts the frozen v1.0/v2 artifact; must stay green",
        },
    }, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("\nfull suite:", tail)


if __name__ == "__main__":
    main()
