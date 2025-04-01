from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class NotificationBase(BaseModel):
    """Schema de bază pentru notificare"""
    title: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1)
    type: str = Field(..., pattern='^(system|schedule|deadline|info)$')

class NotificationCreate(NotificationBase):
    """Schema pentru crearea unei notificări"""
    recipients: Optional[List[int]] = None
    role: Optional[str] = Field(None, pattern='^(SEC|SG|CD|ADM)$')
    send_email: Optional[bool] = False

class NotificationResponse(NotificationBase):
    """Schema pentru răspunsul cu informații despre notificare"""
    id: int
    read: bool
    createdAt: datetime

    class Config:
        orm_mode = True

class NotificationSettings(BaseModel):
    """Schema pentru setările de notificare"""
    email_notifications: bool = True
    push_notifications: bool = False
    schedule_notifications: bool = True
    system_notifications: bool = True

class NotificationSettingsUpdate(BaseModel):
    """Schema pentru actualizarea setărilor de notificare"""
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    schedule_notifications: Optional[bool] = None
    system_notifications: Optional[bool] = None

class PaginatedNotificationResponse(BaseModel):
    """Schema pentru răspunsul paginat cu notificări"""
    notifications: List[NotificationResponse]
    pagination: Dict[str, Any]
