"""
Utilit ário de Paginação
"""
from typing import TypeVar, Generic, List
from pydantic import BaseModel
from sqlalchemy.orm import Query

T = TypeVar('T')


class Page(BaseModel, Generic[T]):
    """Modelo de página paginada"""
    items: List[T]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool

    class Config:
        arbitrary_types_allowed = True


def paginate(query: Query, page: int = 1, per_page: int = 20) -> Page:
    """
    Pagina uma query do SQLAlchemy

    Args:
        query: Query do SQLAlchemy
        page: Número da página (começa em 1)
        per_page: Itens por página

    Returns:
        Page object com itens e metadados
    """
    # Garantir valores mínimos
    page = max(1, page)
    per_page = min(max(1, per_page), 100)  # Máximo 100 itens por página

    # Total de itens
    total = query.count()

    # Total de páginas
    total_pages = (total + per_page - 1) // per_page
    total_pages = max(1, total_pages)

    # Ajustar página se for maior que total
    page = min(page, total_pages)

    # Obter itens
    offset = (page - 1) * per_page
    items = query.limit(per_page).offset(offset).all()

    return Page(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )


def get_pagination_range(current_page: int, total_pages: int, max_pages: int = 5) -> List[int]:
    """
    Retorna lista de números de página para mostrar

    Args:
        current_page: Página atual
        total_pages: Total de páginas
        max_pages: Máximo de páginas a mostrar

    Returns:
        Lista de números de página
    """
    if total_pages <= max_pages:
        return list(range(1, total_pages + 1))

    # Centralizar página atual
    start = max(1, current_page - max_pages // 2)
    end = min(total_pages + 1, start + max_pages)

    # Ajustar se chegou no fim
    if end == total_pages + 1:
        start = max(1, end - max_pages)

    return list(range(start, end))
