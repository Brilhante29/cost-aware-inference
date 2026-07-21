# Architecture Decision

Decision: hexagonal, CLI-first benchmark application.

## Why

Provider execution, transport, token accounting, clocks, and price sources change independently. A narrow `InferenceProvider` port keeps the benchmark use case stable while local and HTTP mechanisms remain replaceable adapters.

## Dependency Rule

- `domain.py` owns requests, responses, and pricing values.
- `ports.py` owns the provider behavior required by the application.
- `application.py` measures calls and builds evidence from ports and domain values.
- `adapters/` owns extractive and HTTP mechanisms.
- `cli.py` composes adapters from explicit configuration.

The domain and application do not import adapter or CLI modules.

## Principles

- SRP: execution, measurement, pricing, transport, and serialization have distinct owners.
- OCP: add a provider adapter without editing benchmark policy.
- LSP: every provider returns text plus exact token usage or fails explicitly.
- ISP: the port exposes one operation and three metadata fields.
- DIP: the runner depends on `InferenceProvider`, not `urllib` or a model SDK.
- KISS/YAGNI: no provider SDK, async framework, database, queue, or web UI is added.

## Rejected Alternatives

- Declared fixture latencies: they do not measure execution.
- A provider-specific SDK in the core: it couples evaluation policy to one vendor.
- A fake API row in the default result: it presents assumptions as observations.
- Automatic token estimation for HTTP responses: it hides incompatible tokenizer behavior; provider usage is required instead.
