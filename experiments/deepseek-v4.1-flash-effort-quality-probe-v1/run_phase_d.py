"""Phase D: 20 baseline vs 20 reasoning_effort="high" on the selected microtest.

    python run_phase_d.py --preflight    writes preflight.json + phase-d-config.json
    python run_phase_d.py --execute      runs the 40 samples in the frozen order

The microtest comes from `calibration-result.json` and cannot be overridden from
the command line: the instrument was chosen by the recorded selection rule
before any `high` sample existed, and this script only obeys that choice.

None of the calibration samples are reused. These are 40 new samples, in a
randomised balanced interleaved order frozen before the first call.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import probe_lib as lib

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw" / "phase-d.jsonl"

N_PER_VARIANT = 20
ORDER_SEED = 31415926
BOOTSTRAP_SEED = 27182818
VARIANTS = {"baseline": None, "high": "high"}


def selected_microtest() -> str:
    result = json.loads((HERE / "calibration-result.json").read_text(encoding="utf-8"))
    chosen = result.get("selected")
    if not chosen:
        raise SystemExit("STOP: calibration selected no microtest")
    return chosen


def build_preflight(model, test_id: str) -> dict:
    prompt = lib.microtest_prompt(test_id)
    base = lib.request_fingerprint(model, None, prompt)
    high = lib.request_fingerprint(model, "high", prompt)
    controlled = {}
    for key in base:
        controlled[key] = {"baseline": base[key], "high": high[key],
                           "same": base[key] == high[key]}
    differences = [k for k, v in controlled.items() if not v["same"]]
    return {
        "generated_utc": lib.now(),
        "phase": "D",
        "question": "Does reasoning_effort=high change task quality on a "
                    "non-saturated objective instrument?",
        "primary_metric": "success rate",
        "is_mondaybench_run": False,
        "microtest_id": test_id,
        "microtest_selected_before_any_high_sample": True,
        "controlled": controlled,
        "differences": differences,
        "declared_deviations_from_a_benchmark_run": [
            {"what": "system prompt", "value": "absent for every variant",
             "constant_across_variants": True,
             "why": "continues the configuration of effort-probe-v1"},
            {"what": "streaming", "value": "on for every variant",
             "constant_across_variants": True,
             "why": "needed to observe reasoning stream events"},
        ],
        "verdict": "CLEAN" if differences == ["reasoning_effort"] else "STOP",
    }


def cmd_preflight(model) -> int:
    test_id = selected_microtest()
    preflight = build_preflight(model, test_id)
    (HERE / "preflight.json").write_text(json.dumps(preflight, indent=2), encoding="utf-8")

    print(f"PREFLIGHT - phase D on {test_id}\n")
    width = max(len(k) for k in preflight["controlled"])
    for key, entry in preflight["controlled"].items():
        tag = "SAME     " if entry["same"] else "DIFFERENT"
        shown = entry["baseline"] if entry["same"] else f"{entry['baseline']}  ->  {entry['high']}"
        print(f"  {tag}  {key:<{width}}  {shown}")
    print(f"\n  differences: {preflight['differences']}")
    print(f"  verdict: {preflight['verdict']}")
    if preflight["verdict"] != "CLEAN":
        print("\nSTOP: something other than reasoning_effort differs.")
        return 1

    config_path = HERE / "phase-d-config.json"
    if config_path.exists():
        print(f"\n{config_path.name} exists; the frozen order is NOT regenerated.")
        return 0
    slots = ["baseline"] * N_PER_VARIANT + ["high"] * N_PER_VARIANT
    random.Random(ORDER_SEED).shuffle(slots)
    order = [{"sample_id": f"d{i + 1:03d}", "variant": v} for i, v in enumerate(slots)]
    keys = lib.answer_keys()[test_id]
    config = {
        "frozen_utc": lib.now(),
        "phase": "D",
        "microtest_id": test_id,
        "prompt_file": keys["prompt_file"],
        "prompt_sha256": keys["prompt_sha256"],
        "prompt_bytes": keys["prompt_bytes"],
        "answer_type": keys["answer_type"],
        "answer_key": keys["answer"],
        "scorer_file": "scorers.py",
        "n_per_variant": N_PER_VARIANT,
        "order_seed": ORDER_SEED,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "bootstrap_resamples": 10000,
        "interleaved": True,
        "reuses_calibration_samples": False,
        "max_variant_executed": False,
        "request_config": {k: v["baseline"] for k, v in
                           build_preflight(model, test_id)["controlled"].items()
                           if k != "reasoning_effort"},
        "order": order,
    }
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    counts = {v: sum(1 for s in order if s["variant"] == v) for v in VARIANTS}
    print(f"\n  frozen order -> {config_path.name} ({counts}, seed {ORDER_SEED})")
    print("  first 12 slots: " + " ".join(s["variant"][0].upper() for s in order[:12]))
    return 0


def cmd_execute(model) -> int:
    preflight = json.loads((HERE / "preflight.json").read_text(encoding="utf-8"))
    if preflight["verdict"] != "CLEAN":
        print("STOP: preflight verdict is not CLEAN")
        return 1
    config = json.loads((HERE / "phase-d-config.json").read_text(encoding="utf-8"))
    test_id = config["microtest_id"]
    if lib.answer_keys()[test_id]["prompt_sha256"] != config["prompt_sha256"]:
        print("STOP: the microtest prompt no longer matches the frozen hash")
        return 1

    provider = lib.build_provider(model)
    done = {r["sample_id"] for r in lib.read_jsonl(RAW)}
    if done:
        print(f"resuming: {len(done)} already recorded")
    for slot in config["order"]:
        if slot["sample_id"] in done:
            continue
        record = lib.one_call(
            provider, model,
            test_id=test_id,
            effort=VARIANTS[slot["variant"]],
            sample_id=slot["sample_id"],
            variant=slot["variant"],
            phase="D",
        )
        lib.append(RAW, record)
        lib.print_row(record)
    print(f"\nwrote -> {RAW}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    model = lib.load_model()
    if args.preflight:
        return cmd_preflight(model)
    if args.execute:
        return cmd_execute(model)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
