"""
Schemas Pydantic para validação de dados
"""
from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


# Enums
class UserRoleEnum(str, Enum):
    OPERADOR = "operador"
    SUPERVISOR = "supervisor"
    GESTOR = "gestor"


class MaterialTypeEnum(str, Enum):
    CHAPA = "chapa"
    MACICO = "maciço"


class WorkOrderStatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# User Schemas
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Nome de utilizador")
    email: EmailStr = Field(..., description="Email válido")
    full_name: str = Field(..., min_length=3, max_length=100, description="Nome completo")
    password: str = Field(..., min_length=6, description="Senha (mínimo 6 caracteres)")
    role: UserRoleEnum = Field(default=UserRoleEnum.OPERADOR)

    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').replace('.', '').isalnum():
            raise ValueError('Username deve conter apenas letras, números, _ e .')
        return v.lower()


class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=1)


# Work Order Schemas
class WorkOrderCreate(BaseModel):
    order_number: str = Field(..., min_length=3, max_length=50, description="Número da ordem")
    product_code: str = Field(..., min_length=1, max_length=50, description="Código do produto")
    product_description: str = Field(..., min_length=3, description="Descrição do produto")
    quantity_planned: float = Field(..., gt=0, description="Quantidade planejada (maior que 0)")
    unit: str = Field(default="UN", max_length=20)
    machine_id: int = Field(..., gt=0, description="ID da máquina")
    priority: int = Field(default=5, ge=1, le=10, description="Prioridade (1-10)")
    planned_start: Optional[datetime] = None
    planned_end: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=1000)

    @validator('planned_end')
    def end_after_start(cls, v, values):
        if v and 'planned_start' in values and values['planned_start']:
            if v <= values['planned_start']:
                raise ValueError('Data de fim deve ser posterior à data de início')
        return v


# Production Log Schemas
class ProductionStart(BaseModel):
    work_order_id: int = Field(..., gt=0)
    machine_id: int = Field(..., gt=0)
    operator1_id: int = Field(..., gt=0)
    operator2_id: Optional[int] = Field(None, gt=0)
    setup_time: Optional[int] = Field(None, ge=0, description="Tempo de setup em minutos")
    notes: Optional[str] = Field(None, max_length=1000)

    @validator('operator2_id')
    def operators_different(cls, v, values):
        if v and 'operator1_id' in values and v == values['operator1_id']:
            raise ValueError('Operador 2 deve ser diferente do Operador 1')
        return v


class ProductionPause(BaseModel):
    pause_reason: str = Field(..., min_length=5, max_length=500, description="Motivo da pausa")


class ProductionComplete(BaseModel):
    quantity_input: float = Field(..., gt=0, description="Quantidade de entrada (maior que 0)")
    quantity_output: float = Field(..., gt=0, description="Quantidade de saída (maior que 0)")
    notes: Optional[str] = Field(None, max_length=1000)

    @validator('quantity_output')
    def output_not_greater_than_input(cls, v, values):
        if 'quantity_input' in values and v > values['quantity_input']:
            raise ValueError('Quantidade de saída não pode ser maior que entrada')
        return v


# Inventory Schemas
class InventoryItemCreate(BaseModel):
    qr_code: str = Field(..., min_length=3, max_length=100, description="Código QR único")
    material_type: MaterialTypeEnum
    material_name: str = Field(..., min_length=3, max_length=100, description="Nome do material")
    color: Optional[str] = Field(None, max_length=50)
    finish: Optional[str] = Field(None, max_length=50)
    length: Optional[float] = Field(None, gt=0, description="Comprimento em cm")
    width: Optional[float] = Field(None, gt=0, description="Largura em cm")
    thickness: Optional[float] = Field(None, gt=0, description="Espessura em cm")
    quantity: float = Field(default=1, gt=0, description="Quantidade (maior que 0)")
    unit: str = Field(default="UN", max_length=20)
    location: Optional[str] = Field(None, max_length=100)
    supplier: Optional[str] = Field(None, max_length=100)
    batch_number: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=1000)


# Non-Compliance Schemas
class NonComplianceCreate(BaseModel):
    nc_type: str = Field(..., description="Tipo de não-conformidade")
    severity: str = Field(..., description="Severidade")
    title: str = Field(..., min_length=5, max_length=200, description="Título")
    description: str = Field(..., min_length=10, description="Descrição detalhada")
    occurred_at: datetime = Field(..., description="Data e hora da ocorrência")
    work_order_id: Optional[int] = Field(None, gt=0)
    machine_id: Optional[int] = Field(None, gt=0)
    assigned_to_id: Optional[int] = Field(None, gt=0)
    estimated_cost: Optional[int] = Field(None, ge=0, description="Custo estimado")

    @validator('occurred_at')
    def not_future_date(cls, v):
        if v > datetime.utcnow():
            raise ValueError('Data de ocorrência não pode ser no futuro')
        return v


class NonComplianceUpdate(BaseModel):
    status: Optional[str] = None
    root_cause: Optional[str] = Field(None, max_length=1000)
    corrective_action: Optional[str] = Field(None, max_length=1000)
    preventive_action: Optional[str] = Field(None, max_length=1000)
    assigned_to_id: Optional[int] = Field(None, gt=0)


# Machine Schema
class MachineCreate(BaseModel):
    code: str = Field(..., min_length=2, max_length=50, description="Código da máquina")
    name: str = Field(..., min_length=3, max_length=100, description="Nome da máquina")
    description: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=100)

    @validator('code')
    def code_uppercase(cls, v):
        return v.upper()
