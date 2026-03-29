from datetime import date

from pydantic import BaseModel
from typing import Optional, Any

class PerfilEstudianteBase(BaseModel):
    nombre_completo: str
    institucion_educativa: str
    nivel_academico: str
    biografia: Optional[str] = None
    habilidades: Optional[Any] = None  # Cambiado a Any para soportar el JSON de MySQL
    ubicacion: Optional[str] = None
    modalidad_preferida: Optional[str] = None

class PerfilEstudianteCreate(PerfilEstudianteBase):
    fecha_nacimiento: date

class PerfilEstudiante(PerfilEstudianteBase):
    usuario_id: int  # Modificado: de user_id a usuario_id
    fecha_nacimiento: Optional[date] = None
    cv_url: Optional[str] = None
    cv_tipo_archivo: Optional[str] = None
    foto_perfil_url: Optional[str] = None

    class Config:
        from_attributes = True
