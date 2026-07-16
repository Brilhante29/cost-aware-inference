# #30 cost-aware-inference: api_cost_per_1k_tokens_usd = 0.00 usd

Cost-aware inference comparator that reports local vs API token cost and latency side by side without paid credentials.

This repository belongs to the AI Evaluation and Retrieval Systems program. Its job is narrow: prove the measurable claim through the selected component pack before adding unrelated infrastructure or features.

The benchmark is the proof. api_cost_per_1k_tokens_usd = 0.00 usd.  The result is stored in `benchmarks/results/cost-aware-baseline.json` and can be reproduced from the Docker/local path.

The important architecture decision is clean-architecture. The metric and benchmark use cases must stay independent from CLI, fixtures, and future providers.

The default path stays local-first. The project uses python, exposes cli-first, uses messaging mode `none`, and stores data with `fixture-files`. The dependency rule is explicit: Domain metrics and application benchmark orchestration do not import interface code.

The rejected work matters as much as the implemented work. Anything that does not improve the benchmark stays out of the first version.

Post angle: start with the number, show the architecture boundary, then explain which future adapter can be added without changing the core use cases.
