# ---- AI YouTube Factory: CPU render/queue worker ----
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# ffmpeg (render) + DejaVu fonts (drawtext / caption burn-in)
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md alembic.ini ./
COPY factory ./factory
COPY worker ./worker
COPY backend ./backend
COPY database ./database

RUN pip install --upgrade pip && pip install -e ".[render]"

RUN useradd -m -u 10002 app && chown -R app:app /app
USER app

CMD ["celery", "-A", "worker.celery_app.celery", "worker", "-Q", "default,render,gpu", "-l", "info", "--concurrency=2"]
