"""Google Gemini integration provider.

Env var: GEMINI_API_KEY
Uses the REST API directly via httpx — no extra SDK required.
"""
from __future__ import annotations

import os

import httpx

from .base import BaseIntegrationProvider, IntegrationConfig

_BASE = "https://generativelanguage.googleapis.com/v1beta"


class GeminiProvider(BaseIntegrationProvider):

    CONFIG = IntegrationConfig(
        name="Google Gemini",
        slug="gemini",
        category="ai",
        description="Gemini 1.5 Flash/Pro text generation",
        api_key_env="GEMINI_API_KEY",
        base_url=_BASE,
        cache_ttl=300,
        docs_url="https://ai.google.dev/docs",
    )

    DEFAULT_MODEL = "gemini-1.5-flash"

    def __init__(self) -> None:
        super().__init__(self.CONFIG)

    async def health_check(self) -> tuple[bool, str]:
        if not self.is_configured:
            return False, "Not configured: GEMINI_API_KEY not set"
        try:
            async with httpx.AsyncClient(base_url=_BASE, timeout=15) as c:
                r = await c.get(
                    "/models",
                    params={"key": self.api_key},
                )
                if r.status_code == 200:
                    count = len(r.json().get("models", []))
                    return True, f"OK — {count} model(s) available"
                if r.status_code in (400, 403):
                    return False, "API key invalid"
                return False, f"HTTP {r.status_code}"
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
        chosen = model or os.getenv("GEMINI_MODEL", self.DEFAULT_MODEL)
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature":     temperature,
            },
        }
        try:
            async with httpx.AsyncClient(base_url=_BASE, timeout=self.config.timeout) as c:
                r = await c.post(
                    f"/models/{chosen}:generateContent",
                    json=payload,
                    params={"key": self.api_key},
                )
                r.raise_for_status()
                candidates = r.json().get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    return "".join(p.get("text", "") for p in parts)
                return ""
        except Exception:
            return ""

    async def get_data(self, **kwargs) -> dict:
        prompt = kwargs.get("prompt", "")
        if not prompt:
            return {}
        text = await self.complete(prompt)
        return {"result": text}
