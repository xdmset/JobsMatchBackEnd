from sqlalchemy.orm import Session
from app.models.vacante import Vacante
from app.schemas.vacante import VacanteCreate

def get_vacante(db: Session, vacante_id: int):
    return db.query(Vacante).filter(Vacante.id == vacante_id).first()

def get_vacantes(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    modalidad: str = None, 
    ubicacion: str = None, 
    sueldo_min: float = None
):
    """RF-09: Obtener vacantes con filtros dinámicos."""
    query = db.query(Vacante)
    
    if modalidad:
        query = query.filter(Vacante.modalidad == modalidad)
    if ubicacion:
        query = query.filter(Vacante.ubicacion.contains(ubicacion))
    if sueldo_min:
        query = query.filter(Vacante.sueldo_minimo >= sueldo_min)
    
    return query.offset(skip).limit(limit).all()

def create_vacante(db: Session, vacante: VacanteCreate, empresa_id: int):
    # Se usa model_dump() para Pydantic v2
    db_vacante = Vacante(**vacante.model_dump(), empresa_id=empresa_id)
    db.add(db_vacante)
    db.commit()
    db.refresh(db_vacante)
    return db_vacante

def update_vacante(db: Session, vacante_id: int, vacante_data: VacanteCreate):
    db_vacante = get_vacante(db, vacante_id)
    if db_vacante:
        for field, value in vacante_data.model_dump(exclude_unset=True).items():
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