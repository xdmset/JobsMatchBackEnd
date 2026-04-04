from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class TipoPlanSuscripcion(str, Enum):
    free = "free"
    premium = "premium"


class SuscripcionBase(BaseModel):
    usuario_id: int
    tipo_plan: TipoPlanSuscripcion
    rol_objetivo: str
    codigo_plan: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None


class SuscripcionCreate(SuscripcionBase):
    pass


class SuscripcionUpdate(BaseModel):
    usuario_id: Optional[int] = None
    tipo_plan: Optional[TipoPlanSuscripcion] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None


class Suscripcion(SuscripcionBase):
    id: int

    class Config:
        from_attributes = True


class SuscripcionActual(BaseModel):
    usuario_id: int
    tipo_plan_actual: TipoPlanSuscripcion
    es_premium: bool
    suscripcion: Optional[Suscripcion] = None

    class Config:
        from_attributes = True
