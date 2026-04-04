from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.dependencies import ensure_roles, ensure_same_user, get_current_user, get_user_role
from app.core.enums import NombreRol
from app.db.session import get_db
from app.models.user import User
from app.schemas.payment import (
    PaypalBillingCycle,
    PaypalBootstrapResponse,
    PaypalCancelSubscriptionRequest,
    PaypalCreateSubscriptionRequest,
    PaypalPlanResponse,
    PaypalSubscriptionCreateResponse,
    PaypalSubscriptionSyncResponse,
)
from app.services.paypal_service import (
    PaypalClient,
    PaypalServiceError,
    extract_subscription_id_from_webhook,
    extract_user_id_from_custom_id,
    get_approval_url,
    get_default_paypal_plan_definitions,
    get_paypal_plan_definitions_for_role,
    get_effective_end_date,
    parse_paypal_date,
    build_paypal_plan_code,
)
from app.services.subscription_service import (
    create_or_update_paypal_subscription,
    get_paypal_plans_by_role,
    get_open_paypal_subscription_for_user,
    get_paypal_plan_by_code,
    get_paypal_plan_by_remote_id,
    get_paypal_subscription_by_remote_id,
    upsert_paypal_plan,
)

router = APIRouter()


def _translate_paypal_error(exc: PaypalServiceError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=f"PayPal devolvio un error: {exc}",
    )


def _sync_paypal_subscription_payload(
    db: Session,
    payload: dict[str, Any],
    *,
    fallback_user_id: int | None = None,
) -> PaypalSubscriptionSyncResponse:
    paypal_subscription_id = payload.get("id")
    if not paypal_subscription_id:
        raise HTTPException(status_code=400, detail="Respuesta de PayPal sin id de suscripcion")

    paypal_plan_id = payload.get("plan_id")
    plan = get_paypal_plan_by_remote_id(db, paypal_plan_id) if paypal_plan_id else None
    custom_id = payload.get("custom_id")
    usuario_id = extract_user_id_from_custom_id(custom_id) or fallback_user_id
    if not usuario_id:
        raise HTTPException(status_code=400, detail="No fue posible identificar al usuario")

    fecha_inicio = parse_paypal_date(payload.get("start_time"))
    estado = payload.get("status", "UNKNOWN")
    fecha_fin = None if estado in {"APPROVAL_PENDING", "APPROVED", "ACTIVE"} else get_effective_end_date(payload)

    suscripcion = create_or_update_paypal_subscription(
        db,
        usuario_id=usuario_id,
        plan=plan,
        paypal_subscription_id=paypal_subscription_id,
        paypal_plan_id=paypal_plan_id,
        estado_externo=estado,
        fecha_inicio=fecha_inicio or date.today(),
        fecha_fin=fecha_fin,
        payload=payload,
    )
    db.commit()
    db.refresh(suscripcion)
    return PaypalSubscriptionSyncResponse.model_validate(suscripcion)


@router.get("/paypal/plans", response_model=list[PaypalPlanResponse])
def list_paypal_plans(db: Session = Depends(get_db)):
    plans = []
    for definition in get_default_paypal_plan_definitions():
        plan = get_paypal_plan_by_code(db, definition.code)
        if plan:
            plans.append(plan)
    return plans


@router.get("/paypal/plans/me", response_model=list[PaypalPlanResponse])
def list_paypal_plans_for_current_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_roles(current_user, NombreRol.estudiante.value, NombreRol.empresa.value)
    role_scope = get_user_role(current_user)
    return get_paypal_plans_by_role(db, role_scope)


@router.post("/paypal/bootstrap", response_model=PaypalBootstrapResponse)
def bootstrap_paypal_catalog(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_roles(current_user, NombreRol.admin.value)
    client = PaypalClient()

    try:
        token = client.get_access_token()
        existing = [get_paypal_plan_by_code(db, item.code) for item in get_default_paypal_plan_definitions()]
        existing = [item for item in existing if item is not None]
        if len(existing) == 6:
            return PaypalBootstrapResponse(
                products={
                    "estudiante": next(item.paypal_product_id for item in existing if item.rol_objetivo == "estudiante"),
                    "empresa": next(item.paypal_product_id for item in existing if item.rol_objetivo == "empresa"),
                },
                plans=existing,
            )

        stored_plans = []
        products: dict[str, str] = {}
        for role_scope in (NombreRol.estudiante.value, NombreRol.empresa.value):
            definitions = get_paypal_plan_definitions_for_role(role_scope)
            product = client.create_product(
                token=token,
                product_name=definitions[0].product_name,
                product_description=definitions[0].product_description,
            )
            product_id = product["id"]
            products[role_scope] = product_id

            for definition in definitions:
                remote_plan = client.create_plan(token=token, product_id=product_id, definition=definition)
                stored_plans.append(
                    upsert_paypal_plan(
                        db,
                        codigo=definition.code,
                        nombre=definition.name,
                        rol_objetivo=definition.role_scope,
                        periodicidad=definition.code.rsplit("_", 1)[-1],
                        paypal_product_id=product_id,
                        paypal_plan_id=remote_plan["id"],
                        moneda=remote_plan["billing_cycles"][0]["pricing_scheme"]["fixed_price"]["currency_code"],
                        precio=definition.price,
                        intervalo_unidad=definition.interval_unit,
                        intervalo_conteo=definition.interval_count,
                    )
                )
        db.commit()
        for plan in stored_plans:
            db.refresh(plan)
        return PaypalBootstrapResponse(products=products, plans=stored_plans)
    except PaypalServiceError as exc:
        db.rollback()
        raise _translate_paypal_error(exc) from exc


@router.post("/paypal/subscriptions", response_model=PaypalSubscriptionCreateResponse)
def create_paypal_subscription(
    payload: PaypalCreateSubscriptionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_roles(current_user, NombreRol.estudiante.value, NombreRol.empresa.value)
    client = PaypalClient()
    role_scope = get_user_role(current_user)
    plan_code = build_paypal_plan_code(role_scope, payload.billing_cycle.value)
    plan = get_paypal_plan_by_code(db, plan_code)
    if not plan or not plan.activo:
        raise HTTPException(status_code=404, detail="Plan PayPal no configurado")
    existing = get_open_paypal_subscription_for_user(db, current_user.id, role_scope=role_scope)
    if existing:
        raise HTTPException(
            status_code=409,
            detail="El usuario ya tiene una suscripcion PayPal abierta para su rol",
        )

    try:
        token = client.get_access_token()
        response = client.create_subscription(
            token=token,
            paypal_plan_id=plan.paypal_plan_id,
            user_id=current_user.id,
            user_email=current_user.email,
            plan_code=plan_code,
            return_url=str(payload.return_url) if payload.return_url else None,
            cancel_url=str(payload.cancel_url) if payload.cancel_url else None,
        )
        sync_response = _sync_paypal_subscription_payload(db, response, fallback_user_id=current_user.id)
        return PaypalSubscriptionCreateResponse(
            paypal_subscription_id=sync_response.paypal_subscription_id or response["id"],
            status=sync_response.estado_externo or response.get("status", "UNKNOWN"),
            approve_url=get_approval_url(response),
        )
    except PaypalServiceError as exc:
        db.rollback()
        raise _translate_paypal_error(exc) from exc


@router.post("/paypal/subscriptions/{paypal_subscription_id}/sync", response_model=PaypalSubscriptionSyncResponse)
def sync_paypal_subscription(
    paypal_subscription_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = get_paypal_subscription_by_remote_id(db, paypal_subscription_id)
    if existing:
        ensure_same_user(current_user, existing.usuario_id)

    client = PaypalClient()
    try:
        token = client.get_access_token()
        payload = client.get_subscription(token=token, paypal_subscription_id=paypal_subscription_id)
        usuario_id = extract_user_id_from_custom_id(payload.get("custom_id"))
        if usuario_id is not None:
            ensure_same_user(current_user, usuario_id)
        return _sync_paypal_subscription_payload(db, payload, fallback_user_id=current_user.id)
    except PaypalServiceError as exc:
        db.rollback()
        raise _translate_paypal_error(exc) from exc


@router.post("/paypal/subscriptions/{paypal_subscription_id}/cancel", response_model=PaypalSubscriptionSyncResponse)
def cancel_paypal_subscription(
    paypal_subscription_id: str,
    payload: PaypalCancelSubscriptionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = get_paypal_subscription_by_remote_id(db, paypal_subscription_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Suscripcion PayPal no encontrada")
    ensure_same_user(current_user, existing.usuario_id)

    client = PaypalClient()
    try:
        token = client.get_access_token()
        client.cancel_subscription(
            token=token,
            paypal_subscription_id=paypal_subscription_id,
            reason=payload.reason,
        )
        remote = client.get_subscription(token=token, paypal_subscription_id=paypal_subscription_id)
        return _sync_paypal_subscription_payload(db, remote, fallback_user_id=current_user.id)
    except PaypalServiceError as exc:
        db.rollback()
        raise _translate_paypal_error(exc) from exc


@router.post("/paypal/webhook")
async def paypal_webhook(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    client = PaypalClient()

    try:
        token = client.get_access_token()
        headers = {
            "PAYPAL-AUTH-ALGO": request.headers.get("PAYPAL-AUTH-ALGO", ""),
            "PAYPAL-CERT-URL": request.headers.get("PAYPAL-CERT-URL", ""),
            "PAYPAL-TRANSMISSION-ID": request.headers.get("PAYPAL-TRANSMISSION-ID", ""),
            "PAYPAL-TRANSMISSION-SIG": request.headers.get("PAYPAL-TRANSMISSION-SIG", ""),
            "PAYPAL-TRANSMISSION-TIME": request.headers.get("PAYPAL-TRANSMISSION-TIME", ""),
        }
        if not client.verify_webhook_signature(token=token, headers=headers, body=body):
            raise HTTPException(status_code=400, detail="Webhook PayPal invalido")

        paypal_subscription_id = extract_subscription_id_from_webhook(body)
        if not paypal_subscription_id:
            return {"status": "ignored"}

        remote = client.get_subscription(token=token, paypal_subscription_id=paypal_subscription_id)
        _sync_paypal_subscription_payload(db, remote)
        return {"status": "ok"}
    except PaypalServiceError as exc:
        db.rollback()
        raise _translate_paypal_error(exc) from exc
