from datetime import date

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.v1.endpoints.swipes import get_company_candidate_feed, get_student_swipe_feed
from app.api.v1.endpoints.matches import read_student_match_history
from app.api.v1.endpoints.vacante import create_new_vacante
from app.api.v1.endpoints.vacante import update_existing_vacante
from app.core.enums import NombreRol
from app.crud.crud_vacante import create_vacante
from app.db.base import Base
from app.models.interaccion_swipe import InteraccionSwipe
from app.models.interaccion_swipe_empresa import InteraccionSwipeEmpresa
from app.models.match import Match
from app.models.perfil_empresa import PerfilEmpresa
from app.models.perfil_estudiante import PerfilEstudiante
from app.models.rol import Role
from app.models.suscripcion import Suscripcion
from app.models.user import User
from app.schemas.perfil_empresa import PerfilEmpresaCreate
from app.schemas.perfil_estudiante import PerfilEstudianteCreate
from app.schemas.vacante import VacanteCreate, VacanteUpdate
from app.services.paypal_service import get_default_paypal_plan_definitions
from app.services.subscription_service import build_plan_context, create_default_subscription_for_user


def _build_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def _seed_roles(db):
    rol_admin = Role(nombre=NombreRol.admin)
    rol_estudiante = Role(nombre=NombreRol.estudiante)
    rol_empresa = Role(nombre=NombreRol.empresa)
    db.add_all([rol_admin, rol_estudiante, rol_empresa])
    db.flush()
    return rol_admin, rol_estudiante, rol_empresa


def test_default_subscription_uses_user_role_scope():
    db = _build_db()
    try:
        _, _, rol_empresa = _seed_roles(db)
        empresa = User(email="empresa-plan@example.com", password_hash="hashed", rol_id=rol_empresa.id, rol=rol_empresa)
        db.add(empresa)
        db.flush()

        db.add(PerfilEmpresa(usuario_id=empresa.id, **PerfilEmpresaCreate(nombre_comercial="Empresa Plan").model_dump()))
        db.commit()

        suscripcion = create_default_subscription_for_user(db, empresa.id)

        assert suscripcion.tipo_plan == "free"
        assert suscripcion.rol_objetivo == "empresa"
        assert suscripcion.codigo_plan == "free_empresa"
    finally:
        db.close()


def test_build_plan_context_returns_expected_limits():
    db = _build_db()
    try:
        _, rol_estudiante, rol_empresa = _seed_roles(db)
        estudiante = User(email="student-plan@example.com", password_hash="hashed", rol_id=rol_estudiante.id, rol=rol_estudiante, es_premium=False)
        empresa = User(email="company-plan@example.com", password_hash="hashed", rol_id=rol_empresa.id, rol=rol_empresa, es_premium=True)
        db.add_all([estudiante, empresa])
        db.flush()

        student_context = build_plan_context(estudiante)
        company_context = build_plan_context(empresa)

        assert student_context.daily_swipes_limit == 10
        assert student_context.view_history_limit == 15
        assert student_context.match_history_limit == 10
        assert company_context.active_vacancies_limit == 50
        assert company_context.candidate_filter_level == "advanced"
        assert company_context.analytics_level == "advanced"
    finally:
        db.close()


def test_company_free_cannot_create_more_than_limit_of_active_vacancies():
    db = _build_db()
    try:
        _, _, rol_empresa = _seed_roles(db)
        empresa = User(email="company-limit@example.com", password_hash="hashed", rol_id=rol_empresa.id, rol=rol_empresa, es_premium=False)
        db.add(empresa)
        db.flush()
        db.add(PerfilEmpresa(usuario_id=empresa.id, nombre_comercial="Empresa Limite"))
        db.add(
            Suscripcion(
                usuario_id=empresa.id,
                tipo_plan="free",
                rol_objetivo="empresa",
                codigo_plan="free_empresa",
                fecha_inicio=date.today(),
            )
        )
        db.commit()

        payload = VacanteCreate(titulo="Vacante", descripcion="Desc", modalidad="remoto")
        for _ in range(5):
            create_new_vacante(empresa.id, payload, db=db, current_user=empresa)

        try:
            create_new_vacante(empresa.id, payload, db=db, current_user=empresa)
            assert False, "Se esperaba HTTPException por limite de vacantes"
        except HTTPException as exc:
            assert exc.status_code == 403
    finally:
        db.close()


def test_vacante_create_rejects_invalid_salary_range():
    with pytest.raises(ValidationError) as exc_info:
        VacanteCreate(
            titulo="Vacante",
            descripcion="Desc",
            modalidad="remoto",
            sueldo_minimo=20000,
            sueldo_maximo=10000,
        )

    assert "sueldo_minimo no puede ser mayor que sueldo_maximo" in str(exc_info.value)


def test_vacante_update_rejects_partial_invalid_salary_range():
    db = _build_db()
    try:
        _, _, rol_empresa = _seed_roles(db)
        empresa = User(email="salary-company@example.com", password_hash="hashed", rol_id=rol_empresa.id, rol=rol_empresa)
        db.add(empresa)
        db.flush()
        db.add(PerfilEmpresa(usuario_id=empresa.id, nombre_comercial="Empresa Salary"))
        db.commit()

        vacante = create_vacante(
            db,
            VacanteCreate(
                titulo="Vacante Salary",
                descripcion="Desc",
                modalidad="remoto",
                sueldo_minimo=10000,
                sueldo_maximo=15000,
            ),
            empresa.id,
        )

        with pytest.raises(HTTPException) as exc_info:
            update_existing_vacante(
                vacante.id,
                VacanteUpdate(sueldo_minimo=20000),
                db=db,
                current_user=empresa,
            )

        assert exc_info.value.status_code == 422
        assert exc_info.value.detail == "sueldo_minimo no puede ser mayor que sueldo_maximo"
    finally:
        db.close()


def test_student_match_history_is_limited_for_free_users():
    db = _build_db()
    try:
        _, rol_estudiante, rol_empresa = _seed_roles(db)
        estudiante = User(email="match-free@example.com", password_hash="hashed", rol_id=rol_estudiante.id, rol=rol_estudiante, es_premium=False)
        empresa = User(email="match-company@example.com", password_hash="hashed", rol_id=rol_empresa.id, rol=rol_empresa)
        db.add_all([estudiante, empresa])
        db.flush()
        db.add(
            PerfilEstudiante(
                usuario_id=estudiante.id,
                **PerfilEstudianteCreate(
                    nombre_completo="Ana",
                    institucion_educativa="UT",
                    nivel_academico="Licenciatura",
                    fecha_nacimiento=date(2002, 4, 10),
                ).model_dump()
            )
        )
        db.add(PerfilEmpresa(usuario_id=empresa.id, nombre_comercial="Empresa Match"))
        db.flush()

        for index in range(12):
            vacante = create_vacante(
                db,
                VacanteCreate(
                    titulo=f"Vacante {index}",
                    descripcion="Desc",
                    modalidad="remoto",
                ),
                empresa.id,
            )
            db.add(Match(estudiante_id=estudiante.id, vacante_id=vacante.id))
        db.commit()

        historial = read_student_match_history(estudiante.id, db=db, current_user=estudiante, limit=100)
        assert len(historial) == 10
    finally:
        db.close()


def test_paypal_catalog_contains_student_and_company_plans():
    definitions = get_default_paypal_plan_definitions()

    assert len(definitions) == 6
    assert {item.role_scope for item in definitions} == {"estudiante", "empresa"}


def test_company_candidate_feed_prioritizes_premium_and_excludes_already_swiped():
    db = _build_db()
    try:
        _, rol_estudiante, rol_empresa = _seed_roles(db)
        empresa = User(email="candidate-company@example.com", password_hash="hashed", rol_id=rol_empresa.id, rol=rol_empresa, es_premium=False)
        premium_student = User(email="premium-student@example.com", password_hash="hashed", rol_id=rol_estudiante.id, rol=rol_estudiante, es_premium=True)
        free_student = User(email="free-student@example.com", password_hash="hashed", rol_id=rol_estudiante.id, rol=rol_estudiante, es_premium=False)
        swiped_student = User(email="swiped-student@example.com", password_hash="hashed", rol_id=rol_estudiante.id, rol=rol_estudiante, es_premium=True)
        db.add_all([empresa, premium_student, free_student, swiped_student])
        db.flush()

        db.add(PerfilEmpresa(usuario_id=empresa.id, nombre_comercial="Empresa Feed"))
        for user, name in (
            (premium_student, "Premium"),
            (free_student, "Free"),
            (swiped_student, "Swiped"),
        ):
            db.add(
                PerfilEstudiante(
                    usuario_id=user.id,
                    **PerfilEstudianteCreate(
                        nombre_completo=name,
                        institucion_educativa="UT",
                        nivel_academico="Licenciatura",
                        fecha_nacimiento=date(2002, 4, 10),
                    ).model_dump()
                )
            )
        db.commit()

        vacante = create_vacante(
            db,
            VacanteCreate(
                titulo="Vacante Feed",
                descripcion="Desc",
                modalidad="remoto",
            ),
            empresa.id,
        )

        db.add(InteraccionSwipe(estudiante_id=premium_student.id, vacante_id=vacante.id, interes_estudiante=True))
        db.add(InteraccionSwipeEmpresa(empresa_id=empresa.id, estudiante_id=swiped_student.id, vacante_id=vacante.id, interes_empresa=False))
        db.commit()

        items = get_company_candidate_feed(empresa.id, vacante.id, db=db, current_user=empresa)

        assert [item.usuario_id for item in items] == [premium_student.id, free_student.id]
        assert items[0].es_premium is True
        assert items[0].ya_dio_like is True
    finally:
        db.close()


def test_admin_can_access_student_match_history_without_freemium_role_error():
    db = _build_db()
    try:
        rol_admin, rol_estudiante, _ = _seed_roles(db)
        admin = User(
            email="admin-history@example.com",
            password_hash="hashed",
            rol_id=rol_admin.id,
            rol=rol_admin,
            is_superuser=True,
        )
        estudiante = User(
            email="student-history@example.com",
            password_hash="hashed",
            rol_id=rol_estudiante.id,
            rol=rol_estudiante,
            es_premium=False,
        )
        db.add_all([admin, estudiante])
        db.flush()
        db.add(
            PerfilEstudiante(
                usuario_id=estudiante.id,
                **PerfilEstudianteCreate(
                    nombre_completo="Ana",
                    institucion_educativa="UT",
                    nivel_academico="Licenciatura",
                    fecha_nacimiento=date(2002, 4, 10),
                ).model_dump()
            )
        )
        db.commit()

        historial = read_student_match_history(estudiante.id, db=db, current_user=admin, limit=100)

        assert historial == []
    finally:
        db.close()


def test_student_swipe_feed_excludes_already_swiped_and_prioritizes_premium_companies():
    db = _build_db()
    try:
        _, rol_estudiante, rol_empresa = _seed_roles(db)
        estudiante = User(email="feed-student@example.com", password_hash="hashed", rol_id=rol_estudiante.id, rol=rol_estudiante)
        premium_company = User(email="premium-company@example.com", password_hash="hashed", rol_id=rol_empresa.id, rol=rol_empresa, es_premium=True)
        free_company = User(email="free-company@example.com", password_hash="hashed", rol_id=rol_empresa.id, rol=rol_empresa, es_premium=False)
        swiped_company = User(email="swiped-company@example.com", password_hash="hashed", rol_id=rol_empresa.id, rol=rol_empresa, es_premium=True)
        db.add_all([estudiante, premium_company, free_company, swiped_company])
        db.flush()

        db.add(
            PerfilEstudiante(
                usuario_id=estudiante.id,
                **PerfilEstudianteCreate(
                    nombre_completo="Ana",
                    institucion_educativa="UT",
                    nivel_academico="Licenciatura",
                    fecha_nacimiento=date(2002, 4, 10),
                ).model_dump()
            )
        )
        db.add_all(
            [
                PerfilEmpresa(usuario_id=premium_company.id, nombre_comercial="Premium Co"),
                PerfilEmpresa(usuario_id=free_company.id, nombre_comercial="Free Co"),
                PerfilEmpresa(usuario_id=swiped_company.id, nombre_comercial="Swiped Co"),
            ]
        )
        db.commit()

        premium_vacante = create_vacante(db, VacanteCreate(titulo="Premium", descripcion="Desc", modalidad="remoto"), premium_company.id)
        free_vacante = create_vacante(db, VacanteCreate(titulo="Free", descripcion="Desc", modalidad="remoto"), free_company.id)
        swiped_vacante = create_vacante(db, VacanteCreate(titulo="Swiped", descripcion="Desc", modalidad="remoto"), swiped_company.id)

        db.add(InteraccionSwipe(estudiante_id=estudiante.id, vacante_id=swiped_vacante.id, interes_estudiante=True))
        db.commit()

        items = get_student_swipe_feed(estudiante.id, db=db, current_user=estudiante)

        assert [item.id for item in items] == [premium_vacante.id, free_vacante.id]
    finally:
        db.close()
