# Agent Handoff

This file records verifiable state and decisions, not private reasoning.

## Current State

- Project: `30 - cost-aware-inference`.
- Status: `published`; provenance-bound V2 evidence was generated from the exact green source commit.
- Architecture: hexagonal `InferenceProvider` port with local and optional OpenAI-compatible HTTP adapters.
- Default path: offline, deterministic, credential-free, and explicitly not an LLM.
- Current Docker publication baseline: 15 measured calls, p95 `0.1136 ms`, 640 observed tokens.
- Cost boundary: `US$ 0.00` is the configured marginal token tariff; host cost is excluded.
- Provider comparison is unavailable because the committed baseline executes one provider.
- Source commit: `a5b7e53b9992250771e4c8be7f8a616b8ef41bda`; source CI: run `31339203270` (green).

## Contracts

- Requests: `data/fixtures/requests.jsonl`
- Pricing assumptions: `data/pricing/providers.json`
- Raw result: `benchmarks/results/cost-aware-baseline.json`
- Publication config: `benchmarks/config/cost-aware-baseline-v2.json`
- Publication evidence: `benchmarks/publication/cost-aware-baseline-v2.json`
- Generic producer: `tools/generate-publication-benchmark.py`
- Project gate: `tools/validate_publication.py`

## Continue Safely

1. Run `python -m unittest discover -s tests -v` with `PYTHONPATH=src`.
2. Run `python tools/validate-runtime.py` and `./tools/validate-project.ps1 -SkipDocker`.
3. Build and execute Docker with `--network none`.
4. Commit and push a clean source tree before generating V2.
5. Generate V2 only through the generic producer from the exact green source SHA.
6. Publish only after the final pushed SHA passes the same GitHub Actions workflow.

Do not call a real endpoint without explicit `CAI_HTTP_*` configuration. Do not describe the local extractive baseline as an LLM, zero-cost infrastructure, or a local-versus-API winner.