"""Google Trends integration provider.

Uses pytrends (already a project dependency).
No API key required — works anonymously.
Results are cached aggressively to avoid rate-limit blocks.
"""
from __future__ import annotations

import asyncio

from .base import BaseIntegrationProvider, IntegrationConfig


class GoogleTrendsProvider(BaseIntegrationProvider):

    CONFIG = IntegrationConfig(
        name="Google Trends",
        slug="google_trends",
        category="trends",
        description="Daily trends, keyword trends, related searches by country",
        api_key_env="",
        requires_key=False,
        cache_ttl=3600,
        docs_url="https://trends.google.com",
    )

    def __init__(self) -> None:
        super().__init__(self.CONFIG)

    # ── helpers ────────────────────────────────────────────────────────

    def _build_client(self, geo: str = "US", hl: str = "en-US"):
        try:
            from pytrends.request import TrendReq
            return TrendReq(hl=hl, tz=360, timeout=(10, 25))
        except ImportError:
            return None

    # ── health ─────────────────────────────────────────────────────────

    async def health_check(self) -> tuple[bool, str]:
        try:
            result = await asyncio.to_thread(self._sync_daily_trends, "US", 1)
            if result:
                return True, f"OK — got {len(result)} trend(s)"
            return False, "No data returned (possible rate-limit)"
        except ImportError:
            return False, "pytrends not installed"
        except Exception as exc:
            return False, str(exc)

    # ── sync helpers (blocking — called via to_thread) ─────────────────

    def _sync_daily_trends(self, geo: str = "US", limit: int = 20) -> list[dict]:
        from pytrends.request import TrendReq
        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        df = pt.trending_searches(pn=geo)
        items = df.iloc[:, 0].tolist()[:limit]
        return [{"keyword": kw, "geo": geo} for kw in items]

    def _sync_keyword_trends(self, keyword: str, geo: str = "US") -> dict:
        from pytrends.request import TrendReq
        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        pt.build_payload([keyword], cat=0, timeframe="today 3-m", geo=geo)
        interest = pt.interest_over_time()
        related  = pt.related_queries()
        top_related = []
        if keyword in related and related[keyword]["top"] is not None:
            top_df = related[keyword]["top"]
            top_related = top_df["query"].head(10).tolist()
        values = []
        if not interest.empty and keyword in interest.columns:
            values = interest[keyword].tail(12).tolist()
        return {
            "keyword":     keyword,
            "geo":         geo,
            "values":      values,
            "top_related": top_related,
        }

    def _sync_related_queries(self, keyword: str, geo: str = "US") -> list[str]:
        from pytrends.request import TrendReq
        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        pt.build_payload([keyword], cat=0, timeframe="today 1-m", geo=geo)
        related = pt.related_queries()
        if keyword in related and related[keyword]["top"] is not None:
            return related[keyword]["top"]["query"].head(20).tolist()
        return []

    def _sync_category_trends(self, category: int = 0, geo: str = "US") -> list[str]:
        from pytrends.request import TrendReq
        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        df = pt.trending_searches(pn=geo)
        return df.iloc[:, 0].head(10).tolist()

    # ── async API ──────────────────────────────────────────────────────

    async def get_daily_trends(self, geo: str = "US", limit: int = 20) -> list[dict]:
        try:
            return await asyncio.to_thread(self._sync_daily_trends, geo, limit)
        except Exception:
            return []

    async def get_keyword_trends(self, keyword: str, geo: str = "US") -> dict:
        try:
            return await asyncio.to_thread(self._sync_keyword_trends, keyword, geo)
        except Exception:
            return {}

    async def get_related_queries(self, keyword: str, geo: str = "US") -> list[str]:
        try:
            return await asyncio.to_thread(self._sync_related_queries, keyword, geo)
        except Exception:
            return []

    async def search(self, query: str, **kwargs) -> list[dict]:
        geo = kwargs.get("geo", "US")
        data = await self.get_keyword_trends(query, geo=geo)
        return [data] if data else []
