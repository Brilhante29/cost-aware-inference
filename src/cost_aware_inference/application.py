from __future__ import annotations

import hashlib
import json
import math
import platform
import statistics
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .domain import InferenceRequest, PricingAssumption
from .ports import InferenceProvider


@dataclass(frozen=True)
class BenchmarkTarget:
    provider: InferenceProvider
    pricing: PricingAssumption

    def __post_init__(self) -> None:
        if self.provider.provider_id != self.pricing.provider_id:
            raise ValueError("provider and pricing identifiers must match")


def load_requests(path: str | Path) -> list[InferenceRequest]:
    rows = [
        json.loads(line)
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return [
        InferenceRequest(
            request_id=row["id"],
            prompt=row["prompt"],
            max_output_tokens=int(row["max_output_tokens"]),
        )
        for row in rows
    ]


def _percentile(values: Sequence[float], percentile: float) -> float:
    ordered = sorted(values)
    rank = max(1, math.ceil(percentile * len(ordered)))
    return ordered[rank - 1]


class BenchmarkRunner:
    def __init__(
        self,
        targets: Sequence[BenchmarkTarget],
        *,
        clock_ns: Callable[[], int] = time.perf_counter_ns,
    ) -> None:
        if not targets:
            raise ValueError("at least one benchmark target is required")
        self.targets = list(targets)
        provider_ids = [target.provider.provider_id for target in self.targets]
        if len(provider_ids) != len(set(provider_ids)):
            raise ValueError("provider identifiers must be unique")
        self.clock_ns = clock_ns

    def run(
        self,
        requests: Sequence[InferenceRequest],
        *,
        repeats: int,
        warmup_iterations: int = 0,
        command: str,
    ) -> dict:
        if not requests:
            raise ValueError("at least one inference request is required")
        if repeats <= 0:
            raise ValueError("repeats must be positive")
        if warmup_iterations < 0:
            raise ValueError("warmup_iterations must not be negative")

        for target in self.targets:
            for _ in range(warmup_iterations):
                target.provider.infer(requests[0])

        provider_samples: dict[str, list[dict]] = {
            target.provider.provider_id: [] for target in self.targets
        }
        for attempt in range(1, repeats + 1):
            for request in requests:
                for target in self.targets:
                    provider_samples[target.provider.provider_id].append(
                        self._measure(target, request, attempt)
                    )

        provider_results = [
            self._summarize_provider(
                target,
                provider_samples[target.provider.provider_id],
                warmup_iterations,
            )
            for target in self.targets
        ]
        primary = provider_results[0]
        measured = primary["measured"]
        total_measured_calls = sum(
            result["measured"]["request_count"] for result in provider_results
        )
        comparison = self._comparison(provider_results)
        return {
            "project": "cost-aware-inference",
            "metric": "observed_p95_latency_ms",
            "value": measured["p95_latency_ms"],
            "unit": "ms",
            "timestamp": datetime.now(timezone.utc)
            .isoformat(timespec="seconds")
            .replace("+00:00", "Z"),
            "command": command,
            "repeat": repeats,
            "measured_iterations": total_measured_calls,
            "samples": [row["observed_latency_ms"] for row in primary["samples"]],
            "summary": {
                "mean_latency_ms": measured["mean_latency_ms"],
                "p50_latency_ms": measured["p50_latency_ms"],
                "p95_latency_ms": measured["p95_latency_ms"],
                "request_count": measured["request_count"],
                "measured_iterations": total_measured_calls,
                "provider_count": len(provider_results),
                "comparison_available": len(provider_results) > 1,
                "warmup_iterations_per_provider": warmup_iterations,
                "failure_count": sum(result["failure_count"] for result in provider_results),
                "total_input_tokens": measured["total_input_tokens"],
                "total_output_tokens": measured["total_output_tokens"],
                "estimated_cost_usd": primary["estimated_cost_usd"],
            },
            "environment": {
                "python": platform.python_version(),
                "platform": platform.platform(),
                "machine": platform.machine() or "unknown",
            },
            "claims": {
                "latency": "observed wall-clock duration around each provider call",
                "tokens": "adapter-reported; local uses a documented regex tokenizer",
                "cost": "estimate from observed tokens and separately configured prices",
                "local_baseline": "deterministic extractive text processing, not an LLM",
            },
            "comparison": comparison,
            "providers": provider_results,
        }

    def _measure(
        self,
        target: BenchmarkTarget,
        request: InferenceRequest,
        attempt: int,
    ) -> dict:
        started = self.clock_ns()
        try:
            response = target.provider.infer(request)
        except Exception as error:  # noqa: BLE001 - failures are benchmark evidence
            elapsed_ms = (self.clock_ns() - started) / 1_000_000
            return {
                "request_id": request.request_id,
                "attempt": attempt,
                "observed_latency_ms": round(elapsed_ms, 6),
                "success": False,
                "error_type": type(error).__name__,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "output_sha256": None,
            }
        elapsed_ms = (self.clock_ns() - started) / 1_000_000
        return {
            "request_id": request.request_id,
            "attempt": attempt,
            "observed_latency_ms": round(elapsed_ms, 6),
            "success": True,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "total_tokens": response.input_tokens + response.output_tokens,
            "output_sha256": hashlib.sha256(response.text.encode("utf-8")).hexdigest(),
        }

    def _summarize_provider(
        self,
        target: BenchmarkTarget,
        samples: list[dict],
        warmup_iterations: int,
    ) -> dict:
        successful = [row for row in samples if row["success"]]
        if not successful:
            raise ValueError(f"provider {target.provider.provider_id} produced no successful calls")
        latencies = [row["observed_latency_ms"] for row in successful]
        input_tokens = sum(row["input_tokens"] for row in successful)
        output_tokens = sum(row["output_tokens"] for row in successful)
        total_duration_ms = sum(latencies)
        estimated_cost = target.pricing.estimate_cost(input_tokens, output_tokens)
        total_tokens = input_tokens + output_tokens
        measured = {
            "request_count": len(samples),
            "total_input_tokens": input_tokens,
            "total_output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "total_duration_ms": round(total_duration_ms, 6),
            "mean_latency_ms": round(statistics.fmean(latencies), 6),
            "p50_latency_ms": round(_percentile(latencies, 0.50), 6),
            "p95_latency_ms": round(_percentile(latencies, 0.95), 6),
            "throughput_tokens_per_second": round(
                total_tokens / (total_duration_ms / 1_000) if total_duration_ms else 0.0,
                3,
            ),
        }
        return {
            "provider": target.provider.provider_id,
            "mode": target.provider.mode,
            "implementation": target.provider.implementation,
            "metadata": dict(getattr(target.provider, "metadata", {})),
            "warmup_iterations": warmup_iterations,
            "failure_count": len(samples) - len(successful),
            "measured": measured,
            "pricing_assumption": {
                "currency": target.pricing.currency,
                "input_per_million_tokens_usd": float(
                    target.pricing.input_per_million_tokens_usd
                ),
                "output_per_million_tokens_usd": float(
                    target.pricing.output_per_million_tokens_usd
                ),
                "source": target.pricing.source,
                "scope": target.pricing.scope,
            },
            "estimated_cost_usd": round(float(estimated_cost), 12),
            "samples": samples,
        }

    @staticmethod
    def _comparison(provider_results: list[dict]) -> dict | None:
        if len(provider_results) < 2:
            return None
        primary = provider_results[0]
        baseline = next(
            (result for result in provider_results[1:] if result["mode"] == "local"),
            provider_results[1],
        )
        primary_p95 = primary["measured"]["p95_latency_ms"]
        baseline_p95 = baseline["measured"]["p95_latency_ms"]
        return {
            "primary_provider": primary["provider"],
            "baseline_provider": baseline["provider"],
            "p95_latency_delta_ms": round(primary_p95 - baseline_p95, 6),
            "p95_latency_ratio": round(
                primary_p95 / baseline_p95 if baseline_p95 else 0.0,
                6,
            ),
            "estimated_token_charge_delta_usd": round(
                primary["estimated_cost_usd"] - baseline["estimated_cost_usd"],
                12,
            ),
        }
