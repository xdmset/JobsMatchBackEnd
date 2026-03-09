from types import SimpleNamespace

from app.services import profile_media


def test_serialize_estudiante_profile_hides_storage_keys_and_resolves_urls(monkeypatch):
    monkeypatch.setattr(
        profile_media,
        "_safe_presigned_url",
        lambda object_name: f"http://localhost:9000/{object_name}" if object_name else None,
    )
    estudiante = SimpleNamespace(
        usuario_id=2,
        nombre_completo="Ana",
        institucion_educativa="UT",
        nivel_academico="Licenciatura",
        biografia="Bio",
        habilidades=["Python"],
        ubicacion="Tijuana",
        modalidad_preferida="remoto",
        cv_tipo_archivo="application/pdf",
        cv_storage_key="estudiantes/cv/2/file.pdf",
        cv_url=None,
        foto_perfil_storage_key="estudiantes/fotos/2/file.jpg",
        foto_perfil_url=None,
    )

    payload = profile_media.serialize_estudiante_profile(estudiante)

    assert payload["cv_url"] == "http://localhost:9000/estudiantes/cv/2/file.pdf"
    assert payload["foto_perfil_url"] == "http://localhost:9000/estudiantes/fotos/2/file.jpg"
    assert "cv_storage_key" not in payload
    assert "foto_perfil_storage_key" not in payload


def test_serialize_empresa_profile_uses_existing_url_when_no_storage_key(monkeypatch):
    monkeypatch.setattr(profile_media, "_safe_presigned_url", lambda object_name: None)
    empresa = SimpleNamespace(
        usuario_id=3,
        nombre_comercial="Empresa X",
        sector="TI",
        descripcion="Desc",
        sitio_web="https://example.com",
        ubicacion_sede="CDMX",
        foto_perfil_storage_key=None,
        foto_perfil_url="https://cdn.example.com/logo.png",
    )

    payload = profile_media.serialize_empresa_profile(empresa)

    assert payload["foto_perfil_url"] == "https://cdn.example.com/logo.png"
    assert "foto_perfil_storage_key" not in payload
