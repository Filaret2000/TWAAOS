from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, EmailStr
import datetime

from common.models import User
from common.services import AuthService
from fastapi_app.dependencies import get_db_session, get_current_user, get_current_active_user
from fastapi_app.schemas.auth import Token, UserCreate, UserResponse, UserUpdate

# Creăm router-ul pentru autentificare
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

# Schema pentru token-ul Google OAuth
class GoogleToken(BaseModel):
    token: str

@router.post("/login", response_model=Token)
async def login(google_token: GoogleToken, db_session: Session = Depends(get_db_session)):
    """
    Endpoint pentru autentificare cu Google OAuth
    """
    # Inițializăm serviciul de autentificare
    auth_service = AuthService(
        db_session=db_session,
        secret_key="your-secret-key",  # Va fi înlocuit cu o variabilă de mediu
        token_expire_minutes=60
    )
    
    # Verificăm token-ul Google OAuth
    user_info = auth_service.verify_google_token(google_token.token)
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Google OAuth invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Obținem utilizatorul după email
    email = user_info.get('email')
    user = auth_service.get_user_by_email(email)
    
    if not user:
        # Verificăm dacă email-ul este valid pentru aplicație
        if not email.endswith('@usv.ro') and not email.endswith('@student.usv.ro'):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email invalid pentru aplicație",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Eroare la crearea utilizatorului",
            )
    
    # Generăm token-ul JWT
    token, expires = auth_service.generate_token(user)
    
    # Calculăm timpul de expirare în secunde
    expires_in = int((expires - datetime.datetime.utcnow()).total_seconds())
    
    # Returnăm răspunsul
    return {
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
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Endpoint pentru obținerea informațiilor utilizatorului curent
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "firstName": current_user.first_name,
        "lastName": current_user.last_name
    }

@router.get("/users", response_model=List[UserResponse])
async def get_users(
    skip: int = 0, 
    limit: int = 100, 
    current_user: User = Depends(get_current_active_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Endpoint pentru obținerea tuturor utilizatorilor (doar pentru administrator)
    """
    # Verificăm dacă utilizatorul este administrator
    if current_user.role != 'ADM':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nu aveți permisiunea de a accesa această resursă",
        )
    
    # Obținem toți utilizatorii din baza de date
    users = db_session.query(User).offset(skip).limit(limit).all()
    
    # Returnăm lista de utilizatori
    return users

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_create: UserCreate, 
    current_user: User = Depends(get_current_active_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Endpoint pentru crearea unui utilizator nou (doar pentru administrator)
    """
    # Verificăm dacă utilizatorul este administrator
    if current_user.role != 'ADM':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nu aveți permisiunea de a accesa această resursă",
        )
    
    # Inițializăm serviciul de autentificare
    auth_service = AuthService(
        db_session=db_session,
        secret_key="your-secret-key"  # Va fi înlocuit cu o variabilă de mediu
    )
    
    # Verificăm dacă utilizatorul există deja
    existing_user = auth_service.get_user_by_email(user_create.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Utilizatorul există deja",
        )
    
    # Creăm utilizatorul
    user = auth_service.create_user(
        email=user_create.email,
        first_name=user_create.firstName,
        last_name=user_create.lastName,
        role=user_create.role
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Eroare la crearea utilizatorului",
        )
    
    # Setăm parola dacă este furnizată și utilizatorul este administrator
    if user_create.password and user_create.role == 'ADM':
        user.set_password(user_create.password)
        db_session.commit()
    
    # Returnăm informațiile utilizatorului creat
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "firstName": user.first_name,
        "lastName": user.last_name
    }

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Endpoint pentru actualizarea unui utilizator (doar pentru administrator)
    """
    # Verificăm dacă utilizatorul este administrator
    if current_user.role != 'ADM':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nu aveți permisiunea de a accesa această resursă",
        )
    
    # Obținem utilizatorul din baza de date
    user = db_session.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilizator negăsit",
        )
    
    # Actualizăm datele utilizatorului
    if user_update.firstName is not None:
        user.first_name = user_update.firstName
    
    if user_update.lastName is not None:
        user.last_name = user_update.lastName
    
    if user_update.role is not None:
        # Validăm rolul
        valid_roles = ['SEC', 'SG', 'CD', 'ADM']
        if user_update.role not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Rol invalid. Rolurile valide sunt: {', '.join(valid_roles)}",
            )
        
        user.role = user_update.role
    
    # Setăm parola dacă este furnizată și utilizatorul este administrator
    if user_update.password and user.role == 'ADM':
        user.set_password(user_update.password)
    
    db_session.commit()
    
    # Returnăm informațiile utilizatorului actualizat
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "firstName": user.first_name,
        "lastName": user.last_name
    }

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Endpoint pentru ștergerea unui utilizator (doar pentru administrator)
    """
    # Verificăm dacă utilizatorul este administrator
    if current_user.role != 'ADM':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nu aveți permisiunea de a accesa această resursă",
        )
    
    # Obținem utilizatorul din baza de date
    user = db_session.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilizator negăsit",
        )
    
    # Ștergem utilizatorul
    db_session.delete(user)
    db_session.commit()
    
    # Returnăm un răspuns gol
    return None
