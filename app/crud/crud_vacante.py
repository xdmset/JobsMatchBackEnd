from sqlalchemy.orm import Session
from app.models.vacante import Vacante
from app.schemas.vacante import VacanteCreate

def get_vacante(db: Session, vacante_id: int):
    return db.query(Vacante).filter(Vacante.id == vacante_id).first()

def get_vacantes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Vacante).offset(skip).limit(limit).all()

def create_vacante(db: Session, vacante: VacanteCreate, empresa_id: int):
    db_vacante = Vacante(empresa_id=empresa_id, **vacante.dict())
    db.add(db_vacante)
    db.commit()
    db.refresh(db_vacante)
    return db_vacante

def update_vacante(db: Session, vacante_id: int, vacante_data: VacanteCreate):
    db_vacante = get_vacante(db, vacante_id)
    if db_vacante:
        for field, value in vacante_data.dict(exclude_unset=True).items():
            setattr(db_vacante, field, value)
        db.commit()
        db.refresh(db_vacante)
    return db_vacante

def delete_vacante(db: Session, vacante_id: int):
    db_vacante = get_vacante(db, vacante_id)
    if db_vacante:
        db.delete(db_vacante)
        db.commit()
    return db_vacante
