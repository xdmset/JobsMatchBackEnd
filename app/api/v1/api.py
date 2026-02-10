from fastapi import APIRouter
# Añade "match" al final de la importación
from app.api.v1.endpoints import rol, user, perfil_estudiante, perfil_empresa, vacante, match

api_router = APIRouter()
api_router.include_router(rol.router, prefix="/rol", tags=["Rol"])
api_router.include_router(user.router, prefix="/user", tags=["User"])
api_router.include_router(perfil_estudiante.router, prefix="/perfil_estudiante", tags=["Perfil_Estudiante"])
api_router.include_router(perfil_empresa.router, prefix="/perfil_empresa", tags=["Perfil_Empresa"])
api_router.include_router(vacante.router, prefix="/vacante", tags=["Vacante"])

# Agrega esta línea para activar el motor de Swipe y Matches
api_router.include_router(match.router, prefix="/matches", tags=["Matches"])