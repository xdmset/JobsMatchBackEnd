from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración principal de la aplicación.

    Los valores por defecto permiten ejecutar el proyecto sin necesidad de
    variables de entorno, pero se pueden sobreescribir mediante un archivo
    .env o variables del sistema.
    """

    PROJECT_NAME: str = "JOBMATCH"
    DATABASE_URL: str = "mysql+pymysql://mysql:123Tamarindo@localhost:3306"
    SECRET_KEY: str = "123Tamarindo"


    #CONFIGURACIONES DE MINIO

    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "admin"
    minio_secret_key: str = "password123"
    minio_bucket_name: str = "uploads"
    use_ssl: bool = False




    class Config:
        env_file = ".env"


settings = Settings()