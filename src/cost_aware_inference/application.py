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
        self.clock_ns = clock_ns

    def run(
        self,
        requests: Sequence[InferenceRequest],
        *,
        repeats: int,
        command: str,
    ) -> dict:
        if not requests:
            raise ValueError("at least one inference request is required")
        if repeats <= 0:
            raise ValueError("repeats must be positive")

        provider_results = [
            self._run_provider(target, requests, repeats) for target in self.targets
        ]
        primary = provider_results[0]
        measured = primary["measured"]
        return {
            "project": "cost-aware-inference",
            "metric": "observed_p95_latency_ms",
            "value": measured["p95_latency_ms"],
            "unit": "ms",
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "command": command,
            "repeat": repeats,
            "samples": [row["observed_latency_ms"] for row in primary["samples"]],
            "summary": {
                "mean_latency_ms": measured["mean_latency_ms"],
                "p50_latency_ms": measured["p50_latency_ms"],
                "p95_latency_ms": measured["p95_latency_ms"],
                "request_count": measured["request_count"],
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
            "providers": provider_results,
        }

    def _run_provider(
        self,
        target: BenchmarkTarget,
        requests: Sequence[InferenceRequest],
        repeats: int,
    ) -> dict:
        samples: list[dict] = []
        for attempt in range(1, repeats + 1):
            for request in requests:
                started = self.clock_ns()
                response = target.provider.infer(request)
                elapsed_ms = (self.clock_ns() - started) / 1_000_000
                samples.append(
                    {
                        "request_id": request.request_id,
                        "attempt": attempt,
                        "observed_latency_ms": round(elapsed_ms, 6),
                        "input_tokens": response.input_tokens,
                        "output_tokens": response.output_tokens,
                        "total_tokens": response.input_tokens + response.output_tokens,
                        "output_sha256": hashlib.sha256(
                            response.text.encode("utf-8")
                        ).hexdigest(),
                    }
                )

        latencies = [row["observed_latency_ms"] for row in samples]
        input_tokens = sum(row["input_tokens"] for row in samples)
        output_tokens = sum(row["output_tokens"] for row in samples)
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
