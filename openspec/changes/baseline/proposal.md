# Change Proposal: honest pluggable inference benchmark

Project: `cost-aware-inference` (#30)

## Intent

Replace the declared-number calculator with executed provider work, observed per-request measurements, and separately sourced cost assumptions.

## Scope

- In scope: provider port, deterministic local adapter, optional environment-configured HTTP adapter, samples, pricing separation, tests, Docker, and evidence.
- Out of scope: paid default calls, model-quality claims, provider SDKs, UI, and full infrastructure cost modeling.

## Portfolio Impact

This establishes an honest measured-versus-assumed contract for the AI Evaluation and Retrieval Systems program. The reusable shape is recorded as kit backlog, while prompts and prices remain project-owned.

## Acceptance Signal

The committed result satisfies the shared benchmark fields, includes 15 local samples, and passes the project contract validator without credentials or network.
