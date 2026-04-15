from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, synonym
from app.db.base_class import Base

class User(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    rol_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    # FastAPI Users expects `hashed_password`; map it to existing DB column `password_hash`.
    hashed_password = Column("password_hash", String(255), nullable=False)
    password_hash = synonym("hashed_password")

    is_active = Column(Boolean, default=True, server_default="1", nullable=False)
    is_superuser = Column(Boolean, default=False, server_default="0", nullable=False)
    is_verified = Column(Boolean, default=False, server_default="0", nullable=False)
    es_premium = Column(Boolean, default=False)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())
    fcm_token = Column(String(512), nullable=True)

    rol = relationship("Role", back_populates="usuarios")
    perfil_estudiante = relationship("PerfilEstudiante", back_populates="user", uselist=False, cascade="all, delete-orphan")
    perfil_empresa = relationship("PerfilEmpresa", back_populates="user", uselist=False, cascade="all, delete-orphan")
    suscripciones = relationship("Suscripcion", back_populates="usuario", cascade="all, delete-orphan")
