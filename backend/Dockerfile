# ---- AI YouTube Factory: API service ----
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Build context is the repo root (see docker-compose.yml).
COPY pyproject.toml README.md alembic.ini ./
COPY factory ./factory
COPY backend ./backend
COPY database ./database

RUN pip install --upgrade pip && pip install -e .

# Non-root
RUN useradd -m -u 10001 app && chown -R app:app /app
USER app

EXPOSE 8000

# Apply migrations, then serve. (Dev also create_all's on startup — idempotent.)
CMD ["sh", "-c", "alembic upgrade head && uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers ${WEB_CONCURRENCY:-2}"]
