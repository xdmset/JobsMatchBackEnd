from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.crud.crud_user import get_user, get_users, create_user, delete_user
from app.schemas.user import User, UserCreate

router = APIRouter() # ESTA LÍNEA ES LA QUE GENERABA EL NAMEERROR

@router.get("/", response_model=list[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_users(db, skip=skip, limit=limit)

@router.put("/{user_id}/premium")
def upgrade_to_premium(user_id: int, es_premium: bool, db: Session = Depends(get_db)):
    # Lógica RF-07
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user.es_premium = es_premium
    db.commit()
    return {"message": f"Usuario premium: {es_premium}"}