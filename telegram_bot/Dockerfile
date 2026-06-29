# ---- Telegram Bot ----
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies first (cached layer)
COPY telegram_bot/requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy source code
COPY factory ./factory
COPY telegram_bot ./telegram_bot

# Add factory and telegram_bot to Python path
ENV PYTHONPATH=/app

RUN useradd -m -u 10003 app && chown -R app:app /app
USER app

CMD ["python", "-m", "telegram_bot.bot"]
