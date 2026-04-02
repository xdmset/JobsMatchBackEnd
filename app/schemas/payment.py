from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import AnyHttpUrl, BaseModel, ConfigDict


class PaypalPlanCode(str, Enum):
    mensual = "mensual"
    semestral = "semestral"
    anual = "anual"


class PaypalPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: PaypalPlanCode
    nombre: str
    paypal_product_id: str
    paypal_plan_id: str
    moneda: str
    precio: Decimal
    intervalo_unidad: str
    intervalo_conteo: int
    activo: bool


class PaypalBootstrapResponse(BaseModel):
    product_id: str
    plans: list[PaypalPlanResponse]


class PaypalCreateSubscriptionRequest(BaseModel):
    plan_code: PaypalPlanCode
    return_url: Optional[AnyHttpUrl] = None
    cancel_url: Optional[AnyHttpUrl] = None


class PaypalSubscriptionCreateResponse(BaseModel):
    paypal_subscription_id: str
    status: str
    approve_url: AnyHttpUrl | None = None


class PaypalSubscriptionSyncResponse(BaseModel):
    id: int
    usuario_id: int
    tipo_plan: str
    origen_pago: str
    estado_externo: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    paypal_plan_id: Optional[str] = None
    paypal_subscription_id: Optional[str] = None
    moneda: Optional[str] = None
    monto: Optional[Decimal] = None

    model_config = ConfigDict(from_attributes=True)


class PaypalCancelSubscriptionRequest(BaseModel):
    reason: str = "Cancelada por el usuario"
