from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.dependencies import (
    ensure_roles,
    ensure_same_user,
    get_current_user,
    get_current_user_optional,
    get_user_role,
)
from app.core.enums import NombreRol
from app.models.user import User
from app.schemas.vacante import (
    VacanteCreate,
    Vacante,
    VacanteHistorialEmpresa,
    VacanteHistorialEstudiante,
    VacanteUpdate,
)
from app.crud.crud_vacante import (
    count_active_vacantes_by_empresa,
    create_vacante,
    delete_vacante,
    get_historial_vacantes_empresa,
    get_historial_vacantes_estudiante,
    get_vacante,
    get_vacantes,
    registrar_visualizacion_vacante,
    update_vacante,
)
from app.db.session import get_db
from app.services.subscription_service import build_plan_context

router = APIRouter()


def _bounded_limit(skip: int, requested_limit: int, max_items: int | None) -> int:
    if max_items is None:
        return requested_limit
    remaining = max(max_items - skip, 0)
    return min(requested_limit, remaining)


def _ensure_valid_salary_range(sueldo_minimo: float | None, sueldo_maximo: float | None) -> None:
    if (
        sueldo_minimo is not None
        and sueldo_maximo is not None
        and sueldo_minimo > sueldo_maximo
    ):
        raise HTTPException(
            status_code=422,
            detail="sueldo_minimo no puede ser mayor que sueldo_maximo",
        )

@router.get("/", response_model=List[Vacante])
def read_vacantes(
    skip: int = 0,
    limit: int = 100,
    modalidad: Optional[str] = Query(None, description="Filtrar por remoto, presencial o hibrido"),
    ubicacion: Optional[str] = Query(None, description="Filtrar por ciudad o estado"),
    sueldo_min: Optional[float] = Query(None, description="Sueldo mínimo deseado"),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """
    Obtiene el listado de vacantes activas con soporte para filtros (RF-09).

    Si el usuario autenticado es un estudiante, se excluyen las vacantes
    donde ya hizo swipe (like o dislike).
    """
    estudiante_id = None
    if current_user and get_user_role(current_user) == NombreRol.estudiante.value:
        estudiante_id = current_user.id

    return get_vacantes(
        db,
        skip=skip,
        limit=limit,
        modalidad=modalidad,
        ubicacion=ubicacion,
        sueldo_min=sueldo_min,
        estudiante_id=estudiante_id,
    )


@router.post("/{vacante_id}/view")
def register_vacante_view(
    vacante_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_roles(current_user, NombreRol.estudiante.value)
    vacante = get_vacante(db, vacante_id)
    if not vacante:
        raise HTTPException(status_code=404, detail="Vacante no encontrada")

    visualizacion = registrar_visualizacion_vacante(db, current_user.id, vacante_id)
    return {
        "vacante_id": vacante_id,
        "estudiante_id": current_user.id,
        "primera_visualizacion": visualizacion.primera_visualizacion,
        "ultima_visualizacion": visualizacion.ultima_visualizacion,
        "total_visualizaciones": visualizacion.total_visualizaciones,
    }


@router.get("/historial/estudiante/{estudiante_id}", response_model=List[VacanteHistorialEstudiante])
def read_historial_vacantes_estudiante(
    estudiante_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_same_user(current_user, estudiante_id, NombreRol.estudiante.value)
    plan_context = build_plan_context(current_user)
    effective_limit = _bounded_limit(skip, limit, plan_context.view_history_limit)
    return get_historial_vacantes_estudiante(db, estudiante_id=estudiante_id, skip=skip, limit=effective_limit)


@router.get("/historial/empresa/{empresa_id}", response_model=List[VacanteHistorialEmpresa])
def read_historial_vacantes_empresa(
    empresa_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_same_user(current_user, empresa_id, NombreRol.empresa.value)
    historial = get_historial_vacantes_empresa(db, empresa_id=empresa_id, skip=skip, limit=limit)
    plan_context = build_plan_context(current_user)
    if plan_context.analytics_level == "basic":
        for item in historial:
            item.ultima_visualizacion = None
            item.ultimo_like_estudiante = None
            item.ultimo_like_empresa = None
    return historial

@router.get("/{vacante_id}", response_model=Vacante)
def read_vacante(vacante_id: int, db: Session = Depends(get_db)):
    vacante = get_vacante(db, vacante_id)
    if not vacante:
        raise HTTPException(status_code=404, detail="Vacante no encontrada")
    return vacante

@router.post("/{empresa_id}", response_model=Vacante)
def create_new_vacante(
    empresa_id: int,
    vacante: VacanteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_same_user(current_user, empresa_id, NombreRol.empresa.value)
    _ensure_valid_salary_range(vacante.sueldo_minimo, vacante.sueldo_maximo)
    plan_context = build_plan_context(current_user)
    requested_state = vacante.estado or "activa"
    if requested_state == "activa" and plan_context.active_vacancies_limit is not None:
        active_count = count_active_vacantes_by_empresa(db, empresa_id)
        if active_count >= plan_context.active_vacancies_limit:
            raise HTTPException(
                status_code=403,
                detail="Límite de vacantes activas alcanzado para tu plan actual",
            )
    return create_vacante(db, vacante, empresa_id)

@router.put("/{vacante_id}", response_model=Vacante)
def update_existing_vacante(
    vacante_id: int,
    vacante: VacanteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = get_vacante(db, vacante_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Vacante no encontrada")
    if current_user.id != existing.empresa_id:
        ensure_roles(current_user, NombreRol.admin.value)

    incoming = vacante.model_dump(exclude_unset=True)
    _ensure_valid_salary_range(
        incoming.get("sueldo_minimo", existing.sueldo_minimo),
        incoming.get("sueldo_maximo", existing.sueldo_maximo),
    )

    target_state = vacante.estado or existing.estado
    if existing.estado != "activa" and target_state == "activa":
        owner_user = current_user if current_user.id == existing.empresa_id else existing.empresa.user
        plan_context = build_plan_context(owner_user)
        if plan_context.active_vacancies_limit is not None:
            active_count = count_active_vacantes_by_empresa(db, existing.empresa_id)
            if active_count >= plan_context.active_vacancies_limit:
                raise HTTPException(
                    status_code=403,
                    detail="Límite de vacantes activas alcanzado para tu plan actual",
                )

    updated = update_vacante(db, vacante_id, vacante)
    return updated

@router.delete("/{vacante_id}", response_model=Vacante)
def delete_existing_vacante(
    vacante_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = get_vacante(db, vacante_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Vacante no encontrada")
    if current_user.id != existing.empresa_id:
        ensure_roles(current_user, NombreRol.admin.value)

    deleted = delete_vacante(db, vacante_id)
    return deleted
