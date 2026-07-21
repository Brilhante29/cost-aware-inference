import unittest

from cost_aware_inference.adapters.local import LocalExtractiveProvider, count_tokens
from cost_aware_inference.domain import InferenceRequest


class LocalProviderTests(unittest.TestCase):
    def test_executes_deterministic_extractive_work(self):
        provider = LocalExtractiveProvider()
        request = InferenceRequest(
            request_id="local-1",
            prompt="Short sentence. Benchmark latency latency with observed work.",
            max_output_tokens=5,
        )

        first = provider.infer(request)
        second = provider.infer(request)

        self.assertEqual(first, second)
        self.assertEqual(first.input_tokens, count_tokens(request.prompt))
        self.assertGreater(first.output_tokens, 0)
        self.assertLessEqual(first.output_tokens, request.max_output_tokens)
        self.assertIn("latency", first.text.lower())

    def test_rejects_empty_prompt(self):
        with self.assertRaises(ValueError):
            InferenceRequest("empty", " ", 10)


if __name__ == "__main__":
    unittest.main()
