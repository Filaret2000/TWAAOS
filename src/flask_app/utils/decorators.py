from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from sqlalchemy.orm import Session

from src.common.models import User
from src.flask_app.utils.db import get_db_session

def role_required(*roles):
    """
    Decorator pentru verificarea rolului utilizatorului
    
    Utilizare:
    @app.route('/admin')
    @jwt_required()
    @role_required('ADM')
    def admin():
        return jsonify({"message": "Admin access"})
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Verificăm token-ul JWT
            verify_jwt_in_request()
            
            # Obținem ID-ul utilizatorului din token
            user_id = get_jwt_identity()
            
            # Obținem utilizatorul din baza de date
            db_session = get_db_session()
            user = db_session.query(User).filter(User.id == user_id).first()
            
            # Verificăm dacă utilizatorul există
            if not user:
                return jsonify({"error": "Utilizator inexistent"}), 401
            
            # Verificăm dacă utilizatorul are rolul necesar
            if user.role not in roles:
                return jsonify({"error": "Acces interzis"}), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def validate_json(*required_fields):
    """
    Decorator pentru validarea datelor JSON din request
    
    Utilizare:
    @app.route('/api/users', methods=['POST'])
    @validate_json('name', 'email')
    def create_user():
        data = request.get_json()
        # Acum putem fi siguri că data conține 'name' și 'email'
        return jsonify({"message": "User created"})
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Verificăm dacă request-ul conține JSON
            if not request.is_json:
                return jsonify({"error": "Request-ul trebuie să fie în format JSON"}), 400
            
            # Obținem datele JSON
            data = request.get_json()
            
            # Verificăm dacă toate câmpurile necesare sunt prezente
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({
                    "error": "Câmpuri lipsă",
                    "missing_fields": missing_fields
                }), 400
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator
