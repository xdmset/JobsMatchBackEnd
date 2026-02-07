from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.perfil_empresa import PerfilEmpresaCreate, PerfilEmpresa
from app.crud.crud_perfil_empresa import get_empresa, create_empresa, update_empresa, delete_empresa
from app.db.session import get_db

router = APIRouter()

@router.get("/{user_id}", response_model=PerfilEmpresa)
def read_empresa(user_id: int, db: Session = Depends(get_db)):
    empresa = get_empresa(db, user_id)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa not found")
    return empresa

@router.post("/{user_id}", response_model=PerfilEmpresa)
def create_new_empresa(user_id: int, empresa: PerfilEmpresaCreate, db: Session = Depends(get_db)):
    return create_empresa(db, empresa, user_id)

@router.put("/{user_id}", response_model=PerfilEmpresa)
def update_existing_empresa(user_id: int, empresa: PerfilEmpresaCreate, db: Session = Depends(get_db)):
    updated = update_empresa(db, user_id, empresa)
    if not updated:
        raise HTTPException(status_code=404, detail="Empresa not found")
    return updated

@router.delete("/{user_id}", response_model=PerfilEmpresa)
def delete_existing_empresa(user_id: int, db: Session = Depends(get_db)):
    deleted = delete_empresa(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Empresa not found")
    return deleted
