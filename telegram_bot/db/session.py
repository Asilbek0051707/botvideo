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
    from telegram_bot.db import material_models      # noqa: F401 — registers Asset, AssetCollection, CollectionAsset, SearchHistory, PromptTemplate
    from telegram_bot.db import project_models       # noqa: F401 — registers ProjectMeta, ProjectTask, ProjectNote, ProjectResource
    from telegram_bot.db import integration_models  # noqa: F401 — registers ProviderStatus, SyncHistory, CacheEntry, ProviderLog
    from telegram_bot.db import automation_models   # noqa: F401 — registers AutomationRun, WorkflowTemplate, AutomationPackage, AssistantConversation, AutomationSettings

    Base.metadata.create_all(bind=engine)
