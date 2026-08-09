# Verification: cost-aware-inference

## Verified Evidence

- Seven unit tests pass; HTTP tests inject transport and open no network connection.
- `tools/validate-runtime.py` validates the committed baseline and a fresh local reproduction.
- `tools/validate-project.ps1 -SkipDocker` passes the runtime and publication gates.
- Workload accounting is explicit: 3 prompts x 5 repetitions = 15 measured calls.
- Current host baseline: p95 `0.1136 ms`, 465 input tokens, 175 output tokens, 640 total tokens.
- Measured latency/usage and estimated tariff cost are separate structures.
- Python 3.12.13 Docker base is pinned by version and digest and runs as UID 10001.
- V2 config, producer, schema, exact lock, Codex skill, Claude skill, and project validator are present.

## Claim Check

- The local provider is deterministic extractive processing, not an LLM.
- `US$ 0.00` means zero configured marginal token tariff, not zero infrastructure cost.
- No provider comparison is claimed because the committed baseline executes one provider.
- A real HTTP endpoint remains opt-in through explicit `CAI_HTTP_*` configuration.
- V2 was generated from green source SHA `a5b7e53b9992250771e4c8be7f8a616b8ef41bda`.

## Publication Evidence

- Source commit `a5b7e53b9992250771e4c8be7f8a616b8ef41bda`; GitHub Actions run `31339203270` passed.
- Docker-derived V1 and provenance-bound V2 result are committed; image digest is `sha256:05ac538158ae840c54fbc21b71f77826712e75ac5a2560bb6f04fc0256ba00f1`.
- The publication commit must pass the same exact-head GitHub Actions workflow before release is reported complete.