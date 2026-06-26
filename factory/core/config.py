"""Central typed configuration, loaded once from the environment.

Every service imports `settings` from here. Nothing else should read os.environ.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False
    )

    # ---- App ----
    app_name: str = "AI YouTube Factory"
    env: Literal["development", "staging", "production"] = "development"
    log_level: str = "INFO"
    secret_key: str = "change-me"
    public_base_url: str = "http://localhost:8000"
    api_keys: str = "devkey-change-me"  # comma-separated

    # ---- Postgres ----
    postgres_user: str = "factory"
    postgres_password: str = "factory"
    postgres_db: str = "factory"
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    database_url: str | None = None

    # ---- Redis / Celery ----
    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: str = "redis://redis:6379/1"
    celery_result_backend: str = "redis://redis:6379/2"

    # ---- Storage ----
    storage_backend: Literal["local", "minio", "s3", "supabase"] = "minio"
    storage_bucket: str = "factory"
    storage_public: bool = True
    local_storage_dir: str = "/data/storage"
    s3_endpoint_url: str | None = None
    s3_region: str = "us-east-1"
    s3_access_key_id: str | None = None
    s3_secret_access_key: str | None = None
    s3_public_endpoint: str | None = None
    supabase_url: str | None = None
    supabase_service_key: str | None = None
    supabase_storage_bucket: str = "factory"

    # ---- LLM ----
    llm_provider: Literal["anthropic", "openai", "mock"] = "mock"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-4-6"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    # ---- TTS ----
    tts_provider: Literal["elevenlabs", "openai", "mock"] = "mock"
    elevenlabs_api_key: str | None = None
    elevenlabs_voice_id: str = "Rachel"
    openai_tts_voice: str = "alloy"

    # ---- Text-to-video ----
    t2v_provider: Literal["mock", "replicate", "gpu"] = "mock"
    replicate_api_token: str | None = None
    replicate_t2v_model: str = "lightricks/ltx-video"
    gpu_t2v_model: str = "Lightricks/LTX-Video"
    hf_token: str | None = None
    pexels_api_key: str | None = None

    # ---- Render defaults ----
    video_width: int = 1080
    video_height: int = 1920
    video_fps: int = 30
    target_duration_sec: int = 45
    max_duration_sec: int = 60

    # ---- Telegram ----
    telegram_bot_token: str | None = None
    admin_id: int | None = None              # single admin Telegram user ID
    telegram_admin_ids: str = ""             # legacy comma-separated (kept for backwards compat)
    telegram_user_daily_limit: int = 5

    # ---- Misc ----
    webhook_signing_secret: str = "change-me"
    flower_basic_auth: str = "admin:admin"
    sentry_dsn: str | None = None

    # ---------------- derived ----------------
    @computed_field  # type: ignore[prop-decorator]
    @property
    def sqlalchemy_url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def api_key_set(self) -> set[str]:
        return {k.strip() for k in self.api_keys.split(",") if k.strip()}

    @property
    def admin_id_set(self) -> set[int]:
        out: set[int] = set()
        if self.admin_id:
            out.add(self.admin_id)
        for part in self.telegram_admin_ids.split(","):
            part = part.strip()
            if part.isdigit():
                out.add(int(part))
        return out

    @property
    def is_prod(self) -> bool:
        return self.env == "production"

    @property
    def resolution(self) -> tuple[int, int]:
        return (self.video_width, self.video_height)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
