import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import jwt
from datetime import datetime, timedelta

from fastapi_app.main import app
from fastapi_app.dependencies import get_db_session, get_current_user
from common.models.user import User

class TestFastAPIAuthAPI:
    """Teste pentru API-ul de autentificare FastAPI"""

    @pytest.fixture
    def client(self):
        """Creează un client de test pentru aplicația FastAPI"""
        return TestClient(app)
    
    @pytest.fixture
    def override_get_db_session(self, db_session):
        """Override pentru dependența get_db_session"""
        def _get_db_session():
            try:
                yield db_session
            finally:
                pass
        
        app.dependency_overrides[get_db_session] = _get_db_session
        yield
        app.dependency_overrides.pop(get_db_session)
    
    @pytest.fixture
    def override_get_current_user(self, test_user):
        """Override pentru dependența get_current_user"""
        async def _get_current_user():
            return test_user
        
        app.dependency_overrides[get_current_user] = _get_current_user
        yield
        app.dependency_overrides.pop(get_current_user)
    
    @pytest.fixture
    def override_get_admin_user(self, test_admin):
        """Override pentru dependența get_current_user cu un administrator"""
        async def _get_current_user():
            return test_admin
        
        app.dependency_overrides[get_current_user] = _get_current_user
        yield
        app.dependency_overrides.pop(get_current_user)
    
    @patch('fastapi_app.api.auth.AuthService.verify_google_token')
    def test_login(self, mock_verify_google_token, client, override_get_db_session, test_user):
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
        data = response.json()
        assert 'access_token' in data
        assert 'token_type' in data
        assert 'expires_in' in data
        assert 'user' in data
        assert data['user']['email'] == test_user.email
        assert data['user']['role'] == test_user.role
    
    def test_get_current_user_info(self, client, override_get_db_session, override_get_current_user, test_user):
        """Testează endpoint-ul pentru obținerea informațiilor utilizatorului curent"""
        # Facem un request către endpoint-ul pentru obținerea utilizatorului curent
        response = client.get('/api/auth/me')
        
        # Verificăm răspunsul
        assert response.status_code == 200
        data = response.json()
        assert data['id'] == test_user.id
        assert data['email'] == test_user.email
        assert data['role'] == test_user.role
        assert data['firstName'] == test_user.first_name
        assert data['lastName'] == test_user.last_name
    
    def test_get_users(self, client, override_get_db_session, override_get_admin_user, test_user):
        """Testează endpoint-ul pentru obținerea tuturor utilizatorilor"""
        # Facem un request către endpoint-ul pentru obținerea tuturor utilizatorilor
        response = client.get('/api/auth/users')
        
        # Verificăm răspunsul
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Verificăm dacă utilizatorul de test este în listă
        user_ids = [user['id'] for user in data]
        assert test_user.id in user_ids
    
    def test_get_users_as_non_admin(self, client, override_get_db_session, override_get_current_user):
        """Testează endpoint-ul pentru obținerea tuturor utilizatorilor ca non-administrator"""
        # Facem un request către endpoint-ul pentru obținerea tuturor utilizatorilor
        response = client.get('/api/auth/users')
        
        # Verificăm răspunsul (ar trebui să fie acces interzis)
        assert response.status_code == 403
        data = response.json()
        assert 'detail' in data
    
    @patch('fastapi_app.api.auth.AuthService.create_user')
    def test_create_user(self, mock_create_user, client, override_get_db_session, override_get_admin_user):
        """Testează endpoint-ul pentru crearea unui utilizator"""
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
            '/api/auth/users',
            json={
                'email': 'new_user@usv.ro',
                'firstName': 'New',
                'lastName': 'User',
                'role': 'CD'
            }
        )
        
        # Verificăm răspunsul
        assert response.status_code == 201
        data = response.json()
        assert data['email'] == 'new_user@usv.ro'
        assert data['firstName'] == 'New'
        assert data['lastName'] == 'User'
        assert data['role'] == 'CD'
    
    @patch('fastapi_app.api.auth.AuthService.get_user_by_email')
    def test_create_user_duplicate_email(self, mock_get_user_by_email, client, override_get_db_session, override_get_admin_user, test_user):
        """Testează endpoint-ul pentru crearea unui utilizator cu email duplicat"""
        # Mock-uim funcția de obținere a utilizatorului după email
        mock_get_user_by_email.return_value = test_user
        
        # Facem un request către endpoint-ul pentru crearea unui utilizator
        response = client.post(
            '/api/auth/users',
            json={
                'email': test_user.email,
                'firstName': 'New',
                'lastName': 'User',
                'role': 'CD'
            }
        )
        
        # Verificăm răspunsul (ar trebui să fie conflict)
        assert response.status_code == 409
        data = response.json()
        assert 'detail' in data
    
    @patch('fastapi_app.api.auth.AuthService.get_user_by_id')
    def test_update_user(self, mock_get_user_by_id, client, override_get_db_session, override_get_admin_user, test_user):
        """Testează endpoint-ul pentru actualizarea unui utilizator"""
        # Mock-uim funcția de obținere a utilizatorului după ID
        mock_get_user_by_id.return_value = test_user
        
        # Facem un request către endpoint-ul pentru actualizarea unui utilizator
        response = client.put(
            f'/api/auth/users/{test_user.id}',
            json={
                'firstName': 'Updated',
                'lastName': 'User',
                'role': 'SEC'
            }
        )
        
        # Verificăm răspunsul
        assert response.status_code == 200
        data = response.json()
        assert data['id'] == test_user.id
        assert data['email'] == test_user.email
        assert data['firstName'] == 'Updated'
        assert data['lastName'] == 'User'
        assert data['role'] == 'SEC'
    
    @patch('fastapi_app.api.auth.AuthService.get_user_by_id')
    def test_delete_user(self, mock_get_user_by_id, client, override_get_db_session, override_get_admin_user, test_user, db_session):
        """Testează endpoint-ul pentru ștergerea unui utilizator"""
        # Mock-uim funcția de obținere a utilizatorului după ID
        mock_get_user_by_id.return_value = test_user
        
        # Facem un request către endpoint-ul pentru ștergerea unui utilizator
        response = client.delete(f'/api/auth/users/{test_user.id}')
        
        # Verificăm răspunsul
        assert response.status_code == 204
