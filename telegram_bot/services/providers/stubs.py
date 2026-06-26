"""URL-generating provider stubs.

Each provider builds a ready-to-use browser search URL.
Actual API/scraping will be added in a later step.
"""

from __future__ import annotations

from urllib.parse import quote_plus

from telegram_bot.services.providers.base import BaseProvider, SearchResult

# ─── material type → search modifier map ──────────────────────────

_MAT_MODIFIERS: dict[str, str] = {
    "png":        "PNG transparent",
    "gs":         "green screen",
    "anim":       "animation loop",
    "gif":        "GIF animated",
    "vid":        "video clip",
    "bg":         "background wallpaper",
    "mus":        "music soundtrack",
    "sfx":        "sound effect",
    "voice":      "voice sample",
    "fx":         "visual effect",
    "thumb":      "thumbnail design",
    "prompts":    "fan art",
    "videas":     "video ideas",
    "pack":       "asset pack",
    "search":     "",
}


def _q(character: str, material_type: str) -> str:
    mod = _MAT_MODIFIERS.get(material_type, "")
    raw = f"{character} {mod}".strip()
    return quote_plus(raw)


# ─── provider implementations ─────────────────────────────────────

class YandexProvider(BaseProvider):
    name = "Yandex"
    icon = "🔎"

    def build_search_url(self, query: str, material_type: str) -> str:
        q = _q(query, material_type)
        return f"https://yandex.com/images/search?text={q}"

    async def search(self, query: str, material_type: str, limit: int = 10) -> list[SearchResult]:
        return []  # API integration in future step


class GoogleProvider(BaseProvider):
    name = "Google"
    icon = "🔍"

    def build_search_url(self, query: str, material_type: str) -> str:
        q = _q(query, material_type)
        return f"https://www.google.com/search?q={q}&tbm=isch"

    async def search(self, query: str, material_type: str, limit: int = 10) -> list[SearchResult]:
        return []


class PixabayProvider(BaseProvider):
    name = "Pixabay"
    icon = "🖼"

    def build_search_url(self, query: str, material_type: str) -> str:
        q = _q(query, material_type)
        return f"https://pixabay.com/images/search/{q}/"

    async def search(self, query: str, material_type: str, limit: int = 10) -> list[SearchResult]:
        return []


class PexelsProvider(BaseProvider):
    name = "Pexels"
    icon = "📷"

    def build_search_url(self, query: str, material_type: str) -> str:
        q = _q(query, material_type)
        return f"https://www.pexels.com/search/{q}/"

    async def search(self, query: str, material_type: str, limit: int = 10) -> list[SearchResult]:
        return []


class FreepikProvider(BaseProvider):
    name = "Freepik"
    icon = "🎨"

    def build_search_url(self, query: str, material_type: str) -> str:
        q = _q(query, material_type)
        return f"https://www.freepik.com/search?query={q}"

    async def search(self, query: str, material_type: str, limit: int = 10) -> list[SearchResult]:
        return []


class YouTubeProvider(BaseProvider):
    name = "YouTube"
    icon = "▶️"

    def build_search_url(self, query: str, material_type: str) -> str:
        q = _q(query, material_type)
        return f"https://www.youtube.com/results?search_query={q}"

    async def search(self, query: str, material_type: str, limit: int = 10) -> list[SearchResult]:
        return []


# ─── registry ─────────────────────────────────────────────────────

ALL_PROVIDERS: list[BaseProvider] = [
    YandexProvider(),
    GoogleProvider(),
    PixabayProvider(),
    PexelsProvider(),
    FreepikProvider(),
    YouTubeProvider(),
]
