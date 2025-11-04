"""
Rotas de Inventário
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import io
import base64

from config.database import get_db
from app.models.user import User
from app.models.inventory import InventoryItem, MaterialType, MaterialStatus
from app.routes.auth import require_auth
from utils.qr_generator import generate_inventory_qr_code

router = APIRouter(prefix="/inventory", tags=["inventory"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def list_inventory(
    request: Request,
    material_type: Optional[str] = None,
    status: Optional[str] = None,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Lista itens do inventário"""
    query = db.query(InventoryItem).filter(InventoryItem.is_active == True)

    if material_type:
        query = query.filter(InventoryItem.material_type == material_type)

    if status:
        query = query.filter(InventoryItem.status == status)

    items = query.order_by(InventoryItem.created_at.desc()).all()

    return templates.TemplateResponse(
        "inventory/list.html",
        {"request": request, "items": items, "user": user}
    )


@router.get("/new", response_class=HTMLResponse)
async def new_inventory_form(
    request: Request,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Formulário de novo item de inventário"""
    return templates.TemplateResponse(
        "inventory/form.html",
        {"request": request, "user": user}
    )


@router.post("/new")
async def create_inventory_item(
    qr_code: str = Form(...),
    material_type: str = Form(...),
    material_name: str = Form(...),
    color: Optional[str] = Form(None),
    finish: Optional[str] = Form(None),
    length: Optional[float] = Form(None),
    width: Optional[float] = Form(None),
    thickness: Optional[float] = Form(None),
    quantity: float = Form(1),
    location: Optional[str] = Form(None),
    supplier: Optional[str] = Form(None),
    batch_number: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Cria novo item de inventário"""
    # Verificar se QR code já existe
    existing = db.query(InventoryItem).filter(InventoryItem.qr_code == qr_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="QR Code já existe")

    item = InventoryItem(
        qr_code=qr_code,
        material_type=MaterialType(material_type),
        material_name=material_name,
        color=color,
        finish=finish,
        length=length,
        width=width,
        thickness=thickness,
        quantity=quantity,
        location=location,
        supplier=supplier,
        batch_number=batch_number,
        received_date=datetime.utcnow(),
        notes=notes
    )

    db.add(item)
    db.commit()

    return RedirectResponse(url="/inventory", status_code=303)


@router.get("/{item_id}", response_class=HTMLResponse)
async def view_inventory_item(
    request: Request,
    item_id: int,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Visualiza detalhes de um item de inventário"""
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    # Gerar QR code para visualização
    qr_image = generate_inventory_qr_code(item.id, item.qr_code)

    return templates.TemplateResponse(
        "inventory/detail.html",
        {"request": request, "item": item, "qr_image": qr_image, "user": user}
    )


@router.get("/{item_id}/qr-code")
async def get_qr_code(
    item_id: int,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Retorna o QR code de um item"""
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    qr_image_base64 = generate_inventory_qr_code(item.id, item.qr_code)
    qr_image_bytes = base64.b64decode(qr_image_base64)

    return Response(content=qr_image_bytes, media_type="image/png")


@router.post("/{item_id}/update-status")
async def update_item_status(
    item_id: int,
    new_status: str = Form(...),
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Atualiza status de um item"""
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    item.status = MaterialStatus(new_status)

    if new_status == "in_use":
        item.last_used_date = datetime.utcnow()

    db.commit()

    return RedirectResponse(url=f"/inventory/{item_id}", status_code=303)


@router.get("/search/qr", response_class=HTMLResponse)
async def search_by_qr(
    request: Request,
    qr: str,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Busca item por QR code"""
    # Extrair código do QR (formato: INV-{id}-{qr_code})
    if qr.startswith("INV-"):
        parts = qr.split("-")
        if len(parts) >= 3:
            qr_code = "-".join(parts[2:])
            item = db.query(InventoryItem).filter(InventoryItem.qr_code == qr_code).first()

            if item:
                return RedirectResponse(url=f"/inventory/{item.id}", status_code=303)

    raise HTTPException(status_code=404, detail="Item não encontrado")
