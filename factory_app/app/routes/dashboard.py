"""
Rotas de Dashboard
"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func

from config.database import get_db
from app.models.user import User
from app.models.work_order import WorkOrder
from app.models.production_log import ProductionLog, ProductionStatus
from app.models.inventory import InventoryItem, MaterialStatus
from app.models.non_compliance import NonCompliance, NonComplianceStatus
from app.routes.auth import require_auth

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Redireciona para login ou dashboard"""
    from app.routes.auth import get_current_user

    user = get_current_user(request, next(get_db()))
    if user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/dashboard")

    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/auth/login")


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Dashboard principal"""
    # Estatísticas gerais
    stats = {
        "work_orders_pending": db.query(WorkOrder).filter(
            WorkOrder.status == "pending"
        ).count(),
        "work_orders_in_progress": db.query(WorkOrder).filter(
            WorkOrder.status == "in_progress"
        ).count(),
        "productions_active": db.query(ProductionLog).filter(
            ProductionLog.status.in_([ProductionStatus.IN_PROGRESS, ProductionStatus.PAUSED])
        ).count(),
        "inventory_available": db.query(InventoryItem).filter(
            InventoryItem.status == MaterialStatus.AVAILABLE,
            InventoryItem.is_active == True
        ).count(),
        "nc_open": db.query(NonCompliance).filter(
            NonCompliance.status.in_([NonComplianceStatus.OPEN, NonComplianceStatus.IN_ANALYSIS])
        ).count(),
    }

    # Produções ativas
    active_productions = db.query(ProductionLog).filter(
        ProductionLog.status == ProductionStatus.IN_PROGRESS
    ).limit(5).all()

    # Ordens de trabalho prioritárias
    priority_orders = db.query(WorkOrder).filter(
        WorkOrder.status.in_(["pending", "in_progress"])
    ).order_by(WorkOrder.priority.asc()).limit(5).all()

    # Não-conformidades recentes
    recent_ncs = db.query(NonCompliance).filter(
        NonCompliance.status != NonComplianceStatus.CLOSED
    ).order_by(NonCompliance.reported_at.desc()).limit(5).all()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "stats": stats,
            "active_productions": active_productions,
            "priority_orders": priority_orders,
            "recent_ncs": recent_ncs
        }
    )
