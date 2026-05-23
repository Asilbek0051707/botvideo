"""Storage interface. All backends return a publicly resolvable URL for a key."""

from __future__ import annotations

import abc
from pathlib import Path


class Storage(abc.ABC):
    """Object storage abstraction (local disk / MinIO / S3 / Supabase)."""

    @abc.abstractmethod
    def put_bytes(self, data: bytes, key: str, content_type: str = "application/octet-stream") -> str:
        """Store raw bytes under `key`; return a resolvable URL."""

    @abc.abstractmethod
    def url_for(self, key: str) -> str:
        """Return a resolvable URL for an existing key (public or presigned)."""

    @abc.abstractmethod
    def exists(self, key: str) -> bool: ...

    @abc.abstractmethod
    def delete(self, key: str) -> None: ...

    def put_file(self, path: str | Path, key: str, content_type: str | None = None) -> str:
        p = Path(path)
        ctype = content_type or _guess_content_type(p.name)
        return self.put_bytes(p.read_bytes(), key, ctype)


def _guess_content_type(name: str) -> str:
    name = name.lower()
    if name.endswith(".mp4"):
        return "video/mp4"
    if name.endswith((".mp3",)):
        return "audio/mpeg"
    if name.endswith((".wav",)):
        return "audio/wav"
    if name.endswith((".png",)):
        return "image/png"
    if name.endswith((".jpg", ".jpeg")):
        return "image/jpeg"
    if name.endswith((".srt", ".vtt")):
        return "text/plain"
    if name.endswith(".json"):
        return "application/json"
    return "application/octet-stream"
