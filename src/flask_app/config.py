import os
from datetime import timedelta

class Config:
    # Configurare Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key_for_development_only')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False') == 'True'
    
    # Configurare bază de date
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://fiesc_admin:secure_password@db:5432/exam_scheduling')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurare JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Configurare Google OAuth
    GOOGLE_OAUTH_CLIENT_ID = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
    GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')
    
    # Configurare SendGrid
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    EMAIL_FROM = os.environ.get('EMAIL_FROM', 'planificare@fiesc.usv.ro')
    EMAIL_FROM_NAME = os.environ.get('EMAIL_FROM_NAME', 'Planificare Examene FIESC')
    
    # Configurare upload fișiere
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    
    # Configurare perioade examene (implicit)
    DEFAULT_EXAM_START_DATE = '2025-01-15'
    DEFAULT_EXAM_END_DATE = '2025-01-30'
    DEFAULT_COLLOQUIUM_START_DATE = '2025-01-05'
    DEFAULT_COLLOQUIUM_END_DATE = '2025-01-14'

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    
    # În producție, asigurați-vă că SECRET_KEY este setat în variabilele de mediu
    # și nu este hardcodat în cod
    
    # Configurare HTTPS
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    
class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
# Configurare în funcție de mediu
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

# Configurare implicită
Config = config_by_name[os.environ.get('FLASK_ENV', 'development')]
