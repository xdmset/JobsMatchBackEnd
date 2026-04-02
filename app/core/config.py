from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "JOBMATCH"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: str = ""
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_SECRET: str | None = None
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Configuraciones de MinIO
    minio_endpoint: str = "localhost:9000"
    minio_public_endpoint: str = "localhost:9000"
    minio_access_key: str = "admin"
    minio_secret_key: str = "password123"
    minio_bucket_name: str = "uploads"
    use_ssl: bool = False
    media_url_expiration_seconds: int = 3600
    max_image_upload_bytes: int = 5 * 1024 * 1024
    max_document_upload_bytes: int = 10 * 1024 * 1024

    PAYPAL_CLIENT_ID: str = ""
    PAYPAL_SECRET: str = ""
    PAYPAL_BASE_URL: str = "https://api-m.sandbox.paypal.com"
    PAYPAL_WEBHOOK_ID: str = ""
    PAYPAL_WEB_RETURN_URL: str = "http://localhost:3000/payments/paypal/success"
    PAYPAL_WEB_CANCEL_URL: str = "http://localhost:3000/payments/paypal/cancel"
    PAYPAL_CURRENCY: str = "USD"
    PAYPAL_PRODUCT_NAME: str = "JOBMATCH Premium"
    PAYPAL_PRODUCT_DESCRIPTION: str = "Suscripciones premium de JOBMATCH"
    PAYPAL_MONTHLY_PRICE: float = 9.99
    PAYPAL_SEMIANNUAL_PRICE: float = 49.99
    PAYPAL_ANNUAL_PRICE: float = 89.99

    class Config:
        env_file = ".env"


settings = Settings()
if settings.REFRESH_TOKEN_SECRET is None:
    settings.REFRESH_TOKEN_SECRET = settings.SECRET_KEY
