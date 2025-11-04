"""
Rotas de Ordens de Trabalho
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from config.database import get_db
from app.models.user import User
from app.models.work_order import WorkOrder, WorkOrderStatus
from app.models.machine import Machine
from app.routes.auth import require_auth, require_role
from utils.pagination import paginate, get_pagination_range

router = APIRouter(prefix="/work-orders", tags=["work_orders"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def list_work_orders(
    request: Request,
    status: Optional[str] = None,
    page: int = Query(1, ge=1, description="Número da página"),
    per_page: int = Query(20, ge=1, le=100, description="Itens por página"),
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Lista todas as ordens de trabalho com paginação"""
    query = db.query(WorkOrder)

    if status:
        query = query.filter(WorkOrder.status == status)

    query = query.order_by(WorkOrder.priority.asc(), WorkOrder.planned_start.asc())

    # Paginar
    paginated = paginate(query, page=page, per_page=per_page)

    # Obter range de páginas
    page_range = get_pagination_range(paginated.page, paginated.total_pages)

    return templates.TemplateResponse(
        "work_orders/list.html",
        {
            "request": request,
            "work_orders": paginated.items,
            "pagination": paginated,
            "page_range": page_range,
            "status_filter": status,
            "user": user
        }
    )


@router.get("/new", response_class=HTMLResponse)
async def new_work_order_form(
    request: Request,
    user: User = Depends(require_role(["supervisor", "gestor"])),
    db: Session = Depends(get_db)
):
    """Formulário de nova ordem de trabalho"""
    machines = db.query(Machine).filter(Machine.is_active == True).all()
    return templates.TemplateResponse(
        "work_orders/form.html",
        {"request": request, "user": user, "machines": machines}
    )


@router.post("/new")
async def create_work_order(
    order_number: str = Form(...),
    product_code: str = Form(...),
    product_description: str = Form(...),
    quantity_planned: float = Form(...),
    machine_id: int = Form(...),
    priority: int = Form(5),
    planned_start: str = Form(None),
    planned_end: str = Form(None),
    notes: str = Form(None),
    user: User = Depends(require_role(["supervisor", "gestor"])),
    db: Session = Depends(get_db)
):
    """Cria nova ordem de trabalho"""
    # Verificar se já existe
    existing = db.query(WorkOrder).filter(WorkOrder.order_number == order_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ordem de trabalho já existe")

    work_order = WorkOrder(
        order_number=order_number,
        product_code=product_code,
        product_description=product_description,
        quantity_planned=quantity_planned,
        machine_id=machine_id,
        priority=priority,
        planned_start=datetime.fromisoformat(planned_start) if planned_start else None,
        planned_end=datetime.fromisoformat(planned_end) if planned_end else None,
        notes=notes
    )

    db.add(work_order)
    db.commit()

    return RedirectResponse(url="/work-orders", status_code=303)


@router.get("/{work_order_id}", response_class=HTMLResponse)
async def view_work_order(
    request: Request,
    work_order_id: int,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Visualiza detalhes de uma ordem de trabalho"""
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()

    if not work_order:
        raise HTTPException(status_code=404, detail="Ordem de trabalho não encontrada")

    return templates.TemplateResponse(
        "work_orders/detail.html",
        {"request": request, "work_order": work_order, "user": user}
    )


@router.post("/{work_order_id}/status")
async def update_work_order_status(
    work_order_id: int,
    new_status: str = Form(...),
    user: User = Depends(require_role(["supervisor", "gestor"])),
    db: Session = Depends(get_db)
):
    """Atualiza status da ordem de trabalho"""
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()

    if not work_order:
        raise HTTPException(status_code=404, detail="Ordem de trabalho não encontrada")

    work_order.status = WorkOrderStatus(new_status)

    if new_status == "in_progress" and not work_order.actual_start:
        work_order.actual_start = datetime.utcnow()
    elif new_status == "completed" and not work_order.actual_end:
        work_order.actual_end = datetime.utcnow()

    db.commit()

    return RedirectResponse(url=f"/work-orders/{work_order_id}", status_code=303)
