from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.common.models import User, Notification
from src.common.services import NotificationService
from src.flask_app.utils.db import get_db_session
from src.flask_app.utils.decorators import role_required

# Creăm blueprint-ul pentru notificări
notification_bp = Blueprint('notification', __name__)

@notification_bp.route('', methods=['GET'])
@jwt_required()
def get_notifications():
    """
    Endpoint pentru obținerea notificărilor utilizatorului curent
    
    Query parameters:
    - unread_only: Dacă se returnează doar notificările necitite (opțional, default: false)
    - page: Numărul paginii (opțional, default: 1)
    - per_page: Numărul de notificări per pagină (opțional, default: 10)
    
    Response:
    {
        "notifications": [
            {
                "id": 1,
                "title": "Planificare nouă",
                "message": "A fost adăugată o planificare nouă pentru grupa 3A4",
                "type": "schedule",
                "read": false,
                "createdAt": "2023-05-01T12:00:00Z"
            }
        ],
        "pagination": {
            "page": 1,
            "per_page": 10,
            "total_pages": 1,
            "total_items": 1
        }
    }
    """
    # Obținem parametrii din query string
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Obținem ID-ul utilizatorului curent
    user_id = get_jwt_identity()
    
    # Inițializăm serviciul de notificări
    db_session = get_db_session()
    notification_service = NotificationService(
        db_session=db_session,
        api_key=current_app.config['SENDGRID_API_KEY']
    )
    
    # Obținem notificările
    notifications, pagination = notification_service.get_user_notifications(
        user_id=user_id,
        unread_only=unread_only,
        page=page,
        per_page=per_page
    )
    
    # Returnăm lista de notificări
    return jsonify({
        "notifications": [notification.to_dict() for notification in notifications],
        "pagination": pagination
    })

@notification_bp.route('/<int:notification_id>/read', methods=['POST'])
@jwt_required()
def mark_notification_as_read(notification_id):
    """
    Endpoint pentru marcarea unei notificări ca citită
    
    Response:
    {
        "success": true,
        "message": "Notificare marcată ca citită"
    }
    """
    # Obținem ID-ul utilizatorului curent
    user_id = get_jwt_identity()
    
    # Inițializăm serviciul de notificări
    db_session = get_db_session()
    notification_service = NotificationService(
        db_session=db_session,
        api_key=current_app.config['SENDGRID_API_KEY']
    )
    
    # Marcăm notificarea ca citită
    success = notification_service.mark_notification_as_read(
        notification_id=notification_id,
        user_id=user_id
    )
    
    if not success:
        return jsonify({
            "success": False,
            "error": "Notificare negăsită sau nu aparține utilizatorului curent"
        }), 404
    
    # Returnăm mesajul de succes
    return jsonify({
        "success": True,
        "message": "Notificare marcată ca citită"
    })

@notification_bp.route('/read-all', methods=['POST'])
@jwt_required()
def mark_all_notifications_as_read():
    """
    Endpoint pentru marcarea tuturor notificărilor ca citite
    
    Response:
    {
        "success": true,
        "message": "Toate notificările au fost marcate ca citite",
        "count": 5
    }
    """
    # Obținem ID-ul utilizatorului curent
    user_id = get_jwt_identity()
    
    # Inițializăm serviciul de notificări
    db_session = get_db_session()
    notification_service = NotificationService(
        db_session=db_session,
        api_key=current_app.config['SENDGRID_API_KEY']
    )
    
    # Marcăm toate notificările ca citite
    count = notification_service.mark_all_notifications_as_read(user_id=user_id)
    
    # Returnăm mesajul de succes
    return jsonify({
        "success": True,
        "message": "Toate notificările au fost marcate ca citite",
        "count": count
    })

@notification_bp.route('/settings', methods=['GET'])
@jwt_required()
def get_notification_settings():
    """
    Endpoint pentru obținerea setărilor de notificare ale utilizatorului curent
    
    Response:
    {
        "email_notifications": true,
        "push_notifications": false,
        "schedule_notifications": true,
        "system_notifications": true
    }
    """
    # Obținem ID-ul utilizatorului curent
    user_id = get_jwt_identity()
    
    # Inițializăm serviciul de notificări
    db_session = get_db_session()
    notification_service = NotificationService(
        db_session=db_session,
        api_key=current_app.config['SENDGRID_API_KEY']
    )
    
    # Obținem setările de notificare
    settings = notification_service.get_notification_settings(user_id=user_id)
    
    # Returnăm setările de notificare
    return jsonify(settings)

@notification_bp.route('/settings', methods=['PUT'])
@jwt_required()
def update_notification_settings():
    """
    Endpoint pentru actualizarea setărilor de notificare ale utilizatorului curent
    
    Request:
    {
        "email_notifications": true,
        "push_notifications": false,
        "schedule_notifications": true,
        "system_notifications": true
    }
    
    Response:
    {
        "success": true,
        "message": "Setări de notificare actualizate cu succes",
        "settings": {
            "email_notifications": true,
            "push_notifications": false,
            "schedule_notifications": true,
            "system_notifications": true
        }
    }
    """
    # Obținem datele din request
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Date lipsă"}), 400
    
    # Obținem ID-ul utilizatorului curent
    user_id = get_jwt_identity()
    
    # Inițializăm serviciul de notificări
    db_session = get_db_session()
    notification_service = NotificationService(
        db_session=db_session,
        api_key=current_app.config['SENDGRID_API_KEY']
    )
    
    # Actualizăm setările de notificare
    settings = notification_service.update_notification_settings(
        user_id=user_id,
        email_notifications=data.get('email_notifications'),
        push_notifications=data.get('push_notifications'),
        schedule_notifications=data.get('schedule_notifications'),
        system_notifications=data.get('system_notifications')
    )
    
    # Returnăm mesajul de succes
    return jsonify({
        "success": True,
        "message": "Setări de notificare actualizate cu succes",
        "settings": settings
    })

@notification_bp.route('/admin/send', methods=['POST'])
@jwt_required()
@role_required('ADM', 'SEC')
def send_notification():
    """
    Endpoint pentru trimiterea unei notificări către utilizatori (doar pentru administrator și secretariat)
    
    Request:
    {
        "title": "Anunț important",
        "message": "Conținutul anunțului",
        "type": "system",
        "recipients": [1, 2, 3],  # ID-urile utilizatorilor (opțional)
        "role": "SG",  # Rolul utilizatorilor (opțional)
        "send_email": true  # Dacă se trimite și email (opțional, default: false)
    }
    
    Response:
    {
        "success": true,
        "message": "Notificare trimisă cu succes",
        "count": 3
    }
    """
    # Obținem datele din request
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Date lipsă"}), 400
    
    # Validăm datele
    required_fields = ['title', 'message', 'type']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Câmpul '{field}' lipsește"}), 400
    
    # Validăm tipul notificării
    valid_types = ['system', 'schedule', 'deadline', 'info']
    if data['type'] not in valid_types:
        return jsonify({"error": f"Tip notificare invalid. Tipurile valide sunt: {', '.join(valid_types)}"}), 400
    
    # Verificăm dacă a fost specificat cel puțin un criteriu de filtrare
    if 'recipients' not in data and 'role' not in data:
        return jsonify({"error": "Trebuie specificat cel puțin un criteriu de filtrare: recipients sau role"}), 400
    
    # Obținem ID-ul utilizatorului curent
    user_id = get_jwt_identity()
    
    # Inițializăm serviciul de notificări
    db_session = get_db_session()
    notification_service = NotificationService(
        db_session=db_session,
        api_key=current_app.config['SENDGRID_API_KEY']
    )
    
    # Trimitem notificarea
    count = notification_service.send_notification(
        title=data['title'],
        message=data['message'],
        notification_type=data['type'],
        recipients=data.get('recipients', []),
        role=data.get('role'),
        send_email=data.get('send_email', False),
        sender_id=user_id
    )
    
    # Returnăm mesajul de succes
    return jsonify({
        "success": True,
        "message": "Notificare trimisă cu succes",
        "count": count
    })
