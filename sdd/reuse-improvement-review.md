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
| AI evaluation repos need a shared result validator that distinguishes measured values from assumptions. | `backlog` | `contracts`, `validation` | Promote provider samples, price source/scope, output identity, and no-secret checks after sibling repos confirm the shape. | recorded |
| External adapters need an offline test transport and environment-only secret policy. | `backlog` | `skills`, `templates` | Add an adapter testing recipe to the reuse kit. | recorded |
| Prompt and pricing content is project-specific. | `reject` | `templates` | Keep fixtures and assumptions in this repository. | done |

## Patch Now Decisions

- The repository now includes a strict project validator; the shared kit is not changed from this isolated worktree.

## Backlog Decisions

- Generalize the provider-sample contract only after `llm-agent-eval` or another sibling proves the same shape.
- Add a reusable no-network adapter test recipe to the kit.

## Rejected Improvements

- Do not move prompts, provider identifiers, or price values into the kit.

## Final Gate

- [x] Reusable improvements were patched or recorded.
- [x] Project-specific implementation was not moved into the kit.
- [x] Validation reflects measured-versus-assumed evidence and offline adapter tests.
