from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class PerfilEmpresa(Base):
    __tablename__ = "perfiles_empresas"

    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True)
    nombre_comercial = Column(String(255), nullable=False)
    sector = Column(String(255))
    descripcion = Column(Text)
    sitio_web = Column(String(255))
    ubicacion_sede = Column(String(255))

    user = relationship("User", back_populates="perfil_empresa")
    vacantes = relationship("Vacante", back_populates="empresa")