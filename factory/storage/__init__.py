"""Storage factory — pick a backend from settings."""

from __future__ import annotations

from functools import lru_cache

from factory.core.config import settings
from factory.storage.base import Storage


@lru_cache
def get_storage() -> Storage:
    backend = settings.storage_backend
    if backend in ("s3", "minio"):
        from factory.storage.s3 import S3Storage

        return S3Storage()
    if backend == "supabase":
        from factory.storage.supabase_store import SupabaseStorage

        return SupabaseStorage()
    from factory.storage.local import LocalStorage

    return LocalStorage()


__all__ = ["Storage", "get_storage"]
