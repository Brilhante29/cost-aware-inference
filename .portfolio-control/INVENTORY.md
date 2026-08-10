# Portfolio Control: #30 cost-aware-inference

## Identity

- **Program:** AI Evaluation and Retrieval Systems
- **Status:** published
- **Proves:** measured local LLM HTTP latency/usage versus an explicitly non-LLM reference with separate pricing assumptions
- **Primary benchmark:** `observed_p95_latency_ms = 1011.015`

## Evidence Map

| Evidence | Location | State |
|---|---|---|
| Specification | `sdd/spec.md` | complete |
| Architecture decision | `sdd/architecture-decision.md` | complete |
| Benchmark plan | `sdd/benchmark-plan.md` | complete |
| Raw result | `benchmarks/results/cost-aware-baseline.json` | 60 measured calls |
| V2 publication | `benchmarks/publication/cost-aware-baseline-v2.json` | provenance validated |
| Model identity | `benchmarks/config/cost-aware-baseline-v2.json` | name and digest pinned |
| OpenSpec verification | `openspec/artifacts/verification.md` | complete |
| Reuse review | `sdd/reuse-improvement-review.md` | complete |

This file is the project-level inventory. Update it whenever a new proof artifact, reusable component, or architectural decision appears.
