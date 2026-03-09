from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import ensure_same_user, get_current_user
from app.core.enums import NombreRol
from app.crud.crud_perfil_empresa import get_empresa, create_empresa, update_empresa, delete_empresa
from app.db.session import get_db
from app.models.user import User
from app.schemas.perfil_empresa import PerfilEmpresa, PerfilEmpresaCreate
from app.services.profile_media import serialize_empresa_profile

router = APIRouter()

@router.get("/{user_id}", response_model=PerfilEmpresa)
def read_empresa(user_id: int, db: Session = Depends(get_db)):
    empresa = get_empresa(db, user_id)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa not found")
    return serialize_empresa_profile(empresa)

@router.post("/{user_id}", response_model=PerfilEmpresa)
def create_new_empresa(
    user_id: int,
    empresa: PerfilEmpresaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_same_user(current_user, user_id, NombreRol.empresa.value)
    created = create_empresa(db, empresa, user_id)
    return serialize_empresa_profile(created)

@router.put("/{user_id}", response_model=PerfilEmpresa)
def update_existing_empresa(
    user_id: int,
    empresa: PerfilEmpresaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_same_user(current_user, user_id, NombreRol.empresa.value)
    updated = update_empresa(db, user_id, empresa)
    if not updated:
        raise HTTPException(status_code=404, detail="Empresa not found")
    return serialize_empresa_profile(updated)

@router.delete("/{user_id}", response_model=PerfilEmpresa)
def delete_existing_empresa(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_same_user(current_user, user_id, NombreRol.empresa.value)
    deleted = delete_empresa(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Empresa not found")
    return serialize_empresa_profile(deleted)
