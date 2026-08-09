from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
V1_PATH = ROOT / "benchmarks" / "results" / "cost-aware-baseline.json"
V2_PATH = ROOT / "benchmarks" / "publication" / "cost-aware-baseline-v2.json"
SCHEMA_PATH = ROOT / ".portfolio" / "contracts" / "benchmark-result-v2.schema.json"
CONFIG_PATH = ROOT / "benchmarks" / "config" / "cost-aware-baseline-v2.json"
FIXTURE_PATH = ROOT / "data"
LOCK_PATH = ROOT / "requirements-validation.lock"
PRODUCER_PATH = ROOT / "tools" / "generate-publication-benchmark.py"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256_file(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def load_producer() -> Any:
    spec = importlib.util.spec_from_file_location("publication_benchmark", PRODUCER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load publication producer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git_has_commit(commit: str) -> bool:
    completed = subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={ROOT}",
            "-C",
            str(ROOT),
            "cat-file",
            "-e",
            f"{commit}^{{commit}}",
        ],
        capture_output=True,
        check=False,
    )
    return completed.returncode == 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-git", action="store_true")
    args = parser.parse_args()

    manifest = (ROOT / "project.yaml").read_text(encoding="utf-8")
    published = re.search(r"(?m)^status:\s*published\s*$", manifest) is not None
    lock = LOCK_PATH.read_text(encoding="utf-8")
    require("jsonschema==4.26.0" in lock, "jsonschema is not pinned")
    require("setuptools==80.9.0" in lock, "setuptools is not pinned")

    config = read_json(CONFIG_PATH)
    require(config["provider_aliases"] == ["local"], "publication config provider mismatch")
    require(config["measured_requests"] == 3, "publication config request count mismatch")
    require(config["repeat"] == 5, "publication config repeat mismatch")
    require(config["measured_iterations"] == 15, "publication config iteration mismatch")
    require(config["concurrency"] == 1, "publication config concurrency mismatch")
    if not V2_PATH.is_file():
        require(not published, "published project requires V2 evidence")
        print("publication_evidence=not-applicable")
        return

    import jsonschema

    v1 = read_json(V1_PATH)
    v2 = read_json(V2_PATH)
    schema = read_json(SCHEMA_PATH)
    jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    ).validate(v2)

    require(v1.get("project") == "cost-aware-inference", "unexpected V1 project")
    require(v2.get("project") == "cost-aware-inference", "unexpected V2 project")
    require(
        v2.get("benchmark_id") == "offline-local-cost-accounting-v1",
        "unexpected benchmark id",
    )
    require(v1.get("metric") == "observed_p95_latency_ms", "unexpected primary metric")
    require(isinstance(v1.get("value"), (int, float)), "V1 latency must be numeric")
    require(v1.get("repeat") == 5, "unexpected process repetition count")
    require(v1.get("measured_iterations") == 15, "top-level measured iteration mismatch")
    require(len(v1.get("samples", [])) == 15, "expected 15 primary latency samples")

    summary = v1.get("summary", {})
    require(summary.get("request_count") == 15, "expected 15 measured requests")
    require(summary.get("measured_iterations") == 15, "summary iteration mismatch")
    require(summary.get("provider_count") == 1, "expected one published provider")
    require(summary.get("comparison_available") is False, "baseline must not claim comparison")
    require(summary.get("total_input_tokens") == 465, "input token baseline mismatch")
    require(summary.get("total_output_tokens") == 175, "output token baseline mismatch")
    require(summary.get("estimated_cost_usd") == 0.0, "local token tariff mismatch")

    claims = v1.get("claims", {})
    require(claims.get("local_baseline", "").endswith("not an LLM"), "local boundary is missing")
    providers = v1.get("providers", [])
    require(len(providers) == 1, "publication baseline must contain one provider")
    provider = providers[0]
    require(provider.get("provider") == "local-extractive-v1", "unexpected local provider")
    require(provider.get("mode") == "local", "unexpected provider mode")
    require(provider.get("estimated_cost_usd") == 0.0, "unexpected token charge")
    require(provider.get("measured", {}).get("request_count") == 15, "provider request count mismatch")
    require(provider.get("measured", {}).get("total_tokens") == 640, "token total mismatch")
    pricing = provider.get("pricing_assumption", {})
    require(pricing.get("input_per_million_tokens_usd") == 0.0, "local input tariff mismatch")
    require(pricing.get("output_per_million_tokens_usd") == 0.0, "local output tariff mismatch")
    require("excludes" in pricing.get("scope", ""), "infrastructure cost exclusion is missing")

    metric = v2["metrics"][0]
    require(metric["name"] == "observed_p95_latency_ms", "unexpected V2 metric")
    require(metric["value"] == v1["value"], "V1/V2 value mismatch")
    require(metric["samples"] == v1["samples"], "V1/V2 samples mismatch")
    require(metric["failures"] == 0, "publication contains failures")
    require(v2["execution"]["repeat"] == 5, "execution repeat mismatch")
    require(v2["workload"]["measured_iterations"] == 15, "workload iteration mismatch")
    require(v2["workload"]["warmup_iterations"] == 0, "unexpected warmup")
    require(v2["workload"]["concurrency"] == 1, "unexpected concurrency")
    require(
        v2["provenance"]["artifact_digest"] == sha256_file(V1_PATH),
        "raw artifact digest mismatch",
    )
    require(
        re.fullmatch(r"sha256:[0-9a-f]{64}", v2["provenance"]["image_digest"])
        is not None,
        "invalid image digest",
    )
    require(v2["comparability_key"] == config["comparability_key"], "comparability key mismatch")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for expected in (f"{v1['value']:.4f}", "640", "US$ 0.00", "not an LLM"):
        require(expected in readme, f"README is missing benchmark value {expected}")
    require(
        "result_path: benchmarks/publication/cost-aware-baseline-v2.json" in manifest,
        "manifest V2 path mismatch",
    )

    if args.require_git:
        source_commit = v2["provenance"]["source_commit"]
        require(git_has_commit(source_commit), "source commit unavailable; fetch full history")
        producer = load_producer()
        require(
            v2["workload"]["fixture_digest"]
            == producer.digest_committed_path(ROOT, FIXTURE_PATH, source_commit),
            "committed data digest mismatch",
        )
        require(
            v2["workload"]["config_digest"]
            == producer.digest_committed_path(ROOT, CONFIG_PATH, source_commit),
            "committed config digest mismatch",
        )
        require(
            v2["provenance"]["dependency_lock_digest"]
            == producer.digest_committed_path(ROOT, LOCK_PATH, source_commit),
            "committed validation-lock digest mismatch",
        )

    serialized = json.dumps({"v1": v1, "v2": v2})
    for forbidden in ("C:\\Users\\", "github" + "_pat_", "gh" + "p_"):
        require(forbidden not in serialized, f"forbidden value in evidence: {forbidden}")
    print("publication_evidence=passed")


if __name__ == "__main__":
    main()