from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# Esquema para crear un Swipe (RF-04)
class SwipeCreate(BaseModel):
    vacante_id: int
    interes_estudiante: bool

# Esquema para la Retroalimentación (RF-11)
class RetroalimentacionCreate(BaseModel):
    campos_mejora: str
    sugerencias_perfil: str

# Esquema para que la empresa actualice el estado (RF-06)
class CambiarEstadoPostulacion(BaseModel):
    nuevo_estado: str  # 'visto', 'en_proceso', 'rechazado'
    feedback: Optional[RetroalimentacionCreate] = None

# Esquema de respuesta para un Match
class MatchResponse(BaseModel):
    id: int
    estudiante_id: int
    vacante_id: int
    fecha_match: datetime

    class Config:
        from_attributes = True

# Esquema de respuesta para ver Postulaciones (RF-06)
class PostulacionRead(BaseModel):
    id: int
    match_id: int
    estado: str
    fecha_actualizacion: Optional[datetime]

    class Config:
        from_attributes = True