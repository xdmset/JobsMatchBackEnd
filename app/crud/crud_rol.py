from sqlalchemy.orm import Session

from app.core.enums import NombreRol
from app.models.rol import Role as RoleModel

# Obtener todos los roles
def get_roles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(RoleModel).offset(skip).limit(limit).all()

# Obtener un rol por ID
def get_rol(db: Session, rol_id: int):
    return db.query(RoleModel).filter(RoleModel.id == rol_id).first()

# Crear un nuevo rol
def create_rol(db: Session, nombre: NombreRol):
    db_rol = RoleModel(nombre=nombre)
    db.add(db_rol)
    db.commit()
    db.refresh(db_rol)
    return db_rol

# Actualizar un rol
def update_rol(db: Session, rol_id: int, nombre: NombreRol):
    db_rol = get_rol(db, rol_id)
    if not db_rol:
        return None
    db_rol.nombre = nombre
    db.commit()
    db.refresh(db_rol)
    return db_rol

# Eliminar un rol
def delete_rol(db: Session, rol_id: int):
    db_rol = get_rol(db, rol_id)
    if not db_rol:
        return None
    db.delete(db_rol)
    db.commit()
    return db_rol
