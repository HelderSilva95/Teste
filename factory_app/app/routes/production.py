"""
Rotas de Produção
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from config.database import get_db
from app.models.user import User
from app.models.production_log import ProductionLog, ProductionStatus
from app.models.work_order import WorkOrder
from app.models.machine import Machine
from app.routes.auth import require_auth

router = APIRouter(prefix="/production", tags=["production"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def production_dashboard(
    request: Request,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Dashboard de produção"""
    # Produções ativas
    active_productions = db.query(ProductionLog).filter(
        ProductionLog.status.in_([ProductionStatus.IN_PROGRESS, ProductionStatus.PAUSED])
    ).all()

    # Ordens de trabalho pendentes
    pending_orders = db.query(WorkOrder).filter(
        WorkOrder.status == "pending"
    ).order_by(WorkOrder.priority.asc()).all()

    return templates.TemplateResponse(
        "production/dashboard.html",
        {
            "request": request,
            "user": user,
            "active_productions": active_productions,
            "pending_orders": pending_orders
        }
    )


@router.get("/start", response_class=HTMLResponse)
async def start_production_form(
    request: Request,
    work_order_id: Optional[int] = None,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Formulário para iniciar produção"""
    work_orders = db.query(WorkOrder).filter(
        WorkOrder.status.in_(["pending", "in_progress"])
    ).all()

    machines = db.query(Machine).filter(Machine.is_active == True).all()
    operators = db.query(User).filter(User.is_active == True).all()

    selected_order = None
    if work_order_id:
        selected_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()

    return templates.TemplateResponse(
        "production/start.html",
        {
            "request": request,
            "user": user,
            "work_orders": work_orders,
            "machines": machines,
            "operators": operators,
            "selected_order": selected_order
        }
    )


@router.post("/start")
async def start_production(
    work_order_id: int = Form(...),
    machine_id: int = Form(...),
    operator1_id: int = Form(...),
    operator2_id: Optional[int] = Form(None),
    setup_time: Optional[int] = Form(None),
    notes: Optional[str] = Form(None),
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Inicia uma produção"""
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not work_order:
        raise HTTPException(status_code=404, detail="Ordem de trabalho não encontrada")

    production_log = ProductionLog(
        work_order_id=work_order_id,
        machine_id=machine_id,
        operator1_id=operator1_id,
        operator2_id=operator2_id if operator2_id else None,
        start_time=datetime.utcnow(),
        setup_time=setup_time,
        status=ProductionStatus.IN_PROGRESS,
        notes=notes
    )

    # Atualizar status da ordem de trabalho
    if work_order.status.value == "pending":
        work_order.status = "in_progress"
        work_order.actual_start = datetime.utcnow()

    db.add(production_log)
    db.commit()

    return RedirectResponse(url="/production", status_code=303)


@router.get("/{production_id}", response_class=HTMLResponse)
async def view_production(
    request: Request,
    production_id: int,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Visualiza detalhes de uma produção"""
    production = db.query(ProductionLog).filter(ProductionLog.id == production_id).first()

    if not production:
        raise HTTPException(status_code=404, detail="Produção não encontrada")

    return templates.TemplateResponse(
        "production/detail.html",
        {"request": request, "production": production, "user": user}
    )


@router.post("/{production_id}/pause")
async def pause_production(
    production_id: int,
    pause_reason: str = Form(...),
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Pausa uma produção"""
    production = db.query(ProductionLog).filter(ProductionLog.id == production_id).first()

    if not production:
        raise HTTPException(status_code=404, detail="Produção não encontrada")

    production.status = ProductionStatus.PAUSED
    production.pause_reason = pause_reason

    db.commit()

    return RedirectResponse(url="/production", status_code=303)


@router.post("/{production_id}/resume")
async def resume_production(
    production_id: int,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Retoma uma produção pausada"""
    production = db.query(ProductionLog).filter(ProductionLog.id == production_id).first()

    if not production:
        raise HTTPException(status_code=404, detail="Produção não encontrada")

    production.status = ProductionStatus.IN_PROGRESS

    db.commit()

    return RedirectResponse(url="/production", status_code=303)


@router.post("/{production_id}/complete")
async def complete_production(
    production_id: int,
    quantity_input: float = Form(...),
    quantity_output: float = Form(...),
    notes: Optional[str] = Form(None),
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Completa uma produção"""
    production = db.query(ProductionLog).filter(ProductionLog.id == production_id).first()

    if not production:
        raise HTTPException(status_code=404, detail="Produção não encontrada")

    production.status = ProductionStatus.COMPLETED
    production.end_time = datetime.utcnow()
    production.quantity_input = quantity_input
    production.quantity_output = quantity_output
    if notes:
        production.notes = notes

    # Atualizar quantidade produzida na ordem de trabalho
    work_order = production.work_order
    work_order.quantity_produced += quantity_output

    # Se atingiu a quantidade planejada, marcar como completa
    if work_order.quantity_produced >= work_order.quantity_planned:
        work_order.status = "completed"
        work_order.actual_end = datetime.utcnow()

    db.commit()

    return RedirectResponse(url="/production", status_code=303)
