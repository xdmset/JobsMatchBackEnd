from pydantic import BaseModel


class SwipeCreate(BaseModel):
    vacante_id: int
    interes_estudiante: bool


class SwipeEmpresaCreate(BaseModel):
    estudiante_id: int
    vacante_id: int
    interes_empresa: bool
