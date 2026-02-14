from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.sql import func
from app.db.base_class import Base


class InteraccionSwipeEmpresa(Base):
    __tablename__ = "interacciones_swipe_empresa"
    __table_args__ = (
        UniqueConstraint("empresa_id", "estudiante_id", "vacante_id", name="uq_swipe_empresa_tripleta"),
    )

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("perfiles_empresas.usuario_id"), nullable=False)
    estudiante_id = Column(Integer, ForeignKey("perfiles_estudiantes.usuario_id"), nullable=False)
    vacante_id = Column(Integer, ForeignKey("vacantes.id"), nullable=False)
    interes_empresa = Column(Boolean, nullable=False)
    fecha = Column(DateTime(timezone=True), server_default=func.now())
