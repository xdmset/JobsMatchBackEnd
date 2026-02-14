from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PostulacionWebCreate(BaseModel):
    estudiante_id: int
    vacante_id: int


class RetroalimentacionCreate(BaseModel):
    campos_mejora: str
    sugerencias_perfil: str


class CambiarEstadoPostulacion(BaseModel):
    nuevo_estado: str
    feedback: Optional[RetroalimentacionCreate] = None


class PostulacionRead(BaseModel):
    id: int
    match_id: Optional[int]
    estudiante_id: int
    vacante_id: int
    empresa_id: int
    source: str
    estado: str
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime]

    class Config:
        from_attributes = True
