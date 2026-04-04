from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.v1.endpoints.swipes import registrar_swipe, registrar_swipe_empresa
from app.core.enums import NombreRol
from app.crud.crud_vacante import create_vacante
from app.db.base import Base
from app.models.interaccion_swipe import InteraccionSwipe
from app.models.interaccion_swipe_empresa import InteraccionSwipeEmpresa
from app.models.match import Match
from app.models.perfil_empresa import PerfilEmpresa
from app.models.perfil_estudiante import PerfilEstudiante
from app.models.postulacion import Postulacion
from app.models.rol import Role
from app.models.user import User
from app.schemas.interaccion_swipe import SwipeCreate, SwipeEmpresaCreate
from app.schemas.perfil_empresa import PerfilEmpresaCreate
from app.schemas.perfil_estudiante import PerfilEstudianteCreate
from app.schemas.vacante import VacanteCreate


def _build_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def _seed_users_and_vacante(db):
    rol_estudiante = Role(nombre=NombreRol.estudiante)
    rol_empresa = Role(nombre=NombreRol.empresa)
    db.add_all([rol_estudiante, rol_empresa])
    db.flush()

    estudiante = User(
        email="student-swipe@example.com",
        password_hash="hashed",
        rol_id=rol_estudiante.id,
        rol=rol_estudiante,
    )
    empresa = User(
        email="company-swipe@example.com",
        password_hash="hashed",
        rol_id=rol_empresa.id,
        rol=rol_empresa,
    )
    db.add_all([estudiante, empresa])
    db.flush()

    db.add(
        PerfilEstudiante(
            usuario_id=estudiante.id,
            **PerfilEstudianteCreate(
                nombre_completo="Ana Swipe",
                institucion_educativa="UT",
                nivel_academico="Licenciatura",
                fecha_nacimiento=date(2002, 1, 10),
            ).model_dump()
        )
    )
    db.add(
        PerfilEmpresa(
            usuario_id=empresa.id,
            **PerfilEmpresaCreate(nombre_comercial="Empresa Swipe").model_dump()
        )
    )
    db.commit()

    vacante = create_vacante(
        db,
        VacanteCreate(
            titulo="Backend Jr",
            descripcion="FastAPI",
            modalidad="remoto",
        ),
        empresa.id,
    )
    return estudiante, empresa, vacante


def test_repeated_student_swipe_is_idempotent():
    db = _build_db()
    try:
        estudiante, _, vacante = _seed_users_and_vacante(db)

        first_response = registrar_swipe(
            estudiante.id,
            SwipeCreate(vacante_id=vacante.id, interes_estudiante=True),
            db=db,
            current_user=estudiante,
        )
        db.refresh(estudiante)

        swipe = db.query(InteraccionSwipe).filter(
            InteraccionSwipe.estudiante_id == estudiante.id,
            InteraccionSwipe.vacante_id == vacante.id,
        ).first()
        first_created_at = swipe.fecha
        first_updated_at = swipe.fecha_actualizacion

        second_response = registrar_swipe(
            estudiante.id,
            SwipeCreate(vacante_id=vacante.id, interes_estudiante=True),
            db=db,
            current_user=estudiante,
        )

        db.refresh(swipe)

        assert first_response is None
        assert second_response is None
        assert db.query(InteraccionSwipe).count() == 1
        assert swipe.fecha == first_created_at
        assert swipe.fecha_actualizacion == first_updated_at
    finally:
        db.close()


def test_student_can_edit_swipe_and_create_single_match_and_postulation():
    db = _build_db()
    try:
        estudiante, empresa, vacante = _seed_users_and_vacante(db)

        registrar_swipe(
            estudiante.id,
            SwipeCreate(vacante_id=vacante.id, interes_estudiante=False),
            db=db,
            current_user=estudiante,
        )
        registrar_swipe_empresa(
            empresa.id,
            SwipeEmpresaCreate(
                estudiante_id=estudiante.id,
                vacante_id=vacante.id,
                interes_empresa=True,
            ),
            db=db,
            current_user=empresa,
        )

        response = registrar_swipe(
            estudiante.id,
            SwipeCreate(vacante_id=vacante.id, interes_estudiante=True),
            db=db,
            current_user=estudiante,
        )

        repeated_response = registrar_swipe(
            estudiante.id,
            SwipeCreate(vacante_id=vacante.id, interes_estudiante=True),
            db=db,
            current_user=estudiante,
        )

        swipe = db.query(InteraccionSwipe).filter(
            InteraccionSwipe.estudiante_id == estudiante.id,
            InteraccionSwipe.vacante_id == vacante.id,
        ).first()

        assert response is not None
        assert repeated_response is not None
        assert repeated_response.id == response.id
        assert swipe.interes_estudiante is True
        assert db.query(Match).count() == 1
        assert db.query(Postulacion).count() == 1
    finally:
        db.close()


def test_repeated_company_swipe_is_idempotent():
    db = _build_db()
    try:
        estudiante, empresa, vacante = _seed_users_and_vacante(db)

        first_response = registrar_swipe_empresa(
            empresa.id,
            SwipeEmpresaCreate(
                estudiante_id=estudiante.id,
                vacante_id=vacante.id,
                interes_empresa=True,
            ),
            db=db,
            current_user=empresa,
        )

        swipe = db.query(InteraccionSwipeEmpresa).filter(
            InteraccionSwipeEmpresa.empresa_id == empresa.id,
            InteraccionSwipeEmpresa.estudiante_id == estudiante.id,
            InteraccionSwipeEmpresa.vacante_id == vacante.id,
        ).first()
        first_created_at = swipe.fecha
        first_updated_at = swipe.fecha_actualizacion

        second_response = registrar_swipe_empresa(
            empresa.id,
            SwipeEmpresaCreate(
                estudiante_id=estudiante.id,
                vacante_id=vacante.id,
                interes_empresa=True,
            ),
            db=db,
            current_user=empresa,
        )

        db.refresh(swipe)

        assert first_response is None
        assert second_response is None
        assert db.query(InteraccionSwipeEmpresa).count() == 1
        assert swipe.fecha == first_created_at
        assert swipe.fecha_actualizacion == first_updated_at
    finally:
        db.close()
