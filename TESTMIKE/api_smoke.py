#!/usr/bin/env python3
"""Simple smoke tests for the FastAPI service.

Default is read-only checks. Use flags to test ID-based endpoints.
"""
from __future__ import annotations

import argparse
import json
import time
from typing import Iterable, Optional

import requests


def _now_ms() -> int:
    return int(time.time() * 1000)


def _print_result(name: str, method: str, url: str, status: int | None, elapsed_ms: int, note: str = "") -> None:
    status_txt = str(status) if status is not None else "ERR"
    note_txt = f" | {note}" if note else ""
    print(f"{name:24} {method:6} {status_txt:4} {elapsed_ms:5}ms {url}{note_txt}")


def _request(method: str, url: str, **kwargs) -> tuple[int | None, int, str]:
    start = _now_ms()
    try:
        resp = requests.request(method, url, timeout=kwargs.pop("timeout", 10), **kwargs)
        elapsed = _now_ms() - start
        return resp.status_code, elapsed, resp.text
    except requests.RequestException as exc:
        elapsed = _now_ms() - start
        return None, elapsed, str(exc)


def _expect_ok(status: int | None) -> bool:
    return status is not None and 200 <= status < 300


def _check_openapi(base_url: str) -> dict:
    url = f"{base_url}/openapi.json"
    status, elapsed, body = _request("GET", url)
    _print_result("openapi", "GET", url, status, elapsed)
    if not _expect_ok(status):
        return {}
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return {}


def _check_docs(base_url: str) -> None:
    url = f"{base_url}/docs"
    status, elapsed, _ = _request("GET", url)
    _print_result("docs", "GET", url, status, elapsed)


def _check_list_users(base_url: str) -> None:
    url = f"{base_url}/api/v1/user/"
    status, elapsed, _ = _request("GET", url)
    _print_result("list_users", "GET", url, status, elapsed)

def _check_list_vacantes(base_url: str) -> None:
    url = f"{base_url}/api/v1/vacante/"
    status, elapsed, _ = _request("GET", url)
    _print_result("list_vacantes", "GET", url, status, elapsed)


def _check_list_suscripciones(base_url: str) -> None:
    url = f"{base_url}/api/v1/suscripciones/"
    status, elapsed, _ = _request("GET", url)
    _print_result("list_suscripciones", "GET", url, status, elapsed)


def _check_get_by_id(base_url: str, name: str, path: str, item_id: int | None) -> None:
    if item_id is None:
        return
    url = f"{base_url}{path}/{item_id}"
    status, elapsed, _ = _request("GET", url)
    _print_result(name, "GET", url, status, elapsed)


def _check_openapi_paths(openapi: dict, expected_paths: Iterable[str]) -> None:
    paths = set((openapi.get("paths") or {}).keys())
    for p in expected_paths:
        note = "OK" if p in paths else "MISSING"
        print(f"path_check             {p} {note}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test API endpoints")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Base URL (default: http://localhost:8000)")
    parser.add_argument("--estudiante-id", type=int, default=None, help="ID to test /perfil_estudiante/{id}")
    parser.add_argument("--empresa-id", type=int, default=None, help="ID to test /perfil_empresa/{id}")
    parser.add_argument("--write", action="store_true", help="Create/update test users and exercise write endpoints")
    parser.add_argument("--cleanup", action="store_true", help="Attempt to delete test users (may fail if data remains)")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")

    openapi = _check_openapi(base_url)
    _check_docs(base_url)

    _check_list_users(base_url)
    _check_list_vacantes(base_url)
    _check_list_suscripciones(base_url)
    _check_get_by_id(base_url, "perfil_estudiante", "/api/v1/perfil_estudiante", args.estudiante_id)
    _check_get_by_id(base_url, "perfil_empresa", "/api/v1/perfil_empresa", args.empresa_id)

    if openapi:
        _check_openapi_paths(
            openapi,
            [
                "/api/v1/user/",
                "/api/v1/perfil_estudiante/{usuario_id}",
                "/api/v1/perfil_empresa/{user_id}",
                "/api/v1/media/estudiantes/{usuario_id}/cv",
                "/api/v1/vacante/{empresa_id}",
                "/api/v1/postulaciones/empresa/{empresa_id}",
                "/api/v1/postulaciones/estudiante/{estudiante_id}",
                "/api/v1/retroalimentacion/postulacion/{postulacion_id}",
                "/api/v1/suscripciones/",
                "/api/v1/suscripciones/usuario/{usuario_id}",
                "/api/v1/suscripciones/{suscripcion_id}",
                "/api/v1/swipes/empresa/{empresa_id}",
            ],
        )

    if args.write:
        _run_write_flow(base_url, cleanup=args.cleanup)

    return 0


def _post_json(url: str, payload: dict) -> tuple[int | None, int, dict | None, str]:
    status, elapsed, body = _request("POST", url, json=payload)
    data = None
    if status is not None and body:
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            data = None
    return status, elapsed, data, body


def _put_json(url: str, payload: dict) -> tuple[int | None, int, dict | None, str]:
    status, elapsed, body = _request("PUT", url, json=payload)
    data = None
    if status is not None and body:
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            data = None
    return status, elapsed, data, body

def _get_json(url: str) -> tuple[int | None, int, dict | list | None, str]:
    status, elapsed, body = _request("GET", url)
    data = None
    if status is not None and body:
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            data = None
    return status, elapsed, data, body


def _delete(url: str) -> tuple[int | None, int, str]:
    return _request("DELETE", url)


def _run_write_flow(base_url: str, cleanup: bool = False) -> None:
    # Create a student and an empresa user, update profiles, then delete users.
    ts = int(time.time())
    student_email = f"smoke_student_{ts}@example.com"
    empresa_email = f"smoke_empresa_{ts}@example.com"

    student_payload = {
        "email": student_email,
        "password": "Test1234!",
        "rol_id": 2,
        "perfil_estudiante": {
            "nombre_completo": "Smoke Test Student",
            "institucion_educativa": "Smoke University",
            "nivel_academico": "Licenciatura",
            "biografia": "Perfil creado por pruebas.",
            "habilidades": ["python", "fastapi"],
            "ubicacion": "Remote",
            "modalidad_preferida": "remoto",
        },
    }

    empresa_payload = {
        "email": empresa_email,
        "password": "Test1234!",
        "rol_id": 3,
        "perfil_empresa": {
            "nombre_comercial": "Smoke Empresa",
            "sector": "Tecnologia",
            "descripcion": "Perfil empresa de pruebas.",
            "sitio_web": "https://example.com",
            "ubicacion_sede": "Remote",
            "foto_perfil_url": "https://example.com/logo.png",
        },
    }

    user_url = f"{base_url}/api/v1/user/"

    s_status, s_elapsed, s_data, _ = _post_json(user_url, student_payload)
    _print_result("create_student", "POST", user_url, s_status, s_elapsed)
    student_id: Optional[int] = None
    if s_data and isinstance(s_data, dict):
        student_id = s_data.get("id")

    e_status, e_elapsed, e_data, _ = _post_json(user_url, empresa_payload)
    _print_result("create_empresa", "POST", user_url, e_status, e_elapsed)
    empresa_id: Optional[int] = None
    if e_data and isinstance(e_data, dict):
        empresa_id = e_data.get("id")

    if student_id is not None:
        update_estudiante_url = f"{base_url}/api/v1/perfil_estudiante/{student_id}"
        update_estudiante_payload = {
            "nombre_completo": "Smoke Test Student",
            "institucion_educativa": "Smoke University",
            "nivel_academico": "Licenciatura",
            "biografia": "Perfil actualizado por pruebas.",
            "habilidades": ["python", "fastapi", "sqlalchemy"],
            "ubicacion": "Remote",
            "modalidad_preferida": "remoto",
        }
        u_status, u_elapsed, _, _ = _put_json(update_estudiante_url, update_estudiante_payload)
        _print_result("update_student", "PUT", update_estudiante_url, u_status, u_elapsed)

    if empresa_id is not None:
        update_empresa_url = f"{base_url}/api/v1/perfil_empresa/{empresa_id}"
        update_empresa_payload = {
            "nombre_comercial": "Smoke Empresa",
            "sector": "Tecnologia",
            "descripcion": "Perfil empresa actualizado por pruebas.",
            "sitio_web": "https://example.com",
            "ubicacion_sede": "Remote",
            "foto_perfil_url": "https://example.com/logo.png",
        }
        u_status, u_elapsed, _, _ = _put_json(update_empresa_url, update_empresa_payload)
        _print_result("update_empresa", "PUT", update_empresa_url, u_status, u_elapsed)

    suscripcion_id: Optional[int] = None
    if student_id is not None:
        list_suscripcion_usuario_url = f"{base_url}/api/v1/suscripciones/usuario/{student_id}"
        l_status, l_elapsed, l_data, _ = _get_json(list_suscripcion_usuario_url)
        _print_result("list_suscripcion_u", "GET", list_suscripcion_usuario_url, l_status, l_elapsed)
        if isinstance(l_data, list) and l_data and isinstance(l_data[0], dict):
            suscripcion_id = l_data[0].get("id")

    if suscripcion_id is not None:
        update_suscripcion_url = f"{base_url}/api/v1/suscripciones/{suscripcion_id}"
        update_suscripcion_payload = {
            "tipo_plan": "premium",
            "fecha_fin": "2026-05-08",
        }
        u_status, u_elapsed, _, _ = _put_json(update_suscripcion_url, update_suscripcion_payload)
        _print_result("update_suscripcion", "PUT", update_suscripcion_url, u_status, u_elapsed)

    vacante_id_primary: Optional[int] = None
    vacante_id_secondary: Optional[int] = None

    if empresa_id is not None:
        vacante_url = f"{base_url}/api/v1/vacante/{empresa_id}"
        vacante_payload_1 = {
            "titulo": "Vacante Smoke 1",
            "descripcion": "Vacante de prueba para swipes.",
            "requisitos": "Python, FastAPI",
            "modalidad": "remoto",
            "ubicacion": "Remote",
            "sueldo_minimo": 1000,
            "sueldo_maximo": 2000,
        }
        v_status, v_elapsed, v_data, _ = _post_json(vacante_url, vacante_payload_1)
        _print_result("create_vacante1", "POST", vacante_url, v_status, v_elapsed)
        if v_data and isinstance(v_data, dict):
            vacante_id_primary = v_data.get("id")

        vacante_payload_2 = {
            "titulo": "Vacante Smoke 2",
            "descripcion": "Vacante de prueba para postulacion web.",
            "requisitos": "SQL, QA",
            "modalidad": "presencial",
            "ubicacion": "CDMX",
            "sueldo_minimo": 900,
            "sueldo_maximo": 1500,
        }
        v_status, v_elapsed, v_data, _ = _post_json(vacante_url, vacante_payload_2)
        _print_result("create_vacante2", "POST", vacante_url, v_status, v_elapsed)
        if v_data and isinstance(v_data, dict):
            vacante_id_secondary = v_data.get("id")

    if vacante_id_primary is not None:
        vacante_get_url = f"{base_url}/api/v1/vacante/{vacante_id_primary}"
        g_status, g_elapsed, _, _ = _get_json(vacante_get_url)
        _print_result("get_vacante1", "GET", vacante_get_url, g_status, g_elapsed)

        vacante_update_estado_url = f"{base_url}/api/v1/vacante/{vacante_id_primary}"
        vacante_update_estado_payload = {"estado": "pausada"}
        g_status, g_elapsed, _, _ = _put_json(vacante_update_estado_url, vacante_update_estado_payload)
        _print_result("vacante_estado", "PUT", vacante_update_estado_url, g_status, g_elapsed)

    if student_id is not None and vacante_id_primary is not None:
        swipe_url = f"{base_url}/api/v1/swipes/{student_id}"
        swipe_payload = {"vacante_id": vacante_id_primary, "interes_estudiante": True}
        s_status, s_elapsed, _, _ = _post_json(swipe_url, swipe_payload)
        _print_result("swipe_student", "POST", swipe_url, s_status, s_elapsed)

    if empresa_id is not None and student_id is not None and vacante_id_primary is not None:
        swipe_empresa_url = f"{base_url}/api/v1/swipes/empresa/{empresa_id}"
        swipe_empresa_payload = {
            "estudiante_id": student_id,
            "vacante_id": vacante_id_primary,
            "interes_empresa": True,
        }
        s_status, s_elapsed, _, _ = _post_json(swipe_empresa_url, swipe_empresa_payload)
        _print_result("swipe_empresa", "POST", swipe_empresa_url, s_status, s_elapsed)

    postulacion_id: Optional[int] = None
    if empresa_id is not None:
        list_post_url = f"{base_url}/api/v1/postulaciones/empresa/{empresa_id}"
        l_status, l_elapsed, l_data, _ = _get_json(list_post_url)
        _print_result("list_postulaciones", "GET", list_post_url, l_status, l_elapsed)
        if isinstance(l_data, list) and vacante_id_primary is not None:
            for item in l_data:
                if isinstance(item, dict) and item.get("vacante_id") == vacante_id_primary:
                    postulacion_id = item.get("id")
                    break

    if student_id is not None:
        list_student_post_url = f"{base_url}/api/v1/postulaciones/estudiante/{student_id}"
        l_status, l_elapsed, l_data, _ = _get_json(list_student_post_url)
        _print_result("list_post_student", "GET", list_student_post_url, l_status, l_elapsed)

    if postulacion_id is not None:
        update_post_url = f"{base_url}/api/v1/postulaciones/{postulacion_id}/estado"
        update_post_payload = {
            "nuevo_estado": "rechazado",
            "feedback": {
                "campos_mejora": "Falta experiencia en APIs.",
                "sugerencias_perfil": "Agregar proyectos con FastAPI.",
            },
        }
        u_status, u_elapsed, _, _ = _put_json(update_post_url, update_post_payload)
        _print_result("postulacion_estado", "PUT", update_post_url, u_status, u_elapsed)

        retro_url = f"{base_url}/api/v1/retroalimentacion/postulacion/{postulacion_id}"
        r_status, r_elapsed, _, _ = _get_json(retro_url)
        _print_result("get_retro", "GET", retro_url, r_status, r_elapsed)

    if student_id is not None and vacante_id_secondary is not None:
        web_post_url = f"{base_url}/api/v1/postulaciones/web"
        web_post_payload = {"estudiante_id": student_id, "vacante_id": vacante_id_secondary}
        p_status, p_elapsed, _, _ = _post_json(web_post_url, web_post_payload)
        _print_result("postulacion_web", "POST", web_post_url, p_status, p_elapsed)

    if cleanup and student_id is not None:
        if suscripcion_id is not None:
            delete_suscripcion_url = f"{base_url}/api/v1/suscripciones/{suscripcion_id}"
            d_status, d_elapsed, _ = _delete(delete_suscripcion_url)
            _print_result("delete_suscripcion", "DELETE", delete_suscripcion_url, d_status, d_elapsed)

        delete_student_url = f"{base_url}/api/v1/user/{student_id}"
        d_status, d_elapsed, _ = _delete(delete_student_url)
        _print_result("delete_student", "DELETE", delete_student_url, d_status, d_elapsed)

    if cleanup and empresa_id is not None:
        delete_empresa_url = f"{base_url}/api/v1/user/{empresa_id}"
        d_status, d_elapsed, _ = _delete(delete_empresa_url)
        _print_result("delete_empresa", "DELETE", delete_empresa_url, d_status, d_elapsed)


if __name__ == "__main__":
    raise SystemExit(main())
