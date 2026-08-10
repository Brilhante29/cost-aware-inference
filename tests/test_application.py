import unittest
from decimal import Decimal

from cost_aware_inference.adapters.local import LocalExtractiveProvider
from cost_aware_inference.application import BenchmarkRunner, BenchmarkTarget
from cost_aware_inference.domain import (
    InferenceRequest,
    InferenceResponse,
    PricingAssumption,
)


class RecordingProvider:
    mode = "http"
    implementation = "recording-test-provider"
    metadata = {"model": "test", "model_digest": "sha256:test", "runtime": "test"}

    def __init__(self, provider_id, calls):
        self.provider_id = provider_id
        self.calls = calls

    def infer(self, request):
        self.calls.append((self.provider_id, request.request_id))
        return InferenceResponse("answer", 2, 1)


class BenchmarkRunnerTests(unittest.TestCase):
    def test_emits_shared_contract_and_per_provider_samples(self):
        provider = LocalExtractiveProvider()
        pricing = PricingAssumption(
            provider_id=provider.provider_id,
            currency="USD",
            input_per_million_tokens_usd=Decimal("1.5"),
            output_per_million_tokens_usd=Decimal("2.0"),
            source="test assumption",
            scope="token charges only",
        )
        ticks = iter((0, 1_000_000, 2_000_000, 4_000_000))
        runner = BenchmarkRunner(
            [BenchmarkTarget(provider=provider, pricing=pricing)],
            clock_ns=lambda: next(ticks),
        )
        requests = [
            InferenceRequest("r1", "First prompt. More useful prompt.", 8),
            InferenceRequest("r2", "Second prompt. Measured prompt work.", 8),
        ]

        result = runner.run(requests, repeats=1, command="test benchmark")

        required = {"project", "metric", "value", "unit", "timestamp", "command"}
        self.assertTrue(required.issubset(result))
        self.assertEqual(result["metric"], "observed_p95_latency_ms")
        self.assertEqual(result["repeat"], 1)
        self.assertEqual(result["measured_iterations"], 2)
        self.assertEqual(result["summary"]["provider_count"], 1)
        self.assertFalse(result["summary"]["comparison_available"])
        self.assertTrue(result["timestamp"].endswith("Z"))
        self.assertEqual(result["samples"], [1.0, 2.0])
        self.assertEqual(result["value"], 2.0)
        row = result["providers"][0]
        self.assertEqual(row["measured"]["request_count"], 2)
        self.assertEqual(len(row["samples"]), 2)
        self.assertNotIn("cost", row["measured"])
        self.assertGreater(row["estimated_cost_usd"], 0)
        self.assertEqual(row["pricing_assumption"]["source"], "test assumption")

    def test_provider_and_pricing_must_match(self):
        provider = LocalExtractiveProvider()
        pricing = PricingAssumption(
            provider_id="another-provider",
            currency="USD",
            input_per_million_tokens_usd=Decimal("0"),
            output_per_million_tokens_usd=Decimal("0"),
            source="test",
            scope="test",
        )
        with self.assertRaises(ValueError):
            BenchmarkTarget(provider=provider, pricing=pricing)

    def test_interleaves_providers_after_explicit_warmup(self):
        calls = []
        providers = [
            RecordingProvider("http-model", calls),
            RecordingProvider("local-reference", calls),
        ]
        providers[1].mode = "local"
        targets = [
            BenchmarkTarget(
                provider=provider,
                pricing=PricingAssumption(
                    provider_id=provider.provider_id,
                    currency="USD",
                    input_per_million_tokens_usd=Decimal("0"),
                    output_per_million_tokens_usd=Decimal("0"),
                    source="test",
                    scope="test",
                ),
            )
            for provider in providers
        ]
        ticks = iter(range(0, 8_000_000, 1_000_000))
        requests = [
            InferenceRequest("r1", "first", 4),
            InferenceRequest("r2", "second", 4),
        ]

        result = BenchmarkRunner(targets, clock_ns=lambda: next(ticks)).run(
            requests,
            repeats=1,
            warmup_iterations=1,
            command="test",
        )

        self.assertEqual(
            calls,
            [
                ("http-model", "r1"),
                ("local-reference", "r1"),
                ("http-model", "r1"),
                ("local-reference", "r1"),
                ("http-model", "r2"),
                ("local-reference", "r2"),
            ],
        )
        self.assertEqual(result["measured_iterations"], 4)
        self.assertEqual(result["summary"]["failure_count"], 0)
        self.assertTrue(result["summary"]["comparison_available"])
        self.assertEqual(result["comparison"]["primary_provider"], "http-model")


if __name__ == "__main__":
    unittest.main()
