"""Generate the candidate-visible datasets for monday-004 "Numbers Don't Lie".

EVALUATOR-SIDE. This script is not part of the scenario and no candidate sees
it. It exists because monday-004 is the first scenario whose difficulty lives in
arithmetic rather than in prose: seven tables have to agree with each other
exactly, and a hand-typed CSV that is out by one row makes the answer key wrong
without anything failing.

So the scenario has one source of truth - the tables below - and every
candidate-visible file is generated from it:

    python tools/build_monday_004.py            write the files
    python tools/build_monday_004.py --check    fail if any file is stale

The canonical numbers are NOT computed here. `tests/monday_004_derivations.py`
recomputes them by reading the written CSVs, and `tests/test_monday_004.py`
asserts `ground-truth.yaml` matches that. A bug in this file therefore changes
the data and the derived answer key together and is caught by the design tests
that assert the traps still exist - not by an equality between two copies of the
same arithmetic.

Design rationale for every number here is in `scenarios/monday-004/design-notes.md`.
"""

from __future__ import annotations

import argparse
import csv
import io
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT = REPO_ROOT / "scenarios" / "monday-004"

SEP = "2026-09"
OCT = "2026-10"

# --------------------------------------------------------------------------
# Customers
# --------------------------------------------------------------------------
# (customer_id, usage_account_id, segment, plan, start_date, status, churn_date,
#  renewal_date, mrr_sep, mrr_oct)
#
# mrr_sep is None for a customer that did not exist in September. Two ids
# deliberately differ between billing and usage (D9). Gringotts' October value
# is its monthly equivalent: it is invoiced annually from October (D1).
CUSTOMERS: list[tuple] = [
    # --- Enterprise segment (8) -------------------------------------------
    ("acme-corp", "acme-corp", "Enterprise", "enterprise", "2023-02-14", "active", "", "2027-02-14", 78000, 78000),
    ("stark-industries", "stark-industries", "Enterprise", "enterprise", "2023-06-02", "active", "", "2027-06-02", 95000, 95000),
    ("wayne-enterprises", "wayne_ent", "Enterprise", "enterprise", "2022-11-30", "active", "", "2026-11-30", 84000, 84000),
    ("umbrella-health", "umbrella-health", "Enterprise", "enterprise", "2024-01-15", "active", "", "2027-01-15", 66000, 66000),
    ("contoso", "contoso", "Enterprise", "enterprise", "2023-09-01", "active", "", "2027-09-01", 71000, 71000),
    ("globex", "globex", "Enterprise", "enterprise", "2024-03-11", "active", "", "2027-03-11", 58000, 58000),
    ("initech", "initech", "Enterprise", "enterprise", "2024-07-22", "active", "", "2027-07-22", 52000, 52000),
    ("cyberdyne", "cyberdyne", "Enterprise", "enterprise", "2023-04-18", "active", "", "2027-04-18", 61000, 61000),
    # --- Mid-market segment (10) ------------------------------------------
    ("gringotts", "gringotts", "Mid-market", "enterprise", "2024-10-01", "active", "", "2027-10-01", 10000, 10000),
    ("soylent", "soylent", "Mid-market", "enterprise", "2024-05-20", "active", "", "2027-05-20", 22000, 19500),
    ("hooli", "hooli", "Mid-market", "enterprise", "2024-03-11", "active", "", "2027-03-11", 18000, 21000),
    ("massive-dynamic", "massive-dynamic", "Mid-market", "enterprise", "2025-01-09", "active", "", "2027-01-09", 16500, 16500),
    ("tyrell-corp", "tyrell-corp", "Mid-market", "enterprise", "2025-02-27", "active", "", "2027-02-27", 14000, 14000),
    ("duff-brewing", "duff-brewing", "Mid-market", "enterprise", "2024-12-05", "active", "", "2026-12-05", 13500, 13500),
    ("aperture-labs", "aperture-labs", "Mid-market", "pro", "2025-04-14", "active", "", "2027-04-14", 12500, 12500),
    ("nakatomi", "nakatomi", "Mid-market", "pro", "2024-08-08", "churned", "2026-10-19", "", 15000, 15000),
    ("vandelay", "vandelay", "Mid-market", "pro", "2026-09-01", "active", "", "2027-09-01", 11000, 11000),
    ("prestige-worldwide", "prestige_ww", "Mid-market", "pro", "2025-06-30", "active", "", "2027-06-30", 9500, 9500),
    # --- SMB segment (18) --------------------------------------------------
    ("wonka-industries", "wonka-industries", "SMB", "pro", "2025-03-17", "active", "", "2027-03-17", 4200, 4200),
    ("oscorp-labs", "oscorp-labs", "SMB", "pro", "2025-08-11", "active", "", "2027-08-11", 3600, 3600),
    ("pied-piper", "pied-piper", "SMB", "pro", "2025-09-23", "active", "", "2027-09-23", 3400, 3400),
    ("planet-express", "planet-express", "SMB", "pro", "2026-09-01", "active", "", "2027-09-01", 3800, 3800),
    ("spacely-sprockets", "spacely-sprockets", "SMB", "pro", "2026-10-01", "active", "", "2027-10-01", None, 3200),
    ("bluth-company", "bluth-company", "SMB", "starter", "2025-05-06", "active", "", "2027-05-06", 2400, 2400),
    ("dunder-mifflin", "dunder-mifflin", "SMB", "starter", "2025-02-11", "active", "", "2027-02-11", 3100, 3100),
    ("sterling-cooper", "sterling-cooper", "SMB", "starter", "2025-07-19", "active", "", "2027-07-19", 2600, 2600),
    ("monsters-inc", "monsters-inc", "SMB", "starter", "2026-09-01", "active", "", "2027-09-01", 2800, 2800),
    ("clampett-oil", "clampett-oil", "SMB", "starter", "2026-09-01", "active", "", "2027-09-01", 2900, 2900),
    ("cogswell-cogs", "cogswell-cogs", "SMB", "starter", "2026-10-01", "active", "", "2027-10-01", None, 2100),
    ("bishop-co", "bishop-co", "SMB", "starter", "2026-10-01", "active", "", "2027-10-01", None, 1700),
    ("gekko-co", "gekko-co", "SMB", "starter", "2026-10-01", "active", "", "2027-10-01", None, 2200),
    ("paper-street-soap", "paper-street-soap", "SMB", "starter", "2026-10-01", "active", "", "2027-10-01", None, 1900),
    ("slate-rock", "slate-rock", "SMB", "starter", "2025-01-28", "churned", "2026-10-08", "", 2000, 2000),
    ("mega-lo-mart", "mega-lo-mart", "SMB", "starter", "2025-04-02", "churned", "2026-10-15", "", 2700, 2700),
    ("dinoco", "dinoco", "SMB", "starter", "2025-10-13", "churned", "2026-10-22", "", 2300, 2300),
    ("buy-n-large", "buy-n-large", "SMB", "starter", "2024-09-09", "churned", "2026-10-27", "", 3300, 3300),
]

# Gringotts is invoiced for twelve months in October instead of monthly (D1).
ANNUAL_CUSTOMER = "gringotts"
ANNUAL_AMOUNT = 120000
ANNUAL_MONTHS = 12

# One-off, non-recurring invoices. (month, customer_id, amount, invoice_type)
ONE_OFFS = [
    (SEP, "globex", 33000, "professional_services"),
    (SEP, "hooli", 18000, "professional_services"),
    (OCT, "aperture-labs", 5700, "professional_services"),
]

# The duplicate (D8): Soylent's October subscription lands twice, from the two
# systems that feed the billing table. Same transaction id, different source and
# a day apart, and the copy is written at the end of the October block rather
# than beside its twin.
DUPLICATE_CUSTOMER = "soylent"

# --------------------------------------------------------------------------
# Usage - requests per customer per month
# --------------------------------------------------------------------------
# Acme's October is the batch migration (D3): requests nearly halve, tokens
# barely move. Soylent's is the unexplained contraction (D11).
REQUESTS: dict[str, tuple[int | None, int]] = {
    "acme-corp": (4200000, 2310000),
    "stark-industries": (3900000, 4290000),
    "wayne_ent": (3100000, 3410000),
    "umbrella-health": (2400000, 2592000),
    "contoso": (2800000, 2940000),
    "globex": (1900000, 2090000),
    "initech": (1600000, 1712000),
    "cyberdyne": (2100000, 2247000),
    "soylent": (980000, 715400),
    "hooli": (810000, 990000),
    "massive-dynamic": (720000, 845000),
    "tyrell-corp": (690000, 780000),
    "duff-brewing": (700000, 815000),
    "gringotts": (640000, 700000),
    "aperture-labs": (580000, 705000),
    "nakatomi": (560000, 470000),
    "vandelay": (520000, 690000),
    "prestige_ww": (480000, 545000),
    "wonka-industries": (900000, 1020000),
    "oscorp-labs": (180000, 198000),
    "pied-piper": (170000, 186000),
    "planet-express": (75000, 112000),
    "spacely-sprockets": (None, 51000),
    "bluth-company": (120000, 132000),
    "dunder-mifflin": (155000, 168000),
    "sterling-cooper": (130000, 141000),
    "monsters-inc": (55000, 84000),
    "clampett-oil": (60000, 88000),
    "cogswell-cogs": (None, 42000),
    "bishop-co": (None, 38000),
    "gekko-co": (None, 33000),
    "paper-street-soap": (None, 46000),
    "slate-rock": (95000, 62000),
    "mega-lo-mart": (140000, 88000),
    "dinoco": (110000, 71000),
    "buy-n-large": (165000, 104000),
}

# Tokens per request, by plan. Enterprise workloads carry longer contexts, which
# is also why enterprise infrastructure costs more per request than Pro's.
TOKENS_PER_REQUEST = {"enterprise": 1100, "pro": 700, "starter": 500}
# Acme's batch runs are far larger calls: half the requests, nearly the same
# tokens. This is the number that says the workload did not leave.
TOKENS_OVERRIDE = {("acme-corp", OCT): 4066.0}
# Seats do not follow request volume through a batching migration.
USERS_OVERRIDE = {("acme-corp", OCT): 232}
USERS_PER_REQUEST = {"enterprise": 17500, "pro": 12000, "starter": 9000}

# --------------------------------------------------------------------------
# Plans
# --------------------------------------------------------------------------
# Revenue and customer counts are derived from CUSTOMERS. Costs and the included
# volume are stated here; there is deliberately no margin and no contribution
# column (D6).
PLAN_COSTS = {
    (SEP, "enterprise"): (288000, 159000),
    (SEP, "pro"): (13600, 6900),
    (SEP, "starter"): (8400, 7300),
    (OCT, "enterprise"): (296800, 168000),
    (OCT, "pro"): (16100, 8600),
    (OCT, "starter"): (11400, 10300),
}
INCLUDED_REQUESTS = {"enterprise": 3000000, "pro": 600000, "starter": 200000}
PLAN_ORDER = ["enterprise", "pro", "starter"]

# --------------------------------------------------------------------------
# Acquisition
# --------------------------------------------------------------------------
# (month, lead_id, customer_id, channel, campaign_start, conversion_date,
#  new_logo, expansion, attributed_revenue_eur)
#
# first_customer_date is looked up from CUSTOMERS, so an expansion row cannot
# accidentally claim to predate its own account.
ACQUISITION: list[tuple] = [
    (SEP, "L-2026-0912", "vandelay", "partner", "2026-08-03", "2026-09-01", True, False, 132000),
    (SEP, "L-2026-0918", "clampett-oil", "partner", "2026-08-03", "2026-09-01", True, False, 34800),
    (SEP, "L-2026-0931", "planet-express", "content", "2026-07-20", "2026-09-01", True, False, 45600),
    (SEP, "L-2026-0944", "monsters-inc", "outbound", "2026-08-17", "2026-09-01", True, False, 33600),
    (SEP, "L-2026-0957", "hooli", "paid_search", "2026-09-07", "2026-09-24", False, True, 36000),
    (OCT, "L-2026-1006", "cogswell-cogs", "content", "2026-09-14", "2026-10-01", True, False, 25200),
    (OCT, "L-2026-1013", "bishop-co", "content", "2026-09-14", "2026-10-01", True, False, 20400),
    (OCT, "L-2026-1021", "spacely-sprockets", "paid_search", "2026-09-28", "2026-10-01", True, False, 38400),
    (OCT, "L-2026-1034", "gekko-co", "paid_search", "2026-09-28", "2026-10-01", True, False, 26400),
    (OCT, "L-2026-1042", "paper-street-soap", "outbound", "2026-09-21", "2026-10-01", True, False, 22800),
    (OCT, "L-2026-1055", "stark-industries", "paid_search", "2026-09-28", "2026-10-13", False, True, 84000),
    (OCT, "L-2026-1063", "umbrella-health", "paid_search", "2026-09-28", "2026-10-20", False, True, 48000),
    (OCT, "L-2026-1071", "globex", "paid_search", "2026-09-28", "2026-10-26", False, True, 42000),
    (OCT, "L-2026-1084", "massive-dynamic", "content", "2026-09-14", "2026-10-09", False, True, 18000),
    (OCT, "L-2026-1092", "cyberdyne", "outbound", "2026-09-21", "2026-10-15", False, True, 24000),
]

# --------------------------------------------------------------------------
# Funnel  (month, channel, leads, conversions)
# --------------------------------------------------------------------------
FUNNEL = [
    (SEP, "paid_search", 520, 44),
    (SEP, "content", 260, 31),
    (SEP, "partner", 60, 15),
    (SEP, "outbound", 160, 10),
    (OCT, "paid_search", 900, 58),
    (OCT, "content", 330, 34),
    (OCT, "partner", 75, 17),
    (OCT, "outbound", 195, 11),
]

# --------------------------------------------------------------------------
# Support
# --------------------------------------------------------------------------
# One character per ticket, so the counts that drive D7, D10 and D11 are visible
# here rather than buried in 133 literal rows.
#   R rate_limits   A api_errors   B billing   I integration
#   H how_to        P performance
CATEGORY = {
    "R": ("rate_limits", "medium"),
    "A": ("api_errors", "high"),
    "B": ("billing", "low"),
    "I": ("integration", "medium"),
    "H": ("how_to", "low"),
    "P": ("performance", "high"),
    "C": ("api_errors", "critical"),
}
TICKETS: dict[tuple[str, str], str] = {
    # September - enterprise plan (33)
    (SEP, "acme-corp"): "APIH",
    (SEP, "stark-industries"): "APIHB",
    (SEP, "wayne_ent"): "AIHP",
    (SEP, "umbrella-health"): "AIH",
    (SEP, "contoso"): "APH",
    (SEP, "globex"): "IH",
    (SEP, "initech"): "AH",
    (SEP, "cyberdyne"): "AIP",
    (SEP, "soylent"): "AIH",
    (SEP, "hooli"): "I",
    (SEP, "massive-dynamic"): "H",
    (SEP, "tyrell-corp"): "B",
    (SEP, "duff-brewing"): "H",
    # September - pro plan (19)
    (SEP, "aperture-labs"): "RIH",
    (SEP, "nakatomi"): "APH",
    (SEP, "vandelay"): "IH",
    (SEP, "prestige_ww"): "RH",
    (SEP, "wonka-industries"): "RRIH",
    (SEP, "oscorp-labs"): "RH",
    (SEP, "pied-piper"): "IH",
    (SEP, "planet-express"): "H",
    # September - starter plan (7)
    (SEP, "bluth-company"): "H",
    (SEP, "dunder-mifflin"): "B",
    (SEP, "sterling-cooper"): "H",
    (SEP, "monsters-inc"): "I",
    (SEP, "slate-rock"): "A",
    (SEP, "mega-lo-mart"): "H",
    (SEP, "buy-n-large"): "B",
    # October - enterprise plan (35)
    (OCT, "acme-corp"): "IHB",
    (OCT, "stark-industries"): "APIHB",
    (OCT, "wayne_ent"): "AIHP",
    (OCT, "umbrella-health"): "AIH",
    (OCT, "contoso"): "APH",
    (OCT, "globex"): "IH",
    (OCT, "initech"): "AH",
    (OCT, "cyberdyne"): "AIP",
    (OCT, "soylent"): "ACAPIHPB",
    (OCT, "hooli"): "I",
    (OCT, "tyrell-corp"): "B",
    # October - pro plan (28)
    (OCT, "aperture-labs"): "RRIH",
    (OCT, "nakatomi"): "AB",
    (OCT, "vandelay"): "RIHP",
    (OCT, "prestige_ww"): "RRH",
    (OCT, "wonka-industries"): "RRRRIHP",
    (OCT, "oscorp-labs"): "RRH",
    (OCT, "pied-piper"): "RIH",
    (OCT, "planet-express"): "R",
    (OCT, "spacely-sprockets"): "H",
    # October - starter plan (11)
    (OCT, "bluth-company"): "H",
    (OCT, "dunder-mifflin"): "B",
    (OCT, "sterling-cooper"): "H",
    (OCT, "monsters-inc"): "I",
    (OCT, "clampett-oil"): "H",
    (OCT, "slate-rock"): "A",
    (OCT, "mega-lo-mart"): "B",
    (OCT, "dinoco"): "A",
    (OCT, "buy-n-large"): "B",
    (OCT, "cogswell-cogs"): "H",
    (OCT, "gekko-co"): "I",
}

STATUSES = ["resolved", "resolved", "resolved", "open", "resolved", "pending"]


# --------------------------------------------------------------------------
# Derived helpers
# --------------------------------------------------------------------------

def customer_rows() -> list[dict]:
    rows = []
    for (cid, uid, segment, plan, start, status, churn, renewal, mrr_sep, mrr_oct) in CUSTOMERS:
        rows.append(
            {
                "customer_id": cid,
                "usage_account_id": uid,
                "segment": segment,
                "plan": plan,
                "start_date": start,
                "status": status,
                "churn_date": churn,
                "arr_eur": mrr_oct * 12,
                "renewal_date": renewal,
                "_mrr": {SEP: mrr_sep, OCT: mrr_oct},
            }
        )
    return rows


def _write(path: Path, header: list[str], rows: list[list], check: bool) -> bool:
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    body = buf.getvalue()
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if existing == body:
        print(f"  {path.name} up to date")
        return False
    if check:
        print(f"  {path.name} is STALE")
        return True
    path.write_text(body, encoding="utf-8", newline="")
    print(f"  wrote {path.name} ({len(rows)} rows)")
    return False


def build(check: bool) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    customers = customer_rows()
    by_id = {c["customer_id"]: c for c in customers}
    stale = 0

    # ---- customers.csv ----------------------------------------------------
    stale += _write(
        OUT / "customers.csv",
        ["customer_id", "usage_account_id", "segment", "plan", "start_date", "status", "churn_date", "arr_eur", "renewal_date"],
        [
            [c["customer_id"], c["usage_account_id"], c["segment"], c["plan"], c["start_date"], c["status"], c["churn_date"], c["arr_eur"], c["renewal_date"]]
            for c in customers
        ],
        check,
    )

    # ---- revenue.csv ------------------------------------------------------
    rev: list[list] = []
    seq = {SEP: 0, OCT: 200}

    def txn(month: str) -> str:
        seq[month] += 1
        return f"INV-{month}-{seq[month]:04d}"

    for month, date in ((SEP, "2026-09-01"), (OCT, "2026-10-01")):
        for c in customers:
            mrr = c["_mrr"][month]
            if mrr is None:
                continue
            if month == OCT and c["customer_id"] == ANNUAL_CUSTOMER:
                continue
            rev.append([txn(month), c["customer_id"], date, "subscription", 1, mrr, "stripe"])
        if month == OCT:
            rev.append([txn(month), ANNUAL_CUSTOMER, "2026-10-01", "annual_subscription", ANNUAL_MONTHS, ANNUAL_AMOUNT, "stripe"])
        for om, ocid, amount, itype in ONE_OFFS:
            if om != month:
                continue
            rev.append([txn(month), ocid, f"{month}-0{2 if month == SEP else 3}", itype, 0, amount, "stripe"])

    # The duplicate: same transaction id, one day later, from the other system.
    twin = next(r for r in rev if r[1] == DUPLICATE_CUSTOMER and r[2] == "2026-10-01" and r[3] == "subscription")
    rev.append([twin[0], twin[1], "2026-10-02", twin[3], twin[4], twin[5], "billing_sync"])

    stale += _write(
        OUT / "revenue.csv",
        ["transaction_id", "customer_id", "date", "invoice_type", "billing_period_months", "amount_eur", "source"],
        rev,
        check,
    )

    # ---- usage.csv --------------------------------------------------------
    usage: list[list] = []
    for month, index in ((SEP, 0), (OCT, 1)):
        for c in customers:
            uid = c["usage_account_id"]
            requests = REQUESTS[uid][index]
            if requests is None:
                continue
            tpr = TOKENS_PER_REQUEST[c["plan"]]
            tokens = TOKENS_OVERRIDE.get((c["customer_id"], month), round(requests * tpr / 1_000_000, 1))
            users = USERS_OVERRIDE.get(
                (c["customer_id"], month), round(requests / USERS_PER_REQUEST[c["plan"]])
            )
            previous = REQUESTS[uid][0]
            if month == OCT and previous:
                change = f"{(requests - previous) / previous * 100:.1f}"
            else:
                change = ""
            usage.append([month, uid, requests, tokens, users, change])
    stale += _write(
        OUT / "usage.csv",
        ["month", "usage_account_id", "requests", "tokens_m", "active_users", "usage_change_pct"],
        usage,
        check,
    )

    # ---- plans.csv --------------------------------------------------------
    plans: list[list] = []
    for month in (SEP, OCT):
        for plan in PLAN_ORDER:
            members = [c for c in customers if c["plan"] == plan and c["_mrr"][month] is not None]
            revenue = sum(c["_mrr"][month] for c in members)
            infra, support = PLAN_COSTS[(month, plan)]
            requests = sum(
                REQUESTS[c["usage_account_id"]][0 if month == SEP else 1] or 0 for c in members
            )
            plans.append(
                [
                    month, plan, len(members), revenue, infra, support,
                    INCLUDED_REQUESTS[plan], round(requests / len(members)),
                ]
            )
    stale += _write(
        OUT / "plans.csv",
        ["month", "plan", "customers", "revenue_eur", "infra_cost_eur", "support_cost_eur", "included_requests_per_customer", "avg_requests_per_customer"],
        plans,
        check,
    )

    # ---- acquisition.csv --------------------------------------------------
    acq = [
        [
            month, lead, cid, channel, campaign, by_id[cid]["start_date"], converted,
            "true" if new_logo else "false", "true" if expansion else "false", amount,
        ]
        for (month, lead, cid, channel, campaign, converted, new_logo, expansion, amount) in ACQUISITION
    ]
    stale += _write(
        OUT / "acquisition.csv",
        ["month", "lead_id", "customer_id", "channel", "campaign_start", "first_customer_date", "conversion_date", "new_logo", "expansion", "attributed_revenue_eur"],
        acq,
        check,
    )

    # ---- funnel.csv -------------------------------------------------------
    stale += _write(
        OUT / "funnel.csv",
        ["month", "channel", "leads", "conversions"],
        [list(row) for row in FUNNEL],
        check,
    )

    # ---- support.csv ------------------------------------------------------
    tickets: list[list] = []
    n = 0
    for month in (SEP, OCT):
        for c in customers:
            codes = TICKETS.get((month, c["usage_account_id"]), "")
            for i, code in enumerate(codes):
                category, severity = CATEGORY[code]
                n += 1
                tickets.append(
                    [
                        month, f"TCK-{month[-2:]}-{n:04d}", c["customer_id"], severity,
                        category, STATUSES[n % len(STATUSES)],
                    ]
                )
    stale += _write(
        OUT / "support.csv",
        ["month", "ticket_id", "customer_id", "severity", "category", "status"],
        tickets,
        check,
    )

    return stale


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="write nothing; exit 1 if stale")
    args = parser.parse_args()
    raise SystemExit(1 if build(args.check) else 0)
