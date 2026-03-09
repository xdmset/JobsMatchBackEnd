from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.schemas.vacante import VacanteCreate, Vacante, VacanteUpdate
from app.crud.crud_vacante import (
    get_vacante, 
    get_vacantes, 
    create_vacante, 
    update_vacante, 
    delete_vacante
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

@router.get("/{vacante_id}", response_model=Vacante)
def read_vacante(vacante_id: int, db: Session = Depends(get_db)):
    vacante = get_vacante(db, vacante_id)
    if not vacante:
        raise HTTPException(status_code=404, detail="Vacante no encontrada")
    return vacante

@router.post("/{empresa_id}", response_model=Vacante)
def create_new_vacante(empresa_id: int, vacante: VacanteCreate, db: Session = Depends(get_db)):
    # Importante: empresa_id es el usuario_id de la empresa que publica
    return create_vacante(db, vacante, empresa_id)

@router.put("/{vacante_id}", response_model=Vacante)
def update_existing_vacante(vacante_id: int, vacante: VacanteUpdate, db: Session = Depends(get_db)):
    updated = update_vacante(db, vacante_id, vacante)
    if not updated:
        raise HTTPException(status_code=404, detail="Vacante no encontrada")
    return updated

@router.delete("/{vacante_id}", response_model=Vacante)
def delete_existing_vacante(vacante_id: int, db: Session = Depends(get_db)):
    deleted = delete_vacante(db, vacante_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Vacante no encontrada")
    return deleted
