from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from src.common.models.base import BaseModel

class Subject(BaseModel):
    """Model pentru disciplinele de studiu"""
    __tablename__ = 'subjects'
    
    name = Column(String(255), nullable=False)
    short_name = Column(String(50), nullable=False)
    credits = Column(Integer, nullable=False)
    semester = Column(Integer, nullable=False)
    
    # Relații
    schedules = relationship("Schedule", back_populates="subject")
    
    def to_dict(self):
        """Convertește modelul într-un dicționar"""
        return super().to_dict()
