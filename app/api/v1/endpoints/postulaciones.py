from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import ensure_roles, ensure_same_user, get_current_user
from app.core.enums import NombreRol
from app.db.session import get_db
from app.schemas.postulacion import PostulacionWebCreate, PostulacionRead, CambiarEstadoPostulacion
from app.models.postulacion import Postulacion
from app.models.user import User
from app.crud import crud_postulacion
from app.services.feedback_roadmap_service import generate_roadmap_for_postulacion
from app.services.subscription_service import build_plan_context

router = APIRouter()

@router.post("/web", response_model=PostulacionRead)
def crear_postulacion_web(
    data: PostulacionWebCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_same_user(current_user, data.estudiante_id, NombreRol.estudiante.value)
    vacante = crud_postulacion.get_vacante(db, data.vacante_id)
    if not vacante:
        raise HTTPException(status_code=404, detail="Vacante no encontrada")

    if not crud_postulacion.puede_reaplicar(db, data.estudiante_id, data.vacante_id):
        raise HTTPException(
            status_code=409,
            detail="No puedes postularte de nuevo hasta que la última postulación sea rechazada."
        )

    nueva_postulacion = crud_postulacion.crear_postulacion_si_aplica(
        db,
        estudiante_id=data.estudiante_id,
        vacante=vacante,
        match_id=None,
        source="web_apply",
    )
    if not nueva_postulacion:
        raise HTTPException(
            status_code=409,
            detail="No puedes postularte de nuevo hasta que la última postulación sea rechazada."
        )

    db.commit()
    db.refresh(nueva_postulacion)
    return nueva_postulacion

@router.get("/empresa/{empresa_id}", response_model=List[PostulacionRead])
def listar_postulaciones_empresa(
    empresa_id: int,
    estado: str | None = Query(None),
    institucion_educativa: str | None = Query(None),
    nivel_academico: str | None = Query(None),
    ubicacion: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_same_user(current_user, empresa_id, NombreRol.empresa.value)
    """RF-06: Permite a la empresa ver quiénes han aplicado a sus vacantes."""
    plan_context = build_plan_context(current_user)

    if plan_context.candidate_filter_level != "advanced" and any(
        [institucion_educativa, nivel_academico, ubicacion]
    ):
        raise HTTPException(
            status_code=403,
            detail="Tu plan actual solo permite filtros básicos sobre postulantes",
        )

    return crud_postulacion.listar_postulaciones_empresa(
        db,
        empresa_id,
        estado=estado,
        institucion_educativa=institucion_educativa,
        nivel_academico=nivel_academico,
        ubicacion=ubicacion,
    )

@router.put("/{postulacion_id}/estado")
def actualizar_estado(
    postulacion_id: int,
    data: CambiarEstadoPostulacion,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """RF-06 y RF-11: Cambia el estado y agrega feedback si es rechazo."""
    postulacion = db.query(Postulacion).filter(Postulacion.id == postulacion_id).first()
    if not postulacion:
        raise HTTPException(status_code=404, detail="Postulación no encontrada")
    if current_user.id != postulacion.empresa_id:
        ensure_roles(current_user, NombreRol.admin.value)

    feedback_payload = None
    if data.feedback:
        feedback_payload = {
            "campos_mejora": data.feedback.campos_mejora,
            "sugerencias_perfil": data.feedback.sugerencias_perfil,
        }

    crud_postulacion.actualizar_estado_postulacion(
        db,
        postulacion_id=postulacion_id,
        nuevo_estado=data.nuevo_estado,
        feedback=feedback_payload,
    )

    db.commit()
    if data.nuevo_estado == "rechazado" and feedback_payload:
        generate_roadmap_for_postulacion(db, postulacion_id)
        db.commit()
    return {"message": "Estado actualizado con éxito"}
