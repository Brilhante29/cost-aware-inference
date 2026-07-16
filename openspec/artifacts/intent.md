# Intent: cost-aware-inference

## Measurable Claim

Cost-aware inference comparator that reports local vs API token cost and latency side by side without paid credentials.

## Problem

Closes the platform loop by comparing quality decisions against cost and latency tradeoffs.

## In Scope

- Use the selected component pack: `ai-evaluation-retrieval`.
- Keep the project under the AI Evaluation and Retrieval Systems program.
- Preserve the benchmark contract: `api_cost_per_1k_tokens_usd` in `benchmarks/results/cost-aware-baseline.json`.
- Keep the default path local-first and reproducible.

## Out Of Scope

- Paid credentials for the default demo.
- External infrastructure that is not required by the benchmark.
- Replacing local portfolio skills with external components silently.

## Default Demo Path

- Status: benchmarked
- Runtime: python-cli
- Benchmark command: `python -m cost_aware_inference benchmark --output benchmarks/results/cost-aware-baseline.json`

## Public Proof

- Benchmark: api_cost_per_1k_tokens_usd = 0.00 usd
- Result path: `benchmarks/results/cost-aware-baseline.json`
