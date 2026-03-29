from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class VacanteBase(BaseModel):
    titulo: str
    descripcion: str
    requisitos: Optional[str] = None
    tipo_contrato: Optional[str] = None
    modalidad: str
    ubicacion: Optional[str] = None
    sueldo_minimo: Optional[float] = None
    sueldo_maximo: Optional[float] = None
    moneda: Optional[str] = None
    estado: Optional[str] = None

class VacanteCreate(VacanteBase):
    pass


class VacanteUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    requisitos: Optional[str] = None
    tipo_contrato: Optional[str] = None
    modalidad: Optional[str] = None
    ubicacion: Optional[str] = None
    sueldo_minimo: Optional[float] = None
    sueldo_maximo: Optional[float] = None
    moneda: Optional[str] = None
    estado: Optional[str] = None

class Vacante(VacanteBase):
    id: int
    empresa_id: int
    estado: str
    fecha_publicacion: datetime

    class Config:
        from_attributes = True


class VacanteHistorialEstudiante(Vacante):
    primera_visualizacion: datetime
    ultima_visualizacion: datetime
    total_visualizaciones: int
    le_dio_like: bool
    fecha_like: Optional[datetime] = None


class VacanteHistorialEmpresa(Vacante):
    total_visualizaciones: int
    total_estudiantes_que_vieron: int
    total_likes_estudiantes: int
    total_likes_empresa: int
    total_matches: int
    ultima_visualizacion: Optional[datetime] = None
    ultimo_like_estudiante: Optional[datetime] = None
    ultimo_like_empresa: Optional[datetime] = None
