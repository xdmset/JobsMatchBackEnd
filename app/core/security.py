from datetime import timedelta
from typing import Any, Union

from fastapi_users.jwt import decode_jwt, generate_jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
ALGORITHM = "HS256"
SECRET_KEY = settings.SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_SECRET = settings.REFRESH_TOKEN_SECRET
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
TOKEN_AUDIENCE = ["fastapi-users:auth"]
ACCESS_TOKEN_KIND = "access"  # nosec B105
REFRESH_TOKEN_KIND = "refresh"  # nosec B105

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def _create_token(
    *,
    subject: Union[str, Any],
    role: str,
    token_type: str,
    secret: str,
    lifetime_seconds: int,
) -> str:
    payload = {
        "sub": str(subject),
        "aud": TOKEN_AUDIENCE,
        "role": role,
        "token_type": token_type,
    }
    return generate_jwt(payload, secret, lifetime_seconds, algorithm=ALGORITHM)


def create_access_token(
    subject: Union[str, Any],
    role: str,
    expires_delta: timedelta | None = None,
) -> str:
    lifetime_seconds = int(
        expires_delta.total_seconds() if expires_delta else ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    return _create_token(
        subject=subject,
        role=role,
        token_type=ACCESS_TOKEN_KIND,
        secret=SECRET_KEY,
        lifetime_seconds=lifetime_seconds,
    )


def create_refresh_token(
    subject: Union[str, Any],
    role: str,
    expires_delta: timedelta | None = None,
) -> str:
    lifetime_seconds = int(
        expires_delta.total_seconds() if expires_delta else REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    return _create_token(
        subject=subject,
        role=role,
        token_type=REFRESH_TOKEN_KIND,
        secret=REFRESH_TOKEN_SECRET,
        lifetime_seconds=lifetime_seconds,
    )


def decode_refresh_token(token: str) -> dict[str, Any]:
    payload = decode_jwt(
        token,
        REFRESH_TOKEN_SECRET,
        TOKEN_AUDIENCE,
        algorithms=[ALGORITHM],
    )
    if payload.get("token_type") != REFRESH_TOKEN_KIND:
        raise ValueError("Invalid refresh token")
    return payload
