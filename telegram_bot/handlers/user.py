"""End-user handlers: submit a topic, get a finished video back."""

from __future__ import annotations

import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from telegram_bot import service

WELCOME = (
    "🎬 <b>AI YouTube Factory</b>\n\n"
    "Send me a <b>topic</b> and I'll generate a vertical short for you.\n\n"
    "Examples:\n"
    "• <i>3 mind-blowing facts about the deep ocean</i>\n"
    "• <i>Why the Roman Empire really fell</i>\n\n"
    "Commands:\n"
    "/create &lt;topic&gt; — start a render\n"
    "/status &lt;job_id&gt; — check progress\n"
    "/help — show this message"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(WELCOME)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(WELCOME)


async def _create(update: Update, topic: str) -> None:
    topic = topic.strip()
    if len(topic) < 3:
        await update.message.reply_text("Please send a longer topic (at least 3 characters).")
        return
    user = update.effective_user
    chat = update.effective_chat
    res = await asyncio.to_thread(
        service.submit_topic, topic, telegram_id=user.id, chat_id=chat.id, name=user.full_name
    )
    if not res["ok"] and res.get("reason") == "limit":
        await update.message.reply_text(
            f"You've hit today's limit ({res['limit']} renders). Try again tomorrow."
        )
        return
    await update.message.reply_html(
        f"✅ Queued! Job <code>{res['job_id']}</code>\n"
        f"I'll send the video here when it's ready.\n"
        f"Check progress: /status {res['job_id']}"
    )


async def create_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _create(update, " ".join(context.args))


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Any plain text message is treated as a topic."""
    await _create(update, update.message.text)


async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /status <job_id>")
        return
    summary = await asyncio.to_thread(service.job_summary, context.args[0])
    await update.message.reply_html(summary or "Job not found.")
