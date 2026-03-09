from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RetroalimentacionBase(BaseModel):
    postulacion_id: int
    campos_mejora: Optional[str] = None
    sugerencias_perfil: Optional[str] = None


class RetroalimentacionCreate(RetroalimentacionBase):
    pass


class RetroalimentacionUpdate(BaseModel):
    campos_mejora: Optional[str] = None
    sugerencias_perfil: Optional[str] = None


class RetroalimentacionRead(RetroalimentacionBase):
    id: int
    fecha_envio: Optional[datetime] = None

    class Config:
        from_attributes = True
