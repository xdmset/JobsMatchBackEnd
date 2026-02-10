from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class InteraccionSwipe(Base):
    __tablename__ = "interacciones_swipe"
    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("perfiles_estudiantes.usuario_id"))
    vacante_id = Column(Integer, ForeignKey("vacantes.id"))
    interes_estudiante = Column(Boolean)
    fecha = Column(DateTime(timezone=True), server_default=func.now())

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("perfiles_estudiantes.usuario_id"))
    vacante_id = Column(Integer, ForeignKey("vacantes.id"))
    fecha_match = Column(DateTime(timezone=True), server_default=func.now())

class Postulacion(Base):
    __tablename__ = "postulaciones"
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="CASCADE"))
    estado = Column(Enum('enviado', 'visto', 'en_proceso', 'rechazado', name='estado_postulacion'), default='enviado')
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

class Retroalimentacion(Base):
    __tablename__ = "retroalimentacion"
    id = Column(Integer, primary_key=True, index=True)
    postulacion_id = Column(Integer, ForeignKey("postulaciones.id"))
    campos_mejora = Column(Text) # RF-11
    sugerencias_perfil = Column(Text) # RF-12
    fecha_envio = Column(DateTime(timezone=True), server_default=func.now())