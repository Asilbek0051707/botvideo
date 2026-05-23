"""Text-to-video provider interface. One clip per scene."""

from __future__ import annotations

import abc
from pathlib import Path

from factory.agents.schema import Scene


class T2VProvider(abc.ABC):
    name: str = "base"

    @abc.abstractmethod
    def generate_clip(
        self, scene: Scene, out_path: Path, *, width: int, height: int, fps: int
    ) -> Path:
        """Render a single scene to `out_path` (mp4) and return it."""
