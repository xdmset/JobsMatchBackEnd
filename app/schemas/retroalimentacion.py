from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RetroalimentacionBase(BaseModel):
    postulacion_id: int
    campos_mejora: Optional[str] = None
    sugerencias_perfil: Optional[str] = None


class RoadmapStep(BaseModel):
    semana: str
    objetivo: str
    tareas: list[str] = Field(default_factory=list)


class RoadmapData(BaseModel):
    habilidades: list[str] = Field(default_factory=list)
    acciones: list[str] = Field(default_factory=list)
    recursos: list[str] = Field(default_factory=list)
    tiempo_estimado: str
    prioridad: str
    roadmap_detallado: list[RoadmapStep] = Field(default_factory=list)


class RetroalimentacionCreate(RetroalimentacionBase):
    pass


class RetroalimentacionUpdate(BaseModel):
    campos_mejora: Optional[str] = None
    sugerencias_perfil: Optional[str] = None


class RetroalimentacionRead(RetroalimentacionBase):
    id: int
    fecha_envio: Optional[datetime] = None
    roadmap_estado: Optional[str] = None
    roadmap_generado_en: Optional[datetime] = None
    roadmap: Optional[RoadmapData] = None

    class Config:
        from_attributes = True
