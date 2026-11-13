"""
Gerenciamento de sessões e engine do SQLAlchemy para o S.G.P.J.

Configurações aplicadas:
- Engine criado com pool de conexões configurável via variáveis de ambiente.
- pool_pre_ping=True: verifica conexões antes de usar (essencial para MySQL).
- pool_recycle: descarta conexões ociosas antes do timeout do MySQL (wait_timeout).
- NÃO chama create_all() — o schema é gerenciado exclusivamente via Database/schema.sql.
"""
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from app.config.settings import settings

# -----------------------------------------------------------------------------
# Engine principal — compartilhado por toda a aplicação
# -----------------------------------------------------------------------------
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
    echo=settings.DEBUG,          # Em DEBUG=True, loga todas as queries SQL no console
    echo_pool=False,
)

# -----------------------------------------------------------------------------
# Fábrica de sessões
# -----------------------------------------------------------------------------
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependência FastAPI que fornece uma sessão de banco de dados por requisição.
    Garante fechamento da sessão ao término da requisição (padrão Unit of Work).

    Uso em rotas:
        @router.get("/exemplo")
        def rota(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connectivity() -> dict:
    """
    Verifica a conectividade com o banco de dados executando uma query mínima.
    Utilizado exclusivamente pelo endpoint /health.

    Retorna:
        dict com status ("ok" | "error") e mensagem descritiva.

    Restrições:
        - Apenas SELECT 1 — não lê, altera ou cria dados ou estrutura.
        - Não usa sessão ORM; usa conexão direta para isolar o health check.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "message": "Conexão com o banco de dados estabelecida com sucesso."}
    except Exception as exc:
        return {"status": "error", "message": f"Falha na conexão com o banco de dados: {exc}"}

