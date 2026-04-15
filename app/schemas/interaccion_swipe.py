from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SwipeCreate(BaseModel):
    vacante_id: int
    interes_estudiante: bool


class SwipeEmpresaCreate(BaseModel):
    estudiante_id: int
    vacante_id: int
    interes_empresa: bool


# --- Schemas para historial de swipes de estudiantes ---


class VacanteSwipeEstudiante(BaseModel):
    """Vacante con informacion del swipe del estudiante."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    empresa_id: int
    titulo: str
    descripcion: str
    requisitos: Optional[str] = None
    tipo_contrato: Optional[str] = None
    modalidad: str
    ubicacion: Optional[str] = None
    sueldo_minimo: Optional[float] = None
    sueldo_maximo: Optional[float] = None
    moneda: Optional[str] = None
    estado: str
    fecha_publicacion: datetime
    fecha_swipe: datetime
    interes_estudiante: bool


class VacanteMatchEstudiante(VacanteSwipeEstudiante):
    """Vacante donde hay match confirmado (ambos dieron like)."""

    fecha_match: datetime


class VacanteRechazadaPorEmpresa(VacanteSwipeEstudiante):
    """Vacante donde la empresa rechazo al estudiante."""

    fecha_rechazo_empresa: datetime


# --- Schema unificado de interacciones para estudiante ---


class VacanteInteraccionEstudiante(BaseModel):
    """Vacante con estado unificado de interacción para vista del estudiante."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    empresa_id: int
    titulo: str
    descripcion: str
    requisitos: Optional[str] = None
    tipo_contrato: Optional[str] = None
    modalidad: str
    ubicacion: Optional[str] = None
    sueldo_minimo: Optional[float] = None
    sueldo_maximo: Optional[float] = None
    moneda: Optional[str] = None
    estado: str
    fecha_publicacion: datetime

    # Estado de la interacción:
    # "pendiente"             – estudiante dio like, empresa no ha respondido
    # "match"                 – ambos dieron like
    # "rechazado"             – estudiante dio dislike a la vacante
    # "rechazado_por_empresa" – empresa dio dislike al estudiante
    # "prospecto"             – empresa dio like, estudiante aún no responde
    estado_interaccion: str
    fecha_interaccion: Optional[datetime] = None  # swipe del estudiante o empresa (el más reciente)
    fecha_match: Optional[datetime] = None


# --- Schemas para candidatos filtrados por estado (empresas) ---


class CandidatoEstadoItem(BaseModel):
    """Candidato con estado para visualizacion de empresa."""

    model_config = ConfigDict(from_attributes=True)

    estudiante_id: int
    email: str
    es_premium: bool
    fecha_registro: Optional[datetime] = None
    vacante_id: int
    vacante_titulo: str
    estado_candidato: str
    fecha_interaccion: Optional[datetime] = None
    perfil_estudiante: dict
