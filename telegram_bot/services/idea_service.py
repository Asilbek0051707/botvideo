"""Video Idea Generator — template-based idea engine with DB persistence.

Templates are data-driven. Add new templates to _IDEA_TEMPLATES to expand
the generator without touching any handler code.
"""

from __future__ import annotations

import asyncio
import json
import random

# ── Idea templates — add unlimited entries here ───────────────────

_IDEA_TEMPLATES: list[dict] = [
    {
        "type": "vs",
        "title": "{char1} vs {char2}",
        "desc": "Ikki karakter o'rtasidagi epik jang!",
        "audience": "kids",
        "length": "60s",
        "keywords": ["vs", "battle", "fight"],
    },
    {
        "type": "evolution",
        "title": "{char} — Evolution Timeline",
        "desc": "Karterdning barcha versiyalari, eng zaifidan eng kuchligisiga",
        "audience": "kids+teens",
        "length": "45–60s",
        "keywords": ["evolution", "timeline", "transformation"],
    },
    {
        "type": "color_challenge",
        "title": "{char} Color Challenge",
        "desc": "Karakter turli ranglarda — qaysi biri eng yaxshi?",
        "audience": "kids",
        "length": "30s",
        "keywords": ["color", "challenge", "trending"],
    },
    {
        "type": "impossible",
        "title": "Impossible {char} Challenge",
        "desc": "Karakter imkonsiz vaziyatni yechishi",
        "audience": "kids+teens",
        "length": "45s",
        "keywords": ["impossible", "challenge", "viral"],
    },
    {
        "type": "guess",
        "title": "Guess the {char}!",
        "desc": "Tomoshabin karterni topishi kerak — qiziqarli puzzle format",
        "audience": "kids",
        "length": "30s",
        "keywords": ["guess", "puzzle", "quiz"],
    },
    {
        "type": "transformation",
        "title": "{char} Transformation",
        "desc": "Karakter o'zgarishi — baby versiyasidan ultra versiyasigacha",
        "audience": "kids",
        "length": "45s",
        "keywords": ["transformation", "glow up", "evolution"],
    },
    {
        "type": "funny_story",
        "title": "Funny {char} Story",
        "desc": "Hazilomuz animatsion qisqa hikoya",
        "audience": "kids",
        "length": "60s",
        "keywords": ["funny", "story", "animation"],
    },
    {
        "type": "ai_story",
        "title": "AI {char} Adventure",
        "desc": "Sun'iy intellekt yaratgan original hikoya",
        "audience": "teens",
        "length": "60s",
        "keywords": ["ai", "story", "adventure"],
    },
    {
        "type": "top10",
        "title": "Top 10 {char} Moments",
        "desc": "Eng kulgili / eng kuchli / eng zo'r 10 ta lahza",
        "audience": "all",
        "length": "60s",
        "keywords": ["top 10", "compilation", "moments"],
    },
    {
        "type": "reaction",
        "title": "{char} Reacts to {char2}",
        "desc": "Bitta karakter boshqasining harakatlariga munosabat bildiradi",
        "audience": "kids+teens",
        "length": "45s",
        "keywords": ["reaction", "funny", "viral"],
    },
    {
        "type": "comparison",
        "title": "{char1} vs {char2} — Kuchlar Taqqoslanishi",
        "desc": "Ikkita karterni kuch, tezlik va maxorat bo'yicha taqqoslash",
        "audience": "kids",
        "length": "60s",
        "keywords": ["comparison", "vs", "power level"],
    },
    {
        "type": "battle",
        "title": "ULTIMATE BATTLE: {char1} vs {char2}",
        "desc": "Epik jang — kim yutadi?",
        "audience": "kids+teens",
        "length": "60s",
        "keywords": ["battle", "fight", "epic"],
    },
    {
        "type": "mystery",
        "title": "{char} Mystery — Kim qildi?",
        "desc": "Qiziqarli sirli hikoya — oxirigacha qolib tur!",
        "audience": "kids",
        "length": "60s",
        "keywords": ["mystery", "secret", "hidden"],
    },
    {
        "type": "random",
        "title": "Random {char} Generator!",
        "desc": "Tasodifiy karakter kombinatsiyalari — kim chiqadi?",
        "audience": "kids",
        "length": "30–45s",
        "keywords": ["random", "generator", "trending"],
    },
    {
        "type": "rescue",
        "title": "{char} Rescues {char2}",
        "desc": "Qahramonlik hikoyasi — kimni qutqaradi?",
        "audience": "kids",
        "length": "60s",
        "keywords": ["rescue", "hero", "story"],
    },
    {
        "type": "baby",
        "title": "Baby {char} Adventures",
        "desc": "Sevimli karterdning baby versiyasidagi quvnoq sarguzashtlar",
        "audience": "kids",
        "length": "30–45s",
        "keywords": ["baby", "cute", "adventure"],
    },
    {
        "type": "team_up",
        "title": "{char1} + {char2} Team Up!",
        "desc": "Ikkita karakter birlashib muammoni hal qiladi",
        "audience": "kids",
        "length": "60s",
        "keywords": ["team", "collab", "adventure"],
    },
    {
        "type": "school",
        "title": "{char} Goes to School",
        "desc": "Karakter maktabda — kulgili va ta'limiy",
        "audience": "kids",
        "length": "45–60s",
        "keywords": ["school", "funny", "kids"],
    },
    {
        "type": "size_challenge",
        "title": "Giant {char1} vs Tiny {char2}",
        "desc": "O'lchov farqi — katta va kichik karakter birgalikda",
        "audience": "kids",
        "length": "30s",
        "keywords": ["giant", "tiny", "comparison"],
    },
    {
        "type": "cursed",
        "title": "Cursed {char} Forms",
        "desc": "Karterdning eng g'ayrioddiy va kulgili versiyalari",
        "audience": "teens",
        "length": "30–45s",
        "keywords": ["cursed", "funny", "meme"],
    },
]

_CHAR2_POOL = [
    "Batman", "Goku", "Sonic", "Spider-Man", "Pikachu",
    "Optimus Prime", "Mario", "Iron Man", "Thor", "Hulk",
    "Naruto", "Luffy", "Saitama", "Minions", "Elsa",
]


def generate_ideas(
    character: str,
    category: str = "general",
    count: int = 6,
) -> list[dict]:
    """Return `count` filled idea templates for the given character."""
    char2 = random.choice([c for c in _CHAR2_POOL if c.lower() != character.lower()])

    rng = random.Random(character.lower() + category)
    pool = list(_IDEA_TEMPLATES)
    rng.shuffle(pool)
    selected = pool[:count]

    ideas = []
    for t in selected:
        title = t["title"].format(char=character, char1=character, char2=char2)
        ideas.append({
            "type": t["type"],
            "title": title,
            "description": t["desc"],
            "character": character,
            "category": category,
            "audience": t.get("audience", "all"),
            "length": t.get("length", "60s"),
            "keywords": t.get("keywords", []),
        })
    return ideas


def search_templates(keyword: str) -> list[dict]:
    """Return templates whose type or desc matches keyword."""
    kl = keyword.lower()
    matched = [
        t for t in _IDEA_TEMPLATES
        if kl in t["type"]
        or kl in t["desc"].lower()
        or any(kl in kw for kw in t.get("keywords", []))
    ]
    return matched or _IDEA_TEMPLATES[:6]


# ── DB persistence ────────────────────────────────────────────────


def _save_idea_sync(
    title: str,
    description: str,
    character: str,
    category: str,
    score: int,
    keywords: list[str],
    project_id: int | None = None,
) -> int:
    from telegram_bot.db.trend_models import VideoIdea
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        idea = VideoIdea(
            title=title,
            description=description,
            character=character,
            category=category,
            trend_score=score,
            keywords=json.dumps(keywords),
            status="saved",
            project_id=project_id,
        )
        db.add(idea)
        db.commit()
        db.refresh(idea)
        return idea.id


async def save_idea(
    title: str,
    description: str,
    character: str = "",
    category: str = "general",
    score: int = 0,
    keywords: list[str] | None = None,
    project_id: int | None = None,
) -> int:
    return await asyncio.to_thread(
        _save_idea_sync,
        title, description, character, category, score,
        keywords or [], project_id,
    )


def _list_ideas_sync(
    limit: int = 20,
    status: str | None = None,
    category: str | None = None,
) -> list:
    from telegram_bot.db.trend_models import VideoIdea
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        q = db.query(VideoIdea)
        if status:
            q = q.filter_by(status=status)
        if category:
            q = q.filter_by(category=category)
        return q.order_by(VideoIdea.created_at.desc()).limit(limit).all()


async def list_ideas(
    limit: int = 20,
    status: str | None = None,
    category: str | None = None,
) -> list:
    return await asyncio.to_thread(_list_ideas_sync, limit, status, category)


def _search_ideas_sync(query: str, limit: int = 10) -> list:
    from telegram_bot.db.trend_models import VideoIdea
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        return (
            db.query(VideoIdea)
            .filter(
                VideoIdea.title.contains(query)
                | VideoIdea.character.contains(query)
                | VideoIdea.keywords.contains(query)
            )
            .order_by(VideoIdea.trend_score.desc())
            .limit(limit)
            .all()
        )


async def search_ideas(query: str, limit: int = 10) -> list:
    return await asyncio.to_thread(_search_ideas_sync, query, limit)


def _delete_idea_sync(idea_id: int) -> bool:
    from telegram_bot.db.trend_models import VideoIdea
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        idea = db.get(VideoIdea, idea_id)
        if not idea:
            return False
        db.delete(idea)
        db.commit()
        return True


async def delete_idea(idea_id: int) -> bool:
    return await asyncio.to_thread(_delete_idea_sync, idea_id)


def _count_ideas_sync() -> int:
    from telegram_bot.db.trend_models import VideoIdea
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        return db.query(VideoIdea).count()


async def count_ideas() -> int:
    return await asyncio.to_thread(_count_ideas_sync)
