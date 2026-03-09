from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import models
from fastapi_users.manager import BaseUserManager

from app.core.fastapi_users import auth_backend, fastapi_users, get_user_manager

router = APIRouter()


async def get_login_credentials(
    request: Request,
    email: Optional[str] = Form(None),
    password: str = Form(...),
    scope: str = Form(""),
    grant_type: Optional[str] = Form(None),
    client_id: Optional[str] = Form(None),
    client_secret: Optional[str] = Form(None),
) -> OAuth2PasswordRequestForm:
    form = await request.form()
    login_value = email or form.get("username")

    if not login_value:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email es requerido",
        )

    return OAuth2PasswordRequestForm(
        grant_type=grant_type,
        username=login_value,
        password=password,
        scope=scope,
        client_id=client_id,
        client_secret=client_secret,
    )


@router.post("/jwt/login", name=f"auth:{auth_backend.name}.login")
async def login(
    request: Request,
    credentials: OAuth2PasswordRequestForm = Depends(get_login_credentials),
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
    strategy=Depends(auth_backend.get_strategy),
):
    user = await user_manager.authenticate(credentials)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="LOGIN_BAD_CREDENTIALS",
        )

    response = await auth_backend.login(strategy, user)
    await user_manager.on_after_login(user, request, response)
    return response


@router.post("/jwt/logout", name=f"auth:{auth_backend.name}.logout")
async def logout(
    user_token=Depends(fastapi_users.authenticator.current_user_token(active=True)),
    strategy=Depends(auth_backend.get_strategy),
):
    user, token = user_token
    return await auth_backend.logout(strategy, user, token)
