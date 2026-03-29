#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DB_PATH = Path("/tmp/jobmatch_media_cv.sqlite3")
if DB_PATH.exists():
    DB_PATH.unlink()

os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"
os.environ["SECRET_KEY"] = "test-secret-key-0123456789abcdef"

import app.models  # noqa: F401
from app.core.constants import ROL_EMPRESA, ROL_ESTUDIANTE
from app.core.security import get_password_hash
from app.crud.crud_user import create_user
from app.db.base_class import Base
from app.db.session import SessionLocal, engine
from app.main import app
from app.models.perfil_estudiante import PerfilEstudiante
from app.models.rol import Role
from app.schemas.user import UserCreate
from app.services import storage_service


def reset_database() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        db.add_all(
            [
                Role(id=ROL_ESTUDIANTE, nombre="estudiante"),
                Role(id=ROL_EMPRESA, nombre="empresa"),
            ]
        )
        db.commit()
    finally:
        db.close()


def seed_users() -> tuple[int, int]:
    db = SessionLocal()
    try:
        student_payload = UserCreate(
            email="cv-student@example.com",
            password="Test1234!",
            rol_id=ROL_ESTUDIANTE,
            perfil_estudiante={
                "nombre_completo": "CV Student",
                "institucion_educativa": "Universidad Test",
                "nivel_academico": "Licenciatura",
            },
        )
        student = create_user(db, student_payload, get_password_hash("Test1234!"))

        company_payload = UserCreate(
            email="cv-company@example.com",
            password="Test1234!",
            rol_id=ROL_EMPRESA,
            perfil_empresa={
                "nombre_comercial": "CV Company",
            },
        )
        company = create_user(db, company_payload, get_password_hash("Test1234!"))

        perfil = db.query(PerfilEstudiante).filter_by(usuario_id=student.id).first()
        assert perfil is not None
        perfil.cv_storage_key = "estudiantes/cv/test/cv.pdf"
        perfil.cv_tipo_archivo = "application/pdf"
        db.commit()

        return student.id, company.id
    finally:
        db.close()


def login(client: TestClient, email: str, password: str) -> str:
    response = client.post(
        "/api/v1/auth/jwt/login",
        data={"email": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    return payload["access_token"]


def main() -> None:
    reset_database()
    student_id, _company_id = seed_users()

    # Avoid MinIO dependency for this test.
    storage_service.StorageService.__init__ = lambda self: None  # type: ignore[assignment]
    storage_service.StorageService.get_presigned_get_url = (  # type: ignore[assignment]
        lambda self, object_name, expires_seconds=None: f"http://example.com/{object_name}"
    )

    client = TestClient(app)

    student_token = login(client, "cv-student@example.com", "Test1234!")
    company_token = login(client, "cv-company@example.com", "Test1234!")

    cv_url = f"/api/v1/media/estudiantes/{student_id}/cv"

    student_resp = client.get(cv_url, headers={"Authorization": f"Bearer {student_token}"})
    assert student_resp.status_code == 200, student_resp.text

    company_resp = client.get(cv_url, headers={"Authorization": f"Bearer {company_token}"})
    assert company_resp.status_code == 200, company_resp.text

    print("media_cv_access_check: OK (empresa y estudiante pueden ver CV)")


if __name__ == "__main__":
    main()
