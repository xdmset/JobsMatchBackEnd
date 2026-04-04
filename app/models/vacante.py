from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Vacante(Base):
    __tablename__ = "vacantes"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("perfiles_empresas.usuario_id"), nullable=False)
    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text)
    requisitos = Column(Text)
    tipo_contrato = Column(String(255))
    modalidad = Column(Enum('remoto', 'presencial', 'hibrido', name='modalidad_vacante'))
    ubicacion = Column(String(255))
    sueldo_minimo = Column(Numeric(10, 2))
    sueldo_maximo = Column(Numeric(10, 2))
    moneda = Column(String(255), default="MXN")
    estado = Column(Enum('activa', 'pausada', 'cerrada', name='estado_vacante'), default="activa")
    fecha_publicacion = Column(DateTime(timezone=True), server_default=func.now())

    empresa = relationship("PerfilEmpresa", back_populates="vacantes")
