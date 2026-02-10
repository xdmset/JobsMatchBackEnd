from sqlalchemy.orm import Session
from app.models.perfil_estudiante import PerfilEstudiante
from app.schemas.perfil_estudiante import PerfilEstudianteCreate

def get_estudiante(db: Session, usuario_id: int):
    # Cambiado de user_id a usuario_id para coincidir con el modelo y SQL
    return db.query(PerfilEstudiante).filter(PerfilEstudiante.usuario_id == usuario_id).first()

def create_estudiante(db: Session, estudiante: PerfilEstudianteCreate, usuario_id: int):
    # Sincronizado con usuario_id
    db_estudiante = PerfilEstudiante(usuario_id=usuario_id, **estudiante.model_dump())
    db.add(db_estudiante)
    db.commit()
    db.refresh(db_estudiante)
    return db_estudiante

def update_estudiante(db: Session, usuario_id: int, estudiante_data: PerfilEstudianteCreate):
    db_estudiante = get_estudiante(db, usuario_id)
    if db_estudiante:
        # model_dump() es la forma correcta en Pydantic v2
        for field, value in estudiante_data.model_dump(exclude_unset=True).items():
            setattr(db_estudiante, field, value)
        db.commit()
        db.refresh(db_estudiante)
    return db_estudiante

def delete_estudiante(db: Session, usuario_id: int):
    db_estudiante = get_estudiante(db, usuario_id)
    if db_estudiante:
        db.delete(db_estudiante)
        db.commit()
    return db_estudiante