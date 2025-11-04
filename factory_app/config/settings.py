"""
Configurações da aplicação
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DB_DRIVER: str = "ODBC Driver 17 for SQL Server"
    DB_SERVER: str = "localhost"
    DB_PORT: int = 1433
    DB_NAME: str = "factory_db"
    DB_USER: str = "sa"
    DB_PASSWORD: str = ""

    # Application
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8080
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # Environment
    ENVIRONMENT: str = "development"

    # External Data Sources
    EXTERNAL_SQL_SERVER: Optional[str] = None
    EXTERNAL_SQL_DATABASE: Optional[str] = None
    EXTERNAL_SQL_USER: Optional[str] = None
    EXTERNAL_SQL_PASSWORD: Optional[str] = None

    # Machine Data Reading
    MACHINE_DATA_PATH: Optional[str] = None
    MACHINE_DATA_POLL_INTERVAL: int = 60

    @property
    def database_url(self) -> str:
        """Retorna a URL de conexão do banco de dados"""
        return (
            f"mssql+pyodbc://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_SERVER}:{self.DB_PORT}/{self.DB_NAME}"
            f"?driver={self.DB_DRIVER.replace(' ', '+')}"
        )

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
