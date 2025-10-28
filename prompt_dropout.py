"""Utility helpers for applying dropout to system prompts."""

from __future__ import annotations

import random
from typing import Iterable


def prompt_dropout(prompt: str, dropout_rate: float) -> str:
    """Randomly drops lines from the given prompt.

    When ``dropout_rate`` is 0, the original prompt is returned unchanged. Values
    greater than 0 drop approximately ``dropout_rate`` fraction of the prompt's
    non-empty lines. An empty result falls back to the original prompt to avoid
    sending blank system prompts.
    """

    if dropout_rate <= 0:
        return prompt

    lines = prompt.splitlines()
    if not lines:
        return prompt

    kept: Iterable[str] = (
        line for line in lines if line.strip() == "" or random.random() >= dropout_rate
    )
    result = "\n".join(kept).strip()
    return result if result else prompt
