# Intent: cost-aware-inference

## Measurable Claim

Execute provider work and report observed p95 latency plus token usage, while keeping monetary cost as an estimate derived from an explicit pricing source.

## Problem

Inference decisions are unreliable when teams compare declared latencies and prices without running the same requests or separating observations from assumptions.

## In Scope

- Deterministic offline provider with real text processing.
- Replaceable provider port.
- Optional OpenAI-compatible HTTP adapter configured from environment variables.
- Per-request latency, token usage, and output identity.
- Separate price assumptions and estimated cost.
- Shared portfolio benchmark root contract.

## Out Of Scope

- LLM quality claims for the local baseline.
- Paid or networked calls on the default path.
- Full hardware total cost of ownership.
- A winner claim without a same-run provider comparison.

## Default Demo Path

- Status: benchmarked
- Runtime: Python CLI or Docker
- Benchmark command: `python -m cost_aware_inference benchmark --providers local --repeat 5 --output benchmarks/results/cost-aware-baseline.json`

## Public Proof

- `observed_p95_latency_ms = 1.2246 ms`
- 15 local calls and 640 observed tokens.
- Result: `benchmarks/results/cost-aware-baseline.json`.
