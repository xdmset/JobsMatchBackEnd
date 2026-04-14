from __future__ import annotations

import re
from typing import Iterable

from sqlalchemy.exc import DataError


ENUM_COLUMN_VALUES: dict[tuple[str, str], tuple[str, ...]] = {
    ("perfiles_estudiantes", "modalidad_preferida"): ("remoto", "presencial", "hibrido"),
    ("vacantes", "modalidad"): ("remoto", "presencial", "hibrido"),
    ("vacantes", "estado"): ("activa", "pausada", "cerrada"),
    ("postulaciones", "source"): ("app_swipe", "web_apply"),
    ("postulaciones", "estado"): ("enviado", "visto", "en_proceso", "rechazado", "aceptado"),
}


def build_enum_data_error_detail(exc: DataError) -> str | None:
    column = _extract_column_name(exc)
    table = _extract_table_name(exc)

    if not column or not table:
        return None

    allowed_values = ENUM_COLUMN_VALUES.get((table, column))
    if not allowed_values:
        return None

    return (
        f"Valor invalido para '{column}'. "
        f"Valores permitidos: {', '.join(allowed_values)}."
    )


def _extract_column_name(exc: DataError) -> str | None:
    message = _collect_error_messages(exc)
    match = re.search(r"Data truncated for column '([^']+)'", message)
    if match:
        return match.group(1)
    return None


def _extract_table_name(exc: DataError) -> str | None:
    statement = getattr(exc, "statement", None) or ""
    patterns = (
        r"INSERT INTO\s+([a-zA-Z_]+)",
        r"UPDATE\s+([a-zA-Z_]+)",
    )

    for pattern in patterns:
        match = re.search(pattern, statement, flags=re.IGNORECASE)
        if match:
            return match.group(1).lower()
    return None


def _collect_error_messages(exc: DataError) -> str:
    parts: list[str] = []

    orig = getattr(exc, "orig", None)
    if orig is not None:
        parts.append(" ".join(str(item) for item in getattr(orig, "args", ()) if item))

    parts.append(str(exc))
    return " ".join(_non_empty(parts))


def _non_empty(values: Iterable[str]) -> list[str]:
    return [value for value in values if value]
