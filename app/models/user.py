from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base_class import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(200), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    rol_id = Column(Integer, ForeignKey("roles.id"),nullable=False)

    rol = relationship("Role", back_populates="usuarios")

    perfil_estudiante = relationship("PerfilEstudiante",back_populates="user",uselist=False)
    perfil_empresa = relationship("PerfilEmpresa",back_populates="user",uselist=False)

    es_premium = Column(Boolean, default=False)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())
