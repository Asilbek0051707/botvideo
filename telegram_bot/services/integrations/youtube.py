"""YouTube Data API v3 integration provider.

Env var: YOUTUBE_API_KEY
Docs:    https://developers.google.com/youtube/v3/docs
"""
from __future__ import annotations

import asyncio
import json

import httpx

from .base import BaseIntegrationProvider, IntegrationConfig

_YT_BASE = "https://www.googleapis.com/youtube/v3"


class YouTubeProvider(BaseIntegrationProvider):

    CONFIG = IntegrationConfig(
        name="YouTube Data API",
        slug="youtube",
        category="video",
        description="Channel lookup, video search, statistics, metadata",
        api_key_env="YOUTUBE_API_KEY",
        base_url=_YT_BASE,
        timeout=20,
        cache_ttl=1800,
        docs_url="https://developers.google.com/youtube/v3/docs",
    )

    def __init__(self) -> None:
        super().__init__(self.CONFIG)

    # ── helpers ───────────────────────────────────────────────────────

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=_YT_BASE, timeout=self.config.timeout)

    def _params(self, **extra) -> dict:
        return {"key": self.api_key, **extra}

    # ── health ────────────────────────────────────────────────────────

    async def health_check(self) -> tuple[bool, str]:
        if not self.is_configured:
            return False, "Not configured: YOUTUBE_API_KEY not set"
        try:
            async with self._client() as c:
                r = await c.get(
                    "/search",
                    params=self._params(part="id", q="test", maxResults=1, type="video"),
                )
                if r.status_code == 200:
                    return True, "OK"
                if r.status_code == 403:
                    return False, "API key invalid or quota exceeded"
                return False, f"HTTP {r.status_code}"
        except Exception as exc:
            return False, str(exc)

    # ── channel ───────────────────────────────────────────────────────

    async def search_channels(self, query: str, limit: int = 5) -> list[dict]:
        if not self.is_configured:
            return []
        try:
            async with self._client() as c:
                r = await c.get(
                    "/search",
                    params=self._params(
                        part="snippet",
                        q=query,
                        type="channel",
                        maxResults=min(limit, 50),
                    ),
                )
                r.raise_for_status()
                return [
                    {
                        "channel_id": item["id"]["channelId"],
                        "title":       item["snippet"]["channelTitle"],
                        "description": item["snippet"]["description"],
                        "thumb":       item["snippet"]["thumbnails"].get("default", {}).get("url", ""),
                    }
                    for item in r.json().get("items", [])
                ]
        except Exception:
            return []

    async def get_channel_stats(self, channel_id: str) -> dict:
        if not self.is_configured:
            return {}
        try:
            async with self._client() as c:
                r = await c.get(
                    "/channels",
                    params=self._params(part="snippet,statistics,contentDetails", id=channel_id),
                )
                r.raise_for_status()
                items = r.json().get("items", [])
                if not items:
                    return {}
                item = items[0]
                stats = item.get("statistics", {})
                return {
                    "channel_id":       channel_id,
                    "title":            item["snippet"]["title"],
                    "description":      item["snippet"]["description"],
                    "subscriber_count": int(stats.get("subscriberCount", 0)),
                    "view_count":       int(stats.get("viewCount", 0)),
                    "video_count":      int(stats.get("videoCount", 0)),
                    "country":          item["snippet"].get("country", ""),
                    "thumb":            item["snippet"]["thumbnails"].get("default", {}).get("url", ""),
                }
        except Exception:
            return {}

    # ── videos ────────────────────────────────────────────────────────

    async def search_videos(self, query: str, limit: int = 10) -> list[dict]:
        if not self.is_configured:
            return []
        try:
            async with self._client() as c:
                r = await c.get(
                    "/search",
                    params=self._params(
                        part="snippet",
                        q=query,
                        type="video",
                        maxResults=min(limit, 50),
                        order="relevance",
                    ),
                )
                r.raise_for_status()
                return [
                    {
                        "video_id":     item["id"]["videoId"],
                        "title":        item["snippet"]["title"],
                        "description":  item["snippet"]["description"],
                        "channel_id":   item["snippet"]["channelId"],
                        "channel_title":item["snippet"]["channelTitle"],
                        "published_at": item["snippet"]["publishedAt"],
                        "thumb":        item["snippet"]["thumbnails"].get("default", {}).get("url", ""),
                    }
                    for item in r.json().get("items", [])
                ]
        except Exception:
            return []

    async def get_video_metadata(self, video_id: str) -> dict:
        if not self.is_configured:
            return {}
        try:
            async with self._client() as c:
                r = await c.get(
                    "/videos",
                    params=self._params(
                        part="snippet,statistics,contentDetails",
                        id=video_id,
                    ),
                )
                r.raise_for_status()
                items = r.json().get("items", [])
                if not items:
                    return {}
                item = items[0]
                stats = item.get("statistics", {})
                return {
                    "video_id":     video_id,
                    "title":        item["snippet"]["title"],
                    "description":  item["snippet"]["description"],
                    "tags":         item["snippet"].get("tags", []),
                    "view_count":   int(stats.get("viewCount", 0)),
                    "like_count":   int(stats.get("likeCount", 0)),
                    "comment_count":int(stats.get("commentCount", 0)),
                    "duration":     item["contentDetails"]["duration"],
                    "published_at": item["snippet"]["publishedAt"],
                }
        except Exception:
            return {}

    # ── playlists ─────────────────────────────────────────────────────

    async def get_channel_playlists(self, channel_id: str, limit: int = 10) -> list[dict]:
        if not self.is_configured:
            return []
        try:
            async with self._client() as c:
                r = await c.get(
                    "/playlists",
                    params=self._params(
                        part="snippet,contentDetails",
                        channelId=channel_id,
                        maxResults=min(limit, 50),
                    ),
                )
                r.raise_for_status()
                return [
                    {
                        "playlist_id":  item["id"],
                        "title":        item["snippet"]["title"],
                        "video_count":  item["contentDetails"]["itemCount"],
                        "published_at": item["snippet"]["publishedAt"],
                    }
                    for item in r.json().get("items", [])
                ]
        except Exception:
            return []

    async def search(self, query: str, **kwargs) -> list[dict]:
        return await self.search_videos(query, limit=kwargs.get("limit", 10))
