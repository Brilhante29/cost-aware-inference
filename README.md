# #30 cost-aware-inference

**Status:** scaffold

**Proves:** custo e latencia local vs API.

**Benchmark target:** cost_per_1k_tokens, latency_ms.

**Stack:** python, fastapi, litellm, ollama, duckdb, docker.

## Next milestone

Implement the smallest Docker-runnable version and produce the first JSON benchmark under enchmarks/results/.

## Run

`ash
docker build -t cost-aware-inference .
docker run --rm cost-aware-inference
`

## Benchmark

`ash
docker run --rm cost-aware-inference benchmark
`

| Metric | Value | Unit |
|---|---:|---|
| cost_per_1k_tokens, latency_ms | pending | pending |

## Architecture

Defined in sdd/spec.md before implementation.

## References

See REFERENCES.md.