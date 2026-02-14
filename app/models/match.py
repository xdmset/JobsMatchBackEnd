from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.db.base_class import Base


class Match(Base):
    __tablename__ = "matches"
    __table_args__ = (
        UniqueConstraint("estudiante_id", "vacante_id", name="uq_match_estudiante_vacante"),
    )

    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("perfiles_estudiantes.usuario_id"), nullable=False)
    vacante_id = Column(Integer, ForeignKey("vacantes.id"), nullable=False)
    fecha_match = Column(DateTime(timezone=True), server_default=func.now())
