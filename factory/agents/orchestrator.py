"""Orchestrator — turns a topic into a complete, render-ready ContentPlan.

This is the pure AI-planning step (no I/O beyond LLM calls). The worker then
synthesizes voice, generates visuals, and assembles the video from this plan.
"""

from __future__ import annotations

from factory.agents.schema import ContentPlan
from factory.agents.scene_agent import SceneAgent
from factory.agents.script_agent import ScriptAgent
from factory.agents.seo_agent import SEOAgent
from factory.agents.visual_agent import VisualAgent
from factory.core.config import settings
from factory.core.logging import get_logger

log = get_logger(__name__)


class Orchestrator:
    def __init__(self) -> None:
        self.script = ScriptAgent()
        self.scenes = SceneAgent()
        self.visual = VisualAgent()
        self.seo = SEOAgent()

    def build_plan(
        self,
        topic: str,
        *,
        style: str = "documentary",
        language: str = "en",
        target_duration: int | None = None,
    ) -> ContentPlan:
        target = target_duration or settings.target_duration_sec

        title, scenes = self.script.write(
            topic, style=style, language=language, target_duration=target
        )
        scenes = self.scenes.normalize(scenes, target_duration=target)
        scenes = self.visual.direct(scenes, style=style)

        narration = " ".join(s.narration for s in scenes)
        seo = self.seo.optimize(topic, narration, fallback_title=title)

        plan = ContentPlan(
            title=seo.get("title", title),
            description=seo.get("description", ""),
            tags=seo.get("tags", []),
            hashtags=seo.get("hashtags", []),
            style=style,
            language=language,
            full_narration=narration,
            scenes=scenes,
        )
        log.info(
            "orchestrator.plan_built",
            topic=topic,
            scenes=len(plan.scenes),
            duration=plan.total_duration,
        )
        return plan
