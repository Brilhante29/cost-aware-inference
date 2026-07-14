import argparse
import json
from pathlib import Path

def load_jsonl(path: str) -> list[dict]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]

def evaluate() -> dict:
    providers = json.loads(Path("data/fixtures/providers.json").read_text(encoding="utf-8"))
    requests = load_jsonl("data/fixtures/requests.jsonl")
    total_tokens = sum(req["input_tokens"] + req["output_tokens"] for req in requests)
    rows = []
    for provider in providers:
        cost = total_tokens / 1000 * provider["cost_per_1k_tokens_usd"]
        latency = total_tokens / 1000 * provider["latency_ms_per_1k_tokens"] / len(requests)
        rows.append({
            "provider": provider["id"],
            "mode": provider["mode"],
            "total_tokens": total_tokens,
            "cost_usd": round(cost, 6),
            "cost_per_1k_tokens_usd": provider["cost_per_1k_tokens_usd"],
            "avg_latency_ms": round(latency, 2),
        })
    api = next(row for row in rows if row["mode"] == "api")
    local = next(row for row in rows if row["mode"] == "local")
    return {"project": "cost-aware-inference", "primary_metric": "api_cost_per_1k_tokens_usd", "api_cost_per_1k_tokens_usd": api["cost_per_1k_tokens_usd"], "local_cost_per_1k_tokens_usd": local["cost_per_1k_tokens_usd"], "providers": rows}

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["benchmark"], nargs="?", default="benchmark")
    parser.add_argument("--output", default="benchmarks/results/cost-aware-baseline.json")
    args = parser.parse_args()
    result = evaluate()
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
