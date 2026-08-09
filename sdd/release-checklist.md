# Release Checklist

- [x] README opens with measured numbers and explicit limitations.
- [x] Seven tests cover application, local adapter, HTTP adapter, pricing, and fail-closed configuration.
- [x] `repeat=5` is distinct from `measured_iterations=15`.
- [x] Measured latency/usage and estimated cost are structurally separated.
- [x] Docker is version-and-digest pinned and runs offline as non-root.
- [x] Publication producer, config, schema, lock, and validator exist.
- [x] Clean source commit `a5b7e53b9992250771e4c8be7f8a616b8ef41bda` is pushed; CI run `31339203270` is green.
- [x] V2 evidence is generated from that exact source commit and image digest `sha256:05ac538158ae840c54fbc21b71f77826712e75ac5a2560bb6f04fc0256ba00f1`.
- [x] Publication commits use the same exact-head CI gate; release is reported complete only after that final run is green.