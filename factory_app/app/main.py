"""
Aplicação principal FastAPI
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from config.database import init_db
from app.routes import auth, dashboard, work_orders, production, inventory, non_compliance, health, sql_import, admin
from utils.logger import logger

# Criar aplicação FastAPI
app = FastAPI(
    title="Factory Work Tracking System",
    description="Sistema de Registo de Trabalho e Produção",
    version="1.0.0"
)

# Montar arquivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Incluir rotas
app.include_router(health.router)
app.include_router(dashboard.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(work_orders.router)
app.include_router(production.router)
app.include_router(inventory.router)
app.include_router(non_compliance.router)
app.include_router(sql_import.router)


@app.on_event("startup")
async def startup_event():
    """Evento de inicialização"""
    print("Inicializando banco de dados...")
    init_db()
    print("Banco de dados inicializado!")
    print("\n" + "="*60)
    print("Sistema de Registo de Trabalho - Factory")
    print("="*60)
    print("Aplicação iniciada com sucesso!")
    print("Acesse: http://localhost:8080")
    print("="*60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Evento de encerramento"""
    print("\nEncerrando aplicação...")


# Handler de erro 404
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handler para páginas não encontradas"""
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "error": "Página não encontrada", "code": 404},
        status_code=404
    )


# Handler de erro 500
@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    """Handler para erros do servidor"""
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "error": "Erro interno do servidor", "code": 500},
        status_code=500
    )
