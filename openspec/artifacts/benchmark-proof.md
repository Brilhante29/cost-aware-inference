# Benchmark Proof: cost-aware-inference

## Primary Metric

- Metric: `observed_p95_latency_ms`
- Unit: `ms`
- Result: `1.2246 ms`
- Samples: 15
- Observed usage: 465 input and 175 output tokens
- Result path: `benchmarks/results/cost-aware-baseline.json`

## Command

    python -m cost_aware_inference benchmark --providers local --repeat 5 --output benchmarks/results/cost-aware-baseline.json

## Evidence Boundary

The measured values are latency and adapter-reported token counts. `estimated_cost_usd` is derived from a separate pricing assumption. The local adapter is deterministic extractive processing, not an LLM, and the committed result contains no API comparison.

The README number comes from the committed JSON. Reruns can produce different latency on another host.
