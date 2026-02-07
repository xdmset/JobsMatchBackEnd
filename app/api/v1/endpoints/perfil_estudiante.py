from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.perfil_estudiante import PerfilEstudianteCreate, PerfilEstudiante
from app.crud.crud_perfil_estudiante import get_estudiante, create_estudiante, update_estudiante, delete_estudiante
from app.db.session import get_db

router = APIRouter()

@router.get("/{user_id}", response_model=PerfilEstudiante)
def read_estudiante(user_id: int, db: Session = Depends(get_db)):
    estudiante = get_estudiante(db, user_id)
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante not found")
    return estudiante

@router.post("/{user_id}", response_model=PerfilEstudiante)
def create_new_estudiante(user_id: int, estudiante: PerfilEstudianteCreate, db: Session = Depends(get_db)):
    return create_estudiante(db, estudiante, user_id)

@router.put("/{user_id}", response_model=PerfilEstudiante)
def update_existing_estudiante(user_id: int, estudiante: PerfilEstudianteCreate, db: Session = Depends(get_db)):
    updated = update_estudiante(db, user_id, estudiante)
    if not updated:
        raise HTTPException(status_code=404, detail="Estudiante not found")
    return updated

@router.delete("/{user_id}", response_model=PerfilEstudiante)
def delete_existing_estudiante(user_id: int, db: Session = Depends(get_db)):
    deleted = delete_estudiante(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Estudiante not found")
    return deleted
