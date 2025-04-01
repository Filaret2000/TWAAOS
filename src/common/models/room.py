from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from src.common.models.base import BaseModel

class Room(BaseModel):
    """Model pentru sălile disponibile pentru examinare"""
    __tablename__ = 'rooms'
    
    name = Column(String(100), nullable=False)
    short_name = Column(String(50), nullable=False)
    capacity = Column(Integer, nullable=False)
    building = Column(String(100))
    floor = Column(Integer)
    
    # Relații
    schedules = relationship("Schedule", back_populates="room")
    
    def to_dict(self):
        """Convertește modelul într-un dicționar"""
        return super().to_dict()
