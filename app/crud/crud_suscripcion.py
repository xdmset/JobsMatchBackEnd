from datetime import date

from sqlalchemy.orm import Session

from app.models.suscripcion import Suscripcion
from app.models.user import User
from app.schemas.suscripcion import SuscripcionCreate, SuscripcionUpdate
from app.services.subscription_service import sync_user_premium_status


def get_suscripcion(db: Session, suscripcion_id: int):
    return db.query(Suscripcion).filter(Suscripcion.id == suscripcion_id).first()


def get_suscripciones(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Suscripcion).offset(skip).limit(limit).all()


def get_suscripciones_by_usuario(db: Session, usuario_id: int):
    return db.query(Suscripcion).filter(Suscripcion.usuario_id == usuario_id).all()


def get_user(db: Session, usuario_id: int):
    return db.query(User).filter(User.id == usuario_id).first()


def create_suscripcion(db: Session, suscripcion: SuscripcionCreate):
    db_suscripcion = Suscripcion(**suscripcion.model_dump())
    db.add(db_suscripcion)
    db.commit()
    sync_user_premium_status(db, db_suscripcion.usuario_id)
    db.commit()
    db.refresh(db_suscripcion)
    return db_suscripcion


def update_suscripcion(db: Session, suscripcion_id: int, suscripcion_data: SuscripcionUpdate):
    db_suscripcion = get_suscripcion(db, suscripcion_id)
    if db_suscripcion:
        previous_user_id = db_suscripcion.usuario_id
        update_fields = suscripcion_data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            setattr(db_suscripcion, field, value)

        # Legacy free subscriptions may carry an expired end date. If they are
        # upgraded to premium without an explicit new end date, treat them as active.
        if db_suscripcion.tipo_plan == "premium":
            if db_suscripcion.fecha_inicio is None:
                db_suscripcion.fecha_inicio = date.today()
            if "fecha_fin" not in update_fields and db_suscripcion.fecha_fin is not None and db_suscripcion.fecha_fin < date.today():
                db_suscripcion.fecha_fin = None

        db.flush()
        sync_user_premium_status(db, previous_user_id)
        if db_suscripcion.usuario_id != previous_user_id:
            sync_user_premium_status(db, db_suscripcion.usuario_id)
        db.commit()
        db.refresh(db_suscripcion)
    return db_suscripcion


def delete_suscripcion(db: Session, suscripcion_id: int):
    db_suscripcion = get_suscripcion(db, suscripcion_id)
    if db_suscripcion:
        usuario_id = db_suscripcion.usuario_id
        db.delete(db_suscripcion)
        db.commit()
        sync_user_premium_status(db, usuario_id)
        db.commit()
    return db_suscripcion
