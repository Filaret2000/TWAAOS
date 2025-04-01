from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
import os

from src.common.models import Notification, User

class NotificationService:
    """Serviciu pentru gestionarea notificărilor"""
    
    def __init__(self, db_session: Session, sendgrid_api_key: Optional[str] = None, email_from: Optional[str] = None):
        self.db_session = db_session
        self.sendgrid_api_key = sendgrid_api_key or os.environ.get('SENDGRID_API_KEY')
        self.email_from = email_from or os.environ.get('EMAIL_FROM', 'planificare@fiesc.usv.ro')
    
    def get_notifications(self, user_id: int, status: Optional[str] = None) -> List[Notification]:
        """
        Obține notificările unui utilizator
        
        Args:
            user_id: ID-ul utilizatorului
            status: Statusul notificărilor (opțional, 'read' sau 'unread')
            
        Returns:
            Listă de obiecte Notification
        """
        try:
            query = self.db_session.query(Notification).filter(Notification.user_id == user_id)
            
            if status:
                query = query.filter(Notification.status == status)
            
            return query.order_by(Notification.date_sent.desc()).all()
        except SQLAlchemyError as e:
            print(f"Eroare la obținerea notificărilor: {str(e)}")
            return []
    
    def mark_notification_as_read(self, notification_id: int) -> Optional[Notification]:
        """
        Marchează o notificare ca citită
        
        Args:
            notification_id: ID-ul notificării
            
        Returns:
            Obiectul Notification actualizat sau None în caz de eroare
        """
        try:
            notification = self.db_session.query(Notification).filter(Notification.id == notification_id).first()
            
            if not notification:
                return None
            
            notification.status = 'read'
            self.db_session.commit()
            
            return notification
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"Eroare la marcarea notificării ca citită: {str(e)}")
            return None
    
    def create_notification(self, user_id: int, message: str) -> Optional[Notification]:
        """
        Creează o notificare nouă
        
        Args:
            user_id: ID-ul utilizatorului destinatar
            message: Mesajul notificării
            
        Returns:
            Obiectul Notification creat sau None în caz de eroare
        """
        try:
            notification = Notification(
                user_id=user_id,
                message=message,
                status='unread'
            )
            
            self.db_session.add(notification)
            self.db_session.commit()
            
            # Trimitem și un email
            user = self.db_session.query(User).filter(User.id == user_id).first()
            if user:
                self.send_email_notification(user.email, "Notificare nouă", message)
            
            return notification
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"Eroare la crearea notificării: {str(e)}")
            return None
    
    def send_email_notification(self, to_email: str, subject: str, message: str) -> bool:
        """
        Trimite o notificare prin email
        
        Args:
            to_email: Adresa de email a destinatarului
            subject: Subiectul email-ului
            message: Conținutul email-ului
            
        Returns:
            True dacă email-ul a fost trimis cu succes, False în caz contrar
        """
        if not self.sendgrid_api_key:
            print("SendGrid API key nu este configurat")
            return False
        
        try:
            sg = sendgrid.SendGridAPIClient(api_key=self.sendgrid_api_key)
            
            from_email = Email(self.email_from)
            to_email = To(to_email)
            content = Content("text/plain", message)
            
            mail = Mail(from_email, to_email, subject, content)
            
            response = sg.client.mail.send.post(request_body=mail.get())
            
            if response.status_code >= 200 and response.status_code < 300:
                return True
            else:
                print(f"Eroare la trimiterea email-ului: {response.status_code}")
                return False
        except Exception as e:
            print(f"Eroare la trimiterea email-ului: {str(e)}")
            return False
    
    def notify_group_leaders(self, message: str) -> int:
        """
        Trimite o notificare tuturor șefilor de grupă
        
        Args:
            message: Mesajul notificării
            
        Returns:
            Numărul de notificări trimise
        """
        try:
            group_leaders = self.db_session.query(User).filter(User.role == 'SG').all()
            
            count = 0
            for leader in group_leaders:
                notification = Notification(
                    user_id=leader.id,
                    message=message,
                    status='unread'
                )
                
                self.db_session.add(notification)
                self.send_email_notification(leader.email, "Notificare nouă", message)
                count += 1
            
            self.db_session.commit()
            return count
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"Eroare la notificarea șefilor de grupă: {str(e)}")
            return 0
    
    def notify_teachers(self, message: str) -> int:
        """
        Trimite o notificare tuturor cadrelor didactice
        
        Args:
            message: Mesajul notificării
            
        Returns:
            Numărul de notificări trimise
        """
        try:
            teachers = self.db_session.query(User).filter(User.role == 'CD').all()
            
            count = 0
            for teacher in teachers:
                notification = Notification(
                    user_id=teacher.id,
                    message=message,
                    status='unread'
                )
                
                self.db_session.add(notification)
                self.send_email_notification(teacher.email, "Notificare nouă", message)
                count += 1
            
            self.db_session.commit()
            return count
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"Eroare la notificarea cadrelor didactice: {str(e)}")
            return 0
