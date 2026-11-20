
"""
Ponto de entrada principal da API do S.G.P.J.
Sistema de Gestão da Prática Jurídica — UNINASSAU.

Responsabilidades:
    - Instanciar a aplicação FastAPI.
    - Configurar o middleware CORS.
    - Registrar os roteadores da API v1.
    - Gerenciar os eventos de inicialização e encerramento.

Restrições:
    - Não cria, altera ou exclui tabelas, índices ou triggers.
    - O banco de dados é gerenciado exclusivamente via Database/schema.sql.
"""

# Bibliotecas para registro de eventos e ciclo de vida da aplicação
import logging
from contextlib import asynccontextmanager

# Componentes principais do FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configurações gerais e roteador principal da API
from app.config.settings import settings
from app.api.v1 import api_router_v1


# ============================================================
# 1. CONFIGURAÇÃO DE LOGGING
# Define o nível e o formato das mensagens exibidas no terminal.
# ============================================================

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Identifica as mensagens de log do S.G.P.J.
logger = logging.getLogger("sgpj")


# ============================================================
# 2. CICLO DE VIDA DA APLICAÇÃO
# Registra eventos executados na inicialização e no encerramento.
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia os eventos de startup e shutdown da aplicação.

    Startup:
        - Exibe informações não sensíveis da configuração.
        - Não executa alterações na estrutura do banco de dados.

    Shutdown:
        - Registra o encerramento da aplicação.
    """

    # Exibe informações sobre a inicialização do backend
    logger.info("=" * 60)
    logger.info("S.G.P.J. Backend — Iniciando...")
    logger.info(f"  Aplicação : {settings.APP_NAME}")
    logger.info(f"  Ambiente  : {settings.APP_ENV.upper()}")
    logger.info(f"  Debug     : {settings.DEBUG}")
    logger.info(f"  Banco     : {settings.DB_NAME}@{settings.DB_HOST}:{settings.DB_PORT}")
    logger.info(f"  CORS      : {settings.CORS_ORIGINS}")
    logger.info("=" * 60)

    yield

    # Registra o encerramento do backend
    logger.info("S.G.P.J. Backend — Encerrado com sucesso.")


# ============================================================
# 3. INSTÂNCIA PRINCIPAL DO FASTAPI
# Define os metadados, a documentação e as configurações da API.
# ============================================================

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "API REST do Sistema de Gestão da Prática Jurídica (S.G.P.J.) — UNINASSAU. "
        "Desenvolvida com FastAPI + SQLAlchemy + MySQL, seguindo arquitetura em camadas "
        "e as regras de negócio definidas para o projeto de estágio supervisionado."
    ),
    version="1.0.0",
    contact={
        "name": "Maria Cristina Nogueira Paulino",
        "url": "https://github.com/cristina",
    },
    license_info={"name": "Projeto Acadêmico — UNINASSAU, 2026"},

    # Disponibiliza a documentação somente no ambiente de desenvolvimento
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,

    # Associa o gerenciamento de inicialização e encerramento
    lifespan=lifespan,
)


# ============================================================
# 4. MIDDLEWARE CORS
# Define quais origens, métodos e cabeçalhos podem acessar a API.
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)


# ============================================================
# 5. REGISTRO DOS ROTEADORES DA API V1
# Inclui as rotas dos módulos utilizando o prefixo /api/v1.
# ============================================================

app.include_router(api_router_v1, prefix="/api/v1")


# ============================================================
# 6. ROTA RAIZ
# Retorna informações básicas e os principais endereços da API.
# ============================================================

@app.get("/", include_in_schema=False)
def root():
    return {
        "message": "S.G.P.J. Backend está em execução.",
        "docs": "/docs" if settings.DEBUG else "Documentação desabilitada em produção.",
        "health": "/api/v1/health",
    }
