from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.notificacion import Notificacion
from app.schemas.notificacion import NotificacionCreate


def crear_notificacion(db: Session, notificacion: NotificacionCreate) -> Notificacion:
    """Crea una nueva notificación."""
    db_notificacion = Notificacion(**notificacion.model_dump())
    db.add(db_notificacion)
    db.commit()
    db.refresh(db_notificacion)
    return db_notificacion


def get_notificacion(db: Session, notificacion_id: int) -> Optional[Notificacion]:
    """Obtiene una notificación por ID."""
    return db.query(Notificacion).filter(Notificacion.id == notificacion_id).first()


def get_notificaciones_usuario(
    db: Session,
    usuario_id: int,
    solo_no_leidas: bool = False,
    skip: int = 0,
    limit: int = 50,
) -> list[Notificacion]:
    """Obtiene las notificaciones de un usuario."""
    query = db.query(Notificacion).filter(Notificacion.usuario_id == usuario_id)

    if solo_no_leidas:
        query = query.filter(Notificacion.leida.is_(False))

    return (
        query.order_by(Notificacion.fecha_creacion.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def contar_notificaciones_usuario(
    db: Session,
    usuario_id: int,
) -> tuple[int, int]:
    """Cuenta las notificaciones totales y no leídas de un usuario."""
    total = db.query(func.count(Notificacion.id)).filter(
        Notificacion.usuario_id == usuario_id
    ).scalar()

    no_leidas = db.query(func.count(Notificacion.id)).filter(
        Notificacion.usuario_id == usuario_id,
        Notificacion.leida.is_(False),
    ).scalar()

    return total or 0, no_leidas or 0


def marcar_como_leida(db: Session, notificacion_id: int) -> Optional[Notificacion]:
    """Marca una notificación como leída."""
    notificacion = get_notificacion(db, notificacion_id)
    if notificacion and not notificacion.leida:
        notificacion.leida = True
        notificacion.fecha_leida = datetime.now(timezone.utc)
        db.commit()
        db.refresh(notificacion)
    return notificacion


def marcar_todas_como_leidas(db: Session, usuario_id: int) -> int:
    """Marca todas las notificaciones de un usuario como leídas."""
    ahora = datetime.now(timezone.utc)
    count = (
        db.query(Notificacion)
        .filter(
            Notificacion.usuario_id == usuario_id,
            Notificacion.leida.is_(False),
        )
        .update({"leida": True, "fecha_leida": ahora})
    )
    db.commit()
    return count


def eliminar_notificacion(db: Session, notificacion_id: int) -> bool:
    """Elimina una notificación."""
    notificacion = get_notificacion(db, notificacion_id)
    if notificacion:
        db.delete(notificacion)
        db.commit()
        return True
    return False
