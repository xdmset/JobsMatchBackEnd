from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    es_premium: bool = False

class UserCreate(UserBase):
    password: str
    rol_id: int

class User(UserBase):
    id: int
    rol_id: int
    fecha_registro: datetime

    class Config:
        from_attributes = True
