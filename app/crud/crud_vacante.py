from datetime import datetime, timezone

from sqlalchemy import and_, case, func
from sqlalchemy.orm import Session

from app.models.interaccion_swipe import InteraccionSwipe
from app.models.interaccion_swipe_empresa import InteraccionSwipeEmpresa
from app.models.match import Match
from app.models.vacante import Vacante
from app.models.vacante_visualizacion import VacanteVisualizacion
from app.schemas.vacante import (
    VacanteCreate,
    VacanteHistorialEmpresa,
    VacanteHistorialEstudiante,
    VacanteUpdate,
)

def get_vacante(db: Session, vacante_id: int):
    return db.query(Vacante).filter(Vacante.id == vacante_id).first()

def get_vacantes(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    modalidad: str = None, 
    ubicacion: str = None, 
    sueldo_min: float = None
):
    """RF-09: Obtener vacantes con filtros dinámicos."""
    query = db.query(Vacante)
    
    if modalidad:
        query = query.filter(Vacante.modalidad == modalidad)
    if ubicacion:
        query = query.filter(Vacante.ubicacion.contains(ubicacion))
    if sueldo_min:
        query = query.filter(Vacante.sueldo_minimo >= sueldo_min)
    
    return query.offset(skip).limit(limit).all()

def create_vacante(db: Session, vacante: VacanteCreate, empresa_id: int):
    # Se usa model_dump() para Pydantic v2
    db_vacante = Vacante(**vacante.model_dump(), empresa_id=empresa_id)
    db.add(db_vacante)
    db.commit()
    db.refresh(db_vacante)
    return db_vacante

def update_vacante(db: Session, vacante_id: int, vacante_data: VacanteUpdate):
    db_vacante = get_vacante(db, vacante_id)
    if db_vacante:
        for field, value in vacante_data.model_dump(exclude_unset=True).items():
            setattr(db_vacante, field, value)
        db.commit()
        db.refresh(db_vacante)
    return db_vacante

def delete_vacante(db: Session, vacante_id: int):
    db_vacante = get_vacante(db, vacante_id)
    if db_vacante:
        db.delete(db_vacante)
        db.commit()
    return db_vacante


def registrar_visualizacion_vacante(
    db: Session,
    estudiante_id: int,
    vacante_id: int,
) -> VacanteVisualizacion:
    visualizacion = db.query(VacanteVisualizacion).filter(
        VacanteVisualizacion.estudiante_id == estudiante_id,
        VacanteVisualizacion.vacante_id == vacante_id,
    ).first()

    ahora = datetime.now(timezone.utc)
    if visualizacion:
        visualizacion.ultima_visualizacion = ahora
        visualizacion.total_visualizaciones += 1
    else:
        visualizacion = VacanteVisualizacion(
            estudiante_id=estudiante_id,
            vacante_id=vacante_id,
            primera_visualizacion=ahora,
            ultima_visualizacion=ahora,
            total_visualizaciones=1,
        )
        db.add(visualizacion)

    db.commit()
    db.refresh(visualizacion)
    return visualizacion


def get_historial_vacantes_estudiante(
    db: Session,
    estudiante_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[VacanteHistorialEstudiante]:
    rows = (
        db.query(VacanteVisualizacion, Vacante, InteraccionSwipe)
        .join(Vacante, Vacante.id == VacanteVisualizacion.vacante_id)
        .outerjoin(
            InteraccionSwipe,
            and_(
                InteraccionSwipe.estudiante_id == VacanteVisualizacion.estudiante_id,
                InteraccionSwipe.vacante_id == VacanteVisualizacion.vacante_id,
            ),
        )
        .filter(VacanteVisualizacion.estudiante_id == estudiante_id)
        .order_by(VacanteVisualizacion.ultima_visualizacion.desc(), Vacante.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    historial: list[VacanteHistorialEstudiante] = []
    for visualizacion, vacante, swipe in rows:
        historial.append(
            VacanteHistorialEstudiante(
                id=vacante.id,
                empresa_id=vacante.empresa_id,
                titulo=vacante.titulo,
                descripcion=vacante.descripcion,
                requisitos=vacante.requisitos,
                tipo_contrato=vacante.tipo_contrato,
                modalidad=vacante.modalidad,
                ubicacion=vacante.ubicacion,
                sueldo_minimo=float(vacante.sueldo_minimo) if vacante.sueldo_minimo is not None else None,
                sueldo_maximo=float(vacante.sueldo_maximo) if vacante.sueldo_maximo is not None else None,
                moneda=vacante.moneda,
                estado=vacante.estado,
                fecha_publicacion=vacante.fecha_publicacion,
                primera_visualizacion=visualizacion.primera_visualizacion,
                ultima_visualizacion=visualizacion.ultima_visualizacion,
                total_visualizaciones=visualizacion.total_visualizaciones,
                le_dio_like=bool(swipe and swipe.interes_estudiante),
                fecha_like=swipe.fecha if swipe and swipe.interes_estudiante else None,
            )
        )

    return historial


def get_historial_vacantes_empresa(
    db: Session,
    empresa_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[VacanteHistorialEmpresa]:
    visualizaciones_subquery = (
        db.query(
            VacanteVisualizacion.vacante_id.label("vacante_id"),
            func.coalesce(func.sum(VacanteVisualizacion.total_visualizaciones), 0).label("total_visualizaciones"),
            func.count(VacanteVisualizacion.id).label("total_estudiantes_que_vieron"),
            func.max(VacanteVisualizacion.ultima_visualizacion).label("ultima_visualizacion"),
        )
        .group_by(VacanteVisualizacion.vacante_id)
        .subquery()
    )

    likes_estudiante_subquery = (
        db.query(
            InteraccionSwipe.vacante_id.label("vacante_id"),
            func.sum(
                case((InteraccionSwipe.interes_estudiante.is_(True), 1), else_=0)
            ).label("total_likes_estudiantes"),
            func.max(
                case(
                    (InteraccionSwipe.interes_estudiante.is_(True), InteraccionSwipe.fecha),
                    else_=None,
                )
            ).label("ultimo_like_estudiante"),
        )
        .group_by(InteraccionSwipe.vacante_id)
        .subquery()
    )

    likes_empresa_subquery = (
        db.query(
            InteraccionSwipeEmpresa.vacante_id.label("vacante_id"),
            func.sum(
                case((InteraccionSwipeEmpresa.interes_empresa.is_(True), 1), else_=0)
            ).label("total_likes_empresa"),
            func.max(
                case(
                    (InteraccionSwipeEmpresa.interes_empresa.is_(True), InteraccionSwipeEmpresa.fecha),
                    else_=None,
                )
            ).label("ultimo_like_empresa"),
        )
        .group_by(InteraccionSwipeEmpresa.vacante_id)
        .subquery()
    )

    matches_subquery = (
        db.query(
            Match.vacante_id.label("vacante_id"),
            func.count(Match.id).label("total_matches"),
        )
        .group_by(Match.vacante_id)
        .subquery()
    )

    rows = (
        db.query(
            Vacante,
            visualizaciones_subquery.c.total_visualizaciones,
            visualizaciones_subquery.c.total_estudiantes_que_vieron,
            visualizaciones_subquery.c.ultima_visualizacion,
            likes_estudiante_subquery.c.total_likes_estudiantes,
            likes_estudiante_subquery.c.ultimo_like_estudiante,
            likes_empresa_subquery.c.total_likes_empresa,
            likes_empresa_subquery.c.ultimo_like_empresa,
            matches_subquery.c.total_matches,
        )
        .outerjoin(visualizaciones_subquery, visualizaciones_subquery.c.vacante_id == Vacante.id)
        .outerjoin(likes_estudiante_subquery, likes_estudiante_subquery.c.vacante_id == Vacante.id)
        .outerjoin(likes_empresa_subquery, likes_empresa_subquery.c.vacante_id == Vacante.id)
        .outerjoin(matches_subquery, matches_subquery.c.vacante_id == Vacante.id)
        .filter(Vacante.empresa_id == empresa_id)
        .order_by(Vacante.fecha_publicacion.desc(), Vacante.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    historial: list[VacanteHistorialEmpresa] = []
    for row in rows:
        (
            vacante,
            total_visualizaciones,
            total_estudiantes_que_vieron,
            ultima_visualizacion,
            total_likes_estudiantes,
            ultimo_like_estudiante,
            total_likes_empresa,
            ultimo_like_empresa,
            total_matches,
        ) = row

        historial.append(
            VacanteHistorialEmpresa(
                id=vacante.id,
                empresa_id=vacante.empresa_id,
                titulo=vacante.titulo,
                descripcion=vacante.descripcion,
                requisitos=vacante.requisitos,
                tipo_contrato=vacante.tipo_contrato,
                modalidad=vacante.modalidad,
                ubicacion=vacante.ubicacion,
                sueldo_minimo=float(vacante.sueldo_minimo) if vacante.sueldo_minimo is not None else None,
                sueldo_maximo=float(vacante.sueldo_maximo) if vacante.sueldo_maximo is not None else None,
                moneda=vacante.moneda,
                estado=vacante.estado,
                fecha_publicacion=vacante.fecha_publicacion,
                total_visualizaciones=int(total_visualizaciones or 0),
                total_estudiantes_que_vieron=int(total_estudiantes_que_vieron or 0),
                total_likes_estudiantes=int(total_likes_estudiantes or 0),
                total_likes_empresa=int(total_likes_empresa or 0),
                total_matches=int(total_matches or 0),
                ultima_visualizacion=ultima_visualizacion,
                ultimo_like_estudiante=ultimo_like_estudiante,
                ultimo_like_empresa=ultimo_like_empresa,
            )
        )

    return historial
