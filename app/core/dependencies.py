from fastapi import Depends, HTTPException, status

from app.core.fastapi_users import current_active_user
from app.core.enums import NombreRol
from app.models.user import User


def get_current_user(user: User = Depends(current_active_user)) -> User:
    return user


def get_user_role(user: User) -> str | None:
    if not user.rol:
        return None
    role = user.rol.nombre
    return role.value if isinstance(role, NombreRol) else str(role)


def ensure_roles(user: User, *allowed_roles: str) -> User:
    if user.is_superuser:
        return user

    if get_user_role(user) not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para esta accion",
        )
    return user


def ensure_same_user(user: User, target_user_id: int, *allowed_roles: str) -> User:
    if user.is_superuser:
        return user

    if user.id != target_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para esta accion",
        )

    if allowed_roles:
        ensure_roles(user, *allowed_roles)
    return user


def role_required(*required_roles: str):
    async def role_checker(user: User = Depends(current_active_user)) -> User:
        return ensure_roles(user, *required_roles)

    return role_checker
