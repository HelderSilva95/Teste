"""
Modelo de Inventário (Chapas e Maciços)
NOTA: Alinhado com create_tables.sql
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, Float, Boolean
from datetime import datetime
from config.database import Base
import enum


class MaterialType(enum.Enum):
    CHAPA = "chapa"
    SOLIDO = "solido"
    MATERIA_PRIMA = "materia_prima"
    OUTRO = "outro"


class MaterialStatus(enum.Enum):
    DISPONIVEL = "disponivel"
    RESERVADO = "reservado"
    EM_USO = "em_uso"
    CONSUMIDO = "consumido"


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    qr_code = Column(String(100), unique=True, index=True, nullable=False)
    material_type = Column(Enum(MaterialType), nullable=False)

    # Informações do material
    material_name = Column(String(100), nullable=False)  # Ex: Granito, Mármore, etc.
    color = Column(String(50))
    dimensions = Column(String(100))  # Ex: "300x200x2cm"
    thickness = Column(Float)  # Espessura (cm)

    # Quantidade e Unidade
    quantity = Column(Float, default=1)
    unit = Column(String(10), default="UN")

    # Localização e Status
    location = Column(String(100))  # Local físico no armazém
    supplier = Column(String(100))
    entry_date = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(MaterialStatus), default=MaterialStatus.DISPONIVEL, nullable=False)

    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<InventoryItem {self.qr_code} - {self.material_name}>"
