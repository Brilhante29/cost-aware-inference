# Change Design: honest pluggable inference benchmark

## Decision

- Architecture: hexagonal.
- Stack: standard-library Python.
- Default adapter: deterministic extractive text processing.
- Optional adapter: OpenAI-compatible HTTP from `CAI_HTTP_*` variables.
- Evidence: observed runtime/usage plus separate pricing assumptions.

## Boundaries

- Domain and application define policy.
- `InferenceProvider` defines replaceable execution.
- Adapters implement local and HTTP mechanisms.
- CLI composes configuration and writes JSON.

## Engineering Rules

- No secrets, URLs, external model names, or external prices in defaults.
- HTTP usage must be provider-reported; no silent token approximation.
- Tests inject transport and clock.
- Output stores response hashes, not response text.
- A provider comparison claim requires providers in the same run.

## Rejected Alternatives

- Fixture latency and token constants: no execution evidence.
- Mock API provider in the public baseline: misleading comparison.
- SDK dependency: unnecessary coupling for a standard HTTP boundary.
