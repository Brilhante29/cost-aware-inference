# Quality Gates: #30 cost-aware-inference

Completion requires evidence, not intent.

- [x] README opens with `#30 cost-aware-inference` and the measured p95.
- [x] `project.yaml` records architecture, providers, metric, and V2 result.
- [x] SDD and OpenSpec agree with the measured local comparison.
- [x] Application code depends on `InferenceProvider`, not HTTP infrastructure.
- [x] SOLID, KISS, YAGNI, and coupling boundaries are explicit.
- [x] Eight tests cover orchestration, interleaving, metadata, HTTP, and local inference.
- [x] Docker executes as an unprivileged user from a pinned base.
- [x] Provider configuration is environment-only and secrets are never serialized.
- [x] V1 and V2 bind 60 calls, model digest, image, data, config, and lock.
- [x] README, raw result, V2, and manifest report the same primary metric.
- [x] Reuse findings are promoted or recorded.
- [x] Independent audit blockers were addressed before default-branch publication.

Each new release still requires central exact-head GitHub Actions evidence.
