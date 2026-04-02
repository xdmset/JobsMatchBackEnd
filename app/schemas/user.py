from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.schemas.perfil_estudiante import PerfilEstudianteCreate
from app.schemas.perfil_empresa import PerfilEmpresaCreate
from app.schemas.perfil_estudiante import PerfilEstudiante
from app.schemas.perfil_empresa import PerfilEmpresa

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    rol_id: int
    perfil_estudiante: Optional[PerfilEstudianteCreate] = None
    perfil_empresa: Optional[PerfilEmpresaCreate] = None

class User(UserBase):
    id: int
    rol_id: int
    es_premium: bool
    fecha_registro: datetime

    class Config:
        from_attributes = True

class UserMe(User):
    rol: Optional[str] = None
    is_active: bool
    is_superuser: bool
    is_verified: bool
    perfil_estudiante: Optional[PerfilEstudiante] = None
    perfil_empresa: Optional[PerfilEmpresa] = None


class PremiumSyncResponse(BaseModel):
    updated_users: int


class PasswordChange(BaseModel):
    current_password: str
    new_password: str
