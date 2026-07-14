# Spec: 30 - cost-aware-inference

## Claim

Cost-aware inference comparator that reports local vs API token cost and latency side by side without paid credentials.

## Acceptance Criteria

- Runs locally with `python -m cost_aware_inference benchmark --output benchmarks/results/cost-aware-baseline.json`.
- Runs in Docker with no paid secret.
- Writes benchmark JSON under `benchmarks/results/`.
- Keeps domain/evaluation logic independent from CLI and future providers.
