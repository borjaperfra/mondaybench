"""Solve the cutover problem exhaustively and prove the answer is unique.

    python solve_and_verify.py

Run before any prompt is written and before any API call. It writes
`answer-key.json` only if the search finds exactly one earliest finishing time
and a witness schedule that satisfies every rule.

The problem is one logical instance. The three density levels are three
*presentations* of it, so this solver is the single source of truth for the
answer key in all three.

## The model of the problem

Seven tasks on a chain with one branch, three people with availability windows,
two tasks contending for one exclusive resource, two tasks restricted to a named
person, and three superseded facts whose later versions are the ones that apply.

The effective state after supersession, which is what is solved:

* the index rebuild belongs to Owen, not Nadia
* Nadia is available 07:00-10:00, not 07:00-12:00
* the permissions sync runs after the schema upgrade, not before

## Why a 15-minute grid is exhaustive here

Every duration (60, 90, 120, 45, 30, 75, 60) and every window boundary (07:00,
09:00, 10:00, 11:00, 12:00, 21:00) is a whole multiple of 15 minutes. If any
feasible schedule exists, one exists with every start on the grid, so scanning
the grid upward and stopping at the first feasible completion proves minimality
rather than merely finding a good schedule.
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
GRID = 15
EARLIEST_START = 7 * 60
DEADLINE = 19 * 60

# Effective windows: the later version of each superseded fact.
WINDOWS = {
    "Nadia": (7 * 60, 10 * 60),     # superseded from 07:00-12:00
    "Priya": (9 * 60, 12 * 60),
    "Owen": (11 * 60, 21 * 60),
}
EVERYONE = ("Nadia", "Priya", "Owen")

TASKS = {
    "export snapshot":    {"duration": 60,  "owners": EVERYONE,  "cluster": False},
    "schema upgrade":     {"duration": 90,  "owners": ("Priya",), "cluster": False},
    "permissions sync":   {"duration": 45,  "owners": EVERYONE,  "cluster": True},
    "index rebuild":      {"duration": 120, "owners": ("Owen",),  "cluster": True},
    "smoke checks":       {"duration": 30,  "owners": EVERYONE,  "cluster": False},
    "consumer replay":    {"duration": 75,  "owners": EVERYONE,  "cluster": False},
    "final verification": {"duration": 60,  "owners": EVERYONE,  "cluster": False},
}

DEPS = {
    "schema upgrade": ["export snapshot"],
    "permissions sync": ["schema upgrade"],       # superseded from "before"
    "index rebuild": ["schema upgrade"],
    "smoke checks": ["index rebuild", "permissions sync"],
    "consumer replay": ["smoke checks"],
    "final verification": ["consumer replay"],
}

# A placement order that respects DEPS.
ORDER = ["export snapshot", "schema upgrade", "permissions sync", "index rebuild",
         "smoke checks", "consumer replay", "final verification"]

TARGET = "final verification"


def hhmm(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def overlaps(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
    return a_start < b_end and b_start < a_end


def _tail_length() -> dict[str, int]:
    """Longest chain of work from each task to the target, inclusive.

    Used as an admissible bound: a task that finishes later than
    `limit - (tail - own duration)` cannot lead to the target finishing by
    `limit`, so that branch is dead. This is what makes the exhaustive search
    terminate quickly instead of walking 60**7 placements.
    """
    successors: dict[str, list[str]] = {task: [] for task in TASKS}
    for task, needs in DEPS.items():
        for need in needs:
            successors[need].append(task)
    memo: dict[str, int] = {}

    def tail(task: str) -> int:
        if task in memo:
            return memo[task]
        best = TASKS[task]["duration"]
        for nxt in successors[task]:
            best = max(best, TASKS[task]["duration"] + tail(nxt))
        memo[task] = best
        return best

    return {task: tail(task) for task in TASKS}


TAIL = _tail_length()


def find_schedule(limit: int) -> dict | None:
    """A schedule finishing the target by `limit`, or None.

    Exhaustive over left-shifted schedules on the 15-minute grid. Only start
    times that are "interesting" are tried - the grid restricted to points at
    or after the task's ready time - and every branch whose remaining chain
    cannot fit inside `limit` is cut.
    """
    starts = list(range(EARLIEST_START, 22 * 60 + 1, GRID))

    def place(index: int, placed: dict) -> dict | None:
        if index == len(ORDER):
            return dict(placed)
        task = ORDER[index]
        spec = TASKS[task]
        duration = spec["duration"]
        ready = max((placed[d][2] for d in DEPS.get(task, [])), default=EARLIEST_START)
        # The latest this task may finish and still leave room for its chain.
        latest_finish = min(DEADLINE, limit - (TAIL[task] - duration))
        for owner in spec["owners"]:
            window_start, window_end = WINDOWS[owner]
            lower = max(ready, window_start, EARLIEST_START)
            for start in starts:
                if start < lower:
                    continue
                end = start + duration
                if end > window_end or end > latest_finish:
                    break          # starts only increase; nothing later can fit
                clash = False
                for other, (other_owner, other_start, other_end) in placed.items():
                    if other_owner == owner and overlaps(start, end, other_start, other_end):
                        clash = True
                        break
                    if (spec["cluster"] and TASKS[other]["cluster"]
                            and overlaps(start, end, other_start, other_end)):
                        clash = True
                        break
                if clash:
                    continue
                placed[task] = (owner, start, end)
                found = place(index + 1, placed)
                if found is not None:
                    return found
                del placed[task]
        return None

    return place(0, {})


def main() -> int:
    earliest = None
    witness = None
    for limit in range(EARLIEST_START, 22 * 60 + 1, GRID):
        found = find_schedule(limit)
        if found is not None:
            earliest = found[TARGET][2]
            witness = found
            break
    if earliest is None:
        raise SystemExit("no feasible schedule - the problem as specified is impossible")

    nothing_earlier = find_schedule(earliest - GRID) is None
    assert nothing_earlier, f"a schedule finishes before {hhmm(earliest)}"
    assert earliest <= DEADLINE, "the answer violates the stated deadline"

    # What a model gets wrong if it drops one constraint. Recorded to make the
    # instrument's failure modes legible, not used in scoring.
    diagnostics = {}

    saved = DEPS["permissions sync"]
    DEPS["permissions sync"] = []
    alt = find_schedule(22 * 60)
    diagnostics["if_the_superseded_dependency_is_missed"] = (
        hhmm(alt[TARGET][2]) if alt else None)
    DEPS["permissions sync"] = saved

    TASKS["permissions sync"]["cluster"] = False
    alt = find_schedule(22 * 60)
    diagnostics["if_the_cluster_exclusivity_is_missed"] = (
        hhmm(alt[TARGET][2]) if alt else None)
    TASKS["permissions sync"]["cluster"] = True

    TASKS["schema upgrade"]["owners"] = EVERYONE
    alt = find_schedule(22 * 60)
    diagnostics["if_the_schema_owner_restriction_is_missed"] = (
        hhmm(alt[TARGET][2]) if alt else None)
    TASKS["schema upgrade"]["owners"] = ("Priya",)

    TASKS["index rebuild"]["owners"] = ("Nadia",)
    alt = find_schedule(22 * 60)
    diagnostics["if_the_stale_index_owner_is_used"] = (
        hhmm(alt[TARGET][2]) if alt else "no feasible schedule")
    TASKS["index rebuild"]["owners"] = ("Owen",)

    WINDOWS["Nadia"] = (7 * 60, 12 * 60)
    alt = find_schedule(22 * 60)
    diagnostics["if_the_stale_nadia_window_is_used"] = (
        hhmm(alt[TARGET][2]) if alt else None)
    WINDOWS["Nadia"] = (7 * 60, 10 * 60)

    key = {
        "problem": "single-day platform cutover, seven tasks",
        "question": "at what clock time does the final verification finish, with "
                    "every task scheduled as early as the rules allow",
        "answer_type": "time",
        "answer": hhmm(earliest),
        "uniqueness": {
            "method": "exhaustive search on a 15-minute grid, limits scanned upward",
            "earliest_feasible_finish": hhmm(earliest),
            "nothing_feasible_15_minutes_earlier": nothing_earlier,
            "within_stated_deadline": True,
        },
        "witness_schedule": {task: [owner, hhmm(start), hhmm(end)]
                             for task, (owner, start, end) in
                             sorted(witness.items(), key=lambda kv: kv[1][1])},
        "effective_state_after_supersession": {
            "index rebuild owner": "Owen (superseding Nadia)",
            "Nadia availability": "07:00-10:00 (superseding 07:00-12:00)",
            "permissions sync ordering": "after the schema upgrade (superseding before)",
        },
        "wrong_answers_reachable_by_dropping_one_constraint": diagnostics,
        "identical_across_all_three_density_levels": True,
    }
    (HERE / "answer-key.json").write_text(json.dumps(key, indent=2), encoding="utf-8")

    print(f"answer: {key['answer']}   (nothing feasible 15 min earlier: {nothing_earlier})")
    print("\nwitness schedule:")
    for task, (owner, start, end) in sorted(witness.items(), key=lambda kv: kv[1][1]):
        print(f"  {hhmm(start)}-{hhmm(end)}  {owner:<6} {task}")
    print("\nwrong answers if one constraint is dropped:")
    for label, value in diagnostics.items():
        print(f"  {label:<48} {value}")
    print("\nwrote -> answer-key.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
