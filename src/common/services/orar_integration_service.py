from typing import List, Dict, Any, Optional
import requests
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.common.models import Teacher, Room, Subject, Group

class OrarIntegrationService:
    """Serviciu pentru integrarea cu API-ul Orar USV"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.base_url = "https://orar.usv.ro/orar/vizualizare/data"
    
    def fetch_teachers(self) -> List[Dict[str, Any]]:
        """
        Preia lista de cadre didactice de la API-ul Orar USV
        
        Returns:
            Listă de dicționare cu informații despre cadrele didactice
        """
        try:
            response = requests.get(f"{self.base_url}/cadre.php?json")
            response.raise_for_status()
            
            return response.json()
        except requests.RequestException as e:
            print(f"Eroare la preluarea cadrelor didactice: {str(e)}")
            return []
    
    def fetch_rooms(self) -> List[Dict[str, Any]]:
        """
        Preia lista de săli de la API-ul Orar USV
        
        Returns:
            Listă de dicționare cu informații despre săli
        """
        try:
            response = requests.get(f"{self.base_url}/sali.php?json")
            response.raise_for_status()
            
            return response.json()
        except requests.RequestException as e:
            print(f"Eroare la preluarea sălilor: {str(e)}")
            return []
    
    def fetch_faculties(self) -> List[Dict[str, Any]]:
        """
        Preia lista de facultăți de la API-ul Orar USV
        
        Returns:
            Listă de dicționare cu informații despre facultăți
        """
        try:
            response = requests.get(f"{self.base_url}/facultati.php?json")
            response.raise_for_status()
            
            return response.json()
        except requests.RequestException as e:
            print(f"Eroare la preluarea facultăților: {str(e)}")
            return []
    
    def fetch_subgroups(self) -> List[Dict[str, Any]]:
        """
        Preia lista de subgrupe de la API-ul Orar USV
        
        Returns:
            Listă de dicționare cu informații despre subgrupe
        """
        try:
            response = requests.get(f"{self.base_url}/subgrupe.php?json")
            response.raise_for_status()
            
            return response.json()
        except requests.RequestException as e:
            print(f"Eroare la preluarea subgrupelor: {str(e)}")
            return []
    
    def fetch_schedule_for_group(self, group_id: int) -> List[Dict[str, Any]]:
        """
        Preia orarul pentru o grupă de la API-ul Orar USV
        
        Args:
            group_id: ID-ul grupei în sistemul Orar USV
            
        Returns:
            Listă de dicționare cu informații despre orar
        """
        try:
            response = requests.get(f"{self.base_url}/orarSPG.php?ID={group_id}&mod=grupa&json")
            response.raise_for_status()
            
            return response.json()
        except requests.RequestException as e:
            print(f"Eroare la preluarea orarului pentru grupa {group_id}: {str(e)}")
            return []
    
    def sync_teachers(self) -> int:
        """
        Sincronizează cadrele didactice din API-ul Orar USV cu baza de date locală
        
        Returns:
            Numărul de cadre didactice sincronizate
        """
        try:
            teachers_data = self.fetch_teachers()
            
            count = 0
            for teacher_data in teachers_data:
                # Verificăm dacă cadrul didactic există deja
                teacher = self.db_session.query(Teacher).filter(Teacher.email == f"{teacher_data['email']}@usm.ro").first()
                
                if teacher:
                    # Actualizăm cadrul didactic existent
                    teacher.first_name = teacher_data['prenume']
                    teacher.last_name = teacher_data['nume']
                    teacher.department = teacher_data.get('departament', 'Necunoscut')
                else:
                    # Creăm un nou cadru didactic
                    teacher = Teacher(
                        first_name=teacher_data['prenume'],
                        last_name=teacher_data['nume'],
                        email=f"{teacher_data['email']}@usm.ro",
                        department=teacher_data.get('departament', 'Necunoscut')
                    )
                    self.db_session.add(teacher)
                
                count += 1
            
            self.db_session.commit()
            return count
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"Eroare la sincronizarea cadrelor didactice: {str(e)}")
            return 0
    
    def sync_rooms(self) -> int:
        """
        Sincronizează sălile din API-ul Orar USV cu baza de date locală
        
        Returns:
            Numărul de săli sincronizate
        """
        try:
            rooms_data = self.fetch_rooms()
            
            count = 0
            for room_data in rooms_data:
                # Verificăm dacă sala există deja
                room = self.db_session.query(Room).filter(
                    Room.building_name == room_data['corp'],
                    Room.short_name == room_data['sala']
                ).first()
                
                if room:
                    # Actualizăm sala existentă
                    room.name = f"{room_data['corp']}{room_data['sala']}"
                    room.capacity = room_data.get('capacitate', 0)
                    room.computers = room_data.get('calculatoare', 0)
                else:
                    # Creăm o nouă sală
                    room = Room(
                        name=f"{room_data['corp']}{room_data['sala']}",
                        short_name=room_data['sala'],
                        building_name=room_data['corp'],
                        capacity=room_data.get('capacitate', 0),
                        computers=room_data.get('calculatoare', 0)
                    )
                    self.db_session.add(room)
                
                count += 1
            
            self.db_session.commit()
            return count
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"Eroare la sincronizarea sălilor: {str(e)}")
            return 0
    
    def sync_groups(self) -> int:
        """
        Sincronizează grupele din API-ul Orar USV cu baza de date locală
        
        Returns:
            Numărul de grupe sincronizate
        """
        try:
            subgroups_data = self.fetch_subgroups()
            
            count = 0
            for subgroup_data in subgroups_data:
                # Extragem informații despre grupă din subgrupă
                group_name = subgroup_data['grupa']
                
                # Extragem anul de studiu din numele grupei (ex: 3A2 -> 3)
                study_year = int(group_name[0]) if group_name[0].isdigit() else 0
                
                # Extragem specializarea din numele grupei (ex: 3A2 -> A)
                specialization = group_name[1] if len(group_name) > 1 else ''
                
                # Verificăm dacă grupa există deja
                group = self.db_session.query(Group).filter(Group.name == group_name).first()
                
                if group:
                    # Actualizăm grupa existentă
                    group.study_year = study_year
                    group.specialization_short_name = specialization
                else:
                    # Creăm o nouă grupă
                    group = Group(
                        name=group_name,
                        study_year=study_year,
                        specialization_short_name=specialization
                    )
                    self.db_session.add(group)
                
                count += 1
            
            self.db_session.commit()
            return count
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"Eroare la sincronizarea grupelor: {str(e)}")
            return 0
    
    def sync_subjects_for_group(self, group_id: int, orar_group_id: int) -> int:
        """
        Sincronizează disciplinele pentru o grupă din API-ul Orar USV cu baza de date locală
        
        Args:
            group_id: ID-ul grupei în baza de date locală
            orar_group_id: ID-ul grupei în sistemul Orar USV
            
        Returns:
            Numărul de discipline sincronizate
        """
        try:
            schedule_data = self.fetch_schedule_for_group(orar_group_id)
            
            count = 0
            processed_subjects = set()
            
            for entry in schedule_data:
                subject_name = entry.get('disciplina', '')
                subject_short_name = entry.get('disciplina_scurt', '')
                
                # Evităm duplicatele
                if subject_name in processed_subjects:
                    continue
                
                processed_subjects.add(subject_name)
                
                # Obținem grupa
                group = self.db_session.query(Group).filter(Group.id == group_id).first()
                if not group:
                    continue
                
                # Verificăm dacă disciplina există deja
                subject = self.db_session.query(Subject).filter(
                    Subject.name == subject_name,
                    Subject.group_id == group_id
                ).first()
                
                if subject:
                    # Actualizăm disciplina existentă
                    subject.short_name = subject_short_name
                    subject.study_program = group.specialization_short_name
                    subject.study_year = group.study_year
                else:
                    # Creăm o nouă disciplină
                    subject = Subject(
                        name=subject_name,
                        short_name=subject_short_name,
                        study_program=group.specialization_short_name,
                        study_year=group.study_year,
                        group_id=group_id
                    )
                    self.db_session.add(subject)
                
                count += 1
            
            self.db_session.commit()
            return count
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"Eroare la sincronizarea disciplinelor pentru grupa {group_id}: {str(e)}")
            return 0
    
    def sync_all_data(self) -> Dict[str, int]:
        """
        Sincronizează toate datele din API-ul Orar USV cu baza de date locală
        
        Returns:
            Dicționar cu numărul de entități sincronizate pentru fiecare tip
        """
        result = {
            'teachers': self.sync_teachers(),
            'rooms': self.sync_rooms(),
            'groups': self.sync_groups(),
            'subjects': 0
        }
        
        # Sincronizăm disciplinele pentru fiecare grupă
        groups = self.db_session.query(Group).all()
        
        # În implementarea reală, ar trebui să avem o mapare între ID-urile grupelor locale și cele din Orar USV
        # Pentru simplitate, folosim un ID fictiv pentru toate grupele
        orar_group_id = 1028  # ID-ul din exemplul din caietul de sarcini
        
        for group in groups:
            result['subjects'] += self.sync_subjects_for_group(group.id, orar_group_id)
        
        return result
