# Verification: cost-aware-inference

## Verified Evidence

- Eight unit tests pass; HTTP tests inject transport and open no network connection.
- `tools/validate-runtime.py` validates the committed baseline and a fresh local reproduction.
- `tools/validate-project.ps1 -SkipDocker` passes the runtime and publication gates.
- Workload accounting is explicit: 3 prompts x 10 repetitions x 2 providers = 60 measured calls after 2 excluded warm-ups.
- Pinned Qwen/Ollama HTTP: p95 `1011.015 ms`, 1820 input tokens, 840 output tokens.
- In-process reference: p95 `0.240 ms`; measured p95 ratio `4213.51x`.
- Measured latency/usage and estimated tariff cost are separate structures.
- Python 3.12.13 Docker base is pinned by version and digest and runs as UID 10001.
- V2 config, producer, schema, exact lock, Codex skill, Claude skill, and project validator are present.

## Claim Check

- The local provider is deterministic extractive processing, not an LLM.
- `US$ 0.00` means zero configured marginal token tariff, not zero infrastructure cost.
- The comparison is local Ollama HTTP versus a non-LLM reference, not local versus cloud.
- The model name and full digest are committed in benchmark config and evidence.
- V2 was generated from clean source SHA `13fb81510b00cf2d7a0d1c522edbc548b39fc91f`.

## Publication Evidence

- Docker-derived V1 and provenance-bound V2 result are committed; image digest is `sha256:6ec2bdb92a439b28d57e222d4a2c9c7e591412a0b7b4d4e0456463fa2dd01c5f`.
- The publication commit must pass the same exact-head GitHub Actions workflow before release is reported complete.
