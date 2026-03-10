from fastapi import APIRouter
from .v1.reports import router as reports_router
from .v1.claims import router as claims_router
from .v1.health import router as health_router
from .v1.auth import router as auth_router
from .ws.verification import router as ws_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(reports_router)
api_router.include_router(claims_router)
api_router.include_router(health_router)
api_router.include_router(auth_router)

# WebSocket router (no /api/v1 prefix)
ws_api_router = ws_router
