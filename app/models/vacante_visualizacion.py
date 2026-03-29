from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func

from app.db.base_class import Base


class VacanteVisualizacion(Base):
    __tablename__ = "vacantes_visualizaciones"
    __table_args__ = (
        UniqueConstraint("estudiante_id", "vacante_id", name="uq_visualizacion_estudiante_vacante"),
    )

    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("perfiles_estudiantes.usuario_id"), nullable=False)
    vacante_id = Column(Integer, ForeignKey("vacantes.id"), nullable=False)
    primera_visualizacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ultima_visualizacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    total_visualizaciones = Column(Integer, nullable=False, default=1, server_default="1")
