from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import ensure_roles, ensure_same_user, get_current_user
from app.core.enums import NombreRol
from app.core.security import get_password_hash
from app.crud.crud_user import create_user, delete_user, get_user_by_email, get_users
from app.db.session import get_db
from app.models.user import User as UserModel
from app.schemas.user import User, UserCreate
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

@router.post("/", response_model=User)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    validate_role_profile_payload(user)
    hashed_password = get_password_hash(user.password)
    return create_user(db, user, hashed_password)

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
