# Reuse Improvement Review

Project: `30 - cost-aware-inference`

## Review Points

- [x] after scaffold
- [x] after architecture decision
- [x] after first working slice
- [x] after benchmark result
- [x] before publication
- [ ] after CI failure, if applicable

## Findings

| Finding | Classification | Kit Area | Action | Status |
|---|---|---|---|---|
| Git blob, image, fixture, config, lock, and raw-result provenance are stable across all benchmark repositories in this macro. | `patch_now` | `harness`, `skills` | Reuse the generic V2 producer, exact validation lock, and matching Codex/Claude publication skills. | done |
| Measured usage and estimated monetary cost require separate contracts. | `backlog` | `contracts`, `validation` | Add an optional provider-sample and pricing-assumption contract after macro closure. | recorded |
| External provider adapters need environment-only configuration and injected offline transport tests. | `backlog` | `skills`, `templates` | Add a no-network adapter testing recipe to the reuse kit after publication. | recorded |
| Prompts, provider IDs, tariffs, and benchmark claims are project-specific. | `reject` | `templates` | Keep domain data and exact assertions in this repository. | done |

## Patch Now Decisions

- Reused the generic execution-derived V2 producer.
- Reused the exact Python validation lock and proven CI sequence.
- Added equivalent publication skills for Codex and Claude.
- Kept cost-aware assertions in `tools/validate_publication.py`.

## Backlog Decisions

- Promote measured-versus-assumed provider evidence only after the macro is closed and the shared contract can be reviewed against all six repositories.
- Add a reusable environment-only HTTP adapter test recipe.

## Rejected Improvements

- Do not move prompts, provider identifiers, price values, or claim boundaries into the kit.

## Final Gate

- [x] Reusable improvements were patched or recorded.
- [x] Project-specific implementation was not moved into the kit.
- [x] Validation reflects measured-versus-assumed evidence, offline adapters, and publication provenance.