import pytest
import json
import jwt
from datetime import datetime, timedelta
from unittest.mock import patch

from flask import Flask
from flask_jwt_extended import JWTManager

from common.models.user import User
from flask_app.routes.auth import auth_bp

class TestFlaskAuthAPI:
    """Teste pentru API-ul de autentificare Flask"""

    @pytest.fixture
    def app(self):
        """Creează o aplicație Flask pentru teste"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['JWT_SECRET_KEY'] = 'test_secret_key'
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
        
        # Inițializăm JWT
        jwt_manager = JWTManager(app)
        
        # Înregistrăm blueprint-ul de autentificare
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        
        # Configurăm un context de aplicație
        with app.app_context():
            yield app
    
    @pytest.fixture
    def client(self, app):
        """Creează un client de test pentru aplicația Flask"""
        return app.test_client()
    
    @pytest.fixture
    def auth_token(self, test_user, app):
        """Creează un token JWT pentru autentificare"""
        with app.app_context():
            expires = datetime.utcnow() + timedelta(hours=1)
            payload = {
                'sub': str(test_user.id),
                'exp': expires
            }
            token = jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')
            return token
    
    @patch('flask_app.routes.auth.AuthService.verify_google_token')
    def test_login(self, mock_verify_google_token, client, db_session, test_user):
        """Testează endpoint-ul de login"""
        # Mock-uim funcția de verificare a token-ului Google
        mock_verify_google_token.return_value = {
            'email': test_user.email,
            'given_name': test_user.first_name,
            'family_name': test_user.last_name
        }
        
        # Facem un request către endpoint-ul de login
        response = client.post(
            '/api/auth/login',
            json={'token': 'google_oauth_token'}
        )
        
        # Verificăm răspunsul
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'token_type' in data
        assert 'expires_in' in data
        assert 'user' in data
        assert data['user']['email'] == test_user.email
        assert data['user']['role'] == test_user.role
    
    def test_get_current_user(self, client, auth_token, test_user):
        """Testează endpoint-ul pentru obținerea utilizatorului curent"""
        # Facem un request către endpoint-ul pentru obținerea utilizatorului curent
        response = client.get(
            '/api/auth/me',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        # Verificăm răspunsul
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == test_user.id
        assert data['email'] == test_user.email
        assert data['role'] == test_user.role
        assert data['firstName'] == test_user.first_name
        assert data['lastName'] == test_user.last_name
    
    def test_get_users_as_admin(self, client, auth_token, test_admin, test_user):
        """Testează endpoint-ul pentru obținerea tuturor utilizatorilor ca administrator"""
        # Creăm un token pentru administrator
        with client.application.app_context():
            expires = datetime.utcnow() + timedelta(hours=1)
            payload = {
                'sub': str(test_admin.id),
                'exp': expires
            }
            admin_token = jwt.encode(payload, client.application.config['JWT_SECRET_KEY'], algorithm='HS256')
        
        # Facem un request către endpoint-ul pentru obținerea tuturor utilizatorilor
        response = client.get(
            '/api/auth/admin/users',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        # Verificăm răspunsul
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Verificăm dacă utilizatorul de test este în listă
        user_ids = [user['id'] for user in data]
        assert test_user.id in user_ids
    
    def test_get_users_as_non_admin(self, client, auth_token, test_user):
        """Testează endpoint-ul pentru obținerea tuturor utilizatorilor ca non-administrator"""
        # Facem un request către endpoint-ul pentru obținerea tuturor utilizatorilor
        response = client.get(
            '/api/auth/admin/users',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        # Verificăm răspunsul (ar trebui să fie acces interzis)
        assert response.status_code == 403
        data = json.loads(response.data)
        assert 'error' in data
    
    @patch('flask_app.routes.auth.AuthService.create_user')
    def test_create_user(self, mock_create_user, client, auth_token, test_admin, db_session):
        """Testează endpoint-ul pentru crearea unui utilizator"""
        # Creăm un token pentru administrator
        with client.application.app_context():
            expires = datetime.utcnow() + timedelta(hours=1)
            payload = {
                'sub': str(test_admin.id),
                'exp': expires
            }
            admin_token = jwt.encode(payload, client.application.config['JWT_SECRET_KEY'], algorithm='HS256')
        
        # Mock-uim funcția de creare a utilizatorului
        new_user = User(
            id=999,
            email='new_user@usv.ro',
            first_name='New',
            last_name='User',
            role='CD'
        )
        mock_create_user.return_value = new_user
        
        # Facem un request către endpoint-ul pentru crearea unui utilizator
        response = client.post(
            '/api/auth/admin/users',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                'email': 'new_user@usv.ro',
                'firstName': 'New',
                'lastName': 'User',
                'role': 'CD'
            }
        )
        
        # Verificăm răspunsul
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['email'] == 'new_user@usv.ro'
        assert data['firstName'] == 'New'
        assert data['lastName'] == 'User'
        assert data['role'] == 'CD'
    
    @patch('flask_app.routes.auth.AuthService.get_user_by_email')
    def test_create_user_duplicate_email(self, mock_get_user_by_email, client, auth_token, test_admin, test_user):
        """Testează endpoint-ul pentru crearea unui utilizator cu email duplicat"""
        # Creăm un token pentru administrator
        with client.application.app_context():
            expires = datetime.utcnow() + timedelta(hours=1)
            payload = {
                'sub': str(test_admin.id),
                'exp': expires
            }
            admin_token = jwt.encode(payload, client.application.config['JWT_SECRET_KEY'], algorithm='HS256')
        
        # Mock-uim funcția de obținere a utilizatorului după email
        mock_get_user_by_email.return_value = test_user
        
        # Facem un request către endpoint-ul pentru crearea unui utilizator
        response = client.post(
            '/api/auth/admin/users',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                'email': test_user.email,
                'firstName': 'New',
                'lastName': 'User',
                'role': 'CD'
            }
        )
        
        # Verificăm răspunsul (ar trebui să fie conflict)
        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'error' in data
