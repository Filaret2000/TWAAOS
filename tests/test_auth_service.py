import pytest
import jwt
from datetime import datetime, timedelta

from common.services.auth_service import AuthService
from common.models.user import User

class TestAuthService:
    """Teste pentru AuthService"""

    def test_create_user(self, db_session):
        """Testează crearea unui utilizator"""
        # Inițializăm serviciul de autentificare
        auth_service = AuthService(db_session=db_session, secret_key="test_secret")
        
        # Creăm un utilizator nou
        user = auth_service.create_user(
            email="new_user@usv.ro",
            first_name="New",
            last_name="User",
            role="CD"
        )
        
        # Verificăm dacă utilizatorul a fost creat corect
        assert user is not None
        assert user.email == "new_user@usv.ro"
        assert user.first_name == "New"
        assert user.last_name == "User"
        assert user.role == "CD"
        
        # Verificăm dacă utilizatorul a fost adăugat în baza de date
        db_user = db_session.query(User).filter(User.email == "new_user@usv.ro").first()
        assert db_user is not None
        assert db_user.id == user.id
    
    def test_get_user_by_email(self, db_session, test_user):
        """Testează obținerea unui utilizator după email"""
        # Inițializăm serviciul de autentificare
        auth_service = AuthService(db_session=db_session, secret_key="test_secret")
        
        # Obținem utilizatorul după email
        user = auth_service.get_user_by_email(test_user.email)
        
        # Verificăm dacă utilizatorul a fost obținut corect
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email
        
        # Testăm și pentru un email care nu există
        non_existent_user = auth_service.get_user_by_email("non_existent@usv.ro")
        assert non_existent_user is None
    
    def test_get_user_by_id(self, db_session, test_user):
        """Testează obținerea unui utilizator după ID"""
        # Inițializăm serviciul de autentificare
        auth_service = AuthService(db_session=db_session, secret_key="test_secret")
        
        # Obținem utilizatorul după ID
        user = auth_service.get_user_by_id(test_user.id)
        
        # Verificăm dacă utilizatorul a fost obținut corect
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email
        
        # Testăm și pentru un ID care nu există
        non_existent_user = auth_service.get_user_by_id(9999)
        assert non_existent_user is None
    
    def test_generate_token(self, db_session, test_user):
        """Testează generarea unui token JWT"""
        # Inițializăm serviciul de autentificare
        auth_service = AuthService(
            db_session=db_session, 
            secret_key="test_secret",
            token_expire_minutes=60
        )
        
        # Generăm un token
        token, expires = auth_service.generate_token(test_user)
        
        # Verificăm dacă token-ul a fost generat corect
        assert token is not None
        assert isinstance(token, str)
        
        # Verificăm dacă data de expirare este corectă
        assert expires is not None
        assert isinstance(expires, datetime)
        assert expires > datetime.utcnow()
        assert expires <= datetime.utcnow() + timedelta(minutes=61)  # Adăugăm o marjă de 1 minut
        
        # Decodăm token-ul pentru a verifica conținutul
        payload = jwt.decode(token, "test_secret", algorithms=["HS256"])
        assert payload["sub"] == str(test_user.id)
        assert "exp" in payload
    
    def test_verify_token(self, db_session, test_user):
        """Testează verificarea unui token JWT"""
        # Inițializăm serviciul de autentificare
        auth_service = AuthService(
            db_session=db_session, 
            secret_key="test_secret",
            token_expire_minutes=60
        )
        
        # Generăm un token
        token, _ = auth_service.generate_token(test_user)
        
        # Verificăm token-ul
        user_id = auth_service.verify_token(token)
        
        # Verificăm dacă ID-ul utilizatorului a fost obținut corect
        assert user_id is not None
        assert user_id == test_user.id
        
        # Testăm și pentru un token invalid
        invalid_token = "invalid_token"
        invalid_user_id = auth_service.verify_token(invalid_token)
        assert invalid_user_id is None
        
        # Testăm și pentru un token expirat
        expired_payload = {
            "sub": str(test_user.id),
            "exp": datetime.utcnow() - timedelta(minutes=1)
        }
        expired_token = jwt.encode(expired_payload, "test_secret", algorithm="HS256")
        expired_user_id = auth_service.verify_token(expired_token)
        assert expired_user_id is None
    
    def test_verify_google_token(self, db_session, monkeypatch):
        """Testează verificarea unui token Google OAuth"""
        # Inițializăm serviciul de autentificare
        auth_service = AuthService(db_session=db_session, secret_key="test_secret")
        
        # Mock-uim funcția de verificare a token-ului Google
        def mock_verify_oauth2_token(*args, **kwargs):
            return {
                "email": "google_user@usv.ro",
                "given_name": "Google",
                "family_name": "User"
            }
        
        monkeypatch.setattr(auth_service, "_verify_google_token_with_google", mock_verify_oauth2_token)
        
        # Verificăm un token Google
        user_info = auth_service.verify_google_token("google_token")
        
        # Verificăm dacă informațiile utilizatorului au fost obținute corect
        assert user_info is not None
        assert user_info["email"] == "google_user@usv.ro"
        assert user_info["given_name"] == "Google"
        assert user_info["family_name"] == "User"
        
        # Testăm și pentru un token invalid
        def mock_verify_oauth2_token_invalid(*args, **kwargs):
            return None
        
        monkeypatch.setattr(auth_service, "_verify_google_token_with_google", mock_verify_oauth2_token_invalid)
        
        invalid_user_info = auth_service.verify_google_token("invalid_token")
        assert invalid_user_info is None
