"""
Modelo de Não-Conformidades
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from config.database import Base
import enum


class NonComplianceType(enum.Enum):
    QUALITY = "quality"
    SAFETY = "safety"
    PROCESS = "process"
    EQUIPMENT = "equipment"
    MATERIAL = "material"
    OTHER = "other"


class NonComplianceSeverity(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NonComplianceStatus(enum.Enum):
    OPEN = "open"
    IN_ANALYSIS = "in_analysis"
    IN_CORRECTION = "in_correction"
    RESOLVED = "resolved"
    CLOSED = "closed"


class NonCompliance(Base):
    __tablename__ = "non_compliances"

    id = Column(Integer, primary_key=True, index=True)
    nc_number = Column(String(50), unique=True, index=True, nullable=False)

    # Tipo e Severidade
    nc_type = Column(Enum(NonComplianceType), nullable=False)
    severity = Column(Enum(NonComplianceSeverity), nullable=False)
    status = Column(Enum(NonComplianceStatus), default=NonComplianceStatus.OPEN, nullable=False)

    # Relacionamentos opcionais
    work_order_id = Column(Integer, ForeignKey("work_orders.id"))
    work_order = relationship("WorkOrder", backref="non_compliances")

    machine_id = Column(Integer, ForeignKey("machines.id"))
    machine = relationship("Machine", backref="non_compliances")

    production_log_id = Column(Integer, ForeignKey("production_logs.id"))
    production_log = relationship("ProductionLog", backref="non_compliances")

    # Reportado por
    reported_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reported_by = relationship("User", foreign_keys=[reported_by_id])

    # Responsável pela resolução
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])

    # Descrição
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    root_cause = Column(Text)
    corrective_action = Column(Text)
    preventive_action = Column(Text)

    # Datas
    occurred_at = Column(DateTime, nullable=False)
    reported_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    closed_at = Column(DateTime)

    # Custo estimado do problema
    estimated_cost = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<NonCompliance {self.nc_number} - {self.status.value}>"
