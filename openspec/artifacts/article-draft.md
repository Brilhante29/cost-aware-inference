# #30 cost-aware-inference: 1.2246 ms observed local p95

The first version looked convincing but only multiplied token totals by declared latency and price constants. It did not execute inference. The corrected benchmark now runs a deterministic extractive provider 15 times, measures every call, records 640 tokens, and emits output hashes.

Cost is intentionally a different field. The committed `US$ 0` assumption means no marginal API token tariff for the local adapter; it excludes hardware, electricity, and operations. A real OpenAI-compatible endpoint can be added through environment variables and measured under the same provider port.

The architecture moved from a future promise to a visible hexagonal boundary: application policy depends on `InferenceProvider`; local processing and HTTP are adapters. The default Docker path remains offline and credential-free.
