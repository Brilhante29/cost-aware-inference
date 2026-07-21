# Tasks: cost-aware-inference

## Planning

- [x] Replace the declared-number calculator with an honest execution claim.
- [x] Record architecture, claim boundaries, and rejected alternatives.
- [x] Keep project-specific prompts and prices outside the reuse kit.

## Implementation

- [x] Implement provider port and deterministic local adapter.
- [x] Implement optional environment-only HTTP adapter.
- [x] Separate measured runtime/usage from pricing assumptions.
- [x] Emit shared root fields and provider-level samples.
- [x] Add offline tests, result validation, Docker, README, SDD, and OpenSpec evidence.

## Local Verification

- [x] Seven unit tests pass.
- [x] Committed and reproduced results pass the benchmark validator.
- [x] Project validator passes.
- [x] OpenSpec strict validation passes.
- [x] Docker builds, runs as non-root, and emits a valid result.

## Publication

- [ ] Push the commit and observe GitHub Actions on its remote SHA.
- [ ] Record publication evidence before changing `status` from `benchmarked`.
- [ ] Run a real HTTP provider comparison only with user-supplied environment configuration.
