"""Standalone runner for a long-form (~1 hour) mock video about AI.

Bypasses Celery/Postgres/Storage and the Orchestrator/script_agent (whose mock
fallback only produces 6 hook beats). Builds a 60-scene plan directly — 12
chapters of 5 scenes each, 60 seconds per scene — and pushes it through the
real RenderPipeline.

Two small adaptations vs. scripts/make_video.py:
  - concat is monkey-patched to use `-c copy` (the 60 mock clips share codec
    settings, so re-encoding 3600s here would waste an extra hour);
  - probe_duration is the same ffmpeg-only fallback as the short runner.

Usage:
    python scripts/make_long_video.py
Output: ./out/long_video.mp4 (plus long_thumbnail.jpg and long_captions.srt).
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

TOPIC = "artificial intelligence"
STYLE = "documentary"
LANGUAGE = "en"
SECONDS_PER_SCENE = 60.0


def _bootstrap_ffmpeg() -> Path:
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


def _concat_copy(clips, out_path, fps):
    # Stream-copy concat: avoids re-encoding 60 mock clips that already share
    # codec settings. Saves roughly an hour at this length.
    listfile = out_path.parent / "concat_list.txt"
    listfile.write_text(
        "".join(f"file '{c.name}'\n" for c in clips), encoding="utf-8"
    )
    _ff_mod.run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listfile.name,
            "-c", "copy", out_path.name,
        ],
        cwd=out_path.parent,
    )
    return out_path


_ff_mod.concat_clips = _concat_copy

from factory.agents.schema import ContentPlan, Scene  # noqa: E402
from factory.agents.voice_agent import VoiceAgent  # noqa: E402
from factory.render.pipeline import RenderPipeline  # noqa: E402


# 12 chapters x 5 scenes = 60 scenes. on_screen_text is the short caption
# that's burned in; narration is the (silent in mock TTS) voice-over line and
# the sidecar SRT body.
CHAPTERS: list[tuple[str, list[tuple[str, str]]]] = [
    ("The Dawn of AI", [
        ("ORIGINS", "In the 1950s a handful of researchers dared to ask whether machines could think."),
        ("THE TURING TEST", "Alan Turing proposed a deceptively simple game to probe machine intelligence."),
        ("EARLY PROGRAMS", "Tiny programs played checkers, proved theorems, and hinted at much more."),
        ("THE AI WINTER", "Promises outran results, funding dried up, and a long, cold winter began."),
        ("THE REAWAKENING", "Decades later, faster chips and bigger data woke the field back up."),
    ]),
    ("How Machines Learn", [
        ("PATTERNS", "Modern AI is built on one core idea: find patterns in mountains of data."),
        ("SUPERVISION", "Labeled examples teach a model to map inputs to the answers humans expect."),
        ("REINFORCEMENT", "Other systems learn from trial and error, guided only by a reward signal."),
        ("TRANSFER", "Knowledge picked up on one task can be reused for many others."),
        ("GENERATION", "Generative models do not just classify the world — they invent new pieces of it."),
    ]),
    ("Inside Neural Networks", [
        ("THE PERCEPTRON", "Decades ago a simple neuron-like unit became the first building block."),
        ("BACKPROPAGATION", "An algorithm for slowly adjusting weights unlocked deep architectures."),
        ("DEEP LEARNING", "Stacking many layers turned out to be more powerful than anyone expected."),
        ("VISION NETS", "Convolutional networks taught computers to see edges, shapes, and objects."),
        ("TRANSFORMERS", "A new attention-based design swept through language, vision, and beyond."),
    ]),
    ("Language and AI", [
        ("TEXT", "Computers learned to read by predicting which word should come next."),
        ("TRANSLATION", "What once took rooms of linguists now happens in milliseconds."),
        ("SUMMARIZATION", "Models distill long documents into a few useful sentences."),
        ("CONVERSATION", "Chat assistants hold context across questions and follow instructions."),
        ("LARGE MODELS", "Scaling to billions of parameters unlocked surprising new abilities."),
    ]),
    ("AI Sees the World", [
        ("VISION", "Pixels become labels: faces, animals, road signs, products."),
        ("DETECTION", "Bounding boxes find every car, pedestrian, and obstacle in a single frame."),
        ("SCENE", "Beyond detection, models infer what is happening, not just what is there."),
        ("IMAGE GENERATION", "Diffusion models paint realistic pictures from a few words of guidance."),
        ("ROBOTICS", "Cameras and AI together let robots grasp, walk, and navigate."),
    ]),
    ("AI in Medicine", [
        ("IMAGING", "AI spots tumors and subtle anomalies that exhaust the human eye."),
        ("DISCOVERY", "Models search molecular space for promising new drug candidates."),
        ("TRIAGE", "Emergency rooms route patients faster with AI risk scores."),
        ("PERSONALIZED", "Genomic signals match treatments to individual patients."),
        ("SURGERY", "Robotic systems assist precise, minimally invasive operations."),
    ]),
    ("AI in Science", [
        ("PROTEINS", "Folding predictions that took years now finish in minutes."),
        ("WEATHER", "Forecasts grow sharper as networks learn from decades of atmospheric data."),
        ("PARTICLES", "Detectors filter trillions of events to spot the truly interesting ones."),
        ("ASTRONOMY", "Telescope surveys are too large for humans alone — AI hunts in the haystack."),
        ("CLIMATE", "Earth-system models simulate the consequences of every plausible choice."),
    ]),
    ("Creative AI", [
        ("IMAGES", "A short prompt becomes a finished illustration in seconds."),
        ("MUSIC", "Models compose original tracks across genres and styles."),
        ("WRITING", "Drafts, edits, and rewrites that used to take days now arrive in moments."),
        ("VIDEO", "Text-to-video systems animate scenes that never happened in reality."),
        ("GAMES", "Procedural worlds and lifelike characters now lean on generative AI."),
    ]),
    ("AI in Daily Life", [
        ("SEARCH", "Answers and citations beat ten blue links when the question is complex."),
        ("NAVIGATION", "Real-time traffic models route millions of cars around invisible jams."),
        ("RECOMMENDATIONS", "Feeds, playlists, and shops quietly learn what each person prefers."),
        ("ASSISTANTS", "Voice-driven helpers handle reminders, messages, and small errands."),
        ("HOME", "Thermostats, doorbells, and lights adapt to the people who live there."),
    ]),
    ("Work and the Economy", [
        ("AUTOMATION", "Repetitive, predictable tasks are the first to be reshaped."),
        ("PRODUCTIVITY", "Tools take routine work off the plate and leave more time for judgment."),
        ("NEW JOBS", "Every wave of automation creates roles that did not exist before."),
        ("DISPLACEMENT", "Some skills lose value, sometimes faster than retraining can keep up."),
        ("UPSKILLING", "Continuous learning becomes a default part of a working life."),
    ]),
    ("Ethics and Responsibility", [
        ("BIAS", "Models inherit the biases hidden inside the data they were trained on."),
        ("TRANSPARENCY", "Decisions that affect lives should be explainable, not just accurate."),
        ("PRIVACY", "Powerful models tempt us to collect more data than we need."),
        ("ACCOUNTABILITY", "When AI fails, the question of who is responsible cannot be skipped."),
        ("ALIGNMENT", "We are still learning how to align powerful systems with human values."),
    ]),
    ("The Path Forward", [
        ("OPEN VS CLOSED", "The future of AI will be shaped by what is shared and what is locked up."),
        ("REGULATION", "Lawmakers race to set rules without smothering the technology itself."),
        ("AGI DEBATES", "Will narrow tools combine into something general — and what would that mean?"),
        ("SAFETY", "Research into oversight, evaluation, and red-teaming is just beginning."),
        ("THE FUTURE", "What we build next depends on the choices we are making right now."),
    ]),
]


def build_plan() -> ContentPlan:
    scenes: list[Scene] = []
    idx = 0
    for chapter_title, beats in CHAPTERS:
        # Chapter intro card: short on-screen title, ~7s.
        scenes.append(
            Scene(
                index=idx,
                narration=f"Chapter {1 + len(scenes) // 5}: {chapter_title}.",
                visual_prompt=(
                    f"cinematic {STYLE} title card about {chapter_title}, "
                    "abstract gradient backdrop, 9:16 vertical"
                ),
                on_screen_text=chapter_title.upper(),
                duration_sec=7.0,
                motion="slow push-in",
            )
        )
        idx += 1
        for caption, narration in beats:
            scenes.append(
                Scene(
                    index=idx,
                    narration=narration,
                    visual_prompt=(
                        f"cinematic {STYLE} shot illustrating {caption.lower()} "
                        f"about {TOPIC}, dramatic lighting, 9:16 vertical"
                    ),
                    on_screen_text=caption,
                    duration_sec=SECONDS_PER_SCENE - 7.0 / 5,
                    motion="orbit",
                )
            )
            idx += 1

    full_narration = " ".join(s.narration for s in scenes)
    return ContentPlan(
        title="Artificial Intelligence — a one-hour journey",
        description=(
            "Twelve chapters surveying the past, present, and future of AI: "
            "origins, learning, perception, language, applications across "
            "science, medicine, daily life, work, ethics, and safety."
        ),
        tags=["ai", "artificial intelligence", "documentary", "long-form"],
        hashtags=["#AI", "#artificialintelligence", "#documentary"],
        style=STYLE,
        language=LANGUAGE,
        full_narration=full_narration,
        scenes=scenes,
    )


def main() -> int:
    out_dir = Path("out")
    out_dir.mkdir(exist_ok=True)
    workdir = out_dir / "_long_work"
    if workdir.exists():
        shutil.rmtree(workdir)
    workdir.mkdir()

    plan = build_plan()
    print(
        f"plan: {plan.title}  ({len(plan.scenes)} scenes, {plan.total_duration:.1f}s)",
        flush=True,
    )

    # Mock TTS returns a silent track sized to fallback_seconds. The mux step
    # below pads with apad to fit the final duration, so we only need a short
    # seed — generating 3600s of silence here would waste ~300 MB on disk.
    audio_bytes, ext = VoiceAgent().synthesize(plan.full_narration, fallback_seconds=2.0)
    audio_path = workdir / f"voice.{ext}"
    audio_path.write_bytes(audio_bytes)
    print(
        f"voice: {audio_path.name}  ({len(audio_bytes) / 1024:.1f} KB, .{ext})",
        flush=True,
    )

    def progress(done: int, total: int) -> None:
        if done == 1 or done == total or done % 5 == 0:
            print(f"  scene {done}/{total}", flush=True)

    result = RenderPipeline().render(plan, audio_path, workdir, progress_cb=progress)

    final = out_dir / "long_video.mp4"
    shutil.copy2(result.video_path, final)
    thumb = out_dir / "long_thumbnail.jpg"
    shutil.copy2(result.thumbnail_path, thumb)
    srt = out_dir / "long_captions.srt"
    shutil.copy2(result.srt_path, srt)

    print()
    print(f"video:     {final.resolve()}")
    print(f"thumbnail: {thumb.resolve()}")
    print(f"captions:  {srt.resolve()}")
    print(f"duration:  {result.duration:.1f}s  ({result.width}x{result.height})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
