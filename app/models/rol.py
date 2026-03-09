from sqlalchemy import Column, Enum, Integer
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.core.enums import NombreRol


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(
        Enum(
            NombreRol,
            name="nombre_rol",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        unique=True,
        nullable=False,
    )

    usuarios = relationship("User", back_populates="rol")
