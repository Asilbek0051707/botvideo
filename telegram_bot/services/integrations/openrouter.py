"""OpenRouter integration provider.

Env var: OPENROUTER_API_KEY
OpenAI-compatible REST API — no extra SDK required, uses httpx.
Provides access to 200+ models from one endpoint.
"""
from __future__ import annotations

import os

import httpx

from .base import BaseIntegrationProvider, IntegrationConfig

_BASE = "https://openrouter.ai/api/v1"


class OpenRouterProvider(BaseIntegrationProvider):

    CONFIG = IntegrationConfig(
        name="OpenRouter",
        slug="openrouter",
        category="ai",
        description="200+ AI models via OpenAI-compatible API",
        api_key_env="OPENROUTER_API_KEY",
        base_url=_BASE,
        cache_ttl=300,
        docs_url="https://openrouter.ai/docs",
    )

    DEFAULT_MODEL = "openai/gpt-4o-mini"

    def __init__(self) -> None:
        super().__init__(self.CONFIG)

    def _headers(self) -> dict:
        return {
            "Authorization":  f"Bearer {self.api_key}",
            "Content-Type":   "application/json",
            "HTTP-Referer":   "https://github.com/Asilbek0051707/botvideo",
            "X-Title":        "YouTube AI Studio Bot",
        }

    async def health_check(self) -> tuple[bool, str]:
        if not self.is_configured:
            return False, "Not configured: OPENROUTER_API_KEY not set"
        try:
            async with httpx.AsyncClient(base_url=_BASE, timeout=15) as c:
                r = await c.get("/models", headers=self._headers())
                if r.status_code == 200:
                    count = len(r.json().get("data", []))
                    return True, f"OK — {count} model(s) available"
                if r.status_code == 401:
                    return False, "API key invalid"
                return False, f"HTTP {r.status_code}"
        except Exception as exc:
            return False, str(exc)

    async def list_models(self) -> list[dict]:
        if not self.is_configured:
            return []
        try:
            async with httpx.AsyncClient(base_url=_BASE, timeout=15) as c:
                r = await c.get("/models", headers=self._headers())
                r.raise_for_status()
                return [
                    {
                        "id":           m["id"],
                        "name":         m.get("name", m["id"]),
                        "context_len":  m.get("context_length", 0),
                        "pricing":      m.get("pricing", {}),
                    }
                    for m in r.json().get("data", [])
                ]
        except Exception:
            return []

    async def complete(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> str:
        if not self.is_configured:
            return ""
        chosen = model or os.getenv("OPENROUTER_MODEL", self.DEFAULT_MODEL)
        payload = {
            "model":      chosen,
            "messages":   [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature":temperature,
        }
        try:
            async with httpx.AsyncClient(base_url=_BASE, timeout=self.config.timeout) as c:
                r = await c.post("/chat/completions", json=payload, headers=self._headers())
                r.raise_for_status()
                return r.json()["choices"][0]["message"]["content"]
        except Exception:
            return ""

    async def get_data(self, **kwargs) -> dict:
        prompt = kwargs.get("prompt", "")
        if not prompt:
            return {}
        text = await self.complete(prompt)
        return {"result": text}
