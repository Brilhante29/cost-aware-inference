# Agent Handoff

This file records verifiable state and decisions, not private reasoning.

## Current State

- Project: `30 - cost-aware-inference`.
- Status: `published`; provenance-bound V2 evidence was generated from the exact green source commit.
- Architecture: hexagonal `InferenceProvider` port with local and optional OpenAI-compatible HTTP adapters.
- Default path remains offline and credential-free; the publication path uses pinned local Ollama HTTP.
- Docker publication: 60 measured calls, Qwen p95 `1011.015 ms`, reference p95 `0.240 ms`, zero failures.
- Cost boundary: `US$ 0.00` is the configured marginal token tariff; host cost is excluded.
- Comparison scope is local LLM API versus non-LLM in-process reference; no cloud claim.
- Source commit: `13fb81510b00cf2d7a0d1c522edbc548b39fc91f`; image `sha256:6ec2bdb9...`.

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
3. Build the offline image; run publication only on a private Docker network with the pinned local model.
4. Commit and push a clean source tree before generating V2.
5. Generate V2 only through the generic producer from the exact green source SHA.
6. Publish only after the final pushed SHA passes the same GitHub Actions workflow.

Do not call an endpoint without explicit `CAI_HTTP_*` configuration. Do not describe the extractive reference as an LLM, `US$ 0.00` as zero infrastructure cost, or this local comparison as cloud evidence.
