"""
Ponto de entrada principal da API do S.G.P.J.
Sistema de Gestão da Prática Jurídica — UNINASSAU.

Responsabilidades:
    - Instanciar a aplicação FastAPI com metadados e documentação automática.
    - Registrar os middlewares de CORS.
    - Incluir os roteadores da API v1.
    - Configurar handlers de eventos de ciclo de vida (startup / shutdown).

Restrições:
    - NÃO cria, altera ou exclui tabelas, índices ou triggers.
    - O banco de dados é gerenciado exclusivamente via Database/schema.sql.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.api.v1 import api_router_v1

# -----------------------------------------------------------------------------
# Configuração de logging
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("sgpj")


# -----------------------------------------------------------------------------
# Ciclo de vida da aplicação
# -----------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia eventos de startup e shutdown da aplicação.

    Startup:
        - Loga as configurações não-sensíveis (host, porta, ambiente).
        - Não executa create_all() nem qualquer DDL.
    Shutdown:
        - Loga o encerramento limpo da aplicação.
    """
    logger.info("=" * 60)
    logger.info("S.G.P.J. Backend — Iniciando...")
    logger.info(f"  Aplicação : {settings.APP_NAME}")
    logger.info(f"  Ambiente  : {settings.APP_ENV.upper()}")
    logger.info(f"  Debug     : {settings.DEBUG}")
    logger.info(f"  Banco     : {settings.DB_NAME}@{settings.DB_HOST}:{settings.DB_PORT}")
    logger.info(f"  CORS      : {settings.CORS_ORIGINS}")
    logger.info("=" * 60)
    yield
    logger.info("S.G.P.J. Backend — Encerrado com sucesso.")


# -----------------------------------------------------------------------------
# Instância principal do FastAPI
# -----------------------------------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "API REST do Sistema de Gestão da Prática Jurídica (S.G.P.J.) — UNINASSAU. "
        "Desenvolvida com FastAPI + SQLAlchemy + MySQL, seguindo arquitetura em camadas "
        "e as regras de negócio RN01–RN10 do projeto de estágio supervisionado."
    ),
    version="1.0.0",
    contact={
        "name": "Maria Cristina Nogueira Paulino",
        "url": "https://github.com/cristina",
    },
    license_info={"name": "Projeto Acadêmico — UNINASSAU, 2026"},
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

# -----------------------------------------------------------------------------
# Middleware: CORS
# -----------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# -----------------------------------------------------------------------------
# Roteadores da API v1
# -----------------------------------------------------------------------------
app.include_router(api_router_v1, prefix="/api/v1")


# -----------------------------------------------------------------------------
# Rota raiz — redireciona para a documentação em desenvolvimento
# -----------------------------------------------------------------------------
@app.get("/", include_in_schema=False)
def root():
    return {
        "message": "S.G.P.J. Backend está em execução.",
        "docs": "/docs" if settings.DEBUG else "Documentação desabilitada em produção.",
        "health": "/api/v1/health",
    }

