from typing import Optional

from pydantic import BaseModel

from app.core.enums import NombreRol


class RoleBase(BaseModel):
    nombre: NombreRol


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    nombre: Optional[NombreRol] = None


class Role(RoleBase):
    id: int

    class Config:
        from_attributes = True
