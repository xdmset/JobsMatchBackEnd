from sqlalchemy.orm import Session
from app.models.perfil_empresa import PerfilEmpresa
from app.schemas.perfil_empresa import PerfilEmpresaCreate

def get_empresa(db: Session, usuario_id: int):
    """Busca una empresa por su usuario_id (PK compartida)."""
    return db.query(PerfilEmpresa).filter(PerfilEmpresa.usuario_id == usuario_id).first()

def create_empresa(db: Session, empresa: PerfilEmpresaCreate, usuario_id: int):
    """Crea el perfil de empresa vinculado al usuario_id."""
    db_empresa = PerfilEmpresa(usuario_id=usuario_id, **empresa.model_dump())
    db.add(db_empresa)
    db.commit()
    db.refresh(db_empresa)
    return db_empresa

def update_empresa(db: Session, usuario_id: int, empresa_data: PerfilEmpresaCreate):
    """Actualiza los datos de la empresa usando el nuevo estándar model_dump."""
    db_empresa = get_empresa(db, usuario_id)
    if db_empresa:
        for field, value in empresa_data.model_dump(exclude_unset=True).items():
            setattr(db_empresa, field, value)
        db.commit()
        db.refresh(db_empresa)
    return db_empresa

def delete_empresa(db: Session, usuario_id: int):
    """Elimina el perfil de empresa."""
    db_empresa = get_empresa(db, usuario_id)
    if db_empresa:
        db.delete(db_empresa)
        db.commit()
    return db_empresa