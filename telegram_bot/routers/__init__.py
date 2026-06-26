"""Router registry — all feature routers are imported and included here."""

from __future__ import annotations

from aiogram import Dispatcher

from telegram_bot.routers import (
    ai_generator,
    channel_analyzer,
    dashboard,
    materials,
    projects,
    settings_router,
    start,
    statistics,
    trend_analyzer,
    trends,
)


def register_routers(dp: Dispatcher) -> None:
    """Include every feature router into the dispatcher."""
    dp.include_router(start.router)
    dp.include_router(dashboard.router)
    dp.include_router(trends.router)
    dp.include_router(materials.router)
    dp.include_router(trend_analyzer.router)
    dp.include_router(channel_analyzer.router)
    dp.include_router(ai_generator.router)
    dp.include_router(projects.router)
    dp.include_router(statistics.router)
    dp.include_router(settings_router.router)
