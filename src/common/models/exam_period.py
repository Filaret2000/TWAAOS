from sqlalchemy import Column, String, Integer, Date
from sqlalchemy.orm import relationship

from src.common.models.base import BaseModel

class ExamPeriod(BaseModel):
    """Model pentru perioadele de examinare"""
    __tablename__ = 'exam_periods'
    
    academic_year = Column(String(20), nullable=False)
    semester = Column(Integer, nullable=False)
    exam_start_date = Column(Date, nullable=False)
    exam_end_date = Column(Date, nullable=False)
    name = Column(String(100), nullable=False)
    
    # Relații
    schedules = relationship("Schedule", back_populates="exam_period")
    
    def to_dict(self):
        """Convertește modelul într-un dicționar"""
        return super().to_dict()
