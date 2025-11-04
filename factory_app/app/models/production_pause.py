"""
Modelo de Pausas de Produção
"""
from sqlalchemy import Column, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from config.database import Base


class ProductionPause(Base):
    __tablename__ = "production_pauses"

    id = Column(Integer, primary_key=True, index=True)

    # Relacionamento com produção
    production_log_id = Column(Integer, ForeignKey("production_logs.id"), nullable=False)
    production_log = relationship("ProductionLog", backref="pauses")

    # Tempos de pausa
    pause_start = Column(DateTime, nullable=False, default=datetime.utcnow)
    pause_end = Column(DateTime)

    # Motivo
    reason = Column(Text, nullable=False)

    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ProductionPause {self.id} - Production:{self.production_log_id}>"

    @property
    def duration_minutes(self):
        """Retorna duração da pausa em minutos"""
        if not self.pause_end:
            # Pausa ainda ativa
            duration = datetime.utcnow() - self.pause_start
        else:
            duration = self.pause_end - self.pause_start

        return int(duration.total_seconds() / 60)
