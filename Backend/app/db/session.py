
import logging
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from app.config.settings import settings


# Configura o registro de erros internos deste módulo.
logger = logging.getLogger(__name__)


# Cria a engine principal, compartilhada por toda a aplicação.
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
    echo=False,
    echo_pool=False,
)


# Define a fábrica de sessões utilizadas pelas requisições.
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# Fornece uma sessão do banco de dados para cada requisição.
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        # Garante o fechamento da sessão após a requisição.
        db.close()


# Verifica a conectividade com o banco de dados.
def check_db_connectivity() -> dict:
    try:
        # Executa uma consulta simples, sem modificar dados.
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "message": "Conexão com o banco de dados estabelecida com sucesso."
        }

    except Exception:
        # Registra os detalhes internamente, sem expor informações do banco.
        logger.exception("Falha na conexão com o banco de dados.")

        return {
            "status": "error",
            "message": "Não foi possível estabelecer conexão com o banco de dados."
        }
