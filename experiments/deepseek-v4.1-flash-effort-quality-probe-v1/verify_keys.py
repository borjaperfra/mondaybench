"""Prove each answer key before a single API call is made.

    python verify_keys.py

A wrong answer key would not produce a noisy experiment - it would produce a
confident, precisely-quantified wrong conclusion. So every key is established
here mechanically, and this script writes `microtests/answer-keys.json` only if
every check passes.

* **mt-01 and mt-05** are combinatorial, so they are solved by exhaustive
  search, and the search also proves the answer is *unique* (no other schedule
  finishes earlier; no other approved set ties on the objective).
* **mt-03** is a rule check: each proposed plan is tested against each written
  rule, and the key follows from which rules it breaks.
* **mt-02** encodes the log's supersessions and the eligibility rules, then
  evaluates each of the four options against them.
* **mt-04** checks the arithmetic that option B asserts, and records why each
  other option is unsupported. That last part is a design assertion about
  causal claims, not something arithmetic can settle, and it is labelled as
  such in the output rather than presented as a proof.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MICROTESTS = HERE / "microtests"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# --------------------------------------------------------------------------
# mt-01: exhaustive schedule search
# --------------------------------------------------------------------------

JOBS = {"P1": 90, "P2": 60, "P3": 120, "P4": 30, "P5": 45}
DEPS = {"P3": ["P1"], "P4": ["P2"], "P5": ["P3", "P4"]}
BENCH = {"P1", "P2"}                     # single-occupancy, may not overlap
ONLY_BO = {"P3"}
WINDOWS = {"Ada": (8 * 60, 13 * 60), "Bo": (10 * 60, 18 * 60)}
GRID = 15  # minutes


def _overlap(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
    return a_start < b_end and b_start < a_end


def schedule_feasible(limit: int) -> dict | None:
    """A schedule with every job finished by `limit`, or None if none exists.

    Exhaustive on a 15-minute grid. The grid loses nothing here: every duration
    (90, 60, 120, 30, 45) and every window boundary (08:00, 10:00, 13:00,
    18:00) is a whole multiple of 15 minutes, so if a feasible schedule exists
    at all, one exists with every start on the grid.
    """
    order = ["P1", "P2", "P3", "P4", "P5"]  # a topological order of DEPS
    starts = list(range(8 * 60, 18 * 60 + 1, GRID))

    def place(index: int, placed: dict) -> dict | None:
        if index == len(order):
            return dict(placed)
        job = order[index]
        duration = JOBS[job]
        techs = ["Bo"] if job in ONLY_BO else ["Ada", "Bo"]
        ready = max((placed[d][2] for d in DEPS.get(job, [])), default=8 * 60)
        for tech in techs:
            window_start, window_end = WINDOWS[tech]
            for start in starts:
                end = start + duration
                if start < max(ready, window_start) or end > window_end or end > limit:
                    continue
                clash = False
                for other, (other_tech, other_start, other_end) in placed.items():
                    if other_tech == tech and _overlap(start, end, other_start, other_end):
                        clash = True
                        break
                    if (job in BENCH and other in BENCH
                            and _overlap(start, end, other_start, other_end)):
                        clash = True
                        break
                if clash:
                    continue
                placed[job] = (tech, start, end)
                found = place(index + 1, placed)
                if found is not None:
                    return found
                del placed[job]
        return None

    return place(0, {})


def hhmm(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def verify_mt01() -> dict:
    """Find the earliest feasible makespan by scanning limits upward."""
    earliest = None
    witness = None
    for limit in range(8 * 60, 18 * 60 + 1, GRID):
        found = schedule_feasible(limit)
        if found is not None:
            earliest = max(end for _, _, end in found.values())
            witness = found
            break
    assert earliest is not None, "mt-01: no feasible schedule at all"
    # Uniqueness of the *answer*: nothing finishes earlier. Scanning upward and
    # stopping at the first feasible limit is exactly that proof.
    infeasible_below = schedule_feasible(earliest - GRID) is None
    assert infeasible_below, f"mt-01: something finishes before {hhmm(earliest)}"
    return {
        "answer": hhmm(earliest),
        "method": "exhaustive search on a 15-minute grid, limits scanned upward",
        "earliest_feasible_makespan": hhmm(earliest),
        "nothing_feasible_15min_earlier": infeasible_below,
        "witness_schedule": {job: [tech, hhmm(start), hhmm(end)]
                             for job, (tech, start, end) in sorted(witness.items())},
    }


# --------------------------------------------------------------------------
# mt-05: exhaustive allocation search
# --------------------------------------------------------------------------

REQUESTS = {
    "R1": {"space": 4, "team": "Blue", "requires": "R4"},
    "R2": {"space": 3, "team": "Green", "requires": None},
    "R3": {"space": 5, "team": "Blue", "requires": None},
    "R4": {"space": 2, "team": "Red", "requires": None},
    "R5": {"space": 3, "team": "Green", "requires": "R2"},
}
CAPACITY = 9
MAX_PER_TEAM = 2
EXCLUSIVE = ("R2", "R3")  # R3 cannot be approved if R2 is


def allocation_valid(chosen: frozenset) -> bool:
    if sum(REQUESTS[r]["space"] for r in chosen) > CAPACITY:
        return False
    for team in {REQUESTS[r]["team"] for r in chosen}:
        if sum(1 for r in chosen if REQUESTS[r]["team"] == team) > MAX_PER_TEAM:
            return False
    for r in chosen:
        needs = REQUESTS[r]["requires"]
        if needs is not None and needs not in chosen:
            return False
    if EXCLUSIVE[0] in chosen and EXCLUSIVE[1] in chosen:
        return False
    return True


def verify_mt05() -> dict:
    ids = list(REQUESTS)
    valid = []
    for size in range(len(ids) + 1):
        for combo in itertools.combinations(ids, size):
            chosen = frozenset(combo)
            if allocation_valid(chosen):
                valid.append((sum(REQUESTS[r]["space"] for r in chosen), len(chosen), chosen))
    assert valid, "mt-05: no valid allocation"
    best_space = max(space for space, _, _ in valid)
    tied_on_space = [v for v in valid if v[0] == best_space]
    best_count = max(count for _, count, _ in tied_on_space)
    winners = [v[2] for v in tied_on_space if v[1] == best_count]
    assert len(winners) == 1, f"mt-05: objective does not pick a unique set: {winners}"
    answer = sorted(winners[0])
    return {
        "answer": answer,
        "method": "exhaustive over all 32 subsets, objective applied as written",
        "valid_sets": len(valid),
        "best_space": best_space,
        "sets_tied_on_space": [sorted(v[2]) for v in tied_on_space],
        "unique_winner": True,
        "runner_up_sets": sorted(
            ([sorted(c), s] for s, _, c in valid if s != best_space),
            key=lambda item: -item[1])[:4],
    }


# --------------------------------------------------------------------------
# mt-03: rule check on two named plans
# --------------------------------------------------------------------------

def verify_mt03() -> dict:
    window = (20 * 60, 30 * 60)          # 20:00 to 06:00 next day
    nightly_job = 25 * 60                # 01:00 next day
    plans = {
        "Plan 1": {"snapshot": (19 * 60 + 45, 20 * 60 + 30),
                   "rebuild": (20 * 60 + 30, 25 * 60 + 30)},
        "Plan 2": {"snapshot": (20 * 60, 20 * 60 + 45),
                   "rebuild": (20 * 60 + 45, 25 * 60 + 45)},
    }
    findings = {}
    for name, plan in plans.items():
        broken = []
        for phase in ("snapshot", "rebuild"):
            start, end = plan[phase]
            if start < window[0] or end > window[1]:
                broken.append(f"{phase} {hhmm(start % 1440)}-{hhmm(end % 1440)} "
                              f"is not entirely inside the maintenance window")
        rebuild_start, rebuild_end = plan["rebuild"]
        if rebuild_start <= nightly_job < rebuild_end:
            broken.append("nightly job N at 01:00 writes to S during the rebuild")
        if rebuild_end - rebuild_start != 300:
            broken.append("rebuild is not 5 hours")
        if plan["snapshot"][1] != rebuild_start:
            broken.append("snapshot does not immediately precede the rebuild")
        if plan["snapshot"][1] - plan["snapshot"][0] != 45:
            broken.append("snapshot is not 45 minutes")
        findings[name] = broken
    executable = [name for name, broken in findings.items() if not broken]
    answer = {0: "D", 1: "A" if "Plan 1" in executable else "B", 2: "C"}[len(executable)]
    return {
        "answer": answer,
        "method": "each plan checked against each written rule",
        "rule_violations": findings,
        "executable_plans": executable,
    }


# --------------------------------------------------------------------------
# mt-02: supersession and eligibility
# --------------------------------------------------------------------------

def verify_mt02() -> dict:
    now = 12 * 60 + 30
    freeze = (13 * 60, 17 * 60)          # 10:15 supersedes the 09:05 window
    freeze_covers_cache = True           # 12:20
    soak_minutes = 60                    # 10:50, must finish before a freeze begins
    assignee = "Ravi"                    # 11:00 supersedes the 09:40 assignment
    dana_available = False               # 11:00, out from 12:00
    blocker_cleared = True               # 12:10 clears the 11:30 block
    ops_members: set[str] = set()        # neither Ravi nor Dana is in Ops

    def may_change_at(actor: str, when: int) -> tuple[bool, str]:
        if freeze[0] <= when < freeze[1] and freeze_covers_cache:
            if actor not in ops_members:
                return False, f"{when // 60:02d}:{when % 60:02d} is inside the freeze " \
                              f"and {actor} is not in Ops"
        if actor == "Dana" and not dana_available:
            return False, "Dana is out from 12:00 and K-12 was reassigned"
        if actor != assignee:
            return False, f"K-12 is assigned to {assignee}"
        if not blocker_cleared:
            return False, "the audit export had not landed"
        return True, "permitted"

    options = {}
    ok_a, why_a = may_change_at("Ravi", 15 * 60)
    options["A"] = {"supported": ok_a, "why": why_a}
    ok_b, why_b = may_change_at("Dana", 15 * 60)
    options["B"] = {"supported": ok_b, "why": why_b}
    # C: start now. The soak must finish before the freeze begins.
    soak_end = now + soak_minutes
    ok_c, why_c = may_change_at("Ravi", now)
    if ok_c and soak_end > freeze[0]:
        ok_c, why_c = False, (f"a {soak_minutes}-minute soak started at "
                              f"{hhmm(now)} ends at {hhmm(soak_end)}, after the "
                              f"freeze begins at {hhmm(freeze[0])}")
    options["C"] = {"supported": ok_c, "why": why_c}
    options["D"] = {"supported": not (ok_a or ok_b or ok_c),
                    "why": "holds exactly when A, B and C are all unsupported"}

    supported = [key for key, value in options.items() if value["supported"]]
    assert len(supported) == 1, f"mt-02: {len(supported)} options are supported: {supported}"
    return {
        "answer": supported[0],
        "method": "supersessions applied in log order, then each option evaluated",
        "effective_state": {
            "freeze_window": f"{hhmm(freeze[0])}-{hhmm(freeze[1])} (10:15 supersedes 09:05)",
            "freeze_covers_cache_layer": freeze_covers_cache,
            "assignee": f"{assignee} (11:00 supersedes 09:40)",
            "blocker_cleared": f"{blocker_cleared} (12:10 clears 11:30)",
            "soak_rule_minutes": soak_minutes,
        },
        "options": options,
    }


# --------------------------------------------------------------------------
# mt-04: arithmetic, plus a labelled design assertion
# --------------------------------------------------------------------------

def verify_mt04() -> dict:
    week1 = 96 / 1200
    week2 = 72 / 800
    assert round(week1 * 100, 4) == 8.0, week1
    assert round(week2 * 100, 4) == 9.0, week2
    signup_drop = 96 - 72
    assert signup_drop == 24
    return {
        "answer": "B",
        "method": "arithmetic checked; the discrimination between options is a "
                  "design assertion about causal claims, not an arithmetic result",
        "arithmetic": {
            "week1_rate_pct": round(week1 * 100, 1),
            "week2_rate_pct": round(week2 * 100, 1),
            "signup_difference": signup_drop,
        },
        "why_each_option": {
            "A": "asserts the video caused the change; two confounded changes "
                 "occurred at once, so attribution is not available",
            "B": "states the rate change, which the arithmetic gives, and "
                 "declines the attribution the data cannot support",
            "C": "the 24-signup drop is real, but 'reduced' is a causal claim "
                 "about the campaign ending, which is equally confounded",
            "D": "a forecast; nothing in two weeks of totals establishes it",
        },
        "design_assertion": True,
    }


VERIFIERS = {
    "mt-01-schedule": (verify_mt01, "time"),
    "mt-02-supersession": (verify_mt02, "choice"),
    "mt-03-plan-trap": (verify_mt03, "choice"),
    "mt-04-supported-claim": (verify_mt04, "choice"),
    "mt-05-allocation": (verify_mt05, "idset"),
}


def main() -> int:
    keys = {}
    for test_id, (verifier, answer_type) in VERIFIERS.items():
        path = MICROTESTS / f"{test_id}.txt"
        data = path.read_bytes()
        result = verifier()
        keys[test_id] = {
            "prompt_file": f"microtests/{test_id}.txt",
            "prompt_sha256": sha256_bytes(data),
            "prompt_bytes": len(data),
            "answer_type": answer_type,
            "answer": result.pop("answer"),
            "verification": result,
        }
        print(f"{test_id:<24} {answer_type:<7} answer={keys[test_id]['answer']!s:<18} "
              f"sha={keys[test_id]['prompt_sha256'][:12]}  bytes={len(data)}")

    out = MICROTESTS / "answer-keys.json"
    out.write_text(json.dumps(keys, indent=2), encoding="utf-8")
    print(f"\nall {len(keys)} keys verified -> {out.relative_to(HERE).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
