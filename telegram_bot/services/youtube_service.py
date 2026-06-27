"""YouTube channel & video info using yt-dlp — no API key required."""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass, field


# ─── data models ──────────────────────────────────────────────────

@dataclass
class ChannelInfo:
    title: str
    channel_url: str
    subscriber_count: int | None
    view_count: int
    video_count: int
    description: str
    country: str
    recent_videos: list[dict] = field(default_factory=list)


@dataclass
class VideoInfo:
    video_id: str
    title: str
    channel_title: str
    view_count: int
    like_count: int
    comment_count: int
    duration: str
    published_at: str
    tags: list[str] = field(default_factory=list)
    description: str = ""


# ─── helpers ──────────────────────────────────────────────────────

def _fmt(n: int | None) -> str:
    if n is None:
        return "Hidden"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def _fmt_duration(seconds: int | None) -> str:
    if not seconds:
        return "—"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def _fmt_date(upload_date: str | None) -> str:
    """20240115 → Jan 15, 2024"""
    if not upload_date or len(upload_date) < 8:
        return "—"
    try:
        from datetime import date, datetime, timezone
        d = date(int(upload_date[:4]), int(upload_date[4:6]), int(upload_date[6:8]))
        diff = (date.today() - d).days
        if diff == 0:
            return "today"
        if diff == 1:
            return "1 day ago"
        if diff < 30:
            return f"{diff} days ago"
        if diff < 365:
            return f"{diff // 30} months ago"
        return f"{diff // 365} years ago"
    except Exception:
        return upload_date


def _build_url(raw: str) -> str:
    """Turn any user input into a full YouTube URL."""
    raw = raw.strip()
    if raw.startswith("http"):
        return raw
    if raw.startswith("UC") and len(raw) > 20:
        return f"https://www.youtube.com/channel/{raw}"
    handle = raw.lstrip("@")
    return f"https://www.youtube.com/@{handle}"


def _extract_video_id(raw: str) -> str | None:
    raw = raw.strip()
    m = re.search(r"youtu\.be/([\w-]{11})", raw)
    if m:
        return m.group(1)
    m = re.search(r"(?:v=|/shorts/|/embed/)([\w-]{11})", raw)
    if m:
        return m.group(1)
    if re.match(r"^[\w-]{11}$", raw):
        return raw
    return None


# ─── yt-dlp extraction (sync, run in thread) ──────────────────────

def _extract_channel_sync(url: str) -> dict | None:
    try:
        import yt_dlp  # type: ignore
    except ImportError:
        return None

    # Step 1: channel metadata (subs, description, title)
    meta_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "playlistend": 1,
        "skip_download": True,
        "ignoreerrors": True,
    }
    # Step 2: recent videos from /videos tab
    vid_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "playlistend": 5,
        "skip_download": True,
        "ignoreerrors": True,
    }
    try:
        with yt_dlp.YoutubeDL(meta_opts) as ydl:
            meta = ydl.extract_info(url, download=False) or {}

        # Try /videos sub-tab for actual video entries
        videos_url = url.rstrip("/") + "/videos"
        with yt_dlp.YoutubeDL(vid_opts) as ydl:
            vdata = ydl.extract_info(videos_url, download=False) or {}

        entries = [e for e in (vdata.get("entries") or []) if e and e.get("id")]
        meta["_recent_entries"] = entries[:5]
        return meta
    except Exception:
        return None


def _extract_video_sync(video_id: str) -> dict | None:
    try:
        import yt_dlp  # type: ignore
    except ImportError:
        return None

    opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "ignoreerrors": True,
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
    except Exception:
        return None


# ─── async API ────────────────────────────────────────────────────

async def get_channel(raw: str) -> ChannelInfo | None:
    url = _build_url(raw)
    data = await asyncio.to_thread(_extract_channel_sync, url)
    if not data:
        return None

    recent_entries = data.get("_recent_entries") or []
    recent: list[dict] = []
    for e in recent_entries:
        if not e:
            continue
        recent.append({
            "title": (e.get("title") or "")[:50],
            "duration": _fmt_duration(e.get("duration")),
            "view_count": _fmt(e.get("view_count")) if e.get("view_count") else "",
            "id": e.get("id", ""),
        })

    return ChannelInfo(
        title=data.get("channel") or data.get("uploader") or data.get("title") or raw,
        channel_url=data.get("channel_url") or data.get("webpage_url") or url,
        subscriber_count=data.get("channel_follower_count"),
        view_count=data.get("view_count") or 0,
        video_count=data.get("playlist_count") or len(recent_entries),
        description=(data.get("description") or "")[:200],
        country=data.get("channel_location") or "—",
        recent_videos=recent,
    )


async def get_video(raw: str) -> VideoInfo | None:
    vid_id = _extract_video_id(raw)
    if not vid_id:
        # Maybe it's a full URL yt-dlp can handle directly
        vid_id = raw.strip()

    data = await asyncio.to_thread(_extract_video_sync, vid_id)
    if not data or data.get("_type") == "playlist":
        return None

    return VideoInfo(
        video_id=data.get("id", vid_id),
        title=data.get("title", ""),
        channel_title=data.get("channel") or data.get("uploader", ""),
        view_count=data.get("view_count") or 0,
        like_count=data.get("like_count") or 0,
        comment_count=data.get("comment_count") or 0,
        duration=_fmt_duration(data.get("duration")),
        published_at=_fmt_date(data.get("upload_date")),
        tags=(data.get("tags") or [])[:10],
        description=(data.get("description") or "")[:250],
    )


# ─── format for Telegram ──────────────────────────────────────────

def format_channel(ch: ChannelInfo) -> str:
    lines = [f"📺 <b>{ch.title}</b>", f"🔗 {ch.channel_url}", ""]

    if ch.subscriber_count is not None:
        lines.append(f"👥 Obunachílar: <b>{_fmt(ch.subscriber_count)}</b>")
    if ch.view_count:
        lines.append(f"👁 Ko'rishlar: <b>{_fmt(ch.view_count)}</b>")
    if ch.video_count:
        lines.append(f"🎥 Videolar: <b>{ch.video_count}</b>")
    if ch.view_count and ch.video_count:
        avg = ch.view_count // ch.video_count
        lines.append(f"📊 O'rtacha ko'rish: <b>{_fmt(avg)}</b>")
    if ch.country and ch.country != "—":
        lines.append(f"🌍 Mamlakat: <b>{ch.country}</b>")

    if ch.description:
        desc = ch.description[:180] + ("…" if len(ch.description) > 180 else "")
        lines += ["", f"📝 {desc}"]

    if ch.recent_videos:
        lines += ["", "🕐 <b>So'nggi videolar:</b>"]
        for i, v in enumerate(ch.recent_videos, 1):
            title = v["title"] + ("…" if len(v["title"]) >= 50 else "")
            extra = ""
            if v.get("view_count") and v["view_count"] not in ("", "0"):
                extra += f" · 👁 {v['view_count']}"
            if v.get("duration") and v["duration"] != "0:00":
                extra += f" · ⏱ {v['duration']}"
            lines.append(f"  {i}. {title}{extra}")

    return "\n".join(lines)


def format_video(v: VideoInfo) -> str:
    lines = [
        f"🎬 <b>{v.title}</b>",
        f"📺 Kanal: <b>{v.channel_title}</b>",
        "",
        f"👁 Ko'rishlar: <b>{_fmt(v.view_count)}</b>",
        f"👍 Layklar: <b>{_fmt(v.like_count)}</b>",
        f"💬 Izohlar: <b>{_fmt(v.comment_count)}</b>",
        f"⏱ Davomiyligi: <b>{v.duration}</b>",
        f"📅 Yuklangan: <b>{v.published_at}</b>",
    ]
    if v.tags:
        lines += ["", f"🏷 Teglar: <code>{', '.join(v.tags[:8])}</code>"]
    if v.description:
        desc = v.description[:200] + ("…" if len(v.description) > 200 else "")
        lines += ["", f"📝 {desc}"]
    return "\n".join(lines)
