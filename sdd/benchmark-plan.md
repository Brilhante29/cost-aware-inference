# Benchmark Plan

## Primary Metric

`observed_p95_latency_ms` for the first configured provider.

## Default Workload

- Provider: `local-extractive-v1`.
- Requests: three committed text prompts.
- Repetitions: five.
- Samples: 15 provider calls.
- Timer: `time.perf_counter_ns()` immediately around `provider.infer()`.
- Token accounting: deterministic regex tokens for the local adapter.

## Cost Method

Token usage is observed first. Input and output price assumptions are loaded separately and multiplied by those totals. Local `US$ 0` means no marginal API token tariff in the checked-in assumption; hardware, electricity, and operational costs are excluded.

## Commands

```powershell
$env:PYTHONPATH = "src"
python -m cost_aware_inference benchmark --providers local --repeat 5 --output benchmarks/results/cost-aware-baseline.json
python tools/validate-benchmark.py benchmarks/results/cost-aware-baseline.json
```

An HTTP comparison is valid only when `local,http` run in the same command and the HTTP endpoint returns exact usage fields.

## Interpretation

The committed baseline demonstrates execution, instrumentation, and result-contract behavior. It does not compare model quality and it is not portable performance evidence; host and container results may differ.
