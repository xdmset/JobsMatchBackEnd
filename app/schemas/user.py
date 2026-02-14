from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.schemas.perfil_estudiante import PerfilEstudianteCreate
from app.schemas.perfil_empresa import PerfilEmpresaCreate

class UserBase(BaseModel):
    email: EmailStr
    es_premium: bool = False

class UserCreate(UserBase):
    password: str
    rol_id: int
    perfil_estudiante: Optional[PerfilEstudianteCreate] = None
    perfil_empresa: Optional[PerfilEmpresaCreate] = None

class User(UserBase):
    id: int
    rol_id: int
    fecha_registro: datetime

    class Config:
        from_attributes = True
