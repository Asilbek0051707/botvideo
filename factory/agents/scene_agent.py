"""Scene agent — normalize timing so total duration fits the target window."""

from __future__ import annotations

from factory.agents.schema import Scene
from factory.core.config import settings


class SceneAgent:
    def normalize(self, scenes: list[Scene], *, target_duration: int) -> list[Scene]:
        if not scenes:
            return scenes
        max_total = settings.max_duration_sec
        total = sum(s.duration_sec for s in scenes)
        target = min(target_duration, max_total)

        # Scale proportionally toward the target, clamp each scene to [1.5, 12]s.
        scale = target / total if total else 1.0
        for s in scenes:
            s.duration_sec = round(max(1.5, min(12.0, s.duration_sec * scale)), 2)

        # If clamping pushed us over the hard ceiling, trim from the longest scenes.
        total = sum(s.duration_sec for s in scenes)
        while total > max_total and len(scenes) > 1:
            longest = max(scenes, key=lambda s: s.duration_sec)
            longest.duration_sec = round(max(1.5, longest.duration_sec - 0.5), 2)
            total = sum(s.duration_sec for s in scenes)
        return scenes
