"""SQLite engine for bot-local data (projects, favourites).

Uses SQLite so the bot works without a PostgreSQL server in dev/Railway.
Data is stored in bot_data.db relative to the working directory.
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Always SQLite for bot-specific data (projects/favourites).
# Fast, zero-config, single-admin concurrency is fine.
_DB_PATH = Path.cwd() / "bot_data.db"
_DB_URL = f"sqlite:///{_DB_PATH}"

engine = create_engine(
    _DB_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db() -> None:
    """Create all bot tables (idempotent — safe to call on every startup)."""
    from telegram_bot.db.models import Base          # noqa: F401 — registers Project, Favourite
    from telegram_bot.db import trend_models         # noqa: F401 — registers Trend, TrendKeyword, VideoIdea, TrendSettings
    from telegram_bot.db import channel_models       # noqa: F401 — registers ChannelRecord, VideoRecord, CompetitorRecord, AnalysisReport, SEORecord, GrowthSnapshot
    from telegram_bot.db import ai_generator_models  # noqa: F401 — registers GeneratedContent, AITemplate, ContentPackage

    Base.metadata.create_all(bind=engine)
