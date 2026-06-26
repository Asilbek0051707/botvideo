"""Prompt service — generates AI prompts from templates."""

from __future__ import annotations

import json
from pathlib import Path

_TMPL_FILE = Path(__file__).parent.parent / "data" / "templates" / "ai_prompts.json"


class PromptService:
    def __init__(self) -> None:
        self._templates: dict[str, str] = {}

    def _load(self) -> None:
        if self._templates:
            return
        try:
            with open(_TMPL_FILE, encoding="utf-8") as f:
                self._templates = json.load(f)
        except Exception:
            self._templates = {}

    def generate(self, character: str, category: str) -> dict[str, str]:
        """Return a dict of prompt_type → rendered prompt string."""
        self._load()
        result: dict[str, str] = {}
        ctx = {"character": character, "category": category}
        for key, tmpl in self._templates.items():
            try:
                result[key] = tmpl.format(**ctx)
            except KeyError:
                result[key] = tmpl
        return result

    def format_for_telegram(self, character: str, category: str) -> str:
        prompts = self.generate(character, category)
        if not prompts:
            return f"⏳ Prompts for <b>{character}</b> — coming soon."

        icons = {
            "image":     "📸",
            "animation": "🎬",
            "thumbnail": "🖼",
            "video":     "🎥",
            "background":"🌄",
            "voice":     "🎤",
        }
        lines = [f"🎨 <b>AI Prompts — {character}</b>\n"]
        for key, text in prompts.items():
            icon = icons.get(key, "✏️")
            label = key.replace("_", " ").title()
            lines.append(f"{icon} <b>{label}:</b>\n<code>{text}</code>\n")
        return "\n".join(lines)


prompt_service = PromptService()
