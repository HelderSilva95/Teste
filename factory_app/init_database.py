"""
Script para inicializar a base de dados com dados de exemplo
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from config.database import SessionLocal, init_db
from app.models import (
    User, UserRole, Machine, WorkOrder, WorkOrderStatus,
    InventoryItem, MaterialType, MaterialStatus
)
from utils.security import get_password_hash


def create_sample_data():
    """Cria dados de exemplo na base de dados"""
    db = SessionLocal()

    try:
        print("Inicializando base de dados...")
        init_db()
        print("✓ Tabelas criadas")

        # Verificar se já existem dados
        if db.query(User).count() > 0:
            print("⚠ Base de dados já contém dados. Abortando...")
            return

        print("\nCriando dados de exemplo...")

        # Criar utilizadores
        print("- Criando utilizadores...")
        users = [
            User(
                username="admin",
                email="admin@factory.com",
                full_name="Administrador",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.GESTOR
            ),
            User(
                username="supervisor",
                email="supervisor@factory.com",
                full_name="João Supervisor",
                hashed_password=get_password_hash("super123"),
                role=UserRole.SUPERVISOR
            ),
            User(
                username="operador1",
                email="operador1@factory.com",
                full_name="Maria Operadora",
                hashed_password=get_password_hash("oper123"),
                role=UserRole.OPERADOR
            ),
            User(
                username="operador2",
                email="operador2@factory.com",
                full_name="Pedro Operador",
                hashed_password=get_password_hash("oper123"),
                role=UserRole.OPERADOR
            ),
        ]
        db.add_all(users)
        db.commit()
        print(f"  ✓ {len(users)} utilizadores criados")

        # Criar máquinas
        print("- Criando máquinas...")
        machines = [
            Machine(code="SERRA-01", name="Serra Ponte", location="Área A"),
            Machine(code="POLID-01", name="Polidora 1", location="Área B"),
            Machine(code="POLID-02", name="Polidora 2", location="Área B"),
            Machine(code="CORTE-01", name="Corte Laser", location="Área C"),
            Machine(code="FRESA-01", name="Fresadora CNC", location="Área D"),
        ]
        db.add_all(machines)
        db.commit()
        print(f"  ✓ {len(machines)} máquinas criadas")

        # Criar ordens de trabalho
        print("- Criando ordens de trabalho...")
        work_orders = [
            WorkOrder(
                order_number="OT-2024-001",
                product_code="BANCADA-GRA-01",
                product_description="Bancada de cozinha em granito preto",
                quantity_planned=2.5,
                unit="M2",
                machine_id=machines[0].id,
                status=WorkOrderStatus.PENDING,
                priority=1,
                planned_start=datetime.utcnow() + timedelta(days=1)
            ),
            WorkOrder(
                order_number="OT-2024-002",
                product_code="LAJE-MAR-01",
                product_description="Laje em mármore branco",
                quantity_planned=5.0,
                unit="M2",
                machine_id=machines[1].id,
                status=WorkOrderStatus.PENDING,
                priority=2,
                planned_start=datetime.utcnow() + timedelta(days=2)
            ),
            WorkOrder(
                order_number="OT-2024-003",
                product_code="ESCADA-GRA-02",
                product_description="Degraus de escada em granito cinza",
                quantity_planned=12,
                unit="UN",
                machine_id=machines[2].id,
                status=WorkOrderStatus.PENDING,
                priority=3
            ),
        ]
        db.add_all(work_orders)
        db.commit()
        print(f"  ✓ {len(work_orders)} ordens de trabalho criadas")

        # Criar itens de inventário
        print("- Criando itens de inventário...")
        inventory_items = [
            InventoryItem(
                qr_code="CHAPA-GRA-001",
                material_type=MaterialType.CHAPA,
                material_name="Granito Preto São Gabriel",
                color="Preto",
                finish="Polido",
                length=280,
                width=180,
                thickness=2,
                quantity=1,
                location="A-01",
                supplier="Mármores do Norte",
                batch_number="LOT-2024-01"
            ),
            InventoryItem(
                qr_code="CHAPA-MAR-002",
                material_type=MaterialType.CHAPA,
                material_name="Mármore Branco Estremoz",
                color="Branco",
                finish="Polido",
                length=300,
                width=200,
                thickness=2,
                quantity=1,
                location="A-02",
                supplier="Mármores do Sul",
                batch_number="LOT-2024-02"
            ),
            InventoryItem(
                qr_code="MAC-GRA-003",
                material_type=MaterialType.MACICO,
                material_name="Granito Cinza Monção",
                color="Cinza",
                finish="Amaciado",
                length=100,
                width=30,
                thickness=15,
                quantity=15,
                unit="UN",
                location="B-01",
                supplier="Granitos Portugueses"
            ),
        ]
        db.add_all(inventory_items)
        db.commit()
        print(f"  ✓ {len(inventory_items)} itens de inventário criados")

        print("\n" + "="*60)
        print("✓ Base de dados inicializada com sucesso!")
        print("="*60)
        print("\nCredenciais de acesso:")
        print("-" * 60)
        print("GESTOR:")
        print("  Utilizador: admin")
        print("  Senha: admin123")
        print("\nSUPERVISOR:")
        print("  Utilizador: supervisor")
        print("  Senha: super123")
        print("\nOPERADOR:")
        print("  Utilizador: operador1")
        print("  Senha: oper123")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n✗ Erro ao criar dados: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_sample_data()
