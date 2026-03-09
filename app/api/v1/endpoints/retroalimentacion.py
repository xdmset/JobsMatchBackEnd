from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import ensure_roles, get_current_user
from app.core.enums import NombreRol
from app.crud import crud_retroalimentacion, crud_postulacion
from app.db.session import get_db
from app.models.user import User
from app.schemas.retroalimentacion import (
    RetroalimentacionCreate,
    RetroalimentacionRead,
    RetroalimentacionUpdate,
)

router = APIRouter()


def _authorize_postulacion_access(current_user: User, empresa_id: int, estudiante_id: int) -> None:
    if current_user.is_superuser:
        return
    if current_user.id in {empresa_id, estudiante_id}:
        return
    ensure_roles(current_user, NombreRol.admin.value)


@router.get("/{retroalimentacion_id}", response_model=RetroalimentacionRead)
def read_retroalimentacion(
    retroalimentacion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    retroalimentacion = crud_retroalimentacion.get_retroalimentacion(db, retroalimentacion_id)
    if not retroalimentacion:
        raise HTTPException(status_code=404, detail="Retroalimentacion no encontrada")
    postulacion = crud_postulacion.get_postulacion(db, retroalimentacion.postulacion_id)
    if not postulacion:
        raise HTTPException(status_code=404, detail="Postulacion no encontrada")
    _authorize_postulacion_access(current_user, postulacion.empresa_id, postulacion.estudiante_id)
    return retroalimentacion


@router.get("/postulacion/{postulacion_id}", response_model=RetroalimentacionRead)
def read_retroalimentacion_by_postulacion(
    postulacion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    postulacion = crud_postulacion.get_postulacion(db, postulacion_id)
    if not postulacion:
        raise HTTPException(status_code=404, detail="Postulacion no encontrada")
    _authorize_postulacion_access(current_user, postulacion.empresa_id, postulacion.estudiante_id)
    retroalimentacion = crud_retroalimentacion.get_retroalimentacion_by_postulacion(
        db, postulacion_id
    )
    if not retroalimentacion:
        raise HTTPException(status_code=404, detail="Retroalimentacion no encontrada")
    return retroalimentacion


@router.post("/", response_model=RetroalimentacionRead)
def create_new_retroalimentacion(
    retroalimentacion: RetroalimentacionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    postulacion = crud_postulacion.get_postulacion(db, retroalimentacion.postulacion_id)
    if not postulacion:
        raise HTTPException(status_code=404, detail="Postulacion no encontrada")
    if current_user.id != postulacion.empresa_id:
        ensure_roles(current_user, NombreRol.admin.value)

    existing = crud_retroalimentacion.get_retroalimentacion_by_postulacion(
        db, retroalimentacion.postulacion_id
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Ya existe retroalimentacion para esta postulacion",
        )

    return crud_retroalimentacion.create_retroalimentacion(db, retroalimentacion)


@router.put("/{retroalimentacion_id}", response_model=RetroalimentacionRead)
def update_existing_retroalimentacion(
    retroalimentacion_id: int,
    retroalimentacion: RetroalimentacionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = crud_retroalimentacion.get_retroalimentacion(db, retroalimentacion_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Retroalimentacion no encontrada")
    postulacion = crud_postulacion.get_postulacion(db, existing.postulacion_id)
    if not postulacion:
        raise HTTPException(status_code=404, detail="Postulacion no encontrada")
    if current_user.id != postulacion.empresa_id:
        ensure_roles(current_user, NombreRol.admin.value)
    return crud_retroalimentacion.update_retroalimentacion(db, existing, retroalimentacion)


@router.delete("/{retroalimentacion_id}", response_model=RetroalimentacionRead)
def delete_existing_retroalimentacion(
    retroalimentacion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = crud_retroalimentacion.get_retroalimentacion(db, retroalimentacion_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Retroalimentacion no encontrada")
    postulacion = crud_postulacion.get_postulacion(db, existing.postulacion_id)
    if not postulacion:
        raise HTTPException(status_code=404, detail="Postulacion no encontrada")
    if current_user.id != postulacion.empresa_id:
        ensure_roles(current_user, NombreRol.admin.value)
    return crud_retroalimentacion.delete_retroalimentacion(db, existing)
