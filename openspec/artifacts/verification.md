# Verification: cost-aware-inference

Date: 2026-07-21

## Verified Evidence

- Unit tests: 7 passed; HTTP tests used an injected fake opener and no network.
- Shared baseline contract: passed for `benchmarks/results/cost-aware-baseline.json`.
- Reproduced local result: passed inside `tools/validate-runtime.py`.
- Project validator: `tools/validate-project.ps1 -SkipDocker` passed.
- OpenSpec: `openspec validate --all --strict --no-interactive` passed 1/1 changes.
- Docker build: passed; final local image ID starts with `sha256:f8777c5c`.
- Optimized Docker build: 16.37 seconds after removing an unnecessary 113.1-second package-install layer.
- Docker execution: passed as non-root and its stdout passed `tools/validate-benchmark.py`.
- Workload: 3 prompts x 5 repetitions = 15 samples.
- Committed baseline: p95 `1.2246 ms`, 465 input tokens, 175 output tokens.

## Claim Check

- Latency and usage are observed.
- Cost is estimated from a separate documented assumption.
- The local provider is described as deterministic extractive processing, not an LLM.
- No API comparison is claimed because no external endpoint was called.
- Status is `benchmarked`, not `published`.

## Not Verified

- A real HTTP/OpenAI-compatible endpoint was intentionally not called.
- GitHub Actions has not run for this local commit.

## Remaining Risk

The Python base image is referenced by a mutable tag in the Dockerfile, although the local build resolved a digest. Pinning policy should be handled consistently by the portfolio reuse kit rather than invented in one repository.
