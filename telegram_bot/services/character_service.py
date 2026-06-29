"""Character service — loads and queries the JSON character database.

Data lives in telegram_bot/data/characters/<category_id>.json.
All data is cached in memory after the first load.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

_DATA_DIR = Path(__file__).parent.parent / "data"
_CHARS_DIR = _DATA_DIR / "characters"
_CATS_FILE = _DATA_DIR / "categories.json"

CHARS_PER_PAGE = 8  # characters shown per page in the Telegram list


@dataclass(frozen=True)
class CharacterData:
    id: str
    name: str
    aliases: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def matches(self, query: str) -> bool:
        q = query.lower()
        return (
            q in self.name.lower()
            or any(q in a.lower() for a in self.aliases)
            or any(q in t.lower() for t in self.tags)
        )


@dataclass(frozen=True)
class CategoryData:
    id: str
    name: str
    icon: str
    callback: str  # the callback_data used in trends.py (e.g. "trends:marvel")


class CharacterService:
    """Singleton service for category + character lookups."""

    def __init__(self) -> None:
        self._categories: list[CategoryData] = []
        self._chars_cache: dict[str, list[CharacterData]] = {}

    # ── categories ───────────────────────────────────────────────

    def get_categories(self) -> list[CategoryData]:
        if not self._categories:
            self._categories = self._load_categories()
        return self._categories

    def get_category(self, cat_id: str) -> CategoryData | None:
        return next((c for c in self.get_categories() if c.id == cat_id), None)

    # ── characters ───────────────────────────────────────────────

    def get_characters(self, cat_id: str) -> list[CharacterData]:
        if cat_id not in self._chars_cache:
            self._chars_cache[cat_id] = self._load_characters(cat_id)
        return self._chars_cache[cat_id]

    def get_character(self, cat_id: str, char_id: str) -> CharacterData | None:
        return next(
            (c for c in self.get_characters(cat_id) if c.id == char_id), None
        )

    def get_page(
        self, cat_id: str, page: int = 0
    ) -> tuple[list[CharacterData], int, int]:
        """Return (chars_on_page, page, total_pages)."""
        all_chars = self.get_characters(cat_id)
        total = len(all_chars)
        total_pages = max(1, (total + CHARS_PER_PAGE - 1) // CHARS_PER_PAGE)
        page = max(0, min(page, total_pages - 1))
        start = page * CHARS_PER_PAGE
        return all_chars[start : start + CHARS_PER_PAGE], page, total_pages

    # ── search ───────────────────────────────────────────────────

    # Flat index: (cat, char, pre-lowercased searchable string).
    # Built once on first search call — O(1) for all subsequent searches.
    _flat_index: list[tuple[CategoryData, CharacterData, str]] = []

    def _ensure_index(self) -> None:
        if self._flat_index:
            return
        for cat in self.get_categories():
            for char in self.get_characters(cat.id):
                # Combine all searchable fields into one lowercased string once.
                blob = " ".join(
                    [char.name] + list(char.aliases) + list(char.tags)
                ).lower()
                self._flat_index.append((cat, char, blob))

    def search(
        self, query: str, limit: int = 20
    ) -> list[tuple[CategoryData, CharacterData]]:
        """Full-text search across all categories using a pre-built flat index."""
        self._ensure_index()
        q = query.lower()
        results: list[tuple[CategoryData, CharacterData]] = []
        for cat, char, blob in self._flat_index:
            if q in blob:
                results.append((cat, char))
                if len(results) >= limit:
                    break
        return results

    # ── private loaders ──────────────────────────────────────────

    def _load_categories(self) -> list[CategoryData]:
        try:
            with open(_CATS_FILE, encoding="utf-8") as f:
                raw = json.load(f)
            return [
                CategoryData(
                    id=c["id"],
                    name=c["name"],
                    icon=c["icon"],
                    callback=c.get("callback", f"trends:{c['id']}"),
                )
                for c in raw["categories"]
            ]
        except Exception:
            return []

    def _load_characters(self, cat_id: str) -> list[CharacterData]:
        path = _CHARS_DIR / f"{cat_id}.json"
        if not path.exists():
            return []
        try:
            with open(path, encoding="utf-8") as f:
                raw = json.load(f)
            return [
                CharacterData(
                    id=c["id"],
                    name=c["name"],
                    aliases=c.get("aliases", []),
                    tags=c.get("tags", []),
                )
                for c in raw.get("characters", [])
            ]
        except Exception:
            return []


# singleton
char_service = CharacterService()
