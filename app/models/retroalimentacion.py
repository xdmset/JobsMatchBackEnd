from sqlalchemy import Column, Integer, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.sql import func
from app.db.base_class import Base


class Retroalimentacion(Base):
    __tablename__ = "retroalimentacion"
    __table_args__ = (
        UniqueConstraint("postulacion_id", name="uq_retro_postulacion"),
    )

    id = Column(Integer, primary_key=True, index=True)
    postulacion_id = Column(Integer, ForeignKey("postulaciones.id"), nullable=False)
    campos_mejora = Column(Text)
    sugerencias_perfil = Column(Text)
    fecha_envio = Column(DateTime(timezone=True), server_default=func.now())
