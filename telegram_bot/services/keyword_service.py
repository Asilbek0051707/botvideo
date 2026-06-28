"""Keyword Engine — store, search, filter and seed trending keywords.

Future search providers can call add_keyword() to populate this automatically.
"""

from __future__ import annotations

import asyncio
import json


# ── default seed data ─────────────────────────────────────────────

_SEED_KEYWORDS: list[tuple] = [
    # (keyword, related, intent, priority, level, category)
    ("spider-man",       ["marvel", "superhero", "shorts"],         "character",  10, "viral",  "cartoon"),
    ("minecraft",        ["gaming", "steve", "creeper", "build"],   "gaming",     10, "viral",  "gaming"),
    ("skibidi toilet",   ["meme", "viral", "funny", "animation"],   "meme",       10, "viral",  "meme"),
    ("goku",             ["dragon ball", "anime", "super saiyan"],  "character",   9, "high",   "anime"),
    ("bluey",            ["kids", "cartoon", "australia", "heeler"],"character",   9, "high",   "cartoon"),
    ("sonic",            ["sega", "hedgehog", "movie", "rings"],    "character",   8, "high",   "gaming"),
    ("batman",           ["dc", "superhero", "dark knight"],        "character",   8, "high",   "cartoon"),
    ("roblox",           ["gaming", "obby", "adopt me", "blox"],   "gaming",      9, "viral",  "gaming"),
    ("pikachu",          ["pokemon", "anime", "cute", "electric"],  "character",   8, "high",   "anime"),
    ("among us",         ["gaming", "impostor", "crewmate"],        "gaming",      6, "medium", "gaming"),
    ("huggy wuggy",      ["poppy playtime", "horror", "viral"],     "character",   7, "high",   "cartoon"),
    ("paw patrol",       ["kids", "rescue", "chase", "skye"],       "character",   8, "high",   "cartoon"),
    ("vs challenge",     ["battle", "fight", "comparison"],         "challenge",   9, "viral",  "general"),
    ("evolution",        ["timeline", "glow up", "transformation"], "idea",        8, "high",   "general"),
    ("funny compilation",["funny", "fail", "moments", "viral"],     "idea",        8, "high",   "general"),
    ("transformation",   ["change", "evolve", "glow up"],           "idea",        7, "high",   "general"),
    ("top 10",           ["countdown", "best", "ranking"],          "idea",        7, "high",   "general"),
    ("baby version",     ["cute", "mini", "funny", "kids"],         "idea",        7, "high",   "kids"),
    ("color challenge",  ["color", "rainbow", "art"],               "challenge",   6, "medium", "kids"),
    ("guess the character",["quiz", "puzzle", "interactive"],       "challenge",   6, "medium", "general"),
    ("naruto",           ["anime", "ninja", "sasuke", "hokage"],    "character",   7, "high",   "anime"),
    ("frozen",           ["disney", "elsa", "anna", "movie"],       "movie",       7, "high",   "cartoon"),
    ("moana",            ["disney", "ocean", "music", "movie"],     "movie",       7, "high",   "cartoon"),
    ("mario",            ["nintendo", "mushroom", "luigi", "game"], "character",   8, "high",   "gaming"),
    ("inside out",       ["pixar", "emotions", "riley", "movie"],   "movie",       8, "high",   "cartoon"),
]


def _seed_sync() -> None:
    from telegram_bot.db.trend_models import TrendKeyword
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        if db.query(TrendKeyword).count() > 0:
            return
        for kw, related, intent, priority, level, cat in _SEED_KEYWORDS:
            db.add(TrendKeyword(
                keyword=kw,
                related_keywords=json.dumps(related),
                search_intent=intent,
                priority=priority,
                trend_level=level,
                category=cat,
            ))
        db.commit()


async def seed_defaults() -> None:
    """Seed default keywords on first run (idempotent)."""
    await asyncio.to_thread(_seed_sync)


# ── CRUD ──────────────────────────────────────────────────────────


def _add_sync(
    keyword: str,
    related: list[str] | None = None,
    intent: str = "general",
    priority: int = 5,
    trend_level: str = "medium",
    category: str = "general",
    language: str = "en",
    country: str = "ALL",
) -> int:
    from telegram_bot.db.trend_models import TrendKeyword
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        existing = db.query(TrendKeyword).filter_by(keyword=keyword.lower()).first()
        if existing:
            return existing.id
        kw = TrendKeyword(
            keyword=keyword.lower(),
            related_keywords=json.dumps(related or []),
            search_intent=intent,
            priority=priority,
            trend_level=trend_level,
            category=category,
            language=language,
            country=country,
        )
        db.add(kw)
        db.commit()
        db.refresh(kw)
        return kw.id


async def add_keyword(keyword: str, **kwargs) -> int:
    return await asyncio.to_thread(_add_sync, keyword, **kwargs)


def _search_sync(query: str, limit: int = 10) -> list:
    from telegram_bot.db.trend_models import TrendKeyword
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        return (
            db.query(TrendKeyword)
            .filter(TrendKeyword.keyword.contains(query.lower()))
            .order_by(TrendKeyword.priority.desc())
            .limit(limit)
            .all()
        )


async def search(query: str, limit: int = 10) -> list:
    return await asyncio.to_thread(_search_sync, query, limit)


def _list_sync(
    category: str | None = None,
    trend_level: str | None = None,
    limit: int = 20,
    sort: str = "priority",
) -> list:
    from telegram_bot.db.trend_models import TrendKeyword
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        q = db.query(TrendKeyword)
        if category:
            q = q.filter_by(category=category)
        if trend_level:
            q = q.filter_by(trend_level=trend_level)
        order_col = TrendKeyword.priority if sort == "priority" else TrendKeyword.created_at
        return q.order_by(order_col.desc()).limit(limit).all()


async def list_keywords(
    category: str | None = None,
    trend_level: str | None = None,
    limit: int = 20,
    sort: str = "priority",
) -> list:
    return await asyncio.to_thread(_list_sync, category, trend_level, limit, sort)


def _count_sync() -> int:
    from telegram_bot.db.trend_models import TrendKeyword
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        return db.query(TrendKeyword).count()


async def count() -> int:
    return await asyncio.to_thread(_count_sync)
