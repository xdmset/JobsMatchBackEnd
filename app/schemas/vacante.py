from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VacanteBase(BaseModel):
    titulo: str
    descripcion: str
    requisitos: Optional[str] = None
    modalidad: str
    ubicacion: Optional[str] = None
    sueldo_minimo: Optional[float] = None
    sueldo_maximo: Optional[float] = None

class VacanteCreate(VacanteBase):
    pass

class Vacante(VacanteBase):
    id: int
    empresa_id: int
    estado: str
    fecha_publicacion: datetime

    class Config:
        from_attributes = True
