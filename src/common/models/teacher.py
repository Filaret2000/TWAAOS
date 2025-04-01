from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from src.common.models.base import BaseModel

class Teacher(BaseModel):
    """Model pentru cadrele didactice"""
    __tablename__ = 'teachers'
    
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    title = Column(String(20))  # Prof., Conf., Lect., etc.
    department = Column(String(100))
    email = Column(String(100), unique=True, nullable=False)
    
    # Relații
    schedules = relationship("Schedule", back_populates="teacher")
    
    @property
    def full_name(self):
        """Returnează numele complet al cadrului didactic"""
        return f"{self.title or ''} {self.first_name} {self.last_name}".strip()
    
    def to_dict(self):
        """Convertește modelul într-un dicționar"""
        data = super().to_dict()
        data['full_name'] = self.full_name
        return data
