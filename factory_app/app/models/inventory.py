"""
Modelo de Inventário (Chapas e Maciços)
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, Float, Boolean
from datetime import datetime
from config.database import Base
import enum


class MaterialType(enum.Enum):
    CHAPA = "chapa"
    MACICO = "maciço"


class MaterialStatus(enum.Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    CONSUMED = "consumed"
    RESERVED = "reserved"


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    qr_code = Column(String(100), unique=True, index=True, nullable=False)
    material_type = Column(Enum(MaterialType), nullable=False)

    # Informações do material
    material_name = Column(String(100), nullable=False)  # Ex: Granito, Mármore, etc.
    color = Column(String(50))
    finish = Column(String(50))  # Polido, Amaciado, etc.

    # Dimensões
    length = Column(Float)  # Comprimento (cm)
    width = Column(Float)   # Largura (cm)
    thickness = Column(Float)  # Espessura (cm)

    # Quantidade e Unidade
    quantity = Column(Float, default=1)
    unit = Column(String(20), default="UN")

    # Localização e Status
    location = Column(String(100))  # Local físico no armazém
    status = Column(Enum(MaterialStatus), default=MaterialStatus.AVAILABLE, nullable=False)

    # Fornecedor e Lote
    supplier = Column(String(100))
    batch_number = Column(String(50))

    # Datas
    received_date = Column(DateTime)
    last_used_date = Column(DateTime)

    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<InventoryItem {self.qr_code} - {self.material_name}>"
