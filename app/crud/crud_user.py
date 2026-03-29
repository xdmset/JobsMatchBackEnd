from sqlalchemy.orm import Session
from app.models.interaccion_swipe import InteraccionSwipe
from app.models.interaccion_swipe_empresa import InteraccionSwipeEmpresa
from app.models.match import Match
from app.models.perfil_empresa import PerfilEmpresa
from app.models.perfil_estudiante import PerfilEstudiante
from app.models.postulacion import Postulacion
from app.models.retroalimentacion import Retroalimentacion
from app.models.user import User
from app.models.vacante import Vacante
from app.models.vacante_visualizacion import VacanteVisualizacion
from app.schemas.user import UserCreate
from app.services.subscription_service import create_default_subscription_for_user
from app.services.user_registration import create_profile_for_user

def get_user(db: Session, user_id: int):
    """Obtiene un usuario por su ID."""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    """Busca un usuario por su correo electrónico."""
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Lista usuarios con paginación."""
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate, hashed_password: str):
    """Crea un usuario y su perfil correspondiente según el rol."""
    db_user = User(
        email=user.email,
        password_hash=hashed_password,
        rol_id=user.rol_id,
        es_premium=False,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    create_profile_for_user(db, db_user, user)
    create_default_subscription_for_user(db, db_user.id)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    """Elimina un usuario de la base de datos."""
    db_user = get_user(db, user_id)
    if db_user:
        vacante_ids = [
            vacante_id
            for (vacante_id,) in db.query(Vacante.id).filter(Vacante.empresa_id == user_id).all()
        ]

        postulacion_ids = [
            postulacion_id
            for (postulacion_id,) in db.query(Postulacion.id).filter(
                (Postulacion.estudiante_id == user_id) | (Postulacion.empresa_id == user_id)
            ).all()
        ]

        if postulacion_ids:
            db.query(Retroalimentacion).filter(
                Retroalimentacion.postulacion_id.in_(postulacion_ids)
            ).delete(synchronize_session=False)

        db.query(Postulacion).filter(
            (Postulacion.estudiante_id == user_id) | (Postulacion.empresa_id == user_id)
        ).delete(synchronize_session=False)

        if vacante_ids:
            db.query(VacanteVisualizacion).filter(
                VacanteVisualizacion.vacante_id.in_(vacante_ids)
            ).delete(synchronize_session=False)
            db.query(InteraccionSwipe).filter(
                InteraccionSwipe.vacante_id.in_(vacante_ids)
            ).delete(synchronize_session=False)
            db.query(InteraccionSwipeEmpresa).filter(
                InteraccionSwipeEmpresa.vacante_id.in_(vacante_ids)
            ).delete(synchronize_session=False)
            db.query(Match).filter(
                Match.vacante_id.in_(vacante_ids)
            ).delete(synchronize_session=False)
            db.query(Vacante).filter(
                Vacante.id.in_(vacante_ids)
            ).delete(synchronize_session=False)

        db.query(VacanteVisualizacion).filter(
            VacanteVisualizacion.estudiante_id == user_id
        ).delete(synchronize_session=False)
        db.query(InteraccionSwipe).filter(
            InteraccionSwipe.estudiante_id == user_id
        ).delete(synchronize_session=False)
        db.query(InteraccionSwipeEmpresa).filter(
            (InteraccionSwipeEmpresa.estudiante_id == user_id) | (InteraccionSwipeEmpresa.empresa_id == user_id)
        ).delete(synchronize_session=False)
        db.query(Match).filter(
            Match.estudiante_id == user_id
        ).delete(synchronize_session=False)
        db.query(PerfilEstudiante).filter(
            PerfilEstudiante.usuario_id == user_id
        ).delete(synchronize_session=False)
        db.query(PerfilEmpresa).filter(
            PerfilEmpresa.usuario_id == user_id
        ).delete(synchronize_session=False)

        db.delete(db_user)
        db.commit()
    return db_user
