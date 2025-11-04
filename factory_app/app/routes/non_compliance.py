"""
Rotas de Não-Conformidades
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from config.database import get_db
from app.models.user import User
from app.models.non_compliance import NonCompliance, NonComplianceType, NonComplianceSeverity, NonComplianceStatus
from app.models.work_order import WorkOrder
from app.models.machine import Machine
from app.routes.auth import require_auth

router = APIRouter(prefix="/non-compliance", tags=["non_compliance"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def list_non_compliances(
    request: Request,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Lista não-conformidades"""
    query = db.query(NonCompliance)

    if status:
        query = query.filter(NonCompliance.status == status)

    if severity:
        query = query.filter(NonCompliance.severity == severity)

    non_compliances = query.order_by(
        NonCompliance.severity.desc(),
        NonCompliance.reported_at.desc()
    ).all()

    return templates.TemplateResponse(
        "non_compliance/list.html",
        {"request": request, "non_compliances": non_compliances, "user": user}
    )


@router.get("/new", response_class=HTMLResponse)
async def new_non_compliance_form(
    request: Request,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Formulário de nova não-conformidade"""
    work_orders = db.query(WorkOrder).all()
    machines = db.query(Machine).all()
    users_list = db.query(User).filter(User.is_active == True).all()

    return templates.TemplateResponse(
        "non_compliance/form.html",
        {
            "request": request,
            "user": user,
            "work_orders": work_orders,
            "machines": machines,
            "users": users_list
        }
    )


@router.post("/new")
async def create_non_compliance(
    nc_type: str = Form(...),
    severity: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    occurred_at: str = Form(...),
    work_order_id: Optional[int] = Form(None),
    machine_id: Optional[int] = Form(None),
    assigned_to_id: Optional[int] = Form(None),
    estimated_cost: Optional[int] = Form(None),
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Cria nova não-conformidade"""
    # Gerar número da NC
    last_nc = db.query(NonCompliance).order_by(NonCompliance.id.desc()).first()
    nc_number = f"NC-{datetime.utcnow().year}-{(last_nc.id + 1 if last_nc else 1):04d}"

    non_compliance = NonCompliance(
        nc_number=nc_number,
        nc_type=NonComplianceType(nc_type),
        severity=NonComplianceSeverity(severity),
        title=title,
        description=description,
        occurred_at=datetime.fromisoformat(occurred_at),
        work_order_id=work_order_id if work_order_id else None,
        machine_id=machine_id if machine_id else None,
        reported_by_id=user.id,
        assigned_to_id=assigned_to_id if assigned_to_id else None,
        estimated_cost=estimated_cost
    )

    db.add(non_compliance)
    db.commit()

    return RedirectResponse(url="/non-compliance", status_code=303)


@router.get("/{nc_id}", response_class=HTMLResponse)
async def view_non_compliance(
    request: Request,
    nc_id: int,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Visualiza detalhes de uma não-conformidade"""
    nc = db.query(NonCompliance).filter(NonCompliance.id == nc_id).first()

    if not nc:
        raise HTTPException(status_code=404, detail="Não-conformidade não encontrada")

    users_list = db.query(User).filter(User.is_active == True).all()

    return templates.TemplateResponse(
        "non_compliance/detail.html",
        {"request": request, "nc": nc, "user": user, "users": users_list}
    )


@router.post("/{nc_id}/update")
async def update_non_compliance(
    nc_id: int,
    status: Optional[str] = Form(None),
    root_cause: Optional[str] = Form(None),
    corrective_action: Optional[str] = Form(None),
    preventive_action: Optional[str] = Form(None),
    assigned_to_id: Optional[int] = Form(None),
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Atualiza não-conformidade"""
    nc = db.query(NonCompliance).filter(NonCompliance.id == nc_id).first()

    if not nc:
        raise HTTPException(status_code=404, detail="Não-conformidade não encontrada")

    if status:
        nc.status = NonComplianceStatus(status)

        if status == "resolved" and not nc.resolved_at:
            nc.resolved_at = datetime.utcnow()
        elif status == "closed" and not nc.closed_at:
            nc.closed_at = datetime.utcnow()

    if root_cause:
        nc.root_cause = root_cause

    if corrective_action:
        nc.corrective_action = corrective_action

    if preventive_action:
        nc.preventive_action = preventive_action

    if assigned_to_id:
        nc.assigned_to_id = assigned_to_id

    db.commit()

    return RedirectResponse(url=f"/non-compliance/{nc_id}", status_code=303)
