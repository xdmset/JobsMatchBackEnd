from fastapi import FastAPI
import logging
import time
from sqladmin import Admin
from sqlalchemy import text

from app.admin.views import UserAdmin
from app.api.v1.api import api_router # Aquí es donde incluiremos el router de media
from app.core.config import settings
from app.db.session import SessionLocal, engine, init_db
from app.services.storage_service import StorageService

logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME)

@app.on_event("startup")
def startup_event():
    for attempt in range(1, 16):
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            init_db()
            break
        except Exception as exc:
            logger.warning("Base de datos no disponible en startup (intento %s/15): %s", attempt, exc)
            time.sleep(2)
    else:
        raise RuntimeError("No fue posible conectar a MySQL durante el arranque")

    try:
        storage = StorageService()
        storage.ensure_bucket_exists()
    except Exception as exc:
        logger.warning("MinIO no disponible en startup: %s", exc)

# # 2. Configuración de SQLAdmin
# admin = Admin(app, engine)
# admin.add_view(UserAdmin)

# 3. Inclusión de Routers (La lógica de subida ya vive dentro de api_router)
app.include_router(api_router, prefix="/api/v1")
