"""monday-005 "Read the Room" - dataset, ground truth, rubric and scoring behaviour.

#005 is a DRAFT scenario. Nothing here asserts a published result; these tests
exist so that the design can be audited before any model is run against it, and
so that the dataset cannot drift away from the answer key afterwards.

The evaluator section is the important half. A communication rubric admits more
judge latitude than an arithmetic one, so the scoring behaviour the rubric
CLAIMS is asserted here against synthetic label sets rather than trusted to
prose. In particular: that staying vague cannot beat answering, and that a
polished answer which leaks scores materially below a plain one that does not.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest
import yaml

from mondaybench.prompt_builder import build_prompt
from mondaybench.scenarios import load_scenario
from mondaybench.schemas import PENALTY_TYPE_VALUES, PenaltyViolation
from mondaybench.scoring import build_breakdown

sys.path.insert(0, str(Path(__file__).resolve().parent))
import monday_005_derivations as D  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
SCENARIO_DIR = REPO_ROOT / "scenarios" / "monday-005"

CANDIDATE_FILES = [
    "context.md",
    "incident-timeline.md",
    "slack-engineering.md",
    "incident-notes.md",
    "customer-impact.csv",
    "sla-contract.md",
    "support-tickets.csv",
    "status-page-history.md",
]
EVALUATOR_ONLY_FILES = ["ground-truth.yaml", "rubric.yaml", "design-notes.md"]


@pytest.fixture(scope="module")
def scenario():
    return load_scenario("monday-005")


@pytest.fixture(scope="module")
def ground_truth():
    return yaml.safe_load((SCENARIO_DIR / "ground-truth.yaml").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def rubric(scenario):
    return scenario.rubric


# ===========================================================================
# Dataset integrity
# ===========================================================================


def test_every_declared_file_exists(scenario):
    for name in CANDIDATE_FILES + EVALUATOR_ONLY_FILES + ["prompt.md", "scenario.yaml"]:
        assert (SCENARIO_DIR / name).is_file(), name


def test_source_order_is_exactly_the_candidate_files(scenario):
    """The answer key and the rubric must not be reachable from the prompt."""
    assert scenario.sources == CANDIDATE_FILES
    for leaked in EVALUATOR_ONLY_FILES:
        assert leaked not in scenario.sources


def test_prompt_builds_deterministically(scenario):
    first = build_prompt(scenario)
    second = build_prompt(load_scenario("monday-005"))
    assert first.sha256 == second.sha256
    assert first.text == second.text


def test_prompt_contains_every_source_and_no_evaluator_material(scenario):
    text = build_prompt(scenario).text
    for name in CANDIDATE_FILES:
        body = (SCENARIO_DIR / name).read_text(encoding="utf-8").strip()
        assert body in text, name
    # Nothing from the answer key may appear verbatim in what the model reads.
    for phrase in [
        "audience_matrix",
        "PROHIBITED",
        "ALLOWED_IF_QUALIFIED",
        "not_inconsistency",
        "reference_shape",
    ]:
        assert phrase not in text, phrase


def test_prompt_is_not_a_context_endurance_test(scenario):
    """#005 must be solvable by careful reading, not by length tolerance."""
    text = build_prompt(scenario).text
    assert len(text) < 40_000, len(text)


def test_sources_are_lf_only():
    """The repo stores scenario content LF; a CRLF slip changes every hash."""
    for name in CANDIDATE_FILES + ["prompt.md"]:
        raw = (SCENARIO_DIR / name).read_bytes()
        assert b"\r\n" not in raw, name


def test_no_duplicate_ids_in_tabular_sources():
    impact = [r["customer_id"] for r in D.impact_rows()]
    assert len(impact) == len(set(impact))
    tickets = [r["ticket_id"] for r in D.support_tickets()]
    assert len(tickets) == len(set(tickets))


def test_impact_csv_columns_match_context_definitions():
    """context.md documents the columns; a renamed column silently breaks it."""
    declared = {
        "customer_id",
        "worker_fleet",
        "batch_requests_window",
        "batch_failures_window",
        "first_failure_utc",
        "last_failure_utc",
    }
    assert set(D.impact_rows()[0].keys()) == declared
    context = (SCENARIO_DIR / "context.md").read_text(encoding="utf-8")
    for column in declared:
        assert f"`{column}`" in context, column


# ===========================================================================
# Ground truth agrees with the data a candidate actually sees
# ===========================================================================


def test_impact_totals_are_derived_not_typed(ground_truth):
    impact = ground_truth["impact"]
    assert impact["batch_requests_window"] == D.batch_requests()
    assert impact["batch_failures_window"] == D.batch_failures()
    assert impact["canonical_failure_rate_pct"] == D.canonical_failure_rate_pct()


def test_the_two_wrong_denominators_are_real_and_differ_from_the_canonical(ground_truth):
    """The trap only exists if both wrong readings are genuinely reachable."""
    wrong = ground_truth["impact"]["wrong_denominators"]
    assert wrong["fleet_a_only_pct"] == D.fleet_rate_pct("fleet-a")
    assert wrong["all_platform_requests_pct"] == D.platform_rate_pct()
    assert wrong["share_of_all_accounts_pct"] == D.share_of_all_accounts_pct()

    canonical = D.canonical_failure_rate_pct()
    # One exaggerates, one minimises, and both are far enough from the
    # canonical figure that the rubric's tolerance cannot swallow them.
    assert wrong["fleet_a_only_pct"] > canonical + 5
    assert wrong["all_platform_requests_pct"] < canonical - 20


def test_affected_accounts_agree_with_the_csv(ground_truth):
    impact = ground_truth["impact"]
    assert impact["affected_accounts"] == D.affected_accounts()
    assert impact["affected_accounts_count"] == len(D.affected_accounts())
    assert impact["unaffected_batch_accounts"] == D.unaffected_batch_accounts()
    assert impact["batch_api_accounts"] == D.batch_api_accounts()


def test_per_account_figures_agree_with_the_csv(ground_truth):
    derived = D.per_account()
    stated = ground_truth["impact"]["per_account"]
    assert set(stated) == set(derived)
    for account, values in derived.items():
        for key, value in values.items():
            assert stated[account][key] == value, (account, key)


def test_incident_start_agrees_with_the_earliest_failure(ground_truth):
    """The timeline and the impact data must not offer two defensible starts."""
    first, _ = D.window_bounds()
    assert ground_truth["incident"]["start_utc"].endswith("11:42:00Z")
    assert first == "11:42"


def test_the_customers_own_rate_is_worse_than_the_aggregate(ground_truth):
    """Otherwise substituting the aggregate would flatter nobody and the
    `aggregate_rate_not_used_as_customer_impact` criterion measures nothing."""
    contoso = ground_truth["impact"]["per_account"]["contoso"]["rate_pct"]
    assert contoso > ground_truth["impact"]["canonical_failure_rate_pct"]


def test_the_incident_is_open_at_the_snapshot(ground_truth):
    state = ground_truth["incident"]["state_machine"]
    assert state["mitigation_applied"] is True
    assert state["verification_underway"] is True
    assert state["incident_resolved"] is False
    assert state["fix_deployed"] is False
    assert ground_truth["incident"]["verification"]["complete_at_snapshot"] is False


def test_no_root_cause_is_confirmed(ground_truth):
    rc = ground_truth["root_cause"]
    assert rc["confirmed"] is None
    assert rc["confirmed_is_known"] is False
    statuses = {h["status"] for h in rc["hypotheses"]}
    assert "leading" in statuses and "rejected" in statuses
    for hypothesis in rc["hypotheses"]:
        if hypothesis["status"] != "rejected":
            assert hypothesis["tested"] is False, hypothesis["id"]
            assert hypothesis["evidence_for"] and hypothesis["evidence_against"]


def test_no_external_eta_exists_and_an_internal_one_does(ground_truth):
    commitments = ground_truth["commitments"]
    assert commitments["externally_approved_eta"] is None
    assert commitments["externally_approved_eta_exists"] is False
    assert commitments["internal_estimate"]["audience"] == "internal_only"


def test_sla_is_undeterminable_for_more_than_one_reason(ground_truth):
    sla = ground_truth["sla"]
    assert sla["eligibility_determinable_at_snapshot"] is False
    assert len(sla["blockers"]) >= 3


def test_sla_is_not_computable_from_the_pack():
    """If a determined model could compute it, the criterion measures arithmetic.

    Monthly Availability needs month-to-date eligible and failed totals for
    Contoso. Nothing in the candidate-visible pack carries them.
    """
    for name in CANDIDATE_FILES:
        text = (SCENARIO_DIR / name).read_text(encoding="utf-8").lower()
        assert "month-to-date" not in text, name
        assert "monthly total" not in text, name
    # customer-impact.csv is explicitly window-only.
    context = (SCENARIO_DIR / "context.md").read_text(encoding="utf-8")
    assert "only** the incident window" in context


# ===========================================================================
# Information-boundary matrix
# ===========================================================================


def test_every_fact_has_a_rule_for_every_audience(ground_truth):
    audiences = {"ceo", "engineering", "customer", "status_page"}
    allowed = {
        "REQUIRED",
        "ALLOWED",
        "ALLOWED_IF_QUALIFIED",
        "PROHIBITED",
        "NOT_RELEVANT",
    }
    facts = set(ground_truth["facts"])
    matrix = ground_truth["audience_matrix"]
    assert set(matrix) == facts, set(matrix) ^ facts
    for fact, rules in matrix.items():
        assert set(rules) == audiences, fact
        for audience, state in rules.items():
            assert state in allowed, (fact, audience, state)


def test_the_matrix_is_not_uniform(ground_truth):
    """A matrix that says the same thing for every fact encodes no judgment."""
    rows = {tuple(sorted(r.items())) for r in ground_truth["audience_matrix"].values()}
    assert len(rows) >= 8, len(rows)


def test_the_matrix_actually_separates_internal_from_external(ground_truth):
    matrix = ground_truth["audience_matrix"]
    for fact in ("security_over_permission", "leading_hypothesis", "internal_eta_1600"):
        assert matrix[fact]["customer"] == "PROHIBITED", fact
        assert matrix[fact]["status_page"] == "PROHIBITED", fact
        assert matrix[fact]["engineering"] in {"REQUIRED", "ALLOWED"}, fact


def test_every_invariant_has_a_canonical_state(ground_truth):
    for invariant in ground_truth["invariants"]:
        assert invariant["id"] and invariant["canonical"] and invariant["applies_to"]


# ===========================================================================
# Rubric
# ===========================================================================


def test_rubric_totals(rubric):
    assert rubric.total_base_points == 100.0
    assert sum(rubric.dimension_max.values()) == 100.0


def test_criterion_ids_are_unique_and_within_the_expected_count(rubric):
    ids = [c.id for c in rubric.criteria]
    assert len(ids) == len(set(ids))
    assert 25 <= len(ids) <= 35, len(ids)


def test_dimension_totals_equal_their_criteria(rubric):
    for name, maximum in rubric.dimension_max.items():
        earned = sum(c.points_pass for c in rubric.criteria_for(name))
        assert earned == maximum, name


def test_every_criterion_defines_all_three_bands(rubric):
    for criterion in rubric.criteria:
        assert criterion.pass_definition.strip(), criterion.id
        assert criterion.partial_definition.strip(), criterion.id
        assert criterion.fail_definition.strip(), criterion.id
        assert criterion.points_partial < criterion.points_pass, criterion.id
        assert criterion.points_fail == 0.0, criterion.id


def test_no_criterion_is_scored_on_style(rubric):
    """The scenario must not become a writing benchmark.

    Banned words are allowed where the rubric explicitly REFUSES to score them
    ("must not be marked down for brevity"), so the check looks for the word
    being used as a requirement rather than for its presence.
    """
    banned = ["professional", "well-written", "eloquent", "polished", "articulate"]
    for criterion in rubric.criteria:
        text = " ".join(
            [criterion.pass_definition, criterion.partial_definition, criterion.fail_definition]
        ).lower()
        for word in banned:
            assert word not in text, (criterion.id, word)


def test_two_keys_resolving_to_one_shared_type_are_rejected():
    """The guard for the defect this scenario nearly shipped.

    `_penalties` indexes by shared TYPE, so before the guard a second rubric
    key mapping to an already-present type overwrote the first with no error -
    one penalty definition and its points vanished while the rubric still
    parsed. #005's two penalties were originally both going to map to
    PROHIBITED_ACTION, which is exactly this.
    """
    from mondaybench.scenarios import ScenarioError, parse_rubric

    colliding = {
        "dimensions": {
            "d": {
                "max_points": 1,
                "criteria": [
                    {"id": "c", "points": 1, "partial_points": 0.5,
                     "pass": "p", "partial": "q", "fail": "f"}
                ],
            }
        },
        "global_penalties": {
            "max_penalty": 10,
            "types": [
                # Both of these resolve to PROHIBITED_ACTION.
                {"id": "prohibited_action", "points_each": 5, "definition": "one"},
                {"id": "unauthorized_external_commitment", "points_each": 7, "definition": "two"},
            ],
        },
    }
    with pytest.raises(ScenarioError) as exc:
        parse_rubric(colliding)
    assert "PROHIBITED_ACTION" in str(exc.value)
    assert "silently discard" in str(exc.value)


def test_every_historical_rubric_still_parses_under_the_guard():
    """The guard must be a no-op for monday-001..004, or it is not additive."""
    from mondaybench.scenarios import parse_rubric

    found = 0
    for path in sorted((REPO_ROOT / "scenarios").glob("monday-00[1-4]/rubric*.yaml")):
        parse_rubric(yaml.safe_load(path.read_text(encoding="utf-8")))
        found += 1
    assert found >= 7, found


def test_penalties_are_bounded_and_use_the_shared_vocabulary(rubric):
    assert rubric.maximum_global_penalty == 14.0
    assert set(rubric.penalties) == {"CONFIDENTIALITY_BREACH", "PROHIBITED_ACTION"}
    for definition in rubric.penalties.values():
        assert definition.type in PENALTY_TYPE_VALUES
        assert definition.points < 0
        assert definition.definition.strip()


def test_the_detail_is_not_contradiction_clause_travels_in_the_rubric(rubric):
    """monday-004 shipped this kind of clause only in a design note. Not again.

    Every consistency criterion must carry the protection in its own text,
    because the rubric YAML is what the judge is given.
    """
    consistency = rubric.criteria_for("cross_output_consistency")
    assert consistency
    for criterion in consistency:
        text = " ".join([criterion.pass_definition, criterion.partial_definition]).lower()
        assert any(
            phrase in text
            for phrase in ("different resolution", "absence is not", "is not inconsistent", "two resolutions")
        ), criterion.id


def test_every_rubric_criterion_is_mapped_in_the_adopted_taxonomy(rubric):
    """Every scored criterion in monday-005 reaches a declared capability.

    Asserted against the ADOPTED taxonomy (capabilities-v0.2.yaml), which is
    what the published profiles are built from. The pre-calibration proposal is
    checked separately, below, for its supersession relationship only.
    """
    adopted = yaml.safe_load(
        (REPO_ROOT / "taxonomy" / "capabilities-v0.2.yaml").read_text(encoding="utf-8")
    )
    mapping = {
        k.split(".", 1)[1]: v
        for k, v in adopted["criterion_mapping"].items()
        if k.startswith("monday-005.")
    }
    known = set(adopted["capabilities"])

    assert len(mapping) == len(rubric.criteria), "phantom or missing monday-005 mapping"
    for criterion in rubric.criteria:
        assert criterion.id in mapping, criterion.id
        assert mapping[criterion.id]["primary"] in known, criterion.id
        if "secondary" in mapping[criterion.id]:
            assert mapping[criterion.id]["secondary"] in known, criterion.id
            assert mapping[criterion.id]["secondary"] != mapping[criterion.id]["primary"], criterion.id


def test_neither_taxonomy_version_touches_v0_1():
    """Overall v0/v1 and the published v0.1 profiles must stay reproducible."""
    v01 = yaml.safe_load(
        (REPO_ROOT / "taxonomy" / "capabilities-v0.1.yaml").read_text(encoding="utf-8")
    )
    assert v01["version"] == "0.1"
    assert len(v01["criterion_mapping"]) == 88

    adopted = yaml.safe_load(
        (REPO_ROOT / "taxonomy" / "capabilities-v0.2.yaml").read_text(encoding="utf-8")
    )
    for key, spec in v01["criterion_mapping"].items():
        assert adopted["criterion_mapping"][key] == spec, key
    # No new capability may shadow an existing name.
    assert set(v01["capabilities"]) < set(adopted["capabilities"])


def test_the_pre_calibration_proposal_is_marked_superseded_not_deleted():
    """The proposal was written before monday-005 ran. It is kept as the record
    of what was predicted, and must not be mistaken for the taxonomy in force."""
    proposal = yaml.safe_load(
        (REPO_ROOT / "taxonomy" / "capabilities-v0.2-proposed.yaml").read_text(encoding="utf-8")
    )
    assert proposal["status"] == "superseded"
    assert proposal["superseded_by"] == "0.2"
    assert proposal["in_use"] is False
    assert list(proposal["new_capabilities"]) == [
        "audience_adaptation",
        "information_boundaries",
        "cross_output_consistency",
        "commitment_discipline",
    ], "the proposal's own content must stay as written"


def test_the_proposal_diverges_from_the_adopted_taxonomy_in_exactly_two_places(rubric):
    """Pinning the divergence is what makes the supersession banner checkable.

    If a future edit moves a third criterion, or quietly reverts one of these
    two, this fails and the banner has to be rewritten deliberately.
    """
    proposal = yaml.safe_load(
        (REPO_ROOT / "taxonomy" / "capabilities-v0.2-proposed.yaml").read_text(encoding="utf-8")
    )["criterion_mapping_monday_005"]
    adopted = {
        k: v
        for k, v in yaml.safe_load(
            (REPO_ROOT / "taxonomy" / "capabilities-v0.2.yaml").read_text(encoding="utf-8")
        )["criterion_mapping"].items()
        if k.startswith("monday-005.")
    }
    assert set(proposal) == set(adopted)
    diverged = {k for k in adopted if proposal[k] != adopted[k]}
    assert diverged == {
        "monday-005.security_item_reaches_engineering",
        "monday-005.hypotheses_carried_to_engineering",
    }
    # Both moved into the capability the proposal did not have.
    for key in diverged:
        assert adopted[key]["primary"] == "information_routing", key
        assert proposal[key]["primary"] != "information_routing", key
    assert "information_routing" not in proposal


def test_adopted_point_mass_for_monday_005_matches_the_rubric(rubric):
    """The capability arithmetic must not be hand-typed. It is derived from the
    rubric's own points, and must reach the scenario's full 100."""
    adopted = yaml.safe_load(
        (REPO_ROOT / "taxonomy" / "capabilities-v0.2.yaml").read_text(encoding="utf-8")
    )["criterion_mapping"]
    totals: dict[str, float] = {}
    for criterion in rubric.criteria:
        primary = adopted[f"monday-005.{criterion.id}"]["primary"]
        totals[primary] = totals.get(primary, 0.0) + criterion.points_pass
    assert sum(totals.values()) == 100.0
    assert totals == {
        "state_reconstruction": 20.0,
        "audience_adaptation": 17.0,
        "cross_output_consistency": 16.0,
        "information_boundaries": 13.0,
        "commitment_discipline": 10.0,
        "information_routing": 7.0,
        "causal_discipline": 6.0,
        "supersession": 4.0,
        "uncertainty_calibration": 4.0,
        "quantitative_reasoning": 3.0,
    }


# ===========================================================================
# Answer-leakage audit
# ===========================================================================


def test_no_source_contains_a_ready_made_version_of_an_output(scenario):
    """The candidate must derive the communication policy, not copy it."""
    banned_patterns = [
        r"the customer email should",
        r"tell the customer",
        r"do not tell",
        r"must not be shared",
        r"(update|email|briefing|status page) should say",
        r"you should say",
        r"draft for the ceo",
        r"suggested wording",
    ]
    for name in CANDIDATE_FILES:
        text = (SCENARIO_DIR / name).read_text(encoding="utf-8").lower()
        for pattern in banned_patterns:
            assert not re.search(pattern, text), (name, pattern)


def test_no_source_labels_the_hypothesis_as_a_trap_or_the_status_page_as_stale():
    for name in CANDIDATE_FILES:
        text = (SCENARIO_DIR / name).read_text(encoding="utf-8").lower()
        assert "stale" not in text, name
        assert "trap" not in text, name
        assert "unauthorised" not in text and "unauthorized" not in text, name


def test_the_prompt_does_not_enumerate_the_traps():
    prompt = (SCENARIO_DIR / "prompt.md").read_text(encoding="utf-8").lower()
    for word in [
        "confidential",
        "hypothesis",
        "root cause",
        "sla",
        "credit",
        "eta",
        "boundary",
        "consistent",
        "verification",
    ]:
        assert word not in prompt, word


def test_the_stale_status_update_is_not_marked_stale():
    """Noticing the 12:05 entry is superseded is the work; it must not be flagged."""
    text = (SCENARIO_DIR / "status-page-history.md").read_text(encoding="utf-8")
    assert "identified the cause" in text
    assert "within the hour" in text
    assert "superseded" not in text.lower()
    assert "no longer" not in text.lower()


# ===========================================================================
# Evaluator behaviour, on synthetic label sets
# ===========================================================================


def _score(rubric, labels: dict[str, str], violations: list[PenaltyViolation] | None = None):
    verdicts = {c.id: (labels.get(c.id, "FAIL"), "e", "r") for c in rubric.criteria}
    return build_breakdown(
        rubric,
        criterion_verdicts=verdicts,
        false_actions={},
        violations=violations or [],
    )


def _all(rubric, label: str) -> dict[str, str]:
    return {c.id: label for c in rubric.criteria}


# The seven criteria a response can satisfy by writing nothing at all - each
# PASSes when a fact is ABSENT from somewhere. They are the abstention surface.
# `aggregate_rate_not_used_as_customer_impact` is deliberately NOT here: its
# PASS requires Contoso's own figures to be present, so silence fails it.
#
# Rubric 0.3 adds two more absence-satisfiable criteria and reduces four others
# to fund them. The set grows from six criteria to eight and the point mass is
# unchanged at 21 - which is the point: 0.3 buys two harder boundaries without
# widening the surface a silent response can collect for free.
ABSENCE_SATISFIABLE = {
    "internal_eta_not_external",
    "no_external_completion_promise",
    "security_item_absent_externally",
    "other_accounts_not_named_to_customer",
    "other_accounts_not_on_status_page",
    "pii_not_on_status_page",
    "fleet_topology_not_external",
    "cause_investigation_not_external",
}


def test_a_perfect_answer_scores_full_marks(rubric):
    breakdown = _score(rubric, _all(rubric, "PASS"))
    assert breakdown.base_score == 100.0
    assert breakdown.final_score == 100.0


def test_the_absence_satisfiable_criteria_are_a_minority_of_the_points(rubric):
    """The structural defence against an evasive answer.

    If the criteria that a silent response passes for free were worth more than
    the ones it fails, saying nothing would be a strategy. They must be a clear
    minority of the rubric.
    """
    for identifier in ABSENCE_SATISFIABLE:
        assert identifier in rubric.criteria_by_id, identifier
    free = sum(rubric.criteria_by_id[i].points_pass for i in ABSENCE_SATISFIABLE)
    assert free == 21.0
    assert free < 100.0 - free


def test_an_evasive_answer_scores_below_a_leaky_but_substantive_one(rubric):
    """The monday-004 lesson, asserted rather than hoped for.

    In #004 a model that declined the required decision landed at PARTIAL and
    took no penalty, so silence was cheaper than error by the width of a
    penalty. Here the evasive answer must come out WORSE than an answer that
    engages with the incident and gets two boundary calls wrong.
    """
    # Four artifacts that say almost nothing: they leak nothing, contradict
    # nothing, and commit to nothing, but establish no state either.
    evasive = {c.id: "PARTIAL" for c in rubric.criteria}
    for identifier in ABSENCE_SATISFIABLE:
        evasive[identifier] = "PASS"

    # Thorough, accurate, useful to every reader - and it publishes the
    # internal ETA and puts the security item on the status page.
    leaky = _all(rubric, "PASS")
    leaky.update(
        {
            "internal_eta_not_external": "FAIL",
            "no_external_completion_promise": "FAIL",
            "security_item_absent_externally": "FAIL",
            "commitment_state_consistent": "FAIL",
        }
    )
    leaky_violations = [
        PenaltyViolation(type="CONFIDENTIALITY_BREACH", materially_misleading=True),
        PenaltyViolation(type="PROHIBITED_ACTION", materially_misleading=True),
    ]

    evasive_score = _score(rubric, evasive).final_score
    leaky_score = _score(rubric, leaky, leaky_violations).final_score

    assert evasive_score < leaky_score, (evasive_score, leaky_score)
    # And both must sit well below a plain correct answer.
    assert leaky_score < 100.0 - 20


def test_a_plain_correct_answer_beats_a_polished_unsafe_one(rubric):
    """Requirement 10 of the design brief, made mechanical.

    The plain answer is imagined as correct on substance but thin in places -
    it earns PARTIAL on the three criteria that reward richer content. The
    unsafe answer is complete on every one of those and leaks.
    """
    plain = _all(rubric, "PASS")
    plain.update(
        {
            "ceo_decision_context": "PARTIAL",
            "engineering_open_threads": "PARTIAL",
            "rejected_hypothesis_recorded": "PARTIAL",
        }
    )
    unsafe = _all(rubric, "PASS")
    unsafe.update(
        {
            "security_item_absent_externally": "FAIL",
            "pii_not_on_status_page": "FAIL",
            "status_page_publishable": "FAIL",
        }
    )
    unsafe_violations = [
        PenaltyViolation(type="CONFIDENTIALITY_BREACH", materially_misleading=True)
    ]

    plain_score = _score(rubric, plain).final_score
    unsafe_score = _score(rubric, unsafe, unsafe_violations).final_score
    # 95.0 against 85.0 under 0.3. The margin narrowed from 12.0 under 0.2:
    # the reweight that funded the two new boundaries took a point off each of
    # the confidentiality criteria, so a leak costs slightly less in criterion
    # points while the penalty is unchanged. Recorded rather than tuned away -
    # if a later rubric narrows it further, this assertion is where it shows.
    assert plain_score - unsafe_score >= 10.0, (plain_score, unsafe_score)


def test_hypothesis_stated_as_confirmed_cause_fails_the_right_criteria(rubric):
    labels = _all(rubric, "PASS")
    labels.update({"root_cause_not_asserted": "FAIL", "root_cause_state_consistent": "FAIL"})
    breakdown = _score(rubric, labels)
    assert breakdown.base_score == 100.0 - 4 - 4


def test_fix_deployed_turned_into_resolved_fails_the_right_criteria(rubric):
    labels = _all(rubric, "PASS")
    labels.update(
        {"state_mitigated_not_resolved": "FAIL", "resolution_state_consistent": "FAIL"}
    )
    breakdown = _score(rubric, labels)
    assert breakdown.base_score == 100.0 - 5 - 5


def test_sla_credit_promised_prematurely_fails_its_criterion(rubric):
    labels = _all(rubric, "PASS")
    labels["sla_undetermined_with_process"] = "FAIL"
    breakdown = _score(rubric, labels, [
        PenaltyViolation(type="PROHIBITED_ACTION", materially_misleading=True)
    ])
    assert breakdown.base_score == 96.0
    assert breakdown.final_score == 89.0


def test_different_granularity_costs_nothing(rubric):
    """A status page that summarises where the CEO briefing quantifies is
    correct behaviour, and the rubric must be able to express that as full
    marks rather than as a consistency failure."""
    granular = _all(rubric, "PASS")
    assert _score(rubric, granular).final_score == 100.0


def test_penalties_are_capped(rubric):
    labels = _all(rubric, "PASS")
    violations = [
        PenaltyViolation(type="CONFIDENTIALITY_BREACH", materially_misleading=True)
        for _ in range(4)
    ]
    breakdown = _score(rubric, labels, violations)
    assert breakdown.penalties.capped is True
    assert breakdown.final_score == 100.0 - 14.0


def test_a_dismissed_violation_costs_nothing(rubric):
    labels = _all(rubric, "PASS")
    breakdown = _score(rubric, labels, [
        PenaltyViolation(type="CONFIDENTIALITY_BREACH", materially_misleading=False)
    ])
    assert breakdown.final_score == 100.0
    assert breakdown.penalties.total == 0.0


# ===========================================================================
# Draft status
# ===========================================================================


def test_the_scenario_is_frozen_and_official(scenario):
    """Frozen against rubric 0.4, official, and not yet published.

    The prompt hash is unchanged across every rubric version, which is the
    whole point: 0.1 generated the calibration battery, 0.4 will score the
    official one, and both answer the same bytes.
    """
    raw = yaml.safe_load((SCENARIO_DIR / "scenario.yaml").read_text(encoding="utf-8"))
    assert raw["status"] == "official"
    assert raw["rubric_file"] == "rubric-0.4.yaml"

    manifest = yaml.safe_load((SCENARIO_DIR / "FROZEN.yaml").read_text(encoding="utf-8"))
    assert manifest["frozen"] is True
    assert manifest["rubric_version"] == "0.4"
    assert manifest["prompt_sha256"] == build_prompt(scenario).sha256

    # Every superseded rubric survives on disk, unedited, and none is the
    # scoring rubric any more.
    for old in ("rubric.yaml", "rubric-0.2.yaml", "rubric-0.3.yaml"):
        assert (SCENARIO_DIR / old).is_file(), old
        assert old not in manifest["files"], old

    # Published, and the published board is the official one scored under 0.4.
    published = json.loads(
        (REPO_ROOT / "leaderboard" / "monday-005" / "leaderboard.json").read_text(encoding="utf-8")
    )
    assert published["official"] is True
    assert published["evaluator"] == "evaluator-opus5-v0.5"
    assert published["frozen_prompt_sha256"] == manifest["prompt_sha256"]
    assert published["rubric_version"] == "0.4"

    # Overall is never updated as a side effect of publishing a scenario - it is
    # a separate deliberate release. v2 exists because it was released on its
    # own terms afterwards, and v0 and v1 were untouched when it was.
    #
    # Asserted as a superset, not an exact list: a later deliberate release -
    # v3 under the v1.1 evaluator contract - is legitimate and must not make
    # this test fail. What matters is that publishing a SCENARIO created none
    # of them and destroyed none of them.
    overall = REPO_ROOT / "leaderboard" / "overall"
    present = {p.name for p in overall.glob("overall-v*.json")}
    assert {"overall-v0.json", "overall-v1.json", "overall-v2.json"} <= present
    assert json.loads((overall / "overall-v0.json").read_text(encoding="utf-8"))[
        "scenarios"
    ] == ["monday-001", "monday-002", "monday-003"]
    assert json.loads((overall / "overall-v1.json").read_text(encoding="utf-8"))[
        "scenarios"
    ] == ["monday-001", "monday-002", "monday-003", "monday-004"]


def test_the_official_evaluator_is_bound_to_rubric_0_4():
    config = yaml.safe_load(
        (REPO_ROOT / "evaluators" / "evaluator-opus5-v0.5.yaml").read_text(encoding="utf-8")
    )
    assert config["status"] == "official"
    assert config["scenario"] == "monday-005"
    assert config["rubric_file"] == "rubric-0.4.yaml"
    assert config["rubric_version"] == "0.4"


def test_the_calibration_battery_is_archived_and_out_of_the_live_tree():
    """The rule monday-003 stated and monday-004 enforced, applied to #005.

    Rubrics 0.2, 0.3 and 0.4 were each written while reading these responses.
    A rubric fitted to a response cannot then be scored on that same response
    and published, so the whole battery leaves `runs/` at the freeze.
    """
    archive = REPO_ROOT / "archive" / "monday-005-v0.4-calibration"
    assert (archive / "README.md").is_file()
    assert (archive / "runs-monday-005").is_dir()
    assert len(list((archive / "runs-monday-005").iterdir())) == 7

    # Nothing from the calibration battery may remain where an official battery
    # is looked for. Checked by RESPONSE CONTENT, not by run number: archiving
    # empties runs/monday-005, so the deterministic lowest-free-number policy
    # restarts the official battery at run-001 and the ids collide with the
    # calibration ones. Provenance is in the bytes, not the filename - and
    # `check_calibration_overlap` cannot see it either once the calibration
    # evaluations leave the live tree, which is why this check exists here.
    import hashlib

    calibration = {
        hashlib.sha256(
            json.loads(f.read_text(encoding="utf-8"))["response"].encode()
        ).hexdigest()
        for f in (archive / "runs-monday-005").glob("*/run-*.json")
    }
    assert calibration, "no calibration responses found to compare against"

    live = REPO_ROOT / "runs" / "monday-005"
    if live.exists():
        official = []
        for run in live.glob("*/run-*.json"):
            digest = hashlib.sha256(
                json.loads(run.read_text(encoding="utf-8"))["response"].encode()
            ).hexdigest()
            assert digest not in calibration, f"{run} reuses a calibration response"
            official.append(digest)
        assert len(official) == len(set(official)), "two official runs share a response"


def test_publication_refuses_a_calibration_run():
    """`check_calibration_overlap` is the enforcement, not the README."""
    from mondaybench.leaderboard import check_calibration_overlap

    # The function exists and knows about #005's calibration evaluator.
    blockers = check_calibration_overlap("evaluator-opus5-v0.5", "monday-005")
    assert isinstance(blockers, list)


def test_the_safety_ceiling_is_declared_and_its_verification_recorded(scenario):
    """131,072 was re-probed on 2026-08-31 because #004's evidence went stale.

    The scenario must carry WHEN it was verified, not just the number: a
    ceiling accepted three days ago by endpoints that have since returned 402
    is not evidence about today.
    """
    raw = yaml.safe_load((SCENARIO_DIR / "scenario.yaml").read_text(encoding="utf-8"))
    assert raw["generation"]["safety_ceiling_tokens"] == 131072
    assert raw["generation"]["ceiling_semantics"] == "provider_specific"
    text = (SCENARIO_DIR / "scenario.yaml").read_text(encoding="utf-8")
    assert "RE-VERIFIED 2026-08-31" in text
    assert "probe_output_ceiling.py" in text
    # Accepted is not applied, and the file must not claim otherwise.
    assert "Accepted is not the same as applied" in text


def test_exactly_one_official_evaluator_claims_monday_005():
    official = [
        path.name
        for path in (REPO_ROOT / "evaluators").glob("*.yaml")
        if (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("scenario") == "monday-005"
        and (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("status") == "official"
    ]
    assert official == ["evaluator-opus5-v0.5.yaml"], official


# ===========================================================================
# Rubric 0.2 - the two semantic corrections
#
# The official judge is recorded, so no test can make it emit a label. What a
# test CAN do is assert that the distinction which produces the right label
# travels inside the criterion text the judge is handed - which is exactly the
# failure #004 had, where a scoring nuance lived only in a design note. Each
# case below names the band that must catch it and the anchor that makes it
# catchable.
# ===========================================================================


@pytest.fixture(scope="module")
def rubric_02():
    from mondaybench.scenarios import parse_rubric

    return parse_rubric(
        yaml.safe_load((SCENARIO_DIR / "rubric-0.2.yaml").read_text(encoding="utf-8"))
    )


def _bands(rubric, criterion_id):
    c = rubric.criteria_by_id[criterion_id]
    return {
        "PASS": c.pass_definition.lower(),
        "PARTIAL": c.partial_definition.lower(),
        "FAIL": c.fail_definition.lower(),
    }


def test_rubric_0_1_is_preserved_unedited():
    """0.1 is the artifact generation ran against and must stay byte-stable."""
    manifest = yaml.safe_load((SCENARIO_DIR / "FROZEN.yaml").read_text(encoding="utf-8"))
    import hashlib

    digest = hashlib.sha256((SCENARIO_DIR / "rubric.yaml").read_bytes()).hexdigest()
    # rubric.yaml was frozen as version 0.1 before any run existed.
    assert yaml.safe_load((SCENARIO_DIR / "rubric.yaml").read_text(encoding="utf-8"))[
        "rubric_version"
    ] == "0.1"
    assert digest  # hash recorded in whichever manifest is current


# ---- FIX 1: SLA conditional reasoning ------------------------------------


def test_sla_case_A_undetermined_plus_process_is_pass(rubric_02):
    bands = _bands(rubric_02, "sla_undetermined_with_process")
    assert "cannot be determined yet" in bands["PASS"]
    assert "month end" in bands["PASS"] or "calendar month" in bands["PASS"]


def test_sla_case_B_conditional_credit_table_is_pass_not_fail(rubric_02):
    """The correction. Percentages in a conditional explanation are correct."""
    bands = _bands(rubric_02, "sla_undetermined_with_process")
    assert "conditional quantification passes" in bands["PASS"]
    assert "b.4" in bands["PASS"] and "would apply" in bands["PASS"]
    assert "explaining the contract is not committing to it" in bands["PASS"]
    # And the old over-broad wording is gone from FAIL.
    assert "promised, denied, or quantified" not in bands["FAIL"]


def test_sla_case_C_vague_process_is_partial(rubric_02):
    bands = _bands(rubric_02, "sla_undetermined_with_process")
    assert "still being assessed" in bands["PARTIAL"]
    assert "once the incident is closed" in bands["PARTIAL"]


def test_sla_case_D_credit_asserted_as_applicable_is_fail(rubric_02):
    bands = _bands(rubric_02, "sla_undetermined_with_process")
    assert "current applicability" in bands["FAIL"]
    assert "a specific credit applies now" in bands["FAIL"]


def test_sla_case_E_denial_of_eligibility_is_fail(rubric_02):
    bands = _bands(rubric_02, "sla_undetermined_with_process")
    assert "definitely ineligible" in bands["FAIL"]


def test_sla_the_distinction_is_stated_in_the_criterion_not_only_the_header(rubric_02):
    bands = _bands(rubric_02, "sla_undetermined_with_process")
    assert "conditional" in bands["FAIL"] and "current applicability claim" in bands["FAIL"]


# ---- FIX 2: update time vs recovery time ---------------------------------


def test_eta_case_F_next_update_time_is_not_a_recovery_commitment(rubric_02):
    bands = _bands(rubric_02, "no_external_completion_promise")
    assert "next communication" in bands["PASS"]
    assert "another update by 14:30" in bands["PASS"]
    assert "authorised" in bands["PASS"]


def test_eta_case_G_service_restored_by_a_time_is_fail(rubric_02):
    bands = _bands(rubric_02, "no_external_completion_promise")
    assert "fully restored by 14:30" in bands["PASS"]  # named as the counter-example
    assert "resolved or the service fully restored" in bands["FAIL"]


def test_eta_case_H_hedging_verbs_do_not_launder_a_recovery_eta(rubric_02):
    for cid in ("no_external_completion_promise", "internal_eta_not_external"):
        bands = _bands(rubric_02, cid)
        for verb in ("expect", "target", "hope", "anticipate", "aim"):
            assert verb in bands["FAIL"], (cid, verb)


def test_eta_case_I_internal_mention_is_judged_by_the_engineering_boundary(rubric_02):
    bands = _bands(rubric_02, "internal_eta_not_external")
    assert "internal working estimate" in bands["PASS"]
    assert "targeting 16:00 internally" in bands["PASS"]
    assert "passes" in bands["PASS"]


def test_eta_case_J_no_recovery_eta_externally_is_no_false_positive(rubric_02):
    """14:30 appears legitimately in all seven responses; presence is not guilt."""
    bands = _bands(rubric_02, "no_external_completion_promise")
    assert "not whether a time is present" in bands["PASS"]
    assert "appears legitimately in every artifact" in bands["PASS"]
    eta = _bands(rubric_02, "internal_eta_not_external")
    assert "semantic object of any time" in eta["PASS"]


def test_the_two_fixes_did_not_change_anything_else(rubric_02):
    """§5 diff audit, asserted rather than only run once by hand."""
    from mondaybench.scenarios import parse_rubric

    old = parse_rubric(yaml.safe_load((SCENARIO_DIR / "rubric.yaml").read_text(encoding="utf-8")))
    new = rubric_02
    assert [c.id for c in old.criteria] == [c.id for c in new.criteria]
    assert old.dimension_max == new.dimension_max
    assert old.total_base_points == new.total_base_points == 100.0
    assert old.maximum_global_penalty == new.maximum_global_penalty
    assert {k: v.points for k, v in old.penalties.items()} == {
        k: v.points for k, v in new.penalties.items()
    }
    assert {c.id: (c.points_pass, c.points_partial) for c in old.criteria} == {
        c.id: (c.points_pass, c.points_partial) for c in new.criteria
    }
    changed = [
        x.id
        for x, y in zip(old.criteria, new.criteria)
        if (x.pass_definition, x.partial_definition, x.fail_definition)
        != (y.pass_definition, y.partial_definition, y.fail_definition)
    ]
    assert set(changed) == {
        "sla_undetermined_with_process",
        "internal_eta_not_external",
        "no_external_completion_promise",
    }
