import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.core.dependencies import ensure_roles, ensure_same_user
from app.core.security import create_access_token, create_refresh_token, decode_refresh_token
from app.api.v1.endpoints.auth import get_login_credentials_flexible


def _build_user(*, user_id: int, role: str, is_superuser: bool = False):
    return SimpleNamespace(
        id=user_id,
        is_superuser=is_superuser,
        rol=SimpleNamespace(nombre=role),
    )


def test_refresh_token_can_be_decoded():
    token = create_refresh_token(subject=7, role="estudiante")

    payload = decode_refresh_token(token)

    assert payload["sub"] == "7"
    assert payload["role"] == "estudiante"
    assert payload["token_type"] == "refresh"


def test_access_token_is_not_valid_as_refresh_token():
    token = create_access_token(subject=7, role="estudiante")

    with pytest.raises(ValueError):
        decode_refresh_token(token)


def test_ensure_roles_accepts_matching_role():
    user = _build_user(user_id=3, role="empresa")

    result = ensure_roles(user, "empresa")

    assert result is user


def test_ensure_same_user_rejects_foreign_user():
    user = _build_user(user_id=3, role="empresa")

    with pytest.raises(HTTPException) as exc_info:
        ensure_same_user(user, 4, "empresa")

    assert exc_info.value.status_code == 403


def test_ensure_same_user_rejects_wrong_role():
    user = _build_user(user_id=3, role="estudiante")

    with pytest.raises(HTTPException) as exc_info:
        ensure_same_user(user, 3, "empresa")

    assert exc_info.value.status_code == 403


def test_ensure_same_user_allows_superuser():
    user = _build_user(user_id=1, role="admin", is_superuser=True)

    result = ensure_same_user(user, 999, "empresa")

    assert result is user


def test_login_credentials_flexible_accepts_json_body():
    async def receive():
        return {
            "type": "http.request",
            "body": b'{"email":"json@test.com","password":"secret"}',
            "more_body": False,
        }

    request = Request(
        {
            "type": "http",
            "method": "POST",
            "headers": [(b"content-type", b"application/json")],
        },
        receive,
    )

    credentials = asyncio.run(get_login_credentials_flexible(request))

    assert credentials.username == "json@test.com"
    assert credentials.password == "secret"
