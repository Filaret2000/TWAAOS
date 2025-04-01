from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from src.common.models.base import BaseModel

class Group(BaseModel):
    """Model pentru grupele de studenți"""
    __tablename__ = 'groups'
    
    name = Column(String(50), nullable=False, unique=True)
    study_year = Column(Integer, nullable=False)
    specialization = Column(String(100), nullable=False)
    number_of_students = Column(Integer, nullable=False)
    
    # Relații
    schedules = relationship("Schedule", back_populates="group")
    
    def to_dict(self):
        """Convertește modelul într-un dicționar"""
        return super().to_dict()
