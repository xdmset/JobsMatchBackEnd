from __future__ import annotations

import sys
from types import SimpleNamespace

from app.core.config import settings
from app.services.storage_service import StorageService


class FakeMinio:
    instances: list["FakeMinio"] = []

    def __init__(self, endpoint: str, *, access_key: str, secret_key: str, secure: bool) -> None:
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.secure = secure
        self.put_calls: list[tuple[str, str, int, str]] = []
        FakeMinio.instances.append(self)

    def bucket_exists(self, bucket_name: str) -> bool:
        return True

    def make_bucket(self, bucket_name: str) -> None:
        return None

    def put_object(self, bucket_name: str, object_name: str, payload, *, length: int, content_type: str) -> None:
        self.put_calls.append((bucket_name, object_name, length, content_type))

    def remove_object(self, bucket_name: str, object_name: str) -> None:
        return None

    def presigned_get_object(self, bucket_name: str, object_name: str, *, expires) -> str:
        scheme = "https" if self.secure else "http"
        return f"{scheme}://{self.endpoint}/{bucket_name}/{object_name}?expires={int(expires.total_seconds())}"


def test_presigned_urls_use_public_https_endpoint(monkeypatch):
    FakeMinio.instances.clear()
    monkeypatch.setitem(sys.modules, "minio", SimpleNamespace(Minio=FakeMinio))
    monkeypatch.setattr(settings, "minio_endpoint", "minio:9000")
    monkeypatch.setattr(settings, "minio_public_endpoint", "https://files.jobmatch.com.mx")
    monkeypatch.setattr(settings, "minio_bucket_name", "uploads")
    monkeypatch.setattr(settings, "minio_access_key", "admin")
    monkeypatch.setattr(settings, "minio_secret_key", "secret")
    monkeypatch.setattr(settings, "use_ssl", False)
    monkeypatch.setattr(settings, "media_url_expiration_seconds", 3600)

    storage = StorageService()
    storage.upload_bytes(b"abc", "estudiantes/fotos/2/test.jpg", "image/jpeg")
    url = storage.get_presigned_get_url("estudiantes/fotos/2/test.jpg")

    assert FakeMinio.instances[0].endpoint == "minio:9000"
    assert FakeMinio.instances[0].secure is False
    assert FakeMinio.instances[1].endpoint == "files.jobmatch.com.mx"
    assert FakeMinio.instances[1].secure is True
    assert FakeMinio.instances[0].put_calls == [
        ("uploads", "estudiantes/fotos/2/test.jpg", 3, "image/jpeg")
    ]
    assert url == "https://files.jobmatch.com.mx/uploads/estudiantes/fotos/2/test.jpg?expires=3600"


def test_presigned_urls_keep_non_tls_public_endpoint_when_no_scheme(monkeypatch):
    FakeMinio.instances.clear()
    monkeypatch.setitem(sys.modules, "minio", SimpleNamespace(Minio=FakeMinio))
    monkeypatch.setattr(settings, "minio_endpoint", "minio:9000")
    monkeypatch.setattr(settings, "minio_public_endpoint", "localhost:9000")
    monkeypatch.setattr(settings, "minio_bucket_name", "uploads")
    monkeypatch.setattr(settings, "minio_access_key", "admin")
    monkeypatch.setattr(settings, "minio_secret_key", "secret")
    monkeypatch.setattr(settings, "use_ssl", False)
    monkeypatch.setattr(settings, "media_url_expiration_seconds", 120)

    storage = StorageService()

    assert storage.get_presigned_get_url("demo.png") == "http://localhost:9000/uploads/demo.png?expires=120"
