from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import case

from app.models.interaccion_swipe import InteraccionSwipe
from app.models.interaccion_swipe_empresa import InteraccionSwipeEmpresa
from app.models.match import Match
from app.models.perfil_estudiante import PerfilEstudiante
from app.models.user import User
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


def get_candidate_feed_for_company(
    db: Session,
    *,
    empresa_id: int,
    vacante_id: int,
    skip: int = 0,
    limit: int = 100,
    ubicacion: str | None = None,
    modalidad_preferida: str | None = None,
    institucion_educativa: str | None = None,
    nivel_academico: str | None = None,
    habilidad: str | None = None,
):
    query = (
        db.query(PerfilEstudiante, User, InteraccionSwipe)
        .join(User, User.id == PerfilEstudiante.usuario_id)
        .outerjoin(
            InteraccionSwipeEmpresa,
            (InteraccionSwipeEmpresa.empresa_id == empresa_id)
            & (InteraccionSwipeEmpresa.estudiante_id == PerfilEstudiante.usuario_id)
            & (InteraccionSwipeEmpresa.vacante_id == vacante_id),
        )
        .outerjoin(
            InteraccionSwipe,
            (InteraccionSwipe.estudiante_id == PerfilEstudiante.usuario_id)
            & (InteraccionSwipe.vacante_id == vacante_id),
        )
        .filter(InteraccionSwipeEmpresa.id.is_(None))
        .filter(User.is_active.is_(True))
        .order_by(
            User.es_premium.desc(),
            case((InteraccionSwipe.interes_estudiante.is_(True), 1), else_=0).desc(),
            User.fecha_registro.desc(),
            User.id.desc(),
        )
    )

    if ubicacion:
        query = query.filter(PerfilEstudiante.ubicacion.contains(ubicacion))
    if modalidad_preferida:
        query = query.filter(PerfilEstudiante.modalidad_preferida == modalidad_preferida)
    if institucion_educativa:
        query = query.filter(PerfilEstudiante.institucion_educativa.contains(institucion_educativa))
    if nivel_academico:
        query = query.filter(PerfilEstudiante.nivel_academico.contains(nivel_academico))
    if habilidad:
        query = query.filter(PerfilEstudiante.habilidades.contains(habilidad))

    return query.offset(skip).limit(limit).all()


def get_vacante_feed_for_student(
    db: Session,
    *,
    estudiante_id: int,
    skip: int = 0,
    limit: int = 100,
    modalidad: str | None = None,
    ubicacion: str | None = None,
    sueldo_min: float | None = None,
):
    query = (
        db.query(Vacante)
        .join(User, User.id == Vacante.empresa_id)
        .outerjoin(
            InteraccionSwipe,
            (InteraccionSwipe.estudiante_id == estudiante_id)
            & (InteraccionSwipe.vacante_id == Vacante.id),
        )
        .filter(InteraccionSwipe.id.is_(None))
        .filter(Vacante.estado == "activa")
        .order_by(User.es_premium.desc(), Vacante.fecha_publicacion.desc(), Vacante.id.desc())
    )

    if modalidad:
        query = query.filter(Vacante.modalidad == modalidad)
    if ubicacion:
        query = query.filter(Vacante.ubicacion.contains(ubicacion))
    if sueldo_min:
        query = query.filter(Vacante.sueldo_minimo >= sueldo_min)

    return query.offset(skip).limit(limit).all()
