# Architecture Record: cost-aware-inference

## Decision

- Architecture: `hexagonal`
- Stack profile: `python`
- API style: `cli-first`
- Messaging: `none`
- Runtime: `python-cli` and Docker

## Reason

Execution providers and pricing sources vary independently. Benchmark policy depends on a narrow port and domain values; local text processing and HTTP stay in adapters.

## Boundaries

- Domain: request, response, and pricing values.
- Application: measured benchmark orchestration.
- Port: provider execution contract.
- Adapters: local algorithm and optional HTTP transport.
- Interface: CLI composition and JSON output.

## Principle Check

- SRP separates execution, timing, pricing, transport, and serialization.
- OCP/LSP permit provider substitution under the same usage contract.
- ISP keeps the port minimal.
- DIP prevents provider infrastructure from entering application policy.
- KISS/YAGNI avoid SDKs, frameworks, and services that add no evidence.
