from sqlalchemy.orm import Session
from app.models.perfil_empresa import PerfilEmpresa
from app.schemas.perfil_empresa import PerfilEmpresaCreate

def get_empresa(db: Session, user_id: int):
    return db.query(PerfilEmpresa).filter(PerfilEmpresa.user_id == user_id).first()

def create_empresa(db: Session, empresa: PerfilEmpresaCreate, user_id: int):
    db_empresa = PerfilEmpresa(user_id=user_id, **empresa.dict())
    db.add(db_empresa)
    db.commit()
    db.refresh(db_empresa)
    return db_empresa

def update_empresa(db: Session, user_id: int, empresa_data: PerfilEmpresaCreate):
    db_empresa = get_empresa(db, user_id)
    if db_empresa:
        for field, value in empresa_data.dict(exclude_unset=True).items():
            setattr(db_empresa, field, value)
        db.commit()
        db.refresh(db_empresa)
    return db_empresa

def delete_empresa(db: Session, user_id: int):
    db_empresa = get_empresa(db, user_id)
    if db_empresa:
        db.delete(db_empresa)
        db.commit()
    return db_empresa
