"""
Router: Health Check — verificação de funcionamento do S.G.P.J. Backend.

Endpoint:
    GET /health

Propósito:
    - Confirmar que a API está operacional.
    - Verificar a conectividade com o banco MySQL (sgpj) via SELECT 1.
    - Expor metadados da versão e ambiente atual.

Restrições:
    - Não requer autenticação.
    - Não lê, cria, altera ou apaga dados no banco.
    - Não modifica estrutura (tabelas, índices, triggers).
"""
from datetime import datetime, timezone

from fastapi import APIRouter

from app.config.settings import settings
from app.db.session import check_db_connectivity

router = APIRouter()


@router.get(
    "/health",
    summary="Verificação de Saúde da API",
    description=(
        "Retorna o status operacional da API e da conexão com o banco de dados MySQL (sgpj). "
        "Não requer autenticação. Não altera dados ou estrutura do banco."
    ),
    response_description="Status atual do sistema e do banco de dados.",
    tags=["Sistema"],
)
def health_check() -> dict:
    """
    Verifica se a API está em funcionamento e se a conexão com o banco está ativa.

    Retorno:
        - **status**: "ok" se tudo estiver funcionando, "degraded" se o banco estiver inacessível.
        - **app**: Nome da aplicação.
        - **environment**: Ambiente atual (development / production).
        - **timestamp**: Data e hora UTC da verificação.
        - **database**: Resultado da verificação de conectividade com o MySQL.
    """
    db_status = check_db_connectivity()

    overall_status = "ok" if db_status["status"] == "ok" else "degraded"

    return {
        "status": overall_status,
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": db_status,
    }

