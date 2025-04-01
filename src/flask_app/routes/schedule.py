from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

from src.common.models import User, Schedule, Room, Group, Subject, Teacher
from src.common.services import ScheduleService, NotificationService
from src.flask_app.utils.db import get_db_session
from src.flask_app.utils.decorators import role_required

# Creăm blueprint-ul pentru planificări
schedule_bp = Blueprint('schedule', __name__)

@schedule_bp.route('', methods=['GET'])
@jwt_required()
def get_schedules():
    """
    Endpoint pentru obținerea planificărilor
    
    Query parameters:
    - group_id: ID-ul grupei (opțional)
    - teacher_id: ID-ul cadrului didactic (opțional)
    - start_date: Data de început pentru filtrare (opțional, format: YYYY-MM-DD)
    - end_date: Data de sfârșit pentru filtrare (opțional, format: YYYY-MM-DD)
    - status: Statusul planificării (opțional, valori: 'proposed', 'approved', 'rejected')
    
    Response:
    [
        {
            "id": 1,
            "subject": {
                "id": 1,
                "name": "Programare Web",
                "acronym": "PW"
            },
            "teacher": {
                "id": 1,
                "firstName": "Nume",
                "lastName": "Prenume",
                "email": "email@usv.ro"
            },
            "group": {
                "id": 1,
                "name": "3A4",
                "year": 3,
                "specialization": "Calculatoare"
            },
            "room": {
                "id": 1,
                "name": "C201",
                "capacity": 30,
                "building": "C"
            },
            "date": "2023-06-15",
            "startTime": "10:00",
            "endTime": "12:00",
            "status": "approved",
            "createdAt": "2023-05-01T12:00:00Z",
            "updatedAt": "2023-05-02T14:30:00Z"
        }
    ]
    """
    # Obținem parametrii din query string
    group_id = request.args.get('group_id', type=int)
    teacher_id = request.args.get('teacher_id', type=int)
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    status = request.args.get('status')
    
    # Convertim datele din string în obiecte date
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
    
    # Inițializăm serviciul de planificare
    db_session = get_db_session()
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
    return jsonify([schedule.to_dict() for schedule in schedules])

@schedule_bp.route('/<int:schedule_id>', methods=['GET'])
@jwt_required()
def get_schedule(schedule_id):
    """
    Endpoint pentru obținerea unei planificări după ID
    
    Response:
    {
        "id": 1,
        "subject": {
            "id": 1,
            "name": "Programare Web",
            "acronym": "PW"
        },
        "teacher": {
            "id": 1,
            "firstName": "Nume",
            "lastName": "Prenume",
            "email": "email@usv.ro"
        },
        "group": {
            "id": 1,
            "name": "3A4",
            "year": 3,
            "specialization": "Calculatoare"
        },
        "room": {
            "id": 1,
            "name": "C201",
            "capacity": 30,
            "building": "C"
        },
        "date": "2023-06-15",
        "startTime": "10:00",
        "endTime": "12:00",
        "status": "approved",
        "createdAt": "2023-05-01T12:00:00Z",
        "updatedAt": "2023-05-02T14:30:00Z"
    }
    """
    # Inițializăm serviciul de planificare
    db_session = get_db_session()
    schedule_service = ScheduleService(db_session=db_session)
    
    # Obținem planificarea
    schedule = schedule_service.get_schedule_by_id(schedule_id)
    
    if not schedule:
        return jsonify({"error": "Planificare negăsită"}), 404
    
    # Returnăm planificarea
    return jsonify(schedule.to_dict())

@schedule_bp.route('', methods=['POST'])
@jwt_required()
@role_required('SEC', 'ADM')
def create_schedule():
    """
    Endpoint pentru crearea unei planificări
    
    Request:
    {
        "subjectId": 1,
        "teacherId": 1,
        "groupId": 1,
        "roomId": 1,
        "date": "2023-06-15",
        "startTime": "10:00",
        "endTime": "12:00"
    }
    
    Response:
    {
        "id": 1,
        "subject": {
            "id": 1,
            "name": "Programare Web",
            "acronym": "PW"
        },
        "teacher": {
            "id": 1,
            "firstName": "Nume",
            "lastName": "Prenume",
            "email": "email@usv.ro"
        },
        "group": {
            "id": 1,
            "name": "3A4",
            "year": 3,
            "specialization": "Calculatoare"
        },
        "room": {
            "id": 1,
            "name": "C201",
            "capacity": 30,
            "building": "C"
        },
        "date": "2023-06-15",
        "startTime": "10:00",
        "endTime": "12:00",
        "status": "proposed",
        "createdAt": "2023-05-01T12:00:00Z",
        "updatedAt": "2023-05-01T12:00:00Z"
    }
    """
    # Obținem datele din request
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Date lipsă"}), 400
    
    # Validăm datele
    required_fields = ['subjectId', 'teacherId', 'groupId', 'roomId', 'date', 'startTime', 'endTime']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Câmpul '{field}' lipsește"}), 400
    
    # Convertim datele din string în obiecte date și timp
    try:
        date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        start_time = datetime.strptime(data['startTime'], '%H:%M').time()
        end_time = datetime.strptime(data['endTime'], '%H:%M').time()
    except ValueError:
        return jsonify({"error": "Format dată sau timp invalid"}), 400
    
    # Inițializăm serviciul de planificare
    db_session = get_db_session()
    schedule_service = ScheduleService(db_session=db_session)
    
    # Obținem ID-ul utilizatorului curent
    user_id = get_jwt_identity()
    
    # Creăm planificarea
    schedule = schedule_service.create_schedule(
        subject_id=data['subjectId'],
        teacher_id=data['teacherId'],
        group_id=data['groupId'],
        room_id=data['roomId'],
        date=date,
        start_time=start_time,
        end_time=end_time,
        created_by=user_id
    )
    
    if not schedule:
        return jsonify({"error": "Eroare la crearea planificării"}), 500
    
    # Trimitem notificări
    notification_service = NotificationService(
        db_session=db_session,
        api_key=current_app.config['SENDGRID_API_KEY']
    )
    
    notification_service.send_schedule_notification(
        schedule_id=schedule.id,
        notification_type='created'
    )
    
    # Returnăm planificarea creată
    return jsonify(schedule.to_dict()), 201

@schedule_bp.route('/<int:schedule_id>', methods=['PUT'])
@jwt_required()
@role_required('SEC', 'ADM')
def update_schedule(schedule_id):
    """
    Endpoint pentru actualizarea unei planificări
    
    Request:
    {
        "subjectId": 1,
        "teacherId": 1,
        "groupId": 1,
        "roomId": 1,
        "date": "2023-06-15",
        "startTime": "10:00",
        "endTime": "12:00",
        "status": "approved"
    }
    
    Response:
    {
        "id": 1,
        "subject": {
            "id": 1,
            "name": "Programare Web",
            "acronym": "PW"
        },
        "teacher": {
            "id": 1,
            "firstName": "Nume",
            "lastName": "Prenume",
            "email": "email@usv.ro"
        },
        "group": {
            "id": 1,
            "name": "3A4",
            "year": 3,
            "specialization": "Calculatoare"
        },
        "room": {
            "id": 1,
            "name": "C201",
            "capacity": 30,
            "building": "C"
        },
        "date": "2023-06-15",
        "startTime": "10:00",
        "endTime": "12:00",
        "status": "approved",
        "createdAt": "2023-05-01T12:00:00Z",
        "updatedAt": "2023-05-02T14:30:00Z"
    }
    """
    # Obținem datele din request
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Date lipsă"}), 400
    
    # Convertim datele din string în obiecte date și timp, dacă sunt furnizate
    date = None
    start_time = None
    end_time = None
    
    if 'date' in data:
        try:
            date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Format dată invalid"}), 400
    
    if 'startTime' in data:
        try:
            start_time = datetime.strptime(data['startTime'], '%H:%M').time()
        except ValueError:
            return jsonify({"error": "Format timp de început invalid"}), 400
    
    if 'endTime' in data:
        try:
            end_time = datetime.strptime(data['endTime'], '%H:%M').time()
        except ValueError:
            return jsonify({"error": "Format timp de sfârșit invalid"}), 400
    
    # Inițializăm serviciul de planificare
    db_session = get_db_session()
    schedule_service = ScheduleService(db_session=db_session)
    
    # Obținem ID-ul utilizatorului curent
    user_id = get_jwt_identity()
    
    # Actualizăm planificarea
    schedule = schedule_service.update_schedule(
        schedule_id=schedule_id,
        subject_id=data.get('subjectId'),
        teacher_id=data.get('teacherId'),
        group_id=data.get('groupId'),
        room_id=data.get('roomId'),
        date=date,
        start_time=start_time,
        end_time=end_time,
        status=data.get('status'),
        updated_by=user_id
    )
    
    if not schedule:
        return jsonify({"error": "Planificare negăsită sau eroare la actualizare"}), 404
    
    # Trimitem notificări dacă statusul a fost actualizat
    if 'status' in data:
        notification_service = NotificationService(
            db_session=db_session,
            api_key=current_app.config['SENDGRID_API_KEY']
        )
        
        notification_type = 'approved' if data['status'] == 'approved' else 'rejected'
        
        notification_service.send_schedule_notification(
            schedule_id=schedule.id,
            notification_type=notification_type
        )
    
    # Returnăm planificarea actualizată
    return jsonify(schedule.to_dict())

@schedule_bp.route('/<int:schedule_id>', methods=['DELETE'])
@jwt_required()
@role_required('SEC', 'ADM')
def delete_schedule(schedule_id):
    """
    Endpoint pentru ștergerea unei planificări
    
    Response:
    {
        "message": "Planificare ștearsă cu succes"
    }
    """
    # Inițializăm serviciul de planificare
    db_session = get_db_session()
    schedule_service = ScheduleService(db_session=db_session)
    
    # Obținem ID-ul utilizatorului curent
    user_id = get_jwt_identity()
    
    # Ștergem planificarea
    success = schedule_service.delete_schedule(
        schedule_id=schedule_id,
        deleted_by=user_id
    )
    
    if not success:
        return jsonify({"error": "Planificare negăsită sau eroare la ștergere"}), 404
    
    # Trimitem notificări
    notification_service = NotificationService(
        db_session=db_session,
        api_key=current_app.config['SENDGRID_API_KEY']
    )
    
    notification_service.send_schedule_notification(
        schedule_id=schedule_id,
        notification_type='deleted'
    )
    
    # Returnăm mesajul de succes
    return jsonify({
        "message": "Planificare ștearsă cu succes"
    })

@schedule_bp.route('/propose', methods=['POST'])
@jwt_required()
@role_required('CD')
def propose_schedule():
    """
    Endpoint pentru propunerea unei planificări de către un cadru didactic
    
    Request:
    {
        "subjectId": 1,
        "groupId": 1,
        "date": "2023-06-15",
        "startTime": "10:00",
        "endTime": "12:00",
        "roomId": 1 (opțional)
    }
    
    Response:
    {
        "id": 1,
        "subject": {
            "id": 1,
            "name": "Programare Web",
            "acronym": "PW"
        },
        "teacher": {
            "id": 1,
            "firstName": "Nume",
            "lastName": "Prenume",
            "email": "email@usv.ro"
        },
        "group": {
            "id": 1,
            "name": "3A4",
            "year": 3,
            "specialization": "Calculatoare"
        },
        "room": {
            "id": 1,
            "name": "C201",
            "capacity": 30,
            "building": "C"
        },
        "date": "2023-06-15",
        "startTime": "10:00",
        "endTime": "12:00",
        "status": "proposed",
        "createdAt": "2023-05-01T12:00:00Z",
        "updatedAt": "2023-05-01T12:00:00Z"
    }
    """
    # Obținem datele din request
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Date lipsă"}), 400
    
    # Validăm datele
    required_fields = ['subjectId', 'groupId', 'date', 'startTime', 'endTime']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Câmpul '{field}' lipsește"}), 400
    
    # Convertim datele din string în obiecte date și timp
    try:
        date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        start_time = datetime.strptime(data['startTime'], '%H:%M').time()
        end_time = datetime.strptime(data['endTime'], '%H:%M').time()
    except ValueError:
        return jsonify({"error": "Format dată sau timp invalid"}), 400
    
    # Inițializăm serviciul de planificare
    db_session = get_db_session()
    schedule_service = ScheduleService(db_session=db_session)
    
    # Obținem ID-ul utilizatorului curent (cadrul didactic)
    user_id = get_jwt_identity()
    
    # Obținem cadrul didactic asociat utilizatorului
    try:
        teacher = db_session.query(Teacher).join(User).filter(User.id == user_id).first()
        
        if not teacher:
            return jsonify({"error": "Cadru didactic negăsit pentru utilizatorul curent"}), 404
        
        # Creăm planificarea
        schedule = schedule_service.create_schedule(
            subject_id=data['subjectId'],
            teacher_id=teacher.id,
            group_id=data['groupId'],
            room_id=data.get('roomId'),  # Poate fi None
            date=date,
            start_time=start_time,
            end_time=end_time,
            created_by=user_id,
            status='proposed'
        )
        
        if not schedule:
            return jsonify({"error": "Eroare la propunerea planificării"}), 500
        
        # Trimitem notificări
        notification_service = NotificationService(
            db_session=db_session,
            api_key=current_app.config['SENDGRID_API_KEY']
        )
        
        notification_service.send_schedule_notification(
            schedule_id=schedule.id,
            notification_type='proposed'
        )
        
        # Returnăm planificarea propusă
        return jsonify(schedule.to_dict()), 201
    except SQLAlchemyError as e:
        db_session.rollback()
        return jsonify({"error": f"Eroare la propunerea planificării: {str(e)}"}), 500

@schedule_bp.route('/conflicts', methods=['GET'])
@jwt_required()
@role_required('SEC', 'ADM', 'CD')
def get_conflicts():
    """
    Endpoint pentru obținerea conflictelor de planificare
    
    Query parameters:
    - start_date: Data de început pentru filtrare (opțional, format: YYYY-MM-DD)
    - end_date: Data de sfârșit pentru filtrare (opțional, format: YYYY-MM-DD)
    
    Response:
    [
        {
            "type": "room",
            "schedules": [
                {
                    "id": 1,
                    "subject": {
                        "id": 1,
                        "name": "Programare Web",
                        "acronym": "PW"
                    },
                    "teacher": {
                        "id": 1,
                        "firstName": "Nume",
                        "lastName": "Prenume",
                        "email": "email@usv.ro"
                    },
                    "group": {
                        "id": 1,
                        "name": "3A4",
                        "year": 3,
                        "specialization": "Calculatoare"
                    },
                    "room": {
                        "id": 1,
                        "name": "C201",
                        "capacity": 30,
                        "building": "C"
                    },
                    "date": "2023-06-15",
                    "startTime": "10:00",
                    "endTime": "12:00",
                    "status": "approved"
                },
                {
                    "id": 2,
                    "subject": {
                        "id": 2,
                        "name": "Baze de Date",
                        "acronym": "BD"
                    },
                    "teacher": {
                        "id": 2,
                        "firstName": "Nume2",
                        "lastName": "Prenume2",
                        "email": "email2@usv.ro"
                    },
                    "group": {
                        "id": 2,
                        "name": "3B4",
                        "year": 3,
                        "specialization": "Calculatoare"
                    },
                    "room": {
                        "id": 1,
                        "name": "C201",
                        "capacity": 30,
                        "building": "C"
                    },
                    "date": "2023-06-15",
                    "startTime": "11:00",
                    "endTime": "13:00",
                    "status": "approved"
                }
            ]
        }
    ]
    """
    # Obținem parametrii din query string
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    # Convertim datele din string în obiecte date
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
    
    # Inițializăm serviciul de planificare
    db_session = get_db_session()
    schedule_service = ScheduleService(db_session=db_session)
    
    # Obținem conflictele
    conflicts = schedule_service.get_conflicts(
        start_date=start_date,
        end_date=end_date
    )
    
    # Returnăm lista de conflicte
    return jsonify(conflicts)

@schedule_bp.route('/available-rooms', methods=['GET'])
@jwt_required()
def get_available_rooms():
    """
    Endpoint pentru obținerea sălilor disponibile pentru o anumită dată și interval orar
    
    Query parameters:
    - date: Data pentru care se caută săli disponibile (format: YYYY-MM-DD)
    - start_time: Ora de început (format: HH:MM)
    - end_time: Ora de sfârșit (format: HH:MM)
    - capacity: Capacitatea minimă a sălii (opțional)
    
    Response:
    [
        {
            "id": 1,
            "name": "C201",
            "capacity": 30,
            "building": "C"
        }
    ]
    """
    # Obținem parametrii din query string
    date_str = request.args.get('date')
    start_time_str = request.args.get('start_time')
    end_time_str = request.args.get('end_time')
    capacity = request.args.get('capacity', type=int)
    
    # Validăm parametrii
    if not date_str or not start_time_str or not end_time_str:
        return jsonify({"error": "Parametrii lipsă: date, start_time, end_time sunt obligatorii"}), 400
    
    # Convertim datele din string în obiecte date și timp
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time()
    except ValueError:
        return jsonify({"error": "Format dată sau timp invalid"}), 400
    
    # Inițializăm serviciul de planificare
    db_session = get_db_session()
    schedule_service = ScheduleService(db_session=db_session)
    
    # Obținem sălile disponibile
    rooms = schedule_service.get_available_rooms(
        date=date,
        start_time=start_time,
        end_time=end_time,
        capacity=capacity
    )
    
    # Returnăm lista de săli disponibile
    return jsonify([{
        "id": room.id,
        "name": room.name,
        "capacity": room.capacity,
        "building": room.building
    } for room in rooms])
