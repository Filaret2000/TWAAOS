from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import datetime

from src.common.models import User
from src.common.services import AuthService
from src.flask_app.utils.db import get_db_session
from src.flask_app.utils.decorators import role_required

# Creăm blueprint-ul pentru autentificare
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Endpoint pentru autentificare cu Google OAuth
    
    Request:
    {
        "token": "google_oauth_token"
    }
    
    Response:
    {
        "access_token": "jwt_token",
        "token_type": "bearer",
        "expires_in": 3600,
        "user": {
            "id": 123,
            "email": "user@usv.ro",
            "role": "SEC",
            "firstName": "Nume",
            "lastName": "Prenume"
        }
    }
    """
    # Obținem token-ul Google OAuth din request
    data = request.get_json()
    
    if not data or 'token' not in data:
        return jsonify({"error": "Token Google OAuth lipsă"}), 400
    
    google_token = data['token']
    
    # Inițializăm serviciul de autentificare
    db_session = get_db_session()
    auth_service = AuthService(
        db_session=db_session,
        secret_key=current_app.config['JWT_SECRET_KEY'],
        token_expire_minutes=60
    )
    
    # Verificăm token-ul Google OAuth
    user_info = auth_service.verify_google_token(google_token)
    
    if not user_info:
        return jsonify({"error": "Token Google OAuth invalid"}), 401
    
    # Obținem utilizatorul după email
    email = user_info.get('email')
    user = auth_service.get_user_by_email(email)
    
    if not user:
        # Verificăm dacă email-ul este valid pentru aplicație
        if not email.endswith('@usv.ro') and not email.endswith('@student.usv.ro'):
            return jsonify({"error": "Email invalid pentru aplicație"}), 401
        
        # Determinăm rolul utilizatorului
        role = 'SG' if email.endswith('@student.usv.ro') else 'CD'
        
        # Creăm un utilizator nou
        user = auth_service.create_user(
            email=email,
            first_name=user_info.get('given_name', ''),
            last_name=user_info.get('family_name', ''),
            role=role
        )
        
        if not user:
            return jsonify({"error": "Eroare la crearea utilizatorului"}), 500
    
    # Generăm token-ul JWT
    token, expires = auth_service.generate_token(user)
    
    # Calculăm timpul de expirare în secunde
    expires_in = int((expires - datetime.datetime.utcnow()).total_seconds())
    
    # Returnăm răspunsul
    return jsonify({
        "access_token": token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "firstName": user.first_name,
            "lastName": user.last_name
        }
    })

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Endpoint pentru obținerea utilizatorului curent
    
    Response:
    {
        "id": 123,
        "email": "user@usv.ro",
        "role": "SEC",
        "firstName": "Nume",
        "lastName": "Prenume"
    }
    """
    # Obținem ID-ul utilizatorului din token
    user_id = get_jwt_identity()
    
    # Obținem utilizatorul din baza de date
    db_session = get_db_session()
    
    try:
        user = db_session.query(User).filter(User.id == user_id).first()
        
        if not user:
            return jsonify({"error": "Utilizator negăsit"}), 404
        
        # Returnăm informațiile utilizatorului
        return jsonify({
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "firstName": user.first_name,
            "lastName": user.last_name
        })
    except SQLAlchemyError as e:
        return jsonify({"error": f"Eroare la obținerea utilizatorului: {str(e)}"}), 500

@auth_bp.route('/admin/users', methods=['GET'])
@jwt_required()
@role_required('ADM')
def get_users():
    """
    Endpoint pentru obținerea tuturor utilizatorilor (doar pentru administrator)
    
    Response:
    [
        {
            "id": 123,
            "email": "user@usv.ro",
            "role": "SEC",
            "firstName": "Nume",
            "lastName": "Prenume"
        }
    ]
    """
    # Obținem toți utilizatorii din baza de date
    db_session = get_db_session()
    
    try:
        users = db_session.query(User).all()
        
        # Returnăm lista de utilizatori
        return jsonify([{
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "firstName": user.first_name,
            "lastName": user.last_name
        } for user in users])
    except SQLAlchemyError as e:
        return jsonify({"error": f"Eroare la obținerea utilizatorilor: {str(e)}"}), 500

@auth_bp.route('/admin/users', methods=['POST'])
@jwt_required()
@role_required('ADM')
def create_user():
    """
    Endpoint pentru crearea unui utilizator nou (doar pentru administrator)
    
    Request:
    {
        "email": "user@usv.ro",
        "firstName": "Nume",
        "lastName": "Prenume",
        "role": "SEC",
        "password": "parola" (opțional, doar pentru administrator)
    }
    
    Response:
    {
        "id": 123,
        "email": "user@usv.ro",
        "role": "SEC",
        "firstName": "Nume",
        "lastName": "Prenume"
    }
    """
    # Obținem datele utilizatorului din request
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Date lipsă"}), 400
    
    # Validăm datele
    required_fields = ['email', 'firstName', 'lastName', 'role']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Câmpul '{field}' lipsește"}), 400
    
    # Validăm rolul
    valid_roles = ['SEC', 'SG', 'CD', 'ADM']
    if data['role'] not in valid_roles:
        return jsonify({"error": f"Rol invalid. Rolurile valide sunt: {', '.join(valid_roles)}"}), 400
    
    # Inițializăm serviciul de autentificare
    db_session = get_db_session()
    auth_service = AuthService(
        db_session=db_session,
        secret_key=current_app.config['JWT_SECRET_KEY']
    )
    
    # Verificăm dacă utilizatorul există deja
    existing_user = auth_service.get_user_by_email(data['email'])
    if existing_user:
        return jsonify({"error": "Utilizatorul există deja"}), 409
    
    # Creăm utilizatorul
    user = auth_service.create_user(
        email=data['email'],
        first_name=data['firstName'],
        last_name=data['lastName'],
        role=data['role']
    )
    
    if not user:
        return jsonify({"error": "Eroare la crearea utilizatorului"}), 500
    
    # Setăm parola dacă este furnizată și utilizatorul este administrator
    if 'password' in data and data['role'] == 'ADM':
        user.set_password(data['password'])
        db_session.commit()
    
    # Returnăm informațiile utilizatorului creat
    return jsonify({
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "firstName": user.first_name,
        "lastName": user.last_name
    }), 201

@auth_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@role_required('ADM')
def update_user(user_id):
    """
    Endpoint pentru actualizarea unui utilizator (doar pentru administrator)
    
    Request:
    {
        "firstName": "Nume",
        "lastName": "Prenume",
        "role": "SEC",
        "password": "parola" (opțional, doar pentru administrator)
    }
    
    Response:
    {
        "id": 123,
        "email": "user@usv.ro",
        "role": "SEC",
        "firstName": "Nume",
        "lastName": "Prenume"
    }
    """
    # Obținem datele utilizatorului din request
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Date lipsă"}), 400
    
    # Obținem utilizatorul din baza de date
    db_session = get_db_session()
    
    try:
        user = db_session.query(User).filter(User.id == user_id).first()
        
        if not user:
            return jsonify({"error": "Utilizator negăsit"}), 404
        
        # Actualizăm datele utilizatorului
        if 'firstName' in data:
            user.first_name = data['firstName']
        
        if 'lastName' in data:
            user.last_name = data['lastName']
        
        if 'role' in data:
            # Validăm rolul
            valid_roles = ['SEC', 'SG', 'CD', 'ADM']
            if data['role'] not in valid_roles:
                return jsonify({"error": f"Rol invalid. Rolurile valide sunt: {', '.join(valid_roles)}"}), 400
            
            user.role = data['role']
        
        # Setăm parola dacă este furnizată și utilizatorul este administrator
        if 'password' in data and user.role == 'ADM':
            user.set_password(data['password'])
        
        db_session.commit()
        
        # Returnăm informațiile utilizatorului actualizat
        return jsonify({
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "firstName": user.first_name,
            "lastName": user.last_name
        })
    except SQLAlchemyError as e:
        db_session.rollback()
        return jsonify({"error": f"Eroare la actualizarea utilizatorului: {str(e)}"}), 500

@auth_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@role_required('ADM')
def delete_user(user_id):
    """
    Endpoint pentru ștergerea unui utilizator (doar pentru administrator)
    
    Response:
    {
        "message": "Utilizator șters cu succes"
    }
    """
    # Obținem utilizatorul din baza de date
    db_session = get_db_session()
    
    try:
        user = db_session.query(User).filter(User.id == user_id).first()
        
        if not user:
            return jsonify({"error": "Utilizator negăsit"}), 404
        
        # Ștergem utilizatorul
        db_session.delete(user)
        db_session.commit()
        
        # Returnăm mesajul de succes
        return jsonify({
            "message": "Utilizator șters cu succes"
        })
    except SQLAlchemyError as e:
        db_session.rollback()
        return jsonify({"error": f"Eroare la ștergerea utilizatorului: {str(e)}"}), 500
