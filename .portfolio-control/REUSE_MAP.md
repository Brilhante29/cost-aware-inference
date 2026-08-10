# Reuse Map: #30 cost-aware-inference

## Kit Inputs

| Concern | Source of truth | Project use |
|---|---|---|
| Agent skills | `.codex/skills/` and `.claude/skills/` | select by problem and language |
| Architecture | `decision-brain/` | record the chosen shape in SDD |
| Stack and libraries | `.portfolio/decision-brain/` | justify against the benchmark |
| Local-first cloud | `.portfolio/decision-brain/cloud-matrix.yaml` | keep provider ports replaceable |
| API style | `decision-brain/api-style-matrix.yaml` | REST, GraphQL, gRPC, or events by need |
| Messaging | `decision-brain/messaging-matrix.yaml` | Kafka/RabbitMQ only with a measured reason |
| Benchmark contract | `contracts/benchmark-result.schema.json` | emit machine-readable evidence |

## Project Delta

List only what this project adds to the kit. If a pattern will be useful in another repository, patch the kit and link the change here instead of hiding it in project code.

| Delta | Why it is project-specific or reusable | Action |
|---|---|---|
| provider evidence envelope | reusable across LLM producers | promote to reuse-kit guidance |
| interleaved multi-provider measurement | reusable benchmark policy | promote to benchmark skill |
| model/digest and pricing values | workload-specific | keep local |

## Coupling Rule

Domain code must not depend on infrastructure adapters, providers, brokers, HTTP frameworks, or model vendors. Dependencies point inward through stable ports. Reuse is accepted only when it reduces duplication without making the problem less clear.
