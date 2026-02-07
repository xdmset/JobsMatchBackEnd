from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.db.base_class import Base
from sqlalchemy.orm import relationship

class PerfilEmpresa(Base):
    __tablename__ = "perfiles_empresas"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer,ForeignKey("users.id"), unique=True, nullable=False)

    user = relationship("User", back_populates="perfil_empresa")

    nombre_comercial = Column(String(100), nullable=False)
    sector = Column(String(50))
    descripcion = Column(Text)
    sitio_web = Column(String(100))
    ubicacion_sede = Column(String(100))
