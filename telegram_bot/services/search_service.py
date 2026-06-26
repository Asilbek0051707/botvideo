"""Search coordinator — aggregates providers and character search."""

from __future__ import annotations

from telegram_bot.services.providers.base import BaseProvider
from telegram_bot.services.providers.stubs import ALL_PROVIDERS


class SearchService:
    """Aggregates all registered search providers."""

    def __init__(self, providers: list[BaseProvider] | None = None) -> None:
        self._providers = providers or ALL_PROVIDERS

    def get_providers(self) -> list[BaseProvider]:
        return self._providers

    def build_links(self, character: str, material_type: str) -> list[tuple[str, str]]:
        """Return [(label, url), ...] for every provider's search link."""
        links = []
        for p in self._providers:
            url = p.build_search_url(character, material_type)
            label = f"{p.icon} {p.name}"
            links.append((label, url))
        return links


search_service = SearchService()
