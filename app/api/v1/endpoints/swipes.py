from datetime import date
from enum import Enum
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
from app.models.perfil_estudiante import PerfilEstudiante
from app.models.user import User
from app.models.vacante import Vacante as VacanteModel
from app.schemas.discovery import CandidateFeedItem
from app.schemas.interaccion_swipe import (
    CandidatoEstadoItem,
    SwipeCreate,
    SwipeEmpresaCreate,
    VacanteMatchEstudiante,
    VacanteRechazadaPorEmpresa,
    VacanteSwipeEstudiante,
)
from app.schemas.match import MatchResponse
from app.schemas.vacante import Vacante
from app.services import notification_service
from app.services.profile_media import serialize_estudiante_profile
from app.services.subscription_service import build_plan_context


class EstadoCandidato(str, Enum):
    matches = "matches"
    rechazados = "rechazados"
    pendientes = "pendientes"

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
        # Obtener perfil del estudiante para notificaciones
        perfil_estudiante = db.query(PerfilEstudiante).filter(
            PerfilEstudiante.usuario_id == estudiante_id
        ).first()
        estudiante_nombre = perfil_estudiante.nombre_completo if perfil_estudiante else "Un estudiante"

        # Notificar a la empresa del like recibido
        notification_service.notificar_like_recibido(
            db=db,
            empresa_id=vacante.empresa_id,
            estudiante_nombre=estudiante_nombre,
            vacante_titulo=vacante.titulo,
            vacante_id=vacante.id,
            estudiante_id=estudiante_id,
        )

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

            postulacion = crud_postulacion.crear_postulacion_si_aplica(
                db,
                estudiante_id=estudiante_id,
                vacante=vacante,
                match_id=match_confirmado.id,
                source="app_swipe",
            )

            # Notificar match a ambos
            notification_service.notificar_match(
                db=db,
                usuario_id=estudiante_id,
                contraparte_nombre=vacante.titulo,
                vacante_titulo=vacante.titulo,
                vacante_id=vacante.id,
                es_estudiante=True,
                postulacion_id=postulacion.id if postulacion else None,
            )
            notification_service.notificar_match(
                db=db,
                usuario_id=vacante.empresa_id,
                contraparte_nombre=estudiante_nombre,
                vacante_titulo=vacante.titulo,
                vacante_id=vacante.id,
                es_estudiante=False,
                postulacion_id=postulacion.id if postulacion else None,
                estudiante_id=estudiante_id,
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

            postulacion = crud_postulacion.crear_postulacion_si_aplica(
                db,
                estudiante_id=swipe.estudiante_id,
                vacante=vacante,
                match_id=match_confirmado.id,
                source="app_swipe",
            )

            # Obtener nombre del estudiante para notificación
            perfil_estudiante = db.query(PerfilEstudiante).filter(
                PerfilEstudiante.usuario_id == swipe.estudiante_id
            ).first()
            estudiante_nombre = perfil_estudiante.nombre_completo if perfil_estudiante else "Un estudiante"

            # Notificar match a ambos
            notification_service.notificar_match(
                db=db,
                usuario_id=swipe.estudiante_id,
                contraparte_nombre=vacante.titulo,
                vacante_titulo=vacante.titulo,
                vacante_id=vacante.id,
                es_estudiante=True,
                postulacion_id=postulacion.id if postulacion else None,
            )
            notification_service.notificar_match(
                db=db,
                usuario_id=empresa_id,
                contraparte_nombre=estudiante_nombre,
                vacante_titulo=vacante.titulo,
                vacante_id=vacante.id,
                es_estudiante=False,
                postulacion_id=postulacion.id if postulacion else None,
                estudiante_id=swipe.estudiante_id,
            )

    db.commit()
    if match_confirmado:
        db.refresh(match_confirmado)
    return match_confirmado


# --- Funciones auxiliares ---


def _vacante_to_dict(vacante: VacanteModel) -> dict:
    """Convierte modelo Vacante a dict para schema."""
    return {
        "id": vacante.id,
        "empresa_id": vacante.empresa_id,
        "titulo": vacante.titulo,
        "descripcion": vacante.descripcion,
        "requisitos": vacante.requisitos,
        "tipo_contrato": vacante.tipo_contrato,
        "modalidad": vacante.modalidad,
        "ubicacion": vacante.ubicacion,
        "sueldo_minimo": float(vacante.sueldo_minimo) if vacante.sueldo_minimo else None,
        "sueldo_maximo": float(vacante.sueldo_maximo) if vacante.sueldo_maximo else None,
        "moneda": vacante.moneda,
        "estado": vacante.estado,
        "fecha_publicacion": vacante.fecha_publicacion,
    }


def _bounded_limit(skip: int, requested_limit: int, max_items: int | None) -> int:
    """Calcula limite acotado para restricciones freemium."""
    if max_items is None:
        return requested_limit
    remaining = max(max_items - skip, 0)
    return min(requested_limit, remaining)


# --- Endpoints de historial de swipes para estudiantes ---


@router.get("/{estudiante_id}/likes", response_model=list[VacanteSwipeEstudiante])
def get_student_likes_endpoint(
    estudiante_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene las vacantes donde el estudiante dio like."""
    ensure_same_user(current_user, estudiante_id, NombreRol.estudiante.value)

    rows = crud_swipe.get_student_likes(
        db, estudiante_id=estudiante_id, skip=skip, limit=limit
    )

    return [
        VacanteSwipeEstudiante(
            **_vacante_to_dict(vacante),
            fecha_swipe=swipe.fecha_actualizacion,
            interes_estudiante=swipe.interes_estudiante,
        )
        for swipe, vacante in rows
    ]


@router.get("/{estudiante_id}/rechazadas", response_model=list[VacanteSwipeEstudiante])
def get_student_dislikes_endpoint(
    estudiante_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene las vacantes que el estudiante rechazo (dio dislike)."""
    ensure_same_user(current_user, estudiante_id, NombreRol.estudiante.value)

    rows = crud_swipe.get_student_dislikes(
        db, estudiante_id=estudiante_id, skip=skip, limit=limit
    )

    return [
        VacanteSwipeEstudiante(
            **_vacante_to_dict(vacante),
            fecha_swipe=swipe.fecha_actualizacion,
            interes_estudiante=swipe.interes_estudiante,
        )
        for swipe, vacante in rows
    ]


@router.get("/{estudiante_id}/pendientes", response_model=list[VacanteSwipeEstudiante])
def get_student_pending_endpoint(
    estudiante_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene vacantes donde el estudiante dio like pero la empresa no ha respondido."""
    ensure_same_user(current_user, estudiante_id, NombreRol.estudiante.value)

    rows = crud_swipe.get_student_pending(
        db, estudiante_id=estudiante_id, skip=skip, limit=limit
    )

    return [
        VacanteSwipeEstudiante(
            **_vacante_to_dict(vacante),
            fecha_swipe=swipe.fecha_actualizacion,
            interes_estudiante=swipe.interes_estudiante,
        )
        for swipe, vacante in rows
    ]


@router.get(
    "/{estudiante_id}/rechazado-por-empresa",
    response_model=list[VacanteRechazadaPorEmpresa],
)
def get_student_rejected_by_company_endpoint(
    estudiante_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene vacantes donde la empresa rechazo al estudiante."""
    ensure_same_user(current_user, estudiante_id, NombreRol.estudiante.value)

    rows = crud_swipe.get_student_rejected_by_company(
        db, estudiante_id=estudiante_id, skip=skip, limit=limit
    )

    return [
        VacanteRechazadaPorEmpresa(
            **_vacante_to_dict(vacante),
            fecha_swipe=swipe_empresa.fecha,
            interes_estudiante=False,
            fecha_rechazo_empresa=swipe_empresa.fecha_actualizacion,
        )
        for swipe_empresa, vacante in rows
    ]


@router.get("/{estudiante_id}/aceptadas", response_model=list[VacanteMatchEstudiante])
def get_student_accepted_endpoint(
    estudiante_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene vacantes donde hay match (ambos dieron like)."""
    ensure_same_user(current_user, estudiante_id, NombreRol.estudiante.value)

    plan_context = build_plan_context(current_user)
    effective_limit = _bounded_limit(skip, limit, plan_context.match_history_limit)

    rows = crud_swipe.get_student_accepted(
        db, estudiante_id=estudiante_id, skip=skip, limit=effective_limit
    )

    return [
        VacanteMatchEstudiante(
            **_vacante_to_dict(vacante),
            fecha_swipe=swipe.fecha_actualizacion if swipe else match.fecha_match,
            interes_estudiante=True,
            fecha_match=match.fecha_match,
        )
        for match, vacante, swipe in rows
    ]


# --- Endpoints de candidatos filtrados por estado para empresas ---


@router.get(
    "/empresa/{empresa_id}/candidatos/estado/{estado}",
    response_model=list[CandidatoEstadoItem],
)
def get_candidatos_by_estado_all_vacantes(
    empresa_id: int,
    estado: EstadoCandidato,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Ver candidatos filtrados por estado para TODAS las vacantes de la empresa.

    Estados disponibles:
    - matches: estudiante dio like + empresa dio like
    - rechazados: empresa dio dislike al estudiante
    - pendientes: estudiante dio like, empresa no ha respondido
    """
    ensure_same_user(current_user, empresa_id, NombreRol.empresa.value)

    return _get_candidatos_by_estado(
        db=db,
        empresa_id=empresa_id,
        estado=estado,
        vacante_id=None,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/empresa/{empresa_id}/vacante/{vacante_id}/candidatos/estado/{estado}",
    response_model=list[CandidatoEstadoItem],
)
def get_candidatos_by_estado_vacante(
    empresa_id: int,
    vacante_id: int,
    estado: EstadoCandidato,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Ver candidatos filtrados por estado para UNA vacante especifica.

    Estados disponibles:
    - matches: estudiante dio like + empresa dio like
    - rechazados: empresa dio dislike al estudiante
    - pendientes: estudiante dio like, empresa no ha respondido
    """
    ensure_same_user(current_user, empresa_id, NombreRol.empresa.value)

    vacante = crud_swipe.get_vacante(db, vacante_id)
    if not vacante:
        raise HTTPException(status_code=404, detail="Vacante no encontrada")
    if vacante.empresa_id != empresa_id:
        raise HTTPException(
            status_code=403, detail="La vacante no pertenece a la empresa"
        )

    return _get_candidatos_by_estado(
        db=db,
        empresa_id=empresa_id,
        estado=estado,
        vacante_id=vacante_id,
        skip=skip,
        limit=limit,
    )


def _get_candidatos_by_estado(
    db: Session,
    empresa_id: int,
    estado: EstadoCandidato,
    vacante_id: int | None,
    skip: int,
    limit: int,
) -> list[CandidatoEstadoItem]:
    """Funcion auxiliar para obtener candidatos por estado."""
    if estado == EstadoCandidato.matches:
        rows = crud_swipe.get_candidatos_matches(
            db, empresa_id=empresa_id, vacante_id=vacante_id, skip=skip, limit=limit
        )
        return [
            CandidatoEstadoItem(
                estudiante_id=user.id,
                email=user.email,
                es_premium=bool(user.es_premium),
                fecha_registro=user.fecha_registro,
                vacante_id=vacante.id,
                vacante_titulo=vacante.titulo,
                estado_candidato="match",
                fecha_interaccion=match.fecha_match,
                perfil_estudiante=serialize_estudiante_profile(perfil),
            )
            for match, perfil, user, vacante in rows
        ]

    elif estado == EstadoCandidato.rechazados:
        rows = crud_swipe.get_candidatos_rechazados(
            db, empresa_id=empresa_id, vacante_id=vacante_id, skip=skip, limit=limit
        )
        return [
            CandidatoEstadoItem(
                estudiante_id=user.id,
                email=user.email,
                es_premium=bool(user.es_premium),
                fecha_registro=user.fecha_registro,
                vacante_id=vacante.id,
                vacante_titulo=vacante.titulo,
                estado_candidato="rechazado",
                fecha_interaccion=swipe_emp.fecha_actualizacion,
                perfil_estudiante=serialize_estudiante_profile(perfil),
            )
            for swipe_emp, perfil, user, vacante in rows
        ]

    else:  # pendientes
        rows = crud_swipe.get_candidatos_pendientes(
            db, empresa_id=empresa_id, vacante_id=vacante_id, skip=skip, limit=limit
        )
        return [
            CandidatoEstadoItem(
                estudiante_id=user.id,
                email=user.email,
                es_premium=bool(user.es_premium),
                fecha_registro=user.fecha_registro,
                vacante_id=vacante.id,
                vacante_titulo=vacante.titulo,
                estado_candidato="pendiente",
                fecha_interaccion=swipe.fecha_actualizacion,
                perfil_estudiante=serialize_estudiante_profile(perfil),
            )
            for swipe, perfil, user, vacante in rows
        ]
