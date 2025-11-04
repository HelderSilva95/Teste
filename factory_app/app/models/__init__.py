"""
Modelos da aplicação
"""
from app.models.user import User, UserRole
from app.models.machine import Machine
from app.models.work_order import WorkOrder, WorkOrderStatus
from app.models.inventory import InventoryItem, MaterialType, MaterialStatus
from app.models.production_log import ProductionLog, ProductionStatus
from app.models.production_pause import ProductionPause
from app.models.material_consumption import MaterialConsumption
from app.models.non_compliance import (
    NonCompliance,
    NonComplianceType,
    NonComplianceSeverity,
    NonComplianceStatus
)

__all__ = [
    "User",
    "UserRole",
    "Machine",
    "WorkOrder",
    "WorkOrderStatus",
    "InventoryItem",
    "MaterialType",
    "MaterialStatus",
    "ProductionLog",
    "ProductionStatus",
    "ProductionPause",
    "MaterialConsumption",
    "NonCompliance",
    "NonComplianceType",
    "NonComplianceSeverity",
    "NonComplianceStatus",
]
