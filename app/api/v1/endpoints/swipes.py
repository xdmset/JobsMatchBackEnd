from typing import Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.schemas.interaccion_swipe import SwipeCreate, SwipeEmpresaCreate
from app.schemas.match import MatchResponse
from app.models.interaccion_swipe import InteraccionSwipe
from app.models.interaccion_swipe_empresa import InteraccionSwipeEmpresa
from app.models.user import User
from app.crud import crud_swipe, crud_postulacion

router = APIRouter()

@router.post("/{estudiante_id}", response_model=Optional[MatchResponse])
def registrar_swipe(estudiante_id: int, swipe: SwipeCreate, db: Session = Depends(get_db)):
    # 1. Verificar Límite Freemium (RF-07)
    usuario = db.query(User).filter(User.id == estudiante_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if not usuario.es_premium:
        hoy = date.today()
        conteo_hoy = db.query(InteraccionSwipe).filter(
            InteraccionSwipe.estudiante_id == estudiante_id,
            func.date(InteraccionSwipe.fecha) == hoy
        ).count()

        if conteo_hoy >= 10:
            raise HTTPException(status_code=403, detail="Límite de swipes diarios alcanzado. ¡Hazte Premium!")

    vacante = crud_swipe.get_vacante(db, swipe.vacante_id)
    if not vacante:
        raise HTTPException(status_code=404, detail="Vacante no encontrada")

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
            InteraccionSwipeEmpresa.interes_empresa == True
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
def registrar_swipe_empresa(empresa_id: int, swipe: SwipeEmpresaCreate, db: Session = Depends(get_db)):
    vacante = crud_swipe.get_vacante(db, swipe.vacante_id)
    if not vacante:
        raise HTTPException(status_code=404, detail="Vacante no encontrada")
    if vacante.empresa_id != empresa_id:
        raise HTTPException(status_code=403, detail="La vacante no pertenece a la empresa")

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
            InteraccionSwipe.interes_estudiante == True
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
