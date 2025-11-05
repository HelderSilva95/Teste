"""
Rotas de Administração - Setores, Máquinas e Utilizadores
"""
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional, List
from passlib.context import CryptContext

from config.database import get_db
from app.models import User, UserRole, Sector, Machine
from app.routes.auth import get_current_user
from utils.logger import logger, log_user_action

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def admin_required(user: User = Depends(get_current_user)):
    """Verifica se o utilizador é admin"""
    if user.role.value not in ['admin', 'gestor']:
        raise HTTPException(status_code=403, detail="Acesso negado")
    return user


# Funções auxiliares para Form handling
async def get_checkbox_value(request: Request, field_name: str) -> bool:
    """Helper para obter valor de checkbox do form"""
    form_data = await request.form()
    return field_name in form_data


async def get_multi_select_ids(request: Request, field_name: str) -> List[int]:
    """Helper para obter múltiplos IDs de checkboxes"""
    form_data = await request.form()
    values = form_data.getlist(field_name)
    return [int(v) for v in values if v.isdigit()]


# ========== PÁGINA PRINCIPAL DE ADMINISTRAÇÃO ==========

@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Painel de administração"""
    # Estatísticas
    total_users = db.query(User).count()
    total_sectors = db.query(Sector).count()
    total_machines = db.query(Machine).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    active_machines = db.query(Machine).filter(Machine.is_active == True).count()

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "user": user,
            "total_users": total_users,
            "total_sectors": total_sectors,
            "total_machines": total_machines,
            "active_users": active_users,
            "active_machines": active_machines,
        }
    )


# ========== GESTÃO DE SETORES ==========

@router.get("/sectors", response_class=HTMLResponse)
async def list_sectors(
    request: Request,
    user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Lista todos os setores"""
    sectors = db.query(Sector).order_by(Sector.name).all()
    return templates.TemplateResponse(
        "admin/sectors.html",
        {"request": request, "user": user, "sectors": sectors}
    )


@router.get("/sectors/new", response_class=HTMLResponse)
async def new_sector_form(
    request: Request,
    user: User = Depends(admin_required)
):
    """Formulário de novo setor"""
    return templates.TemplateResponse(
        "admin/sector_form.html",
        {"request": request, "user": user, "sector": None}
    )


@router.post("/sectors/new")
async def create_sector(
    request: Request,
    code: str = Form(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Cria novo setor"""
    # Verificar se código já existe
    existing = db.query(Sector).filter(Sector.code == code).first()
    if existing:
        return RedirectResponse(
            url="/admin/sectors?error=Código já existe",
            status_code=303
        )

    is_active = await get_checkbox_value(request, "is_active")

    sector = Sector(
        code=code,
        name=name,
        description=description,
        location=location,
        is_active=is_active
    )
    db.add(sector)
    db.commit()

    log_user_action(user.id, user.username, "CREATE_SECTOR", f"Setor: {code} - {name}")

    return RedirectResponse(
        url="/admin/sectors?success=Setor criado com sucesso",
        status_code=303
    )


@router.get("/sectors/{sector_id}/edit", response_class=HTMLResponse)
async def edit_sector_form(
    sector_id: int,
    request: Request,
    user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Formulário de edição de setor"""
    sector = db.query(Sector).filter(Sector.id == sector_id).first()
    if not sector:
        return RedirectResponse(url="/admin/sectors?error=Setor não encontrado", status_code=303)

    return templates.TemplateResponse(
        "admin/sector_form.html",
        {"request": request, "user": user, "sector": sector}
    )


@router.post("/sectors/{sector_id}/edit")
async def update_sector(
    request: Request,
    sector_id: int,
    code: str = Form(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Atualiza setor"""
    sector = db.query(Sector).filter(Sector.id == sector_id).first()
    if not sector:
        return RedirectResponse(url="/admin/sectors?error=Setor não encontrado", status_code=303)

    # Verificar se código já existe (exceto o próprio)
    existing = db.query(Sector).filter(
        Sector.code == code,
        Sector.id != sector_id
    ).first()
    if existing:
        return RedirectResponse(
            url=f"/admin/sectors/{sector_id}/edit?error=Código já existe",
            status_code=303
        )

    is_active = await get_checkbox_value(request, "is_active")

    sector.code = code
    sector.name = name
    sector.description = description
    sector.location = location
    sector.is_active = is_active

    db.commit()

    log_user_action(user.id, user.username, "UPDATE_SECTOR", f"Setor: {code} - {name}")

    return RedirectResponse(
        url="/admin/sectors?success=Setor atualizado com sucesso",
        status_code=303
    )


@router.post("/sectors/{sector_id}/delete")
async def delete_sector(
    sector_id: int,
    user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Elimina setor"""
    sector = db.query(Sector).filter(Sector.id == sector_id).first()
    if not sector:
        return RedirectResponse(url="/admin/sectors?error=Setor não encontrado", status_code=303)

    # Verificar se tem máquinas associadas
    if sector.machines:
        return RedirectResponse(
            url="/admin/sectors?error=Não é possível eliminar setor com máquinas associadas",
            status_code=303
        )

    log_user_action(user.id, user.username, "DELETE_SECTOR", f"Setor: {sector.code} - {sector.name}")

    db.delete(sector)
    db.commit()

    return RedirectResponse(
        url="/admin/sectors?success=Setor eliminado com sucesso",
        status_code=303
    )


# ========== GESTÃO DE MÁQUINAS ==========

@router.get("/machines", response_class=HTMLResponse)
async def list_machines(
    request: Request,
    user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Lista todas as máquinas"""
    machines = db.query(Machine).order_by(Machine.name).all()
    return templates.TemplateResponse(
        "admin/machines.html",
        {"request": request, "user": user, "machines": machines}
    )


@router.get("/machines/new", response_class=HTMLResponse)
async def new_machine_form(
    request: Request,
    user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Formulário de nova máquina"""
    sectors = db.query(Sector).filter(Sector.is_active == True).order_by(Sector.name).all()
    return templates.TemplateResponse(
        "admin/machine_form.html",
        {"request": request, "user": user, "machine": None, "sectors": sectors}
    )


@router.post("/machines/new")
async def create_machine(
    request: Request,
    code: str = Form(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    sector_id: Optional[int] = Form(None),
    user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Cria nova máquina"""
    # Verificar se código já existe
    existing = db.query(Machine).filter(Machine.code == code).first()
    if existing:
        return RedirectResponse(
            url="/admin/machines?error=Código já existe",
            status_code=303
        )

    is_active = await get_checkbox_value(request, "is_active")

    machine = Machine(
        code=code,
        name=name,
        description=description,
        location=location,
        sector_id=sector_id if sector_id else None,
        is_active=is_active
    )
    db.add(machine)
    db.commit()

    log_user_action(user.id, user.username, "CREATE_MACHINE", f"Máquina: {code} - {name}")

    return RedirectResponse(
        url="/admin/machines?success=Máquina criada com sucesso",
        status_code=303
    )


@router.get("/machines/{machine_id}/edit", response_class=HTMLResponse)
async def edit_machine_form(
    machine_id: int,
    request: Request,
    user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Formulário de edição de máquina"""
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        return RedirectResponse(url="/admin/machines?error=Máquina não encontrada", status_code=303)

    sectors = db.query(Sector).filter(Sector.is_active == True).order_by(Sector.name).all()

    return templates.TemplateResponse(
        "admin/machine_form.html",
        {"request": request, "user": user, "machine": machine, "sectors": sectors}
    )


@router.post("/machines/{machine_id}/edit")
async def update_machine(
    request: Request,
    machine_id: int,
    code: str = Form(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    sector_id: Optional[int] = Form(None),
    user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Atualiza máquina"""
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        return RedirectResponse(url="/admin/machines?error=Máquina não encontrada", status_code=303)

    # Verificar se código já existe (exceto a própria)
    existing = db.query(Machine).filter(
        Machine.code == code,
        Machine.id != machine_id
    ).first()
    if existing:
        return RedirectResponse(
            url=f"/admin/machines/{machine_id}/edit?error=Código já existe",
            status_code=303
        )

    is_active = await get_checkbox_value(request, "is_active")

    machine.code = code
    machine.name = name
    machine.description = description
    machine.location = location
    machine.sector_id = sector_id if sector_id else None
    machine.is_active = is_active

    db.commit()

    log_user_action(user.id, user.username, "UPDATE_MACHINE", f"Máquina: {code} - {name}")

    return RedirectResponse(
        url="/admin/machines?success=Máquina atualizada com sucesso",
        status_code=303
    )


@router.post("/machines/{machine_id}/delete")
async def delete_machine(
    machine_id: int,
    user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Elimina máquina"""
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        return RedirectResponse(url="/admin/machines?error=Máquina não encontrada", status_code=303)

    log_user_action(user.id, user.username, "DELETE_MACHINE", f"Máquina: {machine.code} - {machine.name}")

    db.delete(machine)
    db.commit()

    return RedirectResponse(
        url="/admin/machines?success=Máquina eliminada com sucesso",
        status_code=303
    )


# ========== GESTÃO DE UTILIZADORES ==========

@router.get("/users", response_class=HTMLResponse)
async def list_users(
    request: Request,
    user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Lista todos os utilizadores"""
    users = db.query(User).order_by(User.full_name).all()
    return templates.TemplateResponse(
        "admin/users.html",
        {"request": request, "user": user, "users": users}
    )


@router.get("/users/new", response_class=HTMLResponse)
async def new_user_form(
    request: Request,
    user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Formulário de novo utilizador"""
    sectors = db.query(Sector).filter(Sector.is_active == True).order_by(Sector.name).all()
    machines = db.query(Machine).filter(Machine.is_active == True).order_by(Machine.name).all()

    return templates.TemplateResponse(
        "admin/user_form.html",
        {
            "request": request,
            "user": user,
            "edit_user": None,
            "sectors": sectors,
            "machines": machines,
            "roles": list(UserRole)
        }
    )


@router.post("/users/new")
async def create_user(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Cria novo utilizador"""
    # Verificar se username já existe
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        return RedirectResponse(
            url="/admin/users?error=Username já existe",
            status_code=303
        )

    # Verificar se email já existe
    existing_email = db.query(User).filter(User.email == email).first()
    if existing_email:
        return RedirectResponse(
            url="/admin/users?error=Email já existe",
            status_code=303
        )

    # Obter valores de checkboxes
    is_active = await get_checkbox_value(request, "is_active")
    sector_ids = await get_multi_select_ids(request, "sector_ids")
    machine_ids = await get_multi_select_ids(request, "machine_ids")

    # Hash da password
    hashed_password = pwd_context.hash(password)

    # Criar utilizador
    new_user = User(
        username=username,
        email=email,
        full_name=full_name,
        hashed_password=hashed_password,
        role=UserRole[role.upper()],
        is_active=is_active
    )

    # Associar setores
    if sector_ids:
        sectors = db.query(Sector).filter(Sector.id.in_(sector_ids)).all()
        new_user.sectors = sectors

    # Associar máquinas
    if machine_ids:
        machines = db.query(Machine).filter(Machine.id.in_(machine_ids)).all()
        new_user.machines = machines

    db.add(new_user)
    db.commit()

    log_user_action(user.id, user.username, "CREATE_USER", f"Utilizador: {username} - {full_name}")

    return RedirectResponse(
        url="/admin/users?success=Utilizador criado com sucesso",
        status_code=303
    )


@router.get("/users/{user_id}/edit", response_class=HTMLResponse)
async def edit_user_form(
    user_id: int,
    request: Request,
    user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Formulário de edição de utilizador"""
    edit_user = db.query(User).filter(User.id == user_id).first()
    if not edit_user:
        return RedirectResponse(url="/admin/users?error=Utilizador não encontrado", status_code=303)

    sectors = db.query(Sector).filter(Sector.is_active == True).order_by(Sector.name).all()
    machines = db.query(Machine).filter(Machine.is_active == True).order_by(Machine.name).all()

    return templates.TemplateResponse(
        "admin/user_form.html",
        {
            "request": request,
            "user": user,
            "edit_user": edit_user,
            "sectors": sectors,
            "machines": machines,
            "roles": list(UserRole)
        }
    )


@router.post("/users/{user_id}/edit")
async def update_user(
    request: Request,
    user_id: int,
    username: str = Form(...),
    email: str = Form(...),
    full_name: str = Form(...),
    password: Optional[str] = Form(None),
    role: str = Form(...),
    user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Atualiza utilizador"""
    edit_user = db.query(User).filter(User.id == user_id).first()
    if not edit_user:
        return RedirectResponse(url="/admin/users?error=Utilizador não encontrado", status_code=303)

    # Verificar username
    existing = db.query(User).filter(
        User.username == username,
        User.id != user_id
    ).first()
    if existing:
        return RedirectResponse(
            url=f"/admin/users/{user_id}/edit?error=Username já existe",
            status_code=303
        )

    # Verificar email
    existing_email = db.query(User).filter(
        User.email == email,
        User.id != user_id
    ).first()
    if existing_email:
        return RedirectResponse(
            url=f"/admin/users/{user_id}/edit?error=Email já existe",
            status_code=303
        )

    # Obter valores de checkboxes
    is_active = await get_checkbox_value(request, "is_active")
    sector_ids = await get_multi_select_ids(request, "sector_ids")
    machine_ids = await get_multi_select_ids(request, "machine_ids")

    edit_user.username = username
    edit_user.email = email
    edit_user.full_name = full_name
    edit_user.role = UserRole[role.upper()]
    edit_user.is_active = is_active

    # Atualizar password se fornecida
    if password:
        edit_user.hashed_password = pwd_context.hash(password)

    # Atualizar setores
    if sector_ids:
        sectors = db.query(Sector).filter(Sector.id.in_(sector_ids)).all()
        edit_user.sectors = sectors
    else:
        edit_user.sectors = []

    # Atualizar máquinas
    if machine_ids:
        machines = db.query(Machine).filter(Machine.id.in_(machine_ids)).all()
        edit_user.machines = machines
    else:
        edit_user.machines = []

    db.commit()

    log_user_action(user.id, user.username, "UPDATE_USER", f"Utilizador: {username} - {full_name}")

    return RedirectResponse(
        url="/admin/users?success=Utilizador atualizado com sucesso",
        status_code=303
    )


@router.post("/users/{user_id}/delete")
async def delete_user(
    user_id: int,
    user: User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    """Elimina utilizador"""
    delete_user = db.query(User).filter(User.id == user_id).first()
    if not delete_user:
        return RedirectResponse(url="/admin/users?error=Utilizador não encontrado", status_code=303)

    # Não permitir eliminar o próprio utilizador
    if delete_user.id == user.id:
        return RedirectResponse(
            url="/admin/users?error=Não pode eliminar o seu próprio utilizador",
            status_code=303
        )

    log_user_action(user.id, user.username, "DELETE_USER", f"Utilizador: {delete_user.username}")

    db.delete(delete_user)
    db.commit()

    return RedirectResponse(
        url="/admin/users?success=Utilizador eliminado com sucesso",
        status_code=303
    )
