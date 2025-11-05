"""
Modelo de Não-Conformidades
NOTA: Alinhado com create_tables.sql (valores em português)
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from config.database import Base
import enum


class NonComplianceType(enum.Enum):
    QUALIDADE = "qualidade"
    PROCESSO = "processo"
    MATERIAL = "material"
    EQUIPAMENTO = "equipamento"
    SEGURANCA = "seguranca"
    OUTRO = "outro"


class NonComplianceSeverity(enum.Enum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class NonComplianceStatus(enum.Enum):
    ABERTA = "aberta"
    EM_ANALISE = "em_analise"
    RESOLVIDA = "resolvida"
    FECHADA = "fechada"


class NonCompliance(Base):
    __tablename__ = "non_compliances"

    id = Column(Integer, primary_key=True, index=True)
    nc_number = Column(String(50), unique=True, index=True, nullable=False)

    # Tipo e Severidade
    nc_type = Column(Enum(NonComplianceType), nullable=False)
    severity = Column(Enum(NonComplianceSeverity), nullable=False)
    status = Column(Enum(NonComplianceStatus), default=NonComplianceStatus.ABERTA, nullable=False)

    # Descrição
    description = Column(Text, nullable=False)
    resolution = Column(Text)  # Como está no SQL

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

    # Resolvido por (alinhado com SQL)
    resolved_by_id = Column(Integer, ForeignKey("users.id"))
    resolved_by = relationship("User", foreign_keys=[resolved_by_id])

    # Datas (alinhadas com SQL)
    detected_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    resolved_date = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<NonCompliance {self.nc_number} - {self.status.value}>"
