import json
import unittest

from cost_aware_inference.adapters.openai_compatible import OpenAICompatibleProvider
from cost_aware_inference.domain import InferenceRequest
from cost_aware_inference.pricing import http_pricing_from_environment


class FakeResponse:
    def __init__(self, document):
        self.payload = json.dumps(document).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return self.payload


class FakeOpener:
    def __init__(self):
        self.calls = []

    def __call__(self, request, timeout):
        self.calls.append((request, timeout))
        return FakeResponse(
            {
                "choices": [{"message": {"content": "measured response"}}],
                "usage": {"prompt_tokens": 7, "completion_tokens": 2},
            }
        )


class HttpProviderTests(unittest.TestCase):
    def test_requires_environment_configuration_before_network(self):
        opener = FakeOpener()
        with self.assertRaises(ValueError):
            OpenAICompatibleProvider.from_environment({}, opener=opener)
        self.assertEqual(opener.calls, [])

    def test_uses_injected_transport_and_reports_provider_usage(self):
        opener = FakeOpener()
        environment = {
            "CAI_HTTP_BASE_URL": "http://localhost:11434/v1",
            "CAI_HTTP_MODEL": "local-model",
            "CAI_HTTP_TIMEOUT_SECONDS": "4",
        }
        provider = OpenAICompatibleProvider.from_environment(
            environment, opener=opener
        )

        response = provider.infer(InferenceRequest("r1", "hello", 5))

        self.assertEqual(response.input_tokens, 7)
        self.assertEqual(response.output_tokens, 2)
        request, timeout = opener.calls[0]
        self.assertEqual(request.full_url, "http://localhost:11434/v1/chat/completions")
        self.assertEqual(timeout, 4.0)
        self.assertNotIn("Authorization", request.headers)

    def test_http_pricing_is_explicit_and_environment_only(self):
        with self.assertRaises(ValueError):
            http_pricing_from_environment({}, "http-provider")

        pricing = http_pricing_from_environment(
            {
                "CAI_HTTP_INPUT_PRICE_PER_1M_USD": "0.15",
                "CAI_HTTP_OUTPUT_PRICE_PER_1M_USD": "0.60",
                "CAI_HTTP_PRICE_SOURCE": "provider page 2026-07-21",
            },
            "http-provider",
        )
        self.assertEqual(str(pricing.input_per_million_tokens_usd), "0.15")
        self.assertEqual(pricing.source, "provider page 2026-07-21")


if __name__ == "__main__":
    unittest.main()
