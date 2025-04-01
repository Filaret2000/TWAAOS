from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import os
from werkzeug.utils import secure_filename

from src.common.models import User
from src.common.services import ExcelService
from src.flask_app.utils.db import get_db_session
from src.flask_app.utils.decorators import role_required

# Creăm blueprint-ul pentru upload
upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/excel/template', methods=['GET'])
@jwt_required()
@role_required('SEC', 'ADM')
def get_excel_templates():
    """
    Endpoint pentru obținerea template-urilor Excel disponibile
    
    Response:
    [
        {
            "id": 1,
            "name": "Template Discipline",
            "description": "Template pentru încărcarea disciplinelor"
        }
    ]
    """
    # Inițializăm serviciul Excel
    db_session = get_db_session()
    excel_service = ExcelService(
        db_session=db_session,
        upload_folder=os.path.join(current_app.root_path, 'uploads')
    )
    
    # Obținem template-urile disponibile
    templates = excel_service.get_templates()
    
    # Returnăm lista de template-uri
    return jsonify([{
        "id": template.id,
        "name": template.name,
        "description": template.description
    } for template in templates])

@upload_bp.route('/excel/template/<int:template_id>', methods=['GET'])
@jwt_required()
@role_required('SEC', 'ADM')
def download_excel_template(template_id):
    """
    Endpoint pentru descărcarea unui template Excel
    
    Response:
    Fișier Excel template
    """
    # Inițializăm serviciul Excel
    db_session = get_db_session()
    excel_service = ExcelService(
        db_session=db_session,
        upload_folder=os.path.join(current_app.root_path, 'uploads')
    )
    
    # Obținem template-ul
    template = excel_service.get_template_by_id(template_id)
    
    if not template:
        return jsonify({"error": "Template negăsit"}), 404
    
    # Descărcăm template-ul
    template_data = excel_service.download_template(template_id)
    
    if not template_data:
        return jsonify({"error": "Eroare la descărcarea template-ului"}), 500
    
    # Returnăm fișierul Excel
    return send_file(
        io.BytesIO(template_data),
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f"{template.name}.xlsx"
    )

@upload_bp.route('/excel/template', methods=['POST'])
@jwt_required()
@role_required('SEC', 'ADM')
def create_excel_template():
    """
    Endpoint pentru crearea unui nou template Excel
    
    Request:
    {
        "name": "Template Discipline",
        "description": "Template pentru încărcarea disciplinelor"
    }
    
    Response:
    {
        "id": 1,
        "name": "Template Discipline",
        "description": "Template pentru încărcarea disciplinelor"
    }
    """
    # Obținem datele din request
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Date lipsă"}), 400
    
    # Validăm datele
    required_fields = ['name', 'description']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Câmpul '{field}' lipsește"}), 400
    
    # Inițializăm serviciul Excel
    db_session = get_db_session()
    excel_service = ExcelService(
        db_session=db_session,
        upload_folder=os.path.join(current_app.root_path, 'uploads')
    )
    
    # Creăm template-ul
    template = excel_service.create_template(
        name=data['name'],
        description=data['description']
    )
    
    if not template:
        return jsonify({"error": "Eroare la crearea template-ului"}), 500
    
    # Returnăm informațiile template-ului creat
    return jsonify({
        "id": template.id,
        "name": template.name,
        "description": template.description
    }), 201

@upload_bp.route('/excel/subjects', methods=['POST'])
@jwt_required()
@role_required('SEC', 'ADM')
def upload_subjects():
    """
    Endpoint pentru încărcarea disciplinelor din Excel
    
    Request:
    Formular multipart cu fișier Excel
    
    Response:
    {
        "success": true,
        "message": "Import finalizat: 10 discipline importate, 0 erori",
        "imported": 10,
        "errors": 0
    }
    """
    # Verificăm dacă a fost furnizat un fișier
    if 'file' not in request.files:
        return jsonify({"error": "Niciun fișier furnizat"}), 400
    
    file = request.files['file']
    
    # Verificăm dacă fișierul are un nume
    if file.filename == '':
        return jsonify({"error": "Niciun fișier selectat"}), 400
    
    # Verificăm extensia fișierului
    allowed_extensions = {'xlsx', 'xls'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({"error": "Extensie fișier invalidă. Sunt permise doar fișiere Excel (.xlsx, .xls)"}), 400
    
    # Inițializăm serviciul Excel
    db_session = get_db_session()
    excel_service = ExcelService(
        db_session=db_session,
        upload_folder=os.path.join(current_app.root_path, 'uploads')
    )
    
    # Importăm disciplinele din Excel
    result = excel_service.import_subjects_from_excel(file)
    
    # Returnăm rezultatul importului
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 500

@upload_bp.route('/excel/group-leaders', methods=['POST'])
@jwt_required()
@role_required('SEC', 'ADM')
def upload_group_leaders():
    """
    Endpoint pentru încărcarea șefilor de grupă din Excel
    
    Request:
    Formular multipart cu fișier Excel
    
    Response:
    {
        "success": true,
        "message": "Import finalizat: 5 șefi de grupă importați, 0 erori",
        "imported": 5,
        "errors": 0
    }
    """
    # Verificăm dacă a fost furnizat un fișier
    if 'file' not in request.files:
        return jsonify({"error": "Niciun fișier furnizat"}), 400
    
    file = request.files['file']
    
    # Verificăm dacă fișierul are un nume
    if file.filename == '':
        return jsonify({"error": "Niciun fișier selectat"}), 400
    
    # Verificăm extensia fișierului
    allowed_extensions = {'xlsx', 'xls'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({"error": "Extensie fișier invalidă. Sunt permise doar fișiere Excel (.xlsx, .xls)"}), 400
    
    # Inițializăm serviciul Excel
    db_session = get_db_session()
    excel_service = ExcelService(
        db_session=db_session,
        upload_folder=os.path.join(current_app.root_path, 'uploads')
    )
    
    # Importăm șefii de grupă din Excel
    result = excel_service.import_group_leaders_from_excel(file)
    
    # Returnăm rezultatul importului
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 500
