"""LLM client abstraction (Anthropic / OpenAI) with tolerant JSON parsing.

`mock` mode is handled inside each agent (deterministic local generation), so
this module only wires real providers.
"""

from __future__ import annotations

import json
import re
from typing import Protocol

from tenacity import retry, stop_after_attempt, wait_exponential

from factory.core.config import settings
from factory.core.logging import get_logger

log = get_logger(__name__)


class LLM(Protocol):
    def generate(self, system: str, prompt: str, *, max_tokens: int = 1500, temperature: float = 0.8) -> str: ...


class AnthropicLLM:
    def __init__(self) -> None:
        from anthropic import Anthropic

        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def generate(self, system: str, prompt: str, *, max_tokens: int = 1500, temperature: float = 0.8) -> str:
        resp = self.client.messages.create(
            model=self.model,
            system=system,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in resp.content if block.type == "text")


class OpenAILLM:
    def __init__(self) -> None:
        from openai import OpenAI

        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def generate(self, system: str, prompt: str, *, max_tokens: int = 1500, temperature: float = 0.8) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content or ""


def get_llm() -> LLM | None:
    """Return a configured client, or None when running in mock mode / missing keys."""
    provider = settings.llm_provider
    try:
        if provider == "anthropic" and settings.anthropic_api_key:
            return AnthropicLLM()
        if provider == "openai" and settings.openai_api_key:
            return OpenAILLM()
    except Exception as exc:  # missing SDK, bad key, etc.
        log.warning("llm.init_failed", provider=provider, error=str(exc))
    return None


_JSON_RE = re.compile(r"\{.*\}|\[.*\]", re.DOTALL)


def parse_json(text: str) -> dict | list:
    """Extract the first JSON object/array from a model response."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = _JSON_RE.search(text)
        if match:
            return json.loads(match.group(0))
        raise
