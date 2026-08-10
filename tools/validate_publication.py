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
    require(config["provider_aliases"] == ["http", "local"], "publication config provider mismatch")
    require(config["measured_requests_per_provider"] == 30, "publication config request count mismatch")
    require(config["repeat"] == 10, "publication config repeat mismatch")
    require(config["warmup_iterations_per_provider"] == 1, "publication warmup mismatch")
    require(config["warmup_iterations"] == 2, "publication total warmup mismatch")
    require(config["measured_iterations"] == 60, "publication config iteration mismatch")
    require(re.fullmatch(r"sha256:[0-9a-f]{64}", config["model_digest"]) is not None, "invalid configured model digest")
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
        v2.get("benchmark_id") == config["benchmark_id"],
        "unexpected benchmark id",
    )
    require(v1.get("metric") == "observed_p95_latency_ms", "unexpected primary metric")
    require(isinstance(v1.get("value"), (int, float)), "V1 latency must be numeric")
    require(v1.get("repeat") == 10, "unexpected process repetition count")
    require(v1.get("measured_iterations") == 60, "top-level measured iteration mismatch")
    require(len(v1.get("samples", [])) == 30, "expected 30 primary latency samples")

    summary = v1.get("summary", {})
    require(summary.get("request_count") == 30, "expected 30 primary requests")
    require(summary.get("measured_iterations") == 60, "summary iteration mismatch")
    require(summary.get("provider_count") == 2, "expected two published providers")
    require(summary.get("comparison_available") is True, "provider comparison is required")
    require(summary.get("warmup_iterations_per_provider") == 1, "runtime warmup mismatch")
    require(summary.get("failure_count") == 0, "publication must have zero provider failures")
    require(summary.get("total_input_tokens", 0) > 0, "primary input usage is missing")
    require(summary.get("total_output_tokens", 0) > 0, "primary output usage is missing")
    require(summary.get("estimated_cost_usd") == 0.0, "local Ollama token tariff mismatch")

    claims = v1.get("claims", {})
    require(claims.get("local_baseline", "").endswith("not an LLM"), "local boundary is missing")
    providers = v1.get("providers", [])
    require(len(providers) == 2, "publication comparison must contain two providers")
    provider = providers[0]
    require(provider.get("provider") == config["primary_provider"], "unexpected primary provider")
    require(provider.get("mode") == "http", "primary provider must use HTTP")
    require(provider.get("metadata", {}).get("model") == config["model"], "model name mismatch")
    require(provider.get("metadata", {}).get("model_digest") == config["model_digest"], "model digest mismatch")
    require(provider.get("failure_count") == 0, "primary provider contains failures")
    require(provider.get("estimated_cost_usd") == 0.0, "unexpected token charge")
    require(provider.get("measured", {}).get("request_count") == 30, "provider request count mismatch")
    require(provider.get("measured", {}).get("total_tokens", 0) > 0, "provider token usage missing")
    require(all(sample.get("success") for sample in provider.get("samples", [])), "primary provider has failed samples")
    pricing = provider.get("pricing_assumption", {})
    require(pricing.get("input_per_million_tokens_usd") == 0.0, "local input tariff mismatch")
    require(pricing.get("output_per_million_tokens_usd") == 0.0, "local output tariff mismatch")
    require("excludes" in pricing.get("scope", ""), "infrastructure cost exclusion is missing")

    baseline = providers[1]
    require(baseline.get("provider") == "local-extractive-v1", "unexpected reference provider")
    require(baseline.get("mode") == "local", "reference provider mode mismatch")
    require(baseline.get("failure_count") == 0, "reference provider contains failures")
    require(baseline.get("measured", {}).get("request_count") == 30, "reference request count mismatch")

    comparison = v1.get("comparison", {})
    require(comparison.get("primary_provider") == provider["provider"], "comparison primary mismatch")
    require(comparison.get("baseline_provider") == baseline["provider"], "comparison baseline mismatch")
    require(comparison.get("p95_latency_ratio", 0) > 1, "LLM HTTP p95 must exceed in-process reference")
    require(comparison.get("estimated_token_charge_delta_usd") == 0.0, "unexpected token charge delta")

    metric = v2["metrics"][0]
    require(metric["name"] == "observed_p95_latency_ms", "unexpected V2 metric")
    require(metric["value"] == v1["value"], "V1/V2 value mismatch")
    require(metric["samples"] == v1["samples"], "V1/V2 samples mismatch")
    require(metric["failures"] == 0, "publication contains failures")
    require(v2["execution"]["repeat"] == 10, "execution repeat mismatch")
    require(v2["workload"]["measured_iterations"] == 60, "workload iteration mismatch")
    require(v2["workload"]["warmup_iterations"] == 2, "unexpected warmup")
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
    for expected in (f"{v1['value']:.3f}", config["model"], "60", "US$ 0.00", "not an LLM"):
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
