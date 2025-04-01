from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from datetime import date, time, datetime

from common.models import User, Schedule, Room, Group, Subject, Teacher
from common.services import ScheduleService, NotificationService
from fastapi_app.dependencies import get_db_session, get_current_user, get_current_active_user
from fastapi_app.schemas.schedule import (
    ScheduleCreate, ScheduleUpdate, ScheduleResponse, SchedulePropose,
    ConflictResponse, AvailableRoomResponse
)

# Creăm router-ul pentru planificare
router = APIRouter(
    prefix="/schedules",
    tags=["schedules"],
    responses={404: {"description": "Not found"}},
)

@router.get("", response_model=List[ScheduleResponse])
async def get_schedules(
    group_id: Optional[int] = None,
    teacher_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Endpoint pentru obținerea planificărilor
    """
    # Inițializăm serviciul de planificare
    schedule_service = ScheduleService(db_session=db_session)
    
    # Obținem planificările
    schedules = schedule_service.get_schedules(
        group_id=group_id,
        teacher_id=teacher_id,
        start_date=start_date,
        end_date=end_date,
        status=status
    )
    
    # Returnăm lista de planificări
    return schedules

@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_active_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Endpoint pentru obținerea unei planificări după ID
    """
    # Inițializăm serviciul de planificare
    schedule_service = ScheduleService(db_session=db_session)
    
    # Obținem planificarea
    schedule = schedule_service.get_schedule_by_id(schedule_id)
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planificare negăsită",
        )
    
    # Returnăm planificarea
    return schedule

@router.post("", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule_create: ScheduleCreate,
    current_user: User = Depends(get_current_active_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Endpoint pentru crearea unei planificări
    """
    # Verificăm dacă utilizatorul are permisiunea de a crea planificări
    if current_user.role not in ['SEC', 'ADM']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nu aveți permisiunea de a crea planificări",
        )
    
    # Inițializăm serviciul de planificare
    schedule_service = ScheduleService(db_session=db_session)
    
    # Creăm planificarea
    try:
        schedule = schedule_service.create_schedule(
            subject_id=schedule_create.subjectId,
            teacher_id=schedule_create.teacherId,
            group_id=schedule_create.groupId,
            room_id=schedule_create.roomId,
            date=schedule_create.date,
            start_time=schedule_create.startTime,
            end_time=schedule_create.endTime,
            created_by=current_user.id
        )
        
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Eroare la crearea planificării",
            )
        
        # Trimitem notificări
        notification_service = NotificationService(
            db_session=db_session,
            api_key="your-sendgrid-api-key"  # Va fi înlocuit cu o variabilă de mediu
        )
        
        notification_service.send_schedule_notification(
            schedule_id=schedule.id,
            notification_type='created'
        )
        
        # Returnăm planificarea creată
        return schedule
    except SQLAlchemyError as e:
        db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Eroare la crearea planificării: {str(e)}",
        )

@router.put("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int,
    schedule_update: ScheduleUpdate,
    current_user: User = Depends(get_current_active_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Endpoint pentru actualizarea unei planificări
    """
    # Verificăm dacă utilizatorul are permisiunea de a actualiza planificări
    if current_user.role not in ['SEC', 'ADM']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nu aveți permisiunea de a actualiza planificări",
        )
    
    # Inițializăm serviciul de planificare
    schedule_service = ScheduleService(db_session=db_session)
    
    # Actualizăm planificarea
    try:
        schedule = schedule_service.update_schedule(
            schedule_id=schedule_id,
            subject_id=schedule_update.subjectId,
            teacher_id=schedule_update.teacherId,
            group_id=schedule_update.groupId,
            room_id=schedule_update.roomId,
            date=schedule_update.date,
            start_time=schedule_update.startTime,
            end_time=schedule_update.endTime,
            status=schedule_update.status,
            updated_by=current_user.id
        )
        
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Planificare negăsită sau eroare la actualizare",
            )
        
        # Trimitem notificări dacă statusul a fost actualizat
        if schedule_update.status:
            notification_service = NotificationService(
                db_session=db_session,
                api_key="your-sendgrid-api-key"  # Va fi înlocuit cu o variabilă de mediu
            )
            
            notification_type = 'approved' if schedule_update.status == 'approved' else 'rejected'
            
            notification_service.send_schedule_notification(
                schedule_id=schedule.id,
                notification_type=notification_type
            )
        
        # Returnăm planificarea actualizată
        return schedule
    except SQLAlchemyError as e:
        db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Eroare la actualizarea planificării: {str(e)}",
        )

@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_active_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Endpoint pentru ștergerea unei planificări
    """
    # Verificăm dacă utilizatorul are permisiunea de a șterge planificări
    if current_user.role not in ['SEC', 'ADM']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nu aveți permisiunea de a șterge planificări",
        )
    
    # Inițializăm serviciul de planificare
    schedule_service = ScheduleService(db_session=db_session)
    
    # Ștergem planificarea
    try:
        success = schedule_service.delete_schedule(
            schedule_id=schedule_id,
            deleted_by=current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Planificare negăsită sau eroare la ștergere",
            )
        
        # Trimitem notificări
        notification_service = NotificationService(
            db_session=db_session,
            api_key="your-sendgrid-api-key"  # Va fi înlocuit cu o variabilă de mediu
        )
        
        notification_service.send_schedule_notification(
            schedule_id=schedule_id,
            notification_type='deleted'
        )
        
        # Returnăm un răspuns gol
        return None
    except SQLAlchemyError as e:
        db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Eroare la ștergerea planificării: {str(e)}",
        )

@router.post("/propose", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def propose_schedule(
    schedule_propose: SchedulePropose,
    current_user: User = Depends(get_current_active_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Endpoint pentru propunerea unei planificări de către un cadru didactic
    """
    # Verificăm dacă utilizatorul este cadru didactic
    if current_user.role != 'CD':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doar cadrele didactice pot propune planificări",
        )
    
    # Inițializăm serviciul de planificare
    schedule_service = ScheduleService(db_session=db_session)
    
    # Obținem cadrul didactic asociat utilizatorului
    try:
        teacher = db_session.query(Teacher).join(User).filter(User.id == current_user.id).first()
        
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cadru didactic negăsit pentru utilizatorul curent",
            )
        
        # Creăm planificarea
        schedule = schedule_service.create_schedule(
            subject_id=schedule_propose.subjectId,
            teacher_id=teacher.id,
            group_id=schedule_propose.groupId,
            room_id=schedule_propose.roomId,  # Poate fi None
            date=schedule_propose.date,
            start_time=schedule_propose.startTime,
            end_time=schedule_propose.endTime,
            created_by=current_user.id,
            status='proposed'
        )
        
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Eroare la propunerea planificării",
            )
        
        # Trimitem notificări
        notification_service = NotificationService(
            db_session=db_session,
            api_key="your-sendgrid-api-key"  # Va fi înlocuit cu o variabilă de mediu
        )
        
        notification_service.send_schedule_notification(
            schedule_id=schedule.id,
            notification_type='proposed'
        )
        
        # Returnăm planificarea propusă
        return schedule
    except SQLAlchemyError as e:
        db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Eroare la propunerea planificării: {str(e)}",
        )

@router.get("/conflicts", response_model=List[ConflictResponse])
async def get_conflicts(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_active_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Endpoint pentru obținerea conflictelor de planificare
    """
    # Verificăm dacă utilizatorul are permisiunea de a vedea conflictele
    if current_user.role not in ['SEC', 'ADM', 'CD']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nu aveți permisiunea de a vedea conflictele",
        )
    
    # Inițializăm serviciul de planificare
    schedule_service = ScheduleService(db_session=db_session)
    
    # Obținem conflictele
    conflicts = schedule_service.get_conflicts(
        start_date=start_date,
        end_date=end_date
    )
    
    # Returnăm lista de conflicte
    return conflicts

@router.get("/available-rooms", response_model=List[AvailableRoomResponse])
async def get_available_rooms(
    date: date = Query(..., description="Data pentru care se caută săli disponibile"),
    start_time: time = Query(..., description="Ora de început"),
    end_time: time = Query(..., description="Ora de sfârșit"),
    capacity: Optional[int] = Query(None, description="Capacitatea minimă a sălii"),
    current_user: User = Depends(get_current_active_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Endpoint pentru obținerea sălilor disponibile pentru o anumită dată și interval orar
    """
    # Validăm parametrii
    if end_time <= start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Timpul de sfârșit trebuie să fie după timpul de început",
        )
    
    # Inițializăm serviciul de planificare
    schedule_service = ScheduleService(db_session=db_session)
    
    # Obținem sălile disponibile
    rooms = schedule_service.get_available_rooms(
        date=date,
        start_time=start_time,
        end_time=end_time,
        capacity=capacity
    )
    
    # Returnăm lista de săli disponibile
    return rooms
