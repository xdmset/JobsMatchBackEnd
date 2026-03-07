from fastapi import Depends, HTTPException, status

from app.core.fastapi_users import current_active_user
from app.models.user import User


def get_current_user(user: User = Depends(current_active_user)) -> User:
    return user


def role_required(required_role: str):
    async def role_checker(user: User = Depends(current_active_user)) -> User:
        if not user.rol or user.rol.nombre != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para esta accion",
            )
        return user

    return role_checker
