from typing import Generator

from fastapi import Depends, Request
from fastapi_users import exceptions, schemas
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users.manager import BaseUserManager, IntegerIDMixin
from fastapi_users_db_sync_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.services.user_registration import create_profile_for_user, validate_role_profile_payload


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Request | None = None,
    ) -> User:
        validate_role_profile_payload(user_create)
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)
        user_dict.pop("perfil_estudiante", None)
        user_dict.pop("perfil_empresa", None)

        session = self.user_db.session
        created_user = User(**user_dict)

        try:
            session.add(created_user)
            session.flush()
            create_profile_for_user(session, created_user, user_create)
            session.commit()
            session.refresh(created_user)
        except Exception:
            session.rollback()
            raise

        await self.on_after_register(created_user, request)
        return created_user

    async def on_after_register(self, user: User, request: Request | None = None) -> None:
        return


def get_user_db(session: Session = Depends(get_db)) -> Generator[SQLAlchemyUserDatabase[User, int], None, None]:
    yield SQLAlchemyUserDatabase(session, User)


def get_user_manager(
    user_db: SQLAlchemyUserDatabase[User, int] = Depends(get_user_db),
) -> Generator[UserManager, None, None]:
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="/api/v1/auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.SECRET_KEY,
        lifetime_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers(get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
