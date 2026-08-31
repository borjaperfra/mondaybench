"""Guards for monday-004 "Numbers Don't Lie", scenario 0.1 - calibration draft.

This scenario's difficulty is arithmetic, so its failure mode is different from
the three before it. A prose scenario breaks loudly: a missing file, a criterion
with no evidence. A tabular one breaks silently - a customer counted twice, a
plan total that no longer matches the customers on it, a duplicate that is not
actually a duplicate - and every downstream number stays plausible.

So almost everything below recomputes a figure from the published CSVs and
compares it with `ground-truth.yaml`. Nothing in the answer key is trusted
because it is written down. `tests/monday_004_derivations.py` does the
computing and is deliberately not the script that wrote the files.

The other half of the file guards the design rather than the arithmetic: that
each trap still exists and still bites, that no candidate-visible source states
a conclusion, that the metric the pack cannot answer is still unanswerable, and
that a scenario in `status: calibration` cannot reach a published leaderboard.

monday-001, monday-002 and monday-003 are frozen and this work is additive, so
their manifests are verified here too.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

import pytest
import yaml

from mondaybench.config import load_evaluator
from mondaybench.freeze import check_drift, load_manifest
from mondaybench.prompt_builder import build_prompt
from mondaybench.scenarios import load_scenario

sys.path.insert(0, str(Path(__file__).resolve().parent))
import monday_004_derivations as D  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
SCENARIO_DIR = REPO_ROOT / "scenarios" / "monday-004"
EVALUATOR = "evaluator-opus5-v0.4-calibration"

SEP = "2026-09"
OCT = "2026-10"

SOURCE_ORDER = [
    "context.md",
    "customers.csv",
    "revenue.csv",
    "usage.csv",
    "plans.csv",
    "acquisition.csv",
    "funnel.csv",
    "support.csv",
]

# The rendered candidate prompt. Pinned so a stray edit to any of the eight
# sources shows up as a failing test rather than as runs that quietly are not
# comparable with each other.
PROMPT_SHA256 = "3a0cbb569ca4f711b8907177af9204cec267d26f35f732829df56b03ed23ef99"


@pytest.fixture(scope="module")
def scenario():
    return load_scenario("monday-004")


@pytest.fixture(scope="module")
def ground_truth() -> dict:
    return yaml.safe_load((SCENARIO_DIR / "ground-truth.yaml").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def canonical() -> dict:
    return D.canonical()


# ---------------------------------------------------------------------------
# Scenario shape
# ---------------------------------------------------------------------------


def test_scenario_is_frozen_and_official(scenario):
    """Promoted after two calibration batteries. The content never moved."""
    assert scenario.status == "official"
    assert not scenario.is_calibration
    # 0.1, not 0.3: the candidate-visible content is byte-identical to what the
    # first battery answered. Only the rubric iterated, and it carries its own
    # version.
    assert scenario.scenario_version == "0.1"
    assert scenario.rubric.version == "0.3"
    assert (SCENARIO_DIR / "FROZEN.yaml").is_file()


def test_source_order_is_declared_and_complete(scenario):
    assert scenario.sources == SOURCE_ORDER
    for name in SOURCE_ORDER:
        assert (SCENARIO_DIR / name).exists(), name


def test_no_slack_email_or_calendar_source(scenario):
    """#004 exists to test something the other three do not.

    If it acquires a Slack log or an inbox it becomes another reading test with
    a spreadsheet attached, which is not what it is for.
    """
    for name in scenario.sources:
        assert not re.search(r"slack|email|inbox|meeting|calendar", name, re.I), name
    tabular = [s for s in scenario.sources if s.endswith(".csv")]
    assert len(tabular) == 7


def test_prompt_is_deterministic_and_pinned(scenario):
    first = build_prompt(scenario)
    second = build_prompt(scenario)
    assert first.sha256 == second.sha256
    assert first.sha256 == PROMPT_SHA256
    assert first.system_prompt == "You are a helpful assistant."


def test_prompt_contains_every_source_in_order(scenario):
    text = build_prompt(scenario).text
    positions = []
    for name in scenario.sources:
        marker = (SCENARIO_DIR / name).read_text(encoding="utf-8").strip().splitlines()[0]
        assert marker in text, name
        positions.append(text.index(marker))
    assert positions == sorted(positions)


def test_design_notes_are_not_a_candidate_source(scenario):
    assert (SCENARIO_DIR / "design-notes.md").exists()
    assert "design-notes.md" not in scenario.sources
    assert "design-notes" not in build_prompt(scenario).text


def test_ground_truth_is_not_a_candidate_source(scenario):
    assert "ground-truth.yaml" not in scenario.sources
    text = build_prompt(scenario).text
    assert "recommended_product_focus" not in text
    assert "duplicate_transaction_ids" not in text


# ---------------------------------------------------------------------------
# Rubric
# ---------------------------------------------------------------------------


def test_rubric_totals_one_hundred(scenario):
    rubric = scenario.rubric
    assert sum(rubric.dimension_max.values()) == 100
    assert rubric.total_base_points == 100
    for dimension, maximum in rubric.dimension_max.items():
        earned = sum(c.points_pass for c in rubric.criteria_for(dimension))
        assert earned == maximum, dimension


def test_rubric_has_the_declared_criteria(scenario):
    """The frozen rubric, 0.3. The two earlier ones are guarded separately."""
    ids = {c.id for c in scenario.rubric.criteria}
    assert len(scenario.rubric.criteria) == 27
    assert len(ids) == 27
    expected = {
        "duplicate_detected", "annual_prepayment_normalized", "headline_vs_recurring_growth",
        "revenue_conclusion", "segment_retention_quantified", "sample_size_arr_context",
        "acme_false_positive_avoided", "no_churn_overreach",
        "raw_attribution_not_equivalent_new_business", "existing_customer_expansion_removed",
        "conversion_rate_vs_absolute_volume", "no_unsupported_channel_scale_decision",
        "cac_payback_unavailable", "contribution_calculated",
        "margin_calculated_or_correctly_compared", "absolute_vs_scalable_economics",
        "plan_trajectory_evidence", "product_focus_supported", "customer_id_alias_resolved",
        "support_normalized", "figures_carried_correctly", "cross_table_customer_signal",
        "causal_boundary", "segment_recommendation", "acquisition_recommendation",
        "product_recommendation", "uncertainty_discipline",
    }
    assert ids == expected


def test_no_single_criterion_can_decide_a_run(scenario):
    """One arithmetic slip must cost points without deciding the outcome."""
    heaviest = max(c.points_pass for c in scenario.rubric.criteria)
    assert heaviest <= 6


def test_every_criterion_defines_pass_and_partial(scenario):
    for criterion in scenario.rubric.criteria:
        assert criterion.pass_definition, criterion.id
        assert criterion.partial_definition, criterion.id
        assert 0 < criterion.points_partial < criterion.points_pass, criterion.id


def test_penalty_scale_and_cap(scenario):
    rubric = scenario.rubric
    assert rubric.maximum_global_penalty == 25
    assert rubric.penalties["MATERIAL_HALLUCINATION"].points == -5
    assert rubric.penalties["PROHIBITED_ACTION"].points == -7
    assert rubric.penalties["MAJOR_DATA_ERROR"].points == -7
    assert rubric.penalties["UNSUPPORTED_CAUSALITY"].points == -5


def test_evaluator_is_bound_to_this_scenario_and_is_not_official():
    cfg = load_evaluator(EVALUATOR)
    assert cfg.scenario == "monday-004"
    assert cfg.scenario_version == "0.1"
    assert cfg.rubric_version == "0.1"
    # The evaluator id carries the status: an official evaluator never has a
    # `-calibration` suffix, and `mondaybench validate` refuses to pair this one
    # with a scenario that has moved off 0.1.
    assert cfg.id.endswith("-calibration")
    for name in (cfg.prompt_file, cfg.penalty_prompt_file):
        assert (REPO_ROOT / "evaluators" / "monday-004" / name).exists(), name


# ---------------------------------------------------------------------------
# The data parses and is internally consistent
# ---------------------------------------------------------------------------


def test_every_csv_parses_with_a_stable_header():
    expected = {
        "customers.csv": ["customer_id", "usage_account_id", "segment", "plan", "start_date", "status", "churn_date", "arr_eur", "renewal_date"],
        "revenue.csv": ["transaction_id", "customer_id", "date", "invoice_type", "billing_period_months", "amount_eur", "source"],
        "usage.csv": ["month", "usage_account_id", "requests", "tokens_m", "active_users", "usage_change_pct"],
        "plans.csv": ["month", "plan", "customers", "revenue_eur", "infra_cost_eur", "support_cost_eur", "included_requests_per_customer", "avg_requests_per_customer"],
        "acquisition.csv": ["month", "lead_id", "customer_id", "channel", "campaign_start", "first_customer_date", "conversion_date", "new_logo", "expansion", "attributed_revenue_eur"],
        "funnel.csv": ["month", "channel", "leads", "conversions"],
        "support.csv": ["month", "ticket_id", "customer_id", "severity", "category", "status"],
    }
    for name, header in expected.items():
        with (SCENARIO_DIR / name).open(encoding="utf-8", newline="") as handle:
            rows = list(csv.reader(handle))
        assert rows[0] == header, name
        widths = {len(r) for r in rows}
        assert widths == {len(header)}, f"{name} has ragged rows: {widths}"


def test_every_referenced_customer_exists():
    known = {r["customer_id"] for r in D.customers()}
    accounts = {r["usage_account_id"] for r in D.customers()}
    for row in D.revenue():
        assert row["customer_id"] in known, row["transaction_id"]
    for row in D.acquisition():
        assert row["customer_id"] in known, row["lead_id"]
    for row in D.support():
        assert row["customer_id"] in known, row["ticket_id"]
    for row in D.usage():
        assert row["usage_account_id"] in accounts, row["usage_account_id"]


def test_plan_revenue_matches_the_customers_on_the_plan():
    """plans.csv is an aggregate; it has to agree with the rows it aggregates.

    A plan table that drifts from the customer table would make the contribution
    criteria unscorable and nothing else would notice.
    """
    subs: dict[tuple[str, str], float] = {}
    seen: set[str] = set()
    for row in D.revenue():
        if row["transaction_id"] in seen:
            continue
        seen.add(row["transaction_id"])
        months = int(row["billing_period_months"])
        if months <= 0:
            continue
        key = (row["date"][:7], row["customer_id"])
        subs[key] = subs.get(key, 0.0) + float(row["amount_eur"]) / months

    plan_of = D.plan_of()
    for month in (SEP, OCT):
        from_customers: dict[str, float] = {}
        counts: dict[str, int] = {}
        for (m, customer_id), value in subs.items():
            if m != month:
                continue
            plan = plan_of[customer_id]
            from_customers[plan] = from_customers.get(plan, 0.0) + value
            counts[plan] = counts.get(plan, 0) + 1
        for row in D.plans():
            if row["month"] != month:
                continue
            assert float(row["revenue_eur"]) == pytest.approx(from_customers[row["plan"]]), (month, row["plan"])
            assert int(row["customers"]) == counts[row["plan"]], (month, row["plan"])


def test_arr_matches_twelve_times_the_current_monthly_value():
    latest: dict[str, float] = {}
    seen: set[str] = set()
    for row in D.revenue():
        if row["date"][:7] != OCT or row["transaction_id"] in seen:
            continue
        seen.add(row["transaction_id"])
        months = int(row["billing_period_months"])
        if months <= 0:
            continue
        latest[row["customer_id"]] = float(row["amount_eur"]) / months
    for row in D.customers():
        assert float(row["arr_eur"]) == pytest.approx(latest[row["customer_id"]] * 12), row["customer_id"]


def test_usage_change_column_agrees_with_the_two_months():
    by_account = {(r["month"], r["usage_account_id"]): r for r in D.usage()}
    for (month, account), row in by_account.items():
        if month != OCT:
            assert row["usage_change_pct"] == ""
            continue
        previous = by_account.get((SEP, account))
        if previous is None:
            assert row["usage_change_pct"] == ""
            continue
        expected = (float(row["requests"]) - float(previous["requests"])) / float(previous["requests"]) * 100
        assert float(row["usage_change_pct"]) == pytest.approx(expected, abs=0.05), account


# ---------------------------------------------------------------------------
# D8 - the duplicate is exactly one, and exactly as designed
# ---------------------------------------------------------------------------


def test_exactly_one_duplicated_transaction(canonical, ground_truth):
    ids = canonical["revenue"]["duplicate_transaction_ids"]
    assert ids == ground_truth["revenue"]["duplicate_transaction_ids"]
    assert len(ids) == 1
    rows = D.duplicate_rows()
    assert len(rows) == 2
    assert {r["source"] for r in rows} == {"stripe", "billing_sync"}
    assert {r["date"] for r in rows} == {"2026-10-01", "2026-10-02"}
    assert len({r["amount_eur"] for r in rows}) == 1
    assert float(rows[0]["amount_eur"]) == ground_truth["revenue"]["duplicate_amount_eur"]


def test_the_duplicate_is_detectable_only_by_transaction_id():
    """If the two rows were identical in every field, spotting it would be luck.

    They differ in `source` and in `date`; the transaction id is what makes them
    the same invoice. A candidate has to use it.
    """
    a, b = D.duplicate_rows()
    differing = {k for k in a if a[k] != b[k]}
    assert differing == {"source", "date"}


def test_no_other_column_is_accidentally_unique_per_row():
    rows = D.revenue()
    assert len({r["transaction_id"] for r in rows}) == len(rows) - 1


# ---------------------------------------------------------------------------
# D1 - revenue totals, normalisation and growth
# ---------------------------------------------------------------------------


def test_raw_totals_match_the_answer_key(canonical, ground_truth):
    key = ground_truth["revenue"]
    assert canonical["revenue"]["raw_september_eur"] == key["raw_totals"]["september_eur"]
    assert canonical["revenue"]["raw_october_eur"] == key["raw_totals"]["october_eur"]


def test_deduplicated_total_matches_the_answer_key(canonical, ground_truth):
    assert (
        canonical["revenue"]["october_deduplicated_eur"]
        == ground_truth["revenue"]["adjusted_totals"]["october_deduplicated_eur"]
    )
    assert (
        canonical["revenue"]["raw_october_eur"] - canonical["revenue"]["october_deduplicated_eur"]
        == ground_truth["revenue"]["duplicate_amount_eur"]
    )


def test_recurring_normalisation_matches_the_answer_key(canonical, ground_truth):
    key = ground_truth["revenue"]["normalized_recurring"]
    assert canonical["revenue"]["recurring_september_eur"] == key["september_eur"]
    assert canonical["revenue"]["recurring_october_eur"] == key["october_eur"]


def test_exactly_one_annual_invoice_and_its_monthly_equivalent(ground_truth):
    annual = D.annual_invoices()
    assert len(annual) == 1
    row = annual[0]
    key = ground_truth["revenue"]["normalized_recurring"]["annual_invoice"]
    assert row["customer_id"] == key["transaction_customer"]
    assert float(row["amount_eur"]) == key["amount_eur"]
    assert int(row["billing_period_months"]) == key["billing_period_months"]
    assert float(row["amount_eur"]) / int(row["billing_period_months"]) == key["monthly_equivalent_eur"]
    assert float(row["amount_eur"]) - key["monthly_equivalent_eur"] == key["excess_in_october_eur"]


def test_growth_percentages_match_the_answer_key(canonical, ground_truth):
    key = ground_truth["revenue"]
    assert canonical["revenue"]["headline_growth_pct"] == key["headline_growth_pct"]
    assert canonical["revenue"]["deduplicated_growth_pct"] == key["deduplicated_growth_pct"]
    assert canonical["revenue"]["recurring_growth_pct"] == key["recurring_growth_pct"]


def test_both_defensible_normalisations_refute_the_headline(canonical, ground_truth):
    """The one-off services are large in September and small in October, so the
    two reasonable treatments do not agree. Both have to be in the answer key,
    and both have to contradict the +12%: a rubric that accepted only one would
    fail a candidate for a correct calculation."""
    revenue = canonical["revenue"]
    key = ground_truth["revenue"]
    assert revenue["normalized_all_invoices_september_eur"] == key["normalized_all_invoices"]["september_eur"]
    assert revenue["normalized_all_invoices_october_eur"] == key["normalized_all_invoices"]["october_eur"]
    assert revenue["normalized_all_invoices_growth_pct"] == key["normalized_all_invoices_growth_pct"]
    assert revenue["recurring_growth_pct"] > 0 > revenue["normalized_all_invoices_growth_pct"]
    for figure in (revenue["recurring_growth_pct"], revenue["normalized_all_invoices_growth_pct"]):
        assert abs(revenue["headline_growth_pct"] - figure) > 9


def test_the_headline_reverses_after_normalisation(canonical):
    """The trap only exists if the naive answer and the real one differ enough
    to change what leadership would do."""
    revenue = canonical["revenue"]
    assert revenue["headline_growth_pct"] > 11.5
    assert revenue["recurring_growth_pct"] < 3.0
    assert revenue["headline_growth_pct"] - revenue["recurring_growth_pct"] > 9


def test_one_off_invoices_are_present_in_both_months(canonical):
    assert canonical["revenue"]["one_off_september_eur"] > 0
    assert canonical["revenue"]["one_off_october_eur"] > 0


# ---------------------------------------------------------------------------
# D2 - churn
# ---------------------------------------------------------------------------


def test_segment_churn_matches_the_answer_key(canonical, ground_truth):
    derived = canonical["customer_health"]["segment_churn"]
    key = ground_truth["customer_health"]["segment_churn"]
    assert set(derived) == set(key)
    for segment, expected in key.items():
        got = derived[segment]
        assert got["customers"] == expected["customers"], segment
        assert got["churned"] == expected["churned"], segment
        assert got["logo_churn_pct"] == expected["logo_churn_pct"], segment
        assert got["arr_lost_eur"] == expected["arr_lost_eur"], segment
        assert got["arr_total_eur"] == expected["arr_total_eur"], segment


def test_plan_churn_matches_the_answer_key(canonical, ground_truth):
    derived = canonical["customer_health"]["plan_churn"]
    for plan, expected in ground_truth["customer_health"]["plan_churn"].items():
        assert derived[plan]["customers"] == expected["customers"], plan
        assert derived[plan]["churned"] == expected["churned"], plan
        assert derived[plan]["logo_churn_pct"] == expected["logo_churn_pct"], plan


def test_plan_and_segment_do_not_align(canonical):
    """The two churn framings must be different numbers.

    If plan were a synonym for segment, half the cross-table criteria would be
    single-table criteria and `sample_size_arr_context` would have nothing to
    say about missing segment economics.
    """
    by_segment = {s: v["logo_churn_pct"] for s, v in canonical["customer_health"]["segment_churn"].items()}
    by_plan = {p: v["logo_churn_pct"] for p, v in canonical["customer_health"]["plan_churn"].items()}
    assert set(by_segment.values()) != set(by_plan.values())
    pairs = {(r["segment"], r["plan"]) for r in D.customers()}
    segments_per_plan = {}
    for segment, plan in pairs:
        segments_per_plan.setdefault(plan, set()).add(segment)
    assert any(len(v) > 1 for v in segments_per_plan.values())


def test_the_worst_logo_churn_is_not_the_worst_arr_loss(canonical):
    """This is the whole point of D2 and it has to survive any data edit."""
    segments = canonical["customer_health"]["segment_churn"]
    worst_rate = max(segments, key=lambda s: segments[s]["logo_churn_pct"])
    worst_arr = max(segments, key=lambda s: segments[s]["arr_lost_eur"])
    assert worst_rate == "SMB"
    assert worst_arr != worst_rate
    assert segments["SMB"]["arr_lost_eur"] < segments["Mid-market"]["arr_lost_eur"]


def test_arr_totals_match_the_answer_key(canonical, ground_truth):
    key = ground_truth["customer_health"]
    assert canonical["customer_health"]["total_arr_eur"] == key["total_arr_eur"]
    assert canonical["customer_health"]["active_arr_eur"] == key["active_arr_eur"]
    assert (
        key["total_arr_eur"] - key["active_arr_eur"] == key["churned_arr_eur"]
    )


# ---------------------------------------------------------------------------
# D3 / D11 - the usage signals
# ---------------------------------------------------------------------------


def test_acme_is_a_false_positive_by_the_numbers(canonical, ground_truth):
    health = canonical["customer_health"]
    key = ground_truth["customer_health"]["acme_usage_interpretation"]
    assert health["acme_requests_change_pct"] == key["requests_change_pct"]
    assert health["acme_tokens_change_pct"] == key["tokens_change_pct"]
    assert health["acme_users_change_pct"] == key["active_users_change_pct"]
    # The trap only works if requests fall hard and everything else holds.
    assert health["acme_requests_change_pct"] < -40
    assert health["acme_tokens_change_pct"] > -20
    assert abs(health["acme_users_change_pct"]) < 10


def test_the_context_note_supports_acme_without_concluding_anything():
    text = (SCENARIO_DIR / "context.md").read_text(encoding="utf-8").lower()
    assert "batch" in text and "40" in text
    for forbidden in ("healthy", "not a churn", "no cause for concern", "expected decline"):
        assert forbidden not in text


def test_acme_revenue_and_tickets_do_not_move(ground_truth):
    key = ground_truth["customer_health"]["acme_usage_interpretation"]
    assert key["mrr_eur"]["september"] == key["mrr_eur"]["october"]
    assert D.tickets_for("acme-corp", SEP) == key["support_tickets"]["september"]
    assert D.tickets_for("acme-corp", OCT) == key["support_tickets"]["october"]


def test_soylent_shows_three_signals_and_no_mechanism(canonical, ground_truth):
    key = ground_truth["customer_health"]["causal_unknowns"]["soylent"]
    assert canonical["customer_health"]["soylent_requests_change_pct"] == key["requests_change_pct"]
    assert canonical["customer_health"]["soylent_tickets"] == [
        key["support_tickets"]["september"], key["support_tickets"]["october"]
    ]
    assert key["mrr_eur"]["october"] < key["mrr_eur"]["september"]
    # No candidate-visible file may explain any of it.
    for name in SOURCE_ORDER:
        text = (SCENARIO_DIR / name).read_text(encoding="utf-8").lower()
        assert "because" not in text or name == "context.md"


# ---------------------------------------------------------------------------
# D4 / D5 / D12 - acquisition
# ---------------------------------------------------------------------------


def test_attribution_matches_the_answer_key(canonical, ground_truth):
    derived = canonical["acquisition"]["attributed"]
    key = ground_truth["acquisition"]
    for channel, expected in key["raw_attributed_revenue_eur"].items():
        assert derived[channel]["raw"] == expected, channel
    for channel, expected in key["new_logo_revenue_eur"].items():
        assert derived[channel]["new_logo"] == expected, channel
    for channel, expected in key["expansion_revenue_eur"].items():
        assert derived[channel]["expansion"] == expected, channel


def test_the_attribution_ranking_reverses_on_new_logos(canonical):
    derived = canonical["acquisition"]["attributed"]
    raw_leader = max(derived, key=lambda c: derived[c]["raw"])
    new_leader = max(derived, key=lambda c: derived[c]["new_logo"])
    assert raw_leader == "paid_search"
    assert new_leader == "partner"
    ranking = sorted(derived, key=lambda c: derived[c]["new_logo"], reverse=True)
    assert ranking.index("paid_search") == 2


def test_paid_search_expansion_share(canonical, ground_truth):
    derived = canonical["acquisition"]["attributed"]["paid_search"]
    share = round(derived["expansion"] / derived["raw"] * 100, 2)
    assert share == ground_truth["acquisition"]["paid_search_expansion_share_pct"]
    assert share > 70


def test_expansion_rows_are_marked_and_predate_their_campaign():
    for row in D.acquisition():
        if row["expansion"] != "true":
            continue
        assert row["new_logo"] == "false", row["lead_id"]
        assert row["first_customer_date"] < row["campaign_start"], row["lead_id"]
    for row in D.acquisition():
        if row["new_logo"] != "true":
            continue
        assert row["expansion"] == "false", row["lead_id"]
        assert row["first_customer_date"] == row["conversion_date"], row["lead_id"]


def test_conversion_rates_match_the_answer_key(canonical, ground_truth):
    derived = canonical["acquisition"]["conversion"]
    key = ground_truth["acquisition"]["conversion_rates"]
    for month, name in ((SEP, "september"), (OCT, "october")):
        assert derived[month]["leads"] == key[name]["leads"], month
        assert derived[month]["conversions"] == key[name]["conversions"], month
        assert derived[month]["rate_pct"] == key[name]["rate_pct"], month


def test_the_funnel_moves_both_ways_at_once(canonical):
    derived = canonical["acquisition"]["conversion"]
    assert derived[OCT]["rate_pct"] < derived[SEP]["rate_pct"]
    assert derived[OCT]["conversions"] > derived[SEP]["conversions"]
    assert derived[OCT]["leads"] > derived[SEP]["leads"]


def test_channel_conversion_rates_match_the_answer_key(canonical, ground_truth):
    derived = canonical["acquisition"]["channel_conversion_pct"]
    for channel, months in ground_truth["acquisition"]["conversion_rates"]["by_channel_pct"].items():
        assert derived[channel][SEP] == months["september"], channel
        assert derived[channel][OCT] == months["october"], channel


def test_cac_payback_is_genuinely_impossible(canonical):
    """The epistemic criterion needs the input to be absent, not merely hidden."""
    assert canonical["acquisition"]["spend_columns"] == []
    for name in SOURCE_ORDER:
        text = (SCENARIO_DIR / name).read_text(encoding="utf-8").lower()
        for word in ("spend_eur", "cost_per_lead", "cac_eur", "marketing_spend", "ad_spend"):
            assert word not in text, f"{name} contains {word}"


def test_the_pack_asks_for_the_metric_it_cannot_answer():
    text = (SCENARIO_DIR / "context.md").read_text(encoding="utf-8").lower()
    assert "cac payback" in text


# ---------------------------------------------------------------------------
# D6 / D7 / D10 - plan economics
# ---------------------------------------------------------------------------


def test_plans_csv_has_no_precomputed_answer():
    with (SCENARIO_DIR / "plans.csv").open(encoding="utf-8", newline="") as handle:
        header = next(csv.reader(handle))
    for forbidden in ("margin", "contribution", "profit", "gross"):
        assert not any(forbidden in column.lower() for column in header), forbidden


def test_contribution_matches_the_answer_key(canonical, ground_truth):
    key = ground_truth["plans"]["contribution_eur"]
    for month, name in ((SEP, "september"), (OCT, "october")):
        for plan, expected in key[name].items():
            assert canonical["plans"][name][plan]["contribution_eur"] == expected, (month, plan)


def test_margins_match_the_answer_key(canonical, ground_truth):
    key = ground_truth["plans"]["contribution_margin_pct"]
    for name in ("september", "october"):
        for plan, expected in key[name].items():
            assert canonical["plans"][name][plan]["contribution_margin_pct"] == expected, (name, plan)


def test_arpu_and_contribution_per_customer_match_the_answer_key(canonical, ground_truth):
    for plan, expected in ground_truth["plans"]["arpu_eur"]["october"].items():
        assert canonical["plans"]["october"][plan]["arpu_eur"] == expected, plan
    for plan, expected in ground_truth["plans"]["contribution_per_customer_eur"]["october"].items():
        assert canonical["plans"]["october"][plan]["contribution_per_customer_eur"] == expected, plan


def test_highest_arpu_is_the_worst_margin(canonical):
    """D6 in one assertion. If this ever stops being true the scenario has lost
    its unit-economics trap."""
    october = canonical["plans"]["october"]
    top_arpu = max(october, key=lambda p: october[p]["arpu_eur"])
    worst_margin = min(october, key=lambda p: october[p]["contribution_margin_pct"])
    assert top_arpu == "enterprise"
    assert worst_margin == "enterprise"
    assert october["pro"]["contribution_margin_pct"] > october["enterprise"]["contribution_margin_pct"] * 2


def test_the_recommended_plan_is_not_the_biggest(canonical, ground_truth):
    focus = ground_truth["plans"]["recommended_product_focus"]["plan"]
    october = canonical["plans"]["october"]
    assert focus == "pro"
    assert october[focus]["revenue_eur"] < october["enterprise"]["revenue_eur"]
    assert october[focus]["contribution_eur"] < october["enterprise"]["contribution_eur"]
    assert october[focus]["contribution_margin_pct"] == max(
        october[p]["contribution_margin_pct"] for p in october
    )


def test_the_recommended_plan_carries_its_supporting_signals(canonical, ground_truth):
    key = ground_truth["plans"]
    usage = key["usage_signals"]
    derived_sep = canonical["plans"]["usage_totals_september"]
    derived_oct = canonical["plans"]["usage_totals_october"]
    for plan, expected in usage["total_requests"]["september"].items():
        assert derived_sep[plan] == expected, plan
    for plan, expected in usage["total_requests"]["october"].items():
        assert derived_oct[plan] == expected, plan
    # Pro grows against a flat Enterprise book.
    assert D.pct(derived_oct["pro"], derived_sep["pro"]) > 10
    assert abs(D.pct(derived_oct["enterprise"], derived_sep["enterprise"])) < 2
    over = canonical["plans"]["customers_over_included_october"]
    assert over == {k: v for k, v in usage["customers_over_included_october"].items() if v}
    assert over["pro"] == 3


def test_support_normalisation_reverses_the_raw_ranking(canonical, ground_truth):
    counts = canonical["plans"]["tickets_by_plan_october"]
    rates = canonical["plans"]["tickets_per_customer_october"]
    key = ground_truth["plans"]["support_load_october"]
    assert counts == key["tickets_by_plan"]
    assert rates == key["tickets_per_customer"]
    assert max(counts, key=counts.get) == "enterprise"
    assert max(rates, key=rates.get) == "pro"
    assert rates["pro"] > rates["enterprise"] * 1.2


def test_support_costs_and_ticket_counts_are_not_the_same_signal():
    """`support_cost_eur` includes staffing, so it cannot be read as a ticket
    count. If it tracked tickets exactly, D10 would be answerable from one
    table."""
    plans = {(r["month"], r["plan"]): float(r["support_cost_eur"]) for r in D.plans()}
    counts = D.tickets_by_plan(OCT)
    per_ticket = {plan: plans[(OCT, plan)] / counts[plan] for plan in counts}
    assert max(per_ticket.values()) / min(per_ticket.values()) > 3


# ---------------------------------------------------------------------------
# D9 - the alias join
# ---------------------------------------------------------------------------


def test_alias_map_matches_the_answer_key(canonical, ground_truth):
    assert canonical["data_quality"]["aliases"] == ground_truth["data_quality"]["customer_id_aliases"]


def test_a_naive_join_loses_a_major_account(ground_truth):
    """The trap, asserted rather than assumed: joining on customer_id drops
    Wayne, and Wayne is large enough that the loss changes conclusions."""
    accounts = {r["usage_account_id"] for r in D.usage()}
    customers = {r["customer_id"]: r for r in D.customers()}
    dropped = [cid for cid in customers if cid not in accounts]
    assert "wayne-enterprises" in dropped
    wayne = customers["wayne-enterprises"]
    ranked = sorted(customers.values(), key=lambda r: float(r["arr_eur"]), reverse=True)
    assert ranked.index(wayne) < 5
    key = ground_truth["data_quality"]["wayne_usage_requests"]
    series = D.usage_by_account()["wayne_ent"]
    assert series[SEP]["requests"] == key["september"]
    assert series[OCT]["requests"] == key["october"]


def test_the_alias_is_resolvable_without_guessing():
    """`usage_account_id` is in customers.csv, so no fuzzy matching is needed."""
    with (SCENARIO_DIR / "customers.csv").open(encoding="utf-8", newline="") as handle:
        header = next(csv.reader(handle))
    assert "usage_account_id" in header
    text = (SCENARIO_DIR / "context.md").read_text(encoding="utf-8")
    assert "usage_account_id" in text and "authoritative" in text


# ---------------------------------------------------------------------------
# Answer leakage
# ---------------------------------------------------------------------------

# Words and phrases that would turn a derivation into a reading comprehension
# question. Checked across every candidate-visible source.
FORBIDDEN_CONCLUSIONS = [
    "duplicate", "double-counted", "double counted", "counted twice",
    "misleading", "distort", "overstate", "understate", "inflated",
    "actually flat", "not a concern", "best plan", "worst margin",
    "cannot be calculated", "cannot be computed", "not comparable",
    "correlation", "causation", "watch out", "note that this",
    "should not", "beware", "artifact", "anomaly",
]


def test_no_candidate_source_states_a_conclusion(scenario):
    for name in scenario.sources:
        text = (SCENARIO_DIR / name).read_text(encoding="utf-8").lower()
        for phrase in FORBIDDEN_CONCLUSIONS:
            assert phrase not in text, f"{name} contains {phrase!r}"


def test_no_candidate_source_names_the_answer():
    """The three decisions must not be pre-answered anywhere."""
    banned = [
        "paid search is", "smb should", "pro is the", "enterprise is the",
        "recommend", "we should", "prioriti",
    ]
    for name in SOURCE_ORDER:
        text = (SCENARIO_DIR / name).read_text(encoding="utf-8").lower()
        for phrase in banned:
            assert phrase not in text, f"{name} contains {phrase!r}"


def test_the_prompt_gives_no_hints(scenario):
    text = scenario.prompt_template.lower()
    for hint in ("duplicate", "annual", "correlation", "causation", "normalis", "normaliz", "mrr"):
        assert hint not in text, hint


# ---------------------------------------------------------------------------
# Publication gates
# ---------------------------------------------------------------------------


def test_a_calibration_scenario_cannot_be_published(scenario):
    from mondaybench.leaderboard import write_leaderboard

    payload = {
        "scenario": scenario.id,
        "evaluator": EVALUATOR,
        "scenario_status": scenario.status,
        "official": True,
        "models": [],
    }
    with pytest.raises(ValueError):
        write_leaderboard(payload, [], calibration=False)


def test_qualification_gates_apply_to_this_scenario_too(scenario):
    """The hardened gates are shared, so this only checks they are wired to
    monday-004's prompt: a run generated against different bytes, or truncated,
    cannot become evidence for it."""
    from mondaybench.official import qualify_run
    from test_official import make_run

    prompt = build_prompt(scenario)

    good = make_run(scenario_id="monday-004", prompt_hash=prompt.sha256, max_output_tokens=32000)
    assert qualify_run(
        good, path=Path("x"), expected_prompt_sha256=prompt.sha256, model=None, scenario_id="monday-004"
    ).official

    wrong_prompt = make_run(scenario_id="monday-004", prompt_hash="0" * 64, max_output_tokens=32000)
    verdict = qualify_run(
        wrong_prompt, path=Path("x"), expected_prompt_sha256=prompt.sha256, model=None, scenario_id="monday-004"
    )
    assert not verdict.official
    assert any("prompt hash" in r for r in verdict.reasons)

    truncated = make_run(
        scenario_id="monday-004", prompt_hash=prompt.sha256, finish_reason="length", max_output_tokens=32000
    )
    assert not qualify_run(
        truncated, path=Path("x"), expected_prompt_sha256=prompt.sha256, model=None, scenario_id="monday-004"
    ).official


# ---------------------------------------------------------------------------
# The three frozen scenarios are untouched
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("scenario_id", ["monday-001", "monday-002", "monday-003"])
def test_published_scenarios_still_verify(scenario_id):
    directory = REPO_ROOT / "scenarios" / scenario_id
    manifest = load_manifest(directory)
    assert manifest is not None, f"{scenario_id} has no freeze manifest"
    drift = check_drift(manifest, directory)
    assert drift.clean, f"{scenario_id} has drifted: {drift}"


@pytest.mark.parametrize(
    "scenario_id,expected",
    [
        ("monday-003", "aaf788f309d955d2b427c86fe7d95d2bbf88575fde7306adcfd74b0ec4a4103f"),
    ],
)
def test_published_prompt_hashes_are_unchanged(scenario_id, expected):
    assert build_prompt(load_scenario(scenario_id)).sha256 == expected


# ---------------------------------------------------------------------------
# Proposed rubric 0.2 (not adopted)
# ---------------------------------------------------------------------------
#
# rubric-0.2.yaml is a proposal. These tests guard the two properties that make
# it a *proposal about scoring* rather than a new scenario: it still totals 100,
# and it leaves the candidate-visible bytes alone so the v0.1 responses remain
# valid evidence for it. They do not assert that it is the rubric in force.


def test_proposed_rubric_v02_totals_one_hundred():
    proposed = load_scenario("monday-004", rubric_file="rubric-0.2.yaml").rubric
    assert proposed.version == "0.2"
    assert sum(proposed.dimension_max.values()) == 100
    assert len(proposed.criteria) == 26
    for dimension, maximum in proposed.dimension_max.items():
        earned = sum(c.points_pass for c in proposed.criteria_for(dimension))
        assert earned == maximum, dimension


def test_v01_rubric_is_untouched_by_the_proposal():
    """v0.1 has to keep reproducing the first calibration's scores exactly.

    Loaded by name rather than through the scenario, which now defaults to the
    frozen 0.3.
    """
    rubric = load_scenario("monday-004", rubric_file="rubric.yaml").rubric
    assert rubric.version == "0.1"
    assert len(rubric.criteria) == 25
    assert sum(rubric.dimension_max.values()) == 100
    ids = {c.id for c in rubric.criteria}
    assert "segment_churn_math" in ids
    assert "enterprise_revenue_not_margin" in ids


def test_the_proposal_does_not_move_the_candidate_prompt(scenario):
    """The whole point of a rubric-only revision.

    If this ever fails, the v0.1 responses have stopped being evidence for v0.2
    and the shadow rescore is void.
    """
    proposed = load_scenario("monday-004", rubric_file="rubric-0.2.yaml")
    assert build_prompt(proposed).sha256 == PROMPT_SHA256
    assert build_prompt(scenario).sha256 == build_prompt(proposed).sha256
    assert proposed.sources == scenario.sources


def test_proposed_rubric_v02_renames_and_replaces_as_documented():
    proposed = load_scenario("monday-004", rubric_file="rubric-0.2.yaml").rubric
    ids = {c.id for c in proposed.criteria}
    assert "segment_retention_quantified" in ids
    assert "segment_churn_math" not in ids
    assert "absolute_vs_scalable_economics" in ids
    assert "plan_trajectory_evidence" in ids
    assert "enterprise_revenue_not_margin" not in ids
    points = {c.id: c.points_pass for c in proposed.criteria}
    assert points["contribution_calculated"] == 4
    assert points["margin_calculated_or_correctly_compared"] == 3
    assert points["product_focus_supported"] == 5
    assert max(points.values()) <= 6


def test_shadow_evaluator_is_bound_to_the_proposal():
    cfg = load_evaluator("evaluator-opus5-v0.4-calibration-2")
    assert cfg.scenario == "monday-004"
    assert cfg.scenario_version == "0.1"
    assert cfg.rubric_version == "0.2"
    assert cfg.rubric_file == "rubric-0.2.yaml"
    assert cfg.id.endswith("-calibration-2")


# ---------------------------------------------------------------------------
# Generation ceiling policy
# ---------------------------------------------------------------------------


def test_monday_004_declares_its_own_safety_ceiling(scenario):
    """The ceiling is per scenario so the frozen three keep theirs."""
    assert scenario.safety_ceiling_tokens == 96000
    for frozen in ("monday-001", "monday-002", "monday-003"):
        assert load_scenario(frozen).safety_ceiling_tokens is None


def test_the_ceiling_does_not_move_the_candidate_prompt(scenario):
    """scenario.yaml is not a candidate source, so declaring a ceiling in it
    must leave the rendered prompt byte-identical."""
    assert build_prompt(scenario).sha256 == PROMPT_SHA256


def test_effective_ceiling_falls_back_to_the_model_default():
    from mondaybench.config import load_models
    from mondaybench.runner import effective_ceiling

    models = load_models()
    assert effective_ceiling(load_scenario("monday-004"), models["gemma4"]) == 96000
    # The frozen three inherit models.yaml unchanged, which is what keeps their
    # published runs qualifying.
    for frozen in ("monday-001", "monday-002", "monday-003"):
        assert effective_ceiling(load_scenario(frozen), models["gemma4"]) == 32000


@pytest.mark.parametrize(
    "finish_reason,delivered,expected",
    [
        ("stop", 20000, "NON_BINDING"),
        ("length", 32000, "BOUND"),
        ("stop", 32000, "BOUND"),
        # A provider that ignored the parameter is NOT bound by it. The audit
        # proved `max_tokens` is applied inconsistently, so exceeding it is the
        # provider's implementation and must never disqualify a candidate.
        ("stop", 58956, "NON_BINDING"),
    ],
)
def test_generation_ceiling_status(finish_reason, delivered, expected):
    from mondaybench.official import generation_ceiling_status
    from test_official import make_run

    run = make_run(finish_reason=finish_reason, max_output_tokens=32000)
    run.usage.output_tokens = delivered
    assert generation_ceiling_status(run) == expected


def test_exceeding_the_legacy_max_tokens_is_not_a_rejection(scenario):
    """The audit's central finding, encoded as a gate.

    qwen3.8-flash has returned up to 84% more completion tokens than the
    configured value on every scenario it has run. That is the provider not
    implementing a legacy parameter, and a benchmark must not fail a model for
    it.
    """
    from mondaybench.official import qualify_run
    from test_official import make_run

    prompt = build_prompt(scenario)
    run = make_run(
        scenario_id="monday-004", prompt_hash=prompt.sha256, max_output_tokens=96000
    )
    run.usage.output_tokens = 120000
    verdict = qualify_run(
        run,
        path=Path("x"),
        expected_prompt_sha256=prompt.sha256,
        model=None,
        scenario_id="monday-004",
        expected_max_output_tokens=96000,
    )
    assert verdict.official, verdict.reasons


def test_a_ceiling_bound_run_does_not_qualify(scenario):
    from mondaybench.official import qualify_run
    from test_official import make_run

    prompt = build_prompt(scenario)
    run = make_run(
        scenario_id="monday-004",
        prompt_hash=prompt.sha256,
        finish_reason="length",
        max_output_tokens=96000,
    )
    verdict = qualify_run(
        run,
        path=Path("x"),
        expected_prompt_sha256=prompt.sha256,
        model=None,
        scenario_id="monday-004",
        expected_max_output_tokens=96000,
    )
    assert not verdict.official
    assert any("BOUND" in r for r in verdict.reasons)


# ---------------------------------------------------------------------------
# Proposed rubric 0.3 (not adopted)
# ---------------------------------------------------------------------------


def test_proposed_rubric_v03_totals_one_hundred():
    proposed = load_scenario("monday-004", rubric_file="rubric-0.3.yaml").rubric
    assert proposed.version == "0.3"
    assert sum(proposed.dimension_max.values()) == 100
    assert len(proposed.criteria) == 27
    for dimension, maximum in proposed.dimension_max.items():
        earned = sum(c.points_pass for c in proposed.criteria_for(dimension))
        assert earned == maximum, dimension


def test_v03_adds_the_figure_accuracy_criterion_and_funds_it():
    v02 = {c.id: c.points_pass for c in load_scenario("monday-004", rubric_file="rubric-0.2.yaml").rubric.criteria}
    v03 = {c.id: c.points_pass for c in load_scenario("monday-004", rubric_file="rubric-0.3.yaml").rubric.criteria}
    assert "figures_carried_correctly" not in v02
    assert v03["figures_carried_correctly"] == 3
    # Funded from three criteria that scored 6/6 PASS in both shadow rescores.
    assert (v02["cac_payback_unavailable"], v03["cac_payback_unavailable"]) == (3, 2)
    assert (v02["contribution_calculated"], v03["contribution_calculated"]) == (4, 3)
    assert (v02["product_recommendation"], v03["product_recommendation"]) == (2, 1)
    moved = sum(v02[k] - v03[k] for k in v02 if k in v03 and v03[k] < v02[k])
    assert moved == 3


def test_every_proposed_rubric_keeps_the_same_prompt(scenario):
    for rubric_file in ("rubric.yaml", "rubric-0.2.yaml", "rubric-0.3.yaml"):
        loaded = load_scenario("monday-004", rubric_file=rubric_file)
        assert build_prompt(loaded).sha256 == PROMPT_SHA256, rubric_file
        assert loaded.sources == scenario.sources


# ---------------------------------------------------------------------------
# The calibration battery, now archived.
#
# It was generated after the ceiling policy and scored under rubric 0.3, and it
# is the evidence that produced the FREEZE recommendation. It is NOT official
# evidence: rubric 0.3 was written while reading these responses. These tests
# assert it survived archiving intact and stays out of the official tree.
# ---------------------------------------------------------------------------

ARCHIVE = REPO_ROOT / "archive" / "monday-004-v0.3-calibration"
CALIBRATION_RUNS = {
    "qwen3.8-flash": 2,
    "glm5.3-flash": 2,
    "deepseek-v4-flash": 3,
    "mimo-v2.5": 3,
    "glm5.2": 2,
    "qwen3.6": 2,
    "gemma4": 2,
}
CALIBRATION_EVALUATOR = "evaluator-opus5-v0.4-calibration-3"


def _calibration_run(slug: str) -> dict:
    path = ARCHIVE / "runs-monday-004" / slug / f"run-{CALIBRATION_RUNS[slug]:03d}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _calibration_evaluation(slug: str) -> dict:
    path = (
        ARCHIVE
        / f"evaluations-{CALIBRATION_EVALUATOR}"
        / slug
        / f"run-{CALIBRATION_RUNS[slug]:03d}.json"
    )
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("slug", sorted(CALIBRATION_RUNS))
def test_every_calibration_run_was_complete_and_unbound(slug, scenario):
    """The whole point of the ceiling policy: nothing was cut off."""
    from mondaybench.official import CEILING_NON_BINDING, generation_ceiling_status
    from mondaybench.schemas import BenchmarkRun

    run = BenchmarkRun.model_validate(_calibration_run(slug))
    assert run.finish_reason == "stop"
    assert run.generation.safety_ceiling_tokens == scenario.safety_ceiling_tokens == 96_000
    assert run.generation.ceiling_semantics == "provider_specific"
    assert generation_ceiling_status(run) == CEILING_NON_BINDING


@pytest.mark.parametrize("slug", sorted(CALIBRATION_RUNS))
def test_calibration_runs_are_out_of_the_official_tree(slug):
    """Archived, so `run --reuse-valid-runs` cannot count one toward the three."""
    number = CALIBRATION_RUNS[slug]
    assert not (REPO_ROOT / "runs" / "monday-004" / slug / f"run-{number:03d}.json").exists()
    assert (ARCHIVE / "runs-monday-004" / slug / f"run-{number:03d}.json").is_file()


@pytest.mark.parametrize("slug", sorted(CALIBRATION_RUNS))
def test_every_criterion_of_rubric_v03_was_labelled(slug):
    """No criterion defaulted, and none scored that the rubric does not define."""
    rubric = load_scenario("monday-004", rubric_file="rubric-0.3.yaml").rubric
    evaluation = _calibration_evaluation(slug)
    assert evaluation["rubric_version"] == "0.3"
    assert set(evaluation["criteria"]) == {c.id for c in rubric.criteria}
    assert sum(c["points_possible"] for c in evaluation["criteria"].values()) == 100


def test_the_calibration_battery_was_judged_from_recorded_verdicts():
    """No API call reached a judge. The verdicts are archived and replayable."""
    verdicts = ARCHIVE / "verdicts" / "calibration-v0.3.jsonl"
    entries = [
        json.loads(line)
        for line in verdicts.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    criteria = [e for e in entries if e["kind"] == "criterion"]
    assert len(criteria) == 27 * len(CALIBRATION_RUNS)
    assert {e["run_id"] for e in entries} == {
        f"monday-004__{slug}__{number:03d}" for slug, number in CALIBRATION_RUNS.items()
    }
    for slug in CALIBRATION_RUNS:
        assert _calibration_evaluation(slug)["judge"]["route"] == "recorded"


def test_the_new_criterion_discriminated():
    """`figures_carried_correctly` was added to price something. It priced it."""
    labels = {
        slug: _calibration_evaluation(slug)["criteria"]["figures_carried_correctly"]["result"]
        for slug in CALIBRATION_RUNS
    }
    assert set(labels.values()) == {"PASS", "PARTIAL", "FAIL"}
    # The two leaders are the reason it exists: neither scored a perfect 100.
    assert labels["qwen3.8-flash"] == "PARTIAL"
    assert labels["glm5.3-flash"] == "PARTIAL"


def test_calibration_penalties_stayed_conservative():
    """A penalty needs a recommended action, not merely a weak answer."""
    charged = {}
    for slug in CALIBRATION_RUNS:
        items = _calibration_evaluation(slug)["penalties"]["items"]
        if items:
            charged[slug] = [i["type"] for i in items]
    assert charged == {
        "deepseek-v4-flash": ["PROHIBITED_ACTION"],
        "glm5.2": ["PROHIBITED_ACTION"],
    }
    for slug in charged:
        assert _calibration_evaluation(slug)["criteria"]["segment_recommendation"]["result"] == "FAIL"
    # MIMO fails figure accuracy on four wrong numbers and is deliberately not
    # penalised: none of them carries a recommendation.
    mimo = _calibration_evaluation("mimo-v2.5")
    assert mimo["criteria"]["figures_carried_correctly"]["result"] == "FAIL"
    assert mimo["penalties"]["items"] == []


def test_the_calibration_draft_was_never_published():
    """The draft stays in archive/, and what got published is not it.

    monday-004 is now published, so "leaderboard/monday-004 does not exist" is
    no longer the way to check this. The guard that still bites is that the
    published board is the official one - official evaluator, official flag,
    frozen rubric - and carries none of the calibration draft's markings.
    """
    board = ARCHIVE / "draft-leaderboard" / "leaderboard.json"
    payload = json.loads(board.read_text(encoding="utf-8"))
    assert payload["scenario_status"] == "calibration"
    assert payload["evaluator"] == CALIBRATION_EVALUATOR
    assert not payload.get("official")

    published = json.loads(
        (REPO_ROOT / "leaderboard" / "monday-004" / "leaderboard.json").read_text(
            encoding="utf-8"
        )
    )
    assert published["official"] is True
    assert published["evaluator"] != CALIBRATION_EVALUATOR
    assert published["scenario_status"] != "calibration"
    assert published["rubric_version"] == "0.3"


def test_naming_a_rubric_explicitly_overrides_the_scenario_default():
    """The sentinel used to be the filename, so you could not ask for rubric.yaml.

    `load_scenario(..., rubric_file="rubric.yaml")` was indistinguishable from
    passing nothing. Once monday-004's scenario pointed at rubric-0.3.yaml, the
    calibration evaluator that declares `rubric_file: rubric.yaml` silently
    started resolving to 0.3 - which would have rescored the first battery under
    a rubric it never saw.
    """
    assert load_scenario("monday-004").rubric.version == "0.3"
    assert load_scenario("monday-004", rubric_file="rubric.yaml").rubric.version == "0.1"
    assert load_scenario("monday-004", rubric_file="rubric-0.2.yaml").rubric.version == "0.2"
    assert load_scenario("monday-004", rubric_file="rubric-0.3.yaml").rubric.version == "0.3"
    # Each calibration evaluator still reaches the rubric it was written for.
    for evaluator_id, version in (
        ("evaluator-opus5-v0.4-calibration", "0.1"),
        ("evaluator-opus5-v0.4-calibration-2", "0.2"),
        ("evaluator-opus5-v0.4-calibration-3", "0.3"),
    ):
        cfg = load_evaluator(evaluator_id)
        assert load_scenario("monday-004", rubric_file=cfg.rubric_file).rubric.version == version


def test_an_empty_official_leaderboard_cannot_be_written(tmp_path):
    """An empty ranking still renders "Every publication gate passed"."""
    from mondaybench.leaderboard import write_leaderboard

    payload = {
        "scenario": "monday-004",
        "evaluator": "evaluator-opus5-v0.4",
        "scenario_status": "official",
        "official": True,
        "models": [],
    }
    with pytest.raises(ValueError, match="no models"):
        write_leaderboard(payload, [], root=tmp_path, calibration=False)
    assert not (tmp_path / "leaderboard").exists()
