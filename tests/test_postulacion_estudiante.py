from datetime import date
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.v1.endpoints.postulaciones import (
    crear_postulacion_web,
    listar_postulaciones_estudiante,
    actualizar_estado,
)
from app.api.v1.endpoints.retroalimentacion import read_retroalimentacion_by_postulacion
from app.core.enums import NombreRol
from app.crud.crud_vacante import create_vacante
from app.db.base import Base
from app.models.perfil_empresa import PerfilEmpresa
from app.models.perfil_estudiante import PerfilEstudiante
from app.models.retroalimentacion import Retroalimentacion
from app.models.rol import Role
from app.models.user import User
from app.schemas.perfil_empresa import PerfilEmpresaCreate
from app.schemas.perfil_estudiante import PerfilEstudianteCreate
from app.schemas.postulacion import CambiarEstadoPostulacion, PostulacionWebCreate, RetroalimentacionCreate
from app.schemas.vacante import VacanteCreate


def _build_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return Session()


def _seed(db):
    rol_estudiante = Role(nombre=NombreRol.estudiante)
    rol_empresa = Role(nombre=NombreRol.empresa)
    db.add_all([rol_estudiante, rol_empresa])
    db.flush()

    estudiante = User(
        email="student-postulacion@example.com",
        password_hash="hashed",
        rol_id=rol_estudiante.id,
        rol=rol_estudiante,
    )
    empresa = User(
        email="company-postulacion@example.com",
        password_hash="hashed",
        rol_id=rol_empresa.id,
        rol=rol_empresa,
    )
    db.add_all([estudiante, empresa])
    db.flush()

    db.add(
        PerfilEstudiante(
            usuario_id=estudiante.id,
            **PerfilEstudianteCreate(
                nombre_completo="Ana Test",
                institucion_educativa="UT",
                nivel_academico="Licenciatura",
                fecha_nacimiento=date(2002, 1, 10),
                habilidades=["python", "fastapi"],
            ).model_dump(),
        )
    )
    db.add(
        PerfilEmpresa(
            usuario_id=empresa.id,
            **PerfilEmpresaCreate(nombre_comercial="Empresa Test").model_dump(),
        )
    )
    db.commit()

    vacante = create_vacante(
        db,
        VacanteCreate(
            titulo="Backend Jr",
            descripcion="FastAPI developer",
            requisitos="Python, SQL",
            modalidad="remoto",
        ),
        empresa.id,
    )
    return estudiante, empresa, vacante


# ---------------------------------------------------------------------------
# Tests del endpoint GET /postulaciones/estudiante/{estudiante_id}
# ---------------------------------------------------------------------------

def test_estudiante_puede_listar_sus_postulaciones():
    db = _build_db()
    try:
        estudiante, empresa, vacante = _seed(db)

        postulacion = crear_postulacion_web(
            PostulacionWebCreate(estudiante_id=estudiante.id, vacante_id=vacante.id),
            db=db,
            current_user=estudiante,
        )
        db.commit()

        resultado = listar_postulaciones_estudiante(
            estudiante.id,
            estado=None,
            db=db,
            current_user=estudiante,
        )

        assert len(resultado) == 1
        assert resultado[0].id == postulacion.id
        assert resultado[0].estudiante_id == estudiante.id
        assert resultado[0].vacante_id == vacante.id
        assert resultado[0].estado == "enviado"
    finally:
        db.close()


def test_estudiante_lista_postulaciones_vacias():
    db = _build_db()
    try:
        estudiante, _, _ = _seed(db)

        resultado = listar_postulaciones_estudiante(
            estudiante.id,
            estado=None,
            db=db,
            current_user=estudiante,
        )

        assert resultado == []
    finally:
        db.close()


def test_estudiante_filtra_postulaciones_por_estado():
    db = _build_db()
    try:
        estudiante, empresa, vacante = _seed(db)

        postulacion = crear_postulacion_web(
            PostulacionWebCreate(estudiante_id=estudiante.id, vacante_id=vacante.id),
            db=db,
            current_user=estudiante,
        )
        db.commit()

        with patch("app.services.feedback_roadmap_service.generate_roadmap_for_postulacion"):
            actualizar_estado(
                postulacion.id,
                CambiarEstadoPostulacion(
                    nuevo_estado="rechazado",
                    feedback=RetroalimentacionCreate(
                        campos_mejora="Mejorar SQL",
                        sugerencias_perfil="Agregar proyectos backend",
                    ),
                ),
                db=db,
                current_user=empresa,
            )
        db.commit()

        rechazadas = listar_postulaciones_estudiante(
            estudiante.id,
            estado="rechazado",
            db=db,
            current_user=estudiante,
        )
        enviadas = listar_postulaciones_estudiante(
            estudiante.id,
            estado="enviado",
            db=db,
            current_user=estudiante,
        )

        assert len(rechazadas) == 1
        assert rechazadas[0].estado == "rechazado"
        assert len(enviadas) == 0
    finally:
        db.close()


def test_empresa_no_puede_listar_postulaciones_de_estudiante():
    db = _build_db()
    try:
        estudiante, empresa, vacante = _seed(db)

        crear_postulacion_web(
            PostulacionWebCreate(estudiante_id=estudiante.id, vacante_id=vacante.id),
            db=db,
            current_user=estudiante,
        )
        db.commit()

        with pytest.raises(HTTPException) as exc_info:
            listar_postulaciones_estudiante(
                estudiante.id,
                estado=None,
                db=db,
                current_user=empresa,
            )

        assert exc_info.value.status_code == 403
    finally:
        db.close()


def test_estudiante_no_puede_ver_postulaciones_de_otro_estudiante():
    db = _build_db()
    try:
        estudiante, _, _ = _seed(db)

        rol_estudiante = db.query(Role).filter(Role.nombre == NombreRol.estudiante).first()
        otro = User(
            email="otro-student@example.com",
            password_hash="hashed",
            rol_id=rol_estudiante.id,
            rol=rol_estudiante,
        )
        db.add(otro)
        db.commit()

        with pytest.raises(HTTPException) as exc_info:
            listar_postulaciones_estudiante(
                estudiante.id,
                estado=None,
                db=db,
                current_user=otro,
            )

        assert exc_info.value.status_code == 403
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Tests de retroalimentación accesible por el estudiante
# ---------------------------------------------------------------------------

def test_estudiante_puede_leer_su_retroalimentacion():
    db = _build_db()
    try:
        estudiante, empresa, vacante = _seed(db)

        postulacion = crear_postulacion_web(
            PostulacionWebCreate(estudiante_id=estudiante.id, vacante_id=vacante.id),
            db=db,
            current_user=estudiante,
        )
        db.commit()

        with patch("app.services.feedback_roadmap_service.generate_roadmap_for_postulacion"):
            actualizar_estado(
                postulacion.id,
                CambiarEstadoPostulacion(
                    nuevo_estado="rechazado",
                    feedback=RetroalimentacionCreate(
                        campos_mejora="Mejorar SQL",
                        sugerencias_perfil="Agregar proyectos backend",
                    ),
                ),
                db=db,
                current_user=empresa,
            )
        db.commit()

        # El estudiante usa el postulacion_id de su lista para leer la retro
        mis_postulaciones = listar_postulaciones_estudiante(
            estudiante.id,
            estado=None,
            db=db,
            current_user=estudiante,
        )
        postulacion_id = mis_postulaciones[0].id

        retro = read_retroalimentacion_by_postulacion(
            postulacion_id,
            db=db,
            current_user=estudiante,
        )

        assert retro.postulacion_id == postulacion_id
        assert retro.campos_mejora == "Mejorar SQL"
        assert retro.sugerencias_perfil == "Agregar proyectos backend"
    finally:
        db.close()


def test_estudiante_sin_retroalimentacion_obtiene_404():
    db = _build_db()
    try:
        estudiante, empresa, vacante = _seed(db)

        postulacion = crear_postulacion_web(
            PostulacionWebCreate(estudiante_id=estudiante.id, vacante_id=vacante.id),
            db=db,
            current_user=estudiante,
        )
        db.commit()

        with pytest.raises(HTTPException) as exc_info:
            read_retroalimentacion_by_postulacion(
                postulacion.id,
                db=db,
                current_user=estudiante,
            )

        assert exc_info.value.status_code == 404
    finally:
        db.close()


def test_otro_estudiante_no_puede_leer_retroalimentacion_ajena():
    db = _build_db()
    try:
        estudiante, empresa, vacante = _seed(db)

        postulacion = crear_postulacion_web(
            PostulacionWebCreate(estudiante_id=estudiante.id, vacante_id=vacante.id),
            db=db,
            current_user=estudiante,
        )
        db.commit()

        with patch("app.services.feedback_roadmap_service.generate_roadmap_for_postulacion"):
            actualizar_estado(
                postulacion.id,
                CambiarEstadoPostulacion(
                    nuevo_estado="rechazado",
                    feedback=RetroalimentacionCreate(
                        campos_mejora="Mejorar SQL",
                        sugerencias_perfil="Agregar proyectos",
                    ),
                ),
                db=db,
                current_user=empresa,
            )
        db.commit()

        rol_estudiante = db.query(Role).filter(Role.nombre == NombreRol.estudiante).first()
        intruso = User(
            email="intruso@example.com",
            password_hash="hashed",
            rol_id=rol_estudiante.id,
            rol=rol_estudiante,
        )
        db.add(intruso)
        db.commit()

        with pytest.raises(HTTPException) as exc_info:
            read_retroalimentacion_by_postulacion(
                postulacion.id,
                db=db,
                current_user=intruso,
            )

        assert exc_info.value.status_code == 403
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Tests del fallback heurístico en feedback_roadmap_service
# ---------------------------------------------------------------------------

def test_roadmap_queda_en_error_cuando_gemini_falla():
    """Sin fallback heurístico: si Gemini falla, roadmap_estado queda en 'error' con detalle del error."""
    from app.services.feedback_roadmap_service import generate_roadmap_for_retroalimentacion

    db = _build_db()
    try:
        estudiante, empresa, vacante = _seed(db)

        postulacion = crear_postulacion_web(
            PostulacionWebCreate(estudiante_id=estudiante.id, vacante_id=vacante.id),
            db=db,
            current_user=estudiante,
        )
        db.commit()

        retro = Retroalimentacion(
            postulacion_id=postulacion.id,
            campos_mejora="Mejorar SQL y comunicación",
            sugerencias_perfil="Agregar proyectos backend en GitHub",
            roadmap_estado="pendiente",
        )
        db.add(retro)
        db.commit()

        with patch(
            "app.services.feedback_roadmap_service._generate_roadmap_payload",
            side_effect=Exception("Connection timeout simulado"),
        ):
            resultado = generate_roadmap_for_retroalimentacion(db, retro)
            db.commit()

        assert resultado.roadmap_estado == "error"
        assert resultado.roadmap_json is None
        assert "Connection timeout simulado" in resultado.roadmap_error
    finally:
        db.close()


def test_roadmap_usa_gemini_cuando_responde_correctamente():
    """Si Gemini responde con JSON válido, se usa su resultado."""
    from app.services.feedback_roadmap_service import generate_roadmap_for_retroalimentacion

    gemini_response = {
        "habilidades": ["SQL avanzado", "FastAPI"],
        "acciones": ["Practicar SQL", "Construir API"],
        "recursos": ["SQLBolt", "FastAPI docs"],
        "tiempo_estimado": "4 semanas",
        "prioridad": "Alta",
        "roadmap_detallado": [
            {"semana": "Semana 1", "objetivo": "SQL", "tareas": ["Ejercicios JOIN"]},
        ],
    }

    db = _build_db()
    try:
        estudiante, empresa, vacante = _seed(db)

        postulacion = crear_postulacion_web(
            PostulacionWebCreate(estudiante_id=estudiante.id, vacante_id=vacante.id),
            db=db,
            current_user=estudiante,
        )
        db.commit()

        retro = Retroalimentacion(
            postulacion_id=postulacion.id,
            campos_mejora="Mejorar SQL",
            sugerencias_perfil="Agregar proyectos",
            roadmap_estado="pendiente",
        )
        db.add(retro)
        db.commit()

        with patch(
            "app.services.feedback_roadmap_service._generate_roadmap_payload",
            return_value=gemini_response,
        ):
            resultado = generate_roadmap_for_retroalimentacion(db, retro)
            db.commit()

        assert resultado.roadmap_estado == "generado"
        assert resultado.roadmap_json["habilidades"] == ["SQL avanzado", "FastAPI"]
        assert resultado.roadmap_json["tiempo_estimado"] == "4 semanas"
    finally:
        db.close()
