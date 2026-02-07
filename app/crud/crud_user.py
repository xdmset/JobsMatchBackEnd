from sqlalchemy.orm import Session
from app.models.user import User
from app.models.perfil_estudiante import PerfilEstudiante
from app.models.perfil_empresa import PerfilEmpresa
from app.schemas.user import UserCreate
from app.core.constants import ROL_ESTUDIANTE, ROL_EMPRESA

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate, hashed_password: str):
    db_user = User(
        email=user.email,
        password_hash=hashed_password,
        rol_id=user.rol_id,
        es_premium=user.es_premium
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    if user.rol_id == ROL_ESTUDIANTE:
        perfil = PerfilEstudiante(user_id=db_user.id, nombre_completo="", institucion_educativa="", nivel_academico="")
        db.add(perfil)

    elif user.rol_id == ROL_EMPRESA:
        perfil = PerfilEmpresa(user_id=db_user.id, nombre_comercial="")
        db.add(perfil)

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user
