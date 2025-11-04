@echo off
echo ============================================================
echo   FACTORY WORK TRACKING SYSTEM - Iniciando Aplicacao
echo ============================================================
echo.

REM Ativar ambiente virtual
echo [1/2] Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Iniciar aplicação
echo [2/2] Iniciando servidor...
echo.
python run.py

pause
