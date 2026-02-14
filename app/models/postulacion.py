from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum, Index
from sqlalchemy.sql import func
from app.db.base_class import Base


class Postulacion(Base):
    __tablename__ = "postulaciones"
    __table_args__ = (
        Index("idx_postulaciones_est_vac_estado", "estudiante_id", "vacante_id", "estado", "fecha_actualizacion"),
        Index("idx_postulaciones_empresa_estado", "empresa_id", "estado", "fecha_actualizacion"),
    )

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="CASCADE"), nullable=True)
    estudiante_id = Column(Integer, ForeignKey("perfiles_estudiantes.usuario_id"), nullable=False)
    vacante_id = Column(Integer, ForeignKey("vacantes.id"), nullable=False)
    empresa_id = Column(Integer, ForeignKey("perfiles_empresas.usuario_id"), nullable=False)
    source = Column(Enum('app_swipe', 'web_apply', name='source_postulacion'), nullable=False)
    estado = Column(Enum('enviado', 'visto', 'en_proceso', 'rechazado', 'aceptado', name='estado_postulacion'), default='enviado', nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
