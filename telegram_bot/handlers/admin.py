"""Admin command handlers — /stats, /recent, /cancel, /retry.

All commands are gated by the AdminOnlyMiddleware at the dispatcher level, so no
per-handler admin check is needed here.
"""

from __future__ import annotations

import asyncio

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from telegram_bot import service

router = Router(name="admin")


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    data = await asyncio.to_thread(service.stats)
    if not data:
        await message.answer("No jobs yet.")
        return
    lines = "\n".join(f"{k:10} {v}" for k, v in sorted(data.items()))
    await message.answer(f"📊 <b>Jobs by status</b>\n<pre>{lines}</pre>")


@router.message(Command("recent"))
async def cmd_recent(message: Message) -> None:
    rows = await asyncio.to_thread(service.recent, 8)
    body = "\n".join(rows) if rows else "none"
    await message.answer(f"🕒 <b>Recent jobs</b>\n<pre>{body}</pre>")


@router.message(Command("cancel"))
async def cmd_cancel(message: Message) -> None:
    args = message.text.split(maxsplit=1) if message.text else []
    if len(args) < 2:
        await message.answer("Usage: /cancel &lt;job_id&gt;")
        return
    ok = await asyncio.to_thread(service.cancel, args[1].strip())
    await message.answer("✅ Canceled." if ok else "Couldn't cancel that job.")


@router.message(Command("retry"))
async def cmd_retry(message: Message) -> None:
    args = message.text.split(maxsplit=1) if message.text else []
    if len(args) < 2:
        await message.answer("Usage: /retry &lt;job_id&gt;")
        return
    ok = await asyncio.to_thread(service.retry, args[1].strip())
    await message.answer("🔁 Requeued." if ok else "Couldn't requeue that job.")
