from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import crud_retroalimentacion, crud_postulacion
from app.db.session import get_db
from app.schemas.retroalimentacion import (
    RetroalimentacionCreate,
    RetroalimentacionRead,
    RetroalimentacionUpdate,
)

router = APIRouter()


@router.get("/{retroalimentacion_id}", response_model=RetroalimentacionRead)
def read_retroalimentacion(retroalimentacion_id: int, db: Session = Depends(get_db)):
    retroalimentacion = crud_retroalimentacion.get_retroalimentacion(db, retroalimentacion_id)
    if not retroalimentacion:
        raise HTTPException(status_code=404, detail="Retroalimentacion no encontrada")
    return retroalimentacion


@router.get("/postulacion/{postulacion_id}", response_model=RetroalimentacionRead)
def read_retroalimentacion_by_postulacion(postulacion_id: int, db: Session = Depends(get_db)):
    retroalimentacion = crud_retroalimentacion.get_retroalimentacion_by_postulacion(
        db, postulacion_id
    )
    if not retroalimentacion:
        raise HTTPException(status_code=404, detail="Retroalimentacion no encontrada")
    return retroalimentacion


@router.post("/", response_model=RetroalimentacionRead)
def create_new_retroalimentacion(
    retroalimentacion: RetroalimentacionCreate,
    db: Session = Depends(get_db),
):
    postulacion = crud_postulacion.get_postulacion(db, retroalimentacion.postulacion_id)
    if not postulacion:
        raise HTTPException(status_code=404, detail="Postulacion no encontrada")

    existing = crud_retroalimentacion.get_retroalimentacion_by_postulacion(
        db, retroalimentacion.postulacion_id
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Ya existe retroalimentacion para esta postulacion",
        )

    return crud_retroalimentacion.create_retroalimentacion(db, retroalimentacion)


@router.put("/{retroalimentacion_id}", response_model=RetroalimentacionRead)
def update_existing_retroalimentacion(
    retroalimentacion_id: int,
    retroalimentacion: RetroalimentacionUpdate,
    db: Session = Depends(get_db),
):
    existing = crud_retroalimentacion.get_retroalimentacion(db, retroalimentacion_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Retroalimentacion no encontrada")
    return crud_retroalimentacion.update_retroalimentacion(db, existing, retroalimentacion)


@router.delete("/{retroalimentacion_id}", response_model=RetroalimentacionRead)
def delete_existing_retroalimentacion(
    retroalimentacion_id: int,
    db: Session = Depends(get_db),
):
    existing = crud_retroalimentacion.get_retroalimentacion(db, retroalimentacion_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Retroalimentacion no encontrada")
    return crud_retroalimentacion.delete_retroalimentacion(db, existing)
