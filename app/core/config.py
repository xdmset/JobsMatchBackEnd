from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):

    PROJECT_NAME: str = "JOBMATCH"
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


    #CONFIGURACIONES DE MINIO

    #Cambiar siguiente paso,despues del login/logout
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "admin"
    minio_secret_key: str = "password123"
    minio_bucket_name: str = "uploads"
    use_ssl: bool = False




    class Config:
        env_file = ".env"


settings = Settings()