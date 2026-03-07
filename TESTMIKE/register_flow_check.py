#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import os
from pathlib import Path
import sys

from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users_db_sync_sqlalchemy import SQLAlchemyUserDatabase


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DB_PATH = Path("/tmp/jobmatch_register_flow.sqlite3")
if DB_PATH.exists():
    DB_PATH.unlink()

os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"
os.environ["SECRET_KEY"] = "test-secret-key-0123456789abcdef"

from app.core.constants import ROL_ADMIN, ROL_EMPRESA, ROL_ESTUDIANTE
from app.core.fastapi_users import UserManager, get_jwt_strategy
from app.core.security import get_password_hash
from app.crud.crud_user import create_user
from app.db.base_class import Base
from app.db.session import SessionLocal, engine
from app.main import app
from app.models.perfil_empresa import PerfilEmpresa
from app.models.perfil_estudiante import PerfilEstudiante
from app.models.rol import Role
from app.models.user import User
from app.schemas.user import UserCreate as LegacyUserCreate


def reset_database() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        db.add_all(
            [
                Role(id=ROL_ADMIN, nombre="admin"),
                Role(id=ROL_ESTUDIANTE, nombre="estudiante"),
                Role(id=ROL_EMPRESA, nombre="empresa"),
            ]
        )
        db.commit()
    finally:
        db.close()


def make_manager() -> tuple[SessionLocal, UserManager]:
    session = SessionLocal()
    user_db = SQLAlchemyUserDatabase(session, User)
    return session, UserManager(user_db)


async def create_and_authenticate(user_payload: dict) -> User:
    session = SessionLocal()
    try:
        user_in = LegacyUserCreate.model_validate(user_payload)
        created_user = create_user(session, user_in, get_password_hash(user_payload["password"]))
    finally:
        session.close()

    session, manager = make_manager()
    try:
        credentials = OAuth2PasswordRequestForm(
            username=user_payload["email"],
            password=user_payload["password"],
            scope="",
        )
        authenticated_user = await manager.authenticate(credentials)
        assert authenticated_user is not None
        token = await get_jwt_strategy().write_token(authenticated_user)
        assert token
        return created_user
    finally:
        session.close()


def assert_student_auth_flow() -> None:
    created_user = asyncio.run(
        create_and_authenticate(
            {
                "email": "student@example.com",
                "password": "Test1234!",
                "rol_id": ROL_ESTUDIANTE,
                "perfil_estudiante": {
                    "nombre_completo": "Student Test",
                    "institucion_educativa": "Universidad Test",
                    "nivel_academico": "Licenciatura",
                    "biografia": "Perfil estudiante",
                    "habilidades": ["python", "fastapi"],
                    "ubicacion": "Quito",
                    "modalidad_preferida": "remoto",
                },
            }
        )
    )

    db = SessionLocal()
    try:
        perfil = db.query(PerfilEstudiante).filter_by(usuario_id=created_user.id).first()
        assert perfil is not None
        assert perfil.nombre_completo == "Student Test"
    finally:
        db.close()


def assert_company_auth_flow() -> None:
    created_user = asyncio.run(
        create_and_authenticate(
            {
                "email": "empresa@example.com",
                "password": "Test1234!",
                "rol_id": ROL_EMPRESA,
                "perfil_empresa": {
                    "nombre_comercial": "Empresa Test",
                    "sector": "Tecnologia",
                    "descripcion": "Perfil empresa",
                    "sitio_web": "https://example.com",
                    "ubicacion_sede": "Bogota",
                    "foto_perfil_url": "https://example.com/logo.png",
                },
            }
        )
    )

    db = SessionLocal()
    try:
        perfil = db.query(PerfilEmpresa).filter_by(usuario_id=created_user.id).first()
        assert perfil is not None
        assert perfil.nombre_comercial == "Empresa Test"
    finally:
        db.close()


def assert_legacy_schema_accepts_profiles() -> None:
    legacy_student = LegacyUserCreate.model_validate(
        {
            "email": "legacy_student@example.com",
            "password": "Test1234!",
            "rol_id": ROL_ESTUDIANTE,
            "perfil_estudiante": {
                "nombre_completo": "Legacy Student",
                "institucion_educativa": "Universidad Test",
                "nivel_academico": "Licenciatura",
            },
        }
    )
    assert legacy_student.perfil_estudiante is not None

    legacy_company = LegacyUserCreate.model_validate(
        {
            "email": "legacy_company@example.com",
            "password": "Test1234!",
            "rol_id": ROL_EMPRESA,
            "perfil_empresa": {
                "nombre_comercial": "Legacy Empresa",
            },
        }
    )
    assert legacy_company.perfil_empresa is not None


def assert_auth_register_removed() -> None:
    route_paths = {route.path for route in app.routes}
    assert "/api/v1/auth/register" not in route_paths
    assert "/api/v1/auth/jwt/login" in route_paths
    assert "/api/v1/users" not in route_paths
    assert "/api/v1/users/me" not in route_paths
    assert "/api/v1/user/" in route_paths


def main() -> int:
    reset_database()
    assert_auth_register_removed()
    assert_legacy_schema_accepts_profiles()
    assert_student_auth_flow()
    assert_company_auth_flow()
    print("register_flow_check: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
