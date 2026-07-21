from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .adapters.local import LocalExtractiveProvider
from .adapters.openai_compatible import OpenAICompatibleProvider
from .application import BenchmarkRunner, BenchmarkTarget, load_requests
from .pricing import http_pricing_from_environment, load_pricing


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["benchmark"], nargs="?", default="benchmark")
    parser.add_argument("--providers", default="local")
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--requests", default="data/fixtures/requests.jsonl")
    parser.add_argument("--pricing", default="data/pricing/providers.json")
    parser.add_argument("--output", default="benchmarks/results/cost-aware-baseline.json")
    return parser


def _targets(provider_names: list[str], pricing_path: str) -> list[BenchmarkTarget]:
    targets: list[BenchmarkTarget] = []
    for name in provider_names:
        if name == "local":
            provider = LocalExtractiveProvider()
            pricing = load_pricing(pricing_path, provider.provider_id)
        elif name == "http":
            provider = OpenAICompatibleProvider.from_environment()
            pricing = http_pricing_from_environment(os.environ, provider.provider_id)
        else:
            raise ValueError(f"unknown provider alias: {name}")
        targets.append(BenchmarkTarget(provider=provider, pricing=pricing))
    return targets


def main(argv: list[str] | None = None) -> None:
    args = _parser().parse_args(argv)
    names = [name.strip() for name in args.providers.split(",") if name.strip()]
    targets = _targets(names, args.pricing)
    command = (
        "python -m cost_aware_inference benchmark "
        f"--providers {args.providers} --repeat {args.repeat} "
        f"--requests {args.requests} --pricing {args.pricing} "
        f"--output {args.output}"
    )
    result = BenchmarkRunner(targets).run(
        load_requests(args.requests),
        repeats=args.repeat,
        command=command,
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
