from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey
from app.db.base_class import Base
from sqlalchemy.orm import relationship

class PerfilEstudiante(Base):
    __tablename__ = "perfiles_estudiantes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer,ForeignKey("users.id"), unique=True, nullable=False)

    user = relationship("User", back_populates="perfil_estudiante")

    nombre_completo = Column(String(100), nullable=False)
    institucion_educativa = Column(String(100))
    nivel_academico = Column(String(100))
    biografia = Column(Text)
    habilidades = Column(JSON)
    ubicacion = Column(String(100))
    modalidad_preferida = Column(String(50))
