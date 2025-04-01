import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError

from common.services.notification_service import NotificationService
from common.models.notification import Notification
from common.models.user import User

class TestNotificationService:
    """Teste pentru NotificationService"""

    def test_get_user_notifications(self, db_session, test_user, test_notification):
        """Testează obținerea notificărilor unui utilizator"""
        # Inițializăm serviciul de notificări
        notification_service = NotificationService(
            db_session=db_session,
            api_key="test_api_key"
        )
        
        # Obținem notificările utilizatorului
        notifications, pagination = notification_service.get_user_notifications(
            user_id=test_user.id,
            unread_only=False,
            page=1,
            per_page=10
        )
        
        # Verificăm dacă notificările au fost obținute corect
        assert notifications is not None
        assert len(notifications) >= 1
        assert any(n.id == test_notification.id for n in notifications)
        
        # Verificăm dacă paginarea este corectă
        assert pagination is not None
        assert pagination["page"] == 1
        assert pagination["per_page"] == 10
        assert pagination["total_items"] >= 1
        assert pagination["total_pages"] >= 1
        
        # Testăm și pentru notificări necitite
        notifications, pagination = notification_service.get_user_notifications(
            user_id=test_user.id,
            unread_only=True,
            page=1,
            per_page=10
        )
        
        # Verificăm dacă notificările necitite au fost obținute corect
        assert notifications is not None
        assert len(notifications) >= 1
        assert all(not n.read for n in notifications)
    
    def test_mark_notification_as_read(self, db_session, test_user, test_notification):
        """Testează marcarea unei notificări ca citită"""
        # Inițializăm serviciul de notificări
        notification_service = NotificationService(
            db_session=db_session,
            api_key="test_api_key"
        )
        
        # Marcăm notificarea ca citită
        success = notification_service.mark_notification_as_read(
            notification_id=test_notification.id,
            user_id=test_user.id
        )
        
        # Verificăm dacă notificarea a fost marcată ca citită cu succes
        assert success is True
        
        # Verificăm dacă notificarea a fost actualizată în baza de date
        db_notification = db_session.query(Notification).filter(Notification.id == test_notification.id).first()
        assert db_notification is not None
        assert db_notification.read is True
        
        # Testăm și pentru un ID care nu există
        success = notification_service.mark_notification_as_read(
            notification_id=9999,
            user_id=test_user.id
        )
        assert success is False
        
        # Testăm și pentru un utilizator care nu este proprietarul notificării
        other_user = User(
            email="other@usv.ro",
            first_name="Other",
            last_name="User",
            role="CD"
        )
        db_session.add(other_user)
        db_session.commit()
        
        success = notification_service.mark_notification_as_read(
            notification_id=test_notification.id,
            user_id=other_user.id
        )
        assert success is False
    
    def test_mark_all_notifications_as_read(self, db_session, test_user, test_notification):
        """Testează marcarea tuturor notificărilor ca citite"""
        # Inițializăm serviciul de notificări
        notification_service = NotificationService(
            db_session=db_session,
            api_key="test_api_key"
        )
        
        # Creăm încă o notificare pentru test
        notification2 = Notification(
            user_id=test_user.id,
            title="Test Notification 2",
            message="This is another test notification",
            type="system",
            read=False
        )
        db_session.add(notification2)
        db_session.commit()
        
        # Marcăm toate notificările ca citite
        count = notification_service.mark_all_notifications_as_read(user_id=test_user.id)
        
        # Verificăm dacă notificările au fost marcate ca citite cu succes
        assert count >= 2
        
        # Verificăm dacă notificările au fost actualizate în baza de date
        db_notifications = db_session.query(Notification).filter(Notification.user_id == test_user.id).all()
        assert db_notifications is not None
        assert len(db_notifications) >= 2
        assert all(n.read for n in db_notifications)
    
    def test_get_notification_settings(self, db_session, test_user):
        """Testează obținerea setărilor de notificare"""
        # Inițializăm serviciul de notificări
        notification_service = NotificationService(
            db_session=db_session,
            api_key="test_api_key"
        )
        
        # Obținem setările de notificare
        settings = notification_service.get_notification_settings(user_id=test_user.id)
        
        # Verificăm dacă setările au fost obținute corect
        assert settings is not None
        assert "email_notifications" in settings
        assert "push_notifications" in settings
        assert "schedule_notifications" in settings
        assert "system_notifications" in settings
    
    def test_update_notification_settings(self, db_session, test_user):
        """Testează actualizarea setărilor de notificare"""
        # Inițializăm serviciul de notificări
        notification_service = NotificationService(
            db_session=db_session,
            api_key="test_api_key"
        )
        
        # Actualizăm setările de notificare
        settings = notification_service.update_notification_settings(
            user_id=test_user.id,
            email_notifications=False,
            push_notifications=True,
            schedule_notifications=False,
            system_notifications=True
        )
        
        # Verificăm dacă setările au fost actualizate corect
        assert settings is not None
        assert settings["email_notifications"] is False
        assert settings["push_notifications"] is True
        assert settings["schedule_notifications"] is False
        assert settings["system_notifications"] is True
        
        # Verificăm dacă setările au fost actualizate în baza de date
        updated_settings = notification_service.get_notification_settings(user_id=test_user.id)
        assert updated_settings is not None
        assert updated_settings["email_notifications"] is False
        assert updated_settings["push_notifications"] is True
        assert updated_settings["schedule_notifications"] is False
        assert updated_settings["system_notifications"] is True
    
    @patch("common.services.notification_service.NotificationService._send_email")
    def test_send_notification(self, mock_send_email, db_session, test_user, test_admin):
        """Testează trimiterea unei notificări"""
        # Inițializăm serviciul de notificări
        notification_service = NotificationService(
            db_session=db_session,
            api_key="test_api_key"
        )
        
        # Mock-uim funcția de trimitere email
        mock_send_email.return_value = True
        
        # Trimitem o notificare către un utilizator specific
        count = notification_service.send_notification(
            title="Test Notification",
            message="This is a test notification",
            notification_type="system",
            recipients=[test_user.id],
            send_email=True,
            sender_id=test_admin.id
        )
        
        # Verificăm dacă notificarea a fost trimisă cu succes
        assert count == 1
        
        # Verificăm dacă notificarea a fost adăugată în baza de date
        db_notification = db_session.query(Notification).filter(
            Notification.user_id == test_user.id,
            Notification.title == "Test Notification"
        ).first()
        assert db_notification is not None
        assert db_notification.message == "This is a test notification"
        assert db_notification.type == "system"
        assert db_notification.read is False
        
        # Verificăm dacă funcția de trimitere email a fost apelată
        mock_send_email.assert_called_once()
        
        # Trimitem o notificare către toți utilizatorii cu un anumit rol
        count = notification_service.send_notification(
            title="Role Notification",
            message="This is a notification for all users with a specific role",
            notification_type="info",
            role="SEC",
            send_email=False,
            sender_id=test_admin.id
        )
        
        # Verificăm dacă notificarea a fost trimisă cu succes
        assert count >= 1
        
        # Verificăm dacă notificarea a fost adăugată în baza de date pentru utilizatorii cu rolul specificat
        db_notifications = db_session.query(Notification).filter(
            Notification.title == "Role Notification"
        ).all()
        assert db_notifications is not None
        assert len(db_notifications) >= 1
        for notification in db_notifications:
            user = db_session.query(User).filter(User.id == notification.user_id).first()
            assert user.role == "SEC"
    
    @patch("common.services.notification_service.NotificationService._send_email")
    def test_send_schedule_notification(self, mock_send_email, db_session, test_schedule):
        """Testează trimiterea unei notificări pentru planificare"""
        # Inițializăm serviciul de notificări
        notification_service = NotificationService(
            db_session=db_session,
            api_key="test_api_key"
        )
        
        # Mock-uim funcția de trimitere email
        mock_send_email.return_value = True
        
        # Trimitem o notificare pentru planificare
        success = notification_service.send_schedule_notification(
            schedule_id=test_schedule.id,
            notification_type="created"
        )
        
        # Verificăm dacă notificarea a fost trimisă cu succes
        assert success is True
        
        # Verificăm dacă notificările au fost adăugate în baza de date
        db_notifications = db_session.query(Notification).filter(
            Notification.type == "schedule"
        ).all()
        assert db_notifications is not None
        assert len(db_notifications) >= 1
        
        # Verificăm dacă funcția de trimitere email a fost apelată
        assert mock_send_email.call_count >= 1
