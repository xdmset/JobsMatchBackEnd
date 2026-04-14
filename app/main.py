import logging
import time
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DataError
from sqlalchemy import text

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.db_error_messages import build_enum_data_error_detail
from app.core.logging import configure_logging
from app.db.session import SessionLocal, init_db
from app.services.storage_service import StorageService

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME)


def _get_cors_origins() -> list[str]:
    origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
    return origins


cors_origins = _get_cors_origins()
if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.middleware("http")
async def add_request_logging(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", uuid4().hex)
    start = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.exception(
            "Unhandled request error",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "duration_ms": duration_ms,
            },
        )
        raise

    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        "Request completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(
        "HTTP exception",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": exc.status_code,
        },
    )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

#Fix ENUM API
@app.exception_handler(DataError)
async def data_error_handler(request: Request, exc: DataError):
    detail = build_enum_data_error_detail(exc)
    if detail:
        logger.warning(
            "Database enum validation error",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": 400,
                "detail": detail,
            },
        )
        return JSONResponse(status_code=400, content={"detail": detail})

    logger.exception(
        "Unhandled database data error",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": 500,
        },
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
#FINISH Fix ENUM API

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "Unhandled application exception",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": 500,
        },
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

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


@app.get("/health")
def health_check():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as exc:
        logger.warning("Health check failed: %s", exc)
        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "environment": settings.ENVIRONMENT,
                "database": "error",
            },
        )
    finally:
        db.close()

    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "database": db_status,
    }

# # 2. Configuración de SQLAdmin
# admin = Admin(app, engine)
# admin.add_view(UserAdmin)

# 3. Inclusión de Routers (La lógica de subida ya vive dentro de api_router)
app.include_router(api_router, prefix="/api/v1")
