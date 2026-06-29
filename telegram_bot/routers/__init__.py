"""Router registry — all feature routers registered here."""

from __future__ import annotations

from aiogram import Dispatcher

from telegram_bot.routers import (
    ai_generator,
    channel_analyzer,
    characters,
    dashboard,
    favorites,
    integrations,
    material_library,
    materials,
    project_workspace,
    projects,
    search_router,
    settings_router,
    start,
    statistics,
    trend_analyzer,
    trend_keywords,
    trends,
    video_ideas,
    video_kit,
)


def register_routers(dp: Dispatcher) -> None:
    """Include every feature router into the dispatcher."""
    dp.include_router(start.router)
    dp.include_router(dashboard.router)
    dp.include_router(trends.router)
    dp.include_router(characters.router)
    dp.include_router(material_library.router)  # must be before materials.router
    dp.include_router(materials.router)
    # Trend Analyzer + sub-routers (order matters: sub-routers first)
    dp.include_router(video_ideas.router)
    dp.include_router(trend_keywords.router)
    dp.include_router(trend_analyzer.router)
    dp.include_router(project_workspace.router)  # must be before projects.router
    dp.include_router(channel_analyzer.router)
    dp.include_router(ai_generator.router)
    dp.include_router(projects.router)
    dp.include_router(statistics.router)
    dp.include_router(integrations.router)     # handles menu:integrations + set:integrations
    dp.include_router(settings_router.router)
    dp.include_router(favorites.router)
    dp.include_router(video_kit.router)
    dp.include_router(search_router.router)
