from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.enums import NombreRol
from app.crud.crud_swipe import upsert_swipe_empresa, upsert_swipe_estudiante
from app.crud.crud_vacante import (
    create_vacante,
    get_historial_vacantes_empresa,
    get_historial_vacantes_estudiante,
    registrar_visualizacion_vacante,
)
from app.db.base import Base
from app.models.perfil_empresa import PerfilEmpresa
from app.models.perfil_estudiante import PerfilEstudiante
from app.models.rol import Role
from app.models.user import User
from app.schemas.perfil_empresa import PerfilEmpresaCreate
from app.schemas.perfil_estudiante import PerfilEstudianteCreate
from app.schemas.vacante import VacanteCreate


def test_historial_estudiante_includes_views_likes_and_birth_date():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        rol_estudiante = Role(nombre=NombreRol.estudiante)
        rol_empresa = Role(nombre=NombreRol.empresa)
        db.add_all([rol_estudiante, rol_empresa])
        db.flush()

        estudiante = User(email="student-history@example.com", password_hash="hashed", rol_id=rol_estudiante.id)
        empresa = User(email="company-history@example.com", password_hash="hashed", rol_id=rol_empresa.id)
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
        db.add(
            PerfilEmpresa(
                usuario_id=empresa.id,
                **PerfilEmpresaCreate(
                    nombre_comercial="Empresa X",
                ).model_dump()
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

        registrar_visualizacion_vacante(db, estudiante.id, vacante.id)
        registrar_visualizacion_vacante(db, estudiante.id, vacante.id)
        upsert_swipe_estudiante(db, estudiante.id, vacante.id, True)
        db.commit()

        historial = get_historial_vacantes_estudiante(db, estudiante.id)

        assert len(historial) == 1
        item = historial[0]
        assert item.id == vacante.id
        assert item.total_visualizaciones == 2
        assert item.le_dio_like is True
        assert item.fecha_like is not None
    finally:
        db.close()


def test_historial_empresa_aggregates_views_and_likes():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        rol_estudiante = Role(nombre=NombreRol.estudiante)
        rol_empresa = Role(nombre=NombreRol.empresa)
        db.add_all([rol_estudiante, rol_empresa])
        db.flush()

        empresa = User(email="company-agg@example.com", password_hash="hashed", rol_id=rol_empresa.id)
        estudiante = User(email="student-agg@example.com", password_hash="hashed", rol_id=rol_estudiante.id)
        db.add_all([empresa, estudiante])
        db.flush()

        db.add(PerfilEmpresa(usuario_id=empresa.id, nombre_comercial="Empresa Y"))
        db.add(PerfilEstudiante(usuario_id=estudiante.id, nombre_completo="Luis"))
        db.commit()

        vacante = create_vacante(
            db,
            VacanteCreate(
                titulo="Frontend Jr",
                descripcion="React",
                modalidad="hibrido",
            ),
            empresa.id,
        )

        registrar_visualizacion_vacante(db, estudiante.id, vacante.id)
        upsert_swipe_estudiante(db, estudiante.id, vacante.id, True)
        upsert_swipe_empresa(db, empresa.id, estudiante.id, vacante.id, True)
        db.commit()

        historial = get_historial_vacantes_empresa(db, empresa.id)

        assert len(historial) == 1
        item = historial[0]
        assert item.id == vacante.id
        assert item.total_visualizaciones == 1
        assert item.total_estudiantes_que_vieron == 1
        assert item.total_likes_estudiantes == 1
        assert item.total_likes_empresa == 1
    finally:
        db.close()
