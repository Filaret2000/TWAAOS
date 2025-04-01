from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
import datetime

from src.common.models.base import BaseModel

class Notification(BaseModel):
    """Model pentru notificările trimise utilizatorilor"""
    __tablename__ = 'notifications'
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), nullable=False)  # info, warning, error, success
    read = Column(DateTime, nullable=True)  # Null dacă nu a fost citită
    
    # Relații
    user = relationship("User", back_populates="notifications")
    
    def to_dict(self):
        """Convertește modelul într-un dicționar"""
        data = super().to_dict()
        data['is_read'] = self.read is not None
        return data
