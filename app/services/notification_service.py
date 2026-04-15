"""Servicio de notificaciones con soporte para Firebase Cloud Messaging (FCM)."""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud import crud_notificacion
from app.models.notificacion import Notificacion
from app.schemas.notificacion import NotificacionCreate, TipoNotificacion

logger = logging.getLogger(__name__)

# Firebase Admin SDK (opcional)
_firebase_app = None


def _init_firebase():
    """Inicializa Firebase Admin SDK si está configurado."""
    global _firebase_app
    if _firebase_app is not None:
        return _firebase_app

    if not settings.FCM_ENABLED or not settings.FCM_CREDENTIALS_PATH:
        logger.info("FCM deshabilitado o sin credenciales configuradas")
        return None

    try:
        import firebase_admin
        from firebase_admin import credentials

        cred = credentials.Certificate(settings.FCM_CREDENTIALS_PATH)
        _firebase_app = firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin SDK inicializado correctamente")
        return _firebase_app
    except Exception as e:
        logger.error(f"Error inicializando Firebase: {e}")
        return None


def _send_fcm_notification(
    fcm_token: str,
    titulo: str,
    mensaje: str,
    data: Optional[dict] = None,
) -> bool:
    """Envía una notificación push via FCM."""
    if not settings.FCM_ENABLED:
        return False

    try:
        from firebase_admin import messaging

        if _init_firebase() is None:
            return False

        message = messaging.Message(
            notification=messaging.Notification(
                title=titulo,
                body=mensaje,
            ),
            data=data or {},
            token=fcm_token,
        )

        response = messaging.send(message)
        logger.info(f"FCM notification enviada: {response}")
        return True
    except Exception as e:
        logger.error(f"Error enviando FCM notification: {e}")
        return False


def crear_notificacion(
    db: Session,
    usuario_id: int,
    tipo: TipoNotificacion,
    titulo: str,
    mensaje: str,
    vacante_id: Optional[int] = None,
    postulacion_id: Optional[int] = None,
    estudiante_id: Optional[int] = None,
    fcm_token: Optional[str] = None,
) -> Notificacion:
    """
    Crea una notificación en la BD y opcionalmente envía push notification.

    Args:
        db: Sesión de base de datos
        usuario_id: ID del usuario destinatario
        tipo: Tipo de notificación
        titulo: Título de la notificación
        mensaje: Mensaje de la notificación
        vacante_id: ID de vacante relacionada (opcional)
        postulacion_id: ID de postulación relacionada (opcional)
        estudiante_id: ID de estudiante relacionado (opcional)
        fcm_token: Token FCM del dispositivo (opcional, para push)

    Returns:
        La notificación creada
    """
    notificacion_data = NotificacionCreate(
        usuario_id=usuario_id,
        tipo=tipo,
        titulo=titulo,
        mensaje=mensaje,
        vacante_id=vacante_id,
        postulacion_id=postulacion_id,
        estudiante_id=estudiante_id,
    )

    notificacion = crud_notificacion.crear_notificacion(db, notificacion_data)

    # Enviar push notification si hay token FCM
    if fcm_token:
        data = {
            "tipo": tipo.value,
            "notificacion_id": str(notificacion.id),
        }
        if vacante_id:
            data["vacante_id"] = str(vacante_id)
        if postulacion_id:
            data["postulacion_id"] = str(postulacion_id)
        if estudiante_id:
            data["estudiante_id"] = str(estudiante_id)

        _send_fcm_notification(fcm_token, titulo, mensaje, data)

    return notificacion


# --- Funciones de alto nivel para casos de uso específicos ---


def notificar_like_recibido(
    db: Session,
    empresa_id: int,
    estudiante_nombre: str,
    vacante_titulo: str,
    vacante_id: int,
    estudiante_id: int,
    fcm_token: Optional[str] = None,
) -> Notificacion:
    """Notifica a una empresa que recibió un like de un estudiante."""
    return crear_notificacion(
        db=db,
        usuario_id=empresa_id,
        tipo=TipoNotificacion.like_recibido,
        titulo="Nuevo like recibido",
        mensaje=f"{estudiante_nombre} mostró interés en tu vacante '{vacante_titulo}'",
        vacante_id=vacante_id,
        estudiante_id=estudiante_id,
        fcm_token=fcm_token,
    )


def notificar_match(
    db: Session,
    usuario_id: int,
    contraparte_nombre: str,
    vacante_titulo: str,
    vacante_id: int,
    es_estudiante: bool,
    postulacion_id: Optional[int] = None,
    estudiante_id: Optional[int] = None,
    fcm_token: Optional[str] = None,
) -> Notificacion:
    """Notifica a un usuario sobre un match."""
    if es_estudiante:
        mensaje = f"Felicidades! La empresa mostró interés en ti para '{vacante_titulo}'"
    else:
        mensaje = f"Match confirmado con {contraparte_nombre} para '{vacante_titulo}'"

    return crear_notificacion(
        db=db,
        usuario_id=usuario_id,
        tipo=TipoNotificacion.match,
        titulo="Nuevo match",
        mensaje=mensaje,
        vacante_id=vacante_id,
        postulacion_id=postulacion_id,
        estudiante_id=estudiante_id,
        fcm_token=fcm_token,
    )


def notificar_cambio_estado_postulacion(
    db: Session,
    estudiante_id: int,
    vacante_titulo: str,
    nuevo_estado: str,
    vacante_id: int,
    postulacion_id: int,
    fcm_token: Optional[str] = None,
) -> Notificacion:
    """Notifica a un estudiante sobre el cambio de estado de su postulación."""
    estados_mensajes = {
        "visto": f"Tu postulación para '{vacante_titulo}' ha sido vista",
        "en_proceso": f"Tu postulación para '{vacante_titulo}' está en proceso de revisión",
        "rechazado": f"Tu postulación para '{vacante_titulo}' no fue seleccionada",
        "aceptado": f"Felicidades! Has sido aceptado para '{vacante_titulo}'",
    }

    mensaje = estados_mensajes.get(
        nuevo_estado,
        f"Tu postulación para '{vacante_titulo}' cambió a estado: {nuevo_estado}",
    )

    return crear_notificacion(
        db=db,
        usuario_id=estudiante_id,
        tipo=TipoNotificacion.postulacion_estado,
        titulo="Actualización de postulación",
        mensaje=mensaje,
        vacante_id=vacante_id,
        postulacion_id=postulacion_id,
        fcm_token=fcm_token,
    )
