"""Thin, robust wrappers around the ffmpeg / ffprobe CLIs."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from factory.core.logging import get_logger

log = get_logger(__name__)


def run(cmd: list[str], cwd: str | Path | None = None) -> str:
    """Run a command, raising RuntimeError with the stderr tail on failure."""
    proc = subprocess.run(
        cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True
    )
    if proc.returncode != 0:
        tail = (proc.stderr or "")[-1500:]
        log.error("ffmpeg.failed", cmd=" ".join(cmd[:6]) + " ...", stderr_tail=tail)
        raise RuntimeError(f"command failed ({proc.returncode}): {' '.join(cmd[:3])}\n{tail}")
    return proc.stdout


def probe_duration(path: str | Path) -> float:
    out = run(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "json", str(path),
        ]
    )
    try:
        return float(json.loads(out)["format"]["duration"])
    except (KeyError, ValueError, json.JSONDecodeError):
        return 0.0


def concat_clips(clips: list[Path], out_path: Path, fps: int) -> Path:
    """Concatenate same-codec clips via the concat demuxer (re-encoded for safety)."""
    listfile = out_path.parent / "concat_list.txt"
    listfile.write_text("".join(f"file '{c.name}'\n" for c in clips), encoding="utf-8")
    run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listfile.name,
            "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
            "-r", str(fps), out_path.name,
        ],
        cwd=out_path.parent,
    )
    return out_path


def mux_audio_and_subtitles(
    video: Path, audio: Path, subtitles: Path | None, out_path: Path, duration: float
) -> Path:
    """Burn subtitles, attach audio (padded/trimmed to `duration`), output final mp4."""
    vf = []
    if subtitles is not None:
        vf.append(f"subtitles={subtitles.name}")
    cmd = ["ffmpeg", "-y", "-i", video.name, "-i", audio.name]
    if vf:
        cmd += ["-vf", ",".join(vf)]
    cmd += [
        "-map", "0:v:0", "-map", "1:a:0",
        "-af", "apad",                 # pad short audio with silence
        "-t", f"{duration:.3f}",       # final length = video length
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
        out_path.name,
    ]
    run(cmd, cwd=out_path.parent)
    return out_path


def extract_thumbnail(video: Path, out_path: Path, at_sec: float = 1.0) -> Path:
    run(
        [
            "ffmpeg", "-y", "-ss", f"{at_sec:.2f}", "-i", video.name,
            "-vframes", "1", "-q:v", "3", out_path.name,
        ],
        cwd=out_path.parent,
    )
    return out_path
