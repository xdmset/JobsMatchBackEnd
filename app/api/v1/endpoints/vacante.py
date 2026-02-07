from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.vacante import VacanteCreate, Vacante
from app.crud.crud_vacante import get_vacante, get_vacantes, create_vacante, update_vacante, delete_vacante
from app.db.session import get_db

router = APIRouter()

@router.get("/", response_model=list[Vacante])
def read_vacantes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_vacantes(db, skip=skip, limit=limit)

@router.get("/{vacante_id}", response_model=Vacante)
def read_vacante(vacante_id: int, db: Session = Depends(get_db)):
    vacante = get_vacante(db, vacante_id)
    if not vacante:
        raise HTTPException(status_code=404, detail="Vacante not found")
    return vacante

@router.post("/{empresa_id}", response_model=Vacante)
def create_new_vacante(empresa_id: int, vacante: VacanteCreate, db: Session = Depends(get_db)):
    return create_vacante(db, vacante, empresa_id)

@router.put("/{vacante_id}", response_model=Vacante)
def update_existing_vacante(vacante_id: int, vacante: VacanteCreate, db: Session = Depends(get_db)):
    updated = update_vacante(db, vacante_id, vacante)
    if not updated:
        raise HTTPException(status_code=404, detail="Vacante not found")
    return updated

@router.delete("/{vacante_id}", response_model=Vacante)
def delete_existing_vacante(vacante_id: int, db: Session = Depends(get_db)):
    deleted = delete_vacante(db, vacante_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Vacante not found")
    return deleted
