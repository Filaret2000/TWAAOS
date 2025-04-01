from fastapi_app.schemas.auth import (
    Token, UserBase, UserCreate, UserUpdate, UserResponse
)
from fastapi_app.schemas.schedule import (
    SubjectBase, SubjectResponse,
    TeacherBase, TeacherResponse,
    GroupBase, GroupResponse,
    RoomBase, RoomResponse,
    ScheduleBase, ScheduleCreate, SchedulePropose, ScheduleUpdate, ScheduleResponse,
    ConflictResponse, AvailableRoomResponse
)
from fastapi_app.schemas.notification import (
    NotificationBase, NotificationCreate, NotificationResponse,
    NotificationSettings, NotificationSettingsUpdate,
    PaginatedNotificationResponse
)

# Exportă toate schemele pentru a fi utilizate în alte module
__all__ = [
    'Token', 'UserBase', 'UserCreate', 'UserUpdate', 'UserResponse',
    'SubjectBase', 'SubjectResponse',
    'TeacherBase', 'TeacherResponse',
    'GroupBase', 'GroupResponse',
    'RoomBase', 'RoomResponse',
    'ScheduleBase', 'ScheduleCreate', 'SchedulePropose', 'ScheduleUpdate', 'ScheduleResponse',
    'ConflictResponse', 'AvailableRoomResponse',
    'NotificationBase', 'NotificationCreate', 'NotificationResponse',
    'NotificationSettings', 'NotificationSettingsUpdate',
    'PaginatedNotificationResponse'
]
