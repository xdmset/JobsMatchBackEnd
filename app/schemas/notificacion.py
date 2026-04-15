from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TipoNotificacion(str, Enum):
    like_recibido = "like_recibido"
    match = "match"
    postulacion_estado = "postulacion_estado"


class NotificacionBase(BaseModel):
    tipo: TipoNotificacion
    titulo: str
    mensaje: str
    vacante_id: Optional[int] = None
    postulacion_id: Optional[int] = None
    estudiante_id: Optional[int] = None


class NotificacionCreate(NotificacionBase):
    usuario_id: int


class NotificacionRead(NotificacionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    leida: bool
    fecha_creacion: datetime
    fecha_leida: Optional[datetime] = None


class NotificacionesResumen(BaseModel):
    total: int
    no_leidas: int
