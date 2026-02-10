from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from app.db.session import get_db
from app.schemas.match import (
    SwipeCreate, MatchResponse, PostulacionRead, CambiarEstadoPostulacion
)
from app.models.match import InteraccionSwipe, Match, Postulacion, Retroalimentacion
from app.models.vacante import Vacante
from app.models.user import User

router = APIRouter()

@router.post("/swipe/{estudiante_id}", response_model=Optional[MatchResponse])
def registrar_swipe(estudiante_id: int, swipe: SwipeCreate, db: Session = Depends(get_db)):
    # 1. Verificar Límite Freemium (RF-07)
    usuario = db.query(User).filter(User.id == estudiante_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if not usuario.es_premium:
        hoy = date.today()
        conteo_hoy = db.query(InteraccionSwipe).filter(
            InteraccionSwipe.estudiante_id == estudiante_id,
            func.date(InteraccionSwipe.fecha) == hoy
        ).count()
        
        if conteo_hoy >= 10:
            raise HTTPException(status_code=403, detail="Límite de swipes diarios alcanzado. ¡Hazte Premium!")

    # 2. Registrar Interacción
    nueva_interaccion = InteraccionSwipe(
        estudiante_id=estudiante_id,
        vacante_id=swipe.vacante_id,
        interes_estudiante=swipe.interes_estudiante
    )
    db.add(nueva_interaccion)
    
    match_confirmado = None

    # 3. Lógica de Match y Postulación Automática (RF-05, RF-06)
    if swipe.interes_estudiante:
        match_confirmado = Match(estudiante_id=estudiante_id, vacante_id=swipe.vacante_id)
        db.add(match_confirmado)
        db.flush() 

        nueva_postulacion = Postulacion(match_id=match_confirmado.id, estado='enviado')
        db.add(nueva_postulacion)
    
    db.commit()
    if match_confirmado:
        db.refresh(match_confirmado)
    return match_confirmado

@router.get("/empresa/{empresa_id}/postulaciones", response_model=List[PostulacionRead])
def listar_postulaciones_empresa(empresa_id: int, db: Session = Depends(get_db)):
    """RF-06: Permite a la empresa ver quiénes han aplicado a sus vacantes."""
    return db.query(Postulacion).join(Match).join(Vacante).filter(
        Vacante.empresa_id == empresa_id
    ).all()

@router.put("/postulacion/{postulacion_id}/estado")
def actualizar_estado(postulacion_id: int, data: CambiarEstadoPostulacion, db: Session = Depends(get_db)):
    """RF-06 y RF-11: Cambia el estado y agrega feedback si es rechazo."""
    postulacion = db.query(Postulacion).filter(Postulacion.id == postulacion_id).first()
    if not postulacion:
        raise HTTPException(status_code=404, detail="Postulación no encontrada")
    
    postulacion.estado = data.nuevo_estado
    
    if data.nuevo_estado == "rechazado" and data.feedback:
        nueva_retro = Retroalimentacion(
            postulacion_id=postulacion_id,
            campos_mejora=data.feedback.campos_mejora,
            sugerencias_perfil=data.feedback.sugerencias_perfil
        )
        db.add(nueva_retro)
    
    db.commit()
    return {"message": "Estado actualizado con éxito"}