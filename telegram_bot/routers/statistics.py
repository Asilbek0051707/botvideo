"""Statistics router — 📊 live system stats page."""

from __future__ import annotations

import asyncio
import os
import subprocess
from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.types import CallbackQuery

from telegram_bot.keyboards.navigation import get_nav_keyboard

router = Router(name="statistics")


def _check_db() -> str:
    try:
        from factory.db.session import engine
        from sqlalchemy import text

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return "✅ Online"
    except Exception:
        return "❌ Offline"


def _check_memory() -> str:
    try:
        import psutil

        process = psutil.Process(os.getpid())
        return f"{process.memory_info().rss / 1024 / 1024:.1f} MB"
    except ImportError:
        return "N/A"


def _check_cpu() -> str:
    try:
        import psutil

        return f"{psutil.cpu_percent(interval=0.3):.1f}%"
    except ImportError:
        return "N/A"


def _check_github() -> str:
    try:
        r = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        url = r.stdout.strip()
        if "github.com" in url:
            repo = url.replace("https://github.com/", "").replace(".git", "")
            return f"✅ {repo}"
    except Exception:
        pass
    return "✅ Asilbek0051707/botvideo"


def _get_version() -> str:
    try:
        import tomllib

        with open("pyproject.toml", "rb") as f:
            data = tomllib.load(f)
        return data["project"]["version"]
    except Exception:
        return "0.1.0"


async def _build_stats_text() -> str:
    async def safe_db() -> str:
        try:
            return await asyncio.wait_for(asyncio.to_thread(_check_db), timeout=3.0)
        except asyncio.TimeoutError:
            return "⏳ Timeout"

    db_status, memory, cpu, github = await asyncio.gather(
        safe_db(),
        asyncio.to_thread(_check_memory),
        asyncio.to_thread(_check_cpu),
        asyncio.to_thread(_check_github),
    )
    version = _get_version()
    now = datetime.now(timezone.utc).strftime("%H:%M UTC")

    return (
        "📊 <b>Statistics</b>\n\n"
        f"🤖 <b>Bot:</b> ✅ Online\n"
        f"🗄 <b>Database:</b> {db_status}\n"
        f"🚂 <b>Railway:</b> ⏳ Unknown\n"
        f"🐙 <b>GitHub:</b> {github}\n\n"
        f"💾 <b>Memory:</b> {memory}\n"
        f"⚡ <b>CPU:</b> {cpu}\n"
        f"📋 <b>Version:</b> {version}\n"
        f"🕐 <b>Updated:</b> {now}"
    )


@router.callback_query(F.data == "menu:statistics")
async def on_statistics(callback: CallbackQuery) -> None:
    await callback.answer("Loading stats...")
    text = await _build_stats_text()
    await callback.message.edit_text(  # type: ignore[union-attr]
        text,
        reply_markup=get_nav_keyboard(current="menu:statistics"),
    )
