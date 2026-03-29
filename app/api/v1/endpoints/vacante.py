from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.dependencies import ensure_roles, ensure_same_user, get_current_user
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

router = APIRouter()

@router.get("/", response_model=List[Vacante])
def read_vacantes(
    skip: int = 0, 
    limit: int = 100, 
    modalidad: Optional[str] = Query(None, description="Filtrar por remoto, presencial o hibrido"),
    ubicacion: Optional[str] = Query(None, description="Filtrar por ciudad o estado"),
    sueldo_min: Optional[float] = Query(None, description="Sueldo mínimo deseado"),
    db: Session = Depends(get_db)
):
    """
    Obtiene el listado de vacantes con soporte para filtros (RF-09).
    """
    # Si no hay filtros, el CRUD get_vacantes funcionará como siempre,
    # pero ahora le pasamos los nuevos parámetros opcionales.
    return get_vacantes(db, skip=skip, limit=limit, modalidad=modalidad, ubicacion=ubicacion, sueldo_min=sueldo_min)


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
    return get_historial_vacantes_estudiante(db, estudiante_id=estudiante_id, skip=skip, limit=limit)


@router.get("/historial/empresa/{empresa_id}", response_model=List[VacanteHistorialEmpresa])
def read_historial_vacantes_empresa(
    empresa_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_same_user(current_user, empresa_id, NombreRol.empresa.value)
    return get_historial_vacantes_empresa(db, empresa_id=empresa_id, skip=skip, limit=limit)

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
