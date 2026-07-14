import unittest
from cost_aware_inference.cli import evaluate

class CostAwareTests(unittest.TestCase):
    def test_local_is_free_and_api_has_cost(self):
        result = evaluate()
        self.assertEqual(result["local_cost_per_1k_tokens_usd"], 0.0)
        self.assertGreater(result["api_cost_per_1k_tokens_usd"], 0.0)

if __name__ == "__main__":
    unittest.main()
