from pydantic import BaseModel
from datetime import datetime


class MatchResponse(BaseModel):
    id: int
    estudiante_id: int
    vacante_id: int
    fecha_match: datetime

    class Config:
        from_attributes = True
