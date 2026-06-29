"""AI Assistant Service — conversational helper using configured AI providers.

Provider preference: anthropic → openai → openrouter → gemini → local fallback.
Conversation history stored in DB (AssistantConversation).
All public functions are async.
"""
from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone


# ─────────────────────────────────────────────────────────────────
# PROVIDER SELECTION
# ─────────────────────────────────────────────────────────────────

_PREFERENCE_ORDER = ["anthropic", "openai", "openrouter", "gemini"]

_SYSTEM_PROMPT = (
    "You are an expert YouTube content creator assistant. "
    "You help plan videos, write scripts, generate titles, create prompts for AI image/video tools, "
    "and give SEO advice. You specialize in YouTube Shorts. "
    "Keep answers concise and actionable. Use bullet points when listing items. "
    "Always respond in the same language the user writes in."
)


def get_preferred_provider():
    """Return the first configured AI provider, or None if none configured."""
    try:
        from telegram_bot.services.integration_manager import manager
        for slug in _PREFERENCE_ORDER:
            p = manager.get(slug)
            if p and p.is_configured:
                return p
    except Exception:
        pass
    return None


async def chat_with_ai(message: str, history: list[dict]) -> str:
    """Send message + history to the best available provider. Returns reply text."""
    provider = get_preferred_provider()

    if provider is None:
        return _local_fallback(message)

    slug = provider.config.slug
    try:
        if slug == "anthropic":
            from telegram_bot.services.integrations.anthropic_provider import AnthropicProvider
            p = AnthropicProvider()
            msgs = history + [{"role": "user", "content": message}]
            reply = await p.complete(
                prompt=message,
                system=_SYSTEM_PROMPT,
                max_tokens=800,
            )
        elif slug in ("openai", "openrouter"):
            # Both use the same complete() interface
            msgs_text = "\n".join(
                f"{m['role'].upper()}: {m['content']}" for m in history[-4:]
            )
            full_prompt = f"{_SYSTEM_PROMPT}\n\n{msgs_text}\nUSER: {message}\nASSISTANT:"
            reply = await provider.complete(full_prompt, max_tokens=800)
        elif slug == "gemini":
            msgs_text = "\n".join(
                f"{m['role'].upper()}: {m['content']}" for m in history[-4:]
            )
            full_prompt = f"{_SYSTEM_PROMPT}\n\n{msgs_text}\nUSER: {message}"
            reply = await provider.complete(full_prompt, max_tokens=800)
        else:
            reply = _local_fallback(message)
    except Exception:
        reply = _local_fallback(message)

    return reply or _local_fallback(message)


def _local_fallback(message: str) -> str:
    """Template-based replies when no AI provider is configured."""
    msg = message.lower()

    if any(w in msg for w in ["idea", "g'oya", "идея", "mavzu"]):
        return (
            "💡 <b>5 ta Shorts g'oyasi:</b>\n\n"
            "1. 🦸 Superqahramon jangi — klassik va har doim ishlaydi\n"
            "2. 🎮 Tiles Hop challenge — trending game format\n"
            "3. 🔥 Epic transformation — character power-up\n"
            "4. ⚡ Speed run — 60 seconds race\n"
            "5. 🎭 Funny fail — comedy always wins\n\n"
            "<i>💡 AI provayderni ulang (ANTHROPIC_API_KEY) — aniqroq natijalar uchun.</i>"
        )
    if any(w in msg for w in ["title", "sarlavha", "заголовок", "nom"]):
        return (
            "🏷 <b>Title maslahatlar:</b>\n\n"
            "✅ Raqamlar ishlatish: '5 Epic Moments'\n"
            "✅ Savol formati: 'Can Spider-Man win?!'\n"
            "✅ Kuchli so'zlar: Epic, Ultimate, Insane, Shocking\n"
            "✅ Emoji birinchi yoki oxirida\n"
            "✅ 60 belgidan oshmasin\n\n"
            "<i>💡 AI provayderni ulang — topicga mos title uchun.</i>"
        )
    if any(w in msg for w in ["script", "skript", "стрипт"]):
        return (
            "📝 <b>Script tuzilmasi (60s Shorts):</b>\n\n"
            "⏱ 0:00–0:03 — HOOK (\"Wait...\", \"Did you see...\")\n"
            "⏱ 0:03–0:10 — Setup (muammo/conflict)\n"
            "⏱ 0:10–0:50 — Action (3-4 scene)\n"
            "⏱ 0:50–0:55 — Twist\n"
            "⏱ 0:55–1:00 — CTA (Like + Subscribe)\n\n"
            "<i>💡 Mavzuni ko'rsating — to'liq script yozib beraman (AI bilan).</i>"
        )
    if any(w in msg for w in ["thumbnail", "tumbnail", "rasm", "dizayn"]):
        return (
            "🎨 <b>Thumbnail maslahatlar:</b>\n\n"
            "✅ Yirik yuz va ifodali ko'zlar\n"
            "✅ Qizil/to'q sariq gradient background\n"
            "✅ 3 ta rang max (kontrast)\n"
            "✅ Katta shrift (30pt+)\n"
            "✅ 1280×720px, 16:9\n\n"
            "<i>💡 AI provayderni ulang — maxsus thumbnail prompt uchun.</i>"
        )

    return (
        "🤖 <b>AI Assistant</b>\n\n"
        "Quyidagilarda yordam bera olaman:\n\n"
        "• 💡 Video g'oyalari\n"
        "• 🏷 Title va sarlavhalar\n"
        "• 📝 Script yozish\n"
        "• 🎨 Thumbnail promptlar\n"
        "• 📈 SEO maslahatlar\n"
        "• 🎬 Shorts format bosqichlari\n\n"
        "Savolingizni yozing!\n\n"
        "<i>💡 AI provayderni ulang (Settings → Integrations) — yanada aqlli javoblar uchun.</i>"
    )


# ─────────────────────────────────────────────────────────────────
# CONVERSATION DB
# ─────────────────────────────────────────────────────────────────

def _load_conv_sync(session_id: str) -> list[dict]:
    from telegram_bot.db.automation_models import AssistantConversation
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        row = db.query(AssistantConversation).filter_by(session_id=session_id).first()
        if not row:
            return []
        try:
            return json.loads(row.messages_json)
        except Exception:
            return []


def _save_conv_sync(session_id: str, messages: list[dict], provider_slug: str = "") -> None:
    from telegram_bot.db.automation_models import AssistantConversation
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        row = db.query(AssistantConversation).filter_by(session_id=session_id).first()
        payload = json.dumps(messages, ensure_ascii=False)
        if row:
            row.messages_json  = payload
            row.total_messages = len(messages)
            row.provider_slug  = provider_slug
            row.updated_at     = datetime.now(timezone.utc)
        else:
            db.add(AssistantConversation(
                session_id=session_id,
                messages_json=payload,
                total_messages=len(messages),
                provider_slug=provider_slug,
            ))
        db.commit()


def _clear_conv_sync(session_id: str) -> None:
    from telegram_bot.db.automation_models import AssistantConversation
    from telegram_bot.db.session import SessionLocal

    with SessionLocal() as db:
        row = db.query(AssistantConversation).filter_by(session_id=session_id).first()
        if row:
            db.delete(row)
            db.commit()


async def load_conversation(session_id: str) -> list[dict]:
    return await asyncio.to_thread(_load_conv_sync, session_id)


async def save_conversation(session_id: str, messages: list[dict], provider_slug: str = "") -> None:
    await asyncio.to_thread(_save_conv_sync, session_id, messages, provider_slug)


async def clear_conversation(session_id: str) -> None:
    await asyncio.to_thread(_clear_conv_sync, session_id)
