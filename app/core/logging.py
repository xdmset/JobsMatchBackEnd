import json
import logging
import sys
from datetime import datetime, timezone
from logging.config import dictConfig

from app.core.config import settings


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for key in ("request_id", "method", "path", "status_code", "duration_ms"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=True)


def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": "app.core.logging.JsonFormatter",
                }
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "stream": sys.stdout,
                    "formatter": "json",
                }
            },
            "root": {
                "level": settings.LOG_LEVEL.upper(),
                "handlers": ["default"],
            },
            "loggers": {
                "uvicorn": {"level": settings.LOG_LEVEL.upper(), "handlers": ["default"], "propagate": False},
                "uvicorn.error": {
                    "level": settings.LOG_LEVEL.upper(),
                    "handlers": ["default"],
                    "propagate": False,
                },
                "uvicorn.access": {
                    "level": settings.LOG_LEVEL.upper(),
                    "handlers": ["default"],
                    "propagate": False,
                },
            },
        }
    )
