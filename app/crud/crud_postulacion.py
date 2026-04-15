from typing import Optional
from sqlalchemy.orm import Session

from app.models.perfil_estudiante import PerfilEstudiante
from app.models.postulacion import Postulacion
from app.models.retroalimentacion import Retroalimentacion
from app.models.user import User
from app.models.vacante import Vacante


def get_postulacion(db: Session, postulacion_id: int) -> Optional[Postulacion]:
    return db.query(Postulacion).filter(Postulacion.id == postulacion_id).first()


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


def listar_postulaciones_estudiante(
    db: Session,
    estudiante_id: int,
    *,
    estado: str | None = None,
):
    query = db.query(Postulacion).filter(Postulacion.estudiante_id == estudiante_id)
    if estado:
        query = query.filter(Postulacion.estado == estado)
    return query.order_by(Postulacion.fecha_actualizacion.desc(), Postulacion.id.desc()).all()


def listar_postulaciones_empresa(
    db: Session,
    empresa_id: int,
    *,
    estado: str | None = None,
    institucion_educativa: str | None = None,
    nivel_academico: str | None = None,
    ubicacion: str | None = None,
):
    query = db.query(Postulacion).join(
        PerfilEstudiante,
        PerfilEstudiante.usuario_id == Postulacion.estudiante_id,
    ).join(
        User,
        User.id == Postulacion.estudiante_id,
    ).filter(Postulacion.empresa_id == empresa_id)

    if estado:
        query = query.filter(Postulacion.estado == estado)
    if institucion_educativa:
        query = query.filter(PerfilEstudiante.institucion_educativa.contains(institucion_educativa))
    if nivel_academico:
        query = query.filter(PerfilEstudiante.nivel_academico.contains(nivel_academico))
    if ubicacion:
        query = query.filter(PerfilEstudiante.ubicacion.contains(ubicacion))

    return query.order_by(User.es_premium.desc(), Postulacion.fecha_actualizacion.desc(), Postulacion.id.desc()).all()


def actualizar_estado_postulacion(
    db: Session,
    postulacion_id: int,
    nuevo_estado: str,
    feedback: Optional[dict] = None,
) -> Optional[Postulacion]:
    postulacion = get_postulacion(db, postulacion_id)
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
            retro_existente.roadmap_json = None
            retro_existente.roadmap_estado = "pendiente"
            retro_existente.roadmap_generado_en = None
            retro_existente.roadmap_error = None
        else:
            nueva_retro = Retroalimentacion(
                postulacion_id=postulacion_id,
                campos_mejora=feedback.get("campos_mejora"),
                sugerencias_perfil=feedback.get("sugerencias_perfil"),
                roadmap_estado="pendiente",
            )
            db.add(nueva_retro)

    return postulacion
