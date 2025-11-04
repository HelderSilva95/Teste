"""
Script principal para iniciar a aplicação Factory Work Tracking System
"""
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from config.settings import settings


def main():
    """Função principal para iniciar o servidor"""
    print("\n" + "="*70)
    print(" FACTORY WORK TRACKING SYSTEM - Sistema de Registo de Trabalho")
    print("="*70)
    print(f"\nIniciando servidor na porta {settings.APP_PORT}...")
    print(f"Ambiente: {settings.ENVIRONMENT}")
    print(f"\nAcesse a aplicação em: http://localhost:{settings.APP_PORT}")
    print("\nPressione CTRL+C para parar o servidor")
    print("="*70 + "\n")

    # Iniciar servidor Uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level="info"
    )


if __name__ == "__main__":
    main()
