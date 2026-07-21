# Technical Decision

- Runtime: Python 3.10+ CLI, tested with the standard library only.
- Provider port: structural `typing.Protocol` with one synchronous `infer` method.
- Local adapter: deterministic frequency-weighted extractive sentence selection.
- Tokenizer: regex-based and explicitly not a model tokenizer.
- HTTP adapter: OpenAI-compatible `/chat/completions` via `urllib.request`.
- HTTP configuration: `CAI_HTTP_*` environment variables; no endpoint, model, key, or price default except a non-secret timeout and provider label.
- Network tests: injected fake opener; no socket or remote service.
- Clock tests: injected nanosecond clock.
- Result: shared root benchmark fields plus measured and assumed provider sections.
- Privacy: only output SHA-256 is persisted, not generated response text.
- Docker: non-root local benchmark with no secret requirement.

## Failure Policy

Missing HTTP configuration, missing provider usage, invalid pricing, provider/pricing ID mismatch, empty workloads, and malformed result contracts fail closed.
