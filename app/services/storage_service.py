from __future__ import annotations

from datetime import timedelta
from io import BytesIO
from urllib.parse import urlsplit

from app.core.config import settings


class StorageService:
    def __init__(self) -> None:
        from minio import Minio

        self.bucket_name = settings.minio_bucket_name
        self.client = self._build_client(Minio, settings.minio_endpoint, secure=settings.use_ssl)
        public_endpoint, public_secure = self._resolve_public_endpoint()
        self.public_client = self._build_client(Minio, public_endpoint, secure=public_secure)

    def _build_client(self, minio_cls, endpoint: str, *, secure: bool):
        return minio_cls(
            endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=secure,
        )

    def _resolve_public_endpoint(self) -> tuple[str, bool]:
        public_endpoint = settings.minio_public_endpoint.strip()
        if "://" not in public_endpoint:
            return public_endpoint, settings.use_ssl

        parsed = urlsplit(public_endpoint)
        endpoint = parsed.netloc or parsed.path
        secure = parsed.scheme == "https"
        return endpoint, secure

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
        return self.public_client.presigned_get_object(
            self.bucket_name,
            object_name,
            expires=expires,
        )
