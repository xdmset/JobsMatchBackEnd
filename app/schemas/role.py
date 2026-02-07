from pydantic import BaseModel

class Role(BaseModel):
    id: int
    nombre: str

    class Config:
        from_attributes = True
