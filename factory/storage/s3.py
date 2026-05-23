"""S3-compatible storage (AWS S3, MinIO, Cloudflare R2)."""

from __future__ import annotations

import boto3
from botocore.client import Config

from factory.core.config import settings
from factory.storage.base import Storage


class S3Storage(Storage):
    def __init__(self) -> None:
        self.bucket = settings.storage_bucket
        self.public = settings.storage_public
        self._public_endpoint = settings.s3_public_endpoint or settings.s3_endpoint_url
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,  # None => real AWS
            region_name=settings.s3_region,
            aws_access_key_id=settings.s3_access_key_id,
            aws_secret_access_key=settings.s3_secret_access_key,
            config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
        )

    def put_bytes(self, data: bytes, key: str, content_type: str = "application/octet-stream") -> str:
        self.client.put_object(Bucket=self.bucket, Key=key, Body=data, ContentType=content_type)
        return self.url_for(key)

    def url_for(self, key: str) -> str:
        if self.public and self._public_endpoint:
            return f"{self._public_endpoint.rstrip('/')}/{self.bucket}/{key}"
        if self.public:
            return f"https://{self.bucket}.s3.{settings.s3_region}.amazonaws.com/{key}"
        return self.client.generate_presigned_url(
            "get_object", Params={"Bucket": self.bucket, "Key": key}, ExpiresIn=7 * 24 * 3600
        )

    def exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except self.client.exceptions.ClientError:
            return False

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)
