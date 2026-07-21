# Spec: 30 - cost-aware-inference

## Claim

Execute real provider work, record observed latency and token usage per request, then estimate monetary cost from explicit pricing assumptions. The default provider is a deterministic extractive text baseline, not an LLM; a real OpenAI-compatible endpoint is optional.

## Acceptance Criteria

- The default benchmark runs offline and without credentials.
- `InferenceProvider` can be replaced without changing benchmark policy.
- The local adapter transforms prompt text and reports tokens from a documented deterministic tokenizer.
- The HTTP adapter reads URL, model, optional key, timeout, and prices only from environment variables.
- Tests never open a network connection.
- Runtime observations and pricing assumptions occupy separate result fields.
- The result satisfies the shared benchmark fields and includes per-provider samples.
- Docker runs the same local benchmark as a non-root user.
- Project status remains `benchmarked` until publication and remote CI are verified.

## Non-Goals

- Claiming LLM quality for the local extractive baseline.
- Claiming that local compute is free.
- Publishing a local-versus-API winner without executing both providers on the same workload.
- Persisting endpoint credentials or response text in benchmark artifacts.
