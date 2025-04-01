from typing import List, Dict, Any, Optional, BinaryIO
import pandas as pd
import io
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import os

from src.common.models import ExcelTemplate, Subject, Teacher, Group, User

class ExcelService:
    """Serviciu pentru gestionarea fișierelor Excel"""
    
    def __init__(self, db_session: Session, upload_folder: str):
        self.db_session = db_session
        self.upload_folder = upload_folder
        
        # Creăm directorul pentru upload-uri dacă nu există
        os.makedirs(self.upload_folder, exist_ok=True)
    
    def get_templates(self) -> List[ExcelTemplate]:
        """
        Obține toate template-urile Excel disponibile
        
        Returns:
            Listă de obiecte ExcelTemplate
        """
        try:
            return self.db_session.query(ExcelTemplate).all()
        except SQLAlchemyError as e:
            print(f"Eroare la obținerea template-urilor: {str(e)}")
            return []
    
    def get_template_by_id(self, template_id: int) -> Optional[ExcelTemplate]:
        """
        Obține un template Excel după ID
        
        Args:
            template_id: ID-ul template-ului
            
        Returns:
            Obiectul ExcelTemplate sau None dacă template-ul nu există
        """
        try:
            return self.db_session.query(ExcelTemplate).filter(ExcelTemplate.id == template_id).first()
        except SQLAlchemyError as e:
            print(f"Eroare la obținerea template-ului: {str(e)}")
            return None
    
    def create_template(self, name: str, description: str) -> Optional[ExcelTemplate]:
        """
        Creează un nou template Excel
        
        Args:
            name: Numele template-ului
            description: Descrierea template-ului
            
        Returns:
            Obiectul ExcelTemplate creat sau None în caz de eroare
        """
        try:
            # Generăm calea către fișierul template
            file_path = os.path.join(self.upload_folder, f"{name.lower().replace(' ', '_')}.xlsx")
            
            # Creăm template-ul în baza de date
            template = ExcelTemplate(
                name=name,
                file_path=file_path,
                description=description
            )
            
            self.db_session.add(template)
            self.db_session.commit()
            
            # Generăm fișierul Excel template
            self._generate_template_file(template)
            
            return template
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"Eroare la crearea template-ului: {str(e)}")
            return None
    
    def _generate_template_file(self, template: ExcelTemplate) -> bool:
        """
        Generează fișierul Excel pentru un template
        
        Args:
            template: Obiectul ExcelTemplate
            
        Returns:
            True dacă fișierul a fost generat cu succes, False în caz contrar
        """
        try:
            # Determinăm tipul de template după nume
            if "discipline" in template.name.lower():
                return self._generate_subjects_template(template.file_path)
            elif "cadre" in template.name.lower() or "profesori" in template.name.lower():
                return self._generate_teachers_template(template.file_path)
            elif "grupe" in template.name.lower():
                return self._generate_groups_template(template.file_path)
            elif "sefi" in template.name.lower():
                return self._generate_group_leaders_template(template.file_path)
            else:
                # Template generic
                return self._generate_generic_template(template.file_path)
        except Exception as e:
            print(f"Eroare la generarea fișierului template: {str(e)}")
            return False
    
    def _generate_subjects_template(self, file_path: str) -> bool:
        """
        Generează un template Excel pentru discipline
        
        Args:
            file_path: Calea către fișierul template
            
        Returns:
            True dacă fișierul a fost generat cu succes, False în caz contrar
        """
        try:
            # Creăm un DataFrame gol cu coloanele necesare
            df = pd.DataFrame(columns=[
                'Nume Disciplină',
                'Acronim',
                'Program Studiu',
                'An Studiu',
                'Grupa',
                'Cadru Didactic Titular (Email)',
                'Tip Evaluare (Examen/Colocviu)'
            ])
            
            # Adăugăm câteva exemple
            df.loc[0] = [
                'Tehnologii Web Avansate și Aplicații Orientate spre Servicii',
                'TWAAOS',
                'Calculatoare',
                3,
                '3A2',
                'profesor@usm.ro',
                'Examen'
            ]
            
            df.loc[1] = [
                'Programare Paralelă și Distribuită',
                'PPD',
                'Calculatoare',
                3,
                '3A2',
                'alt.profesor@usm.ro',
                'Colocviu'
            ]
            
            # Salvăm DataFrame-ul în Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Discipline', index=False)
            
            return True
        except Exception as e:
            print(f"Eroare la generarea template-ului pentru discipline: {str(e)}")
            return False
    
    def _generate_teachers_template(self, file_path: str) -> bool:
        """
        Generează un template Excel pentru cadre didactice
        
        Args:
            file_path: Calea către fișierul template
            
        Returns:
            True dacă fișierul a fost generat cu succes, False în caz contrar
        """
        try:
            # Creăm un DataFrame gol cu coloanele necesare
            df = pd.DataFrame(columns=[
                'Prenume',
                'Nume',
                'Email',
                'Departament'
            ])
            
            # Adăugăm câteva exemple
            df.loc[0] = [
                'Ion',
                'Popescu',
                'ion.popescu@usm.ro',
                'Calculatoare'
            ]
            
            df.loc[1] = [
                'Maria',
                'Ionescu',
                'maria.ionescu@usm.ro',
                'Automatică'
            ]
            
            # Salvăm DataFrame-ul în Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Cadre Didactice', index=False)
            
            return True
        except Exception as e:
            print(f"Eroare la generarea template-ului pentru cadre didactice: {str(e)}")
            return False
    
    def _generate_groups_template(self, file_path: str) -> bool:
        """
        Generează un template Excel pentru grupe
        
        Args:
            file_path: Calea către fișierul template
            
        Returns:
            True dacă fișierul a fost generat cu succes, False în caz contrar
        """
        try:
            # Creăm un DataFrame gol cu coloanele necesare
            df = pd.DataFrame(columns=[
                'Nume Grupă',
                'An Studiu',
                'Specializare'
            ])
            
            # Adăugăm câteva exemple
            df.loc[0] = [
                '3A2',
                3,
                'Calculatoare'
            ]
            
            df.loc[1] = [
                '4B1',
                4,
                'Automatică'
            ]
            
            # Salvăm DataFrame-ul în Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Grupe', index=False)
            
            return True
        except Exception as e:
            print(f"Eroare la generarea template-ului pentru grupe: {str(e)}")
            return False
    
    def _generate_group_leaders_template(self, file_path: str) -> bool:
        """
        Generează un template Excel pentru șefi de grupă
        
        Args:
            file_path: Calea către fișierul template
            
        Returns:
            True dacă fișierul a fost generat cu succes, False în caz contrar
        """
        try:
            # Creăm un DataFrame gol cu coloanele necesare
            df = pd.DataFrame(columns=[
                'Prenume',
                'Nume',
                'Email',
                'Grupă'
            ])
            
            # Adăugăm câteva exemple
            df.loc[0] = [
                'Alexandru',
                'Popescu',
                'alexandru.popescu@student.usv.ro',
                '3A2'
            ]
            
            df.loc[1] = [
                'Elena',
                'Ionescu',
                'elena.ionescu@student.usv.ro',
                '4B1'
            ]
            
            # Salvăm DataFrame-ul în Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Șefi Grupă', index=False)
            
            return True
        except Exception as e:
            print(f"Eroare la generarea template-ului pentru șefi de grupă: {str(e)}")
            return False
    
    def _generate_generic_template(self, file_path: str) -> bool:
        """
        Generează un template Excel generic
        
        Args:
            file_path: Calea către fișierul template
            
        Returns:
            True dacă fișierul a fost generat cu succes, False în caz contrar
        """
        try:
            # Creăm un DataFrame gol cu coloanele necesare
            df = pd.DataFrame(columns=[
                'Coloana 1',
                'Coloana 2',
                'Coloana 3'
            ])
            
            # Adăugăm câteva exemple
            df.loc[0] = [
                'Valoare 1',
                'Valoare 2',
                'Valoare 3'
            ]
            
            # Salvăm DataFrame-ul în Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Date', index=False)
            
            return True
        except Exception as e:
            print(f"Eroare la generarea template-ului generic: {str(e)}")
            return False
    
    def import_subjects_from_excel(self, file_content: BinaryIO) -> Dict[str, Any]:
        """
        Importă discipline dintr-un fișier Excel
        
        Args:
            file_content: Conținutul fișierului Excel
            
        Returns:
            Dicționar cu rezultatele importului
        """
        try:
            # Citim fișierul Excel
            df = pd.read_excel(file_content)
            
            # Verificăm coloanele necesare
            required_columns = [
                'Nume Disciplină',
                'Acronim',
                'Program Studiu',
                'An Studiu',
                'Grupa',
                'Cadru Didactic Titular (Email)',
                'Tip Evaluare (Examen/Colocviu)'
            ]
            
            for column in required_columns:
                if column not in df.columns:
                    return {
                        'success': False,
                        'message': f"Coloana '{column}' lipsește din fișier",
                        'imported': 0,
                        'errors': 0
                    }
            
            # Procesăm fiecare rând
            imported = 0
            errors = 0
            error_details = []
            
            for index, row in df.iterrows():
                try:
                    # Obținem sau creăm grupa
                    group_name = row['Grupa']
                    group = self.db_session.query(Group).filter(Group.name == group_name).first()
                    
                    if not group:
                        # Creăm grupa dacă nu există
                        study_year = int(row['An Studiu'])
                        specialization = group_name[1] if len(group_name) > 1 else ''
                        
                        group = Group(
                            name=group_name,
                            study_year=study_year,
                            specialization_short_name=specialization
                        )
                        self.db_session.add(group)
                        self.db_session.flush()  # Pentru a obține ID-ul grupei
                    
                    # Obținem sau creăm cadrul didactic
                    teacher_email = row['Cadru Didactic Titular (Email)']
                    teacher = self.db_session.query(Teacher).filter(Teacher.email == teacher_email).first()
                    
                    if not teacher:
                        # Creăm cadrul didactic dacă nu există
                        # Presupunem că emailul este în format prenume.nume@usm.ro
                        email_parts = teacher_email.split('@')[0].split('.')
                        first_name = email_parts[0].capitalize() if len(email_parts) > 0 else "Unknown"
                        last_name = email_parts[1].capitalize() if len(email_parts) > 1 else "Unknown"
                        
                        teacher = Teacher(
                            first_name=first_name,
                            last_name=last_name,
                            email=teacher_email,
                            department=row['Program Studiu']
                        )
                        self.db_session.add(teacher)
                        self.db_session.flush()  # Pentru a obține ID-ul cadrului didactic
                    
                    # Verificăm dacă disciplina există deja
                    subject = self.db_session.query(Subject).filter(
                        Subject.name == row['Nume Disciplină'],
                        Subject.group_id == group.id
                    ).first()
                    
                    if subject:
                        # Actualizăm disciplina existentă
                        subject.short_name = row['Acronim']
                        subject.study_program = row['Program Studiu']
                        subject.study_year = row['An Studiu']
                    else:
                        # Creăm o nouă disciplină
                        subject = Subject(
                            name=row['Nume Disciplină'],
                            short_name=row['Acronim'],
                            study_program=row['Program Studiu'],
                            study_year=row['An Studiu'],
                            group_id=group.id
                        )
                        self.db_session.add(subject)
                    
                    imported += 1
                except Exception as e:
                    errors += 1
                    error_details.append(f"Eroare la rândul {index + 2}: {str(e)}")
            
            self.db_session.commit()
            
            return {
                'success': True,
                'message': f"Import finalizat: {imported} discipline importate, {errors} erori",
                'imported': imported,
                'errors': errors,
                'error_details': error_details
            }
        except Exception as e:
            self.db_session.rollback()
            return {
                'success': False,
                'message': f"Eroare la importul disciplinelor: {str(e)}",
                'imported': 0,
                'errors': 1
            }
    
    def import_group_leaders_from_excel(self, file_content: BinaryIO) -> Dict[str, Any]:
        """
        Importă șefi de grupă dintr-un fișier Excel
        
        Args:
            file_content: Conținutul fișierului Excel
            
        Returns:
            Dicționar cu rezultatele importului
        """
        try:
            # Citim fișierul Excel
            df = pd.read_excel(file_content)
            
            # Verificăm coloanele necesare
            required_columns = [
                'Prenume',
                'Nume',
                'Email',
                'Grupă'
            ]
            
            for column in required_columns:
                if column not in df.columns:
                    return {
                        'success': False,
                        'message': f"Coloana '{column}' lipsește din fișier",
                        'imported': 0,
                        'errors': 0
                    }
            
            # Procesăm fiecare rând
            imported = 0
            errors = 0
            error_details = []
            
            for index, row in df.iterrows():
                try:
                    # Verificăm dacă grupa există
                    group_name = row['Grupă']
                    group = self.db_session.query(Group).filter(Group.name == group_name).first()
                    
                    if not group:
                        errors += 1
                        error_details.append(f"Eroare la rândul {index + 2}: Grupa '{group_name}' nu există")
                        continue
                    
                    # Verificăm dacă utilizatorul există deja
                    email = row['Email']
                    user = self.db_session.query(User).filter(User.email == email).first()
                    
                    if user:
                        # Actualizăm utilizatorul existent
                        user.first_name = row['Prenume']
                        user.last_name = row['Nume']
                        user.role = 'SG'  # Șef grupă
                    else:
                        # Creăm un nou utilizator
                        user = User(
                            first_name=row['Prenume'],
                            last_name=row['Nume'],
                            email=email,
                            role='SG'  # Șef grupă
                        )
                        self.db_session.add(user)
                    
                    imported += 1
                except Exception as e:
                    errors += 1
                    error_details.append(f"Eroare la rândul {index + 2}: {str(e)}")
            
            self.db_session.commit()
            
            return {
                'success': True,
                'message': f"Import finalizat: {imported} șefi de grupă importați, {errors} erori",
                'imported': imported,
                'errors': errors,
                'error_details': error_details
            }
        except Exception as e:
            self.db_session.rollback()
            return {
                'success': False,
                'message': f"Eroare la importul șefilor de grupă: {str(e)}",
                'imported': 0,
                'errors': 1
            }
    
    def download_template(self, template_id: int) -> Optional[bytes]:
        """
        Descarcă un template Excel
        
        Args:
            template_id: ID-ul template-ului
            
        Returns:
            Conținutul fișierului Excel ca bytes sau None în caz de eroare
        """
        try:
            template = self.get_template_by_id(template_id)
            
            if not template:
                return None
            
            # Verificăm dacă fișierul există
            if not os.path.exists(template.file_path):
                # Regenerăm fișierul dacă nu există
                if not self._generate_template_file(template):
                    return None
            
            # Citim conținutul fișierului
            with open(template.file_path, 'rb') as f:
                return f.read()
        except Exception as e:
            print(f"Eroare la descărcarea template-ului: {str(e)}")
            return None
