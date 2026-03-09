from pydantic import BaseModel


class MediaUploadResponse(BaseModel):
    usuario_id: int
    media_type: str
    object_name: str
    bucket: str
    url: str
    content_type: str
    size: int


class MediaAccessResponse(BaseModel):
    usuario_id: int
    media_type: str
    object_name: str
    url: str
    expires_in_seconds: int
