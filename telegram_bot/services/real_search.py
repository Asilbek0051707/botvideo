"""Real web search — ddgs + yt-dlp, no API key needed.

Returns actual results (titles + direct URLs) shown inside the bot.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

IMAGE_MAT_CODES = {"png", "bg", "thumb", "gif"}


async def download_images(results: list, limit: int = 4) -> list[tuple[bytes, str]]:
    """Download image bytes for a list of RealResult. Returns (bytes, title) pairs."""
    import httpx
    downloaded: list[tuple[bytes, str]] = []
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
        "Referer": "https://www.google.com/",
    }
    async with httpx.AsyncClient(
        timeout=10, follow_redirects=True, headers=headers
    ) as client:
        for r in results[:limit]:
            try:
                resp = await client.get(r.url)
                if resp.status_code == 200 and len(resp.content) > 2000:
                    downloaded.append((resp.content, r.title))
            except Exception:
                continue
    return downloaded


@dataclass
class RealResult:
    title: str
    url: str
    source: str
    extra: str = ""


# ─── sync workers ─────────────────────────────────────────────────

def _ddg_images_sync(query: str, limit: int) -> list[RealResult]:
    try:
        from ddgs import DDGS  # type: ignore
        results = []
        with DDGS() as d:
            for r in d.images(query, max_results=limit):
                source = r.get("source", "") or r.get("url", "")
                domain = source.split("/")[2] if "//" in source else source
                img_url = r.get("image", "") or r.get("url", "")
                if not img_url:
                    continue
                results.append(RealResult(
                    title=r.get("title", query)[:60],
                    url=img_url,
                    source=domain,
                ))
        return results
    except Exception:
        return []


def _ddg_text_sync(query: str, limit: int) -> list[RealResult]:
    try:
        from ddgs import DDGS  # type: ignore
        results = []
        with DDGS() as d:
            for r in d.text(query, max_results=limit):
                url = r.get("href", "")
                domain = url.split("/")[2] if "//" in url else url
                snippet = r.get("body", "")[:80]
                results.append(RealResult(
                    title=r.get("title", query)[:60],
                    url=url,
                    source=domain,
                    extra=snippet,
                ))
        return results
    except Exception:
        return []


def _yt_search_sync(query: str, limit: int) -> list[RealResult]:
    try:
        import yt_dlp  # type: ignore
        opts = {"quiet": True, "no_warnings": True,
                "extract_flat": True, "skip_download": True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            data = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
        results = []
        for e in (data.get("entries") or []):
            if not e or not e.get("id"):
                continue
            views = e.get("view_count")
            dur   = e.get("duration")
            extra_parts = []
            if views:
                extra_parts.append(
                    f"👁 {views/1_000_000:.1f}M" if views >= 1_000_000
                    else f"👁 {views/1_000:.0f}K" if views >= 1_000
                    else f"👁 {views}"
                )
            if dur:
                m, s = divmod(int(dur), 60)
                extra_parts.append(f"⏱ {m}:{s:02d}")
            results.append(RealResult(
                title=(e.get("title") or query)[:60],
                url=f"https://youtu.be/{e['id']}",
                source="youtube.com",
                extra=" · ".join(extra_parts),
            ))
        return results
    except Exception:
        return []


# ─── async wrappers ───────────────────────────────────────────────

async def search_images(query: str, limit: int = 4) -> list[RealResult]:
    return await asyncio.to_thread(_ddg_images_sync, query, limit)

async def search_web(query: str, limit: int = 4) -> list[RealResult]:
    return await asyncio.to_thread(_ddg_text_sync, query, limit)

async def search_youtube(query: str, limit: int = 4) -> list[RealResult]:
    return await asyncio.to_thread(_yt_search_sync, query, limit)


# ─── material router ──────────────────────────────────────────────

async def search_for_material(query: str, mat_code: str, limit: int = 4) -> list[RealResult]:
    """Route to the right search backend. Falls back to YouTube if DDG fails."""

    async def _with_yt_fallback(ddg_query: str, yt_query: str) -> list[RealResult]:
        results = await search_images(ddg_query, limit)
        if not results:
            results = await search_youtube(yt_query, limit)
        return results

    if mat_code == "png":
        return await _with_yt_fallback(
            f"{query} transparent PNG no background",
            f"{query} PNG transparent free download"
        )

    if mat_code == "bg":
        return await _with_yt_fallback(
            f"{query} background wallpaper 4K",
            f"{query} background free stock"
        )

    if mat_code == "thumb":
        return await _with_yt_fallback(
            f"{query} YouTube thumbnail template",
            f"{query} thumbnail design free"
        )

    if mat_code == "gif":
        results = await search_images(f"{query} animated GIF", limit)
        if not results:
            results = await search_web(f"site:giphy.com OR site:tenor.com {query}", limit)
        return results

    if mat_code == "gs":
        return await search_youtube(f"{query} green screen free download", limit)

    if mat_code == "anim":
        return await search_youtube(f"{query} animation loop free", limit)

    if mat_code == "vid":
        return await search_youtube(f"{query} free stock video", limit)

    if mat_code == "mus":
        return await search_youtube(f"{query} background music no copyright free", limit)

    if mat_code == "fx":
        return await search_youtube(f"{query} visual effect VFX free", limit)

    if mat_code == "sfx":
        results = await search_web(f"{query} sound effect free download freesound", limit)
        if not results:
            results = await search_youtube(f"{query} sound effect free", limit)
        return results

    if mat_code == "voice":
        results = await search_web(f"{query} AI voice generator free", limit)
        if not results:
            results = await search_youtube(f"{query} AI voice", limit)
        return results

    if mat_code == "prompts":
        results = await search_web(f"{query} Midjourney AI prompt", limit)
        if not results:
            results = await search_youtube(f"{query} AI image prompt tutorial", limit)
        return results

    if mat_code == "pack":
        results = await search_web(f"{query} asset pack free download", limit)
        if not results:
            results = await search_youtube(f"{query} free assets pack", limit)
        return results

    # general / search
    results = await search_web(query, limit)
    if not results:
        results = await search_youtube(query, limit)
    return results
