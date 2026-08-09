# Technical Decision

- Runtime: Python 3.10+ CLI; publication uses Python 3.12.13 pinned by image version and digest.
- Core dependencies: Python standard library only.
- Validation dependencies: exact lock with JSON Schema and build backend tooling.
- Architecture: hexagonal application around a structural `InferenceProvider` port.
- Local adapter: deterministic frequency-weighted extractive sentence selection, explicitly not an LLM.
- Tokenizer: documented regex tokens for the local adapter, never presented as model tokens.
- HTTP adapter: OpenAI-compatible `/chat/completions` via `urllib.request`.
- HTTP configuration: `CAI_HTTP_*` environment variables; no URL, model, key, or tariff fallback.
- Network tests: injected opener; no socket or remote service.
- Clock tests: injected nanosecond clock.
- Work accounting: five repetitions over three prompts produce 15 measured iterations.
- Cost policy: measured usage and estimated tariff cost remain separate structures.
- Privacy: persist output SHA-256, not response text or credentials.
- Publication: V1 measurement plus schema-validated V2 Git, image, data, config, and lock provenance.
- Docker: non-root UID 10001 and network-disabled publication execution.

## Failure Policy

Missing HTTP configuration, missing provider usage, invalid pricing, provider/pricing ID mismatch, empty workloads, malformed contracts, stale digests, and claims of comparison from a single provider fail closed.