from pathlib import Path
from typing import List
from pydantic import computed_field, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL as SQLAlchemyURL

# Resolução do caminho absoluto até o diretório Backend/ (pai de app/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    """
    Configurações centralizadas da aplicação S.G.P.J.
    Carregadas a partir de variáveis de ambiente ou do arquivo .env.

    Regras de segurança aplicadas:
    - SECRET_KEY não possui fallback silencioso: a ausência levanta ValueError.
    - DATABASE_URL é gerada via sqlalchemy.engine.URL.create() para suportar
      corretamente senhas com caracteres especiais (ex.: @, #, %, etc.).
    """

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # -------------------------------------------------------------------------
    # Informações da Aplicação
    # -------------------------------------------------------------------------
    APP_NAME: str = "Sistema de Gestão da Prática Jurídica (S.G.P.J.)"
    APP_ENV: str = "development"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # -------------------------------------------------------------------------
    # Banco de Dados MySQL (banco existente: sgpj)
    # -------------------------------------------------------------------------
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "sgpj"

    # Pool de Conexões SQLAlchemy
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE: int = 3600
    DB_POOL_PRE_PING: bool = True

    # -------------------------------------------------------------------------
    # Segurança e Autenticação (JWT — RN01)
    # SECRET_KEY DEVE ser definida explicitamente no .env.
    # Não há fallback: ausência ou string vazia levanta erro na inicialização.
    # -------------------------------------------------------------------------
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # -------------------------------------------------------------------------
    # Regras de Negócio (RN05 — Janela flexível de alerta de prazos)
    # -------------------------------------------------------------------------
    PRAZO_ALERTA_DIAS: int = 5

    # -------------------------------------------------------------------------
    # CORS — Origens autorizadas para o Frontend React (Vite/CRA)
    # -------------------------------------------------------------------------
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # -------------------------------------------------------------------------
    # Validadores
    # -------------------------------------------------------------------------
    @field_validator("SECRET_KEY", mode="after")
    @classmethod
    def secret_key_must_be_set(cls, v: str) -> str:
        """
        Garante que a SECRET_KEY seja definida explicitamente e não seja vazia.
        Impede que a aplicação suba sem uma chave secreta configurada.
        """
        if not v or not v.strip():
            raise ValueError(
                "SECRET_KEY não está definida. "
                "Adicione SECRET_KEY=<valor_seguro> ao arquivo .env antes de iniciar."
            )
        return v

    # -------------------------------------------------------------------------
    # Propriedades computadas
    # -------------------------------------------------------------------------
    @computed_field
    @property
    def DATABASE_URL(self) -> SQLAlchemyURL:
        """
        Gera o objeto URL do SQLAlchemy usando URL.create(), que trata
        automaticamente a codificação de caracteres especiais na senha
        (ex.: @, #, %, &, +), prevenindo falhas silenciosas na string de conexão.
        """
        return SQLAlchemyURL.create(
            drivername="mysql+pymysql",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
            query={"charset": "utf8mb4"},
        )


settings = Settings()
