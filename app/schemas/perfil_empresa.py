from pydantic import BaseModel
from typing import Optional

class PerfilEmpresaBase(BaseModel):
    nombre_comercial: str
    sector: Optional[str] = None
    descripcion: Optional[str] = None
    sitio_web: Optional[str] = None
    ubicacion_sede: Optional[str] = None

class PerfilEmpresaCreate(PerfilEmpresaBase):
    pass

class PerfilEmpresa(PerfilEmpresaBase):
    usuario_id: int  # Modificado: de user_id a usuario_id

    class Config:
        from_attributes = True