"""Base integration provider contract.

Every external API integration must subclass BaseIntegrationProvider.
Key design rules:
- API keys read from env at call-time (never cached at import time).
- health_check() must never raise — always return (bool, str).
- All fetch methods return [] / {} on error; log internally.
- No hardcoded API keys anywhere.
"""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class IntegrationConfig:
    """Immutable config declared once at the class level of each provider."""

    name:          str
    slug:          str                  # short identifier, e.g. "youtube"
    category:      str = "general"      # ai | trends | video | search | audio | news
    description:   str = ""
    api_key_env:   str = ""             # env var name — empty means no key needed
    requires_key:  bool = True
    base_url:      str = ""
    timeout:       int = 30
    retry_count:   int = 3
    cache_ttl:     int = 3600           # seconds
    docs_url:      str = ""
    extra:         dict = field(default_factory=dict)


class BaseIntegrationProvider(ABC):
    """Abstract base for all external integration providers."""

    CONFIG: IntegrationConfig  # must be declared by every subclass

    def __init__(self, config: IntegrationConfig) -> None:
        self.config = config

    # ── key access ──────────────────────────────────────────────────

    @property
    def api_key(self) -> str | None:
        if not self.config.api_key_env:
            return None
        return os.getenv(self.config.api_key_env) or None

    @property
    def is_configured(self) -> bool:
        if not self.config.requires_key:
            return True
        return bool(self.api_key)

    # ── abstract interface ───────────────────────────────────────────

    @abstractmethod
    async def health_check(self) -> tuple[bool, str]:
        """Return (healthy, human-readable message). Never raises."""
        ...

    # ── optional overrides ───────────────────────────────────────────

    async def search(self, query: str, **kwargs) -> list[dict]:
        """Generic search — override for searchable providers."""
        return []

    async def get_data(self, **kwargs) -> dict:
        """Generic data fetch — override per provider."""
        return {}

    # ── helpers ─────────────────────────────────────────────────────

    @property
    def status_emoji(self) -> str:
        return "🟢" if self.is_configured else "🔴"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} slug={self.config.slug!r}>"
