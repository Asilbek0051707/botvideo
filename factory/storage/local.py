"""Local-disk storage for single-process dev. URLs served by the API at /media."""

from __future__ import annotations

from pathlib import Path

from factory.core.config import settings
from factory.storage.base import Storage


class LocalStorage(Storage):
    def __init__(self) -> None:
        self.root = Path(settings.local_storage_dir)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        p = (self.root / key).resolve()
        if not str(p).startswith(str(self.root.resolve())):
            raise ValueError("path traversal blocked")
        return p

    def put_bytes(self, data: bytes, key: str, content_type: str = "application/octet-stream") -> str:
        p = self._path(key)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        return self.url_for(key)

    def url_for(self, key: str) -> str:
        return f"{settings.public_base_url.rstrip('/')}/media/{key}"

    def exists(self, key: str) -> bool:
        return self._path(key).exists()

    def delete(self, key: str) -> None:
        self._path(key).unlink(missing_ok=True)
