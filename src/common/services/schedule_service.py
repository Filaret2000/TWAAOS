from typing import List, Optional, Dict, Any, Tuple
from datetime import date, time
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, func

from src.common.models import Schedule, Subject, Teacher, Room, Group, User, Notification

class ScheduleService:
    """Serviciu pentru gestionarea planificărilor examenelor"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def get_schedules(self, 
                      group_id: Optional[int] = None, 
                      teacher_id: Optional[int] = None, 
                      subject_id: Optional[int] = None, 
                      status: Optional[str] = None,
                      start_date: Optional[date] = None,
                      end_date: Optional[date] = None) -> List[Schedule]:
        """
        Obține planificările examenelor cu filtrare opțională
        
        Args:
            group_id: ID-ul grupei (opțional)
            teacher_id: ID-ul cadrului didactic (opțional)
            subject_id: ID-ul disciplinei (opțional)
            status: Statusul planificării (opțional)
            start_date: Data de început pentru filtrare (opțional)
            end_date: Data de sfârșit pentru filtrare (opțional)
            
        Returns:
            Listă de obiecte Schedule
        """
        try:
            query = self.db_session.query(Schedule)
            
            if group_id:
                query = query.filter(Schedule.group_id == group_id)
            
            if teacher_id:
                query = query.filter(or_(
                    Schedule.teacher_id == teacher_id,
                    Schedule.assistants.any(Teacher.id == teacher_id)
                ))
            
            if subject_id:
                query = query.filter(Schedule.subject_id == subject_id)
            
            if status:
                query = query.filter(Schedule.status == status)
            
            if start_date:
                query = query.filter(Schedule.date >= start_date)
            
            if end_date:
                query = query.filter(Schedule.date <= end_date)
            
            return query.all()
        except SQLAlchemyError as e:
            print(f"Eroare la obținerea planificărilor: {str(e)}")
            return []
    
    def get_schedule_by_id(self, schedule_id: int) -> Optional[Schedule]:
        """
        Obține o planificare după ID
        
        Args:
            schedule_id: ID-ul planificării
            
        Returns:
            Obiectul Schedule sau None dacă planificarea nu există
        """
        try:
            return self.db_session.query(Schedule).filter(Schedule.id == schedule_id).first()
        except SQLAlchemyError as e:
            print(f"Eroare la obținerea planificării după ID: {str(e)}")
            return None
    
    def propose_schedule(self, subject_id: int, group_id: int, teacher_id: int, exam_date: date) -> Optional[Schedule]:
        """
        Propune o nouă planificare de examen
        
        Args:
            subject_id: ID-ul disciplinei
            group_id: ID-ul grupei
            teacher_id: ID-ul cadrului didactic titular
            exam_date: Data propusă pentru examen
            
        Returns:
            Obiectul Schedule creat sau None în caz de eroare
        """
        try:
            # Verificăm dacă există deja o planificare pentru această disciplină și grupă
            existing_schedule = self.db_session.query(Schedule).filter(
                Schedule.subject_id == subject_id,
                Schedule.group_id == group_id
            ).first()
            
            if existing_schedule:
                # Actualizăm planificarea existentă
                existing_schedule.date = exam_date
                existing_schedule.status = 'proposed'
                self.db_session.commit()
                return existing_schedule
            
            # Creăm o nouă planificare
            schedule = Schedule(
                subject_id=subject_id,
                group_id=group_id,
                teacher_id=teacher_id,
                date=exam_date,
                status='proposed'
            )
            
            self.db_session.add(schedule)
            self.db_session.commit()
            
            # Obținem informații despre disciplină și grupă pentru notificare
            subject = self.db_session.query(Subject).filter(Subject.id == subject_id).first()
            group = self.db_session.query(Group).filter(Group.id == group_id).first()
            
            # Trimitem notificare cadrului didactic
            teacher = self.db_session.query(Teacher).filter(Teacher.id == teacher_id).first()
            if teacher:
                user = self.db_session.query(User).filter(User.email == teacher.email).first()
                if user:
                    notification = Notification(
                        user_id=user.id,
                        message=f"O nouă propunere de examen pentru disciplina {subject.name} a fost făcută de grupa {group.name} pentru data {exam_date}."
                    )
                    self.db_session.add(notification)
                    self.db_session.commit()
            
            return schedule
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"Eroare la propunerea planificării: {str(e)}")
            return None
    
    def update_schedule_status(self, schedule_id: int, status: str, message: Optional[str] = None) -> Optional[Schedule]:
        """
        Actualizează statusul unei planificări (aprobă/respinge)
        
        Args:
            schedule_id: ID-ul planificării
            status: Noul status ('approved' sau 'rejected')
            message: Mesaj opțional (pentru respingere)
            
        Returns:
            Obiectul Schedule actualizat sau None în caz de eroare
        """
        try:
            schedule = self.db_session.query(Schedule).filter(Schedule.id == schedule_id).first()
            
            if not schedule:
                return None
            
            schedule.status = status
            self.db_session.commit()
            
            # Obținem informații pentru notificare
            subject = self.db_session.query(Subject).filter(Subject.id == schedule.subject_id).first()
            group = self.db_session.query(Group).filter(Group.id == schedule.group_id).first()
            
            # Găsim șeful de grupă pentru a trimite notificare
            group_leader = self.db_session.query(User).filter(
                User.role == 'SG',
                User.email.like(f"%@student.usv.ro")  # Presupunem că șefii de grupă au email-uri de student
            ).first()
            
            if group_leader:
                notification_message = f"Propunerea de examen pentru disciplina {subject.name} a fost "
                
                if status == 'approved':
                    notification_message += "aprobată."
                else:
                    notification_message += f"respinsă. {message if message else ''}"
                
                notification = Notification(
                    user_id=group_leader.id,
                    message=notification_message
                )
                self.db_session.add(notification)
                self.db_session.commit()
            
            return schedule
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"Eroare la actualizarea statusului planificării: {str(e)}")
            return None
    
    def set_schedule_details(self, schedule_id: int, room_id: int, start_time: time, end_time: time, assistant_ids: List[int]) -> Optional[Schedule]:
        """
        Setează detaliile unei planificări aprobate (sală, oră, asistenți)
        
        Args:
            schedule_id: ID-ul planificării
            room_id: ID-ul sălii
            start_time: Ora de început
            end_time: Ora de sfârșit
            assistant_ids: Lista de ID-uri ale asistenților
            
        Returns:
            Obiectul Schedule actualizat sau None în caz de eroare
        """
        try:
            schedule = self.db_session.query(Schedule).filter(Schedule.id == schedule_id).first()
            
            if not schedule or schedule.status != 'approved':
                return None
            
            # Verificăm dacă există conflicte de sală
            room_conflicts = self.db_session.query(Schedule).filter(
                Schedule.room_id == room_id,
                Schedule.date == schedule.date,
                Schedule.id != schedule_id,
                or_(
                    and_(Schedule.start_time <= start_time, Schedule.end_time > start_time),
                    and_(Schedule.start_time < end_time, Schedule.end_time >= end_time),
                    and_(Schedule.start_time >= start_time, Schedule.end_time <= end_time)
                )
            ).all()
            
            if room_conflicts:
                print("Conflict de sală detectat")
                return None
            
            # Verificăm dacă există conflicte pentru profesori și asistenți
            teacher_conflicts = self.db_session.query(Schedule).filter(
                Schedule.teacher_id == schedule.teacher_id,
                Schedule.date == schedule.date,
                Schedule.id != schedule_id,
                or_(
                    and_(Schedule.start_time <= start_time, Schedule.end_time > start_time),
                    and_(Schedule.start_time < end_time, Schedule.end_time >= end_time),
                    and_(Schedule.start_time >= start_time, Schedule.end_time <= end_time)
                )
            ).all()
            
            if teacher_conflicts:
                print("Conflict de profesor detectat")
                return None
            
            # Actualizăm planificarea
            schedule.room_id = room_id
            schedule.start_time = start_time
            schedule.end_time = end_time
            
            # Actualizăm asistenții
            assistants = self.db_session.query(Teacher).filter(Teacher.id.in_(assistant_ids)).all()
            schedule.assistants = assistants
            
            self.db_session.commit()
            
            return schedule
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"Eroare la setarea detaliilor planificării: {str(e)}")
            return None
    
    def check_conflicts(self, date_val: Optional[date] = None, teacher_id: Optional[int] = None, room_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Verifică conflictele de planificare
        
        Args:
            date_val: Data pentru care se verifică conflictele (opțional)
            teacher_id: ID-ul cadrului didactic pentru care se verifică conflictele (opțional)
            room_id: ID-ul sălii pentru care se verifică conflictele (opțional)
            
        Returns:
            Listă de dicționare cu informații despre conflicte
        """
        conflicts = []
        
        try:
            # Obținem toate planificările pentru data specificată
            query = self.db_session.query(Schedule)
            
            if date_val:
                query = query.filter(Schedule.date == date_val)
            
            schedules = query.all()
            
            # Verificăm conflicte de sală
            if room_id:
                room_schedules = [s for s in schedules if s.room_id == room_id]
                
                for i in range(len(room_schedules)):
                    for j in range(i + 1, len(room_schedules)):
                        s1 = room_schedules[i]
                        s2 = room_schedules[j]
                        
                        # Verificăm dacă există suprapunere de timp
                        if (s1.start_time and s1.end_time and s2.start_time and s2.end_time and
                            ((s1.start_time <= s2.start_time and s1.end_time > s2.start_time) or
                             (s1.start_time < s2.end_time and s1.end_time >= s2.end_time) or
                             (s1.start_time >= s2.start_time and s1.end_time <= s2.end_time))):
                            
                            room = self.db_session.query(Room).filter(Room.id == room_id).first()
                            
                            conflicts.append({
                                'type': 'room_conflict',
                                'schedule_id1': s1.id,
                                'schedule_id2': s2.id,
                                'room_id': room_id,
                                'room_name': room.name if room else 'Unknown',
                                'date': s1.date,
                                'time_range1': f"{s1.start_time}-{s1.end_time}",
                                'time_range2': f"{s2.start_time}-{s2.end_time}"
                            })
            
            # Verificăm conflicte de profesor
            if teacher_id:
                teacher_schedules = [s for s in schedules if s.teacher_id == teacher_id or teacher_id in [a.id for a in s.assistants]]
                
                for i in range(len(teacher_schedules)):
                    for j in range(i + 1, len(teacher_schedules)):
                        s1 = teacher_schedules[i]
                        s2 = teacher_schedules[j]
                        
                        # Verificăm dacă există suprapunere de timp
                        if (s1.start_time and s1.end_time and s2.start_time and s2.end_time and
                            ((s1.start_time <= s2.start_time and s1.end_time > s2.start_time) or
                             (s1.start_time < s2.end_time and s1.end_time >= s2.end_time) or
                             (s1.start_time >= s2.start_time and s1.end_time <= s2.end_time))):
                            
                            teacher = self.db_session.query(Teacher).filter(Teacher.id == teacher_id).first()
                            
                            conflicts.append({
                                'type': 'teacher_conflict',
                                'schedule_id1': s1.id,
                                'schedule_id2': s2.id,
                                'teacher_id': teacher_id,
                                'teacher_name': teacher.full_name if teacher else 'Unknown',
                                'date': s1.date,
                                'time_range1': f"{s1.start_time}-{s1.end_time}",
                                'time_range2': f"{s2.start_time}-{s2.end_time}"
                            })
            
            return conflicts
        except SQLAlchemyError as e:
            print(f"Eroare la verificarea conflictelor: {str(e)}")
            return []
