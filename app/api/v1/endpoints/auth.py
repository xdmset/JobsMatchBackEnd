from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import verify_password, create_access_token
from app.schemas.auth import Token
from app.models.user import User

router = APIRouter()


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
        )

    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
        )

    if not user.rol:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="El usuario no tiene rol asociado",
        )

    access_token = create_access_token(subject=str(user.id), role=user.rol.nombre)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
