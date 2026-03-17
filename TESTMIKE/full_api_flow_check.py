#!/usr/bin/env python3
from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DB_PATH = Path("/tmp/jobmatch_full_api_flow.sqlite3")
if DB_PATH.exists():
    DB_PATH.unlink()

os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"
os.environ["SECRET_KEY"] = "test-secret-key-0123456789abcdef"

import requests

import app.models  # noqa: F401
from app.core.constants import ROL_ADMIN, ROL_EMPRESA, ROL_ESTUDIANTE
from app.db.base_class import Base
from app.db.session import SessionLocal, engine
from app.models.postulacion import Postulacion
from app.models.retroalimentacion import Retroalimentacion
from app.models.rol import Role


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


def assert_status(response, expected_status: int, context: str):
    assert response.status_code == expected_status, (
        f"{context}: expected {expected_status}, got {response.status_code}, body={response.text}"
    )


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def wait_for_server(base_url: str, timeout_seconds: int = 20) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            response = requests.get(f"{base_url}/openapi.json", timeout=1)
            if response.status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(0.25)
    raise RuntimeError(f"Server did not start within {timeout_seconds}s")


def login(base_url: str, email: str, password: str) -> dict:
    response = requests.post(
        f"{base_url}/api/v1/auth/jwt/login",
        data={"email": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    assert_status(response, 200, f"login {email}")
    payload = response.json()
    assert payload["access_token"]
    assert payload["token_type"] == "bearer"
    return payload


def main() -> int:
    reset_database()
    port = find_free_port()
    base_url = f"http://127.0.0.1:{port}"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        wait_for_server(base_url)

        docs_response = requests.get(f"{base_url}/docs", timeout=10)
        assert_status(docs_response, 200, "docs")

        openapi_response = requests.get(f"{base_url}/openapi.json", timeout=10)
        assert_status(openapi_response, 200, "openapi")
        paths = openapi_response.json()["paths"]
        assert "/api/v1/user/" in paths
        assert "/api/v1/auth/jwt/login" in paths
        assert "/api/v1/postulaciones/web" in paths
        assert "/api/v1/media/estudiantes/{usuario_id}/cv" in paths
        assert "/api/v1/retroalimentacion/postulacion/{postulacion_id}" in paths
        assert "/api/v1/suscripciones/" in paths
        assert "/api/v1/suscripciones/usuario/{usuario_id}" in paths
        assert "/api/v1/suscripciones/{suscripcion_id}" in paths
        assert "/api/v1/swipes/empresa/{empresa_id}" in paths
        login_request_body_schema = paths["/api/v1/auth/jwt/login"]["post"]["requestBody"]["content"][
            "application/x-www-form-urlencoded"
        ]["schema"]
        if "$ref" in login_request_body_schema:
            login_schema_name = login_request_body_schema["$ref"].split("/")[-1]
            login_request_body = openapi_response.json()["components"]["schemas"][login_schema_name]
        else:
            login_request_body = login_request_body_schema
        assert "email" in login_request_body["properties"]
        assert "username" not in login_request_body["properties"]

        student_payload = {
            "email": "student-flow@example.com",
            "password": "Test1234!",
            "rol_id": ROL_ESTUDIANTE,
            "perfil_estudiante": {
                "nombre_completo": "Student Flow",
                "institucion_educativa": "Universidad Flow",
                "nivel_academico": "Licenciatura",
                "biografia": "Perfil estudiante de prueba",
                "habilidades": ["python", "fastapi"],
                "ubicacion": "CDMX",
                "modalidad_preferida": "remoto",
            },
        }
        admin_payload = {
            "email": "admin-flow@example.com",
            "password": "Test1234!",
            "rol_id": ROL_ADMIN,
        }
        company_payload = {
            "email": "company-flow@example.com",
            "password": "Test1234!",
            "rol_id": ROL_EMPRESA,
            "perfil_empresa": {
                "nombre_comercial": "Empresa Flow",
                "sector": "Tecnologia",
                "descripcion": "Perfil empresa de prueba",
                "sitio_web": "https://example.com",
                "ubicacion_sede": "CDMX",
                "foto_perfil_url": "https://example.com/logo.png",
            },
        }
        invalid_mixed_profile_payload = {
            "email": "mixed-flow@example.com",
            "password": "Test1234!",
            "rol_id": ROL_ESTUDIANTE,
            "perfil_estudiante": {
                "nombre_completo": "Mixed Flow",
                "institucion_educativa": "Universidad Flow",
                "nivel_academico": "Licenciatura",
            },
            "perfil_empresa": {
                "nombre_comercial": "Empresa Invalida",
            },
        }

        create_invalid_mixed_user = requests.post(
            f"{base_url}/api/v1/user/",
            json=invalid_mixed_profile_payload,
            timeout=10,
        )
        assert_status(create_invalid_mixed_user, 400, "reject mixed student/company profile")

        create_student = requests.post(f"{base_url}/api/v1/user/", json=student_payload, timeout=10)
        assert_status(create_student, 200, "create student")
        student_id = create_student.json()["id"]

        create_admin = requests.post(f"{base_url}/api/v1/user/", json=admin_payload, timeout=10)
        assert_status(create_admin, 200, "create admin")
        admin_id = create_admin.json()["id"]

        create_company = requests.post(f"{base_url}/api/v1/user/", json=company_payload, timeout=10)
        assert_status(create_company, 200, "create company")
        company_id = create_company.json()["id"]

        duplicate_student = requests.post(f"{base_url}/api/v1/user/", json=student_payload, timeout=10)
        assert_status(duplicate_student, 400, "duplicate email rejected")

        student_login = login(base_url, student_payload["email"], student_payload["password"])
        admin_login = login(base_url, admin_payload["email"], admin_payload["password"])
        company_login = login(base_url, company_payload["email"], company_payload["password"])
        assert student_login["access_token"] != company_login["access_token"]

        admin_headers = {"Authorization": f"Bearer {admin_login['access_token']}"}
        student_headers = {"Authorization": f"Bearer {student_login['access_token']}"}
        company_headers = {"Authorization": f"Bearer {company_login['access_token']}"}

        list_users = requests.get(f"{base_url}/api/v1/user/", headers=admin_headers, timeout=10)
        assert_status(list_users, 200, "list users")
        assert len(list_users.json()) == 3

        list_subscriptions = requests.get(f"{base_url}/api/v1/suscripciones/", headers=admin_headers, timeout=10)
        assert_status(list_subscriptions, 200, "list suscripciones")
        assert len(list_subscriptions.json()) == 3

        list_user_subscriptions = requests.get(
            f"{base_url}/api/v1/suscripciones/usuario/{student_id}",
            headers=student_headers,
            timeout=10,
        )
        assert_status(list_user_subscriptions, 200, "list suscripciones by user")
        assert len(list_user_subscriptions.json()) == 1
        subscription_payload = list_user_subscriptions.json()[0]
        subscription_id = subscription_payload["id"]
        assert subscription_payload["usuario_id"] == student_id
        assert subscription_payload["tipo_plan"] == "free"

        get_subscription = requests.get(
            f"{base_url}/api/v1/suscripciones/{subscription_id}",
            headers=admin_headers,
            timeout=10,
        )
        assert_status(get_subscription, 200, "get suscripcion")
        assert get_subscription.json()["tipo_plan"] == "free"

        update_subscription = requests.put(
            f"{base_url}/api/v1/suscripciones/{subscription_id}",
            json={
                "tipo_plan": "premium",
                "fecha_fin": "2026-05-08",
            },
            headers=admin_headers,
            timeout=10,
        )
        assert_status(update_subscription, 200, "update suscripcion")
        updated_subscription = update_subscription.json()
        assert updated_subscription["tipo_plan"] == "premium"
        assert updated_subscription["fecha_fin"] == "2026-05-08"

        synced_user = requests.get(f"{base_url}/api/v1/user/", headers=admin_headers, timeout=10)
        assert_status(synced_user, 200, "list users after suscripcion update")
        student_user = next(item for item in synced_user.json() if item["id"] == student_id)
        assert student_user["es_premium"] is True

        get_student_profile = requests.get(f"{base_url}/api/v1/perfil_estudiante/{student_id}", timeout=10)
        assert_status(get_student_profile, 200, "get student profile")
        assert get_student_profile.json()["nombre_completo"] == "Student Flow"

        update_student_profile = requests.put(
            f"{base_url}/api/v1/perfil_estudiante/{student_id}",
            json={
                "nombre_completo": "Student Flow Updated",
                "institucion_educativa": "Universidad Flow",
                "nivel_academico": "Licenciatura",
                "biografia": "Perfil actualizado",
                "habilidades": ["python", "fastapi", "sqlalchemy"],
                "ubicacion": "Remote",
                "modalidad_preferida": "hibrido",
            },
            headers=student_headers,
            timeout=10,
        )
        assert_status(update_student_profile, 200, "update student profile")
        assert update_student_profile.json()["modalidad_preferida"] == "hibrido"

        get_company_profile = requests.get(f"{base_url}/api/v1/perfil_empresa/{company_id}", timeout=10)
        assert_status(get_company_profile, 200, "get company profile")
        assert get_company_profile.json()["nombre_comercial"] == "Empresa Flow"

        update_company_profile = requests.put(
            f"{base_url}/api/v1/perfil_empresa/{company_id}",
            json={
                "nombre_comercial": "Empresa Flow Updated",
                "sector": "Tecnologia",
                "descripcion": "Perfil empresa actualizado",
                "sitio_web": "https://example.com/jobs",
                "ubicacion_sede": "Remote",
                "foto_perfil_url": "https://example.com/logo-new.png",
            },
            headers=company_headers,
            timeout=10,
        )
        assert_status(update_company_profile, 200, "update company profile")
        assert update_company_profile.json()["ubicacion_sede"] == "Remote"

        create_vacancy_web = requests.post(
            f"{base_url}/api/v1/vacante/{company_id}",
            json={
                "titulo": "Backend Intern",
                "descripcion": "Primera vacante para aplicar desde web",
                "requisitos": "Python, FastAPI",
                "modalidad": "remoto",
                "ubicacion": "CDMX",
                "sueldo_minimo": 1000,
                "sueldo_maximo": 2000,
            },
            headers=company_headers,
            timeout=10,
        )
        assert_status(create_vacancy_web, 200, "create first vacancy")
        first_vacancy_id = create_vacancy_web.json()["id"]

        update_vacancy_state = requests.put(
            f"{base_url}/api/v1/vacante/{first_vacancy_id}",
            json={"estado": "pausada"},
            headers=company_headers,
            timeout=10,
        )
        assert_status(update_vacancy_state, 200, "update vacancy estado")
        assert update_vacancy_state.json()["estado"] == "pausada"

        create_vacancy_swipe = requests.post(
            f"{base_url}/api/v1/vacante/{company_id}",
            json={
                "titulo": "QA Intern",
                "descripcion": "Segunda vacante para match por swipe",
                "requisitos": "QA, SQL",
                "modalidad": "presencial",
                "ubicacion": "Tijuana",
                "sueldo_minimo": 900,
                "sueldo_maximo": 1500,
            },
            headers=company_headers,
            timeout=10,
        )
        assert_status(create_vacancy_swipe, 200, "create second vacancy")
        second_vacancy_id = create_vacancy_swipe.json()["id"]

        list_vacancies = requests.get(f"{base_url}/api/v1/vacante/", timeout=10)
        assert_status(list_vacancies, 200, "list vacancies")
        assert len(list_vacancies.json()) == 2

        filtered_vacancies = requests.get(
            f"{base_url}/api/v1/vacante/",
            params={"modalidad": "remoto"},
            timeout=10,
        )
        assert_status(filtered_vacancies, 200, "filter vacancies")
        assert len(filtered_vacancies.json()) == 1
        assert filtered_vacancies.json()[0]["id"] == first_vacancy_id

        apply_web = requests.post(
            f"{base_url}/api/v1/postulaciones/web",
            json={"estudiante_id": student_id, "vacante_id": first_vacancy_id},
            headers=student_headers,
            timeout=10,
        )
        assert_status(apply_web, 200, "web apply")
        first_application = apply_web.json()
        assert first_application["source"] == "web_apply"
        assert first_application["estado"] == "enviado"
        assert first_application["match_id"] is None

        apply_web_duplicate = requests.post(
            f"{base_url}/api/v1/postulaciones/web",
            json={"estudiante_id": student_id, "vacante_id": first_vacancy_id},
            headers=student_headers,
            timeout=10,
        )
        assert_status(apply_web_duplicate, 409, "prevent duplicate web apply")

        company_applications = requests.get(
            f"{base_url}/api/v1/postulaciones/empresa/{company_id}",
            headers=company_headers,
            timeout=10,
        )
        assert_status(company_applications, 200, "list company applications")
        assert len(company_applications.json()) == 1
        assert company_applications.json()[0]["id"] == first_application["id"]

        reject_application = requests.put(
            f"{base_url}/api/v1/postulaciones/{first_application['id']}/estado",
            json={
                "nuevo_estado": "rechazado",
                "feedback": {
                    "campos_mejora": "Mejorar SQL",
                    "sugerencias_perfil": "Agregar proyectos backend",
                },
            },
            headers=company_headers,
            timeout=10,
        )
        assert_status(reject_application, 200, "reject application with feedback")

        get_feedback = requests.get(
            f"{base_url}/api/v1/retroalimentacion/postulacion/{first_application['id']}",
            headers=company_headers,
            timeout=10,
        )
        assert_status(get_feedback, 200, "get feedback by postulacion")
        feedback_payload = get_feedback.json()
        assert feedback_payload["postulacion_id"] == first_application["id"]
        assert feedback_payload["campos_mejora"] == "Mejorar SQL"

        db = SessionLocal()
        try:
            stored_application = db.query(Postulacion).filter(Postulacion.id == first_application["id"]).first()
            assert stored_application is not None
            assert stored_application.estado == "rechazado"

            stored_feedback = (
                db.query(Retroalimentacion)
                .filter(Retroalimentacion.postulacion_id == first_application["id"])
                .first()
            )
            assert stored_feedback is not None
            assert stored_feedback.campos_mejora == "Mejorar SQL"
            assert stored_feedback.id == feedback_payload["id"]
        finally:
            db.close()

        reapply_web = requests.post(
            f"{base_url}/api/v1/postulaciones/web",
            json={"estudiante_id": student_id, "vacante_id": first_vacancy_id},
            headers=student_headers,
            timeout=10,
        )
        assert_status(reapply_web, 200, "reapply after rejection")
        second_application = reapply_web.json()
        assert second_application["id"] != first_application["id"]

        student_swipe = requests.post(
            f"{base_url}/api/v1/swipes/{student_id}",
            json={"vacante_id": second_vacancy_id, "interes_estudiante": True},
            headers=student_headers,
            timeout=10,
        )
        assert_status(student_swipe, 200, "student swipe")
        assert student_swipe.json() is None

        company_swipe = requests.post(
            f"{base_url}/api/v1/swipes/empresa/{company_id}",
            json={
                "estudiante_id": student_id,
                "vacante_id": second_vacancy_id,
                "interes_empresa": True,
            },
            headers=company_headers,
            timeout=10,
        )
        assert_status(company_swipe, 200, "company swipe")
        match_payload = company_swipe.json()
        assert match_payload["estudiante_id"] == student_id
        assert match_payload["vacante_id"] == second_vacancy_id

        final_company_applications = requests.get(
            f"{base_url}/api/v1/postulaciones/empresa/{company_id}",
            headers=company_headers,
            timeout=10,
        )
        assert_status(final_company_applications, 200, "list final company applications")
        final_applications = final_company_applications.json()
        assert len(final_applications) == 3

        swipe_application = next(
            item for item in final_applications if item["vacante_id"] == second_vacancy_id
        )
        assert swipe_application["source"] == "app_swipe"
        assert swipe_application["match_id"] == match_payload["id"]

        delete_subscription = requests.delete(
            f"{base_url}/api/v1/suscripciones/{subscription_id}",
            headers=admin_headers,
            timeout=10,
        )
        assert_status(delete_subscription, 200, "delete suscripcion")

        list_subscriptions_after_delete = requests.get(
            f"{base_url}/api/v1/suscripciones/",
            headers=admin_headers,
            timeout=10,
        )
        assert_status(list_subscriptions_after_delete, 200, "list suscripciones after delete")
        assert len(list_subscriptions_after_delete.json()) == 2

        users_after_subscription_delete = requests.get(
            f"{base_url}/api/v1/user/",
            headers=admin_headers,
            timeout=10,
        )
        assert_status(users_after_subscription_delete, 200, "list users after suscripcion delete")
        student_after_delete = next(item for item in users_after_subscription_delete.json() if item["id"] == student_id)
        assert student_after_delete["es_premium"] is False

        delete_student = requests.delete(f"{base_url}/api/v1/user/{student_id}", headers=student_headers, timeout=10)
        assert_status(delete_student, 200, "delete student")

        delete_company = requests.delete(f"{base_url}/api/v1/user/{company_id}", headers=company_headers, timeout=10)
        assert_status(delete_company, 200, "delete company")

        final_users = requests.get(f"{base_url}/api/v1/user/", headers=admin_headers, timeout=10)
        assert_status(final_users, 200, "final user list")
        remaining_users = final_users.json()
        assert len(remaining_users) == 1
        assert remaining_users[0]["id"] == admin_id
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=5)

    print("full_api_flow_check: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
