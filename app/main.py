from fastapi import FastAPI
from sqladmin import Admin

from app.admin.views import UserAdmin
from app.api.v1.api import api_router # Aquí es donde incluiremos el router de media
from app.core.config import settings
from app.db.session import engine, init_db
# from app.services.storage_service import StorageService # Importamos tu nuevo servicio

app = FastAPI(title=settings.PROJECT_NAME)

init_db()

# # 1. Evento de inicio para asegurar infraestructura
# @app.on_event("startup")
# async def startup_event():
#     # Inicializa la DB
#     init_db()
#     # Asegura que el bucket de MinIO existe antes de recibir peticiones
#     storage = StorageService()
#     await storage.ensure_bucket_exists()

# # 2. Configuración de SQLAdmin
# admin = Admin(app, engine)
# admin.add_view(UserAdmin)

# 3. Inclusión de Routers (La lógica de subida ya vive dentro de api_router)
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "status": "active",
        "author": "Camcapxi",
    }