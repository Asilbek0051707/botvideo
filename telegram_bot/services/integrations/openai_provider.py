"""OpenAI integration provider.

Env var: OPENAI_API_KEY
Uses the official openai SDK (already in dependencies).
"""
from __future__ import annotations

from .base import BaseIntegrationProvider, IntegrationConfig


class OpenAIProvider(BaseIntegrationProvider):

    CONFIG = IntegrationConfig(
        name="OpenAI",
        slug="openai",
        category="ai",
        description="GPT-4o, GPT-4, GPT-3.5-turbo text generation",
        api_key_env="OPENAI_API_KEY",
        base_url="https://api.openai.com/v1",
        cache_ttl=300,
        docs_url="https://platform.openai.com/docs",
    )

    # Default model — can be overridden via OPENAI_MODEL env var
    DEFAULT_MODEL = "gpt-4o-mini"

    def __init__(self) -> None:
        super().__init__(self.CONFIG)

    def _client(self):
        try:
            from openai import AsyncOpenAI
            return AsyncOpenAI(api_key=self.api_key)
        except ImportError:
            return None

    async def health_check(self) -> tuple[bool, str]:
        if not self.is_configured:
            return False, "Not configured: OPENAI_API_KEY not set"
        client = self._client()
        if client is None:
            return False, "openai package not installed"
        try:
            resp = await client.models.list()
            count = len(list(resp))
            return True, f"OK — {count} model(s) available"
        except Exception as exc:
            return False, str(exc)

    async def complete(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> str:
        if not self.is_configured:
            return ""
        import os
        chosen_model = model or os.getenv("OPENAI_MODEL", self.DEFAULT_MODEL)
        client = self._client()
        if client is None:
            return ""
        try:
            resp = await client.chat.completions.create(
                model=chosen_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return resp.choices[0].message.content or ""
        except Exception:
            return ""

    async def get_data(self, **kwargs) -> dict:
        prompt = kwargs.get("prompt", "")
        if not prompt:
            return {}
        text = await self.complete(prompt)
        return {"result": text}
