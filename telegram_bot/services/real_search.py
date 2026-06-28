"""Real web search — ddgs + yt-dlp, no API key needed.

Returns actual results (titles + direct URLs) shown inside the bot.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

IMAGE_MAT_CODES = {"png", "bg", "thumb", "gif"}
VIDEO_MAT_CODES = {"vid", "gs", "anim", "mus", "fx", "sfx", "voice"}


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


async def download_yt_thumbnails(results: list, limit: int = 4) -> list[tuple[bytes, object]]:
    """Download YouTube video thumbnails at max resolution. Returns (jpg_bytes, RealResult) pairs."""
    import re, httpx
    downloaded: list[tuple[bytes, object]] = []
    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        for r in results[:limit]:
            vid_id: str | None = None
            if "youtu.be/" in r.url:
                vid_id = r.url.split("youtu.be/")[-1][:11]
            else:
                m = re.search(r"[?&]v=([\w-]{11})", r.url)
                if m:
                    vid_id = m.group(1)
            if not vid_id:
                continue
            # Try highest quality first: maxresdefault (1280x720+) → hqdefault fallback
            thumb_data: bytes | None = None
            for quality in ("maxresdefault", "sddefault", "hqdefault"):
                try:
                    resp = await client.get(
                        f"https://img.youtube.com/vi/{vid_id}/{quality}.jpg"
                    )
                    if resp.status_code == 200 and len(resp.content) > 5_000:
                        thumb_data = resp.content
                        break
                except Exception:
                    continue
            if thumb_data:
                downloaded.append((thumb_data, r))
    return downloaded


def _scrape_country_trending_sync(country_code: str, limit: int = 4) -> list:
    try:
        import yt_dlp  # type: ignore
        url = f"https://www.youtube.com/feed/trending?gl={country_code}"
        opts = {
            "quiet": True, "no_warnings": True, "extract_flat": True,
            "playlistend": limit + 4, "skip_download": True, "ignoreerrors": True,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            data = ydl.extract_info(url, download=False) or {}
        results = []
        for e in (data.get("entries") or []):
            if not e or not e.get("id"):
                continue
            views = e.get("view_count")
            dur = e.get("duration")
            extra_parts: list[str] = []
            if views:
                extra_parts.append(
                    f"👁 {views/1_000_000:.1f}M" if views >= 1_000_000
                    else f"👁 {views/1_000:.0f}K"
                )
            if dur:
                mm, ss = divmod(int(dur), 60)
                extra_parts.append(f"⏱ {mm}:{ss:02d}")
            results.append(RealResult(
                title=(e.get("title") or "")[:60],
                url=f"https://youtu.be/{e['id']}",
                source="youtube.com",
                extra=" · ".join(extra_parts),
            ))
        return results[:limit]
    except Exception:
        return []


async def scrape_country_trending(country_code: str, limit: int = 4) -> list:
    return await asyncio.to_thread(_scrape_country_trending_sync, country_code, limit)


def _search_competitors_sync(niche: str, limit: int = 4) -> list[dict]:
    """Search YouTube and return top unique channels for a niche."""
    try:
        import yt_dlp  # type: ignore
        opts = {
            "quiet": True, "no_warnings": True, "extract_flat": True,
            "playlistend": 12, "skip_download": True, "ignoreerrors": True,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            data = ydl.extract_info(f"ytsearch12:{niche}", download=False) or {}
        seen: set[str] = set()
        channels: list[dict] = []
        for e in (data.get("entries") or []):
            if not e:
                continue
            cid = e.get("channel_id", "")
            if not cid or cid in seen:
                continue
            seen.add(cid)
            subs = e.get("channel_follower_count")
            channels.append({
                "name": e.get("channel") or e.get("uploader") or "—",
                "url": e.get("channel_url") or f"https://youtube.com/channel/{cid}",
                "subs": subs,
                "video_id": e.get("id"),
            })
            if len(channels) >= limit:
                break
        return channels
    except Exception:
        return []


async def search_competitors(niche: str, limit: int = 4) -> list[dict]:
    return await asyncio.to_thread(_search_competitors_sync, niche, limit)


# ─── ffmpeg path ──────────────────────────────────────────────────

def _ffmpeg_exe() -> str | None:
    try:
        import imageio_ffmpeg  # type: ignore
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


# ─── yt-dlp audio download ────────────────────────────────────────

def _download_yt_audio_sync(url: str) -> tuple[bytes, str] | None:
    """Download YouTube audio as mp3 320kbps (via ffmpeg). Returns (bytes, title)."""
    import yt_dlp, tempfile, os  # type: ignore
    ffmpeg = _ffmpeg_exe()
    with tempfile.TemporaryDirectory() as tmpdir:
        opts: dict = {
            "format": "bestaudio[abr>=192]/bestaudio/best",
            "outtmpl": f"{tmpdir}/%(id)s.%(ext)s",
            "quiet": True,
            "no_warnings": True,
        }
        if ffmpeg:
            opts["ffmpeg_location"] = ffmpeg
            opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            }]
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True) or {}
            title = info.get("title", "audio")
            for fname in os.listdir(tmpdir):
                path = os.path.join(tmpdir, fname)
                size = os.path.getsize(path)
                if size > 10_000:
                    with open(path, "rb") as fp:
                        return fp.read(), title
        except Exception:
            pass
    return None


async def download_yt_audio(url: str) -> tuple[bytes, str] | None:
    return await asyncio.to_thread(_download_yt_audio_sync, url)


# ─── yt-dlp video download ────────────────────────────────────────

def _download_yt_video_sync(url: str, max_mb: int = 45) -> tuple[bytes, str] | None:
    """Download YouTube video at highest quality fitting within max_mb (Telegram limit).

    Tries in order: 4K → 2K → 1080p → 720p until one fits under max_mb.
    Merges best video + best audio via ffmpeg.
    """
    import yt_dlp, tempfile, os  # type: ignore
    ffmpeg = _ffmpeg_exe()
    max_bytes = max_mb * 1024 * 1024

    # Quality ladder — tries highest first, falls back automatically
    fmt = (
        "bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]"
        "/bestvideo[height<=1440][ext=mp4]+bestaudio[ext=m4a]"
        "/bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]"
        "/bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]"
        "/best[ext=mp4]/best"
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        opts: dict = {
            "format": fmt,
            "outtmpl": f"{tmpdir}/%(id)s.%(ext)s",
            "quiet": True,
            "no_warnings": True,
            "merge_output_format": "mp4",
        }
        if ffmpeg:
            opts["ffmpeg_location"] = ffmpeg

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True) or {}
            title = info.get("title", "video")

            for fname in sorted(os.listdir(tmpdir)):
                path = os.path.join(tmpdir, fname)
                size = os.path.getsize(path)
                if size < 10_000:
                    continue
                if size <= max_bytes:
                    with open(path, "rb") as fp:
                        return fp.read(), title
                # File too large — re-download at lower quality
                break
        except Exception:
            pass

    # Fallback: try 720p if high-res was too big
    with tempfile.TemporaryDirectory() as tmpdir:
        opts2: dict = {
            "format": "best[height<=720][ext=mp4]/best[ext=mp4]/best",
            "outtmpl": f"{tmpdir}/%(id)s.%(ext)s",
            "quiet": True,
            "no_warnings": True,
        }
        if ffmpeg:
            opts2["ffmpeg_location"] = ffmpeg
        try:
            with yt_dlp.YoutubeDL(opts2) as ydl:
                info = ydl.extract_info(url, download=True) or {}
            title = info.get("title", "video")
            for fname in os.listdir(tmpdir):
                path = os.path.join(tmpdir, fname)
                size = os.path.getsize(path)
                if 10_000 < size <= max_bytes:
                    with open(path, "rb") as fp:
                        return fp.read(), title
        except Exception:
            pass
    return None


async def download_yt_video(url: str, max_mb: int = 45) -> tuple[bytes, str] | None:
    return await asyncio.to_thread(_download_yt_video_sync, url, max_mb)


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
        # Request more results to filter by quality (prefer large/HD images)
        with DDGS() as d:
            for r in d.images(query, max_results=limit * 3):
                source = r.get("source", "") or r.get("url", "")
                domain = source.split("/")[2] if "//" in source else source
                img_url = r.get("image", "") or r.get("url", "")
                if not img_url:
                    continue
                # Prefer high-resolution images: width >= 1000 or unknown
                w = r.get("width", 0)
                h = r.get("height", 0)
                if w and w < 500:   # skip tiny images
                    continue
                results.append(RealResult(
                    title=r.get("title", query)[:60],
                    url=img_url,
                    source=domain,
                ))
                if len(results) >= limit:
                    break
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
