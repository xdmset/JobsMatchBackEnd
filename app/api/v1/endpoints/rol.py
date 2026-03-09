from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.enums import NombreRol
from app.schemas.role import Role
from app.crud.crud_rol import get_roles, get_rol, create_rol, update_rol, delete_rol
from app.db.session import get_db

router = APIRouter()

@router.get("/", response_model=list[Role])
def read_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_roles(db, skip=skip, limit=limit)

@router.get("/{rol_id}", response_model=Role)
def read_rol(rol_id: int, db: Session = Depends(get_db)):
    db_rol = get_rol(db, rol_id)
    if not db_rol:
        raise HTTPException(status_code=404, detail="Rol not found")
    return db_rol

@router.post("/", response_model=Role)
def create_new_rol(nombre: NombreRol, db: Session = Depends(get_db)):
    return create_rol(db, nombre)

@router.put("/{rol_id}", response_model=Role)
def update_existing_rol(rol_id: int, nombre: NombreRol, db: Session = Depends(get_db)):
    updated = update_rol(db, rol_id, nombre)
    if not updated:
        raise HTTPException(status_code=404, detail="Rol not found")
    return updated

@router.delete("/{rol_id}", response_model=Role)
def delete_existing_rol(rol_id: int, db: Session = Depends(get_db)):
    deleted = delete_rol(db, rol_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Rol not found")
    return deleted
