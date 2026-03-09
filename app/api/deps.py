from typing import Generator

from fastapi.security import OAuth2PasswordBearer

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/login/access-token")


def get_db() -> Generator:
    # Implementación de sesión de DB
    yield None
