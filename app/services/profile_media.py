from __future__ import annotations

from typing import Any

from app.services.storage_service import StorageService


def _safe_presigned_url(object_name: str | None) -> str | None:
    if not object_name:
        return None

    try:
        return StorageService().get_presigned_get_url(object_name)
    except Exception:
        return None


def serialize_estudiante_profile(estudiante: Any) -> dict[str, Any]:
    data = {
        "usuario_id": estudiante.usuario_id,
        "nombre_completo": estudiante.nombre_completo,
        "institucion_educativa": estudiante.institucion_educativa,
        "nivel_academico": estudiante.nivel_academico,
        "biografia": estudiante.biografia,
        "habilidades": estudiante.habilidades,
        "fecha_nacimiento": estudiante.fecha_nacimiento,
        "ubicacion": estudiante.ubicacion,
        "modalidad_preferida": estudiante.modalidad_preferida,
        "cv_tipo_archivo": estudiante.cv_tipo_archivo,
    }
    data["cv_url"] = _safe_presigned_url(getattr(estudiante, "cv_storage_key", None)) or estudiante.cv_url
    data["foto_perfil_url"] = (
        _safe_presigned_url(getattr(estudiante, "foto_perfil_storage_key", None)) or estudiante.foto_perfil_url
    )
    return data


def serialize_empresa_profile(empresa: Any) -> dict[str, Any]:
    data = {
        "usuario_id": empresa.usuario_id,
        "nombre_comercial": empresa.nombre_comercial,
        "sector": empresa.sector,
        "descripcion": empresa.descripcion,
        "sitio_web": empresa.sitio_web,
        "ubicacion_sede": empresa.ubicacion_sede,
    }
    data["foto_perfil_url"] = (
        _safe_presigned_url(getattr(empresa, "foto_perfil_storage_key", None)) or empresa.foto_perfil_url
    )
    return data
