"""Inventory this experiment's files with their hashes.

    python make_manifest.py

Written last, so the hashes describe the artefacts as they were left. It records
what the experiment touched, which for this experiment is nothing outside its own
directory.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKIP_DIRS = {"__pycache__"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    files = []
    for path in sorted(HERE.rglob("*")):
        if path.is_dir() or any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name == "manifest.json":
            continue
        files.append({
            "path": path.relative_to(HERE).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })

    config_path = HERE / "phase-d-config.json"
    config = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
    summary_path = HERE / "analysis" / "phase-d-summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}

    manifest = {
        "experiment": HERE.name,
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "is_mondaybench_run": False,
        "phases_completed": ["A design", "B keys+scorers", "C calibration", "D baseline vs high"],
        "max_variant_executed": False,
        "model_slug": config.get("model_slug"),
        "microtest_id": config.get("microtest_id"),
        "prompt_sha256": config.get("prompt_sha256"),
        "order_seed": config.get("order_seed"),
        "bootstrap_seed": config.get("bootstrap_seed"),
        "calls": summary.get("calls", {}),
        "decision_gate_outcome": (summary.get("decision_gate") or {}).get("outcome"),
        "recommendation": (summary.get("decision_gate") or {}).get("recommendation"),
        "wrote_outside_this_directory": [],
        "read_for_data_outside_this_directory": [
            "models.yaml (deepseek-v4.1-flash config, read only)",
            ".env (HELMCODE_BASE_URL, HELMCODE_API_KEY, read only)",
            "experiments/deepseek-v4.1-flash-effort-probe-v1/ (phase 1a findings, read only)",
        ],
        "untouched": [
            "runs/", "evaluations/", "verdicts/", "leaderboards/", "releases/",
            "experiments/deepseek-v4.1-flash-reliability-v1/",
            "experiments/deepseek-v4.1-flash-effort-probe-v1/",
            "every published DeepSeek battery",
        ],
        "files": files,
    }
    (HERE / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"manifest.json: {len(files)} files")
    for entry in files:
        print(f"  {entry['sha256'][:12]}  {entry['bytes']:>9}  {entry['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
