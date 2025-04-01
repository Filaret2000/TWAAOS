import os
import pytest
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from sqlalchemy.pool import StaticPool

# Adăugăm directorul src la calea de import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from common.models import Base
from common.models.user import User
from common.models.teacher import Teacher
from common.models.room import Room
from common.models.group import Group
from common.models.subject import Subject
from common.models.schedule import Schedule
from common.models.notification import Notification
from common.models.exam_period import ExamPeriod
from common.models.excel_template import ExcelTemplate
from common.models.audit_log import AuditLog

@pytest.fixture
def in_memory_db():
    """Creează o bază de date SQLite în memorie pentru teste"""
    engine = create_engine('sqlite:///:memory:',
                           connect_args={"check_same_thread": False},
                           poolclass=StaticPool)
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def db_session(in_memory_db):
    """Creează o sesiune de bază de date pentru teste"""
    Session = sessionmaker(bind=in_memory_db)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def test_user(db_session):
    """Creează un utilizator de test"""
    user = User(
        email="test@usv.ro",
        first_name="Test",
        last_name="User",
        role="SEC"
    )
    user.set_password("test_password")
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def test_admin(db_session):
    """Creează un administrator de test"""
    admin = User(
        email="admin@usv.ro",
        first_name="Admin",
        last_name="User",
        role="ADM"
    )
    admin.set_password("admin_password")
    db_session.add(admin)
    db_session.commit()
    return admin

@pytest.fixture
def test_teacher(db_session):
    """Creează un cadru didactic de test"""
    user = User(
        email="teacher@usv.ro",
        first_name="Teacher",
        last_name="User",
        role="CD"
    )
    user.set_password("teacher_password")
    db_session.add(user)
    db_session.commit()
    
    teacher = Teacher(
        user_id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        department="Calculatoare"
    )
    db_session.add(teacher)
    db_session.commit()
    return teacher

@pytest.fixture
def test_student(db_session):
    """Creează un student de test"""
    user = User(
        email="student@student.usv.ro",
        first_name="Student",
        last_name="User",
        role="SG"
    )
    user.set_password("student_password")
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def test_group(db_session):
    """Creează o grupă de test"""
    group = Group(
        name="3A4",
        year=3,
        specialization="Calculatoare",
        faculty="FIESC"
    )
    db_session.add(group)
    db_session.commit()
    return group

@pytest.fixture
def test_room(db_session):
    """Creează o sală de test"""
    room = Room(
        name="C201",
        capacity=30,
        building="C",
        type="Laborator"
    )
    db_session.add(room)
    db_session.commit()
    return room

@pytest.fixture
def test_subject(db_session):
    """Creează o disciplină de test"""
    subject = Subject(
        name="Programare Web",
        acronym="PW",
        credits=5
    )
    db_session.add(subject)
    db_session.commit()
    return subject

@pytest.fixture
def test_schedule(db_session, test_subject, test_teacher, test_group, test_room, test_user):
    """Creează o planificare de test"""
    schedule = Schedule(
        subject_id=test_subject.id,
        teacher_id=test_teacher.id,
        group_id=test_group.id,
        room_id=test_room.id,
        date="2025-01-15",
        start_time="10:00",
        end_time="12:00",
        status="approved",
        created_by=test_user.id
    )
    db_session.add(schedule)
    db_session.commit()
    return schedule

@pytest.fixture
def test_notification(db_session, test_user):
    """Creează o notificare de test"""
    notification = Notification(
        user_id=test_user.id,
        title="Test Notification",
        message="This is a test notification",
        type="system",
        read=False
    )
    db_session.add(notification)
    db_session.commit()
    return notification

@pytest.fixture
def test_exam_period(db_session):
    """Creează o perioadă de examinare de test"""
    exam_period = ExamPeriod(
        name="Sesiune Iarnă 2025",
        start_date="2025-01-15",
        end_date="2025-01-30",
        type="exam"
    )
    db_session.add(exam_period)
    db_session.commit()
    return exam_period
