from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.perfil_empresa import PerfilEmpresa
from app.models.perfil_estudiante import PerfilEstudiante
from app.schemas.media import MediaAccessResponse, MediaUploadResponse
from app.services.storage_service import StorageService

router = APIRouter()

IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
DOCUMENT_CONTENT_TYPES = {"application/pdf"}


def _read_upload(file: UploadFile, allowed_content_types: set[str], max_size: int) -> tuple[bytes, str]:
    if file.content_type not in allowed_content_types:
        raise HTTPException(status_code=400, detail="Tipo de archivo no permitido")

    content = file.file.read()
    if not content:
        raise HTTPException(status_code=400, detail="El archivo esta vacio")

    if len(content) > max_size:
        raise HTTPException(status_code=400, detail="El archivo excede el tamano permitido")

    extension = Path(file.filename or "").suffix.lower()
    if not extension:
        guessed_extension = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
            "application/pdf": ".pdf",
        }
        extension = guessed_extension.get(file.content_type, "")

    return content, extension


def _build_object_name(prefix: str, usuario_id: int, extension: str) -> str:
    return f"{prefix}/{usuario_id}/{uuid4().hex}{extension}"


def _upload_and_build_response(
    *,
    usuario_id: int,
    media_type: str,
    object_name: str,
    content: bytes,
    content_type: str,
) -> MediaUploadResponse:
    storage = StorageService()
    storage.ensure_bucket_exists()
    storage.upload_bytes(content, object_name, content_type)
    url = storage.get_presigned_get_url(object_name)

    return MediaUploadResponse(
        usuario_id=usuario_id,
        media_type=media_type,
        object_name=object_name,
        bucket=settings.minio_bucket_name,
        url=url,
        content_type=content_type,
        size=len(content),
    )


@router.post("/estudiantes/{usuario_id}/foto", response_model=MediaUploadResponse)
def upload_estudiante_foto(
    usuario_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    estudiante = db.query(PerfilEstudiante).filter(PerfilEstudiante.usuario_id == usuario_id).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    content, extension = _read_upload(file, IMAGE_CONTENT_TYPES, settings.max_image_upload_bytes)
    object_name = _build_object_name("estudiantes/fotos", usuario_id, extension)
    response = _upload_and_build_response(
        usuario_id=usuario_id,
        media_type="foto_perfil",
        object_name=object_name,
        content=content,
        content_type=file.content_type or "application/octet-stream",
    )

    old_object_name = estudiante.foto_perfil_storage_key
    estudiante.foto_perfil_storage_key = object_name
    db.commit()

    if old_object_name:
        StorageService().remove_object(old_object_name)

    return response


@router.post("/estudiantes/{usuario_id}/cv", response_model=MediaUploadResponse)
def upload_estudiante_cv(
    usuario_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    estudiante = db.query(PerfilEstudiante).filter(PerfilEstudiante.usuario_id == usuario_id).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    content, extension = _read_upload(file, DOCUMENT_CONTENT_TYPES, settings.max_document_upload_bytes)
    object_name = _build_object_name("estudiantes/cv", usuario_id, extension)
    response = _upload_and_build_response(
        usuario_id=usuario_id,
        media_type="cv",
        object_name=object_name,
        content=content,
        content_type=file.content_type or "application/octet-stream",
    )

    old_object_name = estudiante.cv_storage_key
    estudiante.cv_storage_key = object_name
    estudiante.cv_tipo_archivo = file.content_type
    db.commit()

    if old_object_name:
        StorageService().remove_object(old_object_name)

    return response


@router.get("/estudiantes/{usuario_id}/foto", response_model=MediaAccessResponse)
def get_estudiante_foto(usuario_id: int, db: Session = Depends(get_db)):
    estudiante = db.query(PerfilEstudiante).filter(PerfilEstudiante.usuario_id == usuario_id).first()
    if not estudiante or not estudiante.foto_perfil_storage_key:
        raise HTTPException(status_code=404, detail="Foto de perfil no encontrada")

    storage = StorageService()
    return MediaAccessResponse(
        usuario_id=usuario_id,
        media_type="foto_perfil",
        object_name=estudiante.foto_perfil_storage_key,
        url=storage.get_presigned_get_url(estudiante.foto_perfil_storage_key),
        expires_in_seconds=settings.media_url_expiration_seconds,
    )


@router.get("/estudiantes/{usuario_id}/cv", response_model=MediaAccessResponse)
def get_estudiante_cv(usuario_id: int, db: Session = Depends(get_db)):
    estudiante = db.query(PerfilEstudiante).filter(PerfilEstudiante.usuario_id == usuario_id).first()
    if not estudiante or not estudiante.cv_storage_key:
        raise HTTPException(status_code=404, detail="CV no encontrado")

    storage = StorageService()
    return MediaAccessResponse(
        usuario_id=usuario_id,
        media_type="cv",
        object_name=estudiante.cv_storage_key,
        url=storage.get_presigned_get_url(estudiante.cv_storage_key),
        expires_in_seconds=settings.media_url_expiration_seconds,
    )


@router.delete("/estudiantes/{usuario_id}/foto")
def delete_estudiante_foto(usuario_id: int, db: Session = Depends(get_db)):
    estudiante = db.query(PerfilEstudiante).filter(PerfilEstudiante.usuario_id == usuario_id).first()
    if not estudiante or not estudiante.foto_perfil_storage_key:
        raise HTTPException(status_code=404, detail="Foto de perfil no encontrada")

    StorageService().remove_object(estudiante.foto_perfil_storage_key)
    estudiante.foto_perfil_storage_key = None
    db.commit()
    return {"detail": "Foto eliminada"}


@router.delete("/estudiantes/{usuario_id}/cv")
def delete_estudiante_cv(usuario_id: int, db: Session = Depends(get_db)):
    estudiante = db.query(PerfilEstudiante).filter(PerfilEstudiante.usuario_id == usuario_id).first()
    if not estudiante or not estudiante.cv_storage_key:
        raise HTTPException(status_code=404, detail="CV no encontrado")

    StorageService().remove_object(estudiante.cv_storage_key)
    estudiante.cv_storage_key = None
    estudiante.cv_tipo_archivo = None
    db.commit()
    return {"detail": "CV eliminado"}


@router.post("/empresas/{usuario_id}/foto", response_model=MediaUploadResponse)
def upload_empresa_foto(
    usuario_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    empresa = db.query(PerfilEmpresa).filter(PerfilEmpresa.usuario_id == usuario_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    content, extension = _read_upload(file, IMAGE_CONTENT_TYPES, settings.max_image_upload_bytes)
    object_name = _build_object_name("empresas/fotos", usuario_id, extension)
    response = _upload_and_build_response(
        usuario_id=usuario_id,
        media_type="foto_perfil",
        object_name=object_name,
        content=content,
        content_type=file.content_type or "application/octet-stream",
    )

    old_object_name = empresa.foto_perfil_storage_key
    empresa.foto_perfil_storage_key = object_name
    db.commit()

    if old_object_name:
        StorageService().remove_object(old_object_name)

    return response


@router.get("/empresas/{usuario_id}/foto", response_model=MediaAccessResponse)
def get_empresa_foto(usuario_id: int, db: Session = Depends(get_db)):
    empresa = db.query(PerfilEmpresa).filter(PerfilEmpresa.usuario_id == usuario_id).first()
    if not empresa or not empresa.foto_perfil_storage_key:
        raise HTTPException(status_code=404, detail="Foto de empresa no encontrada")

    storage = StorageService()
    return MediaAccessResponse(
        usuario_id=usuario_id,
        media_type="foto_perfil",
        object_name=empresa.foto_perfil_storage_key,
        url=storage.get_presigned_get_url(empresa.foto_perfil_storage_key),
        expires_in_seconds=settings.media_url_expiration_seconds,
    )


@router.delete("/empresas/{usuario_id}/foto")
def delete_empresa_foto(usuario_id: int, db: Session = Depends(get_db)):
    empresa = db.query(PerfilEmpresa).filter(PerfilEmpresa.usuario_id == usuario_id).first()
    if not empresa or not empresa.foto_perfil_storage_key:
        raise HTTPException(status_code=404, detail="Foto de empresa no encontrada")

    StorageService().remove_object(empresa.foto_perfil_storage_key)
    empresa.foto_perfil_storage_key = None
    db.commit()
    return {"detail": "Foto eliminada"}
