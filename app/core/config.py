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
    PAYPAL_STUDENT_PRODUCT_NAME: str = "JOBMATCH Premium Estudiante"
    PAYPAL_STUDENT_PRODUCT_DESCRIPTION: str = "Suscripciones premium para estudiantes"
    PAYPAL_COMPANY_PRODUCT_NAME: str = "JOBMATCH Premium Empresa"
    PAYPAL_COMPANY_PRODUCT_DESCRIPTION: str = "Suscripciones premium para empresas"
    PAYPAL_STUDENT_MONTHLY_PRICE: float = 99.00
    PAYPAL_STUDENT_SEMIANNUAL_PRICE: float = 499.00
    PAYPAL_STUDENT_ANNUAL_PRICE: float = 899.00
    PAYPAL_COMPANY_MONTHLY_PRICE: float = 399.00
    PAYPAL_COMPANY_SEMIANNUAL_PRICE: float = 1999.00
    PAYPAL_COMPANY_ANNUAL_PRICE: float = 3599.00

    STUDENT_FREE_DAILY_SWIPES: int = 10
    STUDENT_PREMIUM_DAILY_SWIPES: int = 1000
    STUDENT_FREE_VIEW_HISTORY_LIMIT: int = 15
    STUDENT_PREMIUM_VIEW_HISTORY_LIMIT: int = 0
    STUDENT_FREE_MATCH_HISTORY_LIMIT: int = 10
    STUDENT_PREMIUM_MATCH_HISTORY_LIMIT: int = 0
    STUDENT_FREE_SEARCH_PRIORITY: int = 0
    STUDENT_PREMIUM_SEARCH_PRIORITY: int = 10

    COMPANY_FREE_ACTIVE_VACANCIES: int = 5
    COMPANY_PREMIUM_ACTIVE_VACANCIES: int = 50
    COMPANY_FREE_SEARCH_PRIORITY: int = 0
    COMPANY_PREMIUM_SEARCH_PRIORITY: int = 10

    class Config:
        env_file = ".env"


settings = Settings()
if settings.REFRESH_TOKEN_SECRET is None:
    settings.REFRESH_TOKEN_SECRET = settings.SECRET_KEY
