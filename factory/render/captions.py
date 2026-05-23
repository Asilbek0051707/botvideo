"""Build burn-in (ASS) and sidecar (SRT) captions from timed scenes."""

from __future__ import annotations

import textwrap
from pathlib import Path

from factory.agents.schema import Scene

ASS_HEADER = """\
[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV
Style: Pop,DejaVu Sans,84,&H00FFFFFF,&H00000000,&H64000000,1,0,1,5,2,2,60,60,420

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def _ts(seconds: float) -> str:
    cs = int(round(seconds * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _ts_srt(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _caption_text(scene: Scene) -> str:
    return (scene.on_screen_text or scene.narration).strip()


def build_ass(scenes: list[Scene], path: Path) -> Path:
    lines = [ASS_HEADER]
    t = 0.0
    for s in scenes:
        start, end = t, t + s.duration_sec
        t = end
        text = _caption_text(s).upper().replace("\n", " ")
        text = "\\N".join(textwrap.wrap(text, width=18)) or text
        lines.append(f"Dialogue: 0,{_ts(start)},{_ts(end)},Pop,,0,0,0,,{text}")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def build_srt(scenes: list[Scene], path: Path) -> Path:
    blocks = []
    t = 0.0
    for i, s in enumerate(scenes, start=1):
        start, end = t, t + s.duration_sec
        t = end
        blocks.append(f"{i}\n{_ts_srt(start)} --> {_ts_srt(end)}\n{s.narration.strip()}\n")
    path.write_text("\n".join(blocks), encoding="utf-8")
    return path
