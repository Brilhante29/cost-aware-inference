from __future__ import annotations

import json
from collections.abc import Mapping
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .domain import PricingAssumption


def _decimal(value: object, field: str) -> Decimal:
    try:
        return Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"{field} must be a decimal number") from exc


def load_pricing(path: str | Path, provider_id: str) -> PricingAssumption:
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    try:
        row = document[provider_id]
    except KeyError as exc:
        raise ValueError(f"pricing assumption not found for {provider_id}") from exc
    return PricingAssumption(
        provider_id=provider_id,
        currency=row["currency"],
        input_per_million_tokens_usd=_decimal(
            row["input_per_million_tokens_usd"],
            "input_per_million_tokens_usd",
        ),
        output_per_million_tokens_usd=_decimal(
            row["output_per_million_tokens_usd"],
            "output_per_million_tokens_usd",
        ),
        source=row["source"],
        scope=row["scope"],
    )


def http_pricing_from_environment(
    environment: Mapping[str, str], provider_id: str
) -> PricingAssumption:
    required = (
        "CAI_HTTP_INPUT_PRICE_PER_1M_USD",
        "CAI_HTTP_OUTPUT_PRICE_PER_1M_USD",
        "CAI_HTTP_PRICE_SOURCE",
    )
    missing = [name for name in required if not environment.get(name)]
    if missing:
        raise ValueError(
            "HTTP pricing requires environment variables: " + ", ".join(missing)
        )
    return PricingAssumption(
        provider_id=provider_id,
        currency="USD",
        input_per_million_tokens_usd=_decimal(
            environment["CAI_HTTP_INPUT_PRICE_PER_1M_USD"],
            "CAI_HTTP_INPUT_PRICE_PER_1M_USD",
        ),
        output_per_million_tokens_usd=_decimal(
            environment["CAI_HTTP_OUTPUT_PRICE_PER_1M_USD"],
            "CAI_HTTP_OUTPUT_PRICE_PER_1M_USD",
        ),
        source=environment["CAI_HTTP_PRICE_SOURCE"],
        scope="Configured API token charges only; excludes network and host costs.",
    )
