"""Canonical numbers for monday-004, recomputed from the published CSVs.

Deliberately independent of `tools/build_monday_004.py`. That script holds the
design - which customer pays what, which invoice is duplicated - and writes the
files. This module reads the files back and derives the answer key from them,
the same way a candidate has to. `tests/test_monday_004.py` then asserts that
`ground-truth.yaml` agrees with what is derived here.

The point of the separation: nothing in the answer key is hand-typed. If the
data changes, the derived numbers change, the ground truth stops matching and
the tests fail. A wrong number cannot survive in the answer key while the data
says something else.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "scenarios" / "monday-004"

SEP = "2026-09"
OCT = "2026-10"


def _read(name: str) -> list[dict[str, str]]:
    with (D / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def customers() -> list[dict[str, str]]:
    return _read("customers.csv")


def revenue() -> list[dict[str, str]]:
    return _read("revenue.csv")


def usage() -> list[dict[str, str]]:
    return _read("usage.csv")


def plans() -> list[dict[str, str]]:
    return _read("plans.csv")


def acquisition() -> list[dict[str, str]]:
    return _read("acquisition.csv")


def funnel() -> list[dict[str, str]]:
    return _read("funnel.csv")


def support() -> list[dict[str, str]]:
    return _read("support.csv")


def _month(row: dict[str, str]) -> str:
    return row["date"][:7]


def pct(new: float, old: float) -> float:
    """Percentage change, rounded to two decimals."""
    return round((new - old) / old * 100, 2)


# --------------------------------------------------------------------------
# Revenue (D1, D8)
# --------------------------------------------------------------------------


def duplicate_transaction_ids() -> list[str]:
    """Transaction ids that appear more than once in revenue.csv."""
    seen: dict[str, int] = defaultdict(int)
    for row in revenue():
        seen[row["transaction_id"]] += 1
    return sorted(tid for tid, n in seen.items() if n > 1)


def duplicate_rows() -> list[dict[str, str]]:
    ids = set(duplicate_transaction_ids())
    return [r for r in revenue() if r["transaction_id"] in ids]


def raw_total(month: str) -> float:
    """Every row, summed as it stands - the headline figure."""
    return round(sum(float(r["amount_eur"]) for r in revenue() if _month(r) == month), 2)


def deduplicated_total(month: str) -> float:
    """Each transaction id counted once."""
    seen: set[str] = set()
    total = 0.0
    for row in revenue():
        if _month(row) != month or row["transaction_id"] in seen:
            continue
        seen.add(row["transaction_id"])
        total += float(row["amount_eur"])
    return round(total, 2)


def recurring_total(month: str) -> float:
    """Subscriptions at their monthly value, deduplicated.

    An invoice covering `billing_period_months` months contributes
    `amount / billing_period_months`; one-off invoices (period 0) contribute
    nothing to a recurring figure.
    """
    seen: set[str] = set()
    total = 0.0
    for row in revenue():
        if _month(row) != month or row["transaction_id"] in seen:
            continue
        seen.add(row["transaction_id"])
        months = int(row["billing_period_months"])
        if months <= 0:
            continue
        total += float(row["amount_eur"]) / months
    return round(total, 2)


def normalized_all_invoices(month: str) -> float:
    """Recurring plus one-off, with the annual invoice at its monthly value.

    The other defensible normalisation. It answers a different question -
    "what did we invoice for this month's activity" rather than "what recurs" -
    and because September carried EUR 51,000 of professional services against
    October's EUR 5,700, it lands at about -4% where the recurring view lands at
    about +1.6%. Both refute the +12% headline; the rubric accepts either when
    the treatment is stated.
    """
    return round(recurring_total(month) + one_off_total(month), 2)


def one_off_total(month: str) -> float:
    seen: set[str] = set()
    total = 0.0
    for row in revenue():
        if _month(row) != month or row["transaction_id"] in seen:
            continue
        seen.add(row["transaction_id"])
        if int(row["billing_period_months"]) == 0:
            total += float(row["amount_eur"])
    return round(total, 2)


def annual_invoices() -> list[dict[str, str]]:
    return [r for r in revenue() if int(r["billing_period_months"]) > 1]


# --------------------------------------------------------------------------
# Customer health (D2)
# --------------------------------------------------------------------------


def segment_churn() -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for row in customers():
        seg = row["segment"]
        bucket = out.setdefault(seg, {"customers": 0, "churned": 0, "arr_lost_eur": 0.0, "arr_total_eur": 0.0})
        bucket["customers"] += 1
        bucket["arr_total_eur"] += float(row["arr_eur"])
        if row["status"] == "churned":
            bucket["churned"] += 1
            bucket["arr_lost_eur"] += float(row["arr_eur"])
    for bucket in out.values():
        bucket["logo_churn_pct"] = round(bucket["churned"] / bucket["customers"] * 100, 2)
        bucket["arr_lost_eur"] = round(bucket["arr_lost_eur"], 2)
        bucket["arr_total_eur"] = round(bucket["arr_total_eur"], 2)
    return out


def plan_churn() -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for row in customers():
        bucket = out.setdefault(row["plan"], {"customers": 0, "churned": 0})
        bucket["customers"] += 1
        if row["status"] == "churned":
            bucket["churned"] += 1
    for bucket in out.values():
        bucket["logo_churn_pct"] = round(bucket["churned"] / bucket["customers"] * 100, 2)
    return out


def total_arr() -> float:
    return round(sum(float(r["arr_eur"]) for r in customers()), 2)


def active_arr() -> float:
    return round(sum(float(r["arr_eur"]) for r in customers() if r["status"] == "active"), 2)


# --------------------------------------------------------------------------
# Usage (D3, D9, D11)
# --------------------------------------------------------------------------


def usage_by_account() -> dict[str, dict[str, dict[str, float]]]:
    out: dict[str, dict[str, dict[str, float]]] = defaultdict(dict)
    for row in usage():
        out[row["usage_account_id"]][row["month"]] = {
            "requests": float(row["requests"]),
            "tokens_m": float(row["tokens_m"]),
            "active_users": float(row["active_users"]),
        }
    return out


def alias_map() -> dict[str, str]:
    """customer_id -> usage_account_id, only where the two differ."""
    return {
        r["customer_id"]: r["usage_account_id"]
        for r in customers()
        if r["customer_id"] != r["usage_account_id"]
    }


def account_change(customer_id: str, field: str = "requests") -> float:
    row = next(r for r in customers() if r["customer_id"] == customer_id)
    series = usage_by_account()[row["usage_account_id"]]
    return pct(series[OCT][field], series[SEP][field])


# --------------------------------------------------------------------------
# Acquisition (D4, D5, D12)
# --------------------------------------------------------------------------


def attributed_by_channel() -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for row in acquisition():
        bucket = out.setdefault(row["channel"], {"raw": 0.0, "new_logo": 0.0, "expansion": 0.0})
        amount = float(row["attributed_revenue_eur"])
        bucket["raw"] += amount
        if row["new_logo"] == "true":
            bucket["new_logo"] += amount
        if row["expansion"] == "true":
            bucket["expansion"] += amount
    for bucket in out.values():
        for key in bucket:
            bucket[key] = round(bucket[key], 2)
    return out


def conversion_rates() -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for row in funnel():
        bucket = out.setdefault(row["month"], {"leads": 0.0, "conversions": 0.0})
        bucket["leads"] += float(row["leads"])
        bucket["conversions"] += float(row["conversions"])
    for bucket in out.values():
        bucket["rate_pct"] = round(bucket["conversions"] / bucket["leads"] * 100, 2)
    return out


def channel_conversion_rates() -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = defaultdict(dict)
    for row in funnel():
        out[row["channel"]][row["month"]] = round(
            float(row["conversions"]) / float(row["leads"]) * 100, 2
        )
    return dict(out)


def spend_columns_present() -> list[str]:
    """Any column in any candidate source that could carry acquisition spend.

    `cac_payback_unavailable` rests on there being none, so it is asserted
    rather than assumed.
    """
    hits: list[str] = []
    for name in ("customers.csv", "revenue.csv", "usage.csv", "plans.csv", "acquisition.csv", "funnel.csv", "support.csv"):
        with (D / name).open(encoding="utf-8", newline="") as handle:
            header = next(csv.reader(handle))
        for column in header:
            lowered = column.lower()
            if any(word in lowered for word in ("spend", "cac", "budget", "marketing_cost", "sales_cost")):
                hits.append(f"{name}:{column}")
    return hits


# --------------------------------------------------------------------------
# Plan economics (D6, D7, D10)
# --------------------------------------------------------------------------


def plan_economics() -> dict[str, dict[str, dict[str, float]]]:
    out: dict[str, dict[str, dict[str, float]]] = defaultdict(dict)
    for row in plans():
        revenue_eur = float(row["revenue_eur"])
        infra = float(row["infra_cost_eur"])
        support_cost = float(row["support_cost_eur"])
        contribution = revenue_eur - infra - support_cost
        customers_n = float(row["customers"])
        out[row["month"]][row["plan"]] = {
            "customers": customers_n,
            "revenue_eur": revenue_eur,
            "contribution_eur": round(contribution, 2),
            "contribution_margin_pct": round(contribution / revenue_eur * 100, 2),
            "arpu_eur": round(revenue_eur / customers_n, 2),
            "contribution_per_customer_eur": round(contribution / customers_n, 2),
            "avg_requests_per_customer": float(row["avg_requests_per_customer"]),
            "included_requests_per_customer": float(row["included_requests_per_customer"]),
        }
    return dict(out)


def plan_of() -> dict[str, str]:
    return {r["customer_id"]: r["plan"] for r in customers()}


def tickets_by_plan(month: str) -> dict[str, int]:
    plan = plan_of()
    out: dict[str, int] = defaultdict(int)
    for row in support():
        if row["month"] != month:
            continue
        out[plan[row["customer_id"]]] += 1
    return dict(out)


def tickets_per_customer(month: str) -> dict[str, float]:
    counts = tickets_by_plan(month)
    economics = plan_economics()[month]
    return {
        plan: round(counts.get(plan, 0) / economics[plan]["customers"], 2)
        for plan in economics
    }


def tickets_for(customer_id: str, month: str) -> int:
    return sum(1 for r in support() if r["month"] == month and r["customer_id"] == customer_id)


def plan_usage_totals(month: str) -> dict[str, float]:
    plan = plan_of()
    account_of = {r["customer_id"]: r["usage_account_id"] for r in customers()}
    by_account = {(r["month"], r["usage_account_id"]): float(r["requests"]) for r in usage()}
    out: dict[str, float] = defaultdict(float)
    for customer_id, plan_name in plan.items():
        requests = by_account.get((month, account_of[customer_id]))
        if requests is not None:
            out[plan_name] += requests
    return dict(out)


def customers_over_included(month: str) -> dict[str, int]:
    plan = plan_of()
    account_of = {r["customer_id"]: r["usage_account_id"] for r in customers()}
    included = {row["plan"]: float(row["included_requests_per_customer"]) for row in plans() if row["month"] == month}
    by_account = {(r["month"], r["usage_account_id"]): float(r["requests"]) for r in usage()}
    out: dict[str, int] = defaultdict(int)
    for customer_id, plan_name in plan.items():
        requests = by_account.get((month, account_of[customer_id]))
        if requests is not None and requests > included[plan_name]:
            out[plan_name] += 1
    return dict(out)


# --------------------------------------------------------------------------
# One call that produces every published canonical number
# --------------------------------------------------------------------------


def canonical() -> dict:
    econ = plan_economics()
    channels = attributed_by_channel()
    rates = conversion_rates()
    return {
        "revenue": {
            "duplicate_transaction_ids": duplicate_transaction_ids(),
            "raw_september_eur": raw_total(SEP),
            "raw_october_eur": raw_total(OCT),
            "headline_growth_pct": pct(raw_total(OCT), raw_total(SEP)),
            "october_deduplicated_eur": deduplicated_total(OCT),
            "deduplicated_growth_pct": pct(deduplicated_total(OCT), raw_total(SEP)),
            "recurring_september_eur": recurring_total(SEP),
            "recurring_october_eur": recurring_total(OCT),
            "recurring_growth_pct": pct(recurring_total(OCT), recurring_total(SEP)),
            "one_off_september_eur": one_off_total(SEP),
            "one_off_october_eur": one_off_total(OCT),
            "normalized_all_invoices_september_eur": normalized_all_invoices(SEP),
            "normalized_all_invoices_october_eur": normalized_all_invoices(OCT),
            "normalized_all_invoices_growth_pct": pct(
                normalized_all_invoices(OCT), normalized_all_invoices(SEP)
            ),
        },
        "customer_health": {
            "segment_churn": segment_churn(),
            "plan_churn": plan_churn(),
            "total_arr_eur": total_arr(),
            "active_arr_eur": active_arr(),
            "acme_requests_change_pct": account_change("acme-corp", "requests"),
            "acme_tokens_change_pct": account_change("acme-corp", "tokens_m"),
            "acme_users_change_pct": account_change("acme-corp", "active_users"),
            "soylent_requests_change_pct": account_change("soylent", "requests"),
            "soylent_tickets": [tickets_for("soylent", SEP), tickets_for("soylent", OCT)],
        },
        "acquisition": {
            "attributed": channels,
            "conversion": rates,
            "channel_conversion_pct": channel_conversion_rates(),
            "spend_columns": spend_columns_present(),
        },
        "plans": {
            "september": econ[SEP],
            "october": econ[OCT],
            "tickets_per_customer_october": tickets_per_customer(OCT),
            "tickets_by_plan_october": tickets_by_plan(OCT),
            "customers_over_included_october": customers_over_included(OCT),
            "usage_totals_september": plan_usage_totals(SEP),
            "usage_totals_october": plan_usage_totals(OCT),
        },
        "data_quality": {
            "aliases": alias_map(),
            "duplicate_rows": len(duplicate_rows()),
        },
    }


if __name__ == "__main__":  # pragma: no cover - developer convenience
    import json

    print(json.dumps(canonical(), indent=2, sort_keys=True))
