"""FastAPI application entrypoint."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.app.api.routes import auth, health, jobs, videos, webhooks
from factory.core.config import settings
from factory.core.logging import configure_logging, get_logger

log = get_logger("backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    # Dev convenience: ensure tables exist without a separate migration step.
    if not settings.is_prod:
        from factory.db.session import init_db

        init_db()
        log.info("db.initialized", mode="create_all (dev)")
    log.info("startup", env=settings.env, storage=settings.storage_backend, t2v=settings.t2v_provider)
    yield
    log.info("shutdown")


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Automated AI YouTube Shorts factory — REST API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if not settings.is_prod else [settings.public_base_url],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Versioned API
API_PREFIX = "/api/v1"
app.include_router(health.router, prefix="/api")          # /api/health, /api/ready
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(jobs.router, prefix=API_PREFIX)
app.include_router(videos.router, prefix=API_PREFIX)
app.include_router(webhooks.router, prefix=API_PREFIX)

# Serve local-disk assets when using the `local` storage backend.
if settings.storage_backend == "local":
    import os

    os.makedirs(settings.local_storage_dir, exist_ok=True)
    app.mount("/media", StaticFiles(directory=settings.local_storage_dir), name="media")


@app.get("/", include_in_schema=False)
def root() -> JSONResponse:
    return JSONResponse(
        {"app": settings.app_name, "docs": "/docs", "health": "/api/health", "api": API_PREFIX}
    )
