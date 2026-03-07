from __future__ import annotations

from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.constants import ROL_EMPRESA, ROL_ESTUDIANTE
from app.models.perfil_empresa import PerfilEmpresa
from app.models.perfil_estudiante import PerfilEstudiante
from app.models.user import User


def validate_role_profile_payload(user_in: Any) -> None:
    perfil_estudiante = getattr(user_in, "perfil_estudiante", None)
    perfil_empresa = getattr(user_in, "perfil_empresa", None)

    if user_in.rol_id == ROL_ESTUDIANTE:
        if not perfil_estudiante or perfil_empresa:
            raise HTTPException(
                status_code=400,
                detail="Perfil de estudiante requerido y sin perfil de empresa",
            )
        return

    if user_in.rol_id == ROL_EMPRESA:
        if not perfil_empresa or perfil_estudiante:
            raise HTTPException(
                status_code=400,
                detail="Perfil de empresa requerido y sin perfil de estudiante",
            )
        return

    if perfil_estudiante or perfil_empresa:
        raise HTTPException(
            status_code=400,
            detail="El rol indicado no admite perfiles asociados en este registro",
        )


def create_profile_for_user(session: Session, user: User, user_in: Any) -> None:
    perfil_estudiante = getattr(user_in, "perfil_estudiante", None)
    perfil_empresa = getattr(user_in, "perfil_empresa", None)

    if user.rol_id == ROL_ESTUDIANTE and perfil_estudiante:
        session.add(
            PerfilEstudiante(
                usuario_id=user.id,
                **perfil_estudiante.model_dump(),
            )
        )
        return

    if user.rol_id == ROL_EMPRESA and perfil_empresa:
        session.add(
            PerfilEmpresa(
                usuario_id=user.id,
                **perfil_empresa.model_dump(),
            )
        )
