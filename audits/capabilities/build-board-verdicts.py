"""Write the harness verdict files for the three models published in suite v1.10.

    uv run python audits/capabilities/build-board-verdicts.py           # write
    uv run python audits/capabilities/build-board-verdicts.py --check   # compare

The labels are NOT re-derived here. This script runs
`build-provisional-capabilities.py` - the adapter that already assembles each
model's label set and refuses to finish unless every run reproduces its
published score - and reads the label sets it built:

  claude-opus-5          the independent blind re-judge by GPT-5.6 Sol
                         (audits/blind-rejudge/inter-judge/source/), joined to
                         runs through opus-5-blind-rejudge-mapping.json
  claude-fable-5-1       the original recorded Opus 5 judge, POST-AUDIT: the
                         adapter's FABLE_CORRECTIONS (AUDIT.md section 5) applied
  gemini-3-8-flash-high  the blind re-judge by Claude Opus 5.5
                         (experiments/gemini-3.8-flash-high-opus-judge/)

Running the adapter rewrites its own four artefacts under audits/capabilities/;
they come out byte-identical, which `git status` confirms.

What this script adds is the harness shape: `verdicts/<scenario>/<slug>.verdicts.jsonl`
keyed by the harness run ids, one criterion row per rubric criterion, a noise
row where the rubric scores noise, and a penalties row per run. Evidence and
reasons are carried from the same source rows the labels came from; the label
in each row is the adapter's, and the script stops if a source row disagrees
with it anywhere other than an audited Fable correction.

PENALTY CANDIDATES THAT DO NOT DEDUCT. Two of the source judges recorded penalty
candidates with `materially_misleading: false`. The canonical scorer
(`scoring.build_breakdown`) charges nothing for those, but the recorded-verdict
route does not read the flag - every listed violation deducts. So they are
written under `dismissed`, which the route ignores, exactly as the Fable
date-sensitivity verdicts already record their dismissed candidates. Nothing is
dropped and nothing changes what the canonical scorer computes.

`--check` reads the evaluations `mondaybench evaluate --suite-version 1.10`
wrote and compares every run's final score with the adapter's, and every
model's Monday Score with its published figure.
"""

from __future__ import annotations

import contextlib
import io
import json
import runpy
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

SCEN = ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"]
SUITE = "1.10"
PUBLISHED = {"claude-opus-5": 97.07, "claude-fable-5-1": 94.90, "gemini-3-8-flash-high": 86.00}
JUDGE_LINE = {
    "claude-opus-5": "GPT-5.6 Sol, independent blind re-judge (audits/blind-rejudge/inter-judge/source/)",
    "claude-fable-5-1": "the original recorded Claude Opus 5 judge, post-audit "
                        "(experiments/fable-5.1-full-mondaybench/AUDIT.md section 5)",
    "gemini-3-8-flash-high": "Claude Opus 5.5, blind re-judge "
                             "(experiments/gemini-3.8-flash-high-opus-judge/)",
}


def run_adapter() -> dict:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        try:
            return runpy.run_path(str(HERE / "build-provisional-capabilities.py"),
                                  run_name="adapter")
        except SystemExit as exc:
            print(buffer.getvalue(), file=sys.stderr)
            raise SystemExit(f"the adapter refused: exit {exc.code}") from exc


def harness_run_id(sid: str, slug: str, number: int) -> str:
    return f"{sid}__{slug}__{number:03d}"


def split_penalties(violations: list[dict]) -> tuple[list[dict], list[dict]]:
    deducting, dismissed = [], []
    for v in violations:
        entry = {"type": str(v["type"]).upper(), "evidence": v.get("evidence"),
                 "reason": v.get("reason") or v.get("short_rationale")}
        if v.get("materially_misleading", True):
            deducting.append(entry)
        else:
            dismissed.append({**entry, "materially_misleading": False,
                              "note": "recorded by the judge as not materially misleading; "
                                      "the canonical scorer charges nothing for it"})
    return deducting, dismissed


# ---------------------------------------------------------------------------
# Per-model assembly: {sid: {run_number: {"criteria": {cid: (label, evidence,
# reason)}, "noise": [...] | None, "violations": [...], "dismissed": [...]}}}
# plus the adapter's breakdowns keyed the same way.
# ---------------------------------------------------------------------------

def assemble_opus(a: dict):
    gpt, letter_to_run = a["gpt"], a["letter_to_run"]
    out: dict = {sid: {} for sid in SCEN}
    for row in gpt["criterion_verdicts"]:
        sid, n = row["scenario"], letter_to_run[row["scenario"]][row["candidate"]]
        label = a["opus_labels"][sid][f"run{n}"][row["criterion_id"]]
        assert label == row["label"], row
        out[sid].setdefault(n, {"criteria": {}, "noise": None, "violations": [], "dismissed": []})
        out[sid][n]["criteria"][row["criterion_id"]] = (label, None, row["short_rationale"])
    for row in gpt["false_action_verdicts"]:
        sid, n = row["scenario"], letter_to_run[row["scenario"]][row["candidate"]]
        triggered = row["false_action_id"] in a["opus_noise"].get((sid, f"run{n}"), [])
        assert triggered == bool(row["triggered"]), row
        out[sid][n]["noise"] = (out[sid][n]["noise"] or []) + [
            {"id": row["false_action_id"], "triggered": triggered,
             "evidence": row.get("short_rationale") or ""}]
    for row in gpt["penalty_verdicts"]:
        sid, n = row["scenario"], letter_to_run[row["scenario"]][row["candidate"]]
        out[sid][n]["violations"], out[sid][n]["dismissed"] = split_penalties(
            row.get("violations") or [])
    breakdowns = {(sid, int(k[3:])): bd for (sid, k), bd in a["opus_breakdowns"].items()}
    return out, breakdowns


FABLE_002_KEYS = {"A_FROZEN": 1, "A2_FROZEN": 2, "A3_FROZEN": 3}
FABLE_002_RUNKEY = {1: "A1", 2: "A2", 3: "A3"}


def assemble_fable(a: dict):
    corrections = {(sid, rk, cid): (old, new) for sid, rk, cid, old, new in a["FABLE_CORRECTIONS"]}
    rows: dict = {}
    sources = [ROOT / "experiments/fable-5.1-full-mondaybench/verdicts.jsonl",
               ROOT / "experiments/fable-5.1-date-sensitivity/verdicts.jsonl",
               ROOT / "experiments/fable-5.1-date-sensitivity/verdicts-A2-A3.jsonl"]
    for path in sources:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            row = json.loads(line)
            sid, _, tail = row["run_id"].split("__")
            if sid == "monday-002":
                if tail not in FABLE_002_KEYS:
                    continue                      # B_NEUTRALIZED is not in the battery
                n = FABLE_002_KEYS[tail]
            else:
                n = int(tail.removeprefix("run"))
            rows.setdefault((sid, n), []).append(row)

    out: dict = {sid: {} for sid in SCEN}
    for (sid, n), source_rows in rows.items():
        run_key = FABLE_002_RUNKEY[n] if sid == "monday-002" else f"run{n}"
        labels = a["fable_labels"][sid][run_key]
        entry = {"criteria": {}, "noise": None, "violations": [], "dismissed": []}
        for row in source_rows:
            kind = row.get("kind", "criterion")
            if kind == "criterion":
                cid = row["criterion_id"]
                label, reason = labels[cid], row.get("reason")
                if (sid, run_key, cid) in corrections:
                    old, new = corrections[(sid, run_key, cid)]
                    assert row["result"] == old and label == new, (sid, run_key, cid)
                    reason = (f"POST-AUDIT CORRECTION {old} -> {new} (experiments/fable-5.1-"
                              f"full-mondaybench/AUDIT.md section 5). Original reason: {reason}")
                else:
                    assert row["result"] == label, (sid, run_key, cid, row["result"], label)
                entry["criteria"][cid] = (label, row.get("evidence"), reason)
            elif kind == "noise":
                # The adapter scores Fable's noise ladder as untriggered; the
                # source rows must agree or the score would not reproduce.
                assert not any(row["false_actions"].values()), row
                entry["noise"] = [{"id": fid, "triggered": False, "evidence": row.get("reason") or ""}
                                  for fid in row["false_actions"]]
            elif kind == "penalties":
                assert row["violations"] == [] and \
                    a["fable_penalties"].get((sid, run_key), []) == [], (sid, run_key)
                entry["dismissed"] = [
                    {**d, "type": str(d["type"]).upper()} for d in row.get("dismissed") or []]
        out[sid][n] = entry
    breakdowns = {}
    for (sid, run_key), bd in a["fable_breakdowns"].items():
        n = {v: k for k, v in FABLE_002_RUNKEY.items()}[run_key] if sid == "monday-002" \
            else int(run_key.removeprefix("run"))
        breakdowns[(sid, n)] = bd
    return out, breakdowns


def assemble_gemini(a: dict):
    path = ROOT / "experiments/gemini-3.8-flash-high-opus-judge/verdicts.jsonl"
    out: dict = {sid: {} for sid in SCEN}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        sid = row["run_id"].split("__", 1)[0]
        n = int(row["run_id"].rsplit("-", 1)[1])
        entry = out[sid].setdefault(n, {"criteria": {}, "noise": None,
                                        "violations": [], "dismissed": []})
        kind = row.get("kind", "criterion")
        if kind == "criterion":
            label = a["gemini_labels"][sid][row["run_id"]][row["criterion_id"]]
            assert label == row["result"], row
            entry["criteria"][row["criterion_id"]] = (label, row.get("evidence"), row.get("reason"))
        elif kind == "noise":
            entry["noise"] = [{"id": i["id"], "triggered": bool(i.get("triggered")),
                               "evidence": i.get("evidence") or ""} for i in row["items"]]
        elif kind == "penalties":
            entry["violations"], entry["dismissed"] = split_penalties(row.get("violations") or [])
    breakdowns = {(sid, int(k.rsplit("-", 1)[1])): bd
                  for (sid, k), bd in a["gemini_breakdowns"].items()}
    return out, breakdowns


def render(slug: str, sid: str, runs: dict, rubric) -> str:
    # No comment header: the recorded-verdict route skips `#` lines, but other
    # readers of verdicts/ (tests/test_monday_003.py among them) parse every
    # line as JSON, which every other verdict file in the tree allows. Which
    # judge produced the labels is printed below and stated in models.yaml.
    lines: list[str] = []
    for n in sorted(runs):
        entry, run_id = runs[n], harness_run_id(sid, slug, n)
        missing = [c.id for c in rubric.criteria if c.id not in entry["criteria"]]
        assert not missing, (slug, sid, n, missing)
        for criterion in rubric.criteria:
            label, evidence, reason = entry["criteria"][criterion.id]
            lines.append(json.dumps({"run_id": run_id, "criterion_id": criterion.id,
                                     "result": label, "evidence": evidence, "reason": reason},
                                    ensure_ascii=False))
        if rubric.noise is not None:
            noise = entry["noise"]
            assert noise is not None, (slug, sid, n, "no noise row")
            assert {i["id"] for i in noise} == {f.id for f in rubric.noise.false_actions}
            lines.append(json.dumps({"run_id": run_id, "kind": "noise", "items": noise},
                                    ensure_ascii=False))
        lines.append(json.dumps({"run_id": run_id, "kind": "penalties",
                                 "violations": entry["violations"],
                                 "dismissed": entry["dismissed"]}, ensure_ascii=False))
    return "\n".join(lines) + "\n"


def main() -> int:
    check = "--check" in sys.argv[1:]
    a = run_adapter()
    rubrics = a["RUBRICS"]
    models = {
        "claude-opus-5": assemble_opus(a),
        "claude-fable-5-1": assemble_fable(a),
        "gemini-3-8-flash-high": assemble_gemini(a),
    }

    if not check:
        for slug, (per_scen, breakdowns) in models.items():
            for sid in SCEN:
                assert sorted(per_scen[sid]) == [1, 2, 3], (slug, sid, sorted(per_scen[sid]))
                target = ROOT / "verdicts" / sid / f"{slug}.verdicts.jsonl"
                text = render(slug, sid, per_scen[sid], rubrics[sid])
                if target.exists() and target.read_text(encoding="utf-8") != text:
                    raise SystemExit(f"{target} exists and differs - refusing to overwrite")
                target.write_text(text, encoding="utf-8", newline="\n")
                print(f"  {target.relative_to(ROOT).as_posix()}  "
                      f"{sum(1 for l in text.splitlines() if l.startswith('{'))} rows  "
                      f"labels: {JUDGE_LINE[slug]}")
        return 0

    from mondaybench.evaluator import evaluation_path, load_evaluation
    failures = 0
    for slug, (_per_scen, breakdowns) in models.items():
        means = []
        for sid in SCEN:
            evaluator = a["EVALUATORS"][sid]
            scores = []
            for n in (1, 2, 3):
                path = evaluation_path(evaluator, sid, slug, n, None, SUITE)
                got = load_evaluation(path).final_score
                want = breakdowns[(sid, n)].final_score
                ok = abs(got - want) < 1e-9
                failures += not ok
                scores.append(got)
                print(f"  {slug:22} {sid} run-{n:03d}  harness {got:>6}  adapter {want:>6}"
                      f"  {'ok' if ok else 'MISMATCH'}")
            means.append(statistics.mean(scores))
        monday = round(statistics.mean(means), 2)
        ok = abs(monday - PUBLISHED[slug]) < 0.005
        failures += not ok
        print(f"  {slug:22} Monday Score {monday:.2f}  published {PUBLISHED[slug]:.2f}"
              f"  {'ok' if ok else 'MISMATCH'}\n")
    if failures:
        raise SystemExit(f"{failures} mismatch(es)")
    print("every run and every Monday Score reproduces")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
