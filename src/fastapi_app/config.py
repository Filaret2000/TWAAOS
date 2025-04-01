import os
from pydantic import BaseSettings
from datetime import timedelta

class Settings(BaseSettings):
    # Configurare aplicație
    APP_NAME: str = "Sistem Planificare Examene FIESC"
    API_PREFIX: str = "/api"
    DEBUG: bool = os.environ.get("DEBUG", "False") == "True"
    
    # Configurare bază de date
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "postgresql://fiesc_admin:secure_password@db:5432/exam_scheduling")
    
    # Configurare JWT
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev_key_for_development_only")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 oră
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # 30 zile
    
    # Configurare Google OAuth
    GOOGLE_OAUTH_CLIENT_ID: str = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "")
    GOOGLE_OAUTH_CLIENT_SECRET: str = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", "")
    
    # Configurare SendGrid
    SENDGRID_API_KEY: str = os.environ.get("SENDGRID_API_KEY", "")
    EMAIL_FROM: str = os.environ.get("EMAIL_FROM", "planificare@fiesc.usv.ro")
    EMAIL_FROM_NAME: str = os.environ.get("EMAIL_FROM_NAME", "Planificare Examene FIESC")
    
    # Configurare CORS
    CORS_ORIGINS: list = [
        "http://localhost",
        "http://localhost:8080",
        "http://localhost:5000",
    ]
    
    # Configurare perioade examene (implicit)
    DEFAULT_EXAM_START_DATE: str = "2025-01-15"
    DEFAULT_EXAM_END_DATE: str = "2025-01-30"
    DEFAULT_COLLOQUIUM_START_DATE: str = "2025-01-05"
    DEFAULT_COLLOQUIUM_END_DATE: str = "2025-01-14"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Instanță singleton pentru configurare
settings = Settings()

# Funcție pentru a obține configurarea
def get_settings():
    return settings
