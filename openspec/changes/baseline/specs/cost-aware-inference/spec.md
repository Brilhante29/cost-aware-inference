# cost-aware-inference Specification Delta

## ADDED Requirements

### Requirement: Observed provider execution

The system SHALL execute each configured provider and measure wall-clock duration per request.

#### Scenario: Offline baseline

- GIVEN committed prompt fixtures and the local adapter
- WHEN the benchmark runs five repetitions
- THEN 15 provider calls are executed
- AND each sample records latency, input/output tokens, and output SHA-256.

### Requirement: Measured and assumed data remain separate

The system SHALL calculate estimated cost only after observing token usage and SHALL retain price source and scope.

#### Scenario: Local price assumption

- GIVEN a zero marginal token tariff
- WHEN local usage is measured
- THEN estimated token charge is zero
- AND the result states that hardware, electricity, and operations are excluded.

### Requirement: Replaceable provider

The application SHALL depend on `InferenceProvider`, not a concrete transport.

#### Scenario: Optional HTTP provider

- GIVEN URL, model, prices, source, and optional key in environment variables
- WHEN `--providers local,http` runs
- THEN both adapters emit the same sample contract
- AND no secret is serialized.

### Requirement: Offline test suite

The HTTP adapter SHALL accept an injected transport.

#### Scenario: Unit test

- GIVEN a fake opener
- WHEN the HTTP adapter is exercised
- THEN request shape and usage parsing are verified without network access.
