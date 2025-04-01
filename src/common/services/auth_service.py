import jwt
import datetime
from typing import Optional, Dict, Any, Tuple

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.common.models import User

class AuthService:
    """Serviciu pentru autentificare și gestionarea tokenurilor"""
    
    def __init__(self, db_session: Session, secret_key: str, token_expire_minutes: int = 60):
        self.db_session = db_session
        self.secret_key = secret_key
        self.token_expire_minutes = token_expire_minutes
    
    def verify_google_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verifică un token Google OAuth și returnează informațiile utilizatorului
        
        Args:
            token: Token-ul Google OAuth
            
        Returns:
            Dict cu informațiile utilizatorului sau None dacă token-ul este invalid
        """
        try:
            # În implementarea reală, aici ar trebui să verificăm token-ul cu Google
            # Pentru simplitate, presupunem că token-ul este valid și returnăm informații mock
            
            # Acest cod ar trebui înlocuit cu o verificare reală a token-ului
            user_info = {
                'email': 'user@usv.ro',
                'given_name': 'John',
                'family_name': 'Doe'
            }
            
            return user_info
        except Exception as e:
            print(f"Eroare la verificarea token-ului Google: {str(e)}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Obține un utilizator după adresa de email
        
        Args:
            email: Adresa de email a utilizatorului
            
        Returns:
            Obiectul User sau None dacă utilizatorul nu există
        """
        try:
            return self.db_session.query(User).filter(User.email == email).first()
        except SQLAlchemyError as e:
            print(f"Eroare la obținerea utilizatorului după email: {str(e)}")
            return None
    
    def create_user(self, email: str, first_name: str, last_name: str, role: str) -> Optional[User]:
        """
        Creează un utilizator nou
        
        Args:
            email: Adresa de email a utilizatorului
            first_name: Prenumele utilizatorului
            last_name: Numele utilizatorului
            role: Rolul utilizatorului (SEC, SG, CD, ADM)
            
        Returns:
            Obiectul User creat sau None în caz de eroare
        """
        try:
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                role=role
            )
            self.db_session.add(user)
            self.db_session.commit()
            return user
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"Eroare la crearea utilizatorului: {str(e)}")
            return None
    
    def generate_token(self, user: User) -> Tuple[str, datetime.datetime]:
        """
        Generează un token JWT pentru un utilizator
        
        Args:
            user: Obiectul User pentru care se generează token-ul
            
        Returns:
            Tuple cu token-ul generat și data de expirare
        """
        expires = datetime.datetime.utcnow() + datetime.timedelta(minutes=self.token_expire_minutes)
        
        payload = {
            'sub': user.id,
            'email': user.email,
            'role': user.role,
            'exp': expires
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        
        return token, expires
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verifică un token JWT și returnează payload-ul
        
        Args:
            token: Token-ul JWT de verificat
            
        Returns:
            Dict cu payload-ul token-ului sau None dacă token-ul este invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            print("Token expirat")
            return None
        except jwt.InvalidTokenError:
            print("Token invalid")
            return None
    
    def get_user_from_token(self, token: str) -> Optional[User]:
        """
        Obține utilizatorul asociat unui token JWT
        
        Args:
            token: Token-ul JWT
            
        Returns:
            Obiectul User asociat token-ului sau None dacă token-ul este invalid
        """
        payload = self.verify_token(token)
        if not payload:
            return None
        
        user_id = payload.get('sub')
        if not user_id:
            return None
        
        try:
            return self.db_session.query(User).filter(User.id == user_id).first()
        except SQLAlchemyError as e:
            print(f"Eroare la obținerea utilizatorului după ID: {str(e)}")
            return None
