from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
import logging
from typing import Any

import requests
from fastapi import HTTPException, status

from app.core.config import settings

logger = logging.getLogger(__name__)


class PaypalServiceError(Exception):
    pass


@dataclass(frozen=True)
class PaypalPlanDefinition:
    code: str
    name: str
    price: Decimal
    interval_unit: str
    interval_count: int


def get_default_paypal_plan_definitions() -> list[PaypalPlanDefinition]:
    return [
        PaypalPlanDefinition(
            code="mensual",
            name="Premium Mensual",
            price=Decimal(str(settings.PAYPAL_MONTHLY_PRICE)),
            interval_unit="MONTH",
            interval_count=1,
        ),
        PaypalPlanDefinition(
            code="semestral",
            name="Premium Semestral",
            price=Decimal(str(settings.PAYPAL_SEMIANNUAL_PRICE)),
            interval_unit="MONTH",
            interval_count=6,
        ),
        PaypalPlanDefinition(
            code="anual",
            name="Premium Anual",
            price=Decimal(str(settings.PAYPAL_ANNUAL_PRICE)),
            interval_unit="MONTH",
            interval_count=12,
        ),
    ]


def parse_paypal_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


def parse_paypal_date(value: str | None) -> date | None:
    parsed = parse_paypal_datetime(value)
    return parsed.date() if parsed else None


def get_approval_url(payload: dict[str, Any]) -> str | None:
    for link in payload.get("links", []):
        if link.get("rel") == "approve":
            return link.get("href")
    return None


def extract_user_id_from_custom_id(custom_id: str | None) -> int | None:
    if not custom_id:
        return None

    prefix = "user:"
    if not custom_id.startswith(prefix):
        return None

    user_part = custom_id.split("|", 1)[0]
    raw_user_id = user_part.replace(prefix, "", 1)
    try:
        return int(raw_user_id)
    except ValueError:
        return None


def extract_subscription_id_from_webhook(event: dict[str, Any]) -> str | None:
    resource = event.get("resource", {}) or {}
    event_type = event.get("event_type", "")

    if event_type.startswith("BILLING.SUBSCRIPTION."):
        return resource.get("id")

    if event_type.startswith("PAYMENT.SALE."):
        supplementary_data = resource.get("supplementary_data", {}) or {}
        related_ids = supplementary_data.get("related_ids", {}) or {}
        return related_ids.get("subscription_id") or resource.get("billing_agreement_id")

    return resource.get("id")


class PaypalClient:
    def __init__(self) -> None:
        self.base_url = settings.PAYPAL_BASE_URL.rstrip("/")
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.secret = settings.PAYPAL_SECRET
        self.timeout = 30

    def is_configured(self) -> bool:
        return bool(self.client_id and self.secret)

    def _raise_if_unconfigured(self) -> None:
        if not self.is_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="PayPal no esta configurado en el servidor",
            )

    def _request(
        self,
        method: str,
        path: str,
        *,
        token: str | None = None,
        json_payload: dict[str, Any] | None = None,
        data: Any | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        self._raise_if_unconfigured()
        headers = {"Accept": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        if extra_headers:
            headers.update(extra_headers)

        response = requests.request(
            method=method,
            url=f"{self.base_url}{path}",
            headers=headers,
            json=json_payload,
            data=data,
            timeout=self.timeout,
        )

        if response.status_code >= 400:
            detail = response.text
            logger.warning("PayPal request failed: %s %s", response.status_code, detail)
            raise PaypalServiceError(detail)

        if response.status_code == 204 or not response.content:
            return {}

        return response.json()

    def get_access_token(self) -> str:
        self._raise_if_unconfigured()
        response = requests.post(
            f"{self.base_url}/v1/oauth2/token",
            auth=(self.client_id, self.secret),
            headers={"Accept": "application/json", "Accept-Language": "en_US"},
            data={"grant_type": "client_credentials"},
            timeout=self.timeout,
        )
        if response.status_code >= 400:
            logger.warning("PayPal OAuth failed: %s %s", response.status_code, response.text)
            raise PaypalServiceError(response.text)
        payload = response.json()
        token = payload.get("access_token")
        if not token:
            raise PaypalServiceError("PayPal no devolvio un access token")
        return token

    def create_product(self, *, token: str) -> dict[str, Any]:
        payload = {
            "name": settings.PAYPAL_PRODUCT_NAME,
            "description": settings.PAYPAL_PRODUCT_DESCRIPTION,
            "type": "SERVICE",
            "category": "SOFTWARE",
        }
        return self._request(
            "POST",
            "/v1/catalogs/products",
            token=token,
            json_payload=payload,
            extra_headers={"Content-Type": "application/json"},
        )

    def create_plan(
        self,
        *,
        token: str,
        product_id: str,
        definition: PaypalPlanDefinition,
    ) -> dict[str, Any]:
        payload = {
            "product_id": product_id,
            "name": definition.name,
            "description": f"Suscripcion {definition.code} para JOBMATCH Premium",
            "status": "ACTIVE",
            "billing_cycles": [
                {
                    "frequency": {
                        "interval_unit": definition.interval_unit,
                        "interval_count": definition.interval_count,
                    },
                    "tenure_type": "REGULAR",
                    "sequence": 1,
                    "total_cycles": 0,
                    "pricing_scheme": {
                        "fixed_price": {
                            "value": f"{definition.price:.2f}",
                            "currency_code": settings.PAYPAL_CURRENCY,
                        }
                    },
                }
            ],
            "payment_preferences": {
                "auto_bill_outstanding": True,
                "setup_fee_failure_action": "CONTINUE",
                "payment_failure_threshold": 3,
            },
        }
        return self._request(
            "POST",
            "/v1/billing/plans",
            token=token,
            json_payload=payload,
            extra_headers={"Content-Type": "application/json", "Prefer": "return=representation"},
        )

    def create_subscription(
        self,
        *,
        token: str,
        paypal_plan_id: str,
        user_id: int,
        user_email: str,
        plan_code: str,
        return_url: str | None = None,
        cancel_url: str | None = None,
    ) -> dict[str, Any]:
        payload = {
            "plan_id": paypal_plan_id,
            "custom_id": f"user:{user_id}|plan:{plan_code}",
            "subscriber": {
                "email_address": user_email,
            },
            "application_context": {
                "brand_name": settings.PROJECT_NAME,
                "locale": "es-MX",
                "shipping_preference": "NO_SHIPPING",
                "user_action": "SUBSCRIBE_NOW",
                "payment_method": {
                    "payer_selected": "PAYPAL",
                    "payee_preferred": "IMMEDIATE_PAYMENT_REQUIRED",
                },
                "return_url": return_url or settings.PAYPAL_WEB_RETURN_URL,
                "cancel_url": cancel_url or settings.PAYPAL_WEB_CANCEL_URL,
            },
        }
        return self._request(
            "POST",
            "/v1/billing/subscriptions",
            token=token,
            json_payload=payload,
            extra_headers={"Content-Type": "application/json", "Prefer": "return=representation"},
        )

    def get_subscription(self, *, token: str, paypal_subscription_id: str) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/v1/billing/subscriptions/{paypal_subscription_id}",
            token=token,
            extra_headers={"Content-Type": "application/json"},
        )

    def cancel_subscription(
        self,
        *,
        token: str,
        paypal_subscription_id: str,
        reason: str,
    ) -> None:
        self._request(
            "POST",
            f"/v1/billing/subscriptions/{paypal_subscription_id}/cancel",
            token=token,
            json_payload={"reason": reason},
            extra_headers={"Content-Type": "application/json"},
        )

    def verify_webhook_signature(
        self,
        *,
        token: str,
        headers: dict[str, str],
        body: dict[str, Any],
    ) -> bool:
        webhook_id = settings.PAYPAL_WEBHOOK_ID
        if not webhook_id:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="PAYPAL_WEBHOOK_ID no esta configurado",
            )

        payload = {
            "auth_algo": headers.get("PAYPAL-AUTH-ALGO"),
            "cert_url": headers.get("PAYPAL-CERT-URL"),
            "transmission_id": headers.get("PAYPAL-TRANSMISSION-ID"),
            "transmission_sig": headers.get("PAYPAL-TRANSMISSION-SIG"),
            "transmission_time": headers.get("PAYPAL-TRANSMISSION-TIME"),
            "webhook_id": webhook_id,
            "webhook_event": body,
        }
        result = self._request(
            "POST",
            "/v1/notifications/verify-webhook-signature",
            token=token,
            json_payload=payload,
            extra_headers={"Content-Type": "application/json"},
        )
        return result.get("verification_status") == "SUCCESS"


def get_effective_end_date(subscription_payload: dict[str, Any]) -> date | None:
    billing_info = subscription_payload.get("billing_info", {}) or {}
    status = subscription_payload.get("status")

    if status == "ACTIVE":
        return None

    next_billing_time = parse_paypal_date(billing_info.get("next_billing_time"))
    if next_billing_time:
        return next_billing_time

    final_payment_time = parse_paypal_date(billing_info.get("final_payment_time"))
    if final_payment_time:
        return final_payment_time

    status_update_time = parse_paypal_date(subscription_payload.get("status_update_time"))
    if status_update_time:
        return status_update_time

    return datetime.now(timezone.utc).date()
