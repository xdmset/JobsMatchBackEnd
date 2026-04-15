#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DB_PATH = Path(f"/tmp/jobmatch_full_api_flow_{uuid4().hex}.sqlite3")

os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"
os.environ["SECRET_KEY"] = "test-secret-key-0123456789abcdef"

import app.models  # noqa: F401
from fastapi import HTTPException
from pydantic import ValidationError

from app.api.v1.endpoints.perfil_empresa import read_empresa, update_existing_empresa
from app.api.v1.endpoints.perfil_estudiante import read_estudiante, update_existing_estudiante
from app.api.v1.endpoints.postulaciones import (
    actualizar_estado,
    crear_postulacion_web,
    listar_postulaciones_empresa,
)
from app.api.v1.endpoints.retroalimentacion import (
    generate_feedback_roadmap,
    read_retroalimentacion_by_postulacion,
)
from app.api.v1.endpoints.suscripcion import (
    delete_existing_suscripcion,
    read_suscripcion,
    read_suscripciones,
    read_suscripciones_by_usuario,
    update_existing_suscripcion,
)
from app.api.v1.endpoints.swipes import get_company_candidate_feed, registrar_swipe, registrar_swipe_empresa
from app.api.v1.endpoints.user import change_password, create_new_user, read_me, read_users, remove_user
from app.api.v1.endpoints.vacante import (
    create_new_vacante,
    read_historial_vacantes_empresa,
    read_historial_vacantes_estudiante,
    read_vacantes,
    register_vacante_view,
    update_existing_vacante,
)
from app.core.constants import ROL_ADMIN, ROL_EMPRESA, ROL_ESTUDIANTE
from app.core.security import verify_password
from app.db.base_class import Base
from app.db.session import SessionLocal, engine
from app.main import app
from app.models.postulacion import Postulacion
from app.models.retroalimentacion import Retroalimentacion
from app.models.rol import Role
from app.models.user import User
from app.schemas.interaccion_swipe import SwipeCreate, SwipeEmpresaCreate
from app.schemas.perfil_empresa import PerfilEmpresaCreate
from app.schemas.perfil_estudiante import PerfilEstudianteCreate
from app.schemas.postulacion import CambiarEstadoPostulacion, PostulacionWebCreate, RetroalimentacionCreate
from app.schemas.suscripcion import SuscripcionUpdate
from app.schemas.user import PasswordChange, UserCreate
from app.schemas.vacante import VacanteCreate, VacanteUpdate


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


def expect_http_exception(fn, expected_status: int, context: str) -> HTTPException:
    try:
        fn()
    except HTTPException as exc:
        assert exc.status_code == expected_status, (
            f"{context}: expected HTTP {expected_status}, got {exc.status_code}, detail={exc.detail}"
        )
        return exc
    raise AssertionError(f"{context}: expected HTTPException {expected_status}")


def get_user(db, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    assert user is not None
    return user


def expect_validation_error(fn, context: str) -> ValidationError:
    try:
        fn()
    except ValidationError as exc:
        return exc
    raise AssertionError(f"{context}: expected ValidationError")


def main() -> int:
    reset_database()
    db = SessionLocal()
    try:
        run_id = uuid4().hex[:8]
        student_email = f"student-flow-{run_id}@example.com"
        admin_email = f"admin-flow-{run_id}@example.com"
        company_email = f"company-flow-{run_id}@example.com"
        mixed_email = f"mixed-flow-{run_id}@example.com"

        openapi = app.openapi()
        paths = openapi["paths"]
        assert "/api/v1/user/" in paths
        assert "/api/v1/auth/jwt/login" in paths
        assert "/api/v1/postulaciones/web" in paths
        assert "/api/v1/media/estudiantes/{usuario_id}/cv" in paths
        assert "/api/v1/retroalimentacion/postulacion/{postulacion_id}" in paths
        assert "/api/v1/retroalimentacion/postulacion/{postulacion_id}/generar-roadmap" in paths
        assert "/api/v1/suscripciones/" in paths
        assert "/api/v1/suscripciones/usuario/{usuario_id}" in paths
        assert "/api/v1/suscripciones/{suscripcion_id}" in paths
        assert "/api/v1/swipes/empresa/{empresa_id}" in paths
        login_request_body_schema = paths["/api/v1/auth/jwt/login"]["post"]["requestBody"]["content"][
            "application/x-www-form-urlencoded"
        ]["schema"]
        if "$ref" in login_request_body_schema:
            login_schema_name = login_request_body_schema["$ref"].split("/")[-1]
            login_request_body = openapi["components"]["schemas"][login_schema_name]
        else:
            login_request_body = login_request_body_schema
        assert "email" in login_request_body["properties"]
        assert "username" not in login_request_body["properties"]

        invalid_mixed_profile_payload = UserCreate(
            email=mixed_email,
            password="Test1234!",
            rol_id=ROL_ESTUDIANTE,
            perfil_estudiante={
                "nombre_completo": "Mixed Flow",
                "institucion_educativa": "Universidad Flow",
                "nivel_academico": "Licenciatura",
                "fecha_nacimiento": "2002-04-10",
            },
            perfil_empresa={
                "nombre_comercial": "Empresa Invalida",
            },
        )
        expect_http_exception(
            lambda: create_new_user(invalid_mixed_profile_payload, db),
            400,
            "reject mixed student/company profile",
        )

        student = create_new_user(
            UserCreate(
                email=student_email,
                password="Test1234!",
                rol_id=ROL_ESTUDIANTE,
                perfil_estudiante={
                    "nombre_completo": "Student Flow",
                    "institucion_educativa": "Universidad Flow",
                    "nivel_academico": "Licenciatura",
                    "fecha_nacimiento": "2002-04-10",
                    "biografia": "Perfil estudiante de prueba",
                    "habilidades": ["python", "fastapi"],
                    "ubicacion": "CDMX",
                    "modalidad_preferida": "remoto",
                },
            ),
            db,
        )
        admin = create_new_user(
            UserCreate(
                email=admin_email,
                password="Test1234!",
                rol_id=ROL_ADMIN,
            ),
            db,
        )
        company = create_new_user(
            UserCreate(
                email=company_email,
                password="Test1234!",
                rol_id=ROL_EMPRESA,
                perfil_empresa={
                    "nombre_comercial": "Empresa Flow",
                    "sector": "Tecnologia",
                    "descripcion": "Perfil empresa de prueba",
                    "sitio_web": "https://example.com",
                    "ubicacion_sede": "CDMX",
                    "foto_perfil_url": "https://example.com/logo.png",
                },
            ),
            db,
        )

        expect_http_exception(
            lambda: create_new_user(
                UserCreate(
                    email=student_email,
                    password="Test1234!",
                    rol_id=ROL_ESTUDIANTE,
                    perfil_estudiante={
                        "nombre_completo": "Student Flow",
                        "institucion_educativa": "Universidad Flow",
                        "nivel_academico": "Licenciatura",
                        "fecha_nacimiento": "2002-04-10",
                    },
                ),
                db,
            ),
            400,
            "duplicate email rejected",
        )

        admin = get_user(db, admin.id)
        student = get_user(db, student.id)
        company = get_user(db, company.id)

        users = read_users(db=db, current_user=admin)
        assert len(users) == 3

        student_me = read_me(db=db, current_user=student)
        assert student_me.perfil_estudiante.nombre_completo == "Student Flow"

        company_me = read_me(db=db, current_user=company)
        assert company_me.perfil_empresa.nombre_comercial == "Empresa Flow"

        list_subscriptions = read_suscripciones(db=db, current_user=admin)
        assert len(list_subscriptions) == 2

        student_subscriptions = read_suscripciones_by_usuario(student.id, db=db, current_user=student)
        assert len(student_subscriptions) == 1
        student_subscription_id = student_subscriptions[0].id
        assert student_subscriptions[0].tipo_plan == "free"

        company_subscriptions = read_suscripciones_by_usuario(company.id, db=db, current_user=company)
        assert len(company_subscriptions) == 1
        company_subscription_id = company_subscriptions[0].id
        assert company_subscriptions[0].tipo_plan == "free"

        student_subscription = read_suscripcion(student_subscription_id, db=db, current_user=admin)
        assert student_subscription.tipo_plan == "free"

        student_profile = read_estudiante(student.id, db=db)
        assert student_profile["nombre_completo"] == "Student Flow"

        updated_student_profile = update_existing_estudiante(
            student.id,
            PerfilEstudianteCreate(
                nombre_completo="Student Flow Updated",
                institucion_educativa="Universidad Flow",
                nivel_academico="Licenciatura",
                fecha_nacimiento="2002-04-10",
                biografia="Perfil actualizado",
                habilidades=["python", "fastapi", "sqlalchemy"],
                ubicacion="Remote",
                modalidad_preferida="hibrido",
            ),
            db=db,
            current_user=student,
        )
        assert updated_student_profile["modalidad_preferida"] == "hibrido"

        company_profile = read_empresa(company.id, db=db)
        assert company_profile["nombre_comercial"] == "Empresa Flow"

        updated_company_profile = update_existing_empresa(
            company.id,
            PerfilEmpresaCreate(
                nombre_comercial="Empresa Flow Updated",
                sector="Tecnologia",
                descripcion="Perfil empresa actualizado",
                sitio_web="https://example.com/jobs",
                ubicacion_sede="Remote",
                foto_perfil_url="https://example.com/logo-new.png",
            ),
            db=db,
            current_user=company,
        )
        assert updated_company_profile["ubicacion_sede"] == "Remote"

        expect_http_exception(
            lambda: create_new_vacante(
                company.id,
                VacanteCreate(
                    titulo="Unauthorized Vacancy",
                    descripcion="No debe crearse",
                    modalidad="remoto",
                ),
                db=db,
                current_user=student,
            ),
            403,
            "student cannot create company vacancy",
        )

        expect_validation_error(
            lambda: create_new_vacante(
                company.id,
                VacanteCreate(
                    titulo="Broken Vacancy",
                    descripcion="No debe producir 500",
                    modalidad="remoto",
                    sueldo_minimo=5000,
                    sueldo_maximo=1000,
                ),
                db=db,
                current_user=company,
            ),
            "invalid salary range rejected",
        )

        first_vacancy = create_new_vacante(
            company.id,
            VacanteCreate(
                titulo="Backend Intern",
                descripcion="Primera vacante para aplicar desde web",
                requisitos="Python, FastAPI",
                modalidad="remoto",
                ubicacion="CDMX",
                sueldo_minimo=1000,
                sueldo_maximo=2000,
            ),
            db=db,
            current_user=company,
        )
        update_vacancy_state = update_existing_vacante(
            first_vacancy.id,
            VacanteUpdate(estado="pausada"),
            db=db,
            current_user=company,
        )
        assert update_vacancy_state.estado == "pausada"

        second_vacancy = create_new_vacante(
            company.id,
            VacanteCreate(
                titulo="QA Intern",
                descripcion="Segunda vacante para match por swipe",
                requisitos="QA, SQL",
                modalidad="presencial",
                ubicacion="Tijuana",
                sueldo_minimo=900,
                sueldo_maximo=1500,
            ),
            db=db,
            current_user=company,
        )

        # Reactivar first_vacancy (fue pausada para probar el update de estado)
        update_existing_vacante(
            first_vacancy.id,
            VacanteUpdate(estado="activa"),
            db=db,
            current_user=company,
        )

        vacancies = read_vacantes(skip=0, limit=100, modalidad=None, ubicacion=None, sueldo_min=None, db=db, current_user=None)
        assert len(vacancies) == 2
        filtered_vacancies = read_vacantes(
            skip=0,
            limit=100,
            modalidad="remoto",
            ubicacion=None,
            sueldo_min=None,
            db=db,
            current_user=None,
        )
        assert len(filtered_vacancies) == 1
        assert filtered_vacancies[0].id == first_vacancy.id

        first_view = register_vacante_view(first_vacancy.id, db=db, current_user=student)
        assert first_view["total_visualizaciones"] == 1
        second_view = register_vacante_view(first_vacancy.id, db=db, current_user=student)
        assert second_view["total_visualizaciones"] == 2

        student_history = read_historial_vacantes_estudiante(student.id, db=db, current_user=student)
        assert len(student_history) == 1
        assert student_history[0].total_visualizaciones == 2

        basic_company_history = read_historial_vacantes_empresa(company.id, db=db, current_user=company)
        first_history_item = next(item for item in basic_company_history if item.id == first_vacancy.id)
        assert first_history_item.total_visualizaciones == 2
        assert first_history_item.ultima_visualizacion is None
        assert first_history_item.ultimo_like_estudiante is None
        assert first_history_item.ultimo_like_empresa is None

        expect_http_exception(
            lambda: get_company_candidate_feed(
                company.id,
                vacante_id=first_vacancy.id,
                habilidad="python",
                db=db,
                current_user=company,
            ),
            403,
            "free company advanced candidate filter blocked",
        )

        first_application = crear_postulacion_web(
            PostulacionWebCreate(estudiante_id=student.id, vacante_id=first_vacancy.id),
            db=db,
            current_user=student,
        )
        assert first_application.source == "web_apply"
        assert first_application.estado == "enviado"
        assert first_application.match_id is None

        expect_http_exception(
            lambda: crear_postulacion_web(
                PostulacionWebCreate(estudiante_id=student.id, vacante_id=first_vacancy.id),
                db=db,
                current_user=student,
            ),
            409,
            "prevent duplicate web apply",
        )

        company_applications = listar_postulaciones_empresa(
            company.id,
            estado=None,
            institucion_educativa=None,
            nivel_academico=None,
            ubicacion=None,
            db=db,
            current_user=company,
        )
        assert len(company_applications) == 1
        assert company_applications[0].id == first_application.id

        reject_application = actualizar_estado(
            first_application.id,
            CambiarEstadoPostulacion(
                nuevo_estado="rechazado",
                feedback=RetroalimentacionCreate(
                    campos_mejora="Mejorar SQL",
                    sugerencias_perfil="Agregar proyectos backend",
                ),
            ),
            db=db,
            current_user=company,
        )
        assert reject_application["message"] == "Estado actualizado con éxito"

        company_feedback = read_retroalimentacion_by_postulacion(
            first_application.id,
            db=db,
            current_user=company,
        )
        assert company_feedback.postulacion_id == first_application.id
        assert company_feedback.campos_mejora == "Mejorar SQL"
        assert company_feedback.roadmap_estado == "generado"
        assert company_feedback.roadmap is not None
        assert len(company_feedback.roadmap["habilidades"]) >= 1

        student_feedback = read_retroalimentacion_by_postulacion(
            first_application.id,
            db=db,
            current_user=student,
        )
        assert student_feedback.id == company_feedback.id
        assert student_feedback.roadmap is not None

        stored_application = db.query(Postulacion).filter(Postulacion.id == first_application.id).first()
        assert stored_application is not None
        assert stored_application.estado == "rechazado"

        stored_feedback = (
            db.query(Retroalimentacion)
            .filter(Retroalimentacion.postulacion_id == first_application.id)
            .first()
        )
        assert stored_feedback is not None
        assert stored_feedback.campos_mejora == "Mejorar SQL"
        assert stored_feedback.id == company_feedback.id
        assert stored_feedback.roadmap_estado == "generado"
        assert stored_feedback.roadmap_json is not None

        regenerated_feedback = generate_feedback_roadmap(
            first_application.id,
            db=db,
            current_user=student,
        )
        assert regenerated_feedback.roadmap_estado == "generado"
        assert regenerated_feedback.roadmap is not None

        second_application = crear_postulacion_web(
            PostulacionWebCreate(estudiante_id=student.id, vacante_id=first_vacancy.id),
            db=db,
            current_user=student,
        )
        assert second_application.id != first_application.id

        student_swipe = registrar_swipe(
            student.id,
            SwipeCreate(vacante_id=second_vacancy.id, interes_estudiante=True),
            db=db,
            current_user=student,
        )
        assert student_swipe is None

        updated_company_subscription = update_existing_suscripcion(
            company_subscription_id,
            SuscripcionUpdate(tipo_plan="premium", fecha_fin="2026-05-08"),
            db=db,
            current_user=admin,
        )
        assert updated_company_subscription.tipo_plan == "premium"

        synced_after_company_upgrade = read_users(db=db, current_user=admin)
        company_after_upgrade = {item.id: item for item in synced_after_company_upgrade}[company.id]
        assert company_after_upgrade.es_premium is True

        advanced_candidate_filter = get_company_candidate_feed(
            company.id,
            vacante_id=second_vacancy.id,
            habilidad="python",
            db=db,
            current_user=company,
        )
        assert len(advanced_candidate_filter) == 1
        assert advanced_candidate_filter[0].usuario_id == student.id
        assert advanced_candidate_filter[0].ya_dio_like is True

        company_swipe = registrar_swipe_empresa(
            company.id,
            SwipeEmpresaCreate(
                estudiante_id=student.id,
                vacante_id=second_vacancy.id,
                interes_empresa=True,
            ),
            db=db,
            current_user=company,
        )
        assert company_swipe is not None
        assert company_swipe.estudiante_id == student.id
        assert company_swipe.vacante_id == second_vacancy.id

        final_company_applications = listar_postulaciones_empresa(
            company.id,
            estado=None,
            institucion_educativa=None,
            nivel_academico=None,
            ubicacion=None,
            db=db,
            current_user=company,
        )
        assert len(final_company_applications) == 3
        swipe_application = next(item for item in final_company_applications if item.vacante_id == second_vacancy.id)
        assert swipe_application.source == "app_swipe"
        assert swipe_application.match_id == company_swipe.id

        updated_student_subscription = update_existing_suscripcion(
            student_subscription_id,
            SuscripcionUpdate(tipo_plan="premium", fecha_fin="2026-05-08"),
            db=db,
            current_user=admin,
        )
        assert updated_student_subscription.tipo_plan == "premium"

        synced_users = read_users(db=db, current_user=admin)
        users_by_id = {item.id: item for item in synced_users}
        assert users_by_id[student.id].es_premium is True
        assert users_by_id[company.id].es_premium is True

        premium_company_history = read_historial_vacantes_empresa(company.id, db=db, current_user=company)
        premium_swipe_item = next(item for item in premium_company_history if item.id == second_vacancy.id)
        assert premium_swipe_item.total_likes_estudiantes == 1
        assert premium_swipe_item.total_likes_empresa == 1
        assert premium_swipe_item.total_matches == 1
        assert premium_swipe_item.ultimo_like_estudiante is not None
        assert premium_swipe_item.ultimo_like_empresa is not None

        change_password(
            PasswordChange(current_password="Test1234!", new_password="NewPass123!"),
            db=db,
            current_user=student,
        )
        db.refresh(student)
        assert verify_password("NewPass123!", student.password_hash)

        delete_existing_suscripcion(student_subscription_id, db=db, current_user=admin)
        delete_existing_suscripcion(company_subscription_id, db=db, current_user=admin)
        remaining_subscriptions = read_suscripciones(db=db, current_user=admin)
        assert len(remaining_subscriptions) == 0

        users_after_subscription_delete = read_users(db=db, current_user=admin)
        users_after_delete = {item.id: item for item in users_after_subscription_delete}
        assert users_after_delete[student.id].es_premium is False
        assert users_after_delete[company.id].es_premium is False

        remove_user(student.id, db=db, current_user=student)
        admin = get_user(db, admin.id)
        company = get_user(db, company.id)
        remove_user(company.id, db=db, current_user=company)

        final_users = read_users(db=db, current_user=admin)
        assert len(final_users) == 1
        assert final_users[0].id == admin.id

    finally:
        db.close()

    print("full_api_flow_check: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
