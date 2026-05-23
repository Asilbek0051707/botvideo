"""Outbound notifications: signed webhooks + Telegram delivery."""

from __future__ import annotations

import json

import httpx

from factory.core.config import settings
from factory.core.logging import get_logger
from factory.core.security import sign_payload

log = get_logger(__name__)


def send_webhook(url: str, event: str, data: dict) -> bool:
    payload = json.dumps({"event": event, "data": data}, default=str).encode()
    headers = {"Content-Type": "application/json", "X-Factory-Signature": sign_payload(payload)}
    try:
        resp = httpx.post(url, content=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        return True
    except httpx.HTTPError as exc:
        log.warning("webhook.failed", url=url, error=str(exc))
        return False


def telegram_send_message(chat_id: int | str, text: str) -> bool:
    if not settings.telegram_bot_token:
        return False
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    try:
        httpx.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=15).raise_for_status()
        return True
    except httpx.HTTPError as exc:
        log.warning("telegram.message.failed", chat_id=chat_id, error=str(exc))
        return False


def telegram_send_video(chat_id: int | str, video_url: str, caption: str = "") -> bool:
    if not settings.telegram_bot_token:
        return False
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendVideo"
    try:
        httpx.post(url, json={"chat_id": chat_id, "video": video_url, "caption": caption}, timeout=60).raise_for_status()
        return True
    except httpx.HTTPError as exc:
        log.warning("telegram.video.failed", chat_id=chat_id, error=str(exc))
        return False
