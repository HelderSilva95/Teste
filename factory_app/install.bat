@echo off
echo ============================================================
echo   FACTORY WORK TRACKING SYSTEM - Instalacao
echo ============================================================
echo.

REM Verificar Python
echo [1/5] Verificando Python...
python --version
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Por favor, instale Python 3.9 ou superior.
    pause
    exit /b 1
)
echo.

REM Criar ambiente virtual
echo [2/5] Criando ambiente virtual...
python -m venv venv
if errorlevel 1 (
    echo ERRO: Falha ao criar ambiente virtual!
    pause
    exit /b 1
)
echo.

REM Ativar ambiente virtual
echo [3/5] Ativando ambiente virtual...
call venv\Scripts\activate.bat
echo.

REM Instalar dependências
echo [4/5] Instalando dependencias (pode demorar alguns minutos)...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERRO: Falha ao instalar dependencias!
    pause
    exit /b 1
)
echo.

REM Informações finais
echo [5/5] Instalacao concluida!
echo.
echo ============================================================
echo   PROXIMOS PASSOS:
echo ============================================================
echo.
echo 1. Configure o arquivo .env com as credenciais do SQL Server
echo 2. Crie a base de dados no SQL Server (nome: factory_db)
echo 3. Execute: python init_database.py (para criar tabelas e dados)
echo 4. Execute: start.bat (para iniciar a aplicacao)
echo.
echo ============================================================
echo.

pause
