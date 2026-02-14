from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.sql import func
from app.db.base_class import Base


class InteraccionSwipe(Base):
    __tablename__ = "interacciones_swipe"
    __table_args__ = (
        UniqueConstraint("estudiante_id", "vacante_id", name="uq_swipe_estudiante_vacante"),
    )

    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("perfiles_estudiantes.usuario_id"), nullable=False)
    vacante_id = Column(Integer, ForeignKey("vacantes.id"), nullable=False)
    interes_estudiante = Column(Boolean, nullable=False)
    fecha = Column(DateTime(timezone=True), server_default=func.now())
