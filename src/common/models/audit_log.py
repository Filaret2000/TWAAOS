from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
import datetime

from src.common.models.base import BaseModel

class AuditLog(BaseModel):
    """Model pentru jurnalul de audit al modificărilor din sistem"""
    __tablename__ = 'audit_log'
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    action = Column(String(50), nullable=False)  # create, update, delete
    entity_type = Column(String(100), nullable=False)  # numele tabelului
    entity_id = Column(Integer, nullable=False)  # id-ul entității
    changes = Column(Text, nullable=True)  # JSON cu modificările
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    ip_address = Column(String(50), nullable=True)
    
    # Relații
    user = relationship("User")
    
    def to_dict(self):
        """Convertește modelul într-un dicționar"""
        data = super().to_dict()
        data['user_name'] = self.user.full_name if self.user else None
        return data
