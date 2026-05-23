"""Render pipeline: ContentPlan + narration audio -> finished vertical mp4.

Provider-agnostic. The only GPU-aware part is the T2V provider; concat, captions,
muxing and thumbnailing are plain FFmpeg and run on any CPU.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from factory.agents.schema import ContentPlan
from factory.core.config import settings
from factory.core.logging import get_logger
from factory.render import captions, ffmpeg
from factory.render.providers import get_t2v_provider

log = get_logger(__name__)


@dataclass
class RenderResult:
    video_path: Path
    thumbnail_path: Path
    srt_path: Path
    duration: float
    width: int
    height: int
    scene_clips: list[Path] = field(default_factory=list)


class RenderPipeline:
    def __init__(self) -> None:
        self.provider = get_t2v_provider()
        self.width, self.height = settings.resolution
        self.fps = settings.video_fps

    def render(
        self,
        plan: ContentPlan,
        audio_path: Path,
        workdir: Path,
        *,
        progress_cb=None,
    ) -> RenderResult:
        workdir.mkdir(parents=True, exist_ok=True)
        clips: list[Path] = []

        n = len(plan.scenes)
        for scene in plan.scenes:
            clip = workdir / f"scene_{scene.index:02d}.mp4"
            log.info("render.scene", index=scene.index, provider=self.provider.name)
            self.provider.generate_clip(
                scene, clip, width=self.width, height=self.height, fps=self.fps
            )
            clips.append(clip)
            if progress_cb:
                progress_cb(scene.index + 1, n)

        concat = ffmpeg.concat_clips(clips, workdir / "concat.mp4", self.fps)
        duration = ffmpeg.probe_duration(concat)

        ass = captions.build_ass(plan.scenes, workdir / "subs.ass")
        srt = captions.build_srt(plan.scenes, workdir / "captions.srt")

        final = ffmpeg.mux_audio_and_subtitles(
            concat, audio_path, ass, workdir / "final.mp4", duration=duration or plan.total_duration
        )
        thumb = ffmpeg.extract_thumbnail(final, workdir / "thumbnail.jpg", at_sec=min(1.0, duration / 3))

        return RenderResult(
            video_path=final,
            thumbnail_path=thumb,
            srt_path=srt,
            duration=ffmpeg.probe_duration(final),
            width=self.width,
            height=self.height,
            scene_clips=clips,
        )
