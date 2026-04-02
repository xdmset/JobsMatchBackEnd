from __future__ import annotations

from datetime import date
from decimal import Decimal
import json

from sqlalchemy.orm import Session

from app.models.plan import Plan
from app.models.suscripcion import Suscripcion
from app.models.user import User


def get_default_subscription_for_user(db: Session, usuario_id: int) -> Suscripcion | None:
    return (
        db.query(Suscripcion)
        .filter(
            Suscripcion.usuario_id == usuario_id,
            Suscripcion.tipo_plan == "free",
        )
        .order_by(Suscripcion.fecha_inicio.desc(), Suscripcion.id.desc())
        .first()
    )


def is_premium_subscription_active(suscripcion: Suscripcion, today: date | None = None) -> bool:
    today = today or date.today()
    if suscripcion.tipo_plan != "premium":
        return False
    if suscripcion.origen_pago == "paypal":
        if suscripcion.estado_externo == "ACTIVE":
            pass
        elif suscripcion.estado_externo == "CANCELLED" and suscripcion.fecha_fin and suscripcion.fecha_fin >= today:
            pass
        else:
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


def sync_all_users_premium_status(db: Session) -> int:
    users = db.query(User).all()
    updated_count = 0

    for user in users:
        previous_value = user.es_premium
        sync_user_premium_status(db, user.id)
        if user.es_premium != previous_value:
            updated_count += 1

    db.flush()
    return updated_count


def create_default_subscription_for_user(db: Session, usuario_id: int) -> Suscripcion:
    existing_default = get_default_subscription_for_user(db, usuario_id)
    if existing_default:
        sync_user_premium_status(db, usuario_id)
        return existing_default

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


def get_current_subscription(db: Session, usuario_id: int) -> Suscripcion | None:
    subscriptions = get_user_subscriptions(db, usuario_id)
    if not subscriptions:
        return None

    for subscription in subscriptions:
        if is_premium_subscription_active(subscription):
            return subscription

    default_subscription = get_default_subscription_for_user(db, usuario_id)
    if default_subscription:
        return default_subscription

    return subscriptions[0]


def get_paypal_plan_by_code(db: Session, codigo: str) -> Plan | None:
    return db.query(Plan).filter(Plan.codigo == codigo).first()


def get_paypal_plan_by_remote_id(db: Session, paypal_plan_id: str) -> Plan | None:
    return db.query(Plan).filter(Plan.paypal_plan_id == paypal_plan_id).first()


def upsert_paypal_plan(
    db: Session,
    *,
    codigo: str,
    nombre: str,
    paypal_product_id: str,
    paypal_plan_id: str,
    moneda: str,
    precio: Decimal,
    intervalo_unidad: str,
    intervalo_conteo: int,
) -> Plan:
    plan = get_paypal_plan_by_code(db, codigo)
    if not plan:
        plan = Plan(codigo=codigo)
        db.add(plan)

    plan.nombre = nombre
    plan.paypal_product_id = paypal_product_id
    plan.paypal_plan_id = paypal_plan_id
    plan.moneda = moneda
    plan.precio = precio
    plan.intervalo_unidad = intervalo_unidad
    plan.intervalo_conteo = intervalo_conteo
    plan.activo = True
    db.flush()
    return plan


def get_paypal_subscription_by_remote_id(db: Session, paypal_subscription_id: str) -> Suscripcion | None:
    return (
        db.query(Suscripcion)
        .filter(Suscripcion.paypal_subscription_id == paypal_subscription_id)
        .first()
    )


def get_open_paypal_subscription_for_user(db: Session, usuario_id: int) -> Suscripcion | None:
    return (
        db.query(Suscripcion)
        .filter(
            Suscripcion.usuario_id == usuario_id,
            Suscripcion.origen_pago == "paypal",
            Suscripcion.estado_externo.in_(["APPROVAL_PENDING", "APPROVED", "ACTIVE", "SUSPENDED"]),
        )
        .order_by(Suscripcion.id.desc())
        .first()
    )


def create_or_update_paypal_subscription(
    db: Session,
    *,
    usuario_id: int,
    plan: Plan | None,
    paypal_subscription_id: str,
    paypal_plan_id: str,
    estado_externo: str,
    fecha_inicio: date | None,
    fecha_fin: date | None,
    payload: dict,
) -> Suscripcion:
    suscripcion = get_paypal_subscription_by_remote_id(db, paypal_subscription_id)
    if not suscripcion:
        suscripcion = Suscripcion(
            usuario_id=usuario_id,
            tipo_plan="premium",
            origen_pago="paypal",
            paypal_subscription_id=paypal_subscription_id,
        )
        db.add(suscripcion)

    suscripcion.usuario_id = usuario_id
    suscripcion.tipo_plan = "premium"
    suscripcion.origen_pago = "paypal"
    suscripcion.paypal_plan_id = paypal_plan_id
    suscripcion.estado_externo = estado_externo
    suscripcion.fecha_inicio = fecha_inicio
    suscripcion.fecha_fin = fecha_fin
    suscripcion.detalle_externo = json.dumps(payload, ensure_ascii=True, sort_keys=True)

    if plan:
        suscripcion.moneda = plan.moneda
        suscripcion.monto = plan.precio
    elif payload.get("billing_info", {}).get("last_payment", {}).get("amount"):
        amount = payload["billing_info"]["last_payment"]["amount"]
        suscripcion.moneda = amount.get("currency_code")
        value = amount.get("value")
        suscripcion.monto = Decimal(str(value)) if value is not None else None

    db.flush()
    sync_user_premium_status(db, usuario_id)
    return suscripcion
