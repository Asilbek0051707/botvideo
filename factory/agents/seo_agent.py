"""SEO agent — title, description, tags, hashtags for discovery."""

from __future__ import annotations

import re

from factory.agents.llm import get_llm, parse_json
from factory.core.logging import get_logger
from factory.prompts import SEO_SYSTEM, build_seo_prompt

log = get_logger(__name__)


class SEOAgent:
    def optimize(self, topic: str, narration: str, *, fallback_title: str) -> dict:
        llm = get_llm()
        if llm is not None:
            try:
                raw = llm.generate(SEO_SYSTEM, build_seo_prompt(topic, narration), max_tokens=600, temperature=0.7)
                data = parse_json(raw)
                if isinstance(data, dict) and data.get("title"):
                    data.setdefault("hashtags", ["#shorts"])
                    if "#shorts" not in data["hashtags"]:
                        data["hashtags"].append("#shorts")
                    return data
            except Exception as exc:
                log.warning("seo_agent.llm_failed_fallback", error=str(exc))
        return self._mock(topic, fallback_title)

    def _mock(self, topic: str, fallback_title: str) -> dict:
        words = [w.lower() for w in re.findall(r"[a-zA-Z]+", topic) if len(w) > 2]
        tags = list(dict.fromkeys(words + ["shorts", "facts", "viral", "didyouknow"]))[:15]
        return {
            "title": fallback_title[:90],
            "description": f"{fallback_title}. Subscribe for daily shorts about {topic}. #shorts",
            "tags": tags,
            "hashtags": ["#shorts", "#viral", "#facts"],
        }
