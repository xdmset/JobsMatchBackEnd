from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    perfil_empresa,
    perfil_estudiante,
    postulaciones,
    retroalimentacion,
    rol,
    suscripcion,
    swipes,
    user,
    vacante,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(rol.router, prefix="/rol", tags=["Rol"])
api_router.include_router(user.router, prefix="/user", tags=["User"])
api_router.include_router(perfil_estudiante.router, prefix="/perfil_estudiante", tags=["Perfil_Estudiante"])
api_router.include_router(perfil_empresa.router, prefix="/perfil_empresa", tags=["Perfil_Empresa"])
api_router.include_router(vacante.router, prefix="/vacante", tags=["Vacante"])
api_router.include_router(swipes.router, prefix="/swipes", tags=["Swipes"])
api_router.include_router(postulaciones.router, prefix="/postulaciones", tags=["Postulaciones"])
api_router.include_router(suscripcion.router, prefix="/suscripciones", tags=["Suscripciones"])
api_router.include_router(
    retroalimentacion.router,
    prefix="/retroalimentacion",
    tags=["Retroalimentacion"],
)
