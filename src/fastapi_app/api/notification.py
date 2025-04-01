from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional

from common.models import User, Notification
from common.services import NotificationService
from fastapi_app.dependencies import get_db_session, get_current_user, get_current_active_user
from fastapi_app.schemas.notification import (
    NotificationResponse, NotificationCreate, NotificationSettings,
    NotificationSettingsUpdate, PaginatedNotificationResponse
)

# Creăm router-ul pentru notificări
router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
    responses={404: {"description": "Not found"}},
)

@router.get("", response_model=PaginatedNotificationResponse)
async def get_notifications(
    unread_only: bool = Query(False, description="Dacă se returnează doar notificările necitite"),
    page: int = Query(1, ge=1, description="Numărul paginii"),
    per_page: int = Query(10, ge=1, le=100, description="Numărul de notificări per pagină"),
    current_user: User = Depends(get_current_active_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Endpoint pentru obținerea notificărilor utilizatorului curent
    """
    # Inițializăm serviciul de notificări
    notification_service = NotificationService(
        db_session=db_session,
        api_key="your-sendgrid-api-key"  # Va fi înlocuit cu o variabilă de mediu
    )
    
    # Obținem notificările
    notifications, pagination = notification_service.get_user_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        page=page,
        per_page=per_page
    )
    
    # Returnăm lista de notificări
    return {
        "notifications": notifications,
        "pagination": pagination
    }

@router.post("/{notification_id}/read", response_model=dict)
async def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Endpoint pentru marcarea unei notificări ca citită
    """
    # Inițializăm serviciul de notificări
    notification_service = NotificationService(
        db_session=db_session,
        api_key="your-sendgrid-api-key"  # Va fi înlocuit cu o variabilă de mediu
    )
    
    # Marcăm notificarea ca citită
    success = notification_service.mark_notification_as_read(
        notification_id=notification_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificare negăsită sau nu aparține utilizatorului curent",
        )
    
    # Returnăm mesajul de succes
    return {
        "success": True,
        "message": "Notificare marcată ca citită"
    }

@router.post("/read-all", response_model=dict)
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_active_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Endpoint pentru marcarea tuturor notificărilor ca citite
    """
    # Inițializăm serviciul de notificări
    notification_service = NotificationService(
        db_session=db_session,
        api_key="your-sendgrid-api-key"  # Va fi înlocuit cu o variabilă de mediu
    )
    
    # Marcăm toate notificările ca citite
    count = notification_service.mark_all_notifications_as_read(user_id=current_user.id)
    
    # Returnăm mesajul de succes
    return {
        "success": True,
        "message": "Toate notificările au fost marcate ca citite",
        "count": count
    }

@router.get("/settings", response_model=NotificationSettings)
async def get_notification_settings(
    current_user: User = Depends(get_current_active_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Endpoint pentru obținerea setărilor de notificare ale utilizatorului curent
    """
    # Inițializăm serviciul de notificări
    notification_service = NotificationService(
        db_session=db_session,
        api_key="your-sendgrid-api-key"  # Va fi înlocuit cu o variabilă de mediu
    )
    
    # Obținem setările de notificare
    settings = notification_service.get_notification_settings(user_id=current_user.id)
    
    # Returnăm setările de notificare
    return settings

@router.put("/settings", response_model=dict)
async def update_notification_settings(
    settings_update: NotificationSettingsUpdate,
    current_user: User = Depends(get_current_active_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Endpoint pentru actualizarea setărilor de notificare ale utilizatorului curent
    """
    # Inițializăm serviciul de notificări
    notification_service = NotificationService(
        db_session=db_session,
        api_key="your-sendgrid-api-key"  # Va fi înlocuit cu o variabilă de mediu
    )
    
    # Actualizăm setările de notificare
    settings = notification_service.update_notification_settings(
        user_id=current_user.id,
        email_notifications=settings_update.email_notifications,
        push_notifications=settings_update.push_notifications,
        schedule_notifications=settings_update.schedule_notifications,
        system_notifications=settings_update.system_notifications
    )
    
    # Returnăm mesajul de succes
    return {
        "success": True,
        "message": "Setări de notificare actualizate cu succes",
        "settings": settings
    }

@router.post("/admin/send", response_model=dict)
async def send_notification(
    notification_create: NotificationCreate,
    current_user: User = Depends(get_current_active_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Endpoint pentru trimiterea unei notificări către utilizatori (doar pentru administrator și secretariat)
    """
    # Verificăm dacă utilizatorul are permisiunea de a trimite notificări
    if current_user.role not in ['ADM', 'SEC']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nu aveți permisiunea de a trimite notificări",
        )
    
    # Verificăm dacă a fost specificat cel puțin un criteriu de filtrare
    if not notification_create.recipients and not notification_create.role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trebuie specificat cel puțin un criteriu de filtrare: recipients sau role",
        )
    
    # Inițializăm serviciul de notificări
    notification_service = NotificationService(
        db_session=db_session,
        api_key="your-sendgrid-api-key"  # Va fi înlocuit cu o variabilă de mediu
    )
    
    # Trimitem notificarea
    try:
        count = notification_service.send_notification(
            title=notification_create.title,
            message=notification_create.message,
            notification_type=notification_create.type,
            recipients=notification_create.recipients or [],
            role=notification_create.role,
            send_email=notification_create.send_email or False,
            sender_id=current_user.id
        )
        
        # Returnăm mesajul de succes
        return {
            "success": True,
            "message": "Notificare trimisă cu succes",
            "count": count
        }
    except SQLAlchemyError as e:
        db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Eroare la trimiterea notificării: {str(e)}",
        )
