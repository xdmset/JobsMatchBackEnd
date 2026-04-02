from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.crud.crud_suscripcion import update_suscripcion
from app.db.base import Base
from app.models.plan import Plan
from app.models.rol import Role
from app.models.suscripcion import Suscripcion
from app.models.user import User
from app.core.enums import NombreRol
from app.schemas.suscripcion import SuscripcionUpdate
from app.services.subscription_service import (
    create_default_subscription_for_user,
    create_or_update_paypal_subscription,
    get_current_subscription,
    sync_all_users_premium_status,
    sync_user_premium_status,
)


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


def test_paypal_pending_subscription_does_not_mark_user_as_premium():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        role = Role(nombre=NombreRol.estudiante)
        db.add(role)
        db.flush()

        user = User(
            email="paypal-pending@example.com",
            password_hash="hashed",
            rol_id=role.id,
            es_premium=False,
        )
        db.add(user)
        db.flush()

        plan = Plan(
            codigo="mensual",
            nombre="Premium Mensual",
            paypal_product_id="PROD-123",
            paypal_plan_id="P-123",
            moneda="USD",
            precio=Decimal("9.99"),
            intervalo_unidad="MONTH",
            intervalo_conteo=1,
            activo=True,
        )
        db.add(plan)
        db.flush()

        create_or_update_paypal_subscription(
            db,
            usuario_id=user.id,
            plan=plan,
            paypal_subscription_id="I-123",
            paypal_plan_id="P-123",
            estado_externo="APPROVAL_PENDING",
            fecha_inicio=date.today(),
            fecha_fin=None,
            payload={"id": "I-123", "status": "APPROVAL_PENDING"},
        )
        db.commit()
        db.refresh(user)

        assert user.es_premium is False
    finally:
        db.close()


def test_paypal_active_subscription_marks_user_as_premium():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        role = Role(nombre=NombreRol.estudiante)
        db.add(role)
        db.flush()

        user = User(
            email="paypal-active@example.com",
            password_hash="hashed",
            rol_id=role.id,
            es_premium=False,
        )
        db.add(user)
        db.flush()

        plan = Plan(
            codigo="anual",
            nombre="Premium Anual",
            paypal_product_id="PROD-123",
            paypal_plan_id="P-999",
            moneda="USD",
            precio=Decimal("89.99"),
            intervalo_unidad="MONTH",
            intervalo_conteo=12,
            activo=True,
        )
        db.add(plan)
        db.flush()

        create_or_update_paypal_subscription(
            db,
            usuario_id=user.id,
            plan=plan,
            paypal_subscription_id="I-999",
            paypal_plan_id="P-999",
            estado_externo="ACTIVE",
            fecha_inicio=date.today(),
            fecha_fin=None,
            payload={"id": "I-999", "status": "ACTIVE"},
        )
        db.commit()
        db.refresh(user)

        assert user.es_premium is True
    finally:
        db.close()


def test_paypal_cancelled_subscription_keeps_premium_until_end_date():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        role = Role(nombre=NombreRol.estudiante)
        db.add(role)
        db.flush()

        user = User(
            email="paypal-cancelled@example.com",
            password_hash="hashed",
            rol_id=role.id,
            es_premium=False,
        )
        db.add(user)
        db.flush()

        plan = Plan(
            codigo="mensual",
            nombre="Premium Mensual",
            paypal_product_id="PROD-123",
            paypal_plan_id="P-321",
            moneda="USD",
            precio=Decimal("9.99"),
            intervalo_unidad="MONTH",
            intervalo_conteo=1,
            activo=True,
        )
        db.add(plan)
        db.flush()

        create_or_update_paypal_subscription(
            db,
            usuario_id=user.id,
            plan=plan,
            paypal_subscription_id="I-321",
            paypal_plan_id="P-321",
            estado_externo="CANCELLED",
            fecha_inicio=date.today() - timedelta(days=10),
            fecha_fin=date.today() + timedelta(days=20),
            payload={"id": "I-321", "status": "CANCELLED"},
        )
        db.commit()
        db.refresh(user)

        assert user.es_premium is True
    finally:
        db.close()


def test_create_default_subscription_for_user_does_not_duplicate_free_subscription():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        role = Role(nombre=NombreRol.estudiante)
        db.add(role)
        db.flush()

        user = User(
            email="free-default@example.com",
            password_hash="hashed",
            rol_id=role.id,
            es_premium=False,
        )
        db.add(user)
        db.flush()

        first = create_default_subscription_for_user(db, user.id)
        second = create_default_subscription_for_user(db, user.id)
        db.commit()

        subscriptions = db.query(Suscripcion).filter(Suscripcion.usuario_id == user.id).all()

        assert first.id == second.id
        assert len(subscriptions) == 1
        assert subscriptions[0].tipo_plan == "free"
    finally:
        db.close()


def test_get_current_subscription_returns_free_when_no_premium_is_active():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        role = Role(nombre=NombreRol.estudiante)
        db.add(role)
        db.flush()

        user = User(
            email="current-free@example.com",
            password_hash="hashed",
            rol_id=role.id,
            es_premium=False,
        )
        db.add(user)
        db.flush()

        free_subscription = create_default_subscription_for_user(db, user.id)
        db.commit()

        current = get_current_subscription(db, user.id)

        assert current is not None
        assert current.id == free_subscription.id
        assert current.tipo_plan == "free"
    finally:
        db.close()


def test_sync_user_premium_status_turns_off_expired_manual_premium():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        role = Role(nombre=NombreRol.estudiante)
        db.add(role)
        db.flush()

        user = User(
            email="expired-premium@example.com",
            password_hash="hashed",
            rol_id=role.id,
            es_premium=True,
        )
        db.add(user)
        db.flush()

        db.add(
            Suscripcion(
                usuario_id=user.id,
                tipo_plan="premium",
                fecha_inicio=date.today() - timedelta(days=60),
                fecha_fin=date.today() - timedelta(days=1),
            )
        )
        db.commit()

        sync_user_premium_status(db, user.id)
        db.commit()
        db.refresh(user)

        assert user.es_premium is False
    finally:
        db.close()


def test_sync_all_users_premium_status_returns_number_of_updated_users():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        role = Role(nombre=NombreRol.estudiante)
        db.add(role)
        db.flush()

        expired_user = User(
            email="bulk-expired@example.com",
            password_hash="hashed",
            rol_id=role.id,
            es_premium=True,
        )
        active_user = User(
            email="bulk-active@example.com",
            password_hash="hashed",
            rol_id=role.id,
            es_premium=False,
        )
        db.add_all([expired_user, active_user])
        db.flush()

        db.add(
            Suscripcion(
                usuario_id=expired_user.id,
                tipo_plan="premium",
                fecha_inicio=date.today() - timedelta(days=30),
                fecha_fin=date.today() - timedelta(days=1),
            )
        )
        db.add(
            Suscripcion(
                usuario_id=active_user.id,
                tipo_plan="premium",
                fecha_inicio=date.today() - timedelta(days=1),
                fecha_fin=date.today() + timedelta(days=30),
            )
        )
        db.commit()

        updated_count = sync_all_users_premium_status(db)
        db.commit()
        db.refresh(expired_user)
        db.refresh(active_user)

        assert updated_count == 2
        assert expired_user.es_premium is False
        assert active_user.es_premium is True
    finally:
        db.close()
