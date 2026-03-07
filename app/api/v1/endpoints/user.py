from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.crud.crud_user import get_user, get_user_by_email, get_users, create_user, delete_user
from app.schemas.user import User, UserCreate
from app.core.security import get_password_hash
from app.services.user_registration import validate_role_profile_payload

router = APIRouter() # ESTA LÍNEA ES LA QUE GENERABA EL NAMEERROR

@router.get("/", response_model=list[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_users(db, skip=skip, limit=limit)

@router.post("/", response_model=User)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    validate_role_profile_payload(user)
    hashed_password = get_password_hash(user.password)
    return create_user(db, user, hashed_password)

@router.put("/{user_id}/premium")
def upgrade_to_premium(user_id: int, es_premium: bool, db: Session = Depends(get_db)):
    # Lógica RF-07
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user.es_premium = es_premium
    db.commit()
    return {"message": f"Usuario premium: {es_premium}"}

@router.delete("/{user_id}", response_model=User)
def remove_user(user_id: int, db: Session = Depends(get_db)):
    user = delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user
