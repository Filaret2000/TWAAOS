from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Dict, Any

from common.models import User
from common.services import OrarIntegrationService
from fastapi_app.dependencies import get_db_session, get_current_user, get_current_active_user
from fastapi_app.schemas.schedule import TeacherResponse, GroupResponse, RoomResponse

# Creăm router-ul pentru integrarea cu Orar USV
router = APIRouter(
    prefix="/orar",
    tags=["orar"],
    responses={404: {"description": "Not found"}},
)

@router.get("/sync", response_model=Dict[str, Any])
async def sync_data(
    current_user: User = Depends(get_current_active_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Endpoint pentru sincronizarea datelor cu API-ul Orar USV
    """
    # Verificăm dacă utilizatorul are permisiunea de a sincroniza datele
    if current_user.role not in ['SEC', 'ADM']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nu aveți permisiunea de a sincroniza datele",
        )
    
    # Inițializăm serviciul de integrare cu Orar USV
    orar_service = OrarIntegrationService(
        db_session=db_session,
        api_url="https://api.orar.usv.ro"  # Va fi înlocuit cu o variabilă de mediu
    )
    
    # Sincronizăm datele
    try:
        result = orar_service.sync_all_data()
        
        # Returnăm rezultatul sincronizării
        return {
            "success": True,
            "message": "Date sincronizate cu succes",
            "stats": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Eroare la sincronizarea datelor: {str(e)}",
        )

@router.get("/teachers", response_model=List[TeacherResponse])
async def get_teachers(
    search: Optional[str] = Query(None, description="Termen de căutare pentru numele cadrului didactic"),
    current_user: User = Depends(get_current_active_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Endpoint pentru obținerea cadrelor didactice din Orar USV
    """
    # Inițializăm serviciul de integrare cu Orar USV
    orar_service = OrarIntegrationService(
        db_session=db_session,
        api_url="https://api.orar.usv.ro"  # Va fi înlocuit cu o variabilă de mediu
    )
    
    # Obținem cadrele didactice
    try:
        teachers = orar_service.get_teachers(search=search)
        
        # Returnăm lista de cadre didactice
        return teachers
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Eroare la obținerea cadrelor didactice: {str(e)}",
        )

@router.get("/groups", response_model=List[GroupResponse])
async def get_groups(
    search: Optional[str] = Query(None, description="Termen de căutare pentru numele grupei"),
    year: Optional[int] = Query(None, description="Anul de studiu"),
    specialization: Optional[str] = Query(None, description="Specializarea"),
    current_user: User = Depends(get_current_active_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Endpoint pentru obținerea grupelor din Orar USV
    """
    # Inițializăm serviciul de integrare cu Orar USV
    orar_service = OrarIntegrationService(
        db_session=db_session,
        api_url="https://api.orar.usv.ro"  # Va fi înlocuit cu o variabilă de mediu
    )
    
    # Obținem grupele
    try:
        groups = orar_service.get_groups(
            search=search,
            year=year,
            specialization=specialization
        )
        
        # Returnăm lista de grupe
        return groups
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Eroare la obținerea grupelor: {str(e)}",
        )

@router.get("/rooms", response_model=List[RoomResponse])
async def get_rooms(
    search: Optional[str] = Query(None, description="Termen de căutare pentru numele sălii"),
    building: Optional[str] = Query(None, description="Clădirea"),
    capacity: Optional[int] = Query(None, description="Capacitatea minimă"),
    current_user: User = Depends(get_current_active_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Endpoint pentru obținerea sălilor din Orar USV
    """
    # Inițializăm serviciul de integrare cu Orar USV
    orar_service = OrarIntegrationService(
        db_session=db_session,
        api_url="https://api.orar.usv.ro"  # Va fi înlocuit cu o variabilă de mediu
    )
    
    # Obținem sălile
    try:
        rooms = orar_service.get_rooms(
            search=search,
            building=building,
            capacity=capacity
        )
        
        # Returnăm lista de săli
        return rooms
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Eroare la obținerea sălilor: {str(e)}",
        )

@router.get("/subjects", response_model=List[Dict[str, Any]])
async def get_subjects(
    search: Optional[str] = Query(None, description="Termen de căutare pentru numele disciplinei"),
    teacher_id: Optional[int] = Query(None, description="ID-ul cadrului didactic"),
    current_user: User = Depends(get_current_active_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Endpoint pentru obținerea disciplinelor din Orar USV
    """
    # Inițializăm serviciul de integrare cu Orar USV
    orar_service = OrarIntegrationService(
        db_session=db_session,
        api_url="https://api.orar.usv.ro"  # Va fi înlocuit cu o variabilă de mediu
    )
    
    # Obținem disciplinele
    try:
        subjects = orar_service.get_subjects(
            search=search,
            teacher_id=teacher_id
        )
        
        # Returnăm lista de discipline
        return subjects
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Eroare la obținerea disciplinelor: {str(e)}",
        )
