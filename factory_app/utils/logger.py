"""
Sistema de Logging Estruturado
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime


# Criar diretório de logs
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


def setup_logger(name: str = "factory_app", level=logging.INFO):
    """
    Configura logger com handlers para file e console

    Args:
        name: Nome do logger
        level: Nível de logging

    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Evitar duplicação de handlers
    if logger.handlers:
        return logger

    # Formato de log
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler para arquivo (com rotação)
    file_handler = RotatingFileHandler(
        LOG_DIR / "factory_app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Logger global
logger = setup_logger()


def log_user_action(user_id: int, username: str, action: str, details: str = ""):
    """
    Registra ação de utilizador

    Args:
        user_id: ID do utilizador
        username: Nome do utilizador
        action: Ação realizada
        details: Detalhes adicionais
    """
    logger.info(
        f"USER_ACTION | User:{username}(ID:{user_id}) | Action:{action} | {details}"
    )


def log_production_event(production_id: int, event: str, details: str = ""):
    """
    Registra evento de produção

    Args:
        production_id: ID da produção
        event: Tipo de evento
        details: Detalhes
    """
    logger.info(
        f"PRODUCTION | ID:{production_id} | Event:{event} | {details}"
    )


def log_work_order_event(order_id: int, order_number: str, event: str, details: str = ""):
    """
    Registra evento de ordem de trabalho

    Args:
        order_id: ID da ordem
        order_number: Número da ordem
        event: Tipo de evento
        details: Detalhes
    """
    logger.info(
        f"WORK_ORDER | {order_number}(ID:{order_id}) | Event:{event} | {details}"
    )


def log_inventory_event(item_id: int, qr_code: str, event: str, details: str = ""):
    """
    Registra evento de inventário

    Args:
        item_id: ID do item
        qr_code: Código QR
        event: Tipo de evento
        details: Detalhes
    """
    logger.info(
        f"INVENTORY | {qr_code}(ID:{item_id}) | Event:{event} | {details}"
    )


def log_error(error: Exception, context: str = ""):
    """
    Registra erro com contexto

    Args:
        error: Exceção
        context: Contexto do erro
    """
    logger.error(
        f"ERROR | Context:{context} | Type:{type(error).__name__} | Message:{str(error)}",
        exc_info=True
    )


def log_security_event(event: str, details: str = "", level: str = "WARNING"):
    """
    Registra evento de segurança

    Args:
        event: Tipo de evento
        details: Detalhes
        level: Nível (INFO, WARNING, ERROR)
    """
    log_message = f"SECURITY | Event:{event} | {details}"

    if level == "ERROR":
        logger.error(log_message)
    elif level == "WARNING":
        logger.warning(log_message)
    else:
        logger.info(log_message)
