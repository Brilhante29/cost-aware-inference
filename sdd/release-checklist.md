# Release Checklist

- [x] README opens with measured numbers and explicit limitations.
- [x] Seven tests cover application, local adapter, HTTP adapter, pricing, and fail-closed configuration.
- [x] `repeat=5` is distinct from `measured_iterations=15`.
- [x] Measured latency/usage and estimated cost are structurally separated.
- [x] Docker is version-and-digest pinned and runs offline as non-root.
- [x] Publication producer, config, schema, lock, and validator exist.
- [ ] Clean source commit is pushed and its CI is green.
- [ ] V2 evidence is generated from that exact source commit and image.
- [ ] Publication commit is pushed and its exact-head CI is green.