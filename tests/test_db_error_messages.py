from sqlalchemy.exc import DataError

from app.core.db_error_messages import build_enum_data_error_detail


def test_build_enum_data_error_detail_returns_message_for_known_enum():
    exc = DataError(
        statement=(
            "INSERT INTO perfiles_estudiantes (modalidad_preferida) "
            "VALUES (%(modalidad_preferida)s)"
        ),
        params={"modalidad_preferida": "virtual"},
        orig=Exception(1265, "Data truncated for column 'modalidad_preferida' at row 1"),
    )

    detail = build_enum_data_error_detail(exc)

    assert detail == (
        "Valor invalido para 'modalidad_preferida'. "
        "Valores permitidos: remoto, presencial, hibrido."
    )


def test_build_enum_data_error_detail_returns_none_for_unknown_column():
    exc = DataError(
        statement="INSERT INTO usuarios (email) VALUES (%(email)s)",
        params={"email": "ana@example.com"},
        orig=Exception(1265, "Data truncated for column 'email' at row 1"),
    )

    assert build_enum_data_error_detail(exc) is None
