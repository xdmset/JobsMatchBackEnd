from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class User(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    rol_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    es_premium = Column(Boolean, default=False)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())

    rol = relationship("Role", back_populates="usuarios")
    perfil_estudiante = relationship("PerfilEstudiante", back_populates="user", uselist=False, cascade="all, delete-orphan")
    perfil_empresa = relationship("PerfilEmpresa", back_populates="user", uselist=False, cascade="all, delete-orphan")