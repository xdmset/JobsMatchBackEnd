from datetime import datetime
from typing import Optional

from pydantic import BaseModel, model_validator


def _validate_salary_range(sueldo_minimo: Optional[float], sueldo_maximo: Optional[float]) -> None:
    if (
        sueldo_minimo is not None
        and sueldo_maximo is not None
        and sueldo_minimo > sueldo_maximo
    ):
        raise ValueError("sueldo_minimo no puede ser mayor que sueldo_maximo")

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

    @model_validator(mode="after")
    def validate_salary_range(self):
        _validate_salary_range(self.sueldo_minimo, self.sueldo_maximo)
        return self

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

    @model_validator(mode="after")
    def validate_salary_range(self):
        _validate_salary_range(self.sueldo_minimo, self.sueldo_maximo)
        return self

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
