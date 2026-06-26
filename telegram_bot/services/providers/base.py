"""Abstract search provider interface.

New providers: subclass BaseProvider and register in SearchService.
No changes to existing code required.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SearchResult:
    """A single search result from any provider."""

    title: str
    url: str          # direct URL to the resource
    thumb_url: str = ""
    source: str = ""  # provider name


class BaseProvider(ABC):
    """Interface every search provider must implement."""

    name: str = "unknown"
    icon: str = "🔍"

    @abstractmethod
    def build_search_url(self, query: str, material_type: str) -> str:
        """Return a browser-ready search URL for the given query + material type."""

    @abstractmethod
    async def search(self, query: str, material_type: str, limit: int = 10) -> list[SearchResult]:
        """Perform an actual search and return results.

        Stub implementations should raise NotImplementedError or return [].
        Full implementations will be added in a future step.
        """
