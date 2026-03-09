from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import models
from fastapi_users import exceptions
from fastapi_users.manager import BaseUserManager

from app.core.config import settings
from app.core.fastapi_users import auth_backend, current_active_user, get_user_manager
from app.core.security import create_access_token, create_refresh_token, decode_refresh_token
from app.models.user import User
from app.schemas.auth import RefreshTokenRequest, Token

router = APIRouter()
TOKEN_TYPE_BEARER = "bearer"  # nosec B105

LOGIN_OPENAPI_EXTRA = {
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "format": "email"},
                        "password": {"type": "string", "format": "password"},
                    },
                    "required": ["email", "password"],
                },
                "examples": {
                    "json_email": {
                        "summary": "Login con JSON",
                        "value": {"email": "estudiante@test.com", "password": "secret123"},
                    }
                },
            },
            "application/x-www-form-urlencoded": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "format": "email"},
                        "password": {"type": "string", "format": "password"},
                        "grant_type": {"type": "string"},
                        "scope": {"type": "string", "default": ""},
                        "client_id": {"type": "string"},
                        "client_secret": {"type": "string"},
                    },
                    "required": ["email", "password"],
                }
            },
        },
    }
}


async def get_login_credentials(
    request: Request,
) -> OAuth2PasswordRequestForm:
    form = await request.form()
    login_value = form.get("email") or form.get("username")
    password = form.get("password")

    if not login_value or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email y password son requeridos",
        )

    return OAuth2PasswordRequestForm(
        grant_type=form.get("grant_type"),
        username=login_value,
        password=password,
        scope=form.get("scope", ""),
        client_id=form.get("client_id"),
        client_secret=form.get("client_secret"),
    )


async def get_login_credentials_flexible(request: Request) -> OAuth2PasswordRequestForm:
    content_type = request.headers.get("content-type", "").lower()

    if "application/json" in content_type:
        payload = await request.json()
        login_value = payload.get("email") or payload.get("username")
        password = payload.get("password")
        if not login_value or not password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Email y password son requeridos",
            )

        return OAuth2PasswordRequestForm(
            grant_type=payload.get("grant_type"),
            username=login_value,
            password=password,
            scope=payload.get("scope", ""),
            client_id=payload.get("client_id"),
            client_secret=payload.get("client_secret"),
        )

    return await get_login_credentials(request)


def _build_token_response(user: User) -> Token:
    role = user.rol.nombre.value if user.rol else ""
    return Token(
        access_token=create_access_token(user.id, role),
        refresh_token=create_refresh_token(user.id, role),
        token_type=TOKEN_TYPE_BEARER,
        access_token_expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token_expires_in=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )


@router.post(
    "/jwt/login",
    response_model=Token,
    name=f"auth:{auth_backend.name}.login",
    openapi_extra=LOGIN_OPENAPI_EXTRA,
    summary="Login con email y password",
    description=(
        "Acepta JSON o x-www-form-urlencoded. "
        "En el modal Authorize de Swagger UI, el campo username corresponde al email."
    ),
)
async def login(
    request: Request,
    credentials: OAuth2PasswordRequestForm = Depends(get_login_credentials_flexible),
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
):
    user = await user_manager.authenticate(credentials)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="LOGIN_BAD_CREDENTIALS",
        )

    await user_manager.on_after_login(user, request, None)
    return _build_token_response(user)


@router.post("/jwt/refresh", response_model=Token)
async def refresh_access_token(
    payload: RefreshTokenRequest,
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
):
    try:
        token_payload = decode_refresh_token(payload.refresh_token)
        user_id = user_manager.parse_id(token_payload["sub"])
        user = await user_manager.get(user_id)
    except (KeyError, ValueError, exceptions.UserNotExists, exceptions.InvalidID):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="REFRESH_TOKEN_INVALID",
        ) from None

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="USER_INACTIVE",
        )

    return _build_token_response(user)


@router.post("/jwt/logout", name=f"auth:{auth_backend.name}.logout")
async def logout(user: User = Depends(current_active_user)):
    return {"detail": f"Sesion cerrada para {user.email}. El cliente debe descartar los tokens."}
