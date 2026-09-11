"""Mechanical control-vs-treatment telemetry. No quality judgement anywhere.

Counts and distributions only. Nothing here reads a response's content, opens a
verdict file, or ranks one arm against the other; a larger number is reported as
a larger number and not as an improvement.

Control artifacts live in the repository's runs/ tree, treatment artifacts under
this experiment directory, which is why the two are loaded from different roots.
"""
from __future__ import annotations

import json
import statistics
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]

CONTROL = ("deepseek-v4.1-flash-rerun-v1", REPO / "runs")
TREATMENT = ("deepseek-v4.1-flash-rerun-guardrail-v1", ROOT / "runs")
SCENARIOS = ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"]


def load(slug: str, root: Path) -> dict[str, list[dict]]:
    out = {}
    for sid in SCENARIOS:
        rows = []
        for p in sorted((root / sid / slug).glob("run-*.json")):
            d = json.loads(p.read_text(encoding="utf-8"))
            rows.append({
                "run_number": d["run_number"],
                "reasoning_tokens": d["reasoning"]["tokens"],
                "reasoning_status": d["reasoning"]["status"],
                "reasoning_stream_observed": d["reasoning"]["stream_observed"],
                "reasoning_stream_event_count": d["reasoning"]["stream_event_count"],
                "input_tokens": d["usage"]["input_tokens"],
                "output_tokens": d["usage"]["output_tokens"],
                "ttft_ms": d["performance"]["ttft_ms"],
                "ttfa_ms": d["performance"]["ttfa_ms"],
                "total_latency_ms": d["performance"]["total_latency_ms"],
                "tokens_per_second": d["performance"]["tokens_per_second"],
                "finish_reason": d["finish_reason"],
                "max_output_tokens": d["generation"]["max_output_tokens"],
                "response_chars": len(d["response"] or ""),
                "cached_tokens": ((d["provider_metadata"]["raw_usage"] or {})
                                  .get("prompt_tokens_details", {}) or {}).get("cached_tokens"),
            })
        out[sid] = rows
    return out


def stats(vals: list[float]) -> dict:
    vals = [v for v in vals if v is not None]
    if not vals:
        return {"n": 0, "values": [], "mean": None, "median": None,
                "min": None, "max": None, "range": None}
    return {"n": len(vals), "values": vals,
            "mean": round(statistics.fmean(vals), 1),
            "median": round(statistics.median(vals), 1),
            "min": min(vals), "max": max(vals),
            "range": round(max(vals) - min(vals), 1)}


METRICS = ["reasoning_tokens", "output_tokens", "ttfa_ms", "total_latency_ms",
           "ttft_ms", "input_tokens", "response_chars"]


def main() -> int:
    ctl = load(*CONTROL)
    trt = load(*TREATMENT)
    report = {"control": CONTROL[0], "treatment": TREATMENT[0],
              "note": "counts and distributions only; no quality judgement is made or implied",
              "per_scenario": {}, "overall": {}}

    for sid in SCENARIOS:
        entry = {}
        for m in METRICS:
            entry[m] = {"control": stats([r[m] for r in ctl[sid]]),
                        "treatment": stats([r[m] for r in trt[sid]])}
        entry["finish_reason"] = {
            "control": dict(Counter(r["finish_reason"] for r in ctl[sid])),
            "treatment": dict(Counter(r["finish_reason"] for r in trt[sid]))}
        entry["reasoning_delivery_status"] = {
            "control": dict(Counter(r["reasoning_status"] for r in ctl[sid])),
            "treatment": dict(Counter(r["reasoning_status"] for r in trt[sid]))}
        ceil = ctl[sid][0]["max_output_tokens"]
        entry["ceiling"] = {
            "max_output_tokens": ceil,
            "control_hits": sum(1 for r in ctl[sid] if r["output_tokens"] >= ceil),
            "treatment_hits": sum(1 for r in trt[sid] if r["output_tokens"] >= ceil),
            "control_closest_to_ceiling": max(r["output_tokens"] for r in ctl[sid]),
            "treatment_closest_to_ceiling": max(r["output_tokens"] for r in trt[sid]),
            "control_headroom_pct": round(100 * (1 - max(r["output_tokens"] for r in ctl[sid]) / ceil), 1),
            "treatment_headroom_pct": round(100 * (1 - max(r["output_tokens"] for r in trt[sid]) / ceil), 1),
        }
        entry["cached_tokens"] = {
            "control": [r["cached_tokens"] for r in ctl[sid]],
            "treatment": [r["cached_tokens"] for r in trt[sid]]}
        report["per_scenario"][sid] = entry

    allc = [r for sid in SCENARIOS for r in ctl[sid]]
    allt = [r for sid in SCENARIOS for r in trt[sid]]
    for m in METRICS:
        report["overall"][m] = {"control": stats([r[m] for r in allc]),
                                "treatment": stats([r[m] for r in allt])}
    report["overall"]["finish_reason"] = {
        "control": dict(Counter(r["finish_reason"] for r in allc)),
        "treatment": dict(Counter(r["finish_reason"] for r in allt))}
    report["overall"]["reasoning_delivery_status"] = {
        "control": dict(Counter(r["reasoning_status"] for r in allc)),
        "treatment": dict(Counter(r["reasoning_status"] for r in allt))}
    report["overall"]["reasoning_stream_observed"] = {
        "control": dict(Counter(r["reasoning_stream_observed"] for r in allc)),
        "treatment": dict(Counter(r["reasoning_stream_observed"] for r in allt))}
    report["overall"]["ceiling_hits"] = {
        "control": sum(report["per_scenario"][s]["ceiling"]["control_hits"] for s in SCENARIOS),
        "treatment": sum(report["per_scenario"][s]["ceiling"]["treatment_hits"] for s in SCENARIOS)}
    report["overall"]["runs"] = {"control": len(allc), "treatment": len(allt)}

    (ROOT / "telemetry-comparison.json").write_bytes(
        (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))

    def line(label, c, t):
        return (f"  {label:<22} control {str(c['values']):<30} med {str(c['median']):>9}   "
                f"treatment {str(t['values']):<30} med {str(t['median']):>9}")

    for sid in SCENARIOS:
        e = report["per_scenario"][sid]
        print(f"\n=== {sid}  ceiling {e['ceiling']['max_output_tokens']}")
        for m in ("reasoning_tokens", "output_tokens", "ttfa_ms", "total_latency_ms"):
            print(line(m, e[m]["control"], e[m]["treatment"]))
        print(f"  {'finish_reason':<22} control {e['finish_reason']['control']}   "
              f"treatment {e['finish_reason']['treatment']}")
        print(f"  {'ceiling hits':<22} control {e['ceiling']['control_hits']}   "
              f"treatment {e['ceiling']['treatment_hits']}   "
              f"(headroom {e['ceiling']['control_headroom_pct']}% / "
              f"{e['ceiling']['treatment_headroom_pct']}%)")

    print("\n=== overall")
    for m in METRICS:
        c, t = report["overall"][m]["control"], report["overall"][m]["treatment"]
        print(f"  {m:<20} control mean {str(c['mean']):>9} med {str(c['median']):>9} "
              f"min {str(c['min']):>8} max {str(c['max']):>8} range {str(c['range']):>9}")
        print(f"  {'':<20} treatmt mean {str(t['mean']):>9} med {str(t['median']):>9} "
              f"min {str(t['min']):>8} max {str(t['max']):>8} range {str(t['range']):>9}")
    print(f"  finish_reason        control {report['overall']['finish_reason']['control']}  "
          f"treatment {report['overall']['finish_reason']['treatment']}")
    print(f"  reasoning status     control {report['overall']['reasoning_delivery_status']['control']}  "
          f"treatment {report['overall']['reasoning_delivery_status']['treatment']}")
    print(f"  ceiling hits         control {report['overall']['ceiling_hits']['control']}  "
          f"treatment {report['overall']['ceiling_hits']['treatment']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
