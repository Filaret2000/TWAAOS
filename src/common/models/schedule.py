from sqlalchemy import Column, String, Integer, Date, Time, ForeignKey, Table
from sqlalchemy.orm import relationship

from src.common.models.base import BaseModel, Base

# Tabel de legătură pentru asistenți (many-to-many între Schedule și Teacher)
schedule_assistants = Table(
    'schedule_assistants',
    Base.metadata,
    Column('schedule_id', Integer, ForeignKey('schedules.id'), primary_key=True),
    Column('teacher_id', Integer, ForeignKey('teachers.id'), primary_key=True)
)

class Schedule(BaseModel):
    """Model pentru planificările examenelor și colocviilor"""
    __tablename__ = 'schedules'
    
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('teachers.id'), nullable=False)
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=True)  # Poate fi null până la aprobare
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=True)  # Poate fi null până la aprobare
    end_time = Column(Time, nullable=True)    # Poate fi null până la aprobare
    status = Column(String(20), nullable=False, default='proposed')  # proposed, approved, rejected
    
    # Relații
    subject = relationship("Subject", back_populates="schedules")
    teacher = relationship("Teacher", back_populates="schedules")
    room = relationship("Room", back_populates="schedules")
    group = relationship("Group", back_populates="schedules")
    assistants = relationship("Teacher", secondary=schedule_assistants, backref="assisted_schedules")
    
    def to_dict(self):
        """Convertește modelul într-un dicționar"""
        data = super().to_dict()
        data['subject_name'] = self.subject.name if self.subject else None
        data['teacher_name'] = self.teacher.full_name if self.teacher else None
        data['room_name'] = self.room.name if self.room else None
        data['group_name'] = self.group.name if self.group else None
        data['assistants'] = [{'id': a.id, 'name': a.full_name} for a in self.assistants]
        return data
