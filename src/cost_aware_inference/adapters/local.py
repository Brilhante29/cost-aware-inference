from __future__ import annotations

import math
import re
from collections import Counter

from ..domain import InferenceRequest, InferenceResponse

TOKEN_PATTERN = re.compile(r"[\w'-]+|[^\w\s]", re.UNICODE)
WORD_PATTERN = re.compile(r"[\w'-]+", re.UNICODE)
SENTENCE_PATTERN = re.compile(r"(?<=[.!?])\s+")
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "in", "is", "it", "of", "on", "or", "that", "the", "to", "with",
}


def count_tokens(text: str) -> int:
    """Count deterministic regex tokens; this is not a model tokenizer."""
    return len(TOKEN_PATTERN.findall(text))


class LocalExtractiveProvider:
    provider_id = "local-extractive-v1"
    mode = "local"
    implementation = "deterministic-frequency-weighted-extractive-baseline"

    def infer(self, request: InferenceRequest) -> InferenceResponse:
        sentences = [
            sentence.strip()
            for sentence in SENTENCE_PATTERN.split(request.prompt)
            if sentence.strip()
        ]
        words = [word.lower() for word in WORD_PATTERN.findall(request.prompt)]
        frequencies = Counter(word for word in words if word not in STOP_WORDS)

        def score(item: tuple[int, str]) -> tuple[float, int]:
            index, sentence = item
            sentence_words = [word.lower() for word in WORD_PATTERN.findall(sentence)]
            weighted = sum(frequencies[word] for word in sentence_words)
            return weighted / math.sqrt(max(len(sentence_words), 1)), -index

        selected = max(enumerate(sentences), key=score)[1]
        output_tokens = TOKEN_PATTERN.findall(selected)[: request.max_output_tokens]
        output = " ".join(output_tokens)
        return InferenceResponse(
            text=output,
            input_tokens=count_tokens(request.prompt),
            output_tokens=len(output_tokens),
        )
