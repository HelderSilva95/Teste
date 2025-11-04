"""
Módulo para importação de dados de SQL Server externo
Configurar no VS Code com as queries específicas
"""
import pyodbc
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from config.settings import settings
from utils.logger import logger
from app.models import WorkOrder, Machine


class ExternalSQLImporter:
    """
    Importador de dados de SQL Server externo

    Uso:
        importer = ExternalSQLImporter()
        work_orders = importer.import_work_orders()
    """

    def __init__(self):
        """Inicializa conexão com SQL Server externo"""
        self.server = settings.EXTERNAL_SQL_SERVER
        self.database = settings.EXTERNAL_SQL_DATABASE
        self.username = settings.EXTERNAL_SQL_USER
        self.password = settings.EXTERNAL_SQL_PASSWORD
        self.driver = settings.DB_DRIVER

        self.connection_string = None
        if all([self.server, self.database, self.username, self.password]):
            self.connection_string = (
                f"DRIVER={{{self.driver}}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"UID={self.username};"
                f"PWD={self.password}"
            )

    def test_connection(self) -> bool:
        """
        Testa conexão com SQL Server externo

        Returns:
            bool: True se conexão bem-sucedida
        """
        if not self.connection_string:
            logger.error("Configuração de SQL externo não definida no .env")
            return False

        try:
            conn = pyodbc.connect(self.connection_string, timeout=5)
            conn.close()
            logger.info("Conexão com SQL externo bem-sucedida")
            return True
        except pyodbc.Error as e:
            logger.error(f"Erro ao conectar SQL externo: {e}")
            return False

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Executa query no SQL Server externo

        Args:
            query: SQL query para executar
            params: Parâmetros opcionais para a query

        Returns:
            Lista de dicionários com resultados
        """
        if not self.connection_string:
            logger.error("Configuração de SQL externo não definida")
            return []

        try:
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Obter nomes das colunas
            columns = [column[0] for column in cursor.description]

            # Converter resultados para lista de dicionários
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))

            cursor.close()
            conn.close()

            logger.info(f"Query executada com sucesso. {len(results)} registros retornados")
            return results

        except pyodbc.Error as e:
            logger.error(f"Erro ao executar query: {e}")
            return []

    def import_work_orders(self, db: Session, date_from: Optional[datetime] = None) -> int:
        """
        Importa ordens de trabalho do SQL externo

        NOTA: Substituir esta query pela query real fornecida pelo utilizador

        Args:
            db: Sessão do SQLAlchemy
            date_from: Data inicial para filtrar (opcional)

        Returns:
            Número de ordens importadas
        """
        # QUERY DE EXEMPLO - SUBSTITUIR COM A QUERY REAL
        query = """
        SELECT
            OrderNumber,
            ExternalOrderID,
            ProductCode,
            ProductDescription,
            QuantityPlanned,
            Unit,
            MachineCode,
            Priority,
            PlannedStart,
            PlannedEnd,
            Notes
        FROM WorkOrders
        WHERE Status = 'Pending'
        """

        if date_from:
            query += " AND PlannedStart >= ?"
            params = (date_from,)
        else:
            params = None

        try:
            # Executar query no SQL externo
            external_data = self.execute_query(query, params)

            imported_count = 0
            for row in external_data:
                # Verificar se ordem já existe
                existing = db.query(WorkOrder).filter(
                    WorkOrder.order_number == row.get('OrderNumber')
                ).first()

                if existing:
                    logger.info(f"Ordem {row.get('OrderNumber')} já existe, ignorando")
                    continue

                # Buscar máquina pelo código (se fornecido)
                machine = None
                if row.get('MachineCode'):
                    machine = db.query(Machine).filter(
                        Machine.code == row.get('MachineCode')
                    ).first()

                # Criar nova ordem de trabalho
                work_order = WorkOrder(
                    order_number=row.get('OrderNumber'),
                    external_order_id=row.get('ExternalOrderID'),
                    product_code=row.get('ProductCode'),
                    product_description=row.get('ProductDescription'),
                    quantity_planned=float(row.get('QuantityPlanned', 0)),
                    unit=row.get('Unit', 'UN'),
                    machine_id=machine.id if machine else None,
                    priority=int(row.get('Priority', 5)),
                    planned_start=row.get('PlannedStart'),
                    planned_end=row.get('PlannedEnd'),
                    notes=row.get('Notes'),
                    status='pending'
                )

                db.add(work_order)
                imported_count += 1

            db.commit()
            logger.info(f"Importadas {imported_count} ordens de trabalho")
            return imported_count

        except Exception as e:
            logger.error(f"Erro ao importar ordens de trabalho: {e}")
            db.rollback()
            return 0

    def import_custom_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Executa query customizada fornecida pelo utilizador

        Args:
            query: Query SQL customizada
            params: Parâmetros para a query

        Returns:
            Lista de resultados
        """
        return self.execute_query(query, params)


def sync_work_orders_from_external(db: Session, days_back: int = 7) -> int:
    """
    Função auxiliar para sincronizar ordens de trabalho

    Args:
        db: Sessão do SQLAlchemy
        days_back: Quantos dias para trás buscar ordens

    Returns:
        Número de ordens importadas
    """
    from datetime import timedelta

    importer = ExternalSQLImporter()

    if not importer.test_connection():
        logger.error("Não foi possível conectar ao SQL externo")
        return 0

    date_from = datetime.now() - timedelta(days=days_back)
    return importer.import_work_orders(db, date_from)


# ========== EXEMPLOS DE USO ==========
"""
# 1. Testar conexão
importer = ExternalSQLImporter()
if importer.test_connection():
    print("Conexão OK!")

# 2. Importar ordens de trabalho
from config.database import SessionLocal
db = SessionLocal()
count = importer.import_work_orders(db)
print(f"{count} ordens importadas")
db.close()

# 3. Query customizada
results = importer.import_custom_query('''
    SELECT * FROM MinhaTabela WHERE Data > ?
''', (datetime(2025, 1, 1),))

# 4. Agendar sincronização automática
# (adicionar ao cron ou task scheduler)
from config.database import SessionLocal
db = SessionLocal()
sync_work_orders_from_external(db, days_back=7)
db.close()
"""
