# ---- AI YouTube Factory: Telegram bot ----
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml ./
COPY factory ./factory
COPY telegram_bot ./telegram_bot

RUN pip install --upgrade pip && pip install -e .

RUN useradd -m -u 10003 app && chown -R app:app /app
USER app

CMD ["python", "-m", "telegram_bot.bot"]
