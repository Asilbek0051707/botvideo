"""Supabase Storage backend (primary for production)."""

from __future__ import annotations

from functools import cached_property

from factory.core.config import settings
from factory.storage.base import Storage


class SupabaseStorage(Storage):
    def __init__(self) -> None:
        if not (settings.supabase_url and settings.supabase_service_key):
            raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY are required for supabase storage")
        self.bucket = settings.supabase_storage_bucket
        self.public = settings.storage_public

    @cached_property
    def _bucket(self):
        from supabase import create_client

        client = create_client(settings.supabase_url, settings.supabase_service_key)
        # ensure bucket exists (idempotent)
        try:
            client.storage.create_bucket(self.bucket, options={"public": self.public})
        except Exception:
            pass
        return client.storage.from_(self.bucket)

    def put_bytes(self, data: bytes, key: str, content_type: str = "application/octet-stream") -> str:
        self._bucket.upload(
            path=key,
            file=data,
            file_options={"content-type": content_type, "upsert": "true"},
        )
        return self.url_for(key)

    def url_for(self, key: str) -> str:
        if self.public:
            return self._bucket.get_public_url(key)
        signed = self._bucket.create_signed_url(key, 7 * 24 * 3600)
        return signed.get("signedURL") or signed.get("signed_url", "")

    def exists(self, key: str) -> bool:
        try:
            prefix, _, name = key.rpartition("/")
            listing = self._bucket.list(prefix)
            return any(obj.get("name") == name for obj in listing)
        except Exception:
            return False

    def delete(self, key: str) -> None:
        self._bucket.remove([key])
