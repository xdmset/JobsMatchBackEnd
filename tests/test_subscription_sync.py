from datetime import date, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.crud.crud_suscripcion import update_suscripcion
from app.db.base import Base
from app.models.rol import Role
from app.models.suscripcion import Suscripcion
from app.models.user import User
from app.core.enums import NombreRol
from app.schemas.suscripcion import SuscripcionUpdate


def test_update_subscription_marks_user_premium_when_legacy_end_date_is_expired():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        role = Role(nombre=NombreRol.estudiante)
        db.add(role)
        db.flush()

        user = User(
            email="premium-sync@example.com",
            password_hash="hashed",
            rol_id=role.id,
            es_premium=False,
        )
        db.add(user)
        db.flush()

        subscription = Suscripcion(
            usuario_id=user.id,
            tipo_plan="free",
            fecha_inicio=date.today() - timedelta(days=30),
            fecha_fin=date.today() - timedelta(days=1),
        )
        db.add(subscription)
        db.commit()

        updated = update_suscripcion(
            db,
            subscription.id,
            SuscripcionUpdate(tipo_plan="premium"),
        )

        db.refresh(user)

        assert updated is not None
        assert updated.tipo_plan == "premium"
        assert updated.fecha_fin is None
        assert user.es_premium is True
    finally:
        db.close()
