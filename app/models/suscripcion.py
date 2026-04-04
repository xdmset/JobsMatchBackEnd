from sqlalchemy import Column, Date, Enum, ForeignKey, Integer, Numeric, String, Text
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
    rol_objetivo = Column(
        Enum("estudiante", "empresa", name="rol_objetivo_suscripcion"),
        nullable=False,
    )
    codigo_plan = Column(String(64), nullable=True)
    origen_pago = Column(
        Enum("manual", "paypal", name="origen_pago_suscripcion"),
        nullable=False,
        default="manual",
        server_default="manual",
    )
    fecha_inicio = Column(Date, nullable=True)
    fecha_fin = Column(Date, nullable=True)
    paypal_plan_id = Column(String(64), nullable=True)
    paypal_subscription_id = Column(String(64), unique=True, nullable=True)
    estado_externo = Column(String(64), nullable=True)
    moneda = Column(String(3), nullable=True)
    monto = Column(Numeric(10, 2), nullable=True)
    detalle_externo = Column(Text, nullable=True)

    usuario = relationship("User", back_populates="suscripciones")
