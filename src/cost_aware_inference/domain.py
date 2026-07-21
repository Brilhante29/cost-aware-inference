from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class InferenceRequest:
    request_id: str
    prompt: str
    max_output_tokens: int

    def __post_init__(self) -> None:
        if not self.request_id.strip():
            raise ValueError("request_id must not be blank")
        if not self.prompt.strip():
            raise ValueError("prompt must not be blank")
        if self.max_output_tokens <= 0:
            raise ValueError("max_output_tokens must be positive")


@dataclass(frozen=True)
class InferenceResponse:
    text: str
    input_tokens: int
    output_tokens: int

    def __post_init__(self) -> None:
        if self.input_tokens <= 0:
            raise ValueError("input_tokens must be positive")
        if self.output_tokens < 0:
            raise ValueError("output_tokens must not be negative")


@dataclass(frozen=True)
class PricingAssumption:
    provider_id: str
    currency: str
    input_per_million_tokens_usd: Decimal
    output_per_million_tokens_usd: Decimal
    source: str
    scope: str

    def __post_init__(self) -> None:
        if self.currency != "USD":
            raise ValueError("only USD pricing is supported")
        if self.input_per_million_tokens_usd < 0:
            raise ValueError("input price must not be negative")
        if self.output_per_million_tokens_usd < 0:
            raise ValueError("output price must not be negative")

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> Decimal:
        million = Decimal(1_000_000)
        return (
            Decimal(input_tokens) * self.input_per_million_tokens_usd / million
            + Decimal(output_tokens) * self.output_per_million_tokens_usd / million
        )
