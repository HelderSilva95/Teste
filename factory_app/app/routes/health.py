"""
Health Check Endpoint
"""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import platform

from config.database import get_db
from config.settings import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Endpoint de health check para monitorização

    Verifica:
    - Status da aplicação
    - Conexão com BD
    - Informações do sistema
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "app": {
            "name": "Factory Work Tracking System",
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT
        },
        "system": {
            "platform": platform.system(),
            "python_version": platform.python_version()
        }
    }

    # Verificar conexão BD
    try:
        db.execute(text("SELECT 1"))
        health_status["database"] = {
            "status": "connected",
            "server": settings.DB_SERVER,
            "database": settings.DB_NAME
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = {
            "status": "disconnected",
            "error": str(e)
        }
        return JSONResponse(status_code=503, content=health_status)

    return health_status


@router.get("/health/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness probe para Kubernetes/Docker
    """
    try:
        db.execute(text("SELECT 1"))
        return {"ready": True}
    except:
        return JSONResponse(status_code=503, content={"ready": False})


@router.get("/health/live")
async def liveness_check():
    """
    Liveness probe para Kubernetes/Docker
    """
    return {"alive": True}
