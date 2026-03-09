from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.models.suscripcion import Suscripcion
from app.models.user import User


def is_premium_subscription_active(suscripcion: Suscripcion, today: date | None = None) -> bool:
    today = today or date.today()
    if suscripcion.tipo_plan != "premium":
        return False
    if suscripcion.fecha_inicio and suscripcion.fecha_inicio > today:
        return False
    if suscripcion.fecha_fin and suscripcion.fecha_fin < today:
        return False
    return True


def get_user_subscriptions(db: Session, usuario_id: int) -> list[Suscripcion]:
    return (
        db.query(Suscripcion)
        .filter(Suscripcion.usuario_id == usuario_id)
        .order_by(Suscripcion.fecha_inicio.desc(), Suscripcion.id.desc())
        .all()
    )


def sync_user_premium_status(db: Session, usuario_id: int) -> User | None:
    user = db.query(User).filter(User.id == usuario_id).first()
    if not user:
        return None

    subscriptions = get_user_subscriptions(db, usuario_id)
    user.es_premium = any(is_premium_subscription_active(item) for item in subscriptions)
    db.flush()
    return user


def create_default_subscription_for_user(db: Session, usuario_id: int) -> Suscripcion:
    default_subscription = Suscripcion(
        usuario_id=usuario_id,
        tipo_plan="free",
        fecha_inicio=date.today(),
        fecha_fin=None,
    )
    db.add(default_subscription)
    db.flush()
    sync_user_premium_status(db, usuario_id)
    return default_subscription


def set_user_subscription_plan(db: Session, usuario_id: int, tipo_plan: str) -> Suscripcion:
    suscripcion = (
        db.query(Suscripcion)
        .filter(Suscripcion.usuario_id == usuario_id)
        .order_by(Suscripcion.fecha_inicio.desc(), Suscripcion.id.desc())
        .first()
    )

    if not suscripcion:
        suscripcion = create_default_subscription_for_user(db, usuario_id)

    suscripcion.tipo_plan = tipo_plan
    if suscripcion.fecha_inicio is None:
        suscripcion.fecha_inicio = date.today()
    if tipo_plan == "premium" and suscripcion.fecha_fin is not None and suscripcion.fecha_fin < date.today():
        suscripcion.fecha_fin = None

    db.flush()
    sync_user_premium_status(db, usuario_id)
    return suscripcion
