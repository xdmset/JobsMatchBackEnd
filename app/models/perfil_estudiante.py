from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class PerfilEstudiante(Base):
    __tablename__ = "perfiles_estudiantes"

    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True)
    nombre_completo = Column(String(255))
    institucion_educativa = Column(String(255))
    nivel_academico = Column(String(255))
    biografia = Column(Text)
    habilidades = Column(JSON) # RF-02
    cv_url = Column(String(255))
    cv_storage_key = Column(String(512))
    cv_tipo_archivo = Column(String(255))
    foto_perfil_url = Column(String(255))
    foto_perfil_storage_key = Column(String(512))
    fecha_nacimiento = Column(Date, nullable=True)
    ubicacion = Column(String(255))
    modalidad_preferida = Column(Enum('remoto', 'presencial', 'hibrido', name='modalidad_estudiante'))

    user = relationship("User", back_populates="perfil_estudiante")
