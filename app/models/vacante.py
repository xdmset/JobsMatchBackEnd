from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base_class import Base

class Vacante(Base):
    __tablename__ = "vacantes"

    id = Column(Integer, primary_key=True, index=True)

    empresa_id = Column(
        Integer,
        ForeignKey("perfiles_empresas.user_id"),
        nullable=False
    )

    titulo = Column(String(100), nullable=False)
    descripcion = Column(Text)
    requisitos = Column(Text)
    modalidad = Column(String(50))
    ubicacion = Column(String(100))
    sueldo_minimo = Column(Float)
    sueldo_maximo = Column(Float)
    estado = Column(String(20), default="activa")
    fecha_publicacion = Column(DateTime(timezone=True), server_default=func.now())
