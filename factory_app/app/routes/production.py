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
from app.models.user import User, UserRole
from app.models.production_log import ProductionLog, ProductionStatus
from app.models.work_order import WorkOrder
from app.models.machine import Machine
from app.models.production_pause import ProductionPause
from app.routes.auth import require_auth
from utils.logger import log_production_event, log_user_action, log_error

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


@router.get("/my-production", response_class=HTMLResponse)
async def my_production_dashboard(
    request: Request,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Dashboard do Operador - Minhas Produções"""
    # Minhas produções ativas (onde sou operador 1 ou 2)
    my_active_productions = db.query(ProductionLog).filter(
        (ProductionLog.operator1_id == user.id) | (ProductionLog.operator2_id == user.id),
        ProductionLog.status.in_([ProductionStatus.IN_PROGRESS, ProductionStatus.PAUSED])
    ).all()

    # Minhas produções completadas hoje
    from datetime import timedelta
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    my_completed_today = db.query(ProductionLog).filter(
        (ProductionLog.operator1_id == user.id) | (ProductionLog.operator2_id == user.id),
        ProductionLog.status == ProductionStatus.COMPLETED,
        ProductionLog.end_time >= today_start
    ).all()

    # Estatísticas do dia
    total_produced = sum(p.quantity_output or 0 for p in my_completed_today)
    total_time_minutes = sum(
        int((p.end_time - p.start_time).total_seconds() / 60) - (p.pause_time or 0)
        for p in my_completed_today if p.end_time
    )

    return templates.TemplateResponse(
        "production/my_production.html",
        {
            "request": request,
            "user": user,
            "my_active_productions": my_active_productions,
            "my_completed_today": my_completed_today,
            "total_produced": total_produced,
            "total_time_minutes": total_time_minutes
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

    # Filtrar máquinas: se user tem máquinas específicas, mostrar apenas essas
    if user.machines:
        machines = user.machines
    else:
        # Se não tem restrição, mostrar todas ativas
        machines = db.query(Machine).filter(Machine.is_active == True).all()

    # Operadores: apenas ativos com role operador
    operators = db.query(User).filter(
        User.is_active == True,
        User.role.in_([UserRole.OPERADOR, UserRole.SUPERVISOR])
    ).all()

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
    try:
        # Validar Work Order
        work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if not work_order:
            log_user_action(user.id, user.username, "START_PRODUCTION_FAILED",
                          f"WorkOrder ID:{work_order_id} não encontrada")
            raise HTTPException(status_code=404, detail="Ordem de trabalho não encontrada")

        if work_order.status.value == "completed":
            raise HTTPException(status_code=400, detail="Ordem de trabalho já está completa")

        # Validar Máquina não está em uso
        existing_production = db.query(ProductionLog).filter(
            ProductionLog.machine_id == machine_id,
            ProductionLog.status.in_([ProductionStatus.IN_PROGRESS, ProductionStatus.PAUSED])
        ).first()

        if existing_production:
            raise HTTPException(
                status_code=400,
                detail=f"Máquina já está em uso na produção #{existing_production.id}"
            )

        # Validar Operadores diferentes
        if operator2_id and operator2_id == operator1_id:
            raise HTTPException(
                status_code=400,
                detail="Operador 2 deve ser diferente do Operador 1"
            )

        # Validar permissões do utilizador (se tiver máquinas associadas)
        if user.machines:  # Se user tem máquinas específicas
            machine_ids = [m.id for m in user.machines]
            if machine_id not in machine_ids:
                raise HTTPException(
                    status_code=403,
                    detail="Não tem permissão para operar esta máquina"
                )

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
        db.refresh(production_log)

        # Log sucesso
        log_production_event(production_log.id, "STARTED",
                           f"WorkOrder:{work_order.order_number}, Machine:{machine_id}, Operator:{operator1_id}")
        log_user_action(user.id, user.username, "START_PRODUCTION",
                      f"Production ID:{production_log.id} iniciada")

        return RedirectResponse(url="/production", status_code=303)

    except HTTPException:
        raise
    except Exception as e:
        log_error(e, f"start_production - User:{user.username}, WO:{work_order_id}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao iniciar produção: {str(e)}")


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

    # Criar registo de pausa
    pause = ProductionPause(
        production_log_id=production_id,
        pause_start=datetime.utcnow(),
        reason=pause_reason
    )

    production.status = ProductionStatus.PAUSED

    db.add(pause)
    db.commit()

    # Log
    log_production_event(production_id, "PAUSED", f"Motivo: {pause_reason}")
    log_user_action(user.id, user.username, "PAUSE_PRODUCTION", f"Production ID:{production_id}")

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

    # Finalizar pausa ativa (se existir)
    active_pause = db.query(ProductionPause).filter(
        ProductionPause.production_log_id == production_id,
        ProductionPause.pause_end == None
    ).first()

    if active_pause:
        active_pause.pause_end = datetime.utcnow()

    # Calcular tempo total de pausas
    total_pause_minutes = sum(p.duration_minutes for p in production.pauses)
    production.pause_time = total_pause_minutes

    production.status = ProductionStatus.IN_PROGRESS

    db.commit()

    # Log
    log_production_event(production_id, "RESUMED", f"Total pause time: {total_pause_minutes}min")
    log_user_action(user.id, user.username, "RESUME_PRODUCTION", f"Production ID:{production_id}")

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

    # Finalizar pausa ativa se existir
    active_pause = db.query(ProductionPause).filter(
        ProductionPause.production_log_id == production_id,
        ProductionPause.pause_end == None
    ).first()

    if active_pause:
        active_pause.pause_end = datetime.utcnow()

    # Calcular tempo total de pausas
    total_pause_minutes = sum(p.duration_minutes for p in production.pauses)

    production.status = ProductionStatus.COMPLETED
    production.end_time = datetime.utcnow()
    production.quantity_input = quantity_input
    production.quantity_output = quantity_output
    production.pause_time = total_pause_minutes
    if notes:
        production.notes = notes

    # Atualizar quantidade produzida na ordem de trabalho
    work_order = production.work_order
    work_order.quantity_produced += quantity_output

    # Se atingiu a quantidade planejada, marcar como completa
    wo_completed = False
    if work_order.quantity_produced >= work_order.quantity_planned:
        work_order.status = "completed"
        work_order.actual_end = datetime.utcnow()
        wo_completed = True

    db.commit()

    # Log
    details = f"Input:{quantity_input}, Output:{quantity_output}, Pause:{total_pause_minutes}min"
    if wo_completed:
        details += ", WorkOrder COMPLETED"
    log_production_event(production_id, "COMPLETED", details)
    log_user_action(user.id, user.username, "COMPLETE_PRODUCTION", f"Production ID:{production_id}")

    return RedirectResponse(url="/production", status_code=303)
