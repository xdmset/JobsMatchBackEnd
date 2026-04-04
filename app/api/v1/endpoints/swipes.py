from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.dependencies import ensure_same_user, get_current_user
from app.core.enums import NombreRol
from app.crud import crud_postulacion, crud_swipe
from app.db.session import get_db
from app.models.interaccion_swipe import InteraccionSwipe
from app.models.interaccion_swipe_empresa import InteraccionSwipeEmpresa
from app.models.user import User
from app.schemas.discovery import CandidateFeedItem
from app.schemas.interaccion_swipe import SwipeCreate, SwipeEmpresaCreate
from app.schemas.match import MatchResponse
from app.schemas.vacante import Vacante
from app.services.profile_media import serialize_estudiante_profile
from app.services.subscription_service import build_plan_context

router = APIRouter()


@router.get("/{estudiante_id}/vacantes", response_model=list[Vacante])
def get_student_swipe_feed(
    estudiante_id: int,
    skip: int = 0,
    limit: int = 100,
    modalidad: str | None = None,
    ubicacion: str | None = None,
    sueldo_min: float | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_same_user(current_user, estudiante_id, NombreRol.estudiante.value)
    return crud_swipe.get_vacante_feed_for_student(
        db,
        estudiante_id=estudiante_id,
        skip=skip,
        limit=limit,
        modalidad=modalidad,
        ubicacion=ubicacion,
        sueldo_min=sueldo_min,
    )


@router.get("/empresa/{empresa_id}/candidatos", response_model=list[CandidateFeedItem])
def get_company_candidate_feed(
    empresa_id: int,
    vacante_id: int,
    skip: int = 0,
    limit: int = 100,
    ubicacion: str | None = None,
    modalidad_preferida: str | None = None,
    institucion_educativa: str | None = None,
    nivel_academico: str | None = None,
    habilidad: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_same_user(current_user, empresa_id, NombreRol.empresa.value)
    vacante = crud_swipe.get_vacante(db, vacante_id)
    if not vacante:
        raise HTTPException(status_code=404, detail="Vacante no encontrada")
    if vacante.empresa_id != empresa_id:
        raise HTTPException(status_code=403, detail="La vacante no pertenece a la empresa")

    plan_context = build_plan_context(current_user)
    if plan_context.candidate_filter_level != "advanced" and any(
        [institucion_educativa, nivel_academico, habilidad]
    ):
        raise HTTPException(
            status_code=403,
            detail="Tu plan actual solo permite filtros básicos sobre candidatos",
        )

    rows = crud_swipe.get_candidate_feed_for_company(
        db,
        empresa_id=empresa_id,
        vacante_id=vacante_id,
        skip=skip,
        limit=limit,
        ubicacion=ubicacion,
        modalidad_preferida=modalidad_preferida,
        institucion_educativa=institucion_educativa,
        nivel_academico=nivel_academico,
        habilidad=habilidad,
    )

    items = []
    for perfil_estudiante, user, swipe_estudiante in rows:
        items.append(
            CandidateFeedItem(
                usuario_id=user.id,
                email=user.email,
                es_premium=bool(user.es_premium),
                fecha_registro=user.fecha_registro,
                ya_dio_like=bool(swipe_estudiante and swipe_estudiante.interes_estudiante),
                fecha_like=(
                    swipe_estudiante.fecha_actualizacion
                    if swipe_estudiante and swipe_estudiante.interes_estudiante
                    else None
                ),
                perfil_estudiante=serialize_estudiante_profile(perfil_estudiante),
            )
        )
    return items

@router.post("/{estudiante_id}", response_model=Optional[MatchResponse])
def registrar_swipe(
    estudiante_id: int,
    swipe: SwipeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_same_user(current_user, estudiante_id, NombreRol.estudiante.value)
    # 1. Verificar Límite Freemium (RF-07)
    usuario = db.query(User).filter(User.id == estudiante_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    interaccion_existente = crud_swipe.get_swipe_estudiante(db, estudiante_id, swipe.vacante_id)

    plan_context = build_plan_context(usuario)

    if plan_context.daily_swipes_limit is not None and not interaccion_existente:
        hoy = date.today()
        conteo_hoy = db.query(InteraccionSwipe).filter(
            InteraccionSwipe.estudiante_id == estudiante_id,
            func.date(InteraccionSwipe.fecha) == hoy
        ).count()

        if conteo_hoy >= plan_context.daily_swipes_limit:
            raise HTTPException(status_code=403, detail="Límite de swipes diarios alcanzado. ¡Hazte Premium!")

    vacante = crud_swipe.get_vacante(db, swipe.vacante_id)
    if not vacante:
        raise HTTPException(status_code=404, detail="Vacante no encontrada")

    # Reenvio idempotente: no consume un swipe nuevo ni altera timestamps.
    if interaccion_existente and interaccion_existente.interes_estudiante == swipe.interes_estudiante:
        if swipe.interes_estudiante:
            match_confirmado = crud_swipe.get_match(db, estudiante_id, vacante.id)
            if match_confirmado:
                return match_confirmado
        return None

    # 2. Registrar Interacción (upsert simple)
    crud_swipe.upsert_swipe_estudiante(
        db,
        estudiante_id=estudiante_id,
        vacante_id=swipe.vacante_id,
        interes_estudiante=swipe.interes_estudiante,
    )

    match_confirmado = None

    # 3. Lógica de Match y Postulación Automática (RF-05, RF-06)
    if swipe.interes_estudiante:
        interes_empresa = db.query(InteraccionSwipeEmpresa).filter(
            InteraccionSwipeEmpresa.empresa_id == vacante.empresa_id,
            InteraccionSwipeEmpresa.estudiante_id == estudiante_id,
            InteraccionSwipeEmpresa.vacante_id == vacante.id,
            InteraccionSwipeEmpresa.interes_empresa.is_(True),
        ).first()
        if interes_empresa:
            match_existente = crud_swipe.get_match(db, estudiante_id, vacante.id)
            if match_existente:
                match_confirmado = match_existente
            else:
                match_confirmado = crud_swipe.crear_match(db, estudiante_id, vacante.id)

            crud_postulacion.crear_postulacion_si_aplica(
                db,
                estudiante_id=estudiante_id,
                vacante=vacante,
                match_id=match_confirmado.id,
                source="app_swipe",
            )

    db.commit()
    if match_confirmado:
        db.refresh(match_confirmado)
    return match_confirmado

@router.post("/empresa/{empresa_id}", response_model=Optional[MatchResponse])
def registrar_swipe_empresa(
    empresa_id: int,
    swipe: SwipeEmpresaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_same_user(current_user, empresa_id, NombreRol.empresa.value)
    vacante = crud_swipe.get_vacante(db, swipe.vacante_id)
    if not vacante:
        raise HTTPException(status_code=404, detail="Vacante no encontrada")
    if vacante.empresa_id != empresa_id:
        raise HTTPException(status_code=403, detail="La vacante no pertenece a la empresa")

    interaccion_existente = crud_swipe.get_swipe_empresa(
        db,
        empresa_id=empresa_id,
        estudiante_id=swipe.estudiante_id,
        vacante_id=swipe.vacante_id,
    )

    if interaccion_existente and interaccion_existente.interes_empresa == swipe.interes_empresa:
        if swipe.interes_empresa:
            match_confirmado = crud_swipe.get_match(db, swipe.estudiante_id, swipe.vacante_id)
            if match_confirmado:
                return match_confirmado
        return None

    crud_swipe.upsert_swipe_empresa(
        db,
        empresa_id=empresa_id,
        estudiante_id=swipe.estudiante_id,
        vacante_id=swipe.vacante_id,
        interes_empresa=swipe.interes_empresa,
    )

    match_confirmado = None
    if swipe.interes_empresa:
        interes_estudiante = db.query(InteraccionSwipe).filter(
            InteraccionSwipe.estudiante_id == swipe.estudiante_id,
            InteraccionSwipe.vacante_id == swipe.vacante_id,
            InteraccionSwipe.interes_estudiante.is_(True),
        ).first()
        if interes_estudiante:
            match_existente = crud_swipe.get_match(db, swipe.estudiante_id, swipe.vacante_id)
            if match_existente:
                match_confirmado = match_existente
            else:
                match_confirmado = crud_swipe.crear_match(db, swipe.estudiante_id, swipe.vacante_id)

            crud_postulacion.crear_postulacion_si_aplica(
                db,
                estudiante_id=swipe.estudiante_id,
                vacante=vacante,
                match_id=match_confirmado.id,
                source="app_swipe",
            )

    db.commit()
    if match_confirmado:
        db.refresh(match_confirmado)
    return match_confirmado
