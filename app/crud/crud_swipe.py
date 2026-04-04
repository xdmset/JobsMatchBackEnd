from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session

from app.models.interaccion_swipe import InteraccionSwipe
from app.models.interaccion_swipe_empresa import InteraccionSwipeEmpresa
from app.models.match import Match
from app.models.vacante import Vacante


def get_vacante(db: Session, vacante_id: int) -> Optional[Vacante]:
    return db.query(Vacante).filter(Vacante.id == vacante_id).first()


def get_swipe_estudiante(
    db: Session,
    estudiante_id: int,
    vacante_id: int,
) -> Optional[InteraccionSwipe]:
    return db.query(InteraccionSwipe).filter(
        InteraccionSwipe.estudiante_id == estudiante_id,
        InteraccionSwipe.vacante_id == vacante_id,
    ).first()


def get_swipe_empresa(
    db: Session,
    empresa_id: int,
    estudiante_id: int,
    vacante_id: int,
) -> Optional[InteraccionSwipeEmpresa]:
    return db.query(InteraccionSwipeEmpresa).filter(
        InteraccionSwipeEmpresa.empresa_id == empresa_id,
        InteraccionSwipeEmpresa.estudiante_id == estudiante_id,
        InteraccionSwipeEmpresa.vacante_id == vacante_id,
    ).first()


def upsert_swipe_estudiante(
    db: Session,
    estudiante_id: int,
    vacante_id: int,
    interes_estudiante: bool,
) -> InteraccionSwipe:
    interaccion = get_swipe_estudiante(db, estudiante_id, vacante_id)
    if interaccion:
        interaccion.interes_estudiante = interes_estudiante
        interaccion.fecha_actualizacion = datetime.now(timezone.utc)
        return interaccion

    nueva_interaccion = InteraccionSwipe(
        estudiante_id=estudiante_id,
        vacante_id=vacante_id,
        interes_estudiante=interes_estudiante,
        fecha_actualizacion=datetime.now(timezone.utc),
    )
    db.add(nueva_interaccion)
    return nueva_interaccion


def upsert_swipe_empresa(
    db: Session,
    empresa_id: int,
    estudiante_id: int,
    vacante_id: int,
    interes_empresa: bool,
) -> InteraccionSwipeEmpresa:
    interaccion = get_swipe_empresa(db, empresa_id, estudiante_id, vacante_id)
    if interaccion:
        interaccion.interes_empresa = interes_empresa
        interaccion.fecha_actualizacion = datetime.now(timezone.utc)
        return interaccion

    nueva_interaccion = InteraccionSwipeEmpresa(
        empresa_id=empresa_id,
        estudiante_id=estudiante_id,
        vacante_id=vacante_id,
        interes_empresa=interes_empresa,
        fecha_actualizacion=datetime.now(timezone.utc),
    )
    db.add(nueva_interaccion)
    return nueva_interaccion


def get_match(db: Session, estudiante_id: int, vacante_id: int) -> Optional[Match]:
    return db.query(Match).filter(
        Match.estudiante_id == estudiante_id,
        Match.vacante_id == vacante_id
    ).first()


def crear_match(db: Session, estudiante_id: int, vacante_id: int) -> Match:
    match_confirmado = Match(estudiante_id=estudiante_id, vacante_id=vacante_id)
    db.add(match_confirmado)
    db.flush()
    return match_confirmado
