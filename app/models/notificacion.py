from sqlalchemy import Boolean, Column, Enum, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func

from app.db.base_class import Base


class Notificacion(Base):
    __tablename__ = "notificaciones"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)

    tipo = Column(
        Enum(
            "like_recibido",
            "match",
            "postulacion_estado",
            name="tipo_notificacion",
        ),
        nullable=False,
    )

    titulo = Column(String(255), nullable=False)
    mensaje = Column(Text, nullable=False)

    # Referencias opcionales para navegación en el frontend
    vacante_id = Column(Integer, ForeignKey("vacantes.id", ondelete="SET NULL"), nullable=True)
    postulacion_id = Column(Integer, ForeignKey("postulaciones.id", ondelete="SET NULL"), nullable=True)
    estudiante_id = Column(Integer, ForeignKey("perfiles_estudiantes.usuario_id", ondelete="SET NULL"), nullable=True)

    leida = Column(Boolean, default=False, nullable=False, index=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    fecha_leida = Column(DateTime(timezone=True), nullable=True)
