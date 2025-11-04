"""
Modelo de Consumo de Materiais
"""
from sqlalchemy import Column, Integer, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from config.database import Base


class MaterialConsumption(Base):
    __tablename__ = "material_consumptions"

    id = Column(Integer, primary_key=True, index=True)

    # Relacionamentos
    production_log_id = Column(Integer, ForeignKey("production_logs.id"), nullable=False)
    production_log = relationship("ProductionLog", backref="material_consumptions")

    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    inventory_item = relationship("InventoryItem", backref="consumptions")

    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)
    work_order = relationship("WorkOrder", backref="material_consumptions")

    # Quantidade consumida
    quantity_consumed = Column(Float, nullable=False)

    # Data e notas
    consumed_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<MaterialConsumption {self.id} - Item:{self.inventory_item_id}>"
