from __future__ import annotations

import json
import os
from collections.abc import Callable, Mapping
from typing import Any
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from ..domain import InferenceRequest, InferenceResponse

OpenUrl = Callable[[Request, float], Any]


def _open(request: Request, timeout: float) -> Any:
    return urlopen(request, timeout=timeout)


class OpenAICompatibleProvider:
    mode = "http"
    implementation = "openai-compatible-chat-completions"

    def __init__(
        self,
        *,
        provider_id: str,
        base_url: str,
        model: str,
        timeout_seconds: float,
        api_key: str | None,
        opener: OpenUrl = _open,
    ) -> None:
        parsed = urlsplit(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("CAI_HTTP_BASE_URL must be an HTTP(S) URL")
        if parsed.username or parsed.password:
            raise ValueError("credentials must not be embedded in CAI_HTTP_BASE_URL")
        if timeout_seconds <= 0:
            raise ValueError("CAI_HTTP_TIMEOUT_SECONDS must be positive")
        self.provider_id = provider_id
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.api_key = api_key
        self._opener = opener

    @classmethod
    def from_environment(
        cls,
        environment: Mapping[str, str] | None = None,
        *,
        opener: OpenUrl = _open,
    ) -> "OpenAICompatibleProvider":
        values = os.environ if environment is None else environment
        required = ("CAI_HTTP_BASE_URL", "CAI_HTTP_MODEL")
        missing = [name for name in required if not values.get(name)]
        if missing:
            raise ValueError(
                "HTTP provider requires environment variables: " + ", ".join(missing)
            )
        return cls(
            provider_id=values.get("CAI_HTTP_PROVIDER_ID", "openai-compatible-http"),
            base_url=values["CAI_HTTP_BASE_URL"],
            model=values["CAI_HTTP_MODEL"],
            timeout_seconds=float(values.get("CAI_HTTP_TIMEOUT_SECONDS", "30")),
            api_key=values.get("CAI_HTTP_API_KEY") or None,
            opener=opener,
        )

    def infer(self, request: InferenceRequest) -> InferenceResponse:
        endpoint = self.base_url
        if not endpoint.endswith("/chat/completions"):
            endpoint += "/chat/completions"
        payload = json.dumps(
            {
                "model": self.model,
                "messages": [{"role": "user", "content": request.prompt}],
                "max_tokens": request.max_output_tokens,
                "temperature": 0,
            }
        ).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        http_request = Request(endpoint, data=payload, headers=headers, method="POST")
        with self._opener(http_request, self.timeout_seconds) as response:
            document = json.loads(response.read().decode("utf-8"))

        try:
            text = document["choices"][0]["message"]["content"]
            usage = document["usage"]
            input_tokens = int(usage["prompt_tokens"])
            output_tokens = int(usage["completion_tokens"])
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise ValueError(
                "HTTP response must include chat content and exact token usage"
            ) from exc
        if not isinstance(text, str):
            raise ValueError("HTTP response content must be text")
        return InferenceResponse(
            text=text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
