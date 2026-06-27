"""Search coordinator — material-type aware link builder."""

from __future__ import annotations

from telegram_bot.services.providers.stubs import build_material_links


class SearchService:
    def build_links(self, character: str, material_type: str) -> list[tuple[str, str]]:
        """Return [(label, url)] for the correct platforms per material type."""
        return build_material_links(character, material_type)


search_service = SearchService()
