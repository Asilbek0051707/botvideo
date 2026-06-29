"""Anthropic Claude integration provider.

Env var: ANTHROPIC_API_KEY
Uses the official anthropic SDK (already in dependencies).
"""
from __future__ import annotations

import os

from .base import BaseIntegrationProvider, IntegrationConfig


class AnthropicProvider(BaseIntegrationProvider):

    CONFIG = IntegrationConfig(
        name="Anthropic Claude",
        slug="anthropic",
        category="ai",
        description="Claude Sonnet, Haiku, Opus text generation",
        api_key_env="ANTHROPIC_API_KEY",
        base_url="https://api.anthropic.com",
        cache_ttl=300,
        docs_url="https://docs.anthropic.com",
    )

    DEFAULT_MODEL = "claude-haiku-4-5-20251001"

    def __init__(self) -> None:
        super().__init__(self.CONFIG)

    def _client(self):
        try:
            import anthropic
            return anthropic.AsyncAnthropic(api_key=self.api_key)
        except ImportError:
            return None

    async def health_check(self) -> tuple[bool, str]:
        if not self.is_configured:
            return False, "Not configured: ANTHROPIC_API_KEY not set"
        client = self._client()
        if client is None:
            return False, "anthropic package not installed"
        try:
            resp = await client.messages.create(
                model=self.DEFAULT_MODEL,
                max_tokens=10,
                messages=[{"role": "user", "content": "ping"}],
            )
            return True, f"OK — model={resp.model}"
        except Exception as exc:
            return False, str(exc)

    async def complete(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        system: str = "",
    ) -> str:
        if not self.is_configured:
            return ""
        client = self._client()
        if client is None:
            return ""
        chosen_model = model or os.getenv("ANTHROPIC_MODEL", self.DEFAULT_MODEL)
        kwargs: dict = dict(
            model=chosen_model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        if system:
            kwargs["system"] = system
        try:
            resp = await client.messages.create(**kwargs)
            return resp.content[0].text if resp.content else ""
        except Exception:
            return ""

    async def get_data(self, **kwargs) -> dict:
        prompt = kwargs.get("prompt", "")
        if not prompt:
            return {}
        text = await self.complete(prompt, system=kwargs.get("system", ""))
        return {"result": text}
