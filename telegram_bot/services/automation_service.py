"""Automation Service — orchestrates all content generators for Step 10.

quick_generate(topic)  → runs all generators in parallel, returns dict
full_package(topic)    → calls package_service, returns formatted summary
create_project(idea)   → creates Project with metadata, returns project_id
execute_workflow(...)  → runs a named step chain in sequence

All public functions are async.
No generator logic is duplicated — delegates to existing STEP 6 services.
"""
from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


# ─────────────────────────────────────────────────────────────────
# DATA STRUCTURES
# ─────────────────────────────────────────────────────────────────

@dataclass
class QuickResult:
    topic:            str
    video_idea:       str = ""
    script:           str = ""
    titles:           list[str] = field(default_factory=list)
    description:      str = ""
    tags:             list[str] = field(default_factory=list)
    hashtags:         list[str] = field(default_factory=list)
    thumbnail_prompt: str = ""
    image_prompt:     str = ""
    animation_prompt: str = ""
    voice_prompt:     str = ""
    music:            list[dict] = field(default_factory=list)
    seo_summary:      str = ""
    upload_time:      str = ""
    duration_ms:      int = 0

    def to_dict(self) -> dict:
        return {
            "topic":            self.topic,
            "video_idea":       self.video_idea,
            "script":           self.script,
            "titles":           self.titles,
            "description":      self.description,
            "tags":             self.tags,
            "hashtags":         self.hashtags,
            "thumbnail_prompt": self.thumbnail_prompt,
            "image_prompt":     self.image_prompt,
            "animation_prompt": self.animation_prompt,
            "voice_prompt":     self.voice_prompt,
            "music":            self.music,
            "seo_summary":      self.seo_summary,
            "upload_time":      self.upload_time,
        }


# ─────────────────────────────────────────────────────────────────
# SETTINGS
# ─────────────────────────────────────────────────────────────────

def _get_settings_sync():
    from telegram_bot.db.automation_models import AutomationSettings
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        row = db.get(AutomationSettings, 1)
        if not row:
            row = AutomationSettings(id=1)
            db.add(row)
            db.commit()
            db.refresh(row)
        return row


async def get_settings() -> Any:
    return await asyncio.to_thread(_get_settings_sync)


def _update_settings_sync(**kwargs) -> None:
    from telegram_bot.db.automation_models import AutomationSettings
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        row = db.get(AutomationSettings, 1)
        if not row:
            row = AutomationSettings(id=1)
            db.add(row)
        for k, v in kwargs.items():
            if hasattr(row, k):
                setattr(row, k, v)
        db.commit()


async def update_settings(**kwargs) -> None:
    await asyncio.to_thread(_update_settings_sync, **kwargs)


# ─────────────────────────────────────────────────────────────────
# RUN HISTORY
# ─────────────────────────────────────────────────────────────────

def _save_run_sync(
    topic: str,
    run_type: str,
    result: dict,
    provider_slug: str = "local",
    status: str = "done",
    error_msg: str = "",
    duration_ms: int = 0,
) -> int:
    from telegram_bot.db.automation_models import AutomationRun
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        run = AutomationRun(
            topic=topic[:299],
            run_type=run_type,
            provider_slug=provider_slug,
            status=status,
            result_json=json.dumps(result, ensure_ascii=False, default=str),
            error_msg=error_msg[:499],
            duration_ms=duration_ms,
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        return run.id


async def save_run(
    topic: str,
    run_type: str,
    result: dict,
    provider_slug: str = "local",
    status: str = "done",
    error_msg: str = "",
    duration_ms: int = 0,
) -> int:
    return await asyncio.to_thread(
        _save_run_sync, topic, run_type, result, provider_slug, status, error_msg, duration_ms
    )


def _list_runs_sync(run_type: str | None, favorites_only: bool, limit: int) -> list:
    from telegram_bot.db.automation_models import AutomationRun
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        q = db.query(AutomationRun)
        if run_type:
            q = q.filter_by(run_type=run_type)
        if favorites_only:
            q = q.filter_by(is_favorite=True)
        return q.order_by(AutomationRun.created_at.desc()).limit(limit).all()


async def list_runs(
    run_type: str | None = None,
    favorites_only: bool = False,
    limit: int = 20,
) -> list:
    return await asyncio.to_thread(_list_runs_sync, run_type, favorites_only, limit)


def _get_run_sync(run_id: int):
    from telegram_bot.db.automation_models import AutomationRun
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        return db.get(AutomationRun, run_id)


async def get_run(run_id: int):
    return await asyncio.to_thread(_get_run_sync, run_id)


def _toggle_favorite_run_sync(run_id: int) -> bool:
    from telegram_bot.db.automation_models import AutomationRun
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        run = db.get(AutomationRun, run_id)
        if not run:
            return False
        run.is_favorite = not run.is_favorite
        db.commit()
        return run.is_favorite


async def toggle_favorite_run(run_id: int) -> bool:
    return await asyncio.to_thread(_toggle_favorite_run_sync, run_id)


def _delete_run_sync(run_id: int) -> bool:
    from telegram_bot.db.automation_models import AutomationRun
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        run = db.get(AutomationRun, run_id)
        if not run:
            return False
        db.delete(run)
        db.commit()
        return True


async def delete_run(run_id: int) -> bool:
    return await asyncio.to_thread(_delete_run_sync, run_id)


def _run_stats_sync() -> dict:
    from telegram_bot.db.automation_models import AutomationRun
    from telegram_bot.db.session import SessionLocal
    from sqlalchemy import func

    with SessionLocal() as db:
        total = db.query(func.count(AutomationRun.id)).scalar() or 0
        favs  = db.query(func.count(AutomationRun.id)).filter_by(is_favorite=True).scalar() or 0
        by_type = {}
        for row in db.query(AutomationRun.run_type, func.count(AutomationRun.id)).group_by(AutomationRun.run_type).all():
            by_type[row[0]] = row[1]
        return {"total": total, "favorites": favs, "by_type": by_type}


async def run_stats() -> dict:
    return await asyncio.to_thread(_run_stats_sync)


# ─────────────────────────────────────────────────────────────────
# PACKAGE SAVE
# ─────────────────────────────────────────────────────────────────

def _save_package_sync(topic: str, content: dict, run_id: int = 0) -> int:
    from telegram_bot.db.automation_models import AutomationPackage
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        pkg = AutomationPackage(
            topic=topic[:299],
            content_json=json.dumps(content, ensure_ascii=False, default=str),
            run_id=run_id,
        )
        db.add(pkg)
        db.commit()
        db.refresh(pkg)
        return pkg.id


async def save_package(topic: str, content: dict, run_id: int = 0) -> int:
    return await asyncio.to_thread(_save_package_sync, topic, content, run_id)


# ─────────────────────────────────────────────────────────────────
# QUICK GENERATE
# ─────────────────────────────────────────────────────────────────

_SEO_TEMPLATES = [
    "Focus on: keywords in first 3 words of title; description starts with main keyword; "
    "add 5 related tags; upload Tue–Thu 3–5 PM.",
    "Best practice: title under 60 chars; custom thumbnail with face; "
    "add chapters in description; use 3–5 hashtags.",
    "Growth tip: reply to every comment in first hour; "
    "share to community post; end screen + cards on all videos.",
]

_UPLOAD_TIMES = [
    "🕐 Optimal: Tuesday 14:00–16:00 UTC",
    "🕐 Optimal: Wednesday 18:00–20:00 UTC",
    "🕐 Optimal: Thursday 15:00–17:00 UTC",
    "🕐 Optimal: Friday 12:00–14:00 UTC",
    "🕐 Optimal: Saturday 10:00–13:00 UTC",
]

_VIDEO_IDEA_TPL = (
    "💡 <b>Video Idea</b>\n\n"
    "🎯 Title concept: {t} — Ultimate Battle\n"
    "📺 Format: YouTube Shorts (60s)\n"
    "🎬 Style: Action / Gaming\n"
    "🎭 Hook: Unexpected power reveal at 0:05\n"
    "📈 Estimated views: 50K–500K (trending topic)\n"
    "🔄 Series potential: Yes — character universe"
)


async def quick_generate(topic: str) -> QuickResult:
    """Run all generators in parallel and return a QuickResult."""
    from telegram_bot.services.content_gen_service import (
        generate_script,
        generate_titles,
        generate_description,
        generate_tags,
        generate_hashtags,
        get_music_suggestions,
    )
    from telegram_bot.services.prompt_gen_service import (
        generate_thumbnail_prompt,
        generate_image_prompt,
        generate_animation_prompt,
        generate_voice_prompt,
    )
    import random

    t0 = time.monotonic()

    # All sync generators — run in parallel via to_thread
    (
        script, titles, description, tags, hashtags,
        thumb_prompt, image_prompt, anim_prompt, voice_prompt, music
    ) = await asyncio.gather(
        asyncio.to_thread(generate_script, topic, "shorts"),
        asyncio.to_thread(generate_titles, topic, "short"),
        asyncio.to_thread(generate_description, topic, "seo"),
        asyncio.to_thread(generate_tags, topic, "main"),
        asyncio.to_thread(generate_hashtags, topic, "trending"),
        asyncio.to_thread(generate_thumbnail_prompt, topic, "gpt"),
        asyncio.to_thread(generate_image_prompt, topic, "character"),
        asyncio.to_thread(generate_animation_prompt, topic, "idle"),
        asyncio.to_thread(generate_voice_prompt, topic, "narration"),
        asyncio.to_thread(get_music_suggestions, "action"),
    )

    duration_ms = int((time.monotonic() - t0) * 1000)

    return QuickResult(
        topic=topic,
        video_idea=_VIDEO_IDEA_TPL.replace("{t}", topic),
        script=script,
        titles=titles[:5],
        description=description,
        tags=tags[:20],
        hashtags=hashtags[:10],
        thumbnail_prompt=thumb_prompt,
        image_prompt=image_prompt,
        animation_prompt=anim_prompt,
        voice_prompt=voice_prompt,
        music=music[:3],
        seo_summary=random.choice(_SEO_TEMPLATES),
        upload_time=random.choice(_UPLOAD_TIMES),
        duration_ms=duration_ms,
    )


# ─────────────────────────────────────────────────────────────────
# FULL VIDEO PACKAGE
# ─────────────────────────────────────────────────────────────────

async def full_package(topic: str) -> dict:
    """Generate a complete package and save it. Returns formatted dict."""
    from telegram_bot.services.package_service import generate_full_package, format_package_summary

    t0 = time.monotonic()
    pkg = await asyncio.to_thread(generate_full_package, topic)
    duration_ms = int((time.monotonic() - t0) * 1000)
    summary     = format_package_summary(pkg)
    return {
        "topic":       topic,
        "summary":     summary,
        "duration_ms": duration_ms,
        "package":     pkg.__dict__ if hasattr(pkg, "__dict__") else str(pkg),
    }


# ─────────────────────────────────────────────────────────────────
# CREATE PROJECT FROM IDEA
# ─────────────────────────────────────────────────────────────────

async def create_project_from_idea(idea: str) -> int:
    """Create a Project row + default tasks from a free-form idea string.

    Returns the new project_id.
    """
    from telegram_bot.services.project_service import add_task

    # Detect character/category from idea (simple heuristic)
    words       = idea.strip().split()
    char_name   = words[0] if words else "Character"
    category    = "Gaming" if any(w.lower() in idea.lower() for w in
                                  ["minecraft","roblox","tiles","hop","gaming"]) else "YouTube Shorts"

    project_id  = await _create_project_sync(idea, char_name, category)

    # Seed default tasks
    default_tasks = [
        "✍️ Script yozish",
        "🎨 Thumbnail dizayn",
        "🎬 Video montaj",
        "🔊 Ovoz qo'shish",
        "📤 Upload va SEO",
    ]
    for title in default_tasks:
        await add_task(project_id, title)

    return project_id


def _create_project_sync(name: str, char_name: str, category: str) -> int:
    from telegram_bot.db.models import Project
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        p = Project(
            name=name[:200],
            character_name=char_name[:100],
            category_name=category[:100],
            status="idea",
        )
        db.add(p)
        db.commit()
        db.refresh(p)
        return p.id


async def _create_project_sync_async(name: str, char_name: str, category: str) -> int:
    return await asyncio.to_thread(_create_project_sync, name, char_name, category)


# ─────────────────────────────────────────────────────────────────
# WORKFLOW ENGINE
# ─────────────────────────────────────────────────────────────────

BUILTIN_WORKFLOW_STEPS: dict[str, str] = {
    "script":       "📝 Script",
    "title":        "🏷 Title",
    "description":  "📄 Description",
    "tags":         "#️⃣ Tags",
    "hashtags":     "🔥 Hashtags",
    "thumbnail":    "🎨 Thumbnail Prompt",
    "image":        "🖼 Image Prompt",
    "animation":    "🎥 Animation Prompt",
    "voice":        "🎙 Voice Prompt",
    "music":        "🎵 Music",
    "seo":          "📈 SEO",
    "project":      "📁 Create Project",
}

BUILTIN_WORKFLOWS: list[dict] = [
    {
        "name": "🚀 Quick Shorts",
        "description": "Script → Title → Tags → Hashtags",
        "steps": ["script", "title", "tags", "hashtags"],
    },
    {
        "name": "🎨 Full Prompts",
        "description": "Thumbnail → Image → Animation → Voice",
        "steps": ["thumbnail", "image", "animation", "voice"],
    },
    {
        "name": "📈 SEO Pack",
        "description": "Title → Description → Tags → Hashtags → SEO",
        "steps": ["title", "description", "tags", "hashtags", "seo"],
    },
    {
        "name": "🏆 Complete",
        "description": "Script → Title → Description → Tags → Prompts → Project",
        "steps": ["script", "title", "description", "tags", "thumbnail", "image", "project"],
    },
]


async def execute_workflow(topic: str, steps: list[str]) -> dict:
    """Execute a list of step keys and return results dict."""
    from telegram_bot.services.content_gen_service import (
        generate_script, generate_titles, generate_description,
        generate_tags, generate_hashtags,
    )
    from telegram_bot.services.prompt_gen_service import (
        generate_thumbnail_prompt, generate_image_prompt,
        generate_animation_prompt, generate_voice_prompt,
    )
    from telegram_bot.services.content_gen_service import get_music_suggestions

    t0 = time.monotonic()
    results: dict[str, Any] = {"topic": topic, "steps": []}

    for step in steps:
        try:
            if step == "script":
                results["script"] = await asyncio.to_thread(generate_script, topic, "shorts")
            elif step == "title":
                results["titles"] = await asyncio.to_thread(generate_titles, topic, "short")
            elif step == "description":
                results["description"] = await asyncio.to_thread(generate_description, topic, "seo")
            elif step == "tags":
                results["tags"] = await asyncio.to_thread(generate_tags, topic, "main")
            elif step == "hashtags":
                results["hashtags"] = await asyncio.to_thread(generate_hashtags, topic, "trending")
            elif step == "thumbnail":
                results["thumbnail_prompt"] = await asyncio.to_thread(generate_thumbnail_prompt, topic, "gpt")
            elif step == "image":
                results["image_prompt"] = await asyncio.to_thread(generate_image_prompt, topic, "character")
            elif step == "animation":
                results["animation_prompt"] = await asyncio.to_thread(generate_animation_prompt, topic, "idle")
            elif step == "voice":
                results["voice_prompt"] = await asyncio.to_thread(generate_voice_prompt, topic, "narration")
            elif step == "music":
                results["music"] = await asyncio.to_thread(get_music_suggestions, "action")
            elif step == "seo":
                import random
                results["seo"] = random.choice(_SEO_TEMPLATES)
            elif step == "project":
                results["project_id"] = await create_project_from_idea(topic)
            results["steps"].append({"key": step, "status": "ok"})
        except Exception as exc:
            results["steps"].append({"key": step, "status": "error", "msg": str(exc)})

    results["duration_ms"] = int((time.monotonic() - t0) * 1000)
    return results


# ─────────────────────────────────────────────────────────────────
# WORKFLOW TEMPLATES (DB)
# ─────────────────────────────────────────────────────────────────

def _list_workflow_templates_sync() -> list:
    from telegram_bot.db.automation_models import WorkflowTemplate
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        return db.query(WorkflowTemplate).filter_by(is_active=True).order_by(WorkflowTemplate.id).all()


async def list_workflow_templates() -> list:
    return await asyncio.to_thread(_list_workflow_templates_sync)


def _seed_workflows_sync() -> None:
    from telegram_bot.db.automation_models import WorkflowTemplate
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        count = db.query(WorkflowTemplate).count()
        if count > 0:
            return
        for wf in BUILTIN_WORKFLOWS:
            db.add(WorkflowTemplate(
                name=wf["name"],
                description=wf["description"],
                steps_json=json.dumps(wf["steps"]),
                is_default=True,
            ))
        db.commit()


async def seed_workflows() -> None:
    await asyncio.to_thread(_seed_workflows_sync)


# ─────────────────────────────────────────────────────────────────
# FORMAT HELPERS
# ─────────────────────────────────────────────────────────────────

def format_quick_result_summary(r: QuickResult) -> str:
    """Short summary card (fits in one Telegram message)."""
    titles_str = "\n".join(f"  {i+1}. {t}" for i, t in enumerate(r.titles[:3]))
    tags_str   = " ".join(r.tags[:8])
    hash_str   = " ".join(r.hashtags[:5])
    music_str  = r.music[0]["title"] if r.music else "—"
    return (
        f"⚡ <b>Quick Generate: {r.topic}</b>\n"
        f"⏱ {r.duration_ms}ms\n\n"
        f"💡 <b>Titles (top 3):</b>\n{titles_str}\n\n"
        f"🏷 <b>Tags:</b> <code>{tags_str}</code>\n\n"
        f"🔥 <b>Hashtags:</b> {hash_str}\n\n"
        f"🎵 <b>Music:</b> {music_str}\n\n"
        f"📈 <b>SEO:</b> <i>{r.seo_summary}</i>\n\n"
        f"{r.upload_time}"
    )
