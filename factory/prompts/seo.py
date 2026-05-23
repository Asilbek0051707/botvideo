"""YouTube SEO / packaging prompt — title, description, tags, hashtags."""

from __future__ import annotations

SEO_SYSTEM = """\
You are a YouTube growth expert specializing in Shorts packaging and discovery.
Given a topic and the final narration, produce metadata that maximizes click-through
and search/recommendation reach without clickbait that the video can't deliver on.

Return ONLY valid JSON in this schema:
{
  "title": "string (<= 90 chars, curiosity + keyword front-loaded)",
  "description": "2-4 sentences, keyword-rich, with a call to action",
  "tags": ["10-15 lowercase search tags"],
  "hashtags": ["3-6 hashtags including #shorts"]
}
"""


def build_seo_prompt(topic: str, narration: str) -> str:
    return f"""\
TOPIC: {topic}

FINAL NARRATION:
{narration}

Produce the packaging JSON now. Always include "#shorts" in hashtags."""
