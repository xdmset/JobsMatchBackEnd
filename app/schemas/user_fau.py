from fastapi_users import schemas

from app.schemas.perfil_empresa import PerfilEmpresaCreate
from app.schemas.perfil_estudiante import PerfilEstudianteCreate


class UserRead(schemas.BaseUser[int]):
    rol_id: int
    es_premium: bool


class UserCreate(schemas.BaseUserCreate):
    rol_id: int
    es_premium: bool = False
    perfil_estudiante: PerfilEstudianteCreate | None = None
    perfil_empresa: PerfilEmpresaCreate | None = None


class UserUpdate(schemas.BaseUserUpdate):
    rol_id: int | None = None
    es_premium: bool | None = None
