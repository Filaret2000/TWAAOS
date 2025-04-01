from fastapi import APIRouter
from fastapi_app.api.auth import router as auth_router
from fastapi_app.api.schedule import router as schedule_router
from fastapi_app.api.notification import router as notification_router
from fastapi_app.api.orar import router as orar_router

# Creăm router-ul principal pentru API
api_router = APIRouter()

# Înregistrăm toate router-ele
api_router.include_router(auth_router)
api_router.include_router(schedule_router)
api_router.include_router(notification_router)
api_router.include_router(orar_router)

# Exportăm toate router-ele pentru a fi utilizate în alte module
__all__ = [
    'api_router',
    'auth_router',
    'schedule_router',
    'notification_router',
    'orar_router'
]
