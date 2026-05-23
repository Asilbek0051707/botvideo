"""Mock text-to-video: animated gradient clips via FFmpeg (no GPU, no API).

This is what makes the whole pipeline runnable anywhere. It produces a real,
correctly-sized/timed mp4 per scene so assembly, captioning, muxing, upload and
delivery are all exercised end-to-end. Swap T2V_PROVIDER to `replicate`/`gpu`
for real generative video — nothing else in the pipeline changes.
"""

from __future__ import annotations

from pathlib import Path

from factory.agents.schema import Scene
from factory.render.ffmpeg import run
from factory.render.providers.base import T2VProvider

# Cohesive deep-blue/teal palette cycled per scene.
PALETTE = [
    ("0x0F2027", "0x2C5364"),
    ("0x1A1A2E", "0x16213E"),
    ("0x232526", "0x414345"),
    ("0x0F3443", "0x34E89E"),
    ("0x141E30", "0x243B55"),
    ("0x42275A", "0x734B6D"),
]


class MockT2V(T2VProvider):
    name = "mock"

    def generate_clip(self, scene: Scene, out_path: Path, *, width: int, height: int, fps: int) -> Path:
        c0, c1 = PALETTE[scene.index % len(PALETTE)]
        dur = max(1.0, scene.duration_sec)
        run(
            [
                "ffmpeg", "-y",
                "-f", "lavfi",
                "-i",
                (
                    f"gradients=s={width}x{height}:c0={c0}:c1={c1}"
                    f":x0=0:y0=0:x1={width}:y1={height}:speed=0.02:seed={scene.index + 1}:rate={fps}"
                ),
                "-t", f"{dur:.3f}",
                "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                out_path.name,
            ],
            cwd=out_path.parent,
        )
        return out_path
