# Agent Handoff

Project: `30 - cost-aware-inference`

## Current State

- Status: `benchmarked`.
- Architecture: hexagonal provider port with local and optional HTTP adapters.
- Default path: offline, deterministic, credential-free.
- Baseline: 15 samples, p95 `1.2246 ms`, 640 observed tokens.
- Cost boundary: token charge is estimated from a separate assumption; host cost is excluded.
- This handoff belongs to the commit that contains it; use `git log -1 --oneline` for its SHA.

## Verified Commands

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
python tools/validate-benchmark.py benchmarks/results/cost-aware-baseline.json
pwsh -File tools/validate-project.ps1 -SkipDocker
$env:OPENSPEC_TELEMETRY = "0"
openspec validate --all --strict --no-interactive
docker build -t cost-aware-inference .
docker run --rm cost-aware-inference
```

Results on 2026-07-21: 7 tests passed, project validator passed, OpenSpec passed 1/1, Docker build passed, and container JSON passed the benchmark contract.

## Continue From Here

1. Run `git status --short --branch` and `git log -1 --oneline` before editing.
2. Read `README.md`, `sdd/spec.md`, and `openspec/artifacts/verification.md`.
3. Do not call a real HTTP endpoint unless the user supplies `CAI_HTTP_*` environment configuration.
4. Keep network disabled in tests; inject an opener instead.
5. Re-run `tools/validate-project.ps1 -SkipDocker` after code changes and Docker only when the runtime path changed.
6. Keep `status: benchmarked` until the exact commit is pushed and remote CI success is recorded.

## Remaining Work

- Push and verify GitHub Actions for the commit SHA.
- Optionally benchmark a user-configured OpenAI-compatible endpoint in the same run as local.
- Consider promoting the provider-sample contract to `portfolio-reuse-kit` only after a second repository proves the shape.

## Near-Limit Protocol

Before an agent stops because of context, quota, or time, update this file with: last successful command, current Git status, unresolved failure, files in progress, and the single next command. Never leave generated evidence unvalidated or claim publication without the remote SHA and CI result.
