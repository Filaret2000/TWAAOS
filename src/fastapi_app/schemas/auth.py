from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class Token(BaseModel):
    """Schema pentru token-ul de autentificare"""
    access_token: str
    token_type: str
    expires_in: int
    user: Dict[str, Any]

class UserBase(BaseModel):
    """Schema de bază pentru utilizator"""
    email: EmailStr
    firstName: str = Field(..., min_length=1, max_length=100)
    lastName: str = Field(..., min_length=1, max_length=100)
    role: str = Field(..., pattern='^(SEC|SG|CD|ADM)$')

class UserCreate(UserBase):
    """Schema pentru crearea unui utilizator"""
    password: Optional[str] = Field(None, min_length=8)

class UserUpdate(BaseModel):
    """Schema pentru actualizarea unui utilizator"""
    firstName: Optional[str] = Field(None, min_length=1, max_length=100)
    lastName: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[str] = Field(None, pattern='^(SEC|SG|CD|ADM)$')
    password: Optional[str] = Field(None, min_length=8)

class UserResponse(UserBase):
    """Schema pentru răspunsul cu informații despre utilizator"""
    id: int

    class Config:
        orm_mode = True
