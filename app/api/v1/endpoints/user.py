from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import ensure_roles, ensure_same_user, get_current_user, get_user_role
from app.core.enums import NombreRol
from app.core.security import get_password_hash, verify_password
from app.crud.crud_user import create_user, delete_user, get_user_by_email, get_users
from app.db.session import get_db
from app.models.user import User as UserModel
from app.schemas.user import PasswordChange, User, UserCreate, UserMe
from app.services.profile_media import serialize_empresa_profile, serialize_estudiante_profile
from app.services.user_registration import validate_role_profile_payload

router = APIRouter()

@router.get("/", response_model=list[User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    ensure_roles(current_user, NombreRol.admin.value)
    return get_users(db, skip=skip, limit=limit)


@router.get("/me", response_model=UserMe)
def read_me(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    perfil_estudiante = (
        serialize_estudiante_profile(user.perfil_estudiante) if user.perfil_estudiante else None
    )
    perfil_empresa = (
        serialize_empresa_profile(user.perfil_empresa) if user.perfil_empresa else None
    )

    return UserMe(
        id=user.id,
        email=user.email,
        rol_id=user.rol_id,
        rol=get_user_role(user),
        es_premium=user.es_premium,
        fecha_registro=user.fecha_registro,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        is_verified=user.is_verified,
        perfil_estudiante=perfil_estudiante,
        perfil_empresa=perfil_empresa,
    )

@router.post("/", response_model=User)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    validate_role_profile_payload(user)
    hashed_password = get_password_hash(user.password)
    return create_user(db, user, hashed_password)


@router.post("/me/password")
def change_password(
    payload: PasswordChange,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Password actual incorrecto")

    user.password_hash = get_password_hash(payload.new_password)
    db.commit()
    return {"detail": "Password actualizado"}

@router.delete("/{user_id}", response_model=User)
def remove_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    ensure_same_user(current_user, user_id)
    user = delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user
