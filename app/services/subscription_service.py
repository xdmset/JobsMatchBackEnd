from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
import json

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import NombreRol
from app.models.match import Match
from app.models.plan import Plan
from app.models.suscripcion import Suscripcion
from app.models.user import User


FREE_PLAN = "free"
PREMIUM_PLAN = "premium"


@dataclass(frozen=True)
class UserPlanContext:
    role_scope: str
    is_premium: bool
    daily_swipes_limit: int | None = None
    view_history_limit: int | None = None
    match_history_limit: int | None = None
    active_vacancies_limit: int | None = None
    search_priority: int = 0
    candidate_filter_level: str | None = None
    analytics_level: str | None = None


def get_role_scope_for_user(user: User) -> str:
    if not user.rol:
        raise ValueError("El usuario no tiene rol asociado")

    role_name = user.rol.nombre
    if role_name == NombreRol.estudiante or str(role_name) == NombreRol.estudiante.value:
        return NombreRol.estudiante.value
    if role_name == NombreRol.empresa or str(role_name) == NombreRol.empresa.value:
        return NombreRol.empresa.value
    raise ValueError("El rol del usuario no soporta suscripciones freemium")


def build_plan_context(user: User) -> UserPlanContext:
    if user.is_superuser:
        return UserPlanContext(
            role_scope=NombreRol.admin.value,
            is_premium=True,
            daily_swipes_limit=None,
            view_history_limit=None,
            match_history_limit=None,
            active_vacancies_limit=None,
            search_priority=999,
            candidate_filter_level="advanced",
            analytics_level="advanced",
        )

    role_scope = get_role_scope_for_user(user)
    if role_scope == NombreRol.estudiante.value:
        return UserPlanContext(
            role_scope=role_scope,
            is_premium=bool(user.es_premium),
            daily_swipes_limit=(
                settings.STUDENT_PREMIUM_DAILY_SWIPES if user.es_premium else settings.STUDENT_FREE_DAILY_SWIPES
            ),
            view_history_limit=(
                None if settings.STUDENT_PREMIUM_VIEW_HISTORY_LIMIT == 0 and user.es_premium
                else (
                    settings.STUDENT_PREMIUM_VIEW_HISTORY_LIMIT if user.es_premium else settings.STUDENT_FREE_VIEW_HISTORY_LIMIT
                )
            ),
            match_history_limit=(
                None if settings.STUDENT_PREMIUM_MATCH_HISTORY_LIMIT == 0 and user.es_premium
                else (
                    settings.STUDENT_PREMIUM_MATCH_HISTORY_LIMIT if user.es_premium else settings.STUDENT_FREE_MATCH_HISTORY_LIMIT
                )
            ),
            search_priority=(
                settings.STUDENT_PREMIUM_SEARCH_PRIORITY if user.es_premium else settings.STUDENT_FREE_SEARCH_PRIORITY
            ),
        )

    if role_scope == NombreRol.empresa.value:
        return UserPlanContext(
            role_scope=role_scope,
            is_premium=bool(user.es_premium),
            active_vacancies_limit=(
                settings.COMPANY_PREMIUM_ACTIVE_VACANCIES if user.es_premium else settings.COMPANY_FREE_ACTIVE_VACANCIES
            ),
            search_priority=(
                settings.COMPANY_PREMIUM_SEARCH_PRIORITY if user.es_premium else settings.COMPANY_FREE_SEARCH_PRIORITY
            ),
            candidate_filter_level="advanced" if user.es_premium else "basic",
            analytics_level="advanced" if user.es_premium else "basic",
        )

    raise ValueError("Rol no soportado")


def get_default_subscription_for_user(db: Session, usuario_id: int, role_scope: str) -> Suscripcion | None:
    return (
        db.query(Suscripcion)
        .filter(
            Suscripcion.usuario_id == usuario_id,
            Suscripcion.tipo_plan == FREE_PLAN,
            Suscripcion.rol_objetivo == role_scope,
        )
        .order_by(Suscripcion.fecha_inicio.desc(), Suscripcion.id.desc())
        .first()
    )


def is_premium_subscription_active(suscripcion: Suscripcion, today: date | None = None) -> bool:
    today = today or date.today()
    if suscripcion.tipo_plan != PREMIUM_PLAN:
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


def get_user_subscriptions(db: Session, usuario_id: int, role_scope: str | None = None) -> list[Suscripcion]:
    query = db.query(Suscripcion).filter(Suscripcion.usuario_id == usuario_id)
    if role_scope:
        query = query.filter(Suscripcion.rol_objetivo == role_scope)
    return query.order_by(Suscripcion.fecha_inicio.desc(), Suscripcion.id.desc()).all()


def sync_user_premium_status(db: Session, usuario_id: int) -> User | None:
    user = db.query(User).filter(User.id == usuario_id).first()
    if not user:
        return None

    try:
        role_scope = get_role_scope_for_user(user)
    except ValueError:
        user.es_premium = False
        db.flush()
        return user

    subscriptions = get_user_subscriptions(db, usuario_id, role_scope=role_scope)
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


def create_default_subscription_for_user(db: Session, usuario_id: int) -> Suscripcion | None:
    user = db.query(User).filter(User.id == usuario_id).first()
    if not user:
        raise ValueError("Usuario no encontrado")

    try:
        role_scope = get_role_scope_for_user(user)
    except ValueError:
        user.es_premium = False
        db.flush()
        return None

    existing_default = get_default_subscription_for_user(db, usuario_id, role_scope)
    if existing_default:
        sync_user_premium_status(db, usuario_id)
        return existing_default

    default_subscription = Suscripcion(
        usuario_id=usuario_id,
        tipo_plan=FREE_PLAN,
        rol_objetivo=role_scope,
        codigo_plan=f"{FREE_PLAN}_{role_scope}",
        fecha_inicio=date.today(),
        fecha_fin=None,
    )
    db.add(default_subscription)
    db.flush()
    sync_user_premium_status(db, usuario_id)
    return default_subscription


def set_user_subscription_plan(
    db: Session,
    usuario_id: int,
    tipo_plan: str,
    role_scope: str | None = None,
    codigo_plan: str | None = None,
) -> Suscripcion:
    user = db.query(User).filter(User.id == usuario_id).first()
    if not user:
        raise ValueError("Usuario no encontrado")

    role_scope = role_scope or get_role_scope_for_user(user)
    suscripcion = (
        db.query(Suscripcion)
        .filter(
            Suscripcion.usuario_id == usuario_id,
            Suscripcion.rol_objetivo == role_scope,
        )
        .order_by(Suscripcion.fecha_inicio.desc(), Suscripcion.id.desc())
        .first()
    )

    if not suscripcion:
        suscripcion = create_default_subscription_for_user(db, usuario_id)

    suscripcion.tipo_plan = tipo_plan
    suscripcion.rol_objetivo = role_scope
    suscripcion.codigo_plan = codigo_plan or f"{tipo_plan}_{role_scope}"
    if suscripcion.fecha_inicio is None:
        suscripcion.fecha_inicio = date.today()
    if tipo_plan == PREMIUM_PLAN and suscripcion.fecha_fin is not None and suscripcion.fecha_fin < date.today():
        suscripcion.fecha_fin = None

    db.flush()
    sync_user_premium_status(db, usuario_id)
    return suscripcion


def get_current_subscription(db: Session, usuario_id: int) -> Suscripcion | None:
    user = db.query(User).filter(User.id == usuario_id).first()
    if not user:
        return None

    try:
        role_scope = get_role_scope_for_user(user)
    except ValueError:
        return None

    subscriptions = get_user_subscriptions(db, usuario_id, role_scope=role_scope)
    if not subscriptions:
        return None

    for subscription in subscriptions:
        if is_premium_subscription_active(subscription):
            return subscription

    default_subscription = get_default_subscription_for_user(db, usuario_id, role_scope)
    if default_subscription:
        return default_subscription

    return subscriptions[0]


def get_paypal_plan_by_code(db: Session, codigo: str) -> Plan | None:
    return db.query(Plan).filter(Plan.codigo == codigo).first()


def get_paypal_plan_by_remote_id(db: Session, paypal_plan_id: str) -> Plan | None:
    return db.query(Plan).filter(Plan.paypal_plan_id == paypal_plan_id).first()


def get_paypal_plans_by_role(db: Session, role_scope: str) -> list[Plan]:
    return (
        db.query(Plan)
        .filter(
            Plan.rol_objetivo == role_scope,
            Plan.activo.is_(True),
        )
        .order_by(Plan.intervalo_conteo.asc(), Plan.id.asc())
        .all()
    )


def upsert_paypal_plan(
    db: Session,
    *,
    codigo: str,
    nombre: str,
    rol_objetivo: str,
    periodicidad: str,
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
    plan.rol_objetivo = rol_objetivo
    plan.periodicidad = periodicidad
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


def get_open_paypal_subscription_for_user(
    db: Session,
    usuario_id: int,
    role_scope: str | None = None,
) -> Suscripcion | None:
    query = db.query(Suscripcion).filter(
        Suscripcion.usuario_id == usuario_id,
        Suscripcion.origen_pago == "paypal",
        Suscripcion.estado_externo.in_(["APPROVAL_PENDING", "APPROVED", "ACTIVE", "SUSPENDED"]),
    )
    if role_scope:
        query = query.filter(Suscripcion.rol_objetivo == role_scope)
    return query.order_by(Suscripcion.id.desc()).first()


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
    user = db.query(User).filter(User.id == usuario_id).first()
    if not user:
        raise ValueError("Usuario no encontrado")

    role_scope = plan.rol_objetivo if plan else get_role_scope_for_user(user)
    suscripcion = get_paypal_subscription_by_remote_id(db, paypal_subscription_id)
    if not suscripcion:
        suscripcion = Suscripcion(
            usuario_id=usuario_id,
            tipo_plan=PREMIUM_PLAN,
            rol_objetivo=role_scope,
            codigo_plan=plan.codigo if plan else None,
            origen_pago="paypal",
            paypal_subscription_id=paypal_subscription_id,
        )
        db.add(suscripcion)

    suscripcion.usuario_id = usuario_id
    suscripcion.tipo_plan = PREMIUM_PLAN
    suscripcion.rol_objetivo = role_scope
    suscripcion.codigo_plan = plan.codigo if plan else suscripcion.codigo_plan
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


def get_student_match_history(
    db: Session,
    estudiante_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[Match]:
    return (
        db.query(Match)
        .filter(Match.estudiante_id == estudiante_id)
        .order_by(Match.fecha_match.desc(), Match.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
