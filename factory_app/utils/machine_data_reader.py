"""
Módulo para leitura de dados de máquinas
Configurar no VS Code com o formato específico dos arquivos
"""
import os
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from sqlalchemy.orm import Session
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from config.settings import settings
from utils.logger import logger
from app.models import Machine, ProductionLog


class MachineDataParser:
    """
    Parser genérico para dados de máquinas

    NOTA: Substituir os métodos de parse com a lógica específica
    do formato de arquivo usado pelas máquinas
    """

    @staticmethod
    def parse_csv_file(file_path: str) -> List[Dict[str, Any]]:
        """
        Parse arquivo CSV de máquina

        EXEMPLO - Substituir com formato real
        Formato esperado:
        MachineCode,Timestamp,Status,Counter,Temperature,ErrorCode

        Args:
            file_path: Caminho do arquivo

        Returns:
            Lista de dicionários com dados parseados
        """
        import csv

        data = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append({
                        'machine_code': row.get('MachineCode'),
                        'timestamp': datetime.fromisoformat(row.get('Timestamp')),
                        'status': row.get('Status'),
                        'counter': int(row.get('Counter', 0)),
                        'temperature': float(row.get('Temperature', 0)),
                        'error_code': row.get('ErrorCode')
                    })
            logger.info(f"Parseadas {len(data)} linhas de {file_path}")
            return data
        except Exception as e:
            logger.error(f"Erro ao parsear CSV {file_path}: {e}")
            return []

    @staticmethod
    def parse_txt_file(file_path: str) -> List[Dict[str, Any]]:
        """
        Parse arquivo TXT de máquina

        EXEMPLO - Substituir com formato real
        Formato esperado:
        MACHINE:M001
        TIME:2025-01-15 10:30:00
        PIECES:150
        STATUS:RUNNING

        Args:
            file_path: Caminho do arquivo

        Returns:
            Lista de dicionários com dados parseados
        """
        data = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        data[key.lower()] = value.strip()

            # Converter para formato padrão
            parsed = {
                'machine_code': data.get('machine'),
                'timestamp': datetime.fromisoformat(data.get('time')),
                'pieces': int(data.get('pieces', 0)),
                'status': data.get('status')
            }

            logger.info(f"Parseado arquivo TXT: {file_path}")
            return [parsed]
        except Exception as e:
            logger.error(f"Erro ao parsear TXT {file_path}: {e}")
            return []

    @staticmethod
    def parse_xml_file(file_path: str) -> List[Dict[str, Any]]:
        """
        Parse arquivo XML de máquina

        EXEMPLO - Substituir com formato real

        Args:
            file_path: Caminho do arquivo

        Returns:
            Lista de dicionários com dados parseados
        """
        import xml.etree.ElementTree as ET

        data = []
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            for record in root.findall('.//Record'):
                parsed = {
                    'machine_code': record.find('MachineCode').text,
                    'timestamp': datetime.fromisoformat(record.find('Timestamp').text),
                    'value': float(record.find('Value').text)
                }
                data.append(parsed)

            logger.info(f"Parseados {len(data)} registros XML de {file_path}")
            return data
        except Exception as e:
            logger.error(f"Erro ao parsear XML {file_path}: {e}")
            return []


class MachineDataReader:
    """
    Leitor de dados de máquinas de diretório configurado
    """

    def __init__(self, data_path: Optional[str] = None):
        """
        Inicializa leitor

        Args:
            data_path: Caminho do diretório com dados (usa MACHINE_DATA_PATH do .env se não fornecido)
        """
        self.data_path = data_path or settings.MACHINE_DATA_PATH

        if not self.data_path:
            logger.warning("MACHINE_DATA_PATH não configurado no .env")
            self.data_path = None
        elif not os.path.exists(self.data_path):
            logger.warning(f"Diretório {self.data_path} não existe")

        self.parser = MachineDataParser()

    def get_file_parser(self, file_path: str) -> Optional[Callable]:
        """
        Retorna parser apropriado baseado na extensão do arquivo

        Args:
            file_path: Caminho do arquivo

        Returns:
            Função de parser ou None
        """
        ext = Path(file_path).suffix.lower()

        parsers = {
            '.csv': self.parser.parse_csv_file,
            '.txt': self.parser.parse_txt_file,
            '.xml': self.parser.parse_xml_file
        }

        return parsers.get(ext)

    def process_file(self, file_path: str, db: Session) -> int:
        """
        Processa arquivo de dados de máquina

        Args:
            file_path: Caminho do arquivo
            db: Sessão do banco de dados

        Returns:
            Número de registros processados
        """
        parser = self.get_file_parser(file_path)

        if not parser:
            logger.warning(f"Sem parser para {file_path}")
            return 0

        try:
            # Parsear arquivo
            data_records = parser(file_path)

            if not data_records:
                return 0

            # Processar cada registro
            # NOTA: Esta lógica depende do que você quer fazer com os dados
            # Exemplo: atualizar produção, criar logs, etc.

            for record in data_records:
                machine_code = record.get('machine_code')

                if not machine_code:
                    continue

                # Buscar máquina
                machine = db.query(Machine).filter(
                    Machine.code == machine_code
                ).first()

                if not machine:
                    logger.warning(f"Máquina {machine_code} não encontrada")
                    continue

                # EXEMPLO: Atualizar produção ativa
                # Você pode adaptar esta lógica conforme necessário
                active_production = db.query(ProductionLog).filter(
                    ProductionLog.machine_id == machine.id,
                    ProductionLog.status == 'in_progress'
                ).first()

                if active_production and 'pieces' in record:
                    # Atualizar quantidade produzida
                    active_production.quantity_output = record['pieces']
                    active_production.updated_at = datetime.utcnow()

            db.commit()
            logger.info(f"Processados {len(data_records)} registros de {file_path}")
            return len(data_records)

        except Exception as e:
            logger.error(f"Erro ao processar {file_path}: {e}")
            db.rollback()
            return 0

    def scan_directory(self, db: Session, file_pattern: str = "*.*") -> int:
        """
        Escaneia diretório e processa todos os arquivos

        Args:
            db: Sessão do banco de dados
            file_pattern: Padrão de arquivos (ex: "*.csv")

        Returns:
            Total de registros processados
        """
        if not self.data_path or not os.path.exists(self.data_path):
            logger.error("Diretório de dados de máquinas não configurado ou não existe")
            return 0

        total_processed = 0
        path = Path(self.data_path)

        for file_path in path.glob(file_pattern):
            if file_path.is_file():
                count = self.process_file(str(file_path), db)
                total_processed += count

        logger.info(f"Scan completo: {total_processed} registros processados")
        return total_processed

    def watch_directory(self, db: Session):
        """
        Monitora diretório por novos arquivos (modo contínuo)

        Args:
            db: Sessão do banco de dados
        """
        if not self.data_path or not os.path.exists(self.data_path):
            logger.error("Diretório de dados de máquinas não configurado ou não existe")
            return

        class MachineFileHandler(FileSystemEventHandler):
            def __init__(self, reader, db_session):
                self.reader = reader
                self.db = db_session

            def on_created(self, event):
                if isinstance(event, FileCreatedEvent) and not event.is_directory:
                    logger.info(f"Novo arquivo detectado: {event.src_path}")
                    # Aguardar arquivo ser completamente escrito
                    time.sleep(1)
                    self.reader.process_file(event.src_path, self.db)

        event_handler = MachineFileHandler(self, db)
        observer = Observer()
        observer.schedule(event_handler, self.data_path, recursive=False)
        observer.start()

        logger.info(f"Monitorando diretório: {self.data_path}")

        try:
            while True:
                time.sleep(settings.MACHINE_DATA_POLL_INTERVAL)
        except KeyboardInterrupt:
            observer.stop()
            logger.info("Monitoramento interrompido")

        observer.join()


# ========== FUNÇÕES AUXILIARES ==========

def read_machine_data_once(db: Session, file_pattern: str = "*.*") -> int:
    """
    Função auxiliar para ler dados de máquinas uma vez

    Args:
        db: Sessão do banco de dados
        file_pattern: Padrão de arquivos (ex: "*.csv", "*.txt")

    Returns:
        Número de registros processados
    """
    reader = MachineDataReader()
    return reader.scan_directory(db, file_pattern)


def start_machine_data_monitoring(db: Session):
    """
    Inicia monitoramento contínuo do diretório de dados

    Args:
        db: Sessão do banco de dados
    """
    reader = MachineDataReader()
    reader.watch_directory(db)


# ========== EXEMPLOS DE USO ==========
"""
# 1. Scan único
from config.database import SessionLocal
db = SessionLocal()
count = read_machine_data_once(db, "*.csv")
print(f"{count} registros processados")
db.close()

# 2. Processar arquivo específico
reader = MachineDataReader()
db = SessionLocal()
reader.process_file("/caminho/para/arquivo.csv", db)
db.close()

# 3. Monitoramento contínuo (em background)
# Execute em processo separado ou thread
from config.database import SessionLocal
db = SessionLocal()
start_machine_data_monitoring(db)  # Roda indefinidamente

# 4. Integrar com scheduler (ex: APScheduler)
from apscheduler.schedulers.background import BackgroundScheduler
from config.database import SessionLocal

def scheduled_read():
    db = SessionLocal()
    read_machine_data_once(db, "*.csv")
    db.close()

scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_read, 'interval', minutes=5)
scheduler.start()
"""
