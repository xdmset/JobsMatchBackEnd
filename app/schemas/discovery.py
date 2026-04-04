from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.perfil_estudiante import PerfilEstudiante


class CandidateFeedItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    usuario_id: int
    email: str
    es_premium: bool
    fecha_registro: Optional[datetime] = None
    ya_dio_like: bool
    fecha_like: Optional[datetime] = None
    perfil_estudiante: PerfilEstudiante
