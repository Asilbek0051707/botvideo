"""Full Video Package Service — combine all generators into one bundle.

Calls every other generator service and returns a complete ContentPackageData.
Save to DB and Project Creator. Replace body with AI orchestration to upgrade.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field


@dataclass
class ContentPackageData:
    topic: str
    character: str
    category: str
    title: str
    description: str
    tags: list[str]
    hashtags: list[str]
    script: str
    thumbnail_prompt: str
    image_prompt: str
    video_prompt: str
    animation_prompt: str
    voice_prompt: str
    music_suggestions: list[dict]
    seo_summary: str


def _pick_category(topic: str) -> str:
    """Auto-detect category from topic keywords."""
    t = topic.lower()
    if any(w in t for w in ["anime", "naruto", "goku", "dragon ball", "one piece"]):
        return "anime"
    if any(w in t for w in ["minecraft", "roblox", "gaming", "game", "play"]):
        return "gaming"
    if any(w in t for w in ["bluey", "paw patrol", "peppa", "kids", "baby", "child"]):
        return "kids"
    if any(w in t for w in ["meme", "skibidi", "funny", "ohio", "brainrot"]):
        return "meme"
    if any(w in t for w in ["cartoon", "spider", "batman", "marvel", "animation"]):
        return "cartoon"
    return "general"


def generate_full_package(topic: str, character: str = "", category: str = "") -> ContentPackageData:
    """
    Generate a complete video package from templates.
    Replace this body with an AI orchestration call to upgrade.
    Same return type (ContentPackageData) — no router changes needed.
    """
    from telegram_bot.services.content_gen_service import (
        generate_titles, generate_description, generate_tags,
        generate_hashtags, generate_script, get_music_suggestions,
    )
    from telegram_bot.services.prompt_gen_service import (
        generate_thumbnail_prompt, generate_image_prompt,
        generate_video_prompt, generate_animation_prompt, generate_voice_prompt,
    )
    from telegram_bot.services.seo_service import calculate_seo_score, format_seo_result

    char = character or topic
    cat = category or _pick_category(topic)

    # Generate each component
    titles = generate_titles(topic, "clickbait")
    best_title = titles[0] if titles else f"{topic} 😱 #Shorts"

    description = generate_description(topic, "seo")
    tags = generate_tags(topic, "main")
    hashtags = generate_hashtags(topic, "trending")
    script = generate_script(topic, "shorts")
    thumb_prompt = generate_thumbnail_prompt(char, "gpt")
    img_prompt = generate_image_prompt(char, "character")
    vid_prompt = generate_video_prompt(char, "runway")
    anim_prompt = generate_animation_prompt(char, "battle")
    voice_p = generate_voice_prompt(char, "narration")
    music = get_music_suggestions(cat if cat in ("action", "funny", "kids", "gaming", "epic", "battle") else "action")

    seo_result = calculate_seo_score(best_title, "", tags)
    seo_summary = format_seo_result(seo_result, best_title)

    return ContentPackageData(
        topic=topic,
        character=char,
        category=cat,
        title=best_title,
        description=description,
        tags=tags,
        hashtags=hashtags,
        script=script,
        thumbnail_prompt=thumb_prompt,
        image_prompt=img_prompt,
        video_prompt=vid_prompt,
        animation_prompt=anim_prompt,
        voice_prompt=voice_p,
        music_suggestions=music,
        seo_summary=seo_summary,
    )


def format_package_summary(pkg: ContentPackageData) -> str:
    """Format a short summary for Telegram (2048 char limit per message)."""
    tags_str = ", ".join(pkg.tags[:8])
    ht_str = " ".join(pkg.hashtags[:8])
    music_str = " | ".join(m["title"] for m in pkg.music_suggestions[:3])

    return (
        f"📦 <b>Full Video Package: {pkg.topic}</b>\n\n"
        f"🏷 <b>Title:</b>\n<code>{pkg.title}</code>\n\n"
        f"🏷 <b>Tags:</b>\n<code>{tags_str}</code>\n\n"
        f"# <b>Hashtags:</b>\n<code>{ht_str}</code>\n\n"
        f"🎵 <b>Music:</b> {music_str}\n\n"
        f"📊 <b>Kategoriya:</b> {pkg.category}\n"
        f"🦸 <b>Karakter:</b> {pkg.character}"
    )


def _save_package_sync(pkg: ContentPackageData) -> int:
    from telegram_bot.db.ai_generator_models import ContentPackage
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        row = ContentPackage(
            topic=pkg.topic[:300],
            character=pkg.character[:200],
            category=pkg.category[:50],
            title=pkg.title,
            description=pkg.description,
            tags=json.dumps(pkg.tags),
            hashtags=json.dumps(pkg.hashtags),
            script=pkg.script,
            thumbnail_prompt=pkg.thumbnail_prompt,
            image_prompt=pkg.image_prompt,
            video_prompt=pkg.video_prompt,
            animation_prompt=pkg.animation_prompt,
            voice_prompt=pkg.voice_prompt,
            music_suggestions=json.dumps([m["title"] for m in pkg.music_suggestions]),
            seo_summary=pkg.seo_summary,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row.id


async def save_package(pkg: ContentPackageData) -> int:
    return await asyncio.to_thread(_save_package_sync, pkg)


def _list_packages_sync(limit: int = 8) -> list:
    from telegram_bot.db.ai_generator_models import ContentPackage
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        return db.query(ContentPackage).order_by(ContentPackage.created_at.desc()).limit(limit).all()


async def list_packages(limit: int = 8) -> list:
    return await asyncio.to_thread(_list_packages_sync, limit)


def _delete_package_sync(pkg_id: int) -> bool:
    from telegram_bot.db.ai_generator_models import ContentPackage
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        row = db.get(ContentPackage, pkg_id)
        if not row:
            return False
        db.delete(row)
        db.commit()
        return True


async def delete_package(pkg_id: int) -> bool:
    return await asyncio.to_thread(_delete_package_sync, pkg_id)
