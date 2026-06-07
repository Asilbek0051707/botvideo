"""Standalone runner: hand-crafted Uzbek ContentPlan -> finished mp4 on disk.

Bypasses Celery/Postgres/Storage. Drives VoiceAgent + RenderPipeline directly
with mock providers. Hand-crafted scenes are used (instead of script_agent) so
we can produce Uzbek narration without an LLM API key — script_agent's mock
fallback is English-only.

Usage:
    python scripts/make_video.py
Output: ./out/video.mp4 (plus thumbnail.jpg and captions.srt).
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


def _bootstrap_ffmpeg() -> Path:
    """Make `ffmpeg` resolvable on PATH and return its path.

    Reuses a project-local static ffmpeg under vendor/ffmpeg/ when present;
    otherwise falls back to imageio-ffmpeg's bundled binary (copied into
    vendor/ so the rest of the pipeline can find it by name).
    """
    vendor_bin = Path(__file__).resolve().parent.parent / "vendor" / "ffmpeg" / "bin"
    target = vendor_bin / "ffmpeg.exe"
    if not target.exists():
        import imageio_ffmpeg

        src = Path(imageio_ffmpeg.get_ffmpeg_exe())
        vendor_bin.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
    os.environ["PATH"] = str(vendor_bin) + os.pathsep + os.environ.get("PATH", "")
    return target


_FFMPEG = _bootstrap_ffmpeg()

# ffprobe isn't bundled with imageio-ffmpeg. Replace probe_duration with a
# pure-ffmpeg fallback so the render pipeline runs without a separate ffprobe.
from factory.render import ffmpeg as _ff_mod  # noqa: E402

_DUR_RE = re.compile(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)")


def _probe_duration_via_ffmpeg(path) -> float:
    proc = subprocess.run(
        [str(_FFMPEG), "-i", str(path)], capture_output=True, text=True
    )
    m = _DUR_RE.search(proc.stderr or "")
    if not m:
        return 0.0
    h, mn, s = m.groups()
    return int(h) * 3600 + int(mn) * 60 + float(s)


_ff_mod.probe_duration = _probe_duration_via_ffmpeg

from factory.agents.schema import ContentPlan, Scene  # noqa: E402
from factory.agents.voice_agent import VoiceAgent  # noqa: E402
from factory.render.pipeline import RenderPipeline  # noqa: E402


def build_plan_uz() -> ContentPlan:
    style = "documentary"
    beats: list[tuple[str, str, str]] = [
        ("Bugun qurgan biznesingiz — ertaga kelajak avlodga qoldiriladigan meros.",
         "MEROS", "slow push-in"),
        ("Pul emas, qadriyat qoldiring — bu eng katta investitsiya.",
         "QADRIYAT", "drone reveal"),
        ("Har bir farzand uchun yangi imkoniyat yaratish — ota-onaning vazifasi.",
         "IMKONIYAT", "orbit"),
        ("Sabr, halollik va o'zaro hurmat — bu bizning haqiqiy sarmoyamiz.",
         "SARMOYA", "handheld"),
        ("Kelajak biz qanday boshlaganimizdan emas, qanday tugatganimizdan iborat.",
         "KELAJAK", "static"),
    ]
    scenes = [
        Scene(
            index=i,
            narration=narr,
            visual_prompt=(
                f"cinematic {style} shot symbolizing legacy and future generations, "
                "warm golden light, shallow depth of field, 9:16 vertical, 4k"
            ),
            on_screen_text=ost,
            duration_sec=6.0,
            motion=motion,
        )
        for i, (narr, ost, motion) in enumerate(beats)
    ]
    narration = " ".join(s.narration for s in scenes)
    return ContentPlan(
        title="Biznes va kelajak avlodlar",
        description="Kelajak avlodlar uchun biznes qurish — qadriyat, sabr, halollik.",
        tags=["biznes", "kelajak", "meros", "uzbek"],
        hashtags=["#biznes", "#kelajak", "#oilaviy"],
        style=style,
        language="uz",
        full_narration=narration,
        scenes=scenes,
    )


def main() -> int:
    out_dir = Path("out")
    out_dir.mkdir(exist_ok=True)
    workdir = out_dir / "_work"
    if workdir.exists():
        shutil.rmtree(workdir)
    workdir.mkdir()

    plan = build_plan_uz()
    print(f"plan: {plan.title}  ({len(plan.scenes)} scenes, {plan.total_duration}s)", flush=True)

    audio_bytes, ext = VoiceAgent().synthesize(
        plan.full_narration, fallback_seconds=plan.total_duration
    )
    audio_path = workdir / f"voice.{ext}"
    audio_path.write_bytes(audio_bytes)
    print(f"voice: {audio_path.name}  ({len(audio_bytes) / 1024:.1f} KB, .{ext})", flush=True)

    def progress(done: int, total: int) -> None:
        print(f"  scene {done}/{total}", flush=True)

    result = RenderPipeline().render(plan, audio_path, workdir, progress_cb=progress)

    final = out_dir / "video.mp4"
    shutil.copy2(result.video_path, final)
    thumb = out_dir / "thumbnail.jpg"
    shutil.copy2(result.thumbnail_path, thumb)
    srt = out_dir / "captions.srt"
    shutil.copy2(result.srt_path, srt)

    print()
    print(f"video:     {final.resolve()}")
    print(f"thumbnail: {thumb.resolve()}")
    print(f"captions:  {srt.resolve()}")
    print(f"duration:  {result.duration:.1f}s  ({result.width}x{result.height})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
