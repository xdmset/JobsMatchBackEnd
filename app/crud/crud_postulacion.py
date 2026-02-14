from typing import Optional
from sqlalchemy.orm import Session

from app.models.postulacion import Postulacion
from app.models.retroalimentacion import Retroalimentacion
from app.models.vacante import Vacante


def get_vacante(db: Session, vacante_id: int) -> Optional[Vacante]:
    return db.query(Vacante).filter(Vacante.id == vacante_id).first()


def get_ultima_postulacion(db: Session, estudiante_id: int, vacante_id: int) -> Optional[Postulacion]:
    return (
        db.query(Postulacion)
        .filter(
            Postulacion.estudiante_id == estudiante_id,
            Postulacion.vacante_id == vacante_id,
        )
        .order_by(Postulacion.fecha_creacion.desc())
        .first()
    )


def puede_reaplicar(db: Session, estudiante_id: int, vacante_id: int) -> bool:
    ultima = get_ultima_postulacion(db, estudiante_id, vacante_id)
    if not ultima:
        return True
    return ultima.estado == "rechazado"


def crear_postulacion_si_aplica(
    db: Session,
    estudiante_id: int,
    vacante: Vacante,
    match_id: Optional[int],
    source: str,
) -> Optional[Postulacion]:
    if not puede_reaplicar(db, estudiante_id, vacante.id):
        return None

    nueva_postulacion = Postulacion(
        match_id=match_id,
        estudiante_id=estudiante_id,
        vacante_id=vacante.id,
        empresa_id=vacante.empresa_id,
        source=source,
        estado="enviado",
    )
    db.add(nueva_postulacion)
    return nueva_postulacion


def listar_postulaciones_empresa(db: Session, empresa_id: int):
    return db.query(Postulacion).filter(
        Postulacion.empresa_id == empresa_id
    ).all()


def actualizar_estado_postulacion(
    db: Session,
    postulacion_id: int,
    nuevo_estado: str,
    feedback: Optional[dict] = None,
) -> Optional[Postulacion]:
    postulacion = db.query(Postulacion).filter(Postulacion.id == postulacion_id).first()
    if not postulacion:
        return None

    postulacion.estado = nuevo_estado

    if nuevo_estado == "rechazado" and feedback:
        retro_existente = db.query(Retroalimentacion).filter(
            Retroalimentacion.postulacion_id == postulacion_id
        ).first()
        if retro_existente:
            retro_existente.campos_mejora = feedback.get("campos_mejora")
            retro_existente.sugerencias_perfil = feedback.get("sugerencias_perfil")
        else:
            nueva_retro = Retroalimentacion(
                postulacion_id=postulacion_id,
                campos_mejora=feedback.get("campos_mejora"),
                sugerencias_perfil=feedback.get("sugerencias_perfil")
            )
            db.add(nueva_retro)

    return postulacion
