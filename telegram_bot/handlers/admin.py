"""Admin handlers: stats, recent jobs, cancel, retry. Gated by TELEGRAM_ADMIN_IDS."""

from __future__ import annotations

import asyncio
import functools

from telegram import Update
from telegram.ext import ContextTypes

from factory.core.config import settings
from telegram_bot import service


def admin_only(handler):
    @functools.wraps(handler)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in settings.admin_id_set:
            await update.message.reply_text("⛔ Admins only.")
            return
        return await handler(update, context)

    return wrapper


@admin_only
async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = await asyncio.to_thread(service.stats)
    if not data:
        await update.message.reply_text("No jobs yet.")
        return
    lines = "\n".join(f"{k:10} {v}" for k, v in sorted(data.items()))
    await update.message.reply_html(f"📊 <b>Jobs by status</b>\n<pre>{lines}</pre>")


@admin_only
async def recent_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    rows = await asyncio.to_thread(service.recent, 8)
    await update.message.reply_html("🕒 <b>Recent</b>\n<pre>" + ("\n".join(rows) or "none") + "</pre>")


@admin_only
async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /cancel <job_id>")
        return
    ok = await asyncio.to_thread(service.cancel, context.args[0])
    await update.message.reply_text("✅ Canceled." if ok else "Couldn't cancel that job.")


@admin_only
async def retry_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /retry <job_id>")
        return
    ok = await asyncio.to_thread(service.retry, context.args[0])
    await update.message.reply_text("🔁 Requeued." if ok else "Couldn't requeue that job.")
