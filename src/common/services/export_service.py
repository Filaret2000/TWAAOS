from typing import List, Optional, Dict, Any, BinaryIO
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import io
from datetime import date
import os
import tempfile
import pdfkit

from src.common.models import Schedule, Subject, Teacher, Room, Group

class ExportService:
    """Serviciu pentru exportul datelor în formate Excel și PDF"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def export_to_excel(self, 
                        group_id: Optional[int] = None, 
                        teacher_id: Optional[int] = None, 
                        start_date: Optional[date] = None,
                        end_date: Optional[date] = None) -> Optional[bytes]:
        """
        Exportă planificările examenelor în format Excel
        
        Args:
            group_id: ID-ul grupei (opțional)
            teacher_id: ID-ul cadrului didactic (opțional)
            start_date: Data de început pentru filtrare (opțional)
            end_date: Data de sfârșit pentru filtrare (opțional)
            
        Returns:
            Conținutul fișierului Excel ca bytes sau None în caz de eroare
        """
        try:
            # Construim query-ul pentru planificări
            query = self.db_session.query(
                Schedule.id,
                Schedule.date,
                Schedule.start_time,
                Schedule.end_time,
                Schedule.status,
                Subject.name.label('subject_name'),
                Subject.short_name.label('subject_short_name'),
                Teacher.first_name.label('teacher_first_name'),
                Teacher.last_name.label('teacher_last_name'),
                Room.name.label('room_name'),
                Group.name.label('group_name')
            ).join(Subject, Schedule.subject_id == Subject.id)\
             .join(Teacher, Schedule.teacher_id == Teacher.id)\
             .join(Group, Schedule.group_id == Group.id)\
             .outerjoin(Room, Schedule.room_id == Room.id)
            
            # Aplicăm filtrele
            if group_id:
                query = query.filter(Schedule.group_id == group_id)
            
            if teacher_id:
                query = query.filter(Schedule.teacher_id == teacher_id)
            
            if start_date:
                query = query.filter(Schedule.date >= start_date)
            
            if end_date:
                query = query.filter(Schedule.date <= end_date)
            
            # Executăm query-ul
            results = query.all()
            
            # Convertim rezultatele în dicționare
            data = []
            for row in results:
                data.append({
                    'ID': row.id,
                    'Disciplina': row.subject_name,
                    'Acronim': row.subject_short_name,
                    'Cadru didactic': f"{row.teacher_first_name} {row.teacher_last_name}",
                    'Grupa': row.group_name,
                    'Data': row.date,
                    'Ora început': row.start_time.strftime('%H:%M') if row.start_time else '',
                    'Ora sfârșit': row.end_time.strftime('%H:%M') if row.end_time else '',
                    'Sala': row.room_name or '',
                    'Status': row.status
                })
            
            # Creăm un DataFrame pandas
            df = pd.DataFrame(data)
            
            # Exportăm DataFrame-ul în Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Planificare Examene', index=False)
            
            return output.getvalue()
        except SQLAlchemyError as e:
            print(f"Eroare la exportul în Excel: {str(e)}")
            return None
        except Exception as e:
            print(f"Eroare la exportul în Excel: {str(e)}")
            return None
    
    def export_to_pdf(self, 
                      group_id: Optional[int] = None, 
                      teacher_id: Optional[int] = None, 
                      start_date: Optional[date] = None,
                      end_date: Optional[date] = None) -> Optional[bytes]:
        """
        Exportă planificările examenelor în format PDF
        
        Args:
            group_id: ID-ul grupei (opțional)
            teacher_id: ID-ul cadrului didactic (opțional)
            start_date: Data de început pentru filtrare (opțional)
            end_date: Data de sfârșit pentru filtrare (opțional)
            
        Returns:
            Conținutul fișierului PDF ca bytes sau None în caz de eroare
        """
        try:
            # Construim query-ul pentru planificări
            query = self.db_session.query(
                Schedule.id,
                Schedule.date,
                Schedule.start_time,
                Schedule.end_time,
                Schedule.status,
                Subject.name.label('subject_name'),
                Subject.short_name.label('subject_short_name'),
                Teacher.first_name.label('teacher_first_name'),
                Teacher.last_name.label('teacher_last_name'),
                Room.name.label('room_name'),
                Group.name.label('group_name')
            ).join(Subject, Schedule.subject_id == Subject.id)\
             .join(Teacher, Schedule.teacher_id == Teacher.id)\
             .join(Group, Schedule.group_id == Group.id)\
             .outerjoin(Room, Schedule.room_id == Room.id)
            
            # Aplicăm filtrele
            if group_id:
                query = query.filter(Schedule.group_id == group_id)
            
            if teacher_id:
                query = query.filter(Schedule.teacher_id == teacher_id)
            
            if start_date:
                query = query.filter(Schedule.date >= start_date)
            
            if end_date:
                query = query.filter(Schedule.date <= end_date)
            
            # Executăm query-ul
            results = query.all()
            
            # Convertim rezultatele în dicționare
            data = []
            for row in results:
                data.append({
                    'ID': row.id,
                    'Disciplina': row.subject_name,
                    'Acronim': row.subject_short_name,
                    'Cadru didactic': f"{row.teacher_first_name} {row.teacher_last_name}",
                    'Grupa': row.group_name,
                    'Data': row.date.strftime('%d.%m.%Y'),
                    'Ora început': row.start_time.strftime('%H:%M') if row.start_time else '',
                    'Ora sfârșit': row.end_time.strftime('%H:%M') if row.end_time else '',
                    'Sala': row.room_name or '',
                    'Status': row.status
                })
            
            # Creăm un DataFrame pandas
            df = pd.DataFrame(data)
            
            # Generăm HTML pentru PDF
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Planificare Examene FIESC</title>
                <style>
                    body { font-family: Arial, sans-serif; }
                    h1 { text-align: center; color: #003366; }
                    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                    th { background-color: #003366; color: white; padding: 8px; text-align: left; }
                    td { padding: 8px; border-bottom: 1px solid #ddd; }
                    tr:nth-child(even) { background-color: #f2f2f2; }
                </style>
            </head>
            <body>
                <h1>Planificare Examene FIESC</h1>
            """
            
            # Adăugăm informații despre filtre
            html += "<p><strong>Filtre aplicate:</strong> "
            if group_id:
                group = self.db_session.query(Group).filter(Group.id == group_id).first()
                if group:
                    html += f"Grupa: {group.name}, "
            
            if teacher_id:
                teacher = self.db_session.query(Teacher).filter(Teacher.id == teacher_id).first()
                if teacher:
                    html += f"Cadru didactic: {teacher.first_name} {teacher.last_name}, "
            
            if start_date:
                html += f"De la: {start_date.strftime('%d.%m.%Y')}, "
            
            if end_date:
                html += f"Până la: {end_date.strftime('%d.%m.%Y')}, "
            
            html = html.rstrip(", ") + "</p>"
            
            # Adăugăm tabelul cu date
            html += """
                <table>
                    <thead>
                        <tr>
                            <th>Disciplina</th>
                            <th>Cadru didactic</th>
                            <th>Grupa</th>
                            <th>Data</th>
                            <th>Ora</th>
                            <th>Sala</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for _, row in df.iterrows():
                status_text = {
                    'proposed': 'Propus',
                    'approved': 'Aprobat',
                    'rejected': 'Respins'
                }.get(row['Status'], row['Status'])
                
                html += f"""
                        <tr>
                            <td>{row['Disciplina']} ({row['Acronim']})</td>
                            <td>{row['Cadru didactic']}</td>
                            <td>{row['Grupa']}</td>
                            <td>{row['Data']}</td>
                            <td>{row['Ora început']} - {row['Ora sfârșit']}</td>
                            <td>{row['Sala']}</td>
                            <td>{status_text}</td>
                        </tr>
                """
            
            html += """
                    </tbody>
                </table>
            </body>
            </html>
            """
            
            # Generăm PDF din HTML folosind pdfkit
            options = {
                'page-size': 'A4',
                'margin-top': '20mm',
                'margin-right': '20mm',
                'margin-bottom': '20mm',
                'margin-left': '20mm',
                'encoding': 'UTF-8',
                'no-outline': None
            }
            
            # Salvăm HTML într-un fișier temporar
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
                f.write(html.encode('utf-8'))
                temp_html = f.name
            
            # Generăm PDF
            output_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            output_pdf.close()
            
            pdfkit.from_file(temp_html, output_pdf.name, options=options)
            
            # Citim conținutul PDF
            with open(output_pdf.name, 'rb') as f:
                pdf_content = f.read()
            
            # Ștergem fișierele temporare
            os.unlink(temp_html)
            os.unlink(output_pdf.name)
            
            return pdf_content
        except SQLAlchemyError as e:
            print(f"Eroare la exportul în PDF: {str(e)}")
            return None
        except Exception as e:
            print(f"Eroare la exportul în PDF: {str(e)}")
            return None
