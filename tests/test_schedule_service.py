import pytest
from datetime import datetime, date, time
from sqlalchemy.exc import SQLAlchemyError

from common.services.schedule_service import ScheduleService
from common.models.schedule import Schedule

class TestScheduleService:
    """Teste pentru ScheduleService"""

    def test_create_schedule(self, db_session, test_subject, test_teacher, test_group, test_room, test_user):
        """Testează crearea unei planificări"""
        # Inițializăm serviciul de planificare
        schedule_service = ScheduleService(db_session=db_session)
        
        # Creăm o planificare nouă
        schedule = schedule_service.create_schedule(
            subject_id=test_subject.id,
            teacher_id=test_teacher.id,
            group_id=test_group.id,
            room_id=test_room.id,
            date=date(2025, 1, 20),
            start_time=time(10, 0),
            end_time=time(12, 0),
            created_by=test_user.id
        )
        
        # Verificăm dacă planificarea a fost creată corect
        assert schedule is not None
        assert schedule.subject_id == test_subject.id
        assert schedule.teacher_id == test_teacher.id
        assert schedule.group_id == test_group.id
        assert schedule.room_id == test_room.id
        assert schedule.date == date(2025, 1, 20)
        assert schedule.start_time == time(10, 0)
        assert schedule.end_time == time(12, 0)
        assert schedule.created_by == test_user.id
        assert schedule.status == "pending"  # Status implicit
        
        # Verificăm dacă planificarea a fost adăugată în baza de date
        db_schedule = db_session.query(Schedule).filter(
            Schedule.subject_id == test_subject.id,
            Schedule.teacher_id == test_teacher.id,
            Schedule.group_id == test_group.id,
            Schedule.date == date(2025, 1, 20)
        ).first()
        assert db_schedule is not None
        assert db_schedule.id == schedule.id
    
    def test_get_schedule_by_id(self, db_session, test_schedule):
        """Testează obținerea unei planificări după ID"""
        # Inițializăm serviciul de planificare
        schedule_service = ScheduleService(db_session=db_session)
        
        # Obținem planificarea după ID
        schedule = schedule_service.get_schedule_by_id(test_schedule.id)
        
        # Verificăm dacă planificarea a fost obținută corect
        assert schedule is not None
        assert schedule.id == test_schedule.id
        assert schedule.subject_id == test_schedule.subject_id
        assert schedule.teacher_id == test_schedule.teacher_id
        assert schedule.group_id == test_schedule.group_id
        
        # Testăm și pentru un ID care nu există
        non_existent_schedule = schedule_service.get_schedule_by_id(9999)
        assert non_existent_schedule is None
    
    def test_get_schedules(self, db_session, test_schedule):
        """Testează obținerea planificărilor cu filtre"""
        # Inițializăm serviciul de planificare
        schedule_service = ScheduleService(db_session=db_session)
        
        # Obținem planificările fără filtre
        schedules = schedule_service.get_schedules()
        assert len(schedules) >= 1
        
        # Obținem planificările pentru grupa specificată
        schedules = schedule_service.get_schedules(group_id=test_schedule.group_id)
        assert len(schedules) >= 1
        for schedule in schedules:
            assert schedule.group_id == test_schedule.group_id
        
        # Obținem planificările pentru cadrul didactic specificat
        schedules = schedule_service.get_schedules(teacher_id=test_schedule.teacher_id)
        assert len(schedules) >= 1
        for schedule in schedules:
            assert schedule.teacher_id == test_schedule.teacher_id
        
        # Obținem planificările pentru data specificată
        schedules = schedule_service.get_schedules(
            start_date=datetime.strptime("2025-01-01", "%Y-%m-%d").date(),
            end_date=datetime.strptime("2025-01-31", "%Y-%m-%d").date()
        )
        assert len(schedules) >= 1
        for schedule in schedules:
            assert schedule.date >= datetime.strptime("2025-01-01", "%Y-%m-%d").date()
            assert schedule.date <= datetime.strptime("2025-01-31", "%Y-%m-%d").date()
        
        # Obținem planificările pentru statusul specificat
        schedules = schedule_service.get_schedules(status="approved")
        assert len(schedules) >= 1
        for schedule in schedules:
            assert schedule.status == "approved"
    
    def test_update_schedule(self, db_session, test_schedule, test_room):
        """Testează actualizarea unei planificări"""
        # Inițializăm serviciul de planificare
        schedule_service = ScheduleService(db_session=db_session)
        
        # Creăm o sală nouă pentru test
        new_room = test_room
        
        # Actualizăm planificarea
        updated_schedule = schedule_service.update_schedule(
            schedule_id=test_schedule.id,
            room_id=new_room.id,
            date=date(2025, 1, 25),
            start_time=time(14, 0),
            end_time=time(16, 0),
            status="rejected",
            updated_by=test_schedule.created_by
        )
        
        # Verificăm dacă planificarea a fost actualizată corect
        assert updated_schedule is not None
        assert updated_schedule.id == test_schedule.id
        assert updated_schedule.room_id == new_room.id
        assert updated_schedule.date == date(2025, 1, 25)
        assert updated_schedule.start_time == time(14, 0)
        assert updated_schedule.end_time == time(16, 0)
        assert updated_schedule.status == "rejected"
        
        # Verificăm dacă planificarea a fost actualizată în baza de date
        db_schedule = db_session.query(Schedule).filter(Schedule.id == test_schedule.id).first()
        assert db_schedule is not None
        assert db_schedule.room_id == new_room.id
        assert db_schedule.date == date(2025, 1, 25)
        assert db_schedule.start_time == time(14, 0)
        assert db_schedule.end_time == time(16, 0)
        assert db_schedule.status == "rejected"
        
        # Testăm și pentru un ID care nu există
        non_existent_schedule = schedule_service.update_schedule(
            schedule_id=9999,
            status="approved",
            updated_by=test_schedule.created_by
        )
        assert non_existent_schedule is None
    
    def test_delete_schedule(self, db_session, test_schedule):
        """Testează ștergerea unei planificări"""
        # Inițializăm serviciul de planificare
        schedule_service = ScheduleService(db_session=db_session)
        
        # Ștergem planificarea
        success = schedule_service.delete_schedule(
            schedule_id=test_schedule.id,
            deleted_by=test_schedule.created_by
        )
        
        # Verificăm dacă planificarea a fost ștearsă cu succes
        assert success is True
        
        # Verificăm dacă planificarea a fost ștearsă din baza de date
        db_schedule = db_session.query(Schedule).filter(Schedule.id == test_schedule.id).first()
        assert db_schedule is None
        
        # Testăm și pentru un ID care nu există
        success = schedule_service.delete_schedule(
            schedule_id=9999,
            deleted_by=test_schedule.created_by
        )
        assert success is False
    
    def test_get_conflicts(self, db_session, test_schedule, test_subject, test_teacher, test_group, test_room, test_user):
        """Testează obținerea conflictelor de planificare"""
        # Inițializăm serviciul de planificare
        schedule_service = ScheduleService(db_session=db_session)
        
        # Creăm o planificare care se suprapune cu cea existentă
        overlapping_schedule = schedule_service.create_schedule(
            subject_id=test_subject.id,
            teacher_id=test_teacher.id,
            group_id=test_group.id,
            room_id=test_room.id,
            date=test_schedule.date,
            start_time=time(11, 0),  # Se suprapune cu test_schedule (10:00-12:00)
            end_time=time(13, 0),
            created_by=test_user.id,
            status="approved"
        )
        
        # Obținem conflictele
        conflicts = schedule_service.get_conflicts()
        
        # Verificăm dacă conflictele au fost obținute corect
        assert conflicts is not None
        assert len(conflicts) >= 1
        
        # Verificăm dacă există cel puțin un conflict de tip "room"
        room_conflicts = [c for c in conflicts if c["type"] == "room"]
        assert len(room_conflicts) >= 1
        
        # Verificăm dacă există cel puțin un conflict de tip "teacher"
        teacher_conflicts = [c for c in conflicts if c["type"] == "teacher"]
        assert len(teacher_conflicts) >= 1
        
        # Verificăm dacă există cel puțin un conflict de tip "group"
        group_conflicts = [c for c in conflicts if c["type"] == "group"]
        assert len(group_conflicts) >= 1
    
    def test_get_available_rooms(self, db_session, test_schedule, test_room):
        """Testează obținerea sălilor disponibile"""
        # Inițializăm serviciul de planificare
        schedule_service = ScheduleService(db_session=db_session)
        
        # Obținem sălile disponibile pentru o dată și interval orar care nu se suprapun cu planificarea existentă
        available_rooms = schedule_service.get_available_rooms(
            date=test_schedule.date,
            start_time=time(14, 0),
            end_time=time(16, 0)
        )
        
        # Verificăm dacă sala existentă este disponibilă
        assert any(room.id == test_room.id for room in available_rooms)
        
        # Obținem sălile disponibile pentru o dată și interval orar care se suprapun cu planificarea existentă
        available_rooms = schedule_service.get_available_rooms(
            date=test_schedule.date,
            start_time=time(11, 0),
            end_time=time(13, 0)
        )
        
        # Verificăm dacă sala existentă nu este disponibilă
        assert not any(room.id == test_room.id for room in available_rooms)
