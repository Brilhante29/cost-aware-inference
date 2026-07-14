# Benchmark Plan

Primary metric: `api_cost_per_1k_tokens_usd`.

Command:

```powershell
python -m cost_aware_inference benchmark --output benchmarks/results/cost-aware-baseline.json
```

The benchmark uses local fixtures so the result is reproducible and does not require external credentials.
