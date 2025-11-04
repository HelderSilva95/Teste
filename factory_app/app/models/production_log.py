"""
Modelo de Registro de Produção
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from config.database import Base
import enum


class ProductionStatus(enum.Enum):
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProductionLog(Base):
    __tablename__ = "production_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Relacionamentos
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)
    work_order = relationship("WorkOrder", backref="production_logs")

    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    machine = relationship("Machine")

    # Operadores (podem ser 1 ou 2)
    operator1_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    operator1 = relationship("User", foreign_keys=[operator1_id])

    operator2_id = Column(Integer, ForeignKey("users.id"))
    operator2 = relationship("User", foreign_keys=[operator2_id])

    # Tempos
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    setup_time = Column(Integer)  # Tempo de setup em minutos
    pause_time = Column(Integer, default=0)  # Tempo de pausa em minutos

    # Quantidades
    quantity_input = Column(Float)  # Quantidade de entrada
    quantity_output = Column(Float)  # Quantidade de saída
    unit = Column(String(20), default="UN")

    # Status
    status = Column(Enum(ProductionStatus), default=ProductionStatus.IN_PROGRESS, nullable=False)

    # Observações
    notes = Column(Text)
    pause_reason = Column(Text)  # Motivo da pausa

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ProductionLog {self.id} - WO:{self.work_order_id} - {self.status.value}>"
