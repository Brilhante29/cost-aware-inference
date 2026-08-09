# Verification: cost-aware-inference

## Verified Evidence

- Seven unit tests pass; HTTP tests inject transport and open no network connection.
- `tools/validate-runtime.py` validates the committed baseline and a fresh local reproduction.
- `tools/validate-project.ps1 -SkipDocker` passes the runtime and publication gates.
- Workload accounting is explicit: 3 prompts x 5 repetitions = 15 measured calls.
- Current host baseline: p95 `0.1629 ms`, 465 input tokens, 175 output tokens, 640 total tokens.
- Measured latency/usage and estimated tariff cost are separate structures.
- Python 3.12.13 Docker base is pinned by version and digest and runs as UID 10001.
- V2 config, producer, schema, exact lock, Codex skill, Claude skill, and project validator are present.

## Claim Check

- The local provider is deterministic extractive processing, not an LLM.
- `US$ 0.00` means zero configured marginal token tariff, not zero infrastructure cost.
- No provider comparison is claimed because the committed baseline executes one provider.
- A real HTTP endpoint remains opt-in through explicit `CAI_HTTP_*` configuration.
- Status remains `benchmarked` until V2 is generated from a green source SHA.

## Pending Publication Evidence

- Clean source commit and exact-SHA GitHub Actions result.
- Docker-derived V1 and provenance-bound V2 result.
- Exact-head GitHub Actions result for the publication commit.