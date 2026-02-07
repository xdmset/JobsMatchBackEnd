from pydantic import BaseModel
from typing import Optional, Dict

class PerfilEstudianteBase(BaseModel):
    nombre_completo: str
    institucion_educativa: str
    nivel_academico: str
    biografia: Optional[str] = None
    habilidades: Optional[Dict] = None
    ubicacion: Optional[str] = None
    modalidad_preferida: Optional[str] = None

class PerfilEstudianteCreate(PerfilEstudianteBase):
    pass

class PerfilEstudiante(PerfilEstudianteBase):
    user_id: int

    class Config:
        from_attributes = True
