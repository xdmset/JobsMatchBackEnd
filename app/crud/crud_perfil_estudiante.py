from sqlalchemy.orm import Session
from app.models.perfil_estudiante import PerfilEstudiante
from app.schemas.perfil_estudiante import PerfilEstudianteCreate

def get_estudiante(db: Session, user_id: int):
    return db.query(PerfilEstudiante).filter(PerfilEstudiante.user_id == user_id).first()

def create_estudiante(db: Session, estudiante: PerfilEstudianteCreate, user_id: int):
    db_estudiante = PerfilEstudiante(user_id=user_id, **estudiante.dict())
    db.add(db_estudiante)
    db.commit()
    db.refresh(db_estudiante)
    return db_estudiante

def update_estudiante(db: Session, user_id: int, estudiante_data: PerfilEstudianteCreate):
    db_estudiante = get_estudiante(db, user_id)
    if db_estudiante:
        for field, value in estudiante_data.dict(exclude_unset=True).items():
            setattr(db_estudiante, field, value)
        db.commit()
        db.refresh(db_estudiante)
    return db_estudiante

def delete_estudiante(db: Session, user_id: int):
    db_estudiante = get_estudiante(db, user_id)
    if db_estudiante:
        db.delete(db_estudiante)
        db.commit()
    return db_estudiante
