from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.crud.crud_perfil_estudiante import get_estudiante, create_estudiante, update_estudiante, delete_estudiante
from app.db.session import get_db
from app.schemas.perfil_estudiante import PerfilEstudiante, PerfilEstudianteCreate
from app.services.profile_media import serialize_estudiante_profile

router = APIRouter()

@router.get("/{usuario_id}", response_model=PerfilEstudiante)
def read_estudiante(usuario_id: int, db: Session = Depends(get_db)):
    # Llamamos al CRUD con el nombre de variable correcto
    estudiante = get_estudiante(db, usuario_id)
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return serialize_estudiante_profile(estudiante)

@router.post("/{usuario_id}", response_model=PerfilEstudiante)
def create_new_estudiante(usuario_id: int, estudiante: PerfilEstudianteCreate, db: Session = Depends(get_db)):
    created = create_estudiante(db, estudiante, usuario_id)
    return serialize_estudiante_profile(created)

@router.put("/{usuario_id}", response_model=PerfilEstudiante)
def update_existing_estudiante(usuario_id: int, estudiante: PerfilEstudianteCreate, db: Session = Depends(get_db)):
    updated = update_estudiante(db, usuario_id, estudiante)
    if not updated:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return serialize_estudiante_profile(updated)

@router.delete("/{usuario_id}", response_model=PerfilEstudiante)
def delete_existing_estudiante(usuario_id: int, db: Session = Depends(get_db)):
    deleted = delete_estudiante(db, usuario_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return serialize_estudiante_profile(deleted)
