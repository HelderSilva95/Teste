"""
Rotas para importação de dados de SQL externo
"""
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from config.database import get_db
from app.models import User
from app.routes.auth import get_current_user
from utils.sql_import import ExternalSQLImporter, sync_work_orders_from_external
from utils.logger import logger, log_user_action

router = APIRouter(prefix="/import", tags=["import"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def import_page(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Página de importação de dados"""
    # Apenas admin e supervisor podem acessar
    if user.role.value not in ['admin', 'supervisor']:
        return RedirectResponse(url="/dashboard", status_code=303)

    # Testar conexão com SQL externo
    importer = ExternalSQLImporter()
    connection_ok = importer.test_connection()

    return templates.TemplateResponse(
        "import/index.html",
        {
            "request": request,
            "user": user,
            "connection_ok": connection_ok,
            "external_server": importer.server or "Não configurado"
        }
    )


@router.post("/work-orders")
async def import_work_orders(
    days_back: int = Form(7),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Importa ordens de trabalho do SQL externo"""
    # Apenas admin e supervisor
    if user.role.value not in ['admin', 'supervisor']:
        return RedirectResponse(url="/dashboard", status_code=303)

    try:
        count = sync_work_orders_from_external(db, days_back=days_back)

        log_user_action(
            user.id,
            user.username,
            "IMPORT_WORK_ORDERS",
            f"Importadas {count} ordens de trabalho ({days_back} dias)"
        )

        return RedirectResponse(
            url=f"/import?success=Importadas {count} ordens de trabalho",
            status_code=303
        )

    except Exception as e:
        logger.error(f"Erro ao importar ordens: {e}")
        return RedirectResponse(
            url=f"/import?error=Erro ao importar: {str(e)}",
            status_code=303
        )


@router.post("/test-connection")
async def test_connection(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Testa conexão com SQL externo"""
    # Apenas admin e supervisor
    if user.role.value not in ['admin', 'supervisor']:
        return RedirectResponse(url="/dashboard", status_code=303)

    importer = ExternalSQLImporter()
    success = importer.test_connection()

    if success:
        return RedirectResponse(
            url="/import?success=Conexão estabelecida com sucesso",
            status_code=303
        )
    else:
        return RedirectResponse(
            url="/import?error=Falha ao conectar. Verificar configuração no .env",
            status_code=303
        )
