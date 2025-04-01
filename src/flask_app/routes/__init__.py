from flask import Blueprint
from .auth import auth_bp
from .export import export_bp
from .upload import upload_bp
from .schedule import schedule_bp
from .notification import notification_bp

# Creăm blueprint-ul principal pentru API
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Înregistrăm toate blueprint-urile
api_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_bp.register_blueprint(export_bp, url_prefix='/export')
api_bp.register_blueprint(upload_bp, url_prefix='/upload')
api_bp.register_blueprint(schedule_bp, url_prefix='/schedules')
api_bp.register_blueprint(notification_bp, url_prefix='/notifications')

# Exportăm toate blueprint-urile pentru a fi utilizate în alte module
__all__ = [
    'api_bp',
    'auth_bp',
    'export_bp',
    'upload_bp',
    'schedule_bp',
    'notification_bp'
]
