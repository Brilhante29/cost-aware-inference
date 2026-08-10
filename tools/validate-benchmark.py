from __future__ import annotations

import json
import math
import sys
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate(document: dict) -> None:
    required = {"project", "metric", "value", "unit", "timestamp", "command"}
    require(required.issubset(document), "shared benchmark fields are incomplete")
    require(document["project"] == "cost-aware-inference", "unexpected project id")
    require(document["metric"] == "observed_p95_latency_ms", "unexpected metric")
    require(document["unit"] == "ms", "unexpected metric unit")
    require(isinstance(document["value"], (int, float)), "metric value must be numeric")
    require(isinstance(document.get("providers"), list) and document["providers"], "providers are required")

    primary = document["providers"][0]
    primary_latencies = [sample["observed_latency_ms"] for sample in primary["samples"]]
    require(document.get("samples") == primary_latencies, "root samples must mirror the primary provider")
    require(math.isclose(document["value"], primary["measured"]["p95_latency_ms"]), "root metric must match the primary provider")
    require(document.get("repeat", 0) > 0, "repeat must count process workload repetitions")
    total_calls = sum(len(provider["samples"]) for provider in document["providers"])
    require(document.get("measured_iterations") == total_calls, "measured iterations must match all provider calls")
    summary = document.get("summary", {})
    require(summary.get("measured_iterations") == total_calls, "summary measured iterations mismatch")
    require(summary.get("provider_count") == len(document["providers"]), "provider count mismatch")
    require(summary.get("comparison_available") is (len(document["providers"]) > 1), "comparison flag mismatch")

    for provider in document["providers"]:
        require(provider.get("provider"), "provider id is required")
        require(provider.get("implementation"), "provider implementation is required")
        require(provider.get("metadata", {}).get("model") is not None, "provider model metadata is required")
        require(provider.get("metadata", {}).get("model_digest"), "provider model digest metadata is required")
        require(isinstance(provider.get("samples"), list) and provider["samples"], "provider samples are required")
        measured = provider.get("measured", {})
        pricing = provider.get("pricing_assumption", {})
        require("source" in pricing and "scope" in pricing, "pricing source and scope are required")
        require("estimated_cost_usd" in provider, "estimated cost is required")
        require("cost" not in measured, "estimated cost must not be stored as a measured runtime field")
        require(measured.get("request_count") == len(provider["samples"]), "request count does not match samples")
        failures = [sample for sample in provider["samples"] if not sample.get("success")]
        require(provider.get("failure_count") == len(failures), "provider failure count mismatch")
        require(measured.get("total_input_tokens") == sum(row["input_tokens"] for row in provider["samples"]), "input token total does not match samples")
        require(measured.get("total_output_tokens") == sum(row["output_tokens"] for row in provider["samples"]), "output token total does not match samples")
        for sample in provider["samples"]:
            sample_required = {
                "request_id", "attempt", "observed_latency_ms", "input_tokens",
                "output_tokens", "total_tokens", "output_sha256", "success",
            }
            require(sample_required.issubset(sample), "provider sample fields are incomplete")
            require(sample["total_tokens"] == sample["input_tokens"] + sample["output_tokens"], "sample token total is invalid")
            if sample["success"]:
                require(isinstance(sample["output_sha256"], str) and len(sample["output_sha256"]) == 64, "successful output digest is invalid")

    serialized_keys = {str(key).lower() for key in walk_keys(document)}
    forbidden = {"api_key", "authorization", "secret", "access_token"}
    require(not serialized_keys.intersection(forbidden), "benchmark must not serialize secrets")


def walk_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_keys(child)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate-benchmark.py <result.json>")
    path = Path(sys.argv[1])
    validate(json.loads(path.read_text(encoding="utf-8")))
    print(f"benchmark contract passed: {path}")


if __name__ == "__main__":
    main()
