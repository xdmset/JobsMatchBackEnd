from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.crud import crud_notificacion
from app.db.session import get_db
from app.models.user import User
from app.schemas.notificacion import NotificacionRead, NotificacionesResumen

router = APIRouter()


@router.get("/", response_model=list[NotificacionRead])
def listar_notificaciones(
    solo_no_leidas: bool = False,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista las notificaciones del usuario actual."""
    return crud_notificacion.get_notificaciones_usuario(
        db,
        usuario_id=current_user.id,
        solo_no_leidas=solo_no_leidas,
        skip=skip,
        limit=limit,
    )


@router.get("/resumen", response_model=NotificacionesResumen)
def obtener_resumen_notificaciones(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene el resumen de notificaciones (total y no leídas)."""
    total, no_leidas = crud_notificacion.contar_notificaciones_usuario(
        db, usuario_id=current_user.id
    )
    return NotificacionesResumen(total=total, no_leidas=no_leidas)


@router.put("/{notificacion_id}/leer", response_model=NotificacionRead)
def marcar_notificacion_como_leida(
    notificacion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Marca una notificación como leída."""
    notificacion = crud_notificacion.get_notificacion(db, notificacion_id)
    if not notificacion:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    if notificacion.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para esta acción")

    return crud_notificacion.marcar_como_leida(db, notificacion_id)


@router.put("/leer-todas")
def marcar_todas_como_leidas(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Marca todas las notificaciones del usuario como leídas."""
    count = crud_notificacion.marcar_todas_como_leidas(db, usuario_id=current_user.id)
    return {"message": f"Se marcaron {count} notificaciones como leídas"}


@router.delete("/{notificacion_id}")
def eliminar_notificacion(
    notificacion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina una notificación."""
    notificacion = crud_notificacion.get_notificacion(db, notificacion_id)
    if not notificacion:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    if notificacion.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para esta acción")

    crud_notificacion.eliminar_notificacion(db, notificacion_id)
    return {"message": "Notificación eliminada"}
