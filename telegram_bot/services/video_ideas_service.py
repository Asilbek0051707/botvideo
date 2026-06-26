"""Video ideas service — generates video concept templates."""

from __future__ import annotations

import json
from pathlib import Path

_TMPL_FILE = Path(__file__).parent.parent / "data" / "templates" / "video_ideas.json"


class VideoIdeasService:
    def __init__(self) -> None:
        self._templates: list[dict] = []

    def _load(self) -> None:
        if self._templates:
            return
        try:
            with open(_TMPL_FILE, encoding="utf-8") as f:
                data = json.load(f)
            self._templates = data.get("ideas", [])
        except Exception:
            self._templates = []

    def generate(self, character: str, category: str) -> list[dict[str, str]]:
        """Return list of {title, description} for the given character."""
        self._load()
        ctx = {"character": character, "category": category}
        ideas = []
        for tmpl in self._templates:
            try:
                ideas.append(
                    {
                        "title": tmpl["title"].format(**ctx),
                        "description": tmpl.get("description", "").format(**ctx),
                    }
                )
            except KeyError:
                ideas.append({"title": tmpl["title"], "description": ""})
        return ideas

    def format_for_telegram(self, character: str, category: str) -> str:
        ideas = self.generate(character, category)
        if not ideas:
            return f"⏳ Video ideas for <b>{character}</b> — coming soon."

        lines = [f"📝 <b>Video Ideas — {character}</b>\n"]
        for i, idea in enumerate(ideas, 1):
            lines.append(f"<b>{i}. {idea['title']}</b>")
            if idea["description"]:
                lines.append(f"   {idea['description']}")
            lines.append("")
        return "\n".join(lines)


video_ideas_service = VideoIdeasService()
