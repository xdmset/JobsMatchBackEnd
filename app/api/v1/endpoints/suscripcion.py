from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import ensure_roles, ensure_same_user, get_current_user
from app.core.enums import NombreRol
from app.crud.crud_suscripcion import (
    create_suscripcion,
    delete_suscripcion,
    get_suscripcion,
    get_suscripciones,
    get_suscripciones_by_usuario,
    get_user,
    update_suscripcion,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.suscripcion import Suscripcion, SuscripcionCreate, SuscripcionUpdate

router = APIRouter()


@router.get("/", response_model=List[Suscripcion])
def read_suscripciones(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_roles(current_user, NombreRol.admin.value)
    return get_suscripciones(db, skip=skip, limit=limit)


@router.get("/usuario/{usuario_id}", response_model=List[Suscripcion])
def read_suscripciones_by_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_same_user(current_user, usuario_id)
    if not get_user(db, usuario_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return get_suscripciones_by_usuario(db, usuario_id)


@router.get("/{suscripcion_id}", response_model=Suscripcion)
def read_suscripcion(
    suscripcion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_roles(current_user, NombreRol.admin.value)
    suscripcion = get_suscripcion(db, suscripcion_id)
    if not suscripcion:
        raise HTTPException(status_code=404, detail="Suscripcion no encontrada")
    return suscripcion


@router.post("/", response_model=Suscripcion)
def create_new_suscripcion(
    suscripcion: SuscripcionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_roles(current_user, NombreRol.admin.value)
    if not get_user(db, suscripcion.usuario_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return create_suscripcion(db, suscripcion)


@router.put("/{suscripcion_id}", response_model=Suscripcion)
def update_existing_suscripcion(
    suscripcion_id: int,
    suscripcion: SuscripcionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_roles(current_user, NombreRol.admin.value)
    if suscripcion.usuario_id is not None and not get_user(db, suscripcion.usuario_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    updated = update_suscripcion(db, suscripcion_id, suscripcion)
    if not updated:
        raise HTTPException(status_code=404, detail="Suscripcion no encontrada")
    return updated


@router.delete("/{suscripcion_id}", response_model=Suscripcion)
def delete_existing_suscripcion(
    suscripcion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_roles(current_user, NombreRol.admin.value)
    deleted = delete_suscripcion(db, suscripcion_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Suscripcion no encontrada")
    return deleted
