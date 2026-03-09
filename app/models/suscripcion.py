from sqlalchemy import Column, Date, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Suscripcion(Base):
    __tablename__ = "suscripciones"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    tipo_plan = Column(
        Enum("free", "premium", name="tipo_plan_suscripcion"),
        nullable=False,
    )
    fecha_inicio = Column(Date, nullable=True)
    fecha_fin = Column(Date, nullable=True)

    usuario = relationship("User", back_populates="suscripciones")
