"""Telegram bot entrypoint (long-polling).

Run: python -m telegram_bot.bot
Idles (instead of crash-looping) when TELEGRAM_BOT_TOKEN is unset, so the
container can stay up in stacks where the bot isn't configured yet.
"""

from __future__ import annotations

import time

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from factory.core.config import settings
from factory.core.logging import get_logger
from telegram_bot.handlers import admin, user

log = get_logger("telegram")


def build_app():
    app = ApplicationBuilder().token(settings.telegram_bot_token).build()

    # user
    app.add_handler(CommandHandler("start", user.start))
    app.add_handler(CommandHandler("help", user.help_cmd))
    app.add_handler(CommandHandler("create", user.create_cmd))
    app.add_handler(CommandHandler("status", user.status_cmd))

    # admin
    app.add_handler(CommandHandler("stats", admin.stats_cmd))
    app.add_handler(CommandHandler("recent", admin.recent_cmd))
    app.add_handler(CommandHandler("cancel", admin.cancel_cmd))
    app.add_handler(CommandHandler("retry", admin.retry_cmd))

    # plain text => topic
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user.on_text))
    return app


def main() -> None:
    if not settings.telegram_bot_token:
        log.warning("telegram.no_token_idle", msg="TELEGRAM_BOT_TOKEN unset; bot idling")
        while True:
            time.sleep(3600)

    log.info("telegram.starting", admins=len(settings.admin_id_set))
    app = build_app()
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
