"""
Modelo de Ordem de Trabalho
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from config.database import Base
import enum


class WorkOrderStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True, nullable=False)
    external_order_id = Column(String(50), index=True)  # ID da ordem no sistema externo
    product_code = Column(String(50), nullable=False)
    product_description = Column(Text)
    quantity_planned = Column(Float, nullable=False)
    quantity_produced = Column(Float, default=0)
    unit = Column(String(20), default="UN")

    machine_id = Column(Integer, ForeignKey("machines.id"))
    machine = relationship("Machine")

    status = Column(Enum(WorkOrderStatus), default=WorkOrderStatus.PENDING, nullable=False)
    priority = Column(Integer, default=5)  # 1-10, sendo 1 mais alta

    planned_start = Column(DateTime)
    planned_end = Column(DateTime)
    actual_start = Column(DateTime)
    actual_end = Column(DateTime)

    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<WorkOrder {self.order_number} - {self.status.value}>"
