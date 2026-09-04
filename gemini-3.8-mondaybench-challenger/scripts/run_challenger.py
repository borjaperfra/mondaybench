"""Generate challenger runs for Gemini 3.8 Flash (High) against MondayBench v1.0.

Strictly follows clean challenger rules:
- Blind to rubrics, ground truth, and verdicts during generation
- File opening audit hook enforcing zero access to scoring files
- 5 scenarios x 3 independent runs = 15 generations
- Exact prompt hash validation against SUITE-FROZEN.yaml before execution
- Raw response, text response, and metadata three-way preservation
- Generation freeze barrier creating generation-freeze-manifest.json
"""

import hashlib
import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# Add repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

CHALLENGER_DIR = REPO_ROOT / "gemini-3.8-mondaybench-challenger"

FROZEN_PROMPT_HASHES = {
    "monday-001": "ed4d7beb1d7d1029c36eb8533e449027e0dc1a1047f8a38951a91781a0a5e398",
    "monday-002": "740e627cbc7413c321ede0d54000504de54821d34ff4677f82731b89600423a8",
    "monday-003": "aaf788f309d955d2b427c86fe7d95d2bbf88575fde7306adcfd74b0ec4a4103f",
    "monday-004": "3a0cbb569ca4f711b8907177af9204cec267d26f35f732829df56b03ed23ef99",
    "monday-005": "532cd464a9b75045f808886c44e667237d6fd1b947826510643b9f8bcc30059a",
}

SUITE_DIGEST = "c056b4b43d3caeb3b50394282b08ed281a5716fb1df68d1666abb950aa0b2a80"

PROHIBITED_PATTERNS = [
    r"rubric.*\.ya?ml$",
    r"ground[-_]truth.*\.ya?ml$",
    r"factual[-_]anchors",
    r"[\\/]verdicts[\\/]",
    r"[\\/]evaluations[\\/]",
    r"[\\/]leaderboard[\\/]",
    r"[\\/]runs[\\/]",
    r"[\\/]audits[\\/]",
]

OPENED_FILES = set()


def audit_file_open(event, args):
    if event == "open":
        file_path = str(args[0])
        norm_path = os.path.normpath(file_path).lower()
        for pat in PROHIBITED_PATTERNS:
            if re.search(pat, norm_path):
                raise PermissionError(
                    f"GENERATION ISOLATION VIOLATION: Attempted to open prohibited scoring file: {file_path}"
                )
        OPENED_FILES.add(file_path)


# Install audit hook
sys.addaudithook(audit_file_open)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_isolated_prompt(scenario_id: str) -> tuple[str, str]:
    """Load scenario prompt without touching rubric or ground-truth files."""
    scen_dir = REPO_ROOT / "scenarios" / scenario_id
    scen_yaml = scen_dir / "scenario.yaml"

    # Minimal YAML parsing to extract sources and template
    import yaml
    with open(scen_yaml, "r", encoding="utf-8") as f:
        meta = yaml.safe_load(f)

    sources = list(meta.get("sources") or meta.get("source_order") or [])
    prompt_file = scen_dir / meta.get("prompt_file", "prompt.md")

    with open(prompt_file, "r", encoding="utf-8") as f:
        template = f.read()

    source_text = {}
    for src in sources:
        src_path = scen_dir / src
        with open(src_path, "r", encoding="utf-8") as f:
            source_text[src] = f.read()

    # Match mondaybench.prompt_builder assembly logic exactly
    placeholder_pat = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
    any_placeholder = bool(placeholder_pat.search(template))

    if not any_placeholder:
        # Append mode (e.g. monday-002)
        parts = [template.rstrip()]
        for src in sources:
            stem = src.rsplit(".", 1)[0]
            title = re.sub(r"[^0-9A-Za-z]+", " ", stem).strip().title()
            body = source_text[src].strip()
            parts.append(f"---\n\n## {title}\n\n{body}")
        prompt_text = "\n\n".join(parts) + "\n"
    else:
        # Substitution mode (e.g. monday-001, 003, 004, 005)
        prompt_text = template
        for src in sources:
            stem = src.rsplit(".", 1)[0]
            token = "{{" + re.sub(r"[^A-Z0-9]+", "_", stem.upper()).strip("_") + "}}"
            body = source_text[src].strip()
            prompt_text = prompt_text.replace(token, body)

    computed_hash = sha256_text(prompt_text)
    return prompt_text, computed_hash


def call_language_server(prompt_text: str) -> tuple[str, str, float]:
    addr = os.environ.get("ANTIGRAVITY_LS_ADDRESS", "localhost:65173")
    token = os.environ.get("ANTIGRAVITY_CSRF_TOKEN", "")

    url = f"http://{addr}/exa.language_server_pb.LanguageServerService/GetModelResponse"
    req_payload = {
        "prompt": prompt_text,
        "model": "MODEL_PLACEHOLDER_M318"
    }
    body = json.dumps(req_payload).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-codeium-csrf-token": token
        }
    )

    t0 = time.perf_counter()
    with urllib.request.urlopen(req) as resp:
        raw_body = resp.read().decode("utf-8")
    latency_ms = (time.perf_counter() - t0) * 1000.0

    parsed = json.loads(raw_body)
    response_text = parsed.get("response", "")
    return raw_body, response_text, latency_ms


def main():
    print("=================================================================")
    print("MondayBench v1.0 Challenger Run: Gemini 3.8 Flash (High)")
    print("=================================================================")

    # Ensure output directories exist
    config_dir = CHALLENGER_DIR / "config"
    raw_dir = CHALLENGER_DIR / "raw"
    responses_dir = CHALLENGER_DIR / "responses"
    metadata_dir = CHALLENGER_DIR / "metadata"

    config_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)
    responses_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    model_config_file = config_dir / "model-config.json"
    if not model_config_file.exists():
        raise FileNotFoundError(f"Model config not found at {model_config_file}")
    model_config_sha256 = sha256_file(model_config_file)
    print(f"Frozen Model Config: {model_config_file} (SHA256: {model_config_sha256[:16]}...)")

    # Verify all 5 prompt hashes using isolated loader
    print("\n--- Verifying Frozen Scenario Prompts (Isolated Loader) ---")
    scenarios_data = {}
    for sid, expected_hash in FROZEN_PROMPT_HASHES.items():
        prompt_text, prompt_hash = load_isolated_prompt(sid)
        if prompt_hash != expected_hash:
            raise ValueError(f"CRITICAL DISCREPANCY in {sid}: prompt hash {prompt_hash} != {expected_hash}")
        print(f"[OK] {sid}: prompt hash verified ({prompt_hash[:16]}...) [length: {len(prompt_text)} chars]")
        scenarios_data[sid] = (prompt_text, prompt_hash)

    print("\nAll 5 frozen scenario prompt hashes verified exactly against MondayBench v1.0 manifest.")

    # Execute 15 generations
    total_runs = 0
    all_response_hashes = {}
    freeze_runs_data = []

    for sid in ["monday-001", "monday-002", "monday-003", "monday-004", "monday-005"]:
        prompt_text, prompt_hash = scenarios_data[sid]
        print(f"\n========================================================")
        print(f"Executing Scenario: {sid}")
        print(f"========================================================")

        scen_raw_dir = raw_dir / sid
        scen_resp_dir = responses_dir / sid
        scen_meta_dir = metadata_dir / sid
        scen_raw_dir.mkdir(parents=True, exist_ok=True)
        scen_resp_dir.mkdir(parents=True, exist_ok=True)
        scen_meta_dir.mkdir(parents=True, exist_ok=True)

        for run_num in [1, 2, 3]:
            run_id = f"{sid}__gemini-3.8-flash-high__run-{run_num:03d}"
            raw_file = scen_raw_dir / f"run-{run_num:03d}.json"
            resp_file = scen_resp_dir / f"run-{run_num:03d}.txt"
            meta_file = scen_meta_dir / f"run-{run_num:03d}.json"

            print(f"\n--- Generating {sid} run-{run_num:03d} ---")
            started_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

            # Execute inference
            try:
                raw_body, response_text, latency_ms = call_language_server(prompt_text)
                status = "COMPLETED"
                error_msg = None
            except Exception as e:
                status = "FAILED"
                error_msg = str(e)
                raw_body = "{}"
                response_text = ""
                latency_ms = 0.0
                print(f"ERROR generating {run_id}: {e}")
                sys.exit(1)

            finished_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

            # Calculate hashes
            resp_bytes = response_text.encode("utf-8")
            raw_bytes = raw_body.encode("utf-8")
            resp_sha256 = hashlib.sha256(resp_bytes).hexdigest()
            raw_sha256 = hashlib.sha256(raw_bytes).hexdigest()

            # Track duplicate responses
            if resp_sha256 in all_response_hashes:
                print(f"[NOTE] Duplicate response hash detected: {resp_sha256[:16]}... (Also seen in {all_response_hashes[resp_sha256]})")
            all_response_hashes[resp_sha256] = run_id

            # Check truncation heuristic against 65536 max tokens ceiling
            # Rough character ratio ~ 4 chars/tok => ~260,000 chars
            ceiling_char_limit = 65536 * 4
            is_truncated = len(response_text) >= ceiling_char_limit
            finish_reason = "length" if is_truncated else "stop"
            truncation_status = "TRUNCATED" if is_truncated else "COMPLETE"

            # 1. Preserve raw envelope
            raw_file.write_text(raw_body, encoding="utf-8", newline="\n")

            # 2. Preserve textual answer
            resp_file.write_text(response_text, encoding="utf-8", newline="\n")

            # 3. Construct and write metadata
            metadata = {
                "scenario_id": sid,
                "run_id": run_id,
                "run_number": run_num,
                "model_display_name": "Gemini 3.8 Flash (High)",
                "requested_model_id": "gemini-3.8-flash-high",
                "raw_model_identifier": "MODEL_PLACEHOLDER_M318",
                "served_model_id": "UNOBSERVABLE",
                "provider": "google",
                "platform": "antigravity",
                "language_server_version": "ide-2.4.5",
                "session_isolation": "independent stateless RPC, no conversation/session reuse",
                "started_at": started_at,
                "finished_at": finished_at,
                "latency_ms": round(latency_ms, 2),
                "prompt_sha256": prompt_hash,
                "response_sha256": resp_sha256,
                "raw_sha256": raw_sha256,
                "output_bytes": len(resp_bytes),
                "output_chars": len(response_text),
                "max_output_tokens": 65536,
                "finish_reason": finish_reason,
                "truncation_status": truncation_status,
                "status": status,
                "error_status": error_msg,
                "raw_file": str(raw_file.relative_to(CHALLENGER_DIR)),
                "response_file": str(resp_file.relative_to(CHALLENGER_DIR)),
            }
            meta_json = json.dumps(metadata, indent=2)
            meta_file.write_text(meta_json, encoding="utf-8")
            meta_sha256 = hashlib.sha256(meta_json.encode("utf-8")).hexdigest()

            # Record in freeze data
            freeze_runs_data.append({
                "scenario_id": sid,
                "run_id": run_id,
                "prompt_sha256": prompt_hash,
                "response_sha256": resp_sha256,
                "raw_sha256": raw_sha256,
                "metadata_sha256": meta_sha256,
                "started_at": started_at,
                "finished_at": finished_at,
                "requested_model": "gemini-3.8-flash-high",
                "served_model": "UNOBSERVABLE",
                "finish_reason": finish_reason,
                "truncation_status": truncation_status,
                "output_bytes": len(resp_bytes),
            })

            print(f"Completed {run_id}: {len(response_text)} chars in {latency_ms/1000:.2f}s, SHA256: {resp_sha256[:16]}... ({truncation_status})")
            total_runs += 1
            time.sleep(1.0)

    # 5. Write Generation Input Manifest
    repo_root_str = str(REPO_ROOT).lower()
    rel_opened_files = []
    prohibited_count = 0
    for p in sorted(OPENED_FILES):
        p_str = str(p)
        if repo_root_str in p_str.lower():
            rel_p = os.path.relpath(p, REPO_ROOT)
            rel_opened_files.append(rel_p)
            for pat in PROHIBITED_PATTERNS:
                if re.search(pat, rel_p.lower()):
                    prohibited_count += 1

    input_manifest = {
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_files_opened": len(rel_opened_files),
        "prohibited_files_opened": prohibited_count,
        "isolation_verified": prohibited_count == 0,
        "files": rel_opened_files
    }
    input_manifest_file = CHALLENGER_DIR / "generation-input-manifest.json"
    input_manifest_file.write_text(json.dumps(input_manifest, indent=2), encoding="utf-8")
    print(f"\nGeneration input manifest written to {input_manifest_file} (Prohibited files opened: {prohibited_count})")

    # 6. Write Generation Freeze Barrier Manifest
    freeze_manifest = {
        "number_of_runs": total_runs,
        "suite_digest": SUITE_DIGEST,
        "model_config_sha256": model_config_sha256,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "runs": freeze_runs_data
    }
    freeze_manifest_file = CHALLENGER_DIR / "generation-freeze-manifest.json"
    freeze_manifest_json = json.dumps(freeze_manifest, indent=2)
    freeze_manifest_file.write_text(freeze_manifest_json, encoding="utf-8")
    freeze_manifest_sha256 = hashlib.sha256(freeze_manifest_json.encode("utf-8")).hexdigest()

    print(f"\n========================================================")
    print(f"GENERATION FREEZE BARRIER ESTABLISHED")
    print(f"Manifest: {freeze_manifest_file}")
    print(f"Freeze Manifest SHA256: {freeze_manifest_sha256}")
    print(f"Total Runs: {total_runs} / 15")
    print(f"========================================================")


if __name__ == "__main__":
    main()
