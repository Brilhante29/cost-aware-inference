from __future__ import annotations

import compileall
import json
import runpy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from cost_aware_inference.adapters.local import LocalExtractiveProvider
from cost_aware_inference.application import BenchmarkRunner, BenchmarkTarget, load_requests
from cost_aware_inference.pricing import load_pricing


def main() -> None:
    if not compileall.compile_dir(SRC, quiet=1):
        raise SystemExit("source compilation failed")
    if not compileall.compile_dir(ROOT / "tests", quiet=1):
        raise SystemExit("test compilation failed")

    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    if not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful():
        raise SystemExit("unit tests failed")

    validator = runpy.run_path(str(ROOT / "tools" / "validate-benchmark.py"))[
        "validate"
    ]
    baseline = json.loads(
        (ROOT / "benchmarks" / "results" / "cost-aware-baseline.json").read_text(
            encoding="utf-8"
        )
    )
    validator(baseline)

    provider = LocalExtractiveProvider()
    reproduced = BenchmarkRunner(
        [
            BenchmarkTarget(
                provider=provider,
                pricing=load_pricing(
                    ROOT / "data" / "pricing" / "providers.json",
                    provider.provider_id,
                ),
            )
        ]
    ).run(
        load_requests(ROOT / "data" / "fixtures" / "requests.jsonl"),
        repeats=2,
        command="tools/validate-runtime.py",
    )
    validator(reproduced)
    print("runtime tests and benchmark contracts passed")


if __name__ == "__main__":
    main()
