# Benchmark Plan

## Primary Metric

`observed_p95_latency_ms` for the first configured provider. Lower is better only for the same implementation, workload, runtime class, and comparability key.

## Default Workload

- Provider: `local-extractive-v1`.
- Requests: three committed prompts.
- Repetitions: five per prompt.
- Measured iterations: 15 provider calls.
- Concurrency: one.
- Timer: `time.perf_counter_ns()` immediately around `provider.infer()`.
- Token accounting: adapter-reported; deterministic regex tokens for the local adapter.

## Cost Method

Token usage is observed first. Input and output tariffs are loaded separately and multiplied by those totals. Local `US$ 0.00` means no marginal API token tariff in the committed assumption; hardware, electricity, and operations are excluded.

## Commands

```powershell
$env:PYTHONPATH = "src"
python -m cost_aware_inference benchmark --providers local --repeat 5 --output benchmarks/results/cost-aware-baseline.json
python tools/validate-benchmark.py benchmarks/results/cost-aware-baseline.json
```

An HTTP comparison is valid only when `local,http` execute in the same command and the endpoint returns exact usage. No comparison is inferred from pricing files or recorded constants.

## Publication

V1 records every latency, token count, output digest, and pricing scope. V2 binds that result to the source commit, exact Docker image, committed `data` tree, benchmark config, and validation lock. Publication Docker runs with `--network none`.

The default baseline proves execution, instrumentation, and cost-accounting boundaries. It does not compare model quality, an LLM, or an external API.