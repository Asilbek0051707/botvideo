"""Script agent — topic -> title + timed scene list (narration + visual prompts)."""

from __future__ import annotations

from factory.agents.llm import get_llm, parse_json
from factory.agents.schema import Scene
from factory.core.logging import get_logger
from factory.prompts import SCRIPT_SYSTEM, build_script_prompt

log = get_logger(__name__)


class ScriptAgent:
    def write(
        self, topic: str, *, style: str = "documentary", language: str = "en", target_duration: int = 45
    ) -> tuple[str, list[Scene]]:
        llm = get_llm()
        if llm is None:
            return self._mock(topic, style=style, target_duration=target_duration)
        try:
            raw = llm.generate(
                SCRIPT_SYSTEM,
                build_script_prompt(topic, style=style, language=language, target_duration=target_duration),
                max_tokens=2000,
                temperature=0.9,
            )
            data = parse_json(raw)
            title = data.get("title") or topic
            scenes = [
                Scene(
                    index=i,
                    narration=s["narration"],
                    visual_prompt=s["visual_prompt"],
                    on_screen_text=s.get("on_screen_text", ""),
                    duration_sec=float(s.get("duration_sec", 4.0)),
                    motion=s.get("motion", "slow push-in"),
                )
                for i, s in enumerate(data["scenes"])
            ]
            if not scenes:
                raise ValueError("empty scene list")
            return title, scenes
        except Exception as exc:
            log.warning("script_agent.llm_failed_fallback", error=str(exc))
            return self._mock(topic, style=style, target_duration=target_duration)

    def _mock(self, topic: str, *, style: str, target_duration: int) -> tuple[str, list[Scene]]:
        """Deterministic, no-API script so the pipeline always runs end-to-end."""
        beats = [
            (f"Here's something most people never realized about {topic}.", "WAIT FOR IT", "slow push-in"),
            (f"It starts with a detail hiding in plain sight.", "HIDDEN DETAIL", "drone reveal"),
            (f"And once you see it, you can't unsee it.", "LOOK CLOSER", "orbit"),
            (f"Scientists were stunned by what came next.", "STUNNED", "handheld"),
            (f"This is the part nobody talks about.", "THE TWIST", "slow push-in"),
            (f"So next time you think about {topic}, remember this.", "REMEMBER THIS", "static"),
        ]
        per = max(3.0, min(6.0, target_duration / len(beats)))
        scenes = [
            Scene(
                index=i,
                narration=narr,
                visual_prompt=(
                    f"cinematic {style} shot illustrating '{topic}', dramatic lighting, "
                    f"shallow depth of field, 9:16 vertical, highly detailed, 4k"
                ),
                on_screen_text=ost,
                duration_sec=per,
                motion=motion,
            )
            for i, (narr, ost, motion) in enumerate(beats)
        ]
        title = f"The truth about {topic}".strip()[:80]
        return title, scenes
