from __future__ import annotations

from typing import Protocol

from .domain import InferenceRequest, InferenceResponse


class InferenceProvider(Protocol):
    provider_id: str
    mode: str
    implementation: str

    def infer(self, request: InferenceRequest) -> InferenceResponse:
        """Execute one inference and report usage for the produced response."""
