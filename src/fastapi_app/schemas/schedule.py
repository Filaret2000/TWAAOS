from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, time, datetime

class SubjectBase(BaseModel):
    """Schema de bază pentru materie"""
    name: str
    acronym: str

class SubjectResponse(SubjectBase):
    """Schema pentru răspunsul cu informații despre materie"""
    id: int

    class Config:
        orm_mode = True

class TeacherBase(BaseModel):
    """Schema de bază pentru cadru didactic"""
    firstName: str
    lastName: str
    email: str

class TeacherResponse(TeacherBase):
    """Schema pentru răspunsul cu informații despre cadrul didactic"""
    id: int

    class Config:
        orm_mode = True

class GroupBase(BaseModel):
    """Schema de bază pentru grupă"""
    name: str
    year: int
    specialization: str

class GroupResponse(GroupBase):
    """Schema pentru răspunsul cu informații despre grupă"""
    id: int

    class Config:
        orm_mode = True

class RoomBase(BaseModel):
    """Schema de bază pentru sală"""
    name: str
    capacity: int
    building: str

class RoomResponse(RoomBase):
    """Schema pentru răspunsul cu informații despre sală"""
    id: int

    class Config:
        orm_mode = True

class ScheduleBase(BaseModel):
    """Schema de bază pentru planificare"""
    subjectId: int = Field(..., gt=0)
    teacherId: int = Field(..., gt=0)
    groupId: int = Field(..., gt=0)
    roomId: Optional[int] = Field(None, gt=0)
    date: date
    startTime: time
    endTime: time

    @validator('endTime')
    def end_time_must_be_after_start_time(cls, v, values):
        if 'startTime' in values and v <= values['startTime']:
            raise ValueError('Timpul de sfârșit trebuie să fie după timpul de început')
        return v

class ScheduleCreate(ScheduleBase):
    """Schema pentru crearea unei planificări"""
    pass

class SchedulePropose(BaseModel):
    """Schema pentru propunerea unei planificări de către un cadru didactic"""
    subjectId: int = Field(..., gt=0)
    groupId: int = Field(..., gt=0)
    date: date
    startTime: time
    endTime: time
    roomId: Optional[int] = Field(None, gt=0)

    @validator('endTime')
    def end_time_must_be_after_start_time(cls, v, values):
        if 'startTime' in values and v <= values['startTime']:
            raise ValueError('Timpul de sfârșit trebuie să fie după timpul de început')
        return v

class ScheduleUpdate(BaseModel):
    """Schema pentru actualizarea unei planificări"""
    subjectId: Optional[int] = Field(None, gt=0)
    teacherId: Optional[int] = Field(None, gt=0)
    groupId: Optional[int] = Field(None, gt=0)
    roomId: Optional[int] = Field(None, gt=0)
    date: Optional[date] = None
    startTime: Optional[time] = None
    endTime: Optional[time] = None
    status: Optional[str] = Field(None, pattern='^(proposed|approved|rejected)$')

    @validator('endTime')
    def end_time_must_be_after_start_time(cls, v, values):
        if v is not None and 'startTime' in values and values['startTime'] is not None and v <= values['startTime']:
            raise ValueError('Timpul de sfârșit trebuie să fie după timpul de început')
        return v

class ScheduleResponse(BaseModel):
    """Schema pentru răspunsul cu informații despre planificare"""
    id: int
    subject: SubjectResponse
    teacher: TeacherResponse
    group: GroupResponse
    room: Optional[RoomResponse] = None
    date: date
    startTime: time
    endTime: time
    status: str
    createdAt: datetime
    updatedAt: datetime

    class Config:
        orm_mode = True

class ConflictResponse(BaseModel):
    """Schema pentru răspunsul cu informații despre conflicte"""
    type: str
    schedules: List[ScheduleResponse]

class AvailableRoomResponse(RoomResponse):
    """Schema pentru răspunsul cu informații despre sălile disponibile"""
    pass
