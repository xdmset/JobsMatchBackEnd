from __future__ import annotations

from datetime import timedelta
from io import BytesIO
from urllib.parse import urlsplit, urlunsplit

from app.core.config import settings


class StorageService:
    def __init__(self) -> None:
        from minio import Minio

        self.bucket_name = settings.minio_bucket_name
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.use_ssl,
        )
        self.public_base = settings.minio_public_endpoint

    def ensure_bucket_exists(self) -> None:
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)

    def upload_bytes(self, data: bytes, object_name: str, content_type: str) -> str:
        payload = BytesIO(data)
        self.client.put_object(
            self.bucket_name,
            object_name,
            payload,
            length=len(data),
            content_type=content_type,
        )
        return object_name

    def remove_object(self, object_name: str) -> None:
        self.client.remove_object(self.bucket_name, object_name)

    def get_presigned_get_url(self, object_name: str, expires_seconds: int | None = None) -> str:
        expires = timedelta(seconds=expires_seconds or settings.media_url_expiration_seconds)
        internal_url = self.client.presigned_get_object(
            self.bucket_name,
            object_name,
            expires=expires,
        )
        parsed = urlsplit(internal_url)
        return urlunsplit((parsed.scheme, self.public_base, parsed.path, parsed.query, parsed.fragment))
