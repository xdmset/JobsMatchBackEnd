from sqlalchemy import Boolean, Column, Enum, Integer, Numeric, String

from app.db.base_class import Base


class Plan(Base):
    __tablename__ = "planes"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(
        Enum("mensual", "semestral", "anual", name="codigo_plan_paypal"),
        unique=True,
        nullable=False,
    )
    nombre = Column(String(100), nullable=False)
    paypal_product_id = Column(String(64), nullable=False)
    paypal_plan_id = Column(String(64), unique=True, nullable=False, index=True)
    moneda = Column(String(3), nullable=False)
    precio = Column(Numeric(10, 2), nullable=False)
    intervalo_unidad = Column(String(16), nullable=False)
    intervalo_conteo = Column(Integer, nullable=False)
    activo = Column(Boolean, nullable=False, default=True, server_default="1")
