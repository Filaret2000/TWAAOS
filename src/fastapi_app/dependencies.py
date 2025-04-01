from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional
import os

from common.models import User
from common.services import AuthService
from fastapi_app.database import get_db

# Configurăm schema OAuth2 pentru autentificare
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Funcție pentru obținerea sesiunii de bază de date
def get_db_session():
    """
    Dependență pentru obținerea sesiunii de bază de date
    """
    db = get_db()
    try:
        yield db
    finally:
        db.close()

# Funcție pentru obținerea utilizatorului curent
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db_session: Session = Depends(get_db_session)
):
    """
    Dependență pentru obținerea utilizatorului curent din token-ul JWT
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credențiale invalide",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Inițializăm serviciul de autentificare
        auth_service = AuthService(
            db_session=db_session,
            secret_key=os.getenv("JWT_SECRET_KEY", "your-secret-key")
        )
        
        # Verificăm token-ul JWT
        user_id = auth_service.verify_token(token)
        
        if user_id is None:
            raise credentials_exception
        
        # Obținem utilizatorul din baza de date
        user = db_session.query(User).filter(User.id == user_id).first()
        
        if user is None:
            raise credentials_exception
        
        return user
    except JWTError:
        raise credentials_exception

# Funcție pentru obținerea utilizatorului curent activ
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """
    Dependență pentru obținerea utilizatorului curent activ
    """
    if current_user.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Utilizator inactiv",
        )
    
    return current_user

# Funcție pentru verificarea rolului utilizatorului
def check_user_role(allowed_roles: list):
    """
    Funcție pentru crearea unei dependențe care verifică rolul utilizatorului
    """
    async def verify_role(current_user: User = Depends(get_current_active_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rolul '{current_user.role}' nu are permisiunea de a accesa această resursă",
            )
        return current_user
    
    return verify_role
