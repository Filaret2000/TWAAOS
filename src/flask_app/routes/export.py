from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import io
from datetime import datetime

from src.common.models import User
from src.common.services import ExportService
from src.flask_app.utils.db import get_db_session
from src.flask_app.utils.decorators import role_required

# Creăm blueprint-ul pentru export
export_bp = Blueprint('export', __name__)

@export_bp.route('/excel', methods=['GET'])
@jwt_required()
@role_required('SEC', 'ADM')
def export_excel():
    """
    Endpoint pentru exportul planificărilor în format Excel
    
    Query parameters:
    - group_id: ID-ul grupei (opțional)
    - teacher_id: ID-ul cadrului didactic (opțional)
    - start_date: Data de început pentru filtrare (opțional, format: YYYY-MM-DD)
    - end_date: Data de sfârșit pentru filtrare (opțional, format: YYYY-MM-DD)
    
    Response:
    Fișier Excel cu planificarea examenelor
    """
    # Obținem parametrii din query string
    group_id = request.args.get('group_id', type=int)
    teacher_id = request.args.get('teacher_id', type=int)
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    # Convertim datele din string în obiecte date
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
    
    # Inițializăm serviciul de export
    db_session = get_db_session()
    export_service = ExportService(db_session=db_session)
    
    # Generăm fișierul Excel
    excel_data = export_service.export_to_excel(
        group_id=group_id,
        teacher_id=teacher_id,
        start_date=start_date,
        end_date=end_date
    )
    
    if not excel_data:
        return jsonify({"error": "Eroare la generarea fișierului Excel"}), 500
    
    # Creăm un fișier în memorie
    excel_file = io.BytesIO(excel_data)
    excel_file.seek(0)
    
    # Generăm numele fișierului
    filename = f"planificare_examene_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    # Returnăm fișierul Excel
    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

@export_bp.route('/pdf', methods=['GET'])
@jwt_required()
@role_required('SEC', 'ADM', 'CD', 'SG')
def export_pdf():
    """
    Endpoint pentru exportul planificărilor în format PDF
    
    Query parameters:
    - group_id: ID-ul grupei (opțional)
    - teacher_id: ID-ul cadrului didactic (opțional)
    - start_date: Data de început pentru filtrare (opțional, format: YYYY-MM-DD)
    - end_date: Data de sfârșit pentru filtrare (opțional, format: YYYY-MM-DD)
    
    Response:
    Fișier PDF cu planificarea examenelor
    """
    # Obținem parametrii din query string
    group_id = request.args.get('group_id', type=int)
    teacher_id = request.args.get('teacher_id', type=int)
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    # Convertim datele din string în obiecte date
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
    
    # Inițializăm serviciul de export
    db_session = get_db_session()
    export_service = ExportService(db_session=db_session)
    
    # Generăm fișierul PDF
    pdf_data = export_service.export_to_pdf(
        group_id=group_id,
        teacher_id=teacher_id,
        start_date=start_date,
        end_date=end_date
    )
    
    if not pdf_data:
        return jsonify({"error": "Eroare la generarea fișierului PDF"}), 500
    
    # Creăm un fișier în memorie
    pdf_file = io.BytesIO(pdf_data)
    pdf_file.seek(0)
    
    # Generăm numele fișierului
    filename = f"planificare_examene_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    # Returnăm fișierul PDF
    return send_file(
        pdf_file,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )
