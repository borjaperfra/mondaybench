"""Canonical numbers for monday-005, recomputed from the published sources.

Same separation as `monday_005`'s predecessor: this module reads the
candidate-visible files back and derives the answer key from them, the way a
candidate has to. `tests/test_monday_005.py` then asserts that
`ground-truth.yaml` agrees with what is derived here.

Nothing in the answer key is hand-typed. If `customer-impact.csv` changes, the
derived numbers change, the ground truth stops matching, and the tests fail.

#005 carries much less arithmetic than #004 by design - it is a communication
scenario, not an analysis one - so this module is short. What it does cover is
the part that IS numeric and IS a trap: the impact rate and its two wrong
denominators.
"""

from __future__ import annotations

import csv
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "scenarios" / "monday-005"

# Stated in context.md as the platform-wide figure for the same window. It is
# the denominator that minimises, and it is deliberately reachable.
PLATFORM_REQUESTS_WINDOW = 842_000
TOTAL_ACCOUNTS = 36


def _read(name: str) -> list[dict[str, str]]:
    with (D / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def impact_rows() -> list[dict[str, str]]:
    return _read("customer-impact.csv")


def support_tickets() -> list[dict[str, str]]:
    return _read("support-tickets.csv")


def _req(row: dict[str, str]) -> int:
    return int(row["batch_requests_window"])


def _fail(row: dict[str, str]) -> int:
    return int(row["batch_failures_window"])


def batch_requests() -> int:
    return sum(_req(r) for r in impact_rows())


def batch_failures() -> int:
    return sum(_fail(r) for r in impact_rows())


def canonical_failure_rate_pct() -> float:
    """Failed Batch requests over ALL Batch requests in the window.

    context.md names this basis explicitly, which is what makes it canonical
    rather than merely one of three defensible readings.
    """
    return round(batch_failures() / batch_requests() * 100, 2)


def fleet_rate_pct(fleet: str) -> float:
    """The exaggerating denominator: restricted to the degraded fleet."""
    rows = [r for r in impact_rows() if r["worker_fleet"] == fleet]
    return round(sum(_fail(r) for r in rows) / sum(_req(r) for r in rows) * 100, 2)


def platform_rate_pct() -> float:
    """The minimising denominator: Batch failures over all platform traffic."""
    return round(batch_failures() / PLATFORM_REQUESTS_WINDOW * 100, 2)


def batch_share_of_platform_pct() -> float:
    return round(batch_requests() / PLATFORM_REQUESTS_WINDOW * 100, 2)


def affected_accounts() -> list[str]:
    return [r["customer_id"] for r in impact_rows() if _fail(r) > 0]


def unaffected_batch_accounts() -> list[str]:
    return [r["customer_id"] for r in impact_rows() if _fail(r) == 0]


def batch_api_accounts() -> int:
    return len(impact_rows())


def share_of_all_accounts_pct() -> float:
    return round(len(affected_accounts()) / TOTAL_ACCOUNTS * 100, 1)


def per_account() -> dict[str, dict[str, object]]:
    out: dict[str, dict[str, object]] = {}
    for row in impact_rows():
        if _fail(row) == 0:
            continue
        out[row["customer_id"]] = {
            "requests": _req(row),
            "failures": _fail(row),
            "rate_pct": round(_fail(row) / _req(row) * 100, 2),
            "first": row["first_failure_utc"],
            "last": row["last_failure_utc"],
        }
    return out


def window_bounds() -> tuple[str, str]:
    """Earliest and latest failure across all accounts.

    The incident start in the timeline (11:42) must agree with the earliest
    first_failure_utc, or the two sources contradict each other and a candidate
    reading either one would be right.
    """
    firsts = [r["first_failure_utc"] for r in impact_rows() if r["first_failure_utc"]]
    lasts = [r["last_failure_utc"] for r in impact_rows() if r["last_failure_utc"]]
    return min(firsts), max(lasts)
