from typing import Optional

from sqlalchemy.orm import Session

from app.models.retroalimentacion import Retroalimentacion
from app.schemas.retroalimentacion import RetroalimentacionCreate, RetroalimentacionUpdate


def get_retroalimentacion(db: Session, retroalimentacion_id: int) -> Optional[Retroalimentacion]:
    return (
        db.query(Retroalimentacion)
        .filter(Retroalimentacion.id == retroalimentacion_id)
        .first()
    )


def get_retroalimentacion_by_postulacion(
    db: Session, postulacion_id: int
) -> Optional[Retroalimentacion]:
    return (
        db.query(Retroalimentacion)
        .filter(Retroalimentacion.postulacion_id == postulacion_id)
        .first()
    )


def create_retroalimentacion(
    db: Session, retroalimentacion: RetroalimentacionCreate
) -> Retroalimentacion:
    db_obj = Retroalimentacion(**retroalimentacion.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_retroalimentacion(
    db: Session,
    db_obj: Retroalimentacion,
    retroalimentacion: RetroalimentacionUpdate,
) -> Retroalimentacion:
    update_data = retroalimentacion.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    if update_data:
        db_obj.roadmap_json = None
        db_obj.roadmap_estado = "pendiente"
        db_obj.roadmap_generado_en = None
        db_obj.roadmap_error = None
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_retroalimentacion(db: Session, db_obj: Retroalimentacion) -> Retroalimentacion:
    db.delete(db_obj)
    db.commit()
    return db_obj
